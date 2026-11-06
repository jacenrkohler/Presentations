# Pre-work downloads and installations: macOS

This guide gets a Mac ready for Labs 1 to 4 of the BSidesDFW 2026 workshop "Under the Hood of LLMs". When you finish, every lab runs **offline**, except the optional parts that use cloud models. Allow one to two hours, most of it waiting for downloads (about 15 GB). Do it at home: the venue Wi-Fi will not keep up.

You need: a recent macOS on an Apple Silicon (M1 or newer) or Intel Mac; 16 GB of RAM; 25 GB of free disk; an admin account. No separate GPU is required; Apple Silicon's GPU is used automatically where it helps.

Run commands in the **Terminal** app (Applications, Utilities, Terminal).

| Step | What |
|---|---|
| [1](#1-downloads) | Downloads (links) |
| [2](#2-install-the-command-line-tools-and-python) | Install the command line tools and Python |
| [3](#3-install-docker-desktop) | Install Docker Desktop |
| [4](#4-install-vs-code-and-continue) | Install VS Code and Continue |
| [5](#5-get-the-lab-files) to [7](#7-download-the-models-and-container-images) | Lab files, Python libraries, models and images |
| [8](#8-configure-and-check) | Configure and check |
| [9](#9-test-that-it-works-offline) | Test that it works offline |
| [10](#10-troubleshooting) | Troubleshooting |

## 1. Downloads

| Software | Download | Official install guide |
|---|---|---|
| Xcode Command Line Tools (compilers, needed by some Python packages) | Built into macOS: `xcode-select --install` (Step 2) | [Apple: Command Line Tools](https://developer.apple.com/xcode/resources/) |
| Python 3.10 or newer (3.12 recommended) | [python.org/downloads/macos](https://www.python.org/downloads/macos/) (universal installer) | [Using Python on macOS](https://docs.python.org/3/using/mac.html) |
| Docker Desktop (choose Apple silicon or Intel) | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/) |
| VS Code | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on macOS](https://code.visualstudio.com/docs/setup/mac) |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) | [Continue docs](https://docs.continue.dev) |
| Homebrew (optional package manager) | [brew.sh](https://brew.sh) | [Homebrew installation](https://docs.brew.sh/Installation) |

## 2. Install the command line tools and Python

1. Install Apple's command line tools (compilers some Python packages need):

   ```
   xcode-select --install
   ```

   Click **Install** in the window that opens. If it says they are already installed, you are done.
2. Run the Python installer from Section 1.
3. When it finishes, open **Applications, Python 3.x** and double-click **Install Certificates.command**. This lets Python verify secure websites; without it, the download script fails with certificate errors.
4. Check it in a new Terminal window: `python3 --version` prints 3.10 or higher.

(Homebrew users can run `brew install python@3.12` instead of steps 2 and 3.)

## 3. Install Docker Desktop

1. Open the `.dmg` for your chip (Apple silicon or Intel) and drag Docker to Applications.
2. Start Docker from Applications, accept the terms, and allow the helper it asks to install. You can skip signing in; no Docker account is needed for these labs.
3. Configure it (gear icon, **Settings, Resources**): give it at least **8 GB of memory** and 4 CPUs, then **Apply and restart**.
4. Check it:

   ```
   docker run --rm hello-world
   docker compose version
   ```

   The first prints "Hello from Docker!".

Docker on a Mac cannot use the GPU, so containers run on the CPU. The harness itself (outside Docker) can use Apple Silicon's GPU; see the GPU note in Step 6.

## 4. Install VS Code and Continue

1. Open the VS Code download (a `.zip`) and drag **Visual Studio Code** to Applications.
2. Open VS Code, open the Command Palette (Cmd+Shift+P), and run **Shell Command: Install 'code' command in PATH**.
3. Open **Extensions** (Cmd+Shift+X), search for **Continue** (publisher: Continue), and install it.

**macOS firewall.** In Labs 3 and 4 the harness listens for Open WebUI on port 8000. If macOS asks whether Python may accept incoming connections, click **Allow**.
## 5. Get the lab files

1. Download the handout: **[add the link]**.
2. Unzip it into a folder with no spaces in its path, for example `~/ai-workshop`.
3. Check that you have these folders: `lab1`, `lab2`, `lab4`, `labs`, `homework`, `prefetch`. Keep them together; later labs use files from `lab1`.

## 6. Install the Python libraries

In a terminal, go to the `lab1` folder and make a virtual environment, so these packages stay separate from the rest of your system:

```
python3 -m venv .venv
source .venv/bin/activate
```

Activate it again (the second line) in every new terminal you use for the labs. Your prompt shows `(.venv)` when it is active. Then install:

```
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install torch
python3 -m pip install -r requirements-hf.txt
```

What gets installed:

| Package | What it does | Used in |
|---|---|---|
| `llama-cpp-python` | Runs GGUF models inside the harness (llama.cpp) | Labs 1 to 4 |
| `gguf` | Reads GGUF files for the model inspector | Lab 1 |
| `numpy` | Numbers and arrays | All labs |
| `safetensors` | Reads safetensors model files | Lab 1 |
| `onnx` | Reads ONNX model files for the inspector | Lab 1 |
| `onnxruntime` | Runs ONNX models | Labs 1 and 2 |
| `transformers` | Tokenizers and chat templates; runs safetensors models | Labs 1 and 2 |
| `jinja2` | Chat templates | Labs 1 and 2 |
| `torch` (CPU build) | Runs safetensors and image models | Labs 1 and 2 |
| `accelerate` | Helps transformers load models | Lab 1 |
| `diffusers` | Image generation (optional Part 2c) | Lab 1 |
| `pillow` | Images (optional Part 2c) | Lab 1 |

Everything else the labs use (`csv`, `json`, `socket`, `http.server`, and so on) comes with Python. The lab files `harness.py`, `inspect_model.py`, `bench.py` and `syslog_listen.py` need no other packages.

Check it: `python3 -c "import llama_cpp, gguf, onnxruntime, transformers, torch; print('ok')"` prints `ok`.

On Apple Silicon, `llama-cpp-python` and `torch` use the Mac's GPU (Metal) automatically when you add `--gpu-layers -1` to harness commands. See "Optional: use a GPU" in `lab1/README.md` (Setup) for the Metal build of `llama-cpp-python`.

**If `llama-cpp-python` will not install** (most often on Intel Macs, where pip compiles it): make sure Step 2's command line tools are installed and try again. If it still fails, carry on: you can do most of Lab 1 with the safetensors and ONNX models and with Ollama, and pair up with a neighbor for the GGUF steps.

## 7. Download the models and container images

Start Docker first. Then, in a terminal in the `prefetch` folder (with the virtual environment active):

```
python3 prefetch_all.py
```

It downloads everything below, about 15 GB, into the `lab1` folder and into Docker. Run it again if it stops: finished items are skipped and partial downloads resume. `--dry-run` shows the sizes first; `--background` runs it hidden, and `python3 ai_prefetch.py --status --watch` shows progress.

### Models and container images

`prefetch_all.py` downloads all of these. The links are here so you know exactly what you are getting, and so you can download a file by hand if the script fails (put it at the path shown, inside the `lab1` folder).

**Model files** (saved in `lab1/models/`):

| File or folder | Format | Size | Source | Used in |
|---|---|---|---|---|
| `qwen2.5-1.5b-instruct-q4_k_m.gguf` | GGUF, 4-bit | about 1.1 GB | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | Labs 1 to 4 |
| `qwen2.5-0.5b-instruct/` (config, tokenizer, `model.safetensors`) | safetensors, 16-bit | about 1.0 GB | [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) | Labs 1 to 3 |
| `qwen2.5-0.5b-instruct-onnx/` (config, tokenizer, `onnx/model_quantized.onnx`) | ONNX, 8-bit | about 0.6 GB | [onnx-community/Qwen2.5-0.5B-Instruct](https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct) | Labs 1 to 3 |
| `Qwen3-4B-Q4_K_M.gguf` | GGUF, 4-bit | about 2.5 GB | [ggml-org/Qwen3-4B-GGUF](https://huggingface.co/ggml-org/Qwen3-4B-GGUF) | Labs 1 to 4 |

All four are Apache-2.0 licensed and need no Hugging Face account.

**Docker images:**

| Image | Size | Page | Used in |
|---|---|---|---|
| `ollama/ollama:latest` | about 1.8 GB | [Docker Hub](https://hub.docker.com/r/ollama/ollama) | Labs 1 and 2 |
| `ghcr.io/open-webui/open-webui:main` | about 3.5 GB | [GitHub](https://github.com/open-webui/open-webui) | Labs 1, 3 and 4 |
| `koboldai/koboldcpp:latest` | about 1.5 GB | [Docker Hub](https://hub.docker.com/r/koboldai/koboldcpp) | Lab 1 Part 4b (optional) |
| `ghcr.io/ggml-org/llama.cpp:server` | about 0.3 GB | [GitHub](https://github.com/ggml-org/llama.cpp) | Lab 1 Part 4c (optional) |

**Models inside Ollama** (stored in the Docker volume `lab1_ollama-data`):

| Model | Size | Page | Used in |
|---|---|---|---|
| `qwen2.5:1.5b` | about 1.0 GB | [ollama.com/library/qwen2.5](https://ollama.com/library/qwen2.5) | Labs 1 and 2 |
| `qwen3:1.7b` | about 1.4 GB | [ollama.com/library/qwen3](https://ollama.com/library/qwen3) | Lab 2 |

**Optional extras** (only for optional parts; download them now if you want them offline):

| What | Command (in the `prefetch` folder) | Size |
|---|---|---|
| Image models for Lab 1, Part 2c: [google/vit-base-patch16-224](https://huggingface.co/google/vit-base-patch16-224) and [stabilityai/sd-turbo](https://huggingface.co/stabilityai/sd-turbo) (non-commercial and small-business license) | `python3 prefetch_lab1images.py` | about 3 GB |
| Ministral 3 at about 1 GB for Lab 1 Part 1e and Lab 2 Part 2f: [unsloth/Ministral-3-3B-Instruct-2512-GGUF](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF) | `python3 prefetch_lab1ministral.py` | about 3.2 GB |
| Obsidian, for Lab 3 Part 2 | [obsidian.md/download](https://obsidian.md/download) | about 0.3 GB |

When it finishes, stop the Ollama container it started: in the `lab1` folder, `docker compose --profile ollama down`.

## 8. Configure and check

Run these once, in a terminal in the `lab1` folder with the virtual environment active. Several of them also finish first-time setup that needs the internet, so do them before you go offline.

1. **The harness:** `python3 harness.py ask --backend echo "hello"` prints `(echo) You said: hello`.
2. **The three model formats:**

   ```
   python3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
   python3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."
   python3 harness.py ask --model models/qwen2.5-0.5b-instruct "Say hello in five words."
   python3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx "Say hello in five words."
   ```

   Each `ask` should answer within a minute or two on a laptop CPU.
3. **Ollama and Open WebUI (Labs 1, 3 and 4):**
   1. `docker compose --profile ollama up -d`
   2. `docker compose exec ollama ollama list` shows `qwen2.5:1.5b` and `qwen3:1.7b`.
   3. Open http://localhost:3000. The first start can take a few minutes. Create the first account: it becomes the **local admin**, stored only inside the container. Use any email and a password you will remember.
   4. Choose `qwen2.5:1.5b` and say hello.
   5. `docker compose --profile ollama down`
4. **The benchmark (Lab 2):** start Ollama again (`docker compose --profile ollama up -d`), then in the `lab2` folder: `python3 bench.py run --only math --target ollama:qwen2.5:1.5b --no-warmup`. You should see one PASS or FAIL row. Then stop Ollama.
5. **VS Code and Continue (Lab 3):** open VS Code, click the Continue icon in the side bar, and close any sign-in prompt (you do not need a Continue account for local models). Continue creates its settings file; you will add the harness to it in Lab 3.
6. **The syslog listener (Lab 4):** in the `lab4` folder, `python3 syslog_listen.py` says it is listening on port 5514. Stop it with Ctrl-C.
7. **The log folder (Lab 4):** `python3 harness.py ask --backend echo --log-dir ../logs "test"` creates a `logs` folder with one `.log` file in it.

## 9. Test that it works offline

Everything in Labs 1 to 4 runs on your laptop, except the optional parts that use cloud models (Anthropic, OpenAI, Gemini, Copilot) and the optional Security Onion server in Lab 4. To prove it before the workshop:

1. Turn off Wi-Fi (and unplug any network cable).
2. Repeat checks 1 to 4 and 6 in Section 8.
3. Turn Wi-Fi back on.

If anything fails offline, it is still trying to download something: run `python3 prefetch_all.py` again while online, and post the error in the Discord forum channel.

Things that need the internet even after setup: the cloud models, the official AI CLIs and desktop apps, Lakera's website, Security Onion (if your instructor runs one on the network), and installing anything new.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `CERTIFICATE_VERIFY_FAILED` while downloading | Run **Install Certificates.command** from the Python folder in Applications (Step 2) |
| `xcrun: error: invalid active developer path` | Run `xcode-select --install` |
| Docker is slow or a model is killed | Give Docker more memory (Step 3), and stop containers you are not using |
| Open WebUI cannot reach the harness (Labs 3 and 4) | Start the harness with `--host 0.0.0.0`, and allow Python's incoming connections when macOS asks |
| A download stops or fails | Run `python3 prefetch_all.py` again; it resumes |
| `code` command not found | Run **Shell Command: Install 'code' command in PATH** in VS Code (Step 4) |
