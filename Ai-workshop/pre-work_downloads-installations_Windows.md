# Pre-work downloads and installations: Windows

This guide gets a Windows 10 or 11 laptop ready for Labs 1 to 4 of the BSidesDFW 2026 workshop "Under the Hood of LLMs". When you finish, every lab runs **offline**, except the optional parts that use cloud models. Allow one to two hours, most of it waiting for downloads (about 15 GB). Do it at home: the venue Wi-Fi will not keep up.

You need: Windows 10 (22H2) or Windows 11, 64-bit; 16 GB of RAM; 25 GB of free disk; admin rights. No GPU is required.

Run every command in **PowerShell** (or Windows Terminal) unless a step says otherwise. Use `py -3` where other guides say `python3`.

| Step | What |
|---|---|
| [1](#1-downloads) | Downloads (links) |
| [2](#2-turn-on-virtualization-and-install-wsl-2) | Turn on virtualization and install WSL 2 |
| [3](#3-install-python-and-the-build-tools) | Install Python (and, only if needed, build tools) |
| [4](#4-install-docker-desktop-vs-code-and-continue) | Install Docker Desktop, VS Code and Continue |
| [5](#5-get-the-lab-files) to [7](#7-download-the-models-and-container-images) | Lab files, Python libraries, models and images |
| [8](#8-configure-and-check) | Configure and check |
| [9](#9-test-that-it-works-offline) | Test that it works offline |
| [10](#10-troubleshooting) | Troubleshooting |

## 1. Downloads

| Software | Download | Official install guide |
|---|---|---|
| WSL 2 (Windows Subsystem for Linux) | Built into Windows: `wsl --install` (Step 2) | [Microsoft: Install WSL](https://learn.microsoft.com/windows/wsl/install) |
| Python 3.10 or newer (3.12 recommended) | [python.org/downloads/windows](https://www.python.org/downloads/windows/) (64-bit installer) | [Using Python on Windows](https://docs.python.org/3/using/windows.html) |
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/) and [Docker Desktop WSL 2 backend](https://docs.docker.com/desktop/features/wsl/) |
| VS Code | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on Windows](https://code.visualstudio.com/docs/setup/windows) |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) | [Continue docs](https://docs.continue.dev) |
| Windows Terminal (recommended) | [Microsoft Store: Windows Terminal](https://aka.ms/terminal) | [Windows Terminal docs](https://learn.microsoft.com/windows/terminal/) |
| Build Tools for Visual Studio (only if Step 6 fails to install `llama-cpp-python`) | [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) | Choose the "Desktop development with C++" workload |

## 2. Turn on virtualization and install WSL 2

Docker Desktop runs Linux containers inside WSL 2, a lightweight virtual machine built into Windows.

1. **Check virtualization.** Open Task Manager (Ctrl+Shift+Esc), go to **Performance, CPU**, and look for **Virtualization: Enabled**. If it says Disabled, restart into your BIOS or UEFI settings and turn on Intel VT-x (or Intel Virtualization Technology) or AMD-V (SVM Mode). Your laptop maker's support site shows how.
2. **Install WSL 2.** Open PowerShell **as Administrator** (right-click, Run as administrator) and run:

   ```
   wsl --install
   ```

   Restart when it asks. After the restart, an Ubuntu window opens and asks you to create a Linux username and password: choose any, and remember them. (If WSL was already installed, run `wsl --update` instead.)
3. **Check it:**

   ```
   wsl --status
   wsl --version
   ```

   `wsl --status` should say the default version is 2.
4. **Optional: limit WSL's memory.** By default WSL 2 can use up to half your RAM, which suits a 16 GB laptop. To set it yourself, create the file `%UserProfile%\.wslconfig` (for example with `notepad $env:USERPROFILE\.wslconfig`) containing:

   ```
   [wsl2]
   memory=8GB
   ```

   Then run `wsl --shutdown`. See [Microsoft: WSL configuration](https://learn.microsoft.com/windows/wsl/wsl-config).

**Two ways to run the labs on Windows.** This guide runs Python in Windows itself and Docker through WSL 2. That is the simplest path. If `llama-cpp-python` will not install in Windows (Step 6), you can instead run the labs inside the Ubuntu you just installed: open Ubuntu from the Start menu, follow the **Linux** guide (`pre-work_downloads-installations_Linux.md`) from its Python step onward, and skip its Docker install (Docker Desktop provides Docker to Ubuntu once you turn on WSL integration in Step 4).

## 3. Install Python (and the build tools only if needed)

1. Run the Python installer from Section 1. On the first screen, tick **Add python.exe to PATH**, then choose **Install Now**. At the end, if offered, choose **Disable path length limit**.
2. Open a **new** PowerShell window and check: `py -3 --version` prints 3.10 or higher.
3. Allow PowerShell to run the virtual-environment activation script (once):

   ```
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

Build Tools for Visual Studio are only needed if Step 6 cannot find a ready-made `llama-cpp-python` package and starts compiling. Skip them for now.

## 4. Install Docker Desktop, VS Code and Continue

**Docker Desktop**

1. Run the Docker Desktop installer. Keep **Use WSL 2 instead of Hyper-V** ticked.
2. Restart if asked, then start Docker Desktop and accept the terms. You can skip signing in; no Docker account is needed for these labs.
3. Configure it (gear icon, **Settings**):
   - **General:** tick **Use the WSL 2 based engine**.
   - **Resources, WSL integration:** turn on integration with **Ubuntu** (needed only if you run the labs inside Ubuntu).
4. Check it in PowerShell:

   ```
   docker run --rm hello-world
   docker compose version
   ```

   The first prints "Hello from Docker!".

**VS Code and Continue**

1. Run the VS Code installer. On the "Additional tasks" screen, tick **Add to PATH**.
2. Open VS Code, open **Extensions** (Ctrl+Shift+X), search for **Continue** (publisher: Continue), and install it.

**Windows Defender Firewall.** In Labs 3 and 4 the harness listens for Open WebUI on port 8000. The first time, Windows asks whether to allow Python on networks: allow it on **Private networks** only, never Public.
## 5. Get the lab files

1. Download the handout: **[add the link]**.
2. Unzip it into a folder with no spaces in its path, for example `C:\Users\YOU\ai-workshop`.
3. Check that you have these folders: `lab1`, `lab2`, `lab4`, `labs`, `homework`, `prefetch`. Keep them together; later labs use files from `lab1`.

## 6. Install the Python libraries

In a terminal, go to the `lab1` folder and make a virtual environment, so these packages stay separate from the rest of your system:

```
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
```

Activate it again (the second line) in every new terminal you use for the labs. Your prompt shows `(.venv)` when it is active. Then install:

```
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
py -3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
py -3 -m pip install -r requirements-hf.txt
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

Check it: `py -3 -c "import llama_cpp, gguf, onnxruntime, transformers, torch; print('ok')"` prints `ok`.

**If `llama-cpp-python` will not install.** On Windows, pip sometimes cannot find a ready-made package and tries to compile one, which fails without a C++ compiler. Choose one:

1. Install the Build Tools for Visual Studio (Section 1) with the **Desktop development with C++** workload, open a new PowerShell, activate the virtual environment, and run `py -3 -m pip install -r requirements.txt` again (it can take 10 minutes or more).
2. Or run the labs inside WSL's Ubuntu (see the end of Step 2) using the Linux guide.
3. Or carry on without it: you can still do most of Lab 1 with the safetensors and ONNX models and with Ollama, and pair up with a neighbor for the GGUF steps.

**GPU option (NVIDIA).** With a recent NVIDIA driver, see "Optional: use a GPU" in `lab1/README.md` (Setup) for GPU builds of `llama-cpp-python` and `torch`. Docker Desktop on Windows can also pass an NVIDIA GPU to containers through WSL 2 ([Docker: GPU support](https://docs.docker.com/desktop/features/gpu/)).

## 7. Download the models and container images

Start Docker first. Then, in a terminal in the `prefetch` folder (with the virtual environment active):

```
py -3 prefetch_all.py
```

It downloads everything below, about 15 GB, into the `lab1` folder and into Docker. Run it again if it stops: finished items are skipped and partial downloads resume. `--dry-run` shows the sizes first; `--background` runs it hidden, and `py -3 ai_prefetch.py --status --watch` shows progress.

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
| Image models for Lab 1, Part 2c: [google/vit-base-patch16-224](https://huggingface.co/google/vit-base-patch16-224) and [stabilityai/sd-turbo](https://huggingface.co/stabilityai/sd-turbo) (non-commercial and small-business license) | `py -3 prefetch_lab1images.py` | about 3 GB |
| Ministral 3 at about 1 GB for Lab 1 Part 1e and Lab 2 Part 2f: [unsloth/Ministral-3-3B-Instruct-2512-GGUF](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF) | `py -3 prefetch_lab1ministral.py` | about 3.2 GB |
| Obsidian, for Lab 3 Part 2 | [obsidian.md/download](https://obsidian.md/download) | about 0.3 GB |

When it finishes, stop the Ollama container it started: in the `lab1` folder, `docker compose --profile ollama down`.

## 8. Configure and check

Run these once, in a terminal in the `lab1` folder with the virtual environment active. Several of them also finish first-time setup that needs the internet, so do them before you go offline.

1. **The harness:** `py -3 harness.py ask --backend echo "hello"` prints `(echo) You said: hello`.
2. **The three model formats:**

   ```
   py -3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
   py -3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."
   py -3 harness.py ask --model models/qwen2.5-0.5b-instruct "Say hello in five words."
   py -3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx "Say hello in five words."
   ```

   Each `ask` should answer within a minute or two on a laptop CPU.
3. **Ollama and Open WebUI (Labs 1, 3 and 4):**
   1. `docker compose --profile ollama up -d`
   2. `docker compose exec ollama ollama list` shows `qwen2.5:1.5b` and `qwen3:1.7b`.
   3. Open http://localhost:3000. The first start can take a few minutes. Create the first account: it becomes the **local admin**, stored only inside the container. Use any email and a password you will remember.
   4. Choose `qwen2.5:1.5b` and say hello.
   5. `docker compose --profile ollama down`
4. **The benchmark (Lab 2):** start Ollama again (`docker compose --profile ollama up -d`), then in the `lab2` folder: `py -3 bench.py run --only math --target ollama:qwen2.5:1.5b --no-warmup`. You should see one PASS or FAIL row. Then stop Ollama.
5. **VS Code and Continue (Lab 3):** open VS Code, click the Continue icon in the side bar, and close any sign-in prompt (you do not need a Continue account for local models). Continue creates its settings file; you will add the harness to it in Lab 3.
6. **The syslog listener (Lab 4):** in the `lab4` folder, `py -3 syslog_listen.py` says it is listening on port 5514. Stop it with Ctrl-C.
7. **The log folder (Lab 4):** `py -3 harness.py ask --backend echo --log-dir ../logs "test"` creates a `logs` folder with one `.log` file in it.

## 9. Test that it works offline

Everything in Labs 1 to 4 runs on your laptop, except the optional parts that use cloud models (Anthropic, OpenAI, Gemini, Copilot) and the optional Security Onion server in Lab 4. To prove it before the workshop:

1. Turn off Wi-Fi (and unplug any network cable).
2. Repeat checks 1 to 4 and 6 in Section 8.
3. Turn Wi-Fi back on.

If anything fails offline, it is still trying to download something: run `py -3 prefetch_all.py` again while online, and post the error in the Discord forum channel.

Things that need the internet even after setup: the cloud models, the official AI CLIs and desktop apps, Lakera's website, Security Onion (if your instructor runs one on the network), and installing anything new.

## 10. Troubleshooting

| Problem | Fix |
|---|---|
| `py` is not recognized | Reinstall Python with **Add python.exe to PATH** ticked, then open a new PowerShell |
| `.venv\Scripts\Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| Docker Desktop: "WSL 2 installation is incomplete" or "Virtualization not enabled" | Run `wsl --update` as Administrator; turn on virtualization in the BIOS (Step 2) |
| `docker` works only as Administrator | Sign out and back in after installing Docker Desktop; make sure your account is in the `docker-users` group ([Docker docs](https://docs.docker.com/desktop/setup/install/windows-install/)) |
| Open WebUI cannot reach the harness (Labs 3 and 4) | Start the harness with `--host 0.0.0.0`, and allow Python through the firewall on Private networks |
| A download stops or fails | Run `py -3 prefetch_all.py` again; it resumes |
| Path or permission errors | Keep the lab folder out of OneDrive and other synced folders, and use a path with no spaces |
