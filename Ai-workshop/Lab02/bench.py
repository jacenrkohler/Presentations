#!/usr/bin/env python3
"""bench.py - Lab 2: benchmark models and harnesses.

Runs the same prompts against one or more targets, checks each answer, and records per prompt
and per session: the prompt, the response, the operating time, and the tokens (input, output,
cache read, cache write, reasoning). Results stream to the terminal as they happen, to a JSONL
file, and (with --live-html) to a web page that refreshes itself.

Targets (--target, repeat it to compare several in one run):
  harness:PATH                 a local model through the Lab 1 harness (GGUF, safetensors or ONNX)
  ollama:MODEL                 Ollama's own API, e.g. ollama:qwen2.5:1.5b   (Part 2)
  server:URL#MODEL             any OpenAI-compatible server, e.g. server:http://localhost:8080/v1#qwen
  anthropic:MODEL  openai:MODEL  gemini:MODEL  copilot:MODEL      cloud APIs through the harness (Part 3)
  cli:claude  cli:codex  cli:gemini  cli:copilot                   the official CLIs (Part 4)

  python3 bench.py run --target harness:../Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf --target ollama:qwen2.5:1.5b
  python3 bench.py run --target harness:MODEL --gpu-layers -1 --label gpu       (then --label cpu without it)
  python3 bench.py report results/*.jsonl --out report.html
  python3 bench.py compare results/run-cpu.jsonl results/run-gpu.jsonl

Standard library only, plus whatever the harness needs for the model you test.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "Lab01"))
try:
    import harness  # the Lab 1 harness, with the Part 1 metrics added
except ImportError:
    sys.exit("bench.py needs harness.py from the Lab01 folder next to this one (../Lab01/harness.py).")

TOKEN_KEYS = harness.TOKEN_KEYS  # input, output, cache_read, cache_write, reasoning
DEFAULT_SYSTEM = "You are a helpful assistant. Follow the format the user asks for exactly."


# --------------------------------------------------------------------------
# Checking answers: is the response right? (the "effectiveness" half of a benchmark)
# --------------------------------------------------------------------------
def strip_think(text):
    return re.sub(r"<think>.*?(</think>|$)", "", text, flags=re.S).strip()


def first_json(text):
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            depth += (text[i] == "{") - (text[i] == "}")
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except ValueError:
                    break
        start = text.find("{", start + 1)
    return None


def check_answer(text, check):
    """Return (passed, reason). Every rule in the check must hold."""
    t = strip_think(text)
    low = t.lower()
    if not check:
        return None, "no check"
    if "number" in check:
        nums = re.findall(r"-?\d+(?:\.\d+)?", t.replace(",", ""))
        if not nums or float(nums[0]) != float(check["number"]):
            return False, f"expected {check['number']}, got {nums[0] if nums else 'no number'}"
    if "contains" in check and not all(w.lower() in low for w in check["contains"]):
        return False, "missing " + ", ".join(w for w in check["contains"] if w.lower() not in low)
    if "contains_any" in check and not any(w.lower() in low for w in check["contains_any"]):
        return False, "none of: " + ", ".join(check["contains_any"])
    if "regex" in check and not re.search(check["regex"], t):
        return False, "format does not match"
    if "json" in check:
        obj = first_json(t)
        if not isinstance(obj, dict):
            return False, "no JSON object"
        for k, v in check["json"].items():
            if str(obj.get(k)).lower() != str(v).lower():
                return False, f"{k} is {obj.get(k)!r}, expected {v!r}"
    if "max_sentences" in check and len(re.findall(r"[.!?](\s|$)", t)) > check["max_sentences"]:
        return False, "too long"
    return True, "ok"


# --------------------------------------------------------------------------
# Live display: one updating line while a prompt runs, then one row when it is done.
# --------------------------------------------------------------------------
class Live:
    def __init__(self, label, enabled=True):
        self.label, self.enabled = label, enabled and sys.stderr.isatty()
        self.pieces, self.t0, self.first, self.stop = 0, time.perf_counter(), None, False
        self.thread = None

    def start(self):
        self.t0 = time.perf_counter()
        if self.enabled:
            self.thread = threading.Thread(target=self._tick, daemon=True)
            self.thread.start()

    def piece(self):
        self.pieces += 1
        if self.first is None:
            self.first = time.perf_counter()

    def _tick(self):
        while not self.stop:
            el = time.perf_counter() - self.t0
            rate = ""
            if self.first and self.pieces > 1:
                rate = f"  {self.pieces / max(time.perf_counter() - self.first, 1e-6):5.1f} pieces/s"
            ttft = f"  first token {self.first - self.t0:.2f} s" if self.first else "  waiting for first token"
            sys.stderr.write(f"\r  {self.label}  {el:6.1f} s  {self.pieces:5d} pieces{ttft}{rate}   \033[K")
            sys.stderr.flush()
            time.sleep(0.2)

    def done(self):
        self.stop = True
        if self.thread:
            self.thread.join()
            sys.stderr.write("\r\033[K")


# --------------------------------------------------------------------------
# Targets. Each has .name, .model, .device and .call(system, prompt, live) -> record dict.
# --------------------------------------------------------------------------
class HarnessTarget:
    """A model through harness.py (local files, a server, or a cloud API)."""

    def __init__(self, spec, a):
        kind, _, rest = spec.partition(":")
        ns = argparse.Namespace(backend="auto", model=None, url=None, key_file=None, threads=a.threads,
                                gpu_layers=a.gpu_layers, ctx=a.ctx, cache=a.cache)
        if kind == "harness":
            ns.model = rest
        elif kind == "server":
            ns.backend = "server"
            ns.url, _, ns.model = rest.partition("#")
        else:  # anthropic, openai, gemini, copilot
            ns.backend, ns.model = kind, rest
            ns.key_file = a.key_files.get(kind) or a.key_files.get("github" if kind == "copilot" else kind)
        self.backend = harness.make_backend(ns)
        self.name = f"{self.backend.name}:{self.backend.model}"
        self.model, self.device = self.backend.model, getattr(self.backend, "device", "?")
        self.settings = dict(harness.DEFAULTS)
        self.settings.update(temperature=a.temperature, max_tokens=a.max_tokens, seed=a.seed)
        if a.effort:
            self.settings["effort"] = a.effort

    def call(self, system, prompt, live):
        msgs = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
        s = harness.apply_effort(self.settings, self.backend)
        self.backend.usage, parts = {}, []
        t0, first = time.perf_counter(), None
        for piece in self.backend.stream(harness.with_think_switch(msgs, s), s):
            first = first or time.perf_counter()
            parts.append(piece)
            live.piece()
        rec = harness.record_call(self.backend, msgs, s, "".join(parts), t0, first, time.perf_counter(),
                                  session=harness.Session())
        return rec


class OllamaTarget:
    """Ollama's native API. It reports token counts and its own timings for every reply."""

    def __init__(self, spec, a):
        self.model = spec.split(":", 1)[1]
        self.url = a.ollama_url.rstrip("/")
        self.name, self.think = f"ollama:{self.model}", a.think
        self.options = {"temperature": a.temperature, "num_predict": a.max_tokens, "num_ctx": a.ctx}
        if a.seed >= 0:
            self.options["seed"] = a.seed
        if a.ollama_num_gpu is not None:
            self.options["num_gpu"] = a.ollama_num_gpu  # 0 = force the CPU
        self.device = "cpu (forced)" if a.ollama_num_gpu == 0 else "ollama default"

    def call(self, system, prompt, live):
        body = {"model": self.model, "stream": True, "options": self.options,
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}]}
        if self.think is not None:
            body["think"] = self.think
        req = urllib.request.Request(self.url + "/api/chat", data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        parts, thinking_chunks, final = [], 0, {}
        t0, first = time.perf_counter(), None
        try:
            with urllib.request.urlopen(req, timeout=900) as r:
                for raw in r:
                    if not raw.strip():
                        continue
                    d = json.loads(raw.decode())
                    if d.get("error"):
                        raise RuntimeError(d["error"])
                    msg = d.get("message", {})
                    if msg.get("thinking"):
                        thinking_chunks += 1  # Ollama streams one token per chunk
                        first = first or time.perf_counter()
                        live.piece()
                    if msg.get("content"):
                        first = first or time.perf_counter()
                        parts.append(msg["content"])
                        live.piece()
                    if d.get("done"):
                        final = d
        except urllib.error.URLError as e:
            raise RuntimeError(f"Could not reach Ollama at {self.url}: {e}. Is it running? (Lab 1, Part 4a)")
        t1 = time.perf_counter()
        ns = 1e9
        tokens = {"input": final.get("prompt_eval_count"), "output": final.get("eval_count"),
                  "cache_read": None, "cache_write": None, "reasoning": thinking_chunks}
        gen_s = (final.get("eval_duration") or 0) / ns
        return {
            "backend": "ollama", "model": self.model, "device": self.device,
            "prompt": prompt, "response": "".join(parts),
            "operating_s": round(t1 - t0, 3), "first_token_s": round(first - t0, 3) if first else None,
            "generate_s": round(gen_s, 3) or None,
            "output_tok_per_s": round(tokens["output"] / gen_s, 1) if tokens["output"] and gen_s else None,
            "load_s": round((final.get("load_duration") or 0) / ns, 3),
            "prompt_eval_s": round((final.get("prompt_eval_duration") or 0) / ns, 3),
            "tokens": tokens,
            "token_source": "reported by Ollama (cache not reported; reasoning = thinking chunks)",
        }


# ---- the official CLIs (Part 4). Their JSON formats change; tokens are found by name, wherever they are.
CLI_COMMANDS = {
    "claude": lambda p: ["claude", "-p", p, "--output-format", "json", "--permission-mode", "plan"],
    "codex": lambda p: ["codex", "exec", "--json", "--sandbox", "read-only", "--skip-git-repo-check", p],
    "gemini": lambda p: ["gemini", "-p", p, "--output-format", "json", "--approval-mode", "plan"],
    "copilot": lambda p: ["copilot", "-p", p, "--output-format", "json"],
}
NAMES = {
    "input": ("input_tokens", "inputtokens", "prompt_tokens", "prompttokencount", "prompt"),
    "output": ("output_tokens", "outputtokens", "completion_tokens", "candidatestokencount", "candidates"),
    "cache_read": ("cache_read_input_tokens", "cachereadinputtokens", "cached_input_tokens", "cached_tokens",
                   "cachedcontenttokencount", "cached"),
    "cache_write": ("cache_creation_input_tokens", "cachecreationinputtokens"),
    "reasoning": ("reasoning_output_tokens", "reasoning_tokens", "thoughtstokencount", "thoughts"),
}
TEXT_KEYS = ("result", "response", "text", "content", "message")


def parse_json_stream(out):
    """The CLI's output as a list of JSON objects (one object, or one per line). Plain text gives []."""
    objs = []
    try:
        objs.append(json.loads(out))
    except ValueError:
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("{"):
                try:
                    objs.append(json.loads(line))
                except ValueError:
                    pass
    return [o for o in objs if isinstance(o, dict)]


def find_tokens(obj):
    """Search nested JSON for token counts by name. The last usage block found wins."""
    found = {}

    def walk(o, depth):
        if isinstance(o, dict):
            block = {}
            for k, v in o.items():
                kl = k.lower()
                for field, names in NAMES.items():
                    if kl in names and isinstance(v, (int, float)) and not isinstance(v, bool):
                        block[field] = int(v)
            if "input" in block or "output" in block:
                found.update(block)
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o:
                walk(v, depth + 1)
    walk(obj, 0)
    return found


def find_text(objs, tool):
    if tool == "codex":  # the final agent message
        texts = [e.get("item", {}).get("text") for e in objs
                 if e.get("type") == "item.completed" and e.get("item", {}).get("type") in ("agent_message", "assistant_message")]
        if texts:
            return texts[-1] or ""
    for o in reversed(objs):
        for k in TEXT_KEYS:
            if isinstance(o.get(k), str) and o[k].strip():
                return o[k]
        d = o.get("data")
        if isinstance(d, dict):
            for k in TEXT_KEYS:
                if isinstance(d.get(k), str):
                    return d[k]
    return ""


class CliTarget:
    def __init__(self, spec, a):
        self.tool = spec.split(":", 1)[1]
        if self.tool not in CLI_COMMANDS:
            sys.exit("cli target must be one of: " + ", ".join("cli:" + k for k in CLI_COMMANDS))
        exe = {"claude": "claude", "codex": "codex", "gemini": "gemini", "copilot": "copilot"}[self.tool]
        # The full path also finds Windows wrappers such as claude.cmd, which subprocess cannot find by name.
        self.exe = shutil.which(exe)
        if not self.exe:
            sys.exit(f"{exe} is not installed or not on PATH. See Lab 1, Bonus Part 5.")
        self.name, self.model, self.device = f"cli:{self.tool}", self.tool, "cloud"
        self.timeout, self.keep_raw = a.cli_timeout, a.raw
        # Agents act on the folder they start in: always an empty, throwaway folder.
        self.workdir = tempfile.mkdtemp(prefix="bench-cli-")

    def call(self, system, prompt, live):
        # The CLIs have their own system prompts; ours is added to the front of the prompt.
        full = prompt if system == DEFAULT_SYSTEM else system + "\n\n" + prompt
        t0 = time.perf_counter()
        try:
            p = subprocess.run([self.exe] + CLI_COMMANDS[self.tool](full)[1:], cwd=self.workdir, capture_output=True, text=True,
                               timeout=self.timeout, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"timed out after {self.timeout} s (it may be waiting for a sign-in or a permission)")
        t1 = time.perf_counter()
        objs = parse_json_stream(p.stdout)
        text = find_text(objs, self.tool) if objs else p.stdout.strip()
        u = {}
        for o in objs:
            u.update(find_tokens(o))
        if self.tool == "claude" and objs:  # Anthropic's input_tokens excludes the cached part
            usage = objs[-1].get("usage") or {}
            u = {"input": (usage.get("input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)
                 + (usage.get("cache_creation_input_tokens") or 0),
                 "output": usage.get("output_tokens"), "cache_read": usage.get("cache_read_input_tokens"),
                 "cache_write": usage.get("cache_creation_input_tokens"), "reasoning": None}
        if self.tool == "gemini" and "reasoning" in u and u.get("output") is not None:
            u["output"] += u["reasoning"]  # Gemini counts thinking separately
        if p.returncode != 0 and not text:
            raise RuntimeError((p.stderr or p.stdout).strip()[-300:] or f"exit code {p.returncode}")
        live.piece()
        rec = {
            "backend": "cli", "model": self.tool, "device": "cloud", "prompt": prompt, "response": text,
            "operating_s": round(t1 - t0, 3), "first_token_s": None, "generate_s": None, "output_tok_per_s": None,
            "tokens": {k: u.get(k) for k in TOKEN_KEYS},
            "token_source": "reported by the CLI" + ("" if self.tool == "claude" else " (format not verified; check raw)"),
            "cli_exit": p.returncode,
        }
        if self.tool == "claude" and objs:
            rec["cli_cost_usd"] = objs[-1].get("total_cost_usd")
            rec["cli_api_s"] = (objs[-1].get("duration_api_ms") or 0) / 1000 or None
        if self.keep_raw:
            rec["raw"] = p.stdout[-20000:]
        return rec


def make_target(spec, a):
    kind = spec.split(":", 1)[0]
    if kind == "ollama":
        return OllamaTarget(spec, a)
    if kind == "cli":
        return CliTarget(spec, a)
    if kind in ("harness", "server", "anthropic", "openai", "gemini", "copilot", "github"):
        return HarnessTarget(spec.replace("github:", "copilot:", 1), a)
    sys.exit(f"Unknown target {spec!r}. See: python3 bench.py run --help")


# --------------------------------------------------------------------------
# Summaries and effectiveness
# --------------------------------------------------------------------------
def summarize(recs, prices=None):
    ok = [r for r in recs if "error" not in r]
    passed = sum(1 for r in ok if r.get("passed"))
    checked = sum(1 for r in ok if r.get("passed") is not None)
    s = {"prompts": len(recs), "errors": len(recs) - len(ok), "passed": passed, "checked": checked,
         "accuracy": round(passed / checked, 3) if checked else None,
         "operating_s": round(sum(r["operating_s"] for r in ok), 2)}
    for k in TOKEN_KEYS:
        vals = [r["tokens"].get(k) for r in ok if r["tokens"].get(k) is not None]
        s[k] = sum(vals) if vals else None
    ft = sorted(r["first_token_s"] for r in ok if r.get("first_token_s") is not None)
    tps = sorted(r["output_tok_per_s"] for r in ok if r.get("output_tok_per_s"))
    s["median_first_token_s"] = ft[len(ft) // 2] if ft else None
    s["median_output_tok_per_s"] = tps[len(tps) // 2] if tps else None
    # Effectiveness: right answers per minute of operating time, and tokens spent per right answer.
    s["correct_per_min"] = round(passed / (s["operating_s"] / 60), 2) if passed and s["operating_s"] else 0
    total_tok = (s["input"] or 0) + (s["output"] or 0)
    s["tokens_per_correct"] = round(total_tok / passed) if passed and total_tok else None
    cost = None
    if prices:
        p_in, p_out, p_cr, p_cw = (prices + [None, None])[:4]
        p_cr = p_in if p_cr is None else p_cr
        p_cw = p_in if p_cw is None else p_cw
        fresh = (s["input"] or 0) - (s["cache_read"] or 0) - (s["cache_write"] or 0)
        cost = (fresh * p_in + (s["cache_read"] or 0) * p_cr + (s["cache_write"] or 0) * p_cw
                + (s["output"] or 0) * p_out) / 1e6
    cli_cost = [r.get("cli_cost_usd") for r in ok if r.get("cli_cost_usd") is not None]
    if cost is None and cli_cost:
        cost = sum(cli_cost)
    s["cost_usd"] = round(cost, 5) if cost is not None else None
    s["cost_per_correct_usd"] = round(cost / passed, 5) if cost is not None and passed else None
    return s


def group_key(r):
    return f"{r.get('label') or '-'} | {r['target']}"


def v(x, nd=None):
    if x is None:
        return "-"
    return f"{x:.{nd}f}" if nd is not None and isinstance(x, (int, float)) else str(x)


def print_row(r):
    if "error" in r:
        sys.stderr.write(f"  {r['id']:<9} ERROR  {r['error'][:110]}\n")
        return
    t = r["tokens"]
    mark = {True: "PASS", False: "FAIL", None: " -- "}[r.get("passed")]
    sys.stderr.write(f"  {r['id']:<9} {mark}  in {v(t['input']):>6} out {v(t['output']):>5} cache r {v(t['cache_read']):>5}"
                     f" w {v(t['cache_write']):>5} reas {v(t['reasoning']):>5} | {r['operating_s']:6.2f} s"
                     f" | first {v(r.get('first_token_s'), 2):>5} s | {v(r.get('output_tok_per_s')):>6} tok/s"
                     f"{'' if r.get('passed') is not False else '  (' + r.get('why', '') + ')'}\n")


def print_summary_table(groups, prices):
    head = ("label | target", "pass", "time s", "input", "output", "cache r", "cache w", "reason",
            "first s", "tok/s", "right/min", "tok/right", "$")
    rows = []
    for key, recs in groups.items():
        s = summarize(recs, prices.get(recs[0]["target"]) if prices else None)
        rows.append((key, f"{s['passed']}/{s['checked']}", v(s["operating_s"], 1), v(s["input"]), v(s["output"]),
                     v(s["cache_read"]), v(s["cache_write"]), v(s["reasoning"]), v(s["median_first_token_s"], 2),
                     v(s["median_output_tok_per_s"]), v(s["correct_per_min"]), v(s["tokens_per_correct"]),
                     v(s["cost_usd"])))
    w = [max(len(str(x)) for x in col) for col in zip(head, *rows)]
    print()
    for row in (head,) + tuple(rows):
        print("  ".join(str(x).ljust(n) for x, n in zip(row, w)))
    print("\nright/min = correct answers per minute of operating time. tok/right = tokens spent per correct answer.")
    print("first s and tok/s are medians. '-' means this target does not report that number.")


# --------------------------------------------------------------------------
# HTML report (also used for the live page)
# --------------------------------------------------------------------------
CSS = """:root{--bg:#f6f4ee;--fg:#14213d;--card:#fff;--line:#d9d5c9;--acc:#137a86;--mute:#4a5568;--bad:#b42318;--good:#137a4a}
@media(prefers-color-scheme:dark){:root{--bg:#0f1b2d;--fg:#f2efe6;--card:#1a2b45;--line:#33496b;--acc:#2bb3c0;--mute:#a9b6c8;--bad:#f97066;--good:#47cd89}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:24px 0 8px}.mute{color:var(--mute)}
.wrap{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%}th,td{padding:5px 8px;border-bottom:1px solid var(--line);text-align:left;font-size:13px;white-space:nowrap}
td.num{text-align:right;font-variant-numeric:tabular-nums}.pass{color:var(--good);font-weight:700}.fail{color:var(--bad);font-weight:700}
.bar{display:inline-block;height:10px;background:var(--acc);border-radius:3px;vertical-align:middle;margin-right:6px}
details{margin:6px 0}pre{white-space:pre-wrap;font-size:12px;margin:4px 0}"""


def write_html(path, recs, prices, title, live=False):
    groups = {}
    for r in recs:
        groups.setdefault(group_key(r), []).append(r)
    sums = {k: summarize(g, prices.get(g[0]["target"]) if prices else None) for k, g in groups.items()}
    max_tps = max([s["median_output_tok_per_s"] or 0 for s in sums.values()] + [1])
    max_cpm = max([s["correct_per_min"] or 0 for s in sums.values()] + [1])
    rows = ""
    for k, s in sums.items():
        rows += ("<tr><td>%s</td><td class=num>%s/%s</td><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td>"
                 "<td class=num>%s</td><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td>"
                 "<td><span class=bar style='width:%dpx'></span>%s</td><td><span class=bar style='width:%dpx'></span>%s</td>"
                 "<td class=num>%s</td><td class=num>%s</td></tr>") % (
            html.escape(k), s["passed"], s["checked"], v(s["operating_s"], 1), v(s["input"]), v(s["output"]),
            v(s["cache_read"]), v(s["cache_write"]), v(s["reasoning"]), v(s["median_first_token_s"], 2),
            int(80 * (s["median_output_tok_per_s"] or 0) / max_tps), v(s["median_output_tok_per_s"]),
            int(80 * (s["correct_per_min"] or 0) / max_cpm), v(s["correct_per_min"]),
            v(s["tokens_per_correct"]), v(s["cost_usd"]))
    detail = ""
    for r in recs:
        if "error" in r:
            detail += "<tr><td>%s</td><td>%s</td><td class=fail colspan=9>ERROR %s</td></tr>" % (
                html.escape(group_key(r)), html.escape(r["id"]), html.escape(r["error"][:200]))
            continue
        t = r["tokens"]
        mark = {True: "<span class=pass>PASS</span>", False: "<span class=fail>FAIL</span>", None: "-"}[r.get("passed")]
        detail += ("<tr><td>%s</td><td>%s</td><td>%s</td><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td>"
                   "<td class=num>%s</td><td class=num>%s</td><td class=num>%s</td><td class=num>%s</td>"
                   "<td><details><summary>prompt and response</summary><pre>%s</pre><pre>%s</pre></details></td></tr>") % (
            html.escape(group_key(r)), html.escape(r["id"]), mark, v(r["operating_s"], 2), v(t["input"]), v(t["output"]),
            v(t["cache_read"]), v(t["cache_write"]), v(t["reasoning"]), v(r.get("output_tok_per_s")),
            html.escape(r["prompt"]), html.escape(r["response"][:4000]))
    refresh = '<meta http-equiv="refresh" content="2">' if live else ""
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{refresh}
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>
<h1>{html.escape(title)}</h1><p class="mute">{len(recs)} prompt runs. {"Live: this page reloads every 2 seconds." if live else "Written " + time.strftime("%Y-%m-%d %H:%M")}</p>
<h2>Per session (one row per label and target)</h2><div class="wrap"><table><tr><th>label | target</th><th>pass</th><th>time s</th><th>input</th><th>output</th><th>cache read</th><th>cache write</th><th>reasoning</th><th>first token s</th><th>output tok/s</th><th>correct/min</th><th>tokens/correct</th><th>$</th></tr>{rows}</table></div>
<p class="mute">Operating time counts only the model's work. '-' means the target does not report that number. Medians for first token and tok/s.</p>
<h2>Per prompt</h2><div class="wrap"><table><tr><th>label | target</th><th>prompt</th><th>check</th><th>time s</th><th>input</th><th>output</th><th>cache read</th><th>cache write</th><th>reasoning</th><th>tok/s</th><th></th></tr>{detail}</table></div>
</body></html>"""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(doc)
    os.replace(tmp, path)


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------
def load_prompts(path, only):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(json.loads(line))
    if only:
        keep = set(only.split(","))
        out = [p for p in out if p["id"] in keep]
    return out


def parse_prices(items):
    prices = {}
    for it in items or []:
        target, _, nums = it.rpartition("=")
        prices[target] = [float(x) for x in nums.split(",")]
    return prices


def cmd_run(a):
    a.key_files = {}
    for kf in a.key_file or []:
        prov, _, path = kf.partition("=")
        a.key_files[prov] = path
    prompts = load_prompts(a.prompts, a.only)
    system = DEFAULT_SYSTEM
    if a.system_file:
        with open(a.system_file, encoding="utf-8") as f:
            system = f.read()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    run_id = uuid.uuid4().hex[:8]
    prices = parse_prices(a.price)
    all_recs = []
    for spec in a.target:
        print(f"\n== {spec}" + (f"  [label: {a.label}]" if a.label else ""), file=sys.stderr)
        try:
            tgt = make_target(spec, a)
        except SystemExit as e:
            print(f"  skipped: {e}", file=sys.stderr)
            continue
        print(f"   device: {tgt.device}. {len(prompts)} prompts x {a.repeat}.", file=sys.stderr)
        if a.warmup and not spec.startswith("cli:"):
            try:  # the first call loads the model; do not let that count against prompt 1
                tgt.call(system, "Say OK.", Live("warm-up", not a.quiet))
            except Exception:
                pass
        for rep in range(a.repeat):
            for p in prompts:
                sysmsg = harness.TOOL_PROMPT if p.get("system") == "tools" else system
                live = Live(f"{p['id']:<9}", not a.quiet)
                live.start()
                try:
                    rec = tgt.call(sysmsg, p["prompt"], live)
                    rec["passed"], rec["why"] = check_answer(rec["response"], p.get("check"))
                except Exception as e:
                    rec = {"prompt": p["prompt"], "response": "", "error": str(e), "operating_s": 0,
                           "tokens": {k: None for k in TOKEN_KEYS}}
                finally:
                    live.done()
                rec.update({"run": run_id, "label": a.label, "target": spec, "id": p["id"], "repeat": rep + 1,
                            "time": time.strftime("%Y-%m-%dT%H:%M:%S")})
                all_recs.append(rec)
                with open(a.out, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print_row(rec)
                if a.show_text and rec.get("response"):
                    print("      " + rec["response"].strip().replace("\n", "\n      ")[:800], file=sys.stderr)
                if a.live_html:
                    write_html(a.live_html, all_recs, prices, "Lab 2 benchmark (live)", live=True)
    groups = {}
    for r in all_recs:
        groups.setdefault(group_key(r), []).append(r)
    if groups:
        print_summary_table(groups, prices)
        print(f"\nSaved {len(all_recs)} records to {a.out}. Make a report: python3 bench.py report {a.out}")
    if a.live_html:
        write_html(a.live_html, all_recs, prices, "Lab 2 benchmark")


def read_records(paths):
    recs = []
    for p in paths:
        for path in glob.glob(p) or [p]:
            with open(path, encoding="utf-8") as f:
                recs += [json.loads(line) for line in f if line.strip()]
    return recs


def cmd_report(a):
    recs = read_records(a.files)
    prices = parse_prices(a.price)
    write_html(a.out, recs, prices, a.title)
    groups = {}
    for r in recs:
        groups.setdefault(group_key(r), []).append(r)
    print_summary_table(groups, prices)
    print(f"\nWrote {a.out}. Open it in your browser.")


def cmd_compare(a):
    """Two runs of the same prompts (for example CPU and GPU): how much faster or cheaper is the second?"""
    groups = []
    for path in a.files:
        recs = read_records([path])
        groups.append((path, recs, summarize(recs)))
    base = groups[0][2]
    print(f"{'run':<40} {'pass':>6} {'time s':>8} {'first s':>8} {'tok/s':>8} {'speedup':>8}")
    for path, recs, s in groups:
        speed = (base["operating_s"] / s["operating_s"]) if s["operating_s"] else 0
        print(f"{os.path.basename(path):<40} {s['passed']:>3}/{s['checked']:<2} {v(s['operating_s'], 1):>8} "
              f"{v(s['median_first_token_s'], 2):>8} {v(s['median_output_tok_per_s']):>8} {speed:>7.2f}x")
    print("\nspeedup = the first run's operating time divided by this run's. Same answers? Compare the pass column.")


def main():
    ap = argparse.ArgumentParser(description="Lab 2 benchmark: models and harnesses",
                                 epilog=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run the prompts against one or more targets")
    r.add_argument("--target", action="append", required=True, help="see the list above; repeat to compare")
    r.add_argument("--prompts", default=os.path.join(HERE, "prompts.jsonl"))
    r.add_argument("--only", help="comma-separated prompt ids to run")
    r.add_argument("--repeat", type=int, default=1, help="run every prompt this many times")
    r.add_argument("--label", default="", help="a name for this run, e.g. cpu or gpu")
    r.add_argument("--out", default=os.path.join("results", "bench-%s.jsonl" % time.strftime("%Y%m%d-%H%M%S")))
    r.add_argument("--live-html", help="also write a self-refreshing web page with the results so far")
    r.add_argument("--system-file", help="a long system prompt (bench_context.md) to make prompt caching visible")
    r.add_argument("--temperature", type=float, default=0.0)
    r.add_argument("--max-tokens", type=int, default=512)
    r.add_argument("--seed", type=int, default=42)
    r.add_argument("--ctx", type=int, default=4096)
    r.add_argument("--effort", choices=["low", "medium", "high"], help="harness targets with Qwen3: thinking off or on")
    r.add_argument("--think", type=lambda x: x.lower() == "true", default=None, help="ollama: true or false")
    r.add_argument("--gpu-layers", type=int, default=0, help="harness targets: -1 = GPU, 0 = CPU (default)")
    r.add_argument("--threads", type=int)
    r.add_argument("--ollama-url", default="http://localhost:11434")
    r.add_argument("--ollama-num-gpu", type=int, help="ollama: 0 forces the CPU; leave out to let Ollama decide")
    r.add_argument("--cache", action="store_true", help="anthropic: mark the system prompt for prompt caching")
    r.add_argument("--key-file", action="append", help="PROVIDER=PATH, e.g. anthropic=~/.config/ai-keys/anthropic")
    r.add_argument("--price", action="append", help="TARGET=IN,OUT[,CACHE_READ,CACHE_WRITE] in dollars per million tokens")
    r.add_argument("--cli-timeout", type=int, default=300)
    r.add_argument("--raw", action="store_true", help="cli targets: keep the raw CLI output in the results")
    r.add_argument("--no-warmup", dest="warmup", action="store_false")
    r.add_argument("--show-text", action="store_true", help="print each response")
    r.add_argument("--quiet", action="store_true", help="no live line")
    r.set_defaults(fn=cmd_run)
    p = sub.add_parser("report", help="make an HTML report from one or more results files")
    p.add_argument("files", nargs="+")
    p.add_argument("--out", default="report.html")
    p.add_argument("--title", default="Lab 2 benchmark report")
    p.add_argument("--price", action="append")
    p.set_defaults(fn=cmd_report)
    c = sub.add_parser("compare", help="compare runs, for example CPU against GPU")
    c.add_argument("files", nargs="+")
    c.set_defaults(fn=cmd_compare)
    a = ap.parse_args()
    if getattr(a, "key_file", None):
        a.key_file = [os.path.expanduser(x.split("=", 1)[0]) + "=" + os.path.expanduser(x.split("=", 1)[1]) for x in a.key_file]
    a.fn(a)


if __name__ == "__main__":
    main()
