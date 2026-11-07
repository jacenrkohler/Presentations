#!/usr/bin/env python3
"""harness.py - a small LLM harness you can read in one sitting.

A harness is the program around the model. The model only turns tokens into
the next token. Everything else is the harness: the chat history, the system
prompt, the settings, and (in later labs) the tools and the logs.

  python3 harness.py chat  --model models/Qwen3-4B-Q4_K_M.gguf     talk to a local model (GGUF)
  python3 harness.py chat  --model models/qwen2.5-0.5b-instruct     a safetensors folder (Hugging Face)
  python3 harness.py chat  --model models/qwen2.5-0.5b-onnx         an ONNX folder (ONNX Runtime)
  python3 harness.py ask   --model ... "Why is the sky blue?"       one question
  python3 harness.py chat  --backend anthropic                      talk to a cloud model (pick from a list)
  python3 harness.py serve --model ... --port 13370                 OpenAI-style server
  python3 harness.py chat  --model ... --tools --tool-dir .         tool loop
  python3 harness.py models --backend anthropic                     list the model ids your key can use
  python3 harness.py image classify photo.jpg                       what is in this picture? (Part 2c)
  python3 harness.py image generate "a robot reading a book"        draw a picture (Part 2c)

Backends (--backend):
  auto       the default: picks llamacpp, transformers or onnx from the --model path
  llamacpp   load a GGUF file inside this process (needs llama-cpp-python)
  transformers  load a Hugging Face safetensors folder (needs torch and transformers)
  onnx       load an ONNX export (needs onnxruntime and transformers for the tokenizer)
  server     any local OpenAI-compatible server: Ollama, KoboldCpp, llama.cpp
             (--url http://localhost:11434/v1  --model qwen3:4b)
  anthropic  Claude, with an Anthropic API key
  openai     OpenAI, with an OpenAI API key
  gemini     Google Gemini, with a Gemini API key
  github     "Copilot" in Part 3d: GitHub Models, with a GitHub token. GitHub Copilot itself has
             no public chat API; GitHub Models is how a GitHub account reaches models by API.
  copilot    the same as github
  echo       no model at all. Used to test the harness.

API keys (checked in this order):
  1. --key-file PATH   a file only you can read (mode 600). The harness refuses a file other users can read.
  2. an environment variable: ANTHROPIC_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, GITHUB_TOKEN
  3. a hidden prompt (nothing you type is shown or saved to shell history)
There is deliberately no --api-key option: anything on the command line is visible to every
user on the machine through `ps`, and is saved in shell history.
Keys are held in memory only. They are never written to disk or printed.

Standard library only for the cloud backends. Local backends need: llama-cpp-python (GGUF),
torch + transformers (safetensors), onnxruntime + transformers (ONNX), diffusers (image generate).
GPU: add --gpu-layers -1 (or a number of layers for GGUF). 0, the default, means CPU only.
"""
import argparse
import ast
import csv
import datetime
import io
import socket
import getpass
import hmac
import json
import operator
import re
import os
import secrets
import stat
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --------------------------------------------------------------------------
# Settings
# --------------------------------------------------------------------------
# "Effort" is a harness-level preset for LOCAL Qwen3 models, not a model feature.
# Qwen3 has a thinking mode that /think and /no_think switch on and off, so effort
# maps to that switch plus a cap on how many tokens it may write. Cloud models
# have their own settings, so effort is ignored for them.
EFFORT = {
    "low":    {"think": False, "max_tokens": 256},
    "medium": {"think": False, "max_tokens": 1024},
    "high":   {"think": True,  "max_tokens": 2048},
}

DEFAULTS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_tokens": 512,
    "seed": -1,
    "repeat_penalty": 1.1,
    "stop": [],
    "ctx": 4096,
    "effort": None,
    "system": "You are a helpful assistant. Keep answers short.",
}
INT_KEYS = {"top_k", "max_tokens", "seed", "ctx"}
FLOAT_KEYS = {"temperature", "top_p", "repeat_penalty"}


def apply_effort(settings, backend):
    s = dict(settings)
    e = s.get("effort")
    if e and backend.local:
        s["max_tokens"] = EFFORT[e]["max_tokens"]
        s["think"] = EFFORT[e]["think"]
    return s


def with_think_switch(messages, settings):
    """Qwen3 reads /think or /no_think at the end of the last user message."""
    if "think" not in settings:
        return messages
    out = [dict(m) for m in messages]
    for m in reversed(out):
        if m["role"] == "user":
            m["content"] = m["content"] + (" /think" if settings["think"] else " /no_think")
            break
    return out


# --------------------------------------------------------------------------
# Backends. Each has .stream(messages, settings) which yields pieces of text.
# messages is a list of {"role": "system"|"user"|"assistant", "content": str}.
# --------------------------------------------------------------------------
def http_lines(req, what):
    """Open a streaming HTTP request and yield decoded lines. Explain errors."""
    secrets = [v for k, v in req.header_items() if k.lower() in ("authorization", "x-api-key", "x-goog-api-key")]
    secrets = [x.replace("Bearer ", "") for x in secrets if len(x) > 8]
    try:
        resp = urllib.request.urlopen(req, timeout=600)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:400]
        for sec in secrets:  # providers sometimes echo part of a bad key
            body = body.replace(sec, "[key hidden]")
        hint = ""
        if e.code in (401, 403):
            hint = "\nThe key was refused. Check it is correct, has no extra spaces, and is allowed to use this model."
        elif e.code == 404:
            hint = "\nThe model name was not found. Check the provider's model list."
        elif e.code == 429:
            hint = "\nRate limit or no credit. Check the account's usage and billing."
        sys.exit(f"{what} returned HTTP {e.code}: {body}{hint}")
    except (urllib.error.URLError, ConnectionError) as e:
        sys.exit(f"Could not reach {what}: {e}")
    with resp:
        for raw in resp:
            yield raw.decode("utf-8", "replace").strip()


def sse_json(lines):
    """Yield the parsed JSON of each 'data:' line in a server-sent-events stream."""
    for line in lines:
        if not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            return
        try:
            yield json.loads(data)
        except ValueError:
            continue


class EchoBackend:
    name, local = "echo", True

    def __init__(self):
        self.model, self.device = "echo", "cpu"

    def stream(self, messages, s):
        last = [m for m in messages if m["role"] == "user"][-1]["content"]
        words = ("(echo) You said: " + last).split(" ")[: s["max_tokens"]]
        # Echo has no tokenizer: one word counts as one token.
        self.usage = {"input": sum(len(m["content"].split()) for m in messages), "output": len(words),
                      "cache_read": 0, "cache_write": None, "reasoning": 0, "source": "counted (words)"}
        for i, w in enumerate(words):
            time.sleep(0.01)
            yield w + (" " if i < len(words) - 1 else "")


class LlamaCppBackend:
    name, local = "llamacpp", True

    def __init__(self, model_path, ctx, threads=None, gpu_layers=0):
        try:
            import llama_cpp
            from llama_cpp import Llama
        except ImportError:
            sys.exit("llama-cpp-python is not installed. Run: python3 -m pip install -r requirements.txt")
        if not os.path.exists(model_path):
            sys.exit(f"Model file not found: {model_path}\nRun the prefetch script or download it first.")
        self.model = os.path.basename(model_path)
        self.llama_cpp = llama_cpp
        gpu_layers = gpu_layers or 0
        if gpu_layers:
            # Only a GPU build of llama-cpp-python can offload (CUDA, Metal, Vulkan or ROCm).
            # The default CPU build ignores the request, so say so instead of failing silently.
            try:
                ok = llama_cpp.llama_supports_gpu_offload()
            except Exception:
                ok = True
            if not ok:
                print("Note: this llama-cpp-python build is CPU only, so --gpu-layers is ignored. "
                      "See Lab 1, Part 0e (GPU software).", file=sys.stderr)
                gpu_layers = 0
        self.llm = Llama(model_path=model_path, n_ctx=ctx, n_threads=threads or os.cpu_count(),
                         n_gpu_layers=gpu_layers, verbose=False)
        self.device = "gpu" if gpu_layers else "cpu"

    def count_tokens(self, text):
        return len(self.llm.tokenize(text.encode("utf-8"), add_bos=False, special=False)) if text else 0

    def _prompt_tokens(self, messages):
        """Render the chat template from the GGUF file (as llama-cpp-python does) and tokenize it."""
        from llama_cpp.llama_chat_format import Jinja2ChatFormatter
        meta = self.llm.metadata
        tmpl = meta.get("tokenizer.chat_template")
        if not tmpl:
            return None
        bos = self.llm.detokenize([self.llm.token_bos()]).decode("utf-8", "ignore") if self.llm.token_bos() >= 0 else ""
        eos = self.llm.detokenize([self.llm.token_eos()]).decode("utf-8", "ignore") if self.llm.token_eos() >= 0 else ""
        prompt = Jinja2ChatFormatter(template=tmpl, eos_token=eos, bos_token=bos)(messages=messages).prompt
        add_bos = str(meta.get("tokenizer.ggml.add_bos_token", "true")).lower() == "true" and not (bos and prompt.startswith(bos))
        return self.llm.tokenize(prompt.encode("utf-8"), add_bos=add_bos, special=True)

    def stream(self, messages, s):
        # Usage. llama.cpp keeps the previous conversation in its KV cache, so a new turn only has
        # to process the tokens after the longest shared prefix: that prefix is the "cache read".
        u = self.usage = {"input": None, "output": 0, "cache_read": 0, "cache_write": None,
                          "reasoning": 0, "source": "counted"}
        try:
            prev = list(self.llm._input_ids[: self.llm.n_tokens])
            new = self._prompt_tokens(messages)
            if new is not None:
                u["input"] = len(new)
                shared = 0
                for x, y in zip(prev, new[:-1]):
                    if x != y:
                        break
                    shared += 1
                u["cache_read"] = shared
                u["cache_write"] = len(new) - shared
        except Exception:
            pass
        text = []
        for chunk in self.llm.create_chat_completion(
            messages=messages, stream=True,
            temperature=s["temperature"], top_p=s["top_p"], top_k=s["top_k"],
            max_tokens=s["max_tokens"], repeat_penalty=s["repeat_penalty"],
            seed=None if s["seed"] < 0 else s["seed"], stop=s["stop"] or None,
        ):
            piece = chunk["choices"][0].get("delta", {}).get("content")
            if piece:
                text.append(piece)
                yield piece
        out = "".join(text)
        u["output"] = self.count_tokens(out)
        u["reasoning"] = self.count_tokens(think_text(out))
        if u["input"] is None:  # no chat template in the file: estimate from the context length
            u["input"] = max(self.llm.n_tokens - u["output"], 0)
            u["source"] = "counted (input estimated)"


def estimate_tokens(text):
    """About 4 characters per token for English text. Used only when nothing better is available."""
    return (len(text) + 3) // 4 if text else 0


def think_text(text):
    """The reasoning part of a reply: text inside <think>...</think> (Qwen3, DeepSeek-R1 style)."""
    if "<think>" not in text:
        return ""
    body = text.split("<think>", 1)[1]
    return body.split("</think>", 1)[0]


def gpu_device(want):
    """Pick a torch device: a GPU if asked for and present, otherwise the CPU."""
    import torch
    if want:
        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
        print("Note: no GPU found by torch, so this runs on the CPU.", file=sys.stderr)
    return "cpu"


def cut_at_stop(pieces, stops):
    """Yield text pieces, but end the reply as soon as a stop sequence appears."""
    if not stops:
        yield from pieces
        return
    buf, keep = "", max(len(x) for x in stops)
    for p in pieces:
        buf += p
        hit = min((buf.find(x) for x in stops if x in buf), default=-1)
        if hit >= 0:
            if buf[:hit]:
                yield buf[:hit]
            return
        if len(buf) > keep:
            yield buf[:-keep]
            buf = buf[-keep:]
    if buf:
        yield buf


def find_hf_folder(path):
    """The folder that holds config.json and the tokenizer for a safetensors or ONNX model."""
    folder = path if os.path.isdir(path) else os.path.dirname(path)
    for d in (folder, os.path.dirname(folder)):
        if os.path.exists(os.path.join(d, "config.json")):
            return d
    sys.exit(f"No config.json next to {path}. A Hugging Face model needs its whole folder, not just the weights.")


class TransformersBackend:
    """A Hugging Face model in safetensors format, run with PyTorch."""
    name, local = "transformers", True

    def __init__(self, path, gpu_layers=0, threads=None):
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError:
            sys.exit("This backend needs torch and transformers: python3 -m pip install -r requirements-hf.txt")
        folder = find_hf_folder(path)
        if threads:
            torch.set_num_threads(threads)
        self.torch, self.device = torch, gpu_device(gpu_layers)
        self.torch_device = self.device
        self.model = os.path.basename(os.path.abspath(folder))
        self.tok = AutoTokenizer.from_pretrained(folder, local_files_only=True)
        # use_safetensors=True: never fall back to a pickle (.bin) file, which could run code.
        self.llm = AutoModelForCausalLM.from_pretrained(
            folder, local_files_only=True, use_safetensors=True,
            dtype=torch.float16 if self.device != "cpu" else torch.float32).to(self.device)
        self.llm.eval()
        self.device = "gpu" if self.torch_device != "cpu" else "cpu"

    def count_tokens(self, text):
        return len(self.tok.encode(text, add_special_tokens=False)) if text else 0

    def stream(self, messages, s):
        from transformers import TextIteratorStreamer
        torch = self.torch
        ids = self.tok.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(self.torch_device)
        streamer = TextIteratorStreamer(self.tok, skip_prompt=True, skip_special_tokens=True)
        if s["seed"] >= 0:
            torch.manual_seed(s["seed"])
        sample = s["temperature"] > 0
        kw = dict(input_ids=ids, attention_mask=torch.ones_like(ids), max_new_tokens=s["max_tokens"],
                  do_sample=sample, repetition_penalty=s["repeat_penalty"], streamer=streamer,
                  pad_token_id=self.tok.pad_token_id or self.tok.eos_token_id)
        if sample:
            kw.update(temperature=s["temperature"], top_p=s["top_p"], top_k=s["top_k"])
        result = {}

        def run():
            result["out"] = self.llm.generate(**kw)
        t = threading.Thread(target=run, daemon=True)
        t.start()
        text = []
        for piece in cut_at_stop(streamer, s["stop"]):
            text.append(piece)
            yield piece
        t.join(timeout=5)
        n_in = int(ids.shape[1])
        n_out = int(result["out"].shape[1]) - n_in if "out" in result else self.count_tokens("".join(text))
        # Transformers rebuilds the KV cache for every turn: nothing is read from an old cache.
        self.usage = {"input": n_in, "output": n_out, "cache_read": 0, "cache_write": n_in,
                      "reasoning": self.count_tokens(think_text("".join(text))), "source": "counted"}


class OnnxBackend:
    """An ONNX export of a chat model, run with ONNX Runtime. The generation loop is written
    out here so you can see it: run the graph, pick one token, feed it back, repeat."""
    name, local = "onnx", True

    def __init__(self, path, gpu_layers=0, threads=None):
        try:
            import onnxruntime as ort
            from transformers import AutoTokenizer
        except ImportError:
            sys.exit("This backend needs onnxruntime and transformers: python3 -m pip install -r requirements.txt")
        import numpy as np
        self.np = np
        if os.path.isdir(path):
            import glob
            cands = sorted(glob.glob(os.path.join(path, "*.onnx")) + glob.glob(os.path.join(path, "onnx", "*.onnx")))
            if not cands:
                sys.exit(f"No .onnx file in {path}")
            path = cands[0]
        folder = find_hf_folder(path)
        name_dir = os.path.abspath(folder)
        if os.path.basename(name_dir) == "onnx":
            name_dir = os.path.dirname(name_dir)
        self.model = os.path.basename(name_dir)
        self.tok = AutoTokenizer.from_pretrained(folder, local_files_only=True)
        with open(os.path.join(folder, "config.json"), encoding="utf-8") as f:
            cfg = json.load(f)
        self.eos = cfg.get("eos_token_id")
        self.eos = set(self.eos if isinstance(self.eos, list) else [self.eos]) | {self.tok.eos_token_id}
        providers = ["CPUExecutionProvider"]
        if gpu_layers:
            have = ort.get_available_providers()
            gpu = [p for p in ("CUDAExecutionProvider", "DmlExecutionProvider", "CoreMLExecutionProvider") if p in have]
            if gpu:
                providers = gpu[:1] + providers
            else:
                print("Note: this onnxruntime has no GPU provider, so this runs on the CPU. "
                      "See Lab 1, Part 0e (GPU software).", file=sys.stderr)
        so = ort.SessionOptions()
        if threads:
            so.intra_op_num_threads = threads
        self.sess = ort.InferenceSession(path, so, providers=providers)
        self.device = "gpu" if self.sess.get_providers()[0] != "CPUExecutionProvider" else "cpu"
        self.inputs = {i.name: i for i in self.sess.get_inputs()}
        self.outputs = [o.name for o in self.sess.get_outputs()]
        self.past = [n for n in self.inputs if n.startswith("past_key_values")]
        heads = cfg.get("num_key_value_heads", cfg.get("num_attention_heads"))
        self.head_dim = cfg.get("head_dim") or cfg["hidden_size"] // cfg["num_attention_heads"]
        self.kv_heads = heads
        kv_type = self.inputs[self.past[0]].type if self.past else "tensor(float)"
        self.kv_dtype = np.float16 if "float16" in kv_type else np.float32

    def count_tokens(self, text):
        return len(self.tok.encode(text, add_special_tokens=False)) if text else 0

    def _sample(self, logits, s, seen, rng):
        np = self.np
        logits = logits.astype(np.float64)
        if s["repeat_penalty"] and s["repeat_penalty"] != 1.0 and seen:
            idx = np.array(sorted(seen))
            vals = logits[idx]
            logits[idx] = np.where(vals > 0, vals / s["repeat_penalty"], vals * s["repeat_penalty"])
        if s["temperature"] <= 0:
            return int(logits.argmax())
        logits = logits / s["temperature"]
        if s["top_k"] and s["top_k"] > 0:
            kth = np.sort(logits)[-min(s["top_k"], logits.size)]
            logits[logits < kth] = -np.inf
        p = np.exp(logits - logits.max())
        p /= p.sum()
        order = np.argsort(-p)
        keep = order[: int(np.searchsorted(np.cumsum(p[order]), s["top_p"])) + 1]
        q = np.zeros_like(p)
        q[keep] = p[keep]
        return int(rng.choice(p.size, p=q / q.sum()))

    def stream(self, messages, s):
        np = self.np
        rng = np.random.default_rng(None if s["seed"] < 0 else s["seed"])
        ids = self.tok.apply_chat_template(messages, add_generation_prompt=True)
        if hasattr(ids, "keys"):
            ids = ids["input_ids"]
        ids = list(ids)
        past = {n: np.zeros((1, self.kv_heads, 0, self.head_dim), dtype=self.kv_dtype) for n in self.past}
        step_ids, total = ids, len(ids)
        seen, out_ids, printed = set(ids), [], ""

        def pieces():
            nonlocal step_ids, total, past, printed
            for _ in range(s["max_tokens"]):
                feed = {"input_ids": np.array([step_ids], dtype=np.int64)}
                if "attention_mask" in self.inputs:
                    feed["attention_mask"] = np.ones((1, total), dtype=np.int64)
                if "position_ids" in self.inputs:
                    feed["position_ids"] = np.arange(total - len(step_ids), total, dtype=np.int64)[None, :]
                feed.update(past)
                res = dict(zip(self.outputs, self.sess.run(self.outputs, feed)))
                nxt = self._sample(res["logits"][0, -1], s, seen, rng)
                if nxt in self.eos:
                    return
                past = {n: res[n.replace("past_key_values", "present")] for n in self.past}
                seen.add(nxt)
                out_ids.append(nxt)
                text = self.tok.decode(out_ids, skip_special_tokens=True)
                if len(text) > len(printed) and not text.endswith("\ufffd"):
                    yield text[len(printed):]
                    printed = text
                step_ids, total = [nxt], total + 1
        text = []
        for piece in cut_at_stop(pieces(), s["stop"]):
            text.append(piece)
            yield piece
        # The loop above builds a fresh KV cache ("past") for every turn.
        self.usage = {"input": len(ids), "output": len(out_ids), "cache_read": 0, "cache_write": len(ids),
                      "reasoning": self.count_tokens(think_text("".join(text))), "source": "counted"}


def detect_backend(path):
    """auto: choose a local backend from what the --model path contains."""
    import glob
    if not path:
        sys.exit("Give a model with --model: a .gguf file, a safetensors folder, or an ONNX folder.\n"
                 "For a cloud model add --backend anthropic, openai, gemini or github.")
    if not os.path.exists(path):
        sys.exit(f"Not found: {path}. For a cloud or server model, add --backend.")
    if path.lower().endswith(".gguf") or (os.path.isdir(path) and glob.glob(os.path.join(path, "*.gguf"))):
        return "llamacpp"
    if path.lower().endswith(".onnx") or (os.path.isdir(path) and (glob.glob(os.path.join(path, "*.onnx")) or glob.glob(os.path.join(path, "onnx", "*.onnx")))):
        return "onnx"
    if path.lower().endswith(".safetensors") or (os.path.isdir(path) and glob.glob(os.path.join(path, "*.safetensors"))):
        return "transformers"
    sys.exit(f"Cannot tell what kind of model {path} is. Use --backend llamacpp, transformers or onnx.\n"
             "This harness does not load .bin/.pt pickle files: loading one can run code hidden inside it.")


class OpenAICompatBackend:
    """Anything that speaks the OpenAI chat API: Ollama, KoboldCpp, llama.cpp, OpenAI, GitHub Models."""

    def __init__(self, name, url, model, key="none", local=True, path="/chat/completions"):
        self.name, self.local = name, local
        self.device = "server" if local else "cloud"
        self.url, self.model, self.key, self.path = url.rstrip("/"), model, key, path

    def stream(self, messages, s):
        body = {"model": self.model, "messages": messages, "stream": True,
                "temperature": s["temperature"], "top_p": s["top_p"]}
        # Newer OpenAI models want max_completion_tokens and reject some other settings.
        body["max_completion_tokens" if self.name == "openai" else "max_tokens"] = s["max_tokens"]
        if s["stop"]:
            body["stop"] = s["stop"]
        if s["seed"] >= 0:
            body["seed"] = s["seed"]
        # Ask for token counts at the end of the stream (OpenAI, GitHub Models, Ollama, llama.cpp).
        body["stream_options"] = {"include_usage": True}
        req = urllib.request.Request(
            self.url + self.path, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + self.key})
        u = self.usage = {"input": None, "output": None, "cache_read": None, "cache_write": None,
                          "reasoning": None, "source": "reported"}
        text, thinking = [], []
        for obj in sse_json(http_lines(req, self.url)):
            for ch in obj.get("choices", []):
                delta = ch.get("delta") or {}
                think = delta.get("reasoning_content") or delta.get("reasoning")
                if think:
                    thinking.append(think)
                piece = delta.get("content")
                if piece:
                    text.append(piece)
                    yield piece
            us = obj.get("usage")
            if us:
                u["input"] = us.get("prompt_tokens")
                u["output"] = us.get("completion_tokens")
                u["cache_read"] = (us.get("prompt_tokens_details") or {}).get("cached_tokens")
                u["reasoning"] = (us.get("completion_tokens_details") or {}).get("reasoning_tokens")
            tm = obj.get("timings")  # llama.cpp server
            if tm:
                if tm.get("cache_n") is not None:
                    u["cache_read"] = tm["cache_n"]
                if tm.get("prompt_n") is not None:
                    u["cache_write"] = tm["prompt_n"]
                    if u["input"] is None:
                        u["input"] = tm["prompt_n"] + (tm.get("cache_n") or 0)
                        u["output"] = tm.get("predicted_n")
        if u["reasoning"] is None and thinking:
            u["reasoning"] = estimate_tokens("".join(thinking))
            u["source"] = "reported (reasoning estimated)"
        if u["output"] is None:
            u["input"] = estimate_tokens(" ".join(m["content"] for m in messages))
            u["output"] = estimate_tokens("".join(text))
            u["source"] = "estimated (the server sent no usage)"


class AnthropicBackend:
    name, local = "anthropic", False

    def __init__(self, model, key, cache=False):
        self.model, self.key, self.cache, self.device = model, key, cache, "cloud"

    def stream(self, messages, s):
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        msgs = [m for m in messages if m["role"] != "system"]
        body = {"model": self.model, "max_tokens": s["max_tokens"], "stream": True,
                "messages": msgs,
                # Anthropic allows temperature from 0 to 1.
                "temperature": min(max(s["temperature"], 0.0), 1.0)}
        if system:
            # --cache marks the system prompt for Anthropic's prompt cache (it must be long: over
            # about 1,024 tokens for most models). The first call writes the cache, later calls read it.
            body["system"] = [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}] if self.cache else system
        if s["stop"]:
            body["stop_sequences"] = s["stop"]
        u = self.usage = {"input": None, "output": None, "cache_read": 0, "cache_write": 0,
                          "reasoning": None, "source": "reported"}
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-api-key": self.key,
                     "anthropic-version": "2023-06-01"})
        for obj in sse_json(http_lines(req, "api.anthropic.com")):
            if obj.get("type") == "message_start":
                mu = obj.get("message", {}).get("usage", {})
                u["cache_read"] = mu.get("cache_read_input_tokens") or 0
                u["cache_write"] = mu.get("cache_creation_input_tokens") or 0
                # Anthropic's input_tokens excludes cached tokens; count the whole prompt here.
                u["input"] = (mu.get("input_tokens") or 0) + u["cache_read"] + u["cache_write"]
            elif obj.get("type") == "message_delta":
                u["output"] = obj.get("usage", {}).get("output_tokens", u["output"])
            if obj.get("type") == "content_block_delta":
                piece = obj.get("delta", {}).get("text")
                if piece:
                    yield piece
            elif obj.get("type") == "error":
                sys.exit("Anthropic error: " + json.dumps(obj.get("error")))


class GeminiBackend:
    name, local = "gemini", False

    def __init__(self, model, key):
        self.model, self.key, self.device = model, key, "cloud"

    def stream(self, messages, s):
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        contents = [{"role": "model" if m["role"] == "assistant" else "user",
                     "parts": [{"text": m["content"]}]}
                    for m in messages if m["role"] != "system"]
        gen = {"temperature": s["temperature"], "topP": s["top_p"], "topK": s["top_k"],
               "maxOutputTokens": s["max_tokens"]}
        if s["stop"]:
            gen["stopSequences"] = s["stop"]
        body = {"contents": contents, "generationConfig": gen}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        model = urllib.parse.quote(self.model, safe="")
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?alt=sse",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "x-goog-api-key": self.key})
        u = self.usage = {"input": None, "output": None, "cache_read": None, "cache_write": None,
                          "reasoning": None, "source": "reported"}
        for obj in sse_json(http_lines(req, "generativelanguage.googleapis.com")):
            um = obj.get("usageMetadata")
            if um:
                u["input"] = um.get("promptTokenCount")
                u["cache_read"] = um.get("cachedContentTokenCount", 0)
                u["reasoning"] = um.get("thoughtsTokenCount", 0)
                # Gemini counts thinking separately; output here includes it, as OpenAI's does.
                u["output"] = (um.get("candidatesTokenCount") or 0) + (u["reasoning"] or 0)
            for cand in obj.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    if part.get("text"):
                        yield part["text"]


CLOUD = {  # backend name -> (environment variables to look in, label)
    "anthropic": (["ANTHROPIC_API_KEY"], "Anthropic"),
    "openai": (["OPENAI_API_KEY"], "OpenAI"),
    "gemini": (["GEMINI_API_KEY", "GOOGLE_API_KEY"], "Gemini"),
    "github": (["GITHUB_TOKEN", "GH_TOKEN"], "GitHub Models (a personal access token with models:read)"),
}


def read_key_file(path):
    """Read a key from a file. On Linux and macOS refuse a file other users can read."""
    try:
        st = os.stat(path)
    except OSError as e:
        sys.exit(f"Cannot read key file: {e}")
    if not stat.S_ISREG(st.st_mode):
        sys.exit(f"{path} is not a regular file.")
    if os.name != "nt":
        if st.st_mode & 0o077:
            sys.exit(f"Refusing {path}: other users can read it (mode {stat.S_IMODE(st.st_mode):o}).\n"
                     f"Fix it with: chmod 600 {path}")
        if hasattr(os, "getuid") and st.st_uid != os.getuid():
            sys.exit(f"Refusing {path}: it is not owned by you.")
    with open(path, encoding="utf-8") as f:
        return f.read()


def harden_process():
    """Small protections that matter once a secret is in memory (Linux and macOS)."""
    try:
        import resource  # a crash must not write the key into a core dump
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    except (ImportError, ValueError, OSError):
        pass


def get_key(backend, key_file):
    envs, label = CLOUD[backend]
    if key_file:
        key = read_key_file(key_file)
    else:
        key = ""
        for e in envs:
            if os.environ.get(e):
                key = os.environ[e]
                break
        if not key:
            if not sys.stdin.isatty():
                sys.exit(f"No {label} key. Set {envs[0]}, use --key-file, or run in a terminal for a hidden prompt.")
            key = getpass.getpass(f"{label} API key (hidden, not saved): ")
    # Keep the key out of the environment we hand to any child process.
    for e in envs:
        os.environ.pop(e, None)
    key = key.strip().strip("\"'")
    if not key or any(c.isspace() for c in key):
        sys.exit("The key is empty or contains spaces or line breaks. Paste only the key itself.")
    harden_process()
    return key


def make_backend(a):
    b = a.backend
    if b == "copilot":
        b = a.backend = "github"
    if b == "auto":
        b = detect_backend(a.model)
    if b == "transformers":
        return TransformersBackend(a.model, a.gpu_layers, a.threads)
    if b == "onnx":
        return OnnxBackend(a.model, a.gpu_layers, a.threads)
    if b == "echo":
        return EchoBackend()
    if b == "server":
        return OpenAICompatBackend("server", a.url, a.model or "default", "none")
    if b == "llamacpp":
        if not a.model:
            sys.exit("Give the GGUF file with --model, for example --model models/Qwen3-4B-Q4_K_M.gguf")
        path = a.model
        if os.path.isdir(path):
            import glob
            path = sorted(glob.glob(os.path.join(path, "*.gguf")))[0]
        return LlamaCppBackend(path, a.ctx or DEFAULTS["ctx"], a.threads, a.gpu_layers)
    key = get_key(b, a.key_file)
    if not a.model:
        a.model = pick_model(b, key)
    if b == "anthropic":
        return AnthropicBackend(a.model, key, cache=getattr(a, "cache", False))
    if b == "gemini":
        return GeminiBackend(a.model, key)
    if b == "openai":
        return OpenAICompatBackend("openai", "https://api.openai.com/v1", a.model, key, local=False)
    # GitHub Models uses the OpenAI format at its own address. Model ids look like openai/gpt-4.1.
    return OpenAICompatBackend("github", "https://models.github.ai/inference", a.model, key,
                               local=False, path="/chat/completions")


# --------------------------------------------------------------------------
# Metrics (Lab 2, Part 1). Every model call becomes one record: the prompt, the reply,
# the time it took, and the tokens. Only the model's own work is timed: time spent
# waiting for you to type (or to approve a tool call) is never counted.
#
# Token fields, the same for every backend:
#   input        all prompt tokens the model read (including any that came from a cache)
#   output       all tokens it wrote (including reasoning)
#   cache_read   prompt tokens reused from a cache instead of being processed again
#   cache_write  prompt tokens processed and stored in a cache for next time
#   reasoning    the part of output spent thinking (<think>...</think>, or reported by the API)
# None means "this backend or provider does not report it". "source" says whether the numbers
# were reported by the provider, counted with the model's own tokenizer, or estimated.
# --------------------------------------------------------------------------
TOKEN_KEYS = ("input", "output", "cache_read", "cache_write", "reasoning")


# --------------------------------------------------------------------------
# Logging (Lab 4). Every record can also go to:
#   a CSV .log file per session, named with the date and time the session started (--log-dir)
#   a syslog server such as Security Onion, as plain text, JSON, CEF or LEEF (--syslog)
# --------------------------------------------------------------------------
CSV_FIELDS = ["prompt_time", "response_time", "session", "turn", "prompt_no", "user", "client", "backend", "model",
              "device", "temperature", "top_p", "top_k", "max_tokens", "seed", "effort", "prompt", "response",
              "operating_s", "first_token_s", "generate_s", "output_tok_per_s", "input_tokens", "output_tokens",
              "cache_read_tokens", "cache_write_tokens", "reasoning_tokens", "token_source"]


def flat_record(rec):
    """One record as a flat dict with the CSV column names."""
    row = {k: rec.get(k) for k in CSV_FIELDS}
    row.update({k: (rec.get("settings") or {}).get(k) for k in ("temperature", "top_p", "top_k", "max_tokens", "seed", "effort")})
    for k in TOKEN_KEYS:
        row[k + "_tokens"] = rec["tokens"].get(k)
    return row


def now_iso(epoch=None):
    t = datetime.datetime.fromtimestamp(epoch if epoch is not None else time.time()).astimezone()
    return t.isoformat(timespec="milliseconds")


class SyslogSender:
    """Send each record to a syslog server (RFC 5424) over UDP or TCP.
    Formats: plain (key=value), json, cef (ArcSight Common Event Format), leef (IBM QRadar LEEF 2.0)."""
    VENDOR, PRODUCT, VERSION = "BSidesDFW", "LLM Harness", "1.0"

    def __init__(self, target, proto="udp", fmt="plain", max_text=1000):
        host, _, port = target.rpartition(":")
        self.host, self.port = (host or target), int(port) if host else 514
        self.proto, self.fmt, self.max_text = proto, fmt, max_text
        self.hostname = socket.gethostname()
        self.sock = None

    def _clip(self, text):
        text = (text or "").replace("\r", " ")
        return text if len(text) <= self.max_text else text[: self.max_text] + "...[truncated]"

    def message(self, rec):
        row = flat_record(rec)
        row["prompt"], row["response"] = self._clip(row["prompt"]), self._clip(row["response"])
        if self.fmt == "json":
            return json.dumps(row, ensure_ascii=False)
        if self.fmt == "cef":
            return self.cef(row)
        if self.fmt == "leef":
            return self.leef(row)
        return " ".join(f'{k}="{str(v).replace(chr(34), chr(39))}"' for k, v in row.items() if v is not None)

    def cef(self, row):
        def hdr(x):  # CEF header: escape backslash and pipe
            return str(x).replace("\\", "\\\\").replace("|", "\\|")

        def ext(x):  # CEF extension values: escape backslash, equals, and line breaks
            return str(x).replace("\\", "\\\\").replace("=", "\\=").replace("\n", "\\n")
        epoch_ms = int(datetime.datetime.fromisoformat(row["prompt_time"]).timestamp() * 1000)
        fields = [("rt", epoch_ms), ("end", int(datetime.datetime.fromisoformat(row["response_time"]).timestamp() * 1000)),
                  ("suser", row["user"]), ("src", row["client"]), ("app", row["backend"]),
                  ("cs1Label", "model"), ("cs1", row["model"]), ("cs2Label", "session"), ("cs2", row["session"]),
                  ("cs3Label", "prompt"), ("cs3", row["prompt"]), ("cs4Label", "response"), ("cs4", row["response"]),
                  ("cs5Label", "device"), ("cs5", row["device"]),
                  ("cs6Label", "cacheTokens"), ("cs6", f"read={row['cache_read_tokens']};write={row['cache_write_tokens']}"),
                  ("cn1Label", "inputTokens"), ("cn1", row["input_tokens"]),
                  ("cn2Label", "outputTokens"), ("cn2", row["output_tokens"]),
                  ("cn3Label", "reasoningTokens"), ("cn3", row["reasoning_tokens"]),
                  ("cfp1Label", "operatingSeconds"), ("cfp1", row["operating_s"]),
                  ("cfp2Label", "firstTokenSeconds"), ("cfp2", row["first_token_s"]),
                  ("cfp3Label", "outputTokensPerSecond"), ("cfp3", row["output_tok_per_s"])]
        extension = " ".join(f"{k}={ext(v)}" for k, v in fields if v is not None)
        return "CEF:0|%s|%s|%s|llm.chat|LLM prompt and response|3|%s" % (
            hdr(self.VENDOR), hdr(self.PRODUCT), hdr(self.VERSION), extension)

    def leef(self, row):
        delim = "^"  # LEEF 2.0 lets you name the delimiter in the header

        def val(x):
            return str(x).replace(delim, " ").replace("\n", " ").replace("\t", " ")
        attrs = {"devTime": row["prompt_time"], "devTimeFormat": "yyyy-MM-dd'T'HH:mm:ss.SSSXXX",
                 "usrName": row["user"], "src": row["client"], "sev": 3, "cat": "llm",
                 "model": row["model"], "backend": row["backend"], "session": row["session"],
                 "prompt": row["prompt"], "response": row["response"], "device": row["device"],
                 "inputTokens": row["input_tokens"], "outputTokens": row["output_tokens"],
                 "cacheReadTokens": row["cache_read_tokens"], "cacheWriteTokens": row["cache_write_tokens"],
                 "reasoningTokens": row["reasoning_tokens"], "operatingSeconds": row["operating_s"],
                 "responseTime": row["response_time"]}
        body = delim.join(f"{k}={val(v)}" for k, v in attrs.items() if v is not None)
        return "LEEF:2.0|%s|%s|%s|llm.chat|%s|%s" % (self.VENDOR, self.PRODUCT, self.VERSION, delim, body)

    def send(self, rec):
        pri = 16 * 8 + 6  # facility local0, severity informational
        msg = self.message(rec)
        line = f"<{pri}>1 {now_iso()} {self.hostname} llm-harness {os.getpid()} {self.fmt.upper()} - {msg}"
        data = line.encode("utf-8")
        try:
            if self.proto == "udp":
                if self.sock is None:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.sock.sendto(data[:8000], (self.host, self.port))  # keep under common UDP limits
            else:
                if self.sock is None:
                    self.sock = socket.create_connection((self.host, self.port), timeout=5)
                self.sock.sendall(f"{len(data)} ".encode() + data)  # RFC 6587 octet counting
        except OSError as e:
            sys.stderr.write(f"[syslog: could not send to {self.host}:{self.port} ({e}); the local logs still have it]\n")
            self.sock = None


class Session:
    def __init__(self):
        self.id = uuid.uuid4().hex[:8]
        self.started = time.time()
        self.records = []
        self.log = None        # JSONL file (Lab 2)
        self.csv_path = None   # CSV .log file for this session (Lab 4)
        self.syslog = None     # SyslogSender (Lab 4)
        self.prompt_no = 0

    def open_csv(self, folder):
        os.makedirs(folder, exist_ok=True)
        stamp = datetime.datetime.fromtimestamp(self.started).strftime("%Y%m%d-%H%M%S")
        self.csv_path = os.path.join(folder, f"harness-{stamp}-{self.id}.log")
        return self.csv_path

    def add(self, rec):
        rec["session"], rec["turn"] = self.id, len(self.records) + 1
        rec["prompt_no"] = self.prompt_no
        self.records.append(rec)
        if self.log:
            with open(self.log, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if self.csv_path:
            new = not os.path.exists(self.csv_path)
            with open(self.csv_path, "a", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                if new:
                    w.writeheader()
                w.writerow(flat_record(rec))
        if self.syslog:
            self.syslog.send(rec)

    def totals(self, records=None):
        recs = self.records if records is None else records
        t = {"calls": len(recs), "operating_s": round(sum(r["operating_s"] for r in recs), 3)}
        for k in TOKEN_KEYS:
            vals = [r["tokens"][k] for r in recs if r["tokens"].get(k) is not None]
            t[k] = sum(vals) if vals else None
        gen = sum(r["generate_s"] or 0 for r in recs)
        t["output_tok_per_s"] = round(t["output"] / gen, 1) if t["output"] and gen else None
        return t


SESSION = Session()


def fmt_tokens(t):
    def v(k):
        return "-" if t.get(k) is None else str(t[k])
    return f"in {v('input')} (cache read {v('cache_read')}, write {v('cache_write')}) | out {v('output')} (reasoning {v('reasoning')})"


def print_stats(rec):
    sys.stderr.write(f"  [{fmt_tokens(rec['tokens'])} | {rec['operating_s']:.2f} s, first token "
                     f"{rec['first_token_s'] if rec['first_token_s'] is not None else '-'} s, "
                     f"{rec['output_tok_per_s'] or '-'} tok/s | {rec['device']}]\n")


def print_session_summary(session=SESSION):
    if not session.records:
        return
    t = session.totals()
    sys.stderr.write(f"\nSession {session.id}: {t['calls']} model calls for {session.prompt_no} prompts, "
                     f"{t['operating_s']:.1f} s operating time (your typing time not counted)\n"
                     f"  {fmt_tokens(t)} | {t['output_tok_per_s'] or '-'} output tok/s\n")


def run_turn(backend, messages, settings, echo=True, session=None, user=None, client=None):
    s = apply_effort(settings, backend)
    parts = []
    backend.usage = {}
    t0 = time.perf_counter()
    first = None
    for piece in backend.stream(with_think_switch(messages, s), s):
        if first is None:
            first = time.perf_counter()
        parts.append(piece)
        if echo:
            sys.stdout.write(piece)
            sys.stdout.flush()
    t1 = time.perf_counter()
    if echo:
        print()
    text = "".join(parts)
    record_call(backend, messages, s, text, t0, first, t1, session, user, client)
    return text


def local_user():
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def record_call(backend, messages, s, text, t0, first, t1, session=None, user=None, client=None):
    u = dict(getattr(backend, "usage", None) or {})
    wall_end = time.time() - (time.perf_counter() - t1)  # turn the precise timer into clock time
    tokens = {k: u.get(k) for k in TOKEN_KEYS}
    gen_s = (t1 - first) if first else None
    out = tokens.get("output")
    rec = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "prompt_time": now_iso(wall_end - (t1 - t0)), "response_time": now_iso(wall_end),
        "user": user or local_user(), "client": client or "local",
        "backend": backend.name, "model": backend.model, "device": getattr(backend, "device", "?"),
        "settings": {k: s.get(k) for k in ("temperature", "top_p", "top_k", "max_tokens", "seed", "effort")},
        "prompt": next((m["content"] for m in reversed(messages) if m["role"] == "user"), ""),
        "response": text,
        "operating_s": round(t1 - t0, 3),
        "first_token_s": round(first - t0, 3) if first else None,
        "generate_s": round(gen_s, 3) if gen_s else None,
        "output_tok_per_s": round(out / gen_s, 1) if out and gen_s and gen_s > 0 else None,
        "tokens": tokens, "token_source": u.get("source", "not reported"),
    }
    session = session or SESSION
    session.add(rec)
    if getattr(session, "show", False):
        print_stats(rec)
    return rec


# --------------------------------------------------------------------------
# Tools (Lab 4 uses these). The model asks for a tool by writing one JSON
# object. The harness runs it and feeds the result back. The model never
# runs anything itself.
# --------------------------------------------------------------------------
TOOL_PROMPT = """You can use tools. To use one, reply with ONLY one JSON object, nothing else:
{"tool": "<name>", "args": {...}}
Tools:
- list_dir: {"path": "."}  lists files in a folder
- read_file: {"path": "notes.txt"}  reads a text file
- calculator: {"expression": "2*(3+4)"}  does arithmetic
After you get a TOOL RESULT, answer the user in plain text. If no tool is needed, answer in plain text."""

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
        ast.USub: operator.neg, ast.UAdd: operator.pos}


def _calc(node):
    if isinstance(node, ast.Expression):
        return _calc(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calc(node.left), _calc(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_calc(node.operand))
    raise ValueError("only numbers and + - * / ** % are allowed")


def safe_path(root, rel):
    """Resolve rel inside root. Refuse anything that escapes it."""
    root = os.path.realpath(root)
    full = os.path.realpath(os.path.join(root, rel))
    if full != root and not full.startswith(root + os.sep):
        raise ValueError("path is outside the tool folder")
    return full


MEMORY_PROMPT = """
Memory tools (an Obsidian vault of Markdown notes). Use them to remember facts the user
asks you to keep, and to look up what you saved before. Search before you say you do not know.
- memory_search: {"query": "juice shop port"}  finds notes that contain those words
- memory_read: {"note": "AI Memory/Project.md"}  reads one note
- memory_write: {"note": "Project", "text": "The lab uses port 3000."}  adds a dated entry to a note"""


def memory_search(vault, query, limit=5):
    words = [w for w in re.findall(r"\w+", query.lower()) if len(w) > 2]
    hits = []
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if not d.startswith(".")]  # skip .obsidian and other hidden folders
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            low = (fn + " " + text).lower()
            score = sum(low.count(w) for w in words)
            if score:
                i = min([low.find(w) for w in words if w in low] or [0])
                snippet = text[max(0, i - 80): i + 160].replace("\n", " ")
                hits.append((score, os.path.relpath(path, vault), snippet))
    hits.sort(reverse=True)
    return "\n".join(f"- {p}: ...{snip}..." for _, p, snip in hits[:limit]) or "No notes found."


def memory_write(vault, folder, note, text):
    name = re.sub(r"[^\w .-]", "", str(note)).strip().lstrip(". ") or "Notes"
    name = name[:-3] if name.lower().endswith(".md") else name
    path = safe_path(os.path.join(vault, folder), name + ".md")  # writes stay inside the memory folder
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:  # Obsidian reads this front matter as note properties
            f.write(f"---\ntags: [ai-memory]\ncreated: {time.strftime('%Y-%m-%d')}\n---\n# {name}\n")
        f.write(f"\n- {time.strftime('%Y-%m-%d %H:%M')}: {str(text).strip()}\n")
    return f"Saved to {os.path.relpath(path, vault)}"


def run_tool(call, tool_dir, memory=None):
    name, args = call.get("tool"), call.get("args", {}) or {}
    if name and name.startswith("memory_"):
        if not memory:
            raise ValueError("memory is not turned on (start the harness with --memory-dir)")
        vault, folder = memory
        if name == "memory_search":
            return memory_search(vault, str(args.get("query", "")))[:2000]
        if name == "memory_read":
            with open(safe_path(vault, str(args.get("note", ""))), encoding="utf-8", errors="replace") as f:
                return f.read(4000)
        if name == "memory_write":
            return memory_write(vault, folder, args.get("note", "Notes"), args.get("text", ""))
    if name == "calculator":
        return str(_calc(ast.parse(str(args.get("expression", "")), mode="eval")))
    if name == "list_dir":
        return "\n".join(sorted(os.listdir(safe_path(tool_dir, args.get("path", ".")))))[:2000]
    if name == "read_file":
        with open(safe_path(tool_dir, args.get("path", "")), encoding="utf-8", errors="replace") as f:
            return f.read(4000)
    raise ValueError(f"unknown tool: {name}")


def find_json(text):
    """Pull the first {...} object with a "tool" key out of a model reply."""
    text = text.split("</think>")[-1]
    start = text.find("{")
    while start != -1:
        depth = 0
        for i in range(start, len(text)):
            depth += (text[i] == "{") - (text[i] == "}")
            if depth == 0:
                try:
                    obj = json.loads(text[start:i + 1])
                    if isinstance(obj, dict) and "tool" in obj:
                        return obj
                except ValueError:
                    pass
                break
        start = text.find("{", start + 1)
    return None


def turn_with_tools(backend, messages, settings, a):
    reply = ""
    for step in range(a.max_steps + 1):
        reply = run_turn(backend, messages, settings)
        messages.append({"role": "assistant", "content": reply})
        call = find_json(reply)
        if not call:
            return reply
        if step == a.max_steps:
            print("[stopped: reached --max-steps]")
            return reply
        result = None
        if a.approve and input(f"  Run {json.dumps(call)}? [y/N] ").strip().lower() != "y":
            result = "The user refused this tool call."
        if result is None:
            try:
                result = run_tool(call, a.tool_dir, memory_of(a))
            except Exception as e:  # tool errors go back to the model as text
                result = f"ERROR: {e}"
        print(f"  tool result: {result[:200]}")
        messages.append({"role": "user", "content": "TOOL RESULT:\n" + result})
    return reply


# --------------------------------------------------------------------------
# chat / ask
# --------------------------------------------------------------------------
HELP = """Commands:
  /set NAME VALUE   change a setting (temperature, top_p, top_k, max_tokens, seed,
                    repeat_penalty, ctx, effort low|medium|high|off, stop TEXT)
  /system TEXT      change the system prompt (clears the conversation)
  /reset            clear the conversation
  /show             show the current settings
  /stats            show the token and time totals for this session
  /quit             leave"""


def parse_setting(settings, name, value):
    if name not in DEFAULTS:
        raise ValueError(f"unknown setting {name}")
    if name == "effort":
        if value not in EFFORT and value != "off":
            raise ValueError("effort must be low, medium, high or off")
        settings["effort"] = None if value == "off" else value
    elif name == "stop":
        settings["stop"] = [value] if value else []
    elif name in INT_KEYS:
        settings[name] = int(value)
    elif name in FLOAT_KEYS:
        settings[name] = float(value)
    else:
        settings[name] = value


def build_settings(a):
    s = dict(DEFAULTS)
    for k in ("temperature", "top_p", "top_k", "max_tokens", "seed", "repeat_penalty", "ctx", "effort"):
        v = getattr(a, k, None)
        if v is not None:
            s[k] = v
    if a.stop:
        s["stop"] = a.stop
    if a.system:
        s["system"] = a.system
    return s


def memory_of(a):
    md = getattr(a, "memory_dir", None)
    return (os.path.realpath(os.path.expanduser(md)), a.memory_folder) if md else None


def new_messages(settings, tools, memory=None):
    extra = ("\n\n" + TOOL_PROMPT if tools else "") + (MEMORY_PROMPT if memory else "")
    return [{"role": "system", "content": settings["system"] + extra}]


def setup_metrics(a):
    if getattr(a, "memory_dir", None):
        if not os.path.isdir(os.path.expanduser(a.memory_dir)):
            sys.exit(f"Memory folder not found: {a.memory_dir}. Create the Obsidian vault first (Lab 3, Part 2).")
        a.tools = True  # memory is used through the tool loop
    SESSION.show = a.stats
    SESSION.log = a.log
    if getattr(a, "log_dir", None):
        print(f"Logging this session to {SESSION.open_csv(os.path.expanduser(a.log_dir))}", file=sys.stderr)
    if getattr(a, "syslog", None):
        SESSION.syslog = SyslogSender(a.syslog, a.syslog_proto, a.syslog_format)
        print(f"Sending {a.syslog_format} syslog over {a.syslog_proto.upper()} to {a.syslog}", file=sys.stderr)
    if a.system_file:
        with open(a.system_file, encoding="utf-8") as f:
            a.system = f.read()


def cmd_chat(a):
    setup_metrics(a)
    backend = make_backend(a)
    settings = build_settings(a)
    messages = new_messages(settings, a.tools, memory_of(a))
    where = "on this computer" if backend.local else "in the cloud (your messages leave this computer)"
    print(f"harness: backend={backend.name} model={backend.model}, running {where}")
    print("Type a message. /help for commands.\n")
    while True:
        try:
            line = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.startswith("/"):
            cmd, _, rest = line[1:].partition(" ")
            try:
                if cmd in ("quit", "exit"):
                    break
                elif cmd == "help":
                    print(HELP)
                elif cmd == "reset":
                    messages = new_messages(settings, a.tools, memory_of(a))
                    print("conversation cleared")
                elif cmd == "system":
                    settings["system"] = rest
                    messages = new_messages(settings, a.tools, memory_of(a))
                    print("system prompt changed, conversation cleared")
                elif cmd == "set":
                    name, _, value = rest.partition(" ")
                    parse_setting(settings, name.strip(), value.strip())
                    print(f"{name} = {settings[name.strip()]}")
                elif cmd == "show":
                    for k, v in settings.items():
                        print(f"  {k}: {v}")
                elif cmd == "stats":
                    print_session_summary()
                else:
                    print("unknown command, try /help")
            except (ValueError, KeyError) as e:
                print("error:", e)
            continue
        messages.append({"role": "user", "content": line})
        SESSION.prompt_no += 1
        if a.tools:
            turn_with_tools(backend, messages, settings, a)
            continue
        print("bot> ", end="", flush=True)
        messages.append({"role": "assistant", "content": run_turn(backend, messages, settings)})
        approx = sum(len(m["content"]) for m in messages) // 4
        if backend.local and approx > settings["ctx"] * 0.8:
            print(f"[warning: history is about {approx} tokens, near the {settings['ctx']} token window]")
    if a.stats or a.log:
        print_session_summary()


def cmd_ask(a):
    setup_metrics(a)
    backend = make_backend(a)
    settings = build_settings(a)
    prompt = " ".join(a.prompt) if a.prompt else ""
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            prompt = (prompt + "\n\n" if prompt else "") + f.read()
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read()
    if not prompt:
        sys.exit("Give a question, --file, or pipe text in.")
    messages = new_messages(settings, a.tools, memory_of(a)) + [{"role": "user", "content": prompt}]
    SESSION.prompt_no += 1
    if a.tools:
        turn_with_tools(backend, messages, settings, a)
    else:
        for i in range(a.repeat):
            if i:
                SESSION.prompt_no += 1
            run_turn(backend, messages, settings)
    if a.stats or a.log:
        print_session_summary()


# --------------------------------------------------------------------------
# models: list the model ids your key can use (Part 3). The key is read the same
# safe way as for chat, and only sent to the provider's own address.
# --------------------------------------------------------------------------
MODEL_LISTS = {
    "anthropic": ("https://api.anthropic.com/v1/models?limit=100", "x-api-key"),
    "openai": ("https://api.openai.com/v1/models", "bearer"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", "x-goog-api-key"),
    "github": ("https://models.github.ai/catalog/models", "bearer"),
}


def list_model_ids(b, key):
    """The model ids this key can use, from the provider's own list."""
    url, how = MODEL_LISTS[b]
    headers = {"Accept": "application/json"}
    if how == "bearer":
        headers["Authorization"] = "Bearer " + key
    else:
        headers[how] = key
    if b == "anthropic":
        headers["anthropic-version"] = "2023-06-01"
    req = urllib.request.Request(url, headers=headers)
    body = "".join(http_lines(req, urllib.parse.urlsplit(url).netloc))
    data = json.loads(body)
    if b == "gemini":
        ids = [m["name"].split("/", 1)[-1] for m in data.get("models", [])
               if "generateContent" in m.get("supportedGenerationMethods", [])]
    elif b == "github":
        items = data if isinstance(data, list) else data.get("data", [])
        ids = [m.get("id") for m in items if m.get("id")]
    else:
        ids = [m["id"] for m in data.get("data", [])]
    return sorted(i for i in ids if i)


def pick_model(b, key):
    """No --model for a cloud backend: show the provider's current list and let the user choose."""
    ids = list_model_ids(b, key)
    if not ids:
        sys.exit("The provider returned no models for this key.")
    if not sys.stdin.isatty():
        sys.exit("Add --model with one of these ids: " + ", ".join(ids[:20]))
    for n, i in enumerate(ids, 1):
        print(f"  {n:3d}  {i}", file=sys.stderr)
    while True:
        choice = input(f"Type the number of a model (1 to {len(ids)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(ids):
            model = ids[int(choice) - 1]
            print(f"Using {model}. Next time you can add --model {model}", file=sys.stderr)
            return model


def cmd_models(a):
    b = "github" if a.backend == "copilot" else a.backend
    if b not in MODEL_LISTS:
        sys.exit("models works with --backend anthropic, openai, gemini or github (copilot).")
    key = get_key(b, a.key_file)
    ids = list_model_ids(b, key)
    for i in ids:
        print(i)
    print(f"\n{len(ids)} models. Lists change often; this is what your key can use today.", file=sys.stderr)


# --------------------------------------------------------------------------
# image: small image models (Part 2c). classify = recognition, generate = drawing.
# Both run on the CPU; --gpu-layers -1 uses a GPU when torch can see one.
# --------------------------------------------------------------------------
def cmd_image(a):
    try:
        import torch
    except ImportError:
        sys.exit("Part 2c needs torch: python3 -m pip install -r requirements-hf.txt")
    device = gpu_device(a.gpu_layers)
    if not os.path.isdir(a.model):
        sys.exit(f"Model folder not found: {a.model}. Run python3 prefetch_lab1.py --with-images, or pass --model.")
    t0 = time.time()
    if a.task == "classify":
        from transformers import pipeline
        from PIL import Image
        clf = pipeline("image-classification", model=a.model, device=device, use_fast=True,
                       model_kwargs={"use_safetensors": True, "local_files_only": True})
        img = Image.open(a.input).convert("RGB")
        print(f"What {os.path.basename(a.model)} sees in {a.input}:")
        for p in clf(img, top_k=a.top):
            print("  %5.1f%%  %s" % (100 * p["score"], p["label"]))
    else:
        try:
            from diffusers import AutoPipelineForText2Image
        except ImportError:
            sys.exit("Image generation needs diffusers: python3 -m pip install -r requirements-hf.txt")
        dtype = torch.float16 if device != "cpu" else torch.float32
        import glob
        # sd-turbo is downloaded as its smaller fp16 files ("variant"); they are converted for the CPU on load.
        variant = "fp16" if glob.glob(os.path.join(a.model, "*", "*.fp16.safetensors")) else None
        pipe = AutoPipelineForText2Image.from_pretrained(a.model, torch_dtype=dtype, use_safetensors=True,
                                                         variant=variant, local_files_only=True).to(device)
        pipe.set_progress_bar_config(disable=True)
        g = torch.Generator(device="cpu").manual_seed(a.seed if a.seed >= 0 else int(time.time()))
        print(f"Drawing with {os.path.basename(a.model)} on the {device.upper()}: {a.steps} step(s), {a.size}x{a.size} ...")
        img = pipe(prompt=a.input, num_inference_steps=a.steps, guidance_scale=a.guidance,
                   height=a.size, width=a.size, generator=g).images[0]
        img.save(a.out)
        print(f"Wrote {a.out}. Open it to look.")
    print(f"[{time.time() - t0:.1f} s on the {device.upper()}]", file=sys.stderr)


# --------------------------------------------------------------------------
# serve: an OpenAI-compatible server, so Open WebUI (Lab 2) and the Continue
# extension (Lab 3) can use this harness as their backend.
# --------------------------------------------------------------------------
def openai_usage(rec):
    """A metrics record in the OpenAI 'usage' shape, so clients of serve can read it."""
    t = rec["tokens"]
    return {"prompt_tokens": t["input"] or 0, "completion_tokens": t["output"] or 0,
            "total_tokens": (t["input"] or 0) + (t["output"] or 0),
            "prompt_tokens_details": {"cached_tokens": t["cache_read"] or 0},
            "completion_tokens_details": {"reasoning_tokens": t["reasoning"] or 0}}


def docker_bridge_ips():
    """IPv4 addresses of the docker0 bridge on Linux (empty elsewhere). Only local containers reach them."""
    try:
        out = subprocess.run(["ip", "-4", "-o", "addr", "show", "docker0"],
                             capture_output=True, text=True, timeout=5).stdout
    except Exception:
        return set()
    return set(re.findall(r"inet (\d+\.\d+\.\d+\.\d+)/", out))


def cmd_serve(a):
    setup_metrics(a)
    # A cloud model spends your key, so only serve it on this machine. The one exception is the
    # address of Docker's own bridge (docker0) on Linux, which only containers on this machine can
    # reach, so Open WebUI in Docker can use it (Lab 4, Part 3). A password is still required.
    if a.backend not in ("auto", "llamacpp", "transformers", "onnx", "server", "echo") and \
            a.host not in ({"127.0.0.1", "localhost", "::1"} | docker_bridge_ips()):
        sys.exit("Refusing to serve a cloud model on a network address: anyone who can reach this port "
                 "could spend your API key. Use --host 127.0.0.1 (or the docker0 address for Docker on Linux), "
                 "or serve a local model.")
    backend = make_backend(a)
    base = build_settings(a)
    lock = threading.Lock()  # one generation at a time; a laptop has one set of cores
    model_id = a.served_name or backend.model
    # A cloud model spends your key. On a shared Linux machine any other user can reach
    # localhost, so require a random token. Enter it as the "API key" in Open WebUI or Continue.
    token = None if backend.local else secrets.token_urlsafe(24)

    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, fmt, *args):
            sys.stderr.write("serve: " + fmt % args + "\n")

        def _json(self, code, obj):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(data)

        def do_OPTIONS(self):
            self.send_response(204)
            for k, v in (("Access-Control-Allow-Origin", "*"), ("Access-Control-Allow-Headers", "*"),
                         ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
                         ("Content-Length", "0")):
                self.send_header(k, v)
            self.end_headers()

        def _who(self, req=None):
            """Who sent this request? Open WebUI forwards the signed-in user in X-OpenWebUI-User-* headers
            when ENABLE_FORWARD_USER_INFO_HEADERS is true; OpenAI clients may send a "user" field."""
            h = self.headers
            user = (h.get("X-OpenWebUI-User-Email") or h.get("X-OpenWebUI-User-Name")
                    or (req or {}).get("user") or "unknown (no user header)")
            role = h.get("X-OpenWebUI-User-Role")
            return (f"{user} [{role}]" if role else user), self.client_address[0]

        def _authorized(self):
            if token is None:
                return True
            given = self.headers.get("Authorization", "").replace("Bearer ", "", 1)
            if hmac.compare_digest(given.encode(), token.encode()):
                return True
            self._json(401, {"error": "missing or wrong token"})
            return False

        def do_GET(self):
            if self.path in ("/", "/health"):
                return self._json(200, {"status": "ok"})
            if not self._authorized():
                return
            if self.path.rstrip("/") in ("/v1/models", "/models"):
                self._json(200, {"object": "list", "data": [
                    {"id": model_id, "object": "model", "owned_by": "harness"}]})
            else:
                self._json(404, {"error": "not found"})

        def _completions(self):
            """The older text-completion API: a prompt in, text out. Some editor features
            (Continue's autocomplete and edit actions) call this instead of chat."""
            try:
                req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
                prompt = req["prompt"] if isinstance(req["prompt"], str) else "".join(req["prompt"])
            except (ValueError, KeyError, TypeError) as e:
                return self._json(400, {"error": f"bad request: {e}"})
            s = dict(base)
            for k in ("temperature", "top_p", "max_tokens", "seed"):
                if req.get(k) is not None:
                    s[k] = req[k]
            if req.get("stop"):
                s["stop"] = [req["stop"]] if isinstance(req["stop"], str) else req["stop"]
            msgs = [{"role": "system", "content": "Continue the text. Reply with only the continuation."},
                    {"role": "user", "content": prompt}]
            with lock:
                SESSION.prompt_no += 1
                user, client = self._who(req)
                text = run_turn(backend, msgs, s, echo=False, user=user, client=client)
            o = {"id": "cmpl-" + uuid.uuid4().hex[:12], "object": "text_completion", "created": int(time.time()),
                 "model": model_id, "choices": [{"index": 0, "text": text, "finish_reason": "stop"}],
                 "usage": openai_usage(SESSION.records[-1])}
            if req.get("stream"):
                data = ("data: " + json.dumps(o) + "\n\ndata: [DONE]\n\n").encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self._json(200, o)

        def do_POST(self):
            if not self._authorized():
                return
            path = self.path.rstrip("/")
            if path.endswith("/completions") and not path.endswith("/chat/completions"):
                return self._completions()
            if not path.endswith("/chat/completions"):
                return self._json(404, {"error": "not found"})
            try:
                n = int(self.headers.get("Content-Length", 0))
                req = json.loads(self.rfile.read(n) or b"{}")
                msgs = [{"role": m["role"], "content": m["content"] if isinstance(m["content"], str)
                         else "".join(p.get("text", "") for p in m["content"])}
                        for m in req["messages"]]
            except (ValueError, KeyError, TypeError) as e:
                return self._json(400, {"error": f"bad request: {e}"})
            s = dict(base)
            for k in ("temperature", "top_p", "max_tokens", "seed"):
                if req.get(k) is not None:
                    s[k] = req[k]
            if req.get("stop"):
                s["stop"] = [req["stop"]] if isinstance(req["stop"], str) else req["stop"]
            cid = "chatcmpl-" + uuid.uuid4().hex[:12]
            created = int(time.time())

            def chunk(delta, finish=None):
                o = {"id": cid, "object": "chat.completion.chunk", "created": created,
                     "model": model_id,
                     "choices": [{"index": 0, "delta": delta, "finish_reason": finish}]}
                return ("data: " + json.dumps(o) + "\n\n").encode()

            with lock:
                if req.get("stream"):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.send_header("Connection", "close")
                    self.end_headers()
                    self.close_connection = True
                    try:
                        self.wfile.write(chunk({"role": "assistant"}))
                        sset = apply_effort(s, backend)
                        SESSION.prompt_no += 1
                        backend.usage, parts, t0, first = {}, [], time.perf_counter(), None
                        for piece in backend.stream(with_think_switch(msgs, sset), sset):
                            first = first or time.perf_counter()
                            parts.append(piece)
                            self.wfile.write(chunk({"content": piece}))
                            self.wfile.flush()
                        user, client = self._who(req)
                        rec = record_call(backend, msgs, sset, "".join(parts), t0, first, time.perf_counter(),
                                          user=user, client=client)
                        if (req.get("stream_options") or {}).get("include_usage"):
                            self.wfile.write(("data: " + json.dumps({
                                "id": cid, "object": "chat.completion.chunk", "created": created,
                                "model": model_id, "choices": [], "usage": openai_usage(rec)}) + "\n\n").encode())
                        self.wfile.write(chunk({}, "stop"))
                        self.wfile.write(b"data: [DONE]\n\n")
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                else:
                    SESSION.prompt_no += 1
                    user, client = self._who(req)
                    reply = run_turn(backend, msgs, s, echo=False, user=user, client=client)
                    self._json(200, {"id": cid, "object": "chat.completion", "created": created,
                                     "model": model_id, "usage": openai_usage(SESSION.records[-1]),
                                     "choices": [{"index": 0, "finish_reason": "stop",
                                                  "message": {"role": "assistant", "content": reply}}]})

    srv = ThreadingHTTPServer((a.host, a.port), H)
    print(f"serving {model_id} on http://{a.host}:{a.port}/v1")
    if token:
        print("This model uses your cloud key, so the server needs a password.")
        print("Open WebUI or Continue: base URL http://localhost:%d/v1, API key: %s" % (a.port, token))
    else:
        print("Open WebUI or Continue: use base URL http://localhost:%d/v1 and any API key." % a.port)
    if a.host == "127.0.0.1":
        print("From Docker on Linux, start with --host 0.0.0.0 so containers can reach it.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


# --------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="A small LLM harness.")
    sub = p.add_subparsers(dest="cmd")

    def common(sp):
        sp.add_argument("--backend", default="auto",
                        choices=["auto", "llamacpp", "transformers", "onnx", "server",
                                 "anthropic", "openai", "gemini", "github", "copilot", "echo"])
        sp.add_argument("--model", help="local: a .gguf file, a safetensors folder or an ONNX folder. "
                                        "cloud or server: a model id")
        sp.add_argument("--url", default="http://localhost:11434/v1",
                        help="server backend base URL. Ollama 11434/v1, KoboldCpp 5001/v1, llama.cpp 8080/v1")
        sp.add_argument("--key-file", help="file holding the API key (must be mode 600). "
                        "Otherwise the key comes from an environment variable or a hidden prompt")
        sp.add_argument("--threads", type=int, help="CPU threads (default: all)")
        sp.add_argument("--gpu-layers", dest="gpu_layers", type=int, default=0,
                        help="local model only: layers to put on the GPU. 0 = CPU only (default), "
                             "-1 = all. Needs a GPU build of llama-cpp-python")
        sp.add_argument("--temperature", type=float)
        sp.add_argument("--top-p", dest="top_p", type=float)
        sp.add_argument("--top-k", dest="top_k", type=int)
        sp.add_argument("--max-tokens", dest="max_tokens", type=int)
        sp.add_argument("--repeat-penalty", dest="repeat_penalty", type=float)
        sp.add_argument("--seed", type=int)
        sp.add_argument("--ctx", type=int, help="context window in tokens for a local model (default 4096)")
        sp.add_argument("--effort", choices=list(EFFORT), help="local Qwen3 preset: thinking on/off + token cap")
        sp.add_argument("--stop", action="append", help="stop sequence (repeatable)")
        sp.add_argument("--system", help="system prompt")
        sp.add_argument("--system-file", help="read the system prompt from a file (for cache tests)")
        sp.add_argument("--stats", action="store_true", help="print tokens and timing after every reply")
        sp.add_argument("--log", help="append one JSON line per model call to this file (prompt, reply, time, tokens)")
        sp.add_argument("--cache", action="store_true", help="anthropic: mark the system prompt for prompt caching")
        sp.add_argument("--log-dir", help="write a date-stamped CSV .log file for this session into this folder (Lab 4)")
        sp.add_argument("--syslog", help="send every record to a syslog server, HOST or HOST:PORT (Lab 4)")
        sp.add_argument("--syslog-proto", choices=["udp", "tcp"], default="udp")
        sp.add_argument("--syslog-format", choices=["plain", "json", "cef", "leef"], default="plain")

    def tools(sp):
        sp.add_argument("--tools", action="store_true", help="enable the tool loop")
        sp.add_argument("--tool-dir", default=".", help="folder the file tools may read")
        sp.add_argument("--approve", action="store_true", help="ask before every tool call")
        sp.add_argument("--max-steps", type=int, default=4)
        sp.add_argument("--memory-dir", help="an Obsidian vault folder to use as long-term memory (Lab 3, Part 2)")
        sp.add_argument("--memory-folder", default="AI Memory", help="the vault subfolder the model may write to")

    c = sub.add_parser("chat", help="interactive chat (default)")
    common(c)
    tools(c)
    k = sub.add_parser("ask", help="one question, then exit")
    common(k)
    tools(k)
    k.add_argument("prompt", nargs="*")
    k.add_argument("--file", help="append this file to the prompt")
    k.add_argument("--repeat", type=int, default=1, help="ask N times (compare variety)")
    s = sub.add_parser("serve", help="OpenAI-compatible server")
    common(s)
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=13370)
    s.add_argument("--served-name", help="model name to advertise")

    m = sub.add_parser("models", help="list the model ids a cloud key can use")
    m.add_argument("--backend", required=True, choices=["anthropic", "openai", "gemini", "github", "copilot"])
    m.add_argument("--key-file", help="file holding the API key (must be mode 600)")
    im = sub.add_parser("image", help="small image models: classify a picture, or generate one (Part 2c)")
    im.add_argument("task", choices=["classify", "generate"])
    im.add_argument("input", help="classify: an image file. generate: a text prompt in quotes")
    im.add_argument("--model", help="model folder (default: models/vit-base-patch16-224 or models/sd-turbo)")
    im.add_argument("--top", type=int, default=5, help="classify: how many labels to show")
    im.add_argument("--steps", type=int, default=1, help="generate: denoising steps (sd-turbo needs 1 to 4)")
    im.add_argument("--guidance", type=float, default=0.0, help="generate: prompt strength (0 for sd-turbo)")
    im.add_argument("--size", type=int, default=512, help="generate: width and height in pixels")
    im.add_argument("--seed", type=int, default=-1)
    im.add_argument("--out", default="image.png")
    im.add_argument("--gpu-layers", dest="gpu_layers", type=int, default=0, help="-1 = use a GPU if torch finds one")

    argv = sys.argv[1:]
    if not argv or argv[0].startswith("-") and argv[0] not in ("-h", "--help"):
        argv = ["chat"] + argv
    a = p.parse_args(argv)
    if not a.cmd:
        p.print_help()
        return
    if a.cmd == "image" and not a.model:
        a.model = os.path.join("models", "vit-base-patch16-224" if a.task == "classify" else "sd-turbo")
    {"chat": cmd_chat, "ask": cmd_ask, "serve": cmd_serve, "models": cmd_models, "image": cmd_image}[a.cmd](a)


if __name__ == "__main__":
    main()
