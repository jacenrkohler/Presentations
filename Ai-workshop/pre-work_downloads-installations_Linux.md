# Pre-work downloads and installations: Linux

This guide gets a Linux laptop (Ubuntu, Debian or Fedora; others are similar) ready for Labs 1 to 4 of the BSidesDFW 2026 workshop "Under the Hood of LLMs". It also works inside WSL 2's Ubuntu on Windows. When you finish, every lab runs **offline**, except the optional parts that use cloud models. Allow one to two hours, most of it waiting for downloads (about 15 GB). Do it at home: the venue Wi-Fi will not keep up.

You need: a 64-bit distribution with a recent kernel; 16 GB of RAM; 25 GB of free disk; `sudo` rights. No GPU is required.

| Step | What |
|---|---|
| [1](#1-downloads) | Downloads (links) |
| [2](#2-install-python-and-build-tools) | Install Python and build tools |
| [3](#3-install-docker-engine) | Install Docker Engine (skip in WSL 2 with Docker Desktop) |
| [4](#4-install-vs-code-and-continue) | Install VS Code and Continue |
| [5](#5-get-the-lab-files) to [7](#7-download-the-models-and-container-images) | Lab files, Python libraries, models and images |
| [8](#8-configure-and-check) | Configure and check |
| [9](#9-test-that-it-works-offline) | Test that it works offline |
| [10](#10-troubleshooting) | Troubleshooting |

## 1. Downloads

| Software | Download | Official install guide |
|---|---|---|
| Python 3.10 or newer, `pip`, `venv` | Your distribution's packages (Step 2) | [Using Python on Unix platforms](https://docs.python.org/3/using/unix.html) |
| Build tools (`gcc`, `cmake`), only used if a package must be compiled | Your distribution's packages (Step 2) | |
| Docker Engine and the Compose plugin | Docker's own package repository (Step 3) | [Install Docker Engine](https://docs.docker.com/engine/install/) and [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) |
| VS Code (`.deb` or `.rpm`) | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on Linux](https://code.visualstudio.com/docs/setup/linux) |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue) | [Continue docs](https://docs.continue.dev) |
| NVIDIA Container Toolkit (optional, NVIDIA GPU only) | NVIDIA's repository | [Install the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) |

## 2. Install Python and build tools

**Ubuntu or Debian (and WSL 2's Ubuntu):**

```
sudo apt update
sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential cmake curl
```

**Fedora:**

```
sudo dnf install -y python3 python3-pip python3-devel gcc gcc-c++ cmake curl
```

Check it: `python3 --version` prints 3.10 or higher. (On an older distribution with Python 3.8 or 3.9, install a newer Python from your distribution's backports, or use [pyenv](https://github.com/pyenv/pyenv).)

## 3. Install Docker Engine

**In WSL 2 on Windows with Docker Desktop:** skip this step. Turn on **Settings, Resources, WSL integration** for your Ubuntu in Docker Desktop instead, then run the checks at the end of this step.

**Everywhere else:** install Docker Engine from Docker's own repository by following [Install Docker Engine](https://docs.docker.com/engine/install/) for your distribution (for example [Ubuntu](https://docs.docker.com/engine/install/ubuntu/), [Debian](https://docs.docker.com/engine/install/debian/) or [Fedora](https://docs.docker.com/engine/install/fedora/)). Install the `docker-compose-plugin` package with it. Use Docker's repository rather than the Snap package or your distribution's older `docker.io` package, so `docker compose` and the `host-gateway` setting the labs use are available.

Then configure it ([post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/)):

```
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in (or restart) so the group change takes effect. Then check:

```
docker run --rm hello-world
docker compose version
```

The first prints "Hello from Docker!" without `sudo`.

**Firewall (Labs 3 and 4).** Open WebUI runs in a container and reaches the harness on your laptop through Docker's bridge network, on ports 8000 to 8002. If you use `ufw`, allow that, and only that:

```
sudo ufw allow from 172.16.0.0/12 to any port 8000:8002 proto tcp
```

(With `firewalld`, add the Docker interface to a trusted zone or open those ports to the Docker network only.)

## 4. Install VS Code and Continue

1. Install VS Code by following [VS Code on Linux](https://code.visualstudio.com/docs/setup/linux) for your distribution (it adds Microsoft's repository so VS Code stays updated), or install the `.deb` or `.rpm` from Section 1: `sudo apt install ./code_*.deb` or `sudo dnf install ./code-*.rpm`.
2. Open VS Code, open **Extensions** (Ctrl+Shift+X), search for **Continue** (publisher: Continue), and install it.

In WSL 2, install VS Code in Windows instead (see the Windows guide) and open your WSL folders with the **WSL** extension ([VS Code: Developing in WSL](https://code.visualstudio.com/docs/remote/wsl)).
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
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
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

On Linux, `llama-cpp-python` usually installs from a ready-made package. If pip compiles it instead, the build tools from Step 2 let it succeed; it can take 10 minutes or more.

**GPU option.** See "Optional: use a GPU" in `lab1/README.md` (Setup) for CUDA (NVIDIA) and Vulkan (AMD or Intel) builds of `llama-cpp-python` and the CUDA build of `torch`. For the GPU Docker profiles in Lab 1 Part 4, install the NVIDIA Container Toolkit (Section 1).

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
| `permission denied` on `/var/run/docker.sock` | Run `sudo usermod -aG docker $USER`, then log out and back in |
| `docker compose` is not a command | Install the `docker-compose-plugin` package from Docker's repository (Step 3) |
| `error: externally-managed-environment` from pip | You are outside the virtual environment: run `source .venv/bin/activate` in the `lab1` folder |
| Open WebUI cannot reach the harness (Labs 3 and 4) | Start the harness with `--host 0.0.0.0` (or `--host 172.17.0.1` for a cloud model), and check the firewall rule in Step 3 |
| A download stops or fails | Run `python3 prefetch_all.py` again; it resumes |
| Out of memory while a model loads | Stop containers you are not using (`docker compose --profile NAME down`) and close the browser tabs you do not need |
