#!/usr/bin/env python3
"""
ai_prefetch.py - background downloader for the BSidesDFW "Under the Hood of LLMs" workshop.

Shows an overall progress bar, one bar per download, and a live list of what is
downloaded, in progress, and remaining. Standard library only (Python 3.8+).

Targets (run them in workshop order so each lab is ready when it starts):
  lab1   Python packages (with PyTorch), three small models in GGUF, safetensors and ONNX (Part 1),
         Qwen3-4B (2.5 GB), the KoboldCpp CPU program, and the Part 4 Docker images and Ollama model
  lab1images  optional Part 2c: PyTorch, an image recognizer (ViT) and an image generator (sd-turbo)
  lab2   the Lab 1 packages and models, plus the Ollama models for the benchmark (qwen2.5:1.5b, qwen3:1.7b)
  lab3   the Lab 1 packages and models, a VS Code check, and the Continue extension
  lab4   the Lab 1 packages and models that Lab 4 uses, and the Open WebUI image
  lab5   Surprise Bonus Lab: nothing to download (checks that Docker is running)
  lab6   homework: Michael Nielsen's network code and the MNIST data (17 MB)
  lab7   homework: the Lab 1 GGUF model to copy to a phone, plus notes for the phone apps
  lab8   homework: KoboldCpp, Hermes 3 3B, Qwen 0.5B, OpenClaw notes
  lab9   homework: an abliterated Qwen2.5 1.5B GGUF (about 1 GB) to compare with the Lab 1 model
  all    everything for the five workshop labs, in order
  bonus  benchmark matrix files, llama.cpp image, notes for the other bonus labs

Examples:
  python3 ai_prefetch.py lab1            (macOS / Linux)
  py -3 ai_prefetch.py all --background  (Windows: runs hidden, log + state file)
  python3 ai_prefetch.py --status        (show progress of a background run)
  python3 ai_prefetch.py all --check     (show what is ready and what is missing; downloads nothing)
"""
import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

VERSION = "1.0"
OLLAMA = os.environ.get("OLLAMA_HOST_URL", "http://localhost:11434")
UA = {"User-Agent": "ai-night-prefetch/" + VERSION}
HF = "https://huggingface.co/"
KOBOLD = "https://github.com/LostRuins/koboldcpp/releases/latest/download/"

WORKSHOP_ORDER = ["lab1", "lab2", "lab3", "lab4", "lab5"]
HOMEWORK_LABS = ["lab6", "lab7", "lab8", "lab9"]
LAB_NAMES = {"lab1": "Lab 1", "lab2": "Lab 2", "lab3": "Lab 3", "lab4": "Lab 4",
             "lab5": "Lab 5", "lab6": "Lab 6", "lab7": "Lab 7", "lab8": "Lab 8", "lab9": "Lab 9", "bonus": "Bonus", "models": "Models",
             "lab1bonus": "Lab 1", "lab1images": "Lab 1 2c", "lab1ministral": "Lab 1 1e"}

# The Python packages and the four Lab 1 models. Labs 2 to 4 use them too.
LAB1_CORE = ["pip_lab1", "pip_torch", "pip_hf", "p1_gguf", "p1_st", "p1_onnx", "qwen3_4b"]

# Items each target needs, in the order they are needed. Items already on the
# machine are skipped, so every script is safe to run again.
TARGET_ITEMS = {
    # Each workshop lab gets everything it uses, also the Lab 1 models and packages, so each
    # Lab## pre-fetch script works alone. Items already on the machine are skipped.
    "lab1": LAB1_CORE + ["kobold_cpu", "docker", "ollama_image", "webui_image", "ollama_up", "qwen15_ollama",
                         "kobold_image", "llamacpp_image"],
    "lab1images": ["pip_torch", "pip_hf", "img_vit", "img_sdturbo"],
    # Optional: Ministral 3 (3B) squeezed to about 1 GB. Only GGUF builds are that small.
    "lab1ministral": ["min_iq2", "min_iq1", "docker", "ollama_image", "ollama_up", "min_ollama"],
    # Lab 1 bonus: the same model in Ollama, llama.cpp and KoboldCpp through Docker.
    # Part 4 only (the Docker runtimes), for people who already have the Part 1 and 2 files.
    "lab1bonus": ["docker", "ollama_image", "webui_image", "ollama_up", "qwen15_ollama", "kobold_image", "llamacpp_image"],
    "lab2": LAB1_CORE + ["docker", "ollama_image", "ollama_up", "qwen15_ollama", "qwen3_17_ollama",
                         "kobold_image", "llamacpp_image"],
    "lab3": LAB1_CORE + ["vscode_app", "continue_ext"],
    "lab4": ["pip_lab1", "p1_gguf", "p1_onnx", "qwen3_4b", "docker", "webui_image"],
    "lab5": ["docker"],
    "lab6": ["nielsen"],
    "lab7": ["p1_gguf", "phone_note"],
    "lab8": ["kobold_bin", "hermes_gguf", "kobold_qwen", "toolcall_note", "openclaw_note"],
    "lab9": ["p1_gguf", "abl_gguf"],
    # Model files only (the biggest downloads), in the order the labs need them.
    "models": ["p1_gguf", "p1_st", "p1_onnx", "qwen3_4b", "hermes_gguf", "kobold_qwen"],
    "bonus": ["docker", "ollama_image", "kobold_bin", "llamacpp_image", "bench_qwen05",
              "bench_llama1b", "bench_hermes3b", "bench_mistral7b", "big_models",
              "concierge_note", "hf_note"],
}
OWNER = {"pip_lab1": "lab1", "qwen3_4b": "lab1", "pip_torch": "lab1", "pip_hf": "lab1", "p1_gguf": "lab1",
         "p1_st": "lab1", "p1_onnx": "lab1", "qwen15_ollama": "lab1", "img_vit": "lab1images", "img_sdturbo": "lab1images",
         "min_iq2": "lab1ministral", "min_iq1": "lab1ministral", "min_ollama": "lab1ministral", "qwen3_17_ollama": "lab2", "qwen3_ollama": "lab1bonus", "kobold_image": "lab1",
         "docker": "lab1", "ollama_image": "lab1", "ollama_up": "lab1", "qwen05": "lab1",
         "webui_image": "lab1", "coder": "lab3", "continue_ext": "lab3", "vscode_app": "lab3", "kobold_cpu": "lab1",
         "nielsen": "lab6", "phone_note": "lab7", "kobold_bin": "lab8", "hermes_gguf": "lab8", "kobold_qwen": "lab8",
         "toolcall_note": "lab8", "openclaw_note": "lab8", "abl_gguf": "lab9"}
NEEDS = {"pip_hf": ["pip_torch"], "continue_ext": ["vscode_app"],  # accelerate needs torch: without torch, the whole install fails
         "ollama_image": ["docker"], "ollama_up": ["docker", "ollama_image"],
         "qwen05": ["ollama_up"], "coder": ["ollama_up"], "webui_image": ["docker"],
         "llamacpp_image": ["docker"], "kobold_image": ["docker"], "qwen3_ollama": ["ollama_up"], "qwen15_ollama": ["ollama_up"],
         "qwen3_17_ollama": ["ollama_up"], "min_ollama": ["ollama_up"]}


def os_key():
    s = platform.system()
    m = platform.machine().lower()
    if s == "Windows":
        return "windows"
    if s == "Darwin":
        return "mac-arm" if m in ("arm64", "aarch64") else "mac-intel"
    return "linux"


def build_catalog(a):
    """All items. est_mb is a rough size used only to weight the overall bar."""
    base = Path(a.dir).expanduser()
    bench = Path(a.bench_dir).expanduser()
    k = os_key()
    kname = {"windows": "koboldcpp.exe", "linux": "koboldcpp-linux-x64",
             "mac-arm": "koboldcpp-mac-arm64"}.get(k)
    c = {}

    def add(id_, name, kind, est=1, **kw):
        c[id_] = dict(id=id_, name=name, kind=kind, est_mb=est, status="waiting",
                      frac=0.0, done=0, total=0, speed=0.0, detail="", **kw)

    add("pip_lab1", "Python packages (llama-cpp-python, gguf, onnx, onnxruntime, transformers)", "pip", 150,
        pkgs=["llama-cpp-python", "gguf", "numpy", "safetensors", "onnx", "onnxruntime", "transformers", "jinja2"],
        mods=["llama_cpp", "gguf", "numpy", "safetensors", "onnx", "onnxruntime", "transformers", "jinja2"])
    # PyTorch: the CPU-only build on Linux and Windows (much smaller); the normal build on macOS.
    torch_index = [] if k.startswith("mac") else ["--index-url", "https://download.pytorch.org/whl/cpu"]
    add("pip_torch", "PyTorch (CPU build)", "pip", 250, pkgs=["torch"], mods=["torch"], index=torch_index)
    add("pip_hf", "Python packages (accelerate, diffusers, pillow)", "pip", 60,
        pkgs=["transformers", "accelerate", "diffusers", "pillow"], mods=["accelerate", "diffusers", "PIL"], index=[])
    add("p1_gguf", "Part 1 GGUF: Qwen2.5 1.5B Q4_K_M (1.1 GB)", "file", 1100,
        url=HF + "Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        dest=str(base / "models" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"), min_mb=800)
    add("p1_st", "Part 1 safetensors: Qwen2.5 0.5B (1.0 GB)", "files", 990, repo="Qwen/Qwen2.5-0.5B-Instruct",
        dest=str(base / "models" / "qwen2.5-0.5b-instruct"),
        files=[("config.json", 0), ("generation_config.json", 0), ("tokenizer.json", 1),
               ("tokenizer_config.json", 0), ("model.safetensors", 800)])
    add("p1_onnx", "Part 1 ONNX: Qwen2.5 0.5B, 8-bit", "files", 600, repo="onnx-community/Qwen2.5-0.5B-Instruct",
        dest=str(base / "models" / "qwen2.5-0.5b-instruct-onnx"),
        files=[("config.json", 0), ("generation_config.json", 0), ("tokenizer.json", 1),
               ("tokenizer_config.json", 0), ("onnx/model_quantized.onnx", 300)])
    add("qwen15_ollama", "Part 4a model in Ollama (qwen2.5:1.5b, 1 GB)", "ollama", 990,
        model="qwen2.5:1.5b", base=str(base))
    MIN = "unsloth/Ministral-3-3B-Instruct-2512-GGUF"
    add("min_iq2", "Ministral 3 3B, UD-IQ2_XXS GGUF (1.1 GB)", "file", 1109,
        url=HF + MIN + "/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf",
        dest=str(base / "models" / "Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf"), min_mb=900)
    add("min_iq1", "Ministral 3 3B, UD-IQ1_M GGUF (1.0 GB)", "file", 1019,
        url=HF + MIN + "/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf",
        dest=str(base / "models" / "Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf"), min_mb=800)
    add("min_ollama", "Ministral 3 in Ollama (needs Ollama 0.13.1+, 1.1 GB)", "ollama", 1109,
        model="hf.co/" + MIN + ":UD-IQ2_XXS", base=str(base))
    add("qwen3_17_ollama", "Lab 2 reasoning model in Ollama (qwen3:1.7b, 1.4 GB)", "ollama", 1400,
        model="qwen3:1.7b", base=str(base))
    add("img_vit", "Part 2c recognizer: google/vit-base-patch16-224 (0.35 GB)", "files", 350,
        repo="google/vit-base-patch16-224", dest=str(base / "models" / "vit-base-patch16-224"),
        files=[("config.json", 0), ("preprocessor_config.json", 0), ("model.safetensors", 300)])
    add("img_sdturbo", "Part 2c generator: stabilityai/sd-turbo, fp16 files (2.6 GB)", "files", 2600,
        repo="stabilityai/sd-turbo", dest=str(base / "models" / "sd-turbo"),
        files=[("model_index.json", 0), ("scheduler/scheduler_config.json", 0),
               ("text_encoder/config.json", 0), ("text_encoder/model.fp16.safetensors", 500),
               ("tokenizer/merges.txt", 0), ("tokenizer/special_tokens_map.json", 0),
               ("tokenizer/tokenizer_config.json", 0), ("tokenizer/vocab.json", 0),
               ("unet/config.json", 0), ("unet/diffusion_pytorch_model.fp16.safetensors", 1500),
               ("vae/config.json", 0), ("vae/diffusion_pytorch_model.fp16.safetensors", 100)])
    add("qwen3_4b", "Model Qwen3-4B Q4_K_M (2.5 GB)", "file", 2500,
        url=HF + "ggml-org/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf",
        dest=str(base / "models" / "Qwen3-4B-Q4_K_M.gguf"), min_mb=2000)
    add("qwen3_ollama", "Same model in Ollama (hf.co/ggml-org/Qwen3-4B-GGUF)", "ollama", 2500,
        model="hf.co/ggml-org/Qwen3-4B-GGUF:Q4_K_M", base=str(base))
    add("kobold_image", "KoboldCpp image (koboldai/koboldcpp, unverified on CPU)", "image", 1500,
        image="koboldai/koboldcpp:latest")
    add("docker", "Docker is installed and running", "docker", 1)
    add("ollama_image", "Ollama image (ollama/ollama)", "image", 1800, image="ollama/ollama:latest")
    add("ollama_up", "Start the Ollama container", "service", 1, service="ollama", base=str(base))
    add("qwen05", "Model qwen2.5:0.5b", "ollama", 400, model="qwen2.5:0.5b", base=str(base))
    add("webui_image", "Open WebUI image", "image", 3500, image="ghcr.io/open-webui/open-webui:main")
    add("coder", "Model qwen2.5-coder:1.5b", "ollama", 1000, model="qwen2.5-coder:1.5b", base=str(base))
    # Homework Lab 6: Michael Nielsen's code (MIT license), from the Python 3 fork, pinned to one commit.
    NNADL = ("https://raw.githubusercontent.com/unexploredtest/neural-networks-and-deep-learning/"
             "1f6f80702e06f1f70949177b479fc596754a3011/")
    add("nielsen", "Homework Lab 6: Nielsen's network code and MNIST data (17 MB)", "files", 17, base_url=NNADL,
        dest=str(base.parent / "Lab06" / "neural-networks-and-deep-learning"),
        files=[("README.md", 0), ("src/mnist_loader.py", 0), ("src/network.py", 0), ("src/network2.py", 0),
               ("data/mnist.pkl.gz", 15)])
    add("abl_gguf", "Homework Lab 9: abliterated Qwen2.5 1.5B, Q4_K_M (1 GB)", "file", 986,
        url=HF + "mradermacher/Qwen2.5-1.5B-Instruct-abliterated-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-abliterated.Q4_K_M.gguf",
        dest=str(base / "models" / "Qwen2.5-1.5B-Instruct-abliterated.Q4_K_M.gguf"), min_mb=800)
    add("phone_note", "Homework Lab 7: phone apps", "manual", 1,
        note="Not scripted. On the phone, install Google AI Edge Gallery and PocketPal AI from the app store, "
             "then follow the Lab 7 file for your computer in the Lab07 folder.")
    add("continue_ext", "Continue extension for VS Code", "vscode", 50, ext="Continue.continue")
    add("vscode_app", "VS Code (the 'code' command)", "app", 1, exe="code",
        note="VS Code is not installed, or 'code' is not on the PATH. Install it from https://code.visualstudio.com/download "
             + {"windows": "(select Add to PATH)", "linux": "(.deb or .rpm)"}.get(k, "(then run 'Shell Command: Install code command in PATH')")
             + ", then run this script again.")
    # Lab 1 Part 4b: the CPU build of KoboldCpp (small, no CUDA). Lab 8 uses the full build (kobold_bin).
    kcpu = {"windows": "koboldcpp-nocuda.exe", "linux": "koboldcpp-linux-x64-nocuda", "mac-arm": "koboldcpp-mac-arm64"}.get(k)
    if kcpu:
        add("kobold_cpu", "KoboldCpp program, CPU build (" + kcpu + ")", "file", 100,
            url=KOBOLD + kcpu, dest=str(base / "kobold" / kcpu), min_mb=20, exe=True)
    else:
        add("kobold_cpu", "KoboldCpp program", "manual", 1,
            note="No ready-made Intel Mac build. Use the KoboldCpp container (Part 4b), or pair up.")
    if kname:
        add("kobold_bin", "KoboldCpp program (" + kname + ")", "file", 600,
            url=KOBOLD + kname, dest=str(base / "kobold" / kname), min_mb=20, exe=True)
    else:
        add("kobold_bin", "KoboldCpp program", "manual", 1,
            note="No ready-made Intel Mac build. Build it from source (see the KoboldCpp README) or pair up.")
    add("hermes_gguf", "Hermes 3 3B model (Q4_K_M, about 2 GB)", "file", 2020,
        url=HF + "NousResearch/Hermes-3-Llama-3.2-3B-GGUF/resolve/main/Hermes-3-Llama-3.2-3B.Q4_K_M.gguf",
        dest=str(base / "kobold" / "hermes3b.gguf"), min_mb=1500)
    add("kobold_qwen", "Qwen2.5 0.5B model for KoboldCpp (0.4 GB)", "file", 398,
        url=HF + "bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        dest=str(base / "kobold" / "qwen05.gguf"), min_mb=300)
    add("toolcall_note", "toolcall_test.py (from the handout)", "manual", 1,
        note="Not scripted yet. See Lab 8, Part 0b, in the Lab08 folder.")
    add("openclaw_note", "OpenClaw (agent harness)", "manual", 1,
        note="Not scripted: install steps are unverified. Follow Lab 8, Part 0, in the Lab08 folder. Use it only in a sandbox virtual machine.")
    add("llamacpp_image", "llama.cpp server image", "image", 300, image="ghcr.io/ggml-org/llama.cpp:server")
    add("bench_qwen05", "Benchmark model qwen05.gguf (0.4 GB)", "file", 398,
        url=HF + "bartowski/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
        dest=str(bench / "models" / "qwen05.gguf"), min_mb=300,
        alias=str(base / "kobold" / "qwen05.gguf"))
    add("bench_llama1b", "Benchmark model llama1b.gguf (0.8 GB)", "file", 808,
        url=HF + "bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        dest=str(bench / "models" / "llama1b.gguf"), min_mb=600)
    add("bench_hermes3b", "Benchmark model hermes3b.gguf (2 GB)", "file", 2020,
        url=HF + "NousResearch/Hermes-3-Llama-3.2-3B-GGUF/resolve/main/Hermes-3-Llama-3.2-3B.Q4_K_M.gguf",
        dest=str(bench / "models" / "hermes3b.gguf"), min_mb=1500,
        alias=str(base / "kobold" / "hermes3b.gguf"))
    if a.with_mistral:
        add("bench_mistral7b", "Benchmark model mistral7b.gguf (4.4 GB, needs 16 GB RAM)", "file", 4370,
            url=HF + "bartowski/Mistral-7B-Instruct-v0.3-GGUF/resolve/main/Mistral-7B-Instruct-v0.3-Q4_K_M.gguf",
            dest=str(bench / "models" / "mistral7b.gguf"), min_mb=3500)
    else:
        add("bench_mistral7b", "Benchmark model mistral7b.gguf (optional, 4.4 GB)", "manual", 1,
            note="Skipped. Add --with-mistral if you have 16 GB of RAM or more.")
    if a.big:
        add("big_models", "Larger Ollama models (qwen2.5:7b)", "ollama", 4700,
            model="qwen2.5:7b", base=str(base))
    else:
        add("big_models", "Larger Ollama models (optional)", "manual", 1,
            note="Skipped. Add --big for qwen2.5:7b (about 4.7 GB).")
    add("concierge_note", "Data Concierge (Bonus 5)", "manual", 1,
        note="Not scripted. Get it from github.com/InfoSecInnovations/concierge/releases. Needs 16 GB of RAM. Verify the install steps first.")
    add("hf_note", "Hugging Face model (Bonus 11)", "manual", 1,
        note="You pick the model in the lab. Check the file and its license before you download.")
    return c


def plan_items(a):
    cat = build_catalog(a)
    targets = WORKSHOP_ORDER if a.target == "all" else [a.target]
    ids = []
    for t in targets:
        for i in TARGET_ITEMS[t]:
            if i not in ids:
                ids.append(i)
    # Docker-backed items run in dependency order even when listed late.
    out = []
    for i in ids:
        it = cat[i]
        it["lab"] = LAB_NAMES.get(OWNER.get(i, a.target), "Bonus" if a.target == "bonus" else "")
        out.append(it)
    return out


# ------------------------------------------------------------------ runners
def run_cmd(cmd, **kw):
    return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True, **kw)


def docker_ok():
    if not shutil.which("docker"):
        return False, "Docker is not installed. Install Docker Desktop (or Docker Engine on Linux) first."
    r = run_cmd(["docker", "info"])
    if r.returncode != 0:
        return False, "Docker is installed but not running. Start Docker Desktop and wait until it says running."
    return True, "ready"


def do_docker(it, a):
    deadline = time.time() + a.wait_docker * 60
    while True:
        ok, msg = docker_ok()
        if ok:
            it["detail"] = "running"
            return
        it["detail"] = msg
        if time.time() > deadline:
            raise RuntimeError(msg)
        time.sleep(5)


LAYER_W = {"pulling fs layer": 0.0, "waiting": 0.0, "downloading": 0.2, "verifying checksum": 0.7,
           "download complete": 0.8, "extracting": 0.9, "pull complete": 1.0, "already exists": 1.0}


def do_image(it, a):
    img = it["image"]
    if run_cmd(["docker", "image", "inspect", img]).returncode == 0:
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "already on this machine"
        return
    p = subprocess.Popen(["docker", "pull", img], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         universal_newlines=True, bufsize=1)
    layers = {}
    tail = []
    for line in p.stdout:
        line = line.strip()
        tail = (tail + [line])[-3:]
        m = re.match(r"^([0-9a-f]{6,}):\s*(.+)$", line)
        if m:
            lid, msg = m.group(1), m.group(2).lower()
            for key, w in LAYER_W.items():
                if msg.startswith(key):
                    layers[lid] = max(layers.get(lid, 0), w)
                    break
        if layers:
            it["frac"] = sum(layers.values()) / len(layers)
            it["detail"] = "%d of %d layers" % (sum(1 for v in layers.values() if v >= 1.0), len(layers))
    if p.wait() != 0:
        raise RuntimeError("docker pull failed: " + " | ".join(tail))
    it["frac"] = 1.0


def compose(base, *args):
    f = Path(base) / "compose.yaml"
    if not f.exists():
        f = Path(base) / "compose.yml"
    if not f.exists():
        raise RuntimeError("compose.yaml not found in %s. Use --dir to point at your ai-night folder." % base)
    return run_cmd(["docker", "compose", "-f", str(f)] + list(args), cwd=str(base))


def ollama_up_check():
    try:
        urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3).read()
        return True
    except Exception:
        return False


def do_service(it, a):
    if ollama_up_check():
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "already running"
        return
    it["detail"] = "docker compose up -d " + it["service"]
    r = compose(it["base"], "up", "-d", it["service"])
    if r.returncode != 0:
        raise RuntimeError("compose up failed: " + r.stdout.strip()[-200:])
    for _ in range(60):
        if ollama_up_check():
            it["frac"] = 1.0
            return
        time.sleep(1)
    raise RuntimeError("Ollama did not answer on " + OLLAMA + ". Check that compose publishes port 11434.")


def ollama_has(model):
    try:
        d = json.loads(urllib.request.urlopen(OLLAMA + "/api/tags", timeout=5).read().decode())
        names = [m.get("name", "") for m in d.get("models", [])]
        return model in names or (":" not in model and model + ":latest" in names)
    except Exception:
        return False


def do_ollama(it, a):
    model = it["model"]
    if ollama_has(model):
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "already pulled"
        return
    req = urllib.request.Request(OLLAMA + "/api/pull", data=json.dumps({"model": model, "stream": True}).encode(),
                                 headers={"Content-Type": "application/json"})
    totals, comp = {}, {}
    with urllib.request.urlopen(req, timeout=120) as r:
        for raw in r:
            if not raw.strip():
                continue
            d = json.loads(raw.decode())
            if d.get("error"):
                raise RuntimeError(d["error"])
            dig = d.get("digest")
            if dig and d.get("total"):
                totals[dig] = d["total"]
                comp[dig] = d.get("completed", 0)
                it["total"], it["done"] = sum(totals.values()), sum(comp.values())
                it["frac"] = it["done"] / float(it["total"])
            it["detail"] = d.get("status", "")[:40]
    it["frac"] = 1.0


def do_vscode(it, a):
    code = shutil.which("code")
    if not code:
        it["status"], it["detail"] = "manual", "VS Code command 'code' not found. Install the extension from the VS Code Extensions tab: " + it["ext"]
        return
    r = run_cmd([code, "--install-extension", it["ext"], "--force"])
    if r.returncode != 0:
        raise RuntimeError(r.stdout.strip()[-200:])
    it["frac"] = 1.0
    it["detail"] = "installed"


def do_app(it, a):
    if shutil.which(it["exe"]):
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "installed"
        return
    raise RuntimeError(it["note"])


def sha256_file(path, it):
    h = hashlib.sha256()
    size = max(path.stat().st_size, 1)
    done = 0
    with open(str(path), "rb") as f:
        while True:
            b = f.read(4 * 1024 * 1024)
            if not b:
                break
            h.update(b)
            done += len(b)
            it["detail"] = "verifying sha256 %d%%" % (100 * done // size)
    return h.hexdigest()


def do_file(it, a):
    dest = Path(it["dest"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size >= it.get("min_mb", 1) * 1024 * 1024:
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "already at " + str(dest)
        return
    alias = it.get("alias")
    if alias and Path(alias).exists() and Path(alias).stat().st_size >= it.get("min_mb", 1) * 1024 * 1024:
        shutil.copy2(alias, str(dest))
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "copied from " + alias
        return
    part = Path(str(dest) + ".part")
    last_err = None
    for attempt in range(1, 6):
        try:
            pos = part.stat().st_size if part.exists() else 0
            headers = dict(UA)
            if pos:
                headers["Range"] = "bytes=%d-" % pos
            with urllib.request.urlopen(urllib.request.Request(it["url"], headers=headers), timeout=30) as r:
                status = getattr(r, "status", 200)
                clen = int(r.headers.get("Content-Length") or 0)
                if pos and status != 206:
                    pos = 0
                total = clen + pos
                etag = (r.headers.get("X-Linked-Etag") or "").strip('"')
                it["total"] = total
                with open(str(part), "ab" if pos else "wb") as f:
                    got = pos
                    while True:
                        chunk = r.read(1024 * 1024)
                        if not chunk:
                            break
                        f.write(chunk)
                        got += len(chunk)
                        it["done"] = got
                        if total:
                            it["frac"] = got / float(total)
            if total and part.stat().st_size != total:
                raise IOError("incomplete download, retrying")
            break
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise RuntimeError("HTTP %d: the file needs a login or license acceptance. Download it by hand from the model page." % e.code)
            last_err = e
        except Exception as e:
            last_err = e
        it["detail"] = "retry %d after: %s" % (attempt, str(last_err)[:40])
        time.sleep(min(30, 3 * attempt))
    else:
        raise RuntimeError("download failed: %s" % last_err)
    if re.fullmatch(r"[0-9a-f]{64}", etag or ""):
        got_hash = sha256_file(part, it)
        if got_hash != etag:
            part.unlink()
            raise RuntimeError("sha256 does not match the published value. File deleted. Run again.")
        it["detail"] = "sha256 verified"
    else:
        it["detail"] = "no published checksum"
    part.replace(dest)
    if it.get("exe") and os.name != "nt":
        dest.chmod(dest.stat().st_mode | 0o111)
    it["frac"] = 1.0


def do_files(it, a):
    """Several files from one Hugging Face repository into one folder (a safetensors or ONNX model)."""
    files = it["files"]
    skipped = 0
    for n, (rel, min_mb) in enumerate(files):
        sub = dict(url=(it.get("base_url") or (HF + it["repo"] + "/resolve/main/")) + rel, dest=str(Path(it["dest"]) / rel),
                   min_mb=min_mb, status="", frac=0.0, done=0, total=0, detail="")
        do_file(sub, a)
        skipped += sub["status"] == "skipped"
        it["frac"] = (n + 1) / float(len(files))
        it["detail"] = "%d of %d files" % (n + 1, len(files))
    if skipped == len(files):
        it["status"], it["detail"] = "skipped", "already at " + it["dest"]


def do_pip(it, a):
    """Install Python packages. The CPU wheel index gives llama-cpp-python a prebuilt wheel."""
    missing = []
    for m in it["mods"]:
        r = run_cmd([sys.executable, "-c", "import " + m])
        if r.returncode != 0:
            missing.append(m)
    if not missing:
        it["status"], it["frac"], it["detail"] = "skipped", 1.0, "already installed"
        return
    index = it.get("index")
    if index is None:  # the default: the CPU wheel index gives llama-cpp-python a prebuilt wheel
        index = ["--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cpu"]
    cmd = [sys.executable, "-m", "pip", "install"] + index + it["pkgs"]
    it["detail"] = "pip install (may take a minute)"
    r = run_cmd(cmd)
    if r.returncode != 0:
        tail = " ".join(r.stdout.strip().splitlines()[-2:])[:140]
        raise RuntimeError("pip failed: " + tail + " | see Lab 1, Part 0c, 'If llama-cpp-python does not install'")
    it["frac"] = 1.0
    it["detail"] = "installed"


def do_manual(it, a):
    it["status"] = "manual"
    it["detail"] = it.get("note", "")


RUNNERS = {"files": do_files, "docker": do_docker, "image": do_image, "service": do_service, "ollama": do_ollama,
           "vscode": do_vscode, "app": do_app, "file": do_file, "manual": do_manual, "pip": do_pip}


def worker(items, a, lock):
    for it in items:
        blocked = [i for i in NEEDS.get(it["id"], []) if i in BLOCKERS and BLOCKERS[i]]
        if blocked:
            it["status"], it["detail"] = "failed", "blocked: " + ", ".join(blocked) + " did not finish"
            BLOCKERS[it["id"]] = True
            continue
        it["status"] = "running"
        it["t0"] = time.time()
        try:
            RUNNERS[it["kind"]](it, a)
            if it["status"] == "running":
                it["status"] = "done"
                it["frac"] = 1.0
            BLOCKERS[it["id"]] = False
        except Exception as e:  # keep going with the other downloads
            it["status"] = "failed"
            it["detail"] = str(e)[:160]
            BLOCKERS[it["id"]] = True
        it["speed"] = 0.0


BLOCKERS = {}

# ------------------------------------------------------------------ check (no downloads)
def check_item(it):
    """Is this item ready on this computer? Returns (True, False or None for 'cannot tell', detail)."""
    k = it["kind"]
    mb = lambda p, m: Path(p).exists() and Path(p).stat().st_size >= m * 1024 * 1024
    if k == "pip":
        bad = [m for m in it["mods"] if run_cmd([sys.executable, "-c", "import " + m]).returncode != 0]
        return (not bad), ("missing Python package(s): " + ", ".join(bad)) if bad else "installed"
    if k == "file":
        return mb(it["dest"], it.get("min_mb", 1)), it["dest"]
    if k == "files":
        bad = [rel for rel, m in it["files"] if not mb(Path(it["dest"]) / rel, m)]
        return (not bad), ("missing: " + ", ".join(bad)) if bad else it["dest"]
    if k == "docker":
        ok, msg = docker_ok()
        return ok, msg
    if k == "image":
        if not docker_ok()[0]:
            return None, "Docker is not running: cannot check"
        ok = run_cmd(["docker", "image", "inspect", it["image"]]).returncode == 0
        return ok, it["image"]
    if k == "ollama":
        if not ollama_up_check():
            return None, "Ollama is not running: start it (docker compose --profile ollama up -d), then check again"
        return ollama_has(it["model"]), it["model"]
    if k == "vscode":
        code = shutil.which("code")
        if not code:
            return False, "VS Code ('code') not found"
        exts = run_cmd([code, "--list-extensions"]).stdout.lower().split()
        return it["ext"].lower() in exts, it["ext"]
    if k == "app":
        return bool(shutil.which(it["exe"])), it.get("note", "") if not shutil.which(it["exe"]) else "installed"
    return None, ""  # services and manual notes


def do_check(items, a):
    print("Check: is this computer ready? (nothing is downloaded)\n")
    missing = 0
    for it in items:
        if it["kind"] in ("service", "manual"):
            continue
        ok, detail = check_item(it)
        tag = "READY  " if ok else ("MISSING" if ok is False else "UNKNOWN")
        missing += ok is False
        print("  %s %-9s %-50s %s" % (tag, it.get("lab", ""), it["name"][:50], detail[:90]))
    if missing:
        print("\n%d item(s) are missing. Run the pre-fetch script again while you are online." % missing)
        return 1
    print("\nReady. Every item that this check can see is on this computer.")
    return 0


def warn_setup(a):
    """Warnings that the Linux offline test found: the wrong Python, and a virtual environment in a synced folder."""
    if sys.version_info[:2] != (3, 12):
        print("Note: this is Python %d.%d. The workshop uses Python 3.12. Other versions from 3.10 can work "
              "online, but the USB copy has packages for 3.12 only." % sys.version_info[:2])
    path = (os.path.abspath(a.dir) + " " + sys.prefix).lower()
    for word in ("onedrive", "dropbox", "icloud", "mobile documents", "google drive", "googledrive", "box sync"):
        if word in path:
            print("Note: the folder is in a synchronized folder (%s). The virtual environment and the models are "
                  "slow there, and the sync program uploads several GB. Move the Ai-workshop folder to a local "
                  "folder, for example in your home folder." % word)
            break


# ------------------------------------------------------------------ display
def enable_vt():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.GetStdHandle(-11)
            m = ctypes.c_uint()
            k.GetConsoleMode(h, ctypes.byref(m))
            k.SetConsoleMode(h, m.value | 4)
        except Exception:
            pass


def fmt_bytes(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%.0f %s" if u in ("B", "KB") else "%.1f %s") % (n, u)
        n /= 1024


def fmt_time(s):
    s = int(max(s, 0))
    return "%d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60) if s >= 3600 else "%02d:%02d" % (s // 60, s % 60)


class View:
    def __init__(self, items, title, color=True):
        self.items, self.title = items, title
        self.t0 = time.time()
        enc = (sys.stdout.encoding or "").lower()
        self.uni = "utf" in enc
        self.fill, self.empty = ("█", "░") if self.uni else ("#", "-")
        self.sym = {"waiting": ("…" if self.uni else ".."), "running": ("▶" if self.uni else ">>"),
                    "done": ("✔" if self.uni else "OK"), "skipped": ("✔" if self.uni else "OK"),
                    "failed": ("✖" if self.uni else "XX"), "manual": ("✋" if self.uni else "!!")}
        self.col = color and sys.stdout.isatty()
        self.last_lines = 0
        self.prev = {}
        self.ospeed = 0.0
        self.otime = time.time()
        self.obytes = 0.0

    def bar(self, f, w=20):
        n = int(round(max(0.0, min(1.0, f)) * w))
        return self.fill * n + self.empty * (w - n)

    def c(self, code, s):
        return "\033[%sm%s\033[0m" % (code, s) if self.col else s

    def weights(self):
        return [max(it["total"] / 1048576.0 if it["total"] else it["est_mb"], 1.0) for it in self.items]

    def overall(self):
        ws = self.weights()
        fr = [1.0 if it["status"] in ("done", "skipped", "manual", "failed") else it["frac"] for it in self.items]
        return sum(w * f for w, f in zip(ws, fr)) / sum(ws), ws, fr

    def tick(self):
        now = time.time()
        # per-item speed from byte counters
        tot_b = 0.0
        for it in self.items:
            b = it["done"]
            tot_b += b if it["kind"] in ("file", "ollama") else it["frac"] * it["est_mb"] * 1048576
            p = self.prev.get(it["id"])
            if p and it["status"] == "running" and now - p[0] >= 1.0 and it["kind"] in ("file", "ollama"):
                inst = (b - p[1]) / (now - p[0])
                it["speed"] = inst if it["speed"] == 0 else 0.6 * it["speed"] + 0.4 * inst
                self.prev[it["id"]] = (now, b)
            elif not p:
                self.prev[it["id"]] = (now, b)
        if now - self.otime >= 2.0:
            inst = max(tot_b - self.obytes, 0) / (now - self.otime)
            self.ospeed = inst if self.ospeed == 0 else 0.6 * self.ospeed + 0.4 * inst
            self.otime, self.obytes = now, tot_b

    def lines(self):
        self.tick()
        of, ws, fr = self.overall()
        n = len(self.items)
        cnt = {}
        for it in self.items:
            cnt[it["status"]] = cnt.get(it["status"], 0) + 1
        done = cnt.get("done", 0) + cnt.get("skipped", 0)
        rem_b = sum(w * (1 - f) for w, f in zip(ws, fr)) * 1048576
        eta = ("  ETA ~" + fmt_time(rem_b / self.ospeed)) if self.ospeed > 50000 and rem_b > 0 else ""
        out = [self.c("1", self.title) + "   elapsed " + fmt_time(time.time() - self.t0)]
        out.append("Overall  [%s] %3d%%   %d of %d finished%s" % (self.bar(of, 30), of * 100, done + cnt.get("manual", 0) + cnt.get("failed", 0), n, eta))
        out.append("")
        for it in self.items:
            s = it["status"]
            tag = {"waiting": "waiting", "running": "running", "done": "done   ", "skipped": "had it ",
                   "failed": "FAILED ", "manual": "manual "}[s]
            colr = {"done": "32", "skipped": "32", "running": "36", "failed": "31", "manual": "33", "waiting": "90"}[s]
            f = 1.0 if s in ("done", "skipped") else it["frac"]
            size = ""
            if it["total"]:
                size = "%s / %s" % (fmt_bytes(it["done"]), fmt_bytes(it["total"]))
            if s == "running" and it["speed"] > 0:
                size += "  %s/s" % fmt_bytes(it["speed"])
            line = "%s %s %-9s %-46s" % (self.sym[s], self.c(colr, tag), (it.get("lab") or "")[:9], it["name"][:46])
            if s in ("manual", "failed"):
                out.append(line)
                out.append("      " + self.c(colr, it["detail"][:100]))
            else:
                out.append("%s [%s] %3d%%  %s" % (line, self.bar(f), f * 100, size.strip()))
                if s == "running" and it["detail"]:
                    out.append("      " + self.c("90", it["detail"][:100]))
        out.append("")
        have = [it["name"] for it in self.items if it["status"] in ("done", "skipped")]
        run = [it["name"] for it in self.items if it["status"] == "running"]
        left = [it["name"] for it in self.items if it["status"] == "waiting"]
        out.append(self.c("32", "Downloaded (%d): " % len(have)) + (", ".join(have) or "nothing yet")[:140])
        out.append(self.c("36", "In progress (%d): " % len(run)) + (", ".join(run) or "nothing")[:140])
        out.append(self.c("90", "Remaining (%d): " % len(left)) + (", ".join(left) or "nothing")[:140])
        if cnt.get("failed"):
            out.append(self.c("31", "Failed (%d). Fix the cause, then run the same command again. It resumes." % cnt["failed"]))
        return out

    def draw(self):
        ls = self.lines()
        if self.col:
            if self.last_lines:
                sys.stdout.write("\033[%dA" % self.last_lines)
            sys.stdout.write("".join("\033[2K" + l + "\n" for l in ls))
            extra = self.last_lines - len(ls)
            if extra > 0:
                sys.stdout.write("\033[2K\n" * extra + "\033[%dA" % extra)
            self.last_lines = len(ls)
        else:
            sys.stdout.write("\n".join(ls) + "\n\n")
        sys.stdout.flush()


# ------------------------------------------------------------------ main
def state_path(a):
    return Path(a.dir).expanduser() / "prefetch" / "state.json"


def save_state(items, a, view, running=True):
    p = state_path(a)
    p.parent.mkdir(parents=True, exist_ok=True)
    of = view.overall()[0]
    p.write_text(json.dumps({"target": a.target, "running": running, "updated": time.time(),
                             "overall": of, "title": view.title, "items": items}, default=str))


def show_status(a):
    p = state_path(a)
    if not p.exists():
        print("No prefetch run found in %s" % p.parent)
        return
    while True:
        d = json.loads(p.read_text())
        v = View(d["items"], d["title"] + ("  (running)" if d["running"] else "  (finished)"))
        v.col = False
        print("\n".join(v.lines()))
        if not a.watch or not d["running"]:
            return
        time.sleep(3)
        print("-" * 40)


def parse(argv):
    ap = argparse.ArgumentParser(description="Workshop download helper", formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    ap.add_argument("target", nargs="?", choices=WORKSHOP_ORDER + ["lab1bonus", "lab1images", "lab1ministral", "lab6", "lab7", "lab8", "lab9", "all", "bonus", "models"])
    # The handout keeps the models, kobold/ and compose.yaml in the Lab01 folder next to this one.
    here_lab1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Lab01")
    default_dir = os.environ.get("AI_NIGHT_DIR") or (os.path.normpath(here_lab1) if os.path.isdir(here_lab1) else "~/ai-night")
    ap.add_argument("--dir", default=default_dir, help="the folder that holds models/ and compose.yaml (default: ../Lab01)")
    ap.add_argument("--bench-dir", default="~/bench", help="benchmark folder (default ~/bench)")
    ap.add_argument("--dry-run", action="store_true", help="show the plan and sizes, download nothing")
    ap.add_argument("--check", action="store_true", help="examine what is on this computer and what is missing, download nothing")
    ap.add_argument("--background", action="store_true", help="run detached; progress goes to a log and a state file")
    ap.add_argument("--status", action="store_true", help="show progress of the last or current run")
    ap.add_argument("--watch", action="store_true", help="with --status, keep refreshing")
    ap.add_argument("--with-mistral", action="store_true", help="bonus: include Mistral 7B (4.4 GB, needs 16 GB RAM)")
    ap.add_argument("--big", action="store_true", help="bonus: include qwen2.5:7b through Ollama")
    ap.add_argument("--wait-docker", type=int, default=10, help="minutes to wait for Docker to start (default 10)")
    ap.add_argument("--no-color", action="store_true")
    a = ap.parse_args(argv)
    if not a.status and not a.target:
        ap.error("choose a target: " + ", ".join(WORKSHOP_ORDER + ["lab1bonus", "lab1images", "lab1ministral", "lab6", "lab7", "lab8", "lab9", "all", "bonus", "models"]))
    return a


def main(argv=None):
    a = parse(sys.argv[1:] if argv is None else argv)
    enable_vt()
    if a.status:
        show_status(a)
        return 0
    items = plan_items(a)
    if a.check:
        return do_check(items, a)
    warn_setup(a)
    title = "BSidesDFW downloads: " + {"all": "all workshop labs", "bonus": "bonus labs"}.get(a.target, LAB_NAMES.get(a.target, a.target))
    need_mb = sum(i["est_mb"] for i in items if i["kind"] in ("file", "files", "image", "ollama", "vscode", "pip"))
    try:
        free_mb = shutil.disk_usage(str(Path(a.dir).expanduser() if Path(a.dir).expanduser().exists() else Path.home())).free / 1048576
    except Exception:
        free_mb = None
    if a.dry_run:
        print(title, "(dry run)")
        for it in items:
            print("  %-9s %-52s ~%5d MB  [%s]" % (it.get("lab", ""), it["name"], it["est_mb"], it["kind"]))
        print("About %.1f GB to download. Free space: %s" % (need_mb / 1024.0, ("%.1f GB" % (free_mb / 1024.0)) if free_mb else "unknown"))
        return 0
    if a.background:
        log = Path(a.dir).expanduser() / "prefetch" / "prefetch.log"
        log.parent.mkdir(parents=True, exist_ok=True)
        args = [sys.executable, os.path.abspath(__file__)] + [x for x in (sys.argv[1:] if argv is None else argv) if x != "--background"]
        lf = open(str(log), "a")
        kw = {"stdin": subprocess.DEVNULL, "stdout": lf, "stderr": lf, "close_fds": True}
        if os.name == "nt":
            kw["creationflags"] = 0x00000008 | 0x00000200
        else:
            kw["start_new_session"] = True
        pr = subprocess.Popen(args, **kw)
        print("Started in the background (process %d). Check progress any time with:\n  %s %s --status --watch\nLog: %s"
              % (pr.pid, "py -3" if os.name == "nt" else "python3", os.path.basename(__file__), log))
        return 0
    if free_mb is not None and free_mb < need_mb * 1.2:
        print("Warning: this needs about %.1f GB and %.1f GB is free. Free some space first." % (need_mb / 1024.0, free_mb / 1024.0))
    print(title + "  (Ctrl+C stops; run it again to resume)\n")
    view = View(items, title, not a.no_color)
    lock = threading.Lock()
    t = threading.Thread(target=worker, args=(items, a, lock), daemon=True)
    t.start()
    last_log = {}
    try:
        while t.is_alive():
            view.draw() if view.col else None
            if not view.col:
                for it in items:
                    key = (it["status"], int(it["frac"] * 10))
                    if last_log.get(it["id"]) != key:
                        last_log[it["id"]] = key
                        print("[%s] %-8s %3d%%  %s %s" % (time.strftime("%H:%M:%S"), it["status"], it["frac"] * 100, it["name"], it["detail"][:80]))
                        sys.stdout.flush()
            save_state(items, a, view)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopped. Partial files stay in place. Run the same command to resume.")
        save_state(items, a, view, running=False)
        return 130
    save_state(items, a, view, running=False)
    if view.col:
        view.draw()
    else:
        print("\n".join(view.lines()))
    failed = [i for i in items if i["status"] == "failed"]
    print("\nFinished with %d problem(s)." % len(failed) if failed else "\nAll done.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
