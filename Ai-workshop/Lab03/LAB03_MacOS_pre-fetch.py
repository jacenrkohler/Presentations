#!/usr/bin/env python3
"""
LAB03_MacOS_pre-fetch.py - download every file that Lab 3 (Integrations and Tooling) needs on macOS (Apple silicon), so that the lab runs without the internet.

The files go into the download folder (Downloads/MacOS next to the lab folders, or the USB folder that holds
this Ai-workshop folder). Then follow the ..._OFFLINE.md walkthrough. The script can run on any operating system.
It needs Python 3 with pip (3.8 or newer), and Docker for the Docker images and the Ollama models.

    python3 LAB03_MacOS_pre-fetch.py                  (Windows: py -3 LAB03_MacOS_pre-fetch.py)
Options:
    --dry-run      show what is present and what is missing, download nothing
    --optional     also the optional files (Ministral 3, image models)
    --gpu          also the NVIDIA GPU files, into the folder gpu (not for macOS: the normal files use Metal)
    --skip-docker  do not save the Docker images or the Ollama models
    --refresh      ask pip again for the newest Python packages
    --dest DIR     use DIR as the download folder
The script examines each file before it downloads it. Files that are present are skipped. It downloads one file at
a time and keeps partial files, so if the connection stops, run it again: it continues where it stopped.
The same script is also in Bash (.sh) and PowerShell (.ps1). They do the same work.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

OS_NAME = "MacOS"
LABS = "3"      # the labs that this script downloads for
ROOT_UP = 1        # 1: this script is in a Lab folder; 0: in the Ai-workshop folder
PIP_SHIM = "import sys,runpy; import pip._vendor.packaging.markers as m; o=m.default_environment; t=dict(x.split('=',1) for x in sys.argv[1].split(';')); m.default_environment=lambda: dict(o(), **t); sys.argv=['pip']+sys.argv[2:]; runpy.run_module('pip', run_name='__main__', alter_sys=True)"
PIP_ENV = "os_name=posix;sys_platform=darwin;platform_system=Darwin;platform_machine=arm64"
M = json.loads(r'''{
 "platform": [
  "macosx_14_0_arm64"
 ],
 "files": [
  [
   "base",
   "1234",
   "python-3.12.10-macos11.pkg",
   "https://www.python.org/ftp/python/3.12.10/python-3.12.10-macos11.pkg"
  ],
  [
   "base",
   "124",
   "Docker-arm64.dmg",
   "https://desktop.docker.com/mac/main/arm64/Docker.dmg"
  ],
  [
   "base",
   "3",
   "VSCode-darwin-universal.zip",
   "https://update.code.visualstudio.com/latest/darwin-universal/stable"
  ],
  [
   "base",
   "3",
   "continue-darwin-arm64-1.3.40.vsix",
   "https://github.com/continuedev/continue/releases/download/v1.3.40-vscode/continue-darwin-arm64-1.3.40.vsix"
  ],
  [
   "base",
   "3",
   "Obsidian-1.15.0.dmg",
   "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.15.0/Obsidian-1.15.0.dmg"
  ],
  [
   "base",
   "1",
   "koboldcpp-mac-arm64",
   "https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp-mac-arm64"
  ],
  [
   "base",
   "1234",
   "llama_cpp_python-0.3.36-py3-none-macosx_11_0_arm64.whl",
   "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36/llama_cpp_python-0.3.36-py3-none-macosx_11_0_arm64.whl"
  ],
  [
   "base",
   "1234",
   "qwen2.5-1.5b-instruct-q4_k_m.gguf",
   "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
  ],
  [
   "base",
   "1234",
   "Qwen3-4B-Q4_K_M.gguf",
   "https://huggingface.co/ggml-org/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf"
  ],
  [
   "base",
   "123",
   "qwen2.5-0.5b-instruct/config.json",
   "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
  ],
  [
   "base",
   "123",
   "qwen2.5-0.5b-instruct/generation_config.json",
   "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
  ],
  [
   "base",
   "123",
   "qwen2.5-0.5b-instruct/tokenizer.json",
   "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
  ],
  [
   "base",
   "123",
   "qwen2.5-0.5b-instruct/tokenizer_config.json",
   "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
  ],
  [
   "base",
   "123",
   "qwen2.5-0.5b-instruct/model.safetensors",
   "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors"
  ],
  [
   "base",
   "1234",
   "qwen2.5-0.5b-instruct-onnx/config.json",
   "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
  ],
  [
   "base",
   "1234",
   "qwen2.5-0.5b-instruct-onnx/generation_config.json",
   "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
  ],
  [
   "base",
   "1234",
   "qwen2.5-0.5b-instruct-onnx/tokenizer.json",
   "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
  ],
  [
   "base",
   "1234",
   "qwen2.5-0.5b-instruct-onnx/tokenizer_config.json",
   "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
  ],
  [
   "base",
   "1234",
   "qwen2.5-0.5b-instruct-onnx/onnx/model_quantized.onnx",
   "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/onnx/model_quantized.onnx"
  ],
  [
   "optional",
   "12",
   "Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf",
   "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf"
  ],
  [
   "optional",
   "12",
   "Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf",
   "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf"
  ],
  [
   "optional",
   "1",
   "vit-base-patch16-224/config.json",
   "https://huggingface.co/google/vit-base-patch16-224/resolve/main/config.json"
  ],
  [
   "optional",
   "1",
   "vit-base-patch16-224/preprocessor_config.json",
   "https://huggingface.co/google/vit-base-patch16-224/resolve/main/preprocessor_config.json"
  ],
  [
   "optional",
   "1",
   "vit-base-patch16-224/model.safetensors",
   "https://huggingface.co/google/vit-base-patch16-224/resolve/main/model.safetensors"
  ],
  [
   "optional",
   "1",
   "sd-turbo/model_index.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/model_index.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/scheduler/scheduler_config.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/scheduler/scheduler_config.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/text_encoder/config.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/config.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/text_encoder/model.fp16.safetensors",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/model.fp16.safetensors"
  ],
  [
   "optional",
   "1",
   "sd-turbo/tokenizer/merges.txt",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/merges.txt"
  ],
  [
   "optional",
   "1",
   "sd-turbo/tokenizer/special_tokens_map.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/special_tokens_map.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/tokenizer/tokenizer_config.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/tokenizer_config.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/tokenizer/vocab.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/vocab.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/unet/config.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/config.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/unet/diffusion_pytorch_model.fp16.safetensors",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors"
  ],
  [
   "optional",
   "1",
   "sd-turbo/vae/config.json",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/config.json"
  ],
  [
   "optional",
   "1",
   "sd-turbo/vae/diffusion_pytorch_model.fp16.safetensors",
   "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/diffusion_pytorch_model.fp16.safetensors"
  ]
 ],
 "index_files": [],
 "pip": [
  [
   "base",
   "1234",
   "core",
   ".",
   [
    ""
   ],
   false,
   [
    "gguf",
    "numpy",
    "safetensors",
    "onnx",
    "onnxruntime",
    "transformers",
    "jinja2",
    "diskcache",
    "typing-extensions"
   ]
  ],
  [
   "base",
   "123",
   "hf",
   ".",
   [
    ""
   ],
   false,
   [
    "diffusers",
    "pillow",
    "transformers",
    "psutil",
    "pyyaml",
    "packaging",
    "huggingface_hub",
    "sympy",
    "networkx",
    "fsspec",
    "filelock",
    "setuptools",
    "mpmath",
    "jinja2",
    "typing-extensions",
    "numpy",
    "safetensors"
   ]
  ],
  [
   "base",
   "123",
   "accelerate",
   ".",
   [
    ""
   ],
   true,
   [
    "accelerate"
   ]
  ],
  [
   "base",
   "123",
   "torch",
   ".",
   [
    ""
   ],
   true,
   [
    "torch"
   ]
  ]
 ],
 "checks": [
  [
   "1234",
   [
    "llama-cpp-python",
    "gguf",
    "numpy",
    "safetensors",
    "onnx",
    "onnxruntime",
    "transformers",
    "jinja2",
    "diskcache",
    "typing-extensions"
   ]
  ],
  [
   "123",
   [
    "torch",
    "transformers",
    "accelerate",
    "diffusers",
    "pillow"
   ]
  ]
 ],
 "images": [
  [
   "base",
   "12",
   "ollama/ollama:latest",
   "linux/arm64",
   "."
  ],
  [
   "base",
   "124",
   "ghcr.io/open-webui/open-webui:main",
   "linux/arm64",
   "."
  ],
  [
   "base",
   "12",
   "koboldai/koboldcpp:latest",
   "linux/arm64",
   "."
  ],
  [
   "base",
   "12",
   "ghcr.io/ggml-org/llama.cpp:server",
   "linux/arm64",
   "."
  ]
 ],
 "ollama": [
  [
   "base",
   "12",
   "qwen2.5:1.5b"
  ],
  [
   "base",
   "2",
   "qwen3:1.7b"
  ]
 ],
 "pack_dirs": [
  "Lab01",
  "Lab02",
  "Lab03",
  "Lab04",
  "Lab05",
  "prefetch",
  "Memes"
 ],
 "pack_skip_files": [
  "BONUS-LABS-PASSWORD.md",
  "INSTRUCTOR-GUIDE-Lab05.md",
  "TODO.md",
  "InstructorNotes.md",
  "deck-source.zip",
  "compose.yaml.new"
 ],
 "pack_skip_dirs": [
  ".venv",
  "__pycache__",
  ".git",
  "Lab01/models",
  "Lab01/kobold",
  "Lab01/prefetch",
  "Lab01/logs",
  "logs",
  "results"
 ],
 "pack_skip_ext": [
  ".gguf",
  ".part",
  ".zip"
 ]
}''')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE) if ROOT_UP else HERE
UA = {"User-Agent": "bsides-workshop-fetch/2.0"}
FAILS = []
A = None


def say(*x):
    print(*x, flush=True)


def want(group, labs):
    return any(c in LABS for c in labs) and (group == "base" or (group == "optional" and A.optional)
                                              or (group == "gpu" and A.gpu and OS_NAME != "MacOS"))


def default_dest():
    parent = os.path.dirname(ROOT)
    return parent if os.path.basename(parent) == OS_NAME else os.path.join(ROOT, "Downloads", OS_NAME)


def human(n):
    return f"{n / 1048576:.0f} MB" if n < 1 << 30 else f"{n / (1 << 30):.1f} GB"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def get(rel, url, sha=None):
    """Download one file, unless it is present. Resumes a partial (.part) file."""
    dest = os.path.join(A.dest, rel)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        say(f"  present  {rel}"); return True
    if A.dry_run:
        say(f"  MISSING  {rel}"); return True
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    part = dest + ".part"
    for attempt in range(1, 4):
        try:
            have = os.path.getsize(part) if os.path.exists(part) else 0
            hdr = dict(UA, **({"Range": f"bytes={have}-"} if have else {}))
            with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
                with open(part, "ab" if have and r.status == 206 else "wb") as f:
                    shutil.copyfileobj(r, f, 1 << 20)
            if sha and sha256(part) != sha:
                os.remove(part)
                raise IOError("the sha256 checksum does not match; the file was deleted")
            os.replace(part, dest)
            say(f"  got      {rel} ({human(os.path.getsize(dest))})")
            return True
        except Exception as e:
            if getattr(e, "code", None) == 416 and os.path.exists(part):  # the partial file is already complete
                os.replace(part, dest); say(f"  got      {rel}"); return True
            say(f"  retry {attempt}: {rel}: {e}")
    FAILS.append(rel); say(f"  FAILED   {rel}")
    return False


def get_index(labs_rel_pat):
    page, pat = labs_rel_pat
    rx = re.compile(pat)
    have = [f for f in (os.listdir(A.dest) if os.path.isdir(A.dest) else []) if rx.fullmatch(f)]
    if have:
        say(f"  present  {have[0]}"); return
    if A.dry_run:
        say(f"  MISSING  {pat} (newest from {page})"); return
    try:
        with urllib.request.urlopen(urllib.request.Request(page, headers=UA), timeout=60) as r:
            names = set(rx.findall(r.read().decode("utf-8", "replace")))
        ver = max(names, key=lambda v: [int(x) for x in v.split(".")])
    except Exception as e:
        FAILS.append(page); say(f"  FAILED   {page}: {e}"); return
    name = pat.replace(r"([0-9]+\.[0-9]+\.[0-9]+)", ver).replace("\\", "")
    get(name, page + name)


def pip_base():
    cmd = [sys.executable, "-c", PIP_SHIM, PIP_ENV, "install", "--dry-run", "--ignore-installed", "--quiet", "--disable-pip-version-check",
           "--only-binary=:all:", "--python-version", "3.12", "--implementation", "cp", "--abi", "cp312"]
    for p in M["platform"]:
        cmd += ["--platform", p]
    return cmd


def resolve(name, indexes, no_deps, pkgs, cache):
    """Ask pip for the exact files of this package set (only the metadata, not the files)."""
    for idx in indexes:
        tmp = tempfile.mkdtemp()
        try:
            rep = os.path.join(tmp, "report.json")
            cmd = pip_base() + ["--target", os.path.join(tmp, "t"), "--report", rep] + (["--no-deps"] if no_deps else []) \
                + (["--index-url", idx] if idx else []) + pkgs
            if subprocess.run(cmd).returncode == 0:
                rows = []
                for it in json.load(open(rep, encoding="utf-8"))["install"]:
                    d = it["download_info"]
                    fn = urllib.parse.unquote(d["url"].split("/")[-1].split("#")[0])
                    rows.append("\t".join([fn, d["url"], (d.get("archive_info", {}).get("hashes") or {}).get("sha256", "")]))
                os.makedirs(os.path.dirname(cache), exist_ok=True)
                with open(cache, "w", encoding="utf-8") as f:
                    f.write("\n".join(rows) + "\n")
                return True
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    return False


def pip_set(name, folder, indexes, no_deps, pkgs):
    cache = os.path.join(A.dest, ".prefetch", f"{OS_NAME}-{name}.tsv")
    if A.refresh or not os.path.exists(cache):
        if A.dry_run:
            say(f"  MISSING  Python package set '{name}' (the list comes from pip when you run without --dry-run)"); return
        say(f"  asking pip for the files of '{name}' ...")
        if not resolve(name, indexes, no_deps, pkgs, cache):
            FAILS.append(f"pip set {name}"); say(f"  FAILED   pip set {name}"); return
    for line in open(cache, encoding="utf-8").read().splitlines():
        if line.strip():
            fn, url, sha = (line.split("\t") + ["", ""])[:3]
            get(fn if folder == "." else os.path.join(folder, fn), url, sha or None)


def pip_check(pkgs):
    tmp = tempfile.mkdtemp()
    try:
        cmd = pip_base() + ["--target", os.path.join(tmp, "t"), "--no-index", "--find-links", A.dest] + pkgs
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if r.returncode == 0:
        say(f"  OK       pip finds {', '.join(pkgs[:3])}... and all their dependencies offline")
    else:
        FAILS.append("offline pip check"); say("  FAILED   offline pip check: " + " ".join(r.stdout.strip().splitlines()[-2:])[:300])


def run(cmd):
    say("   $ " + " ".join(cmd))
    return subprocess.run(cmd).returncode == 0


def docker_items():
    if not shutil.which("docker") or subprocess.run(["docker", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        missing = [i for i in M["images"] if want(i[0], i[1])]
        if missing:
            FAILS.append("docker"); say("  Docker is not installed or not running: Docker images and Ollama models skipped.")
        return
    for g, labs, img, plat, folder in M["images"]:
        if not want(g, labs):
            continue
        name = img.replace("/", "_").replace(":", "_") + "_" + plat.split("/")[1] + ".tar"
        dest = os.path.normpath(os.path.join(A.dest, folder, name))
        if os.path.exists(dest):
            say(f"  present  {name}"); continue
        if A.dry_run:
            say(f"  MISSING  {name}"); continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if not (run(["docker", "pull", "--platform", plat, img]) and run(["docker", "save", "-o", dest + ".part", img])):
            FAILS.append(name); continue
        os.replace(dest + ".part", dest)
    store = os.path.join(A.dest, "ollama")
    todo = []
    for g, labs, model in M["ollama"]:
        if not want(g, labs):
            continue
        n, _, tag = model.partition(":")
        if os.path.exists(os.path.join(store, "models", "manifests", "registry.ollama.ai", "library", n, tag or "latest")):
            say(f"  present  ollama model {model}")
        elif A.dry_run:
            say(f"  MISSING  ollama model {model}")
        else:
            todo.append(model)
    if todo:
        os.makedirs(store, exist_ok=True)
        subprocess.run(["docker", "rm", "-f", "ws-fetch-ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if run(["docker", "run", "-d", "--name", "ws-fetch-ollama", "-v", os.path.abspath(store) + ":/root/.ollama", "ollama/ollama:latest"]):
            for model in todo:  # one model at a time
                if not run(["docker", "exec", "ws-fetch-ollama", "ollama", "pull", model]):
                    FAILS.append("ollama " + model)
            subprocess.run(["docker", "exec", "ws-fetch-ollama", "chmod", "-R", "a+rwX", "/root/.ollama"])
        else:
            FAILS.append("ollama models")
        subprocess.run(["docker", "rm", "-f", "ws-fetch-ollama"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def pack():
    dest = os.path.join(A.dest, "Ai-workshop")
    if os.path.abspath(dest) == os.path.abspath(ROOT):
        say("  The lab files are already in the download folder."); return
    say(f"Lab files -> {dest}")
    if A.dry_run:
        return
    names = {d for d in M["pack_skip_dirs"] if "/" not in d}
    paths = {os.path.normpath(os.path.join(ROOT, d)) for d in M["pack_skip_dirs"] if "/" in d}
    ok = lambda f: f not in M["pack_skip_files"] and not f.endswith(tuple(M["pack_skip_ext"]))
    n = 0
    for f in os.listdir(ROOT):
        if os.path.isfile(os.path.join(ROOT, f)) and ok(f):
            os.makedirs(dest, exist_ok=True); shutil.copy2(os.path.join(ROOT, f), os.path.join(dest, f)); n += 1
    for top in M["pack_dirs"]:
        for d, dirs, fs in os.walk(os.path.join(ROOT, top)):
            dirs[:] = [x for x in dirs if x not in names and os.path.normpath(os.path.join(d, x)) not in paths]
            for f in fs:
                if ok(f):
                    t = os.path.join(dest, os.path.relpath(os.path.join(d, f), ROOT))
                    os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copy2(os.path.join(d, f), t); n += 1
    say(f"  copied {n} files")


def main():
    global A
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for o in ["--dry-run", "--optional", "--gpu", "--skip-docker", "--refresh"] + (["--pack", "--pack-only"] if len(LABS) > 1 else []):
        ap.add_argument(o, action="store_true")
    ap.add_argument("--dest")
    A = ap.parse_args()
    A.pack, A.pack_only = getattr(A, "pack", False), getattr(A, "pack_only", False)
    A.dest = os.path.abspath(A.dest or default_dest())
    say(f"Lab 3 (Integrations and Tooling), {OS_NAME}: download folder {A.dest}" + ("  (dry run)" if A.dry_run else ""))
    if A.gpu and OS_NAME == "MacOS":
        say("macOS: the normal files use the Apple GPU (Metal). --gpu adds nothing.")
    if not A.pack_only:
        say("Files (installers, programs, models):")
        for g, labs, rel, url in M["files"]:
            if want(g, labs):
                get(rel, url)
        for g, labs, page, pat in M["index_files"]:
            if want(g, labs):
                get_index((page, pat))
        say("Python packages for Python 3.12 (one file at a time):")
        for g, labs, name, folder, idx, nd, pkgs in M["pip"]:
            if want(g, labs):
                pip_set(name, folder, idx, nd, pkgs)
        if not A.skip_docker:
            say("Docker images and Ollama models:")
            docker_items()
        if not A.dry_run:
            say("Offline check of the Python packages:")
            for labs, pkgs in M["checks"]:
                if any(c in LABS for c in labs):
                    pip_check(pkgs)
    if A.pack or A.pack_only:
        pack()
    if A.dry_run:
        say("\nDry run: nothing was downloaded."); return 0
    if FAILS:
        say("\nNot complete. Failed: " + ", ".join(FAILS) + "\nRun the script again. It continues where it stopped."); return 1
    say("\nComplete. Everything for Lab 3 (Integrations and Tooling) is in " + A.dest); return 0


if __name__ == "__main__":
    sys.exit(main())
