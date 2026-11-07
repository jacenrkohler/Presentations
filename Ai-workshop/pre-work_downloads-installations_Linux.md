# Pre-work: downloads and installations (Linux)

This guide prepares your computer for Labs 1 to 4 of the BSidesDFW 2026 workshop *Under the Hood of AI: Run, Measure, Secure, and Break Them*. After you complete it, Labs 1 to 4 operate **offline**. Only the optional parts with cloud models need the internet.

Do this guide at home. It takes one to two hours. Most of this time is for downloads (approximately 15 GB). The Wi-Fi at the workshop is not sufficient for these downloads.

You need:

- A recent 64-bit distribution (Ubuntu, Debian or Fedora)
- 16 GB of RAM
- 25 GB of free disk space
- Administrator rights

A GPU is not necessary. All commands are for a computer without a GPU. Section 7 gives the GPU options.

Use terminal for all commands.

| Section | Contents |
|---|---|
| 1 | Download links |
| 2 | Prepare Docker |
| 3 | Install Python |
| 4 | Install Docker, VS Code and Continue |
| 5 | Get the lab files |
| 6 | Install the Python packages |
| 7 | GPU software (optional) |
| 8 | Download the models and the Docker images |
| 9 | Configure and make sure that the setup is correct |
| 10 | Make sure that the labs operate offline |
| 11 | Problems and solutions |

## 1. Download links

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Python 3.10 or newer, pip and venv | Your package manager: `sudo apt install python3 python3-pip python3-venv` (Ubuntu, Debian) or `sudo dnf install python3 python3-pip` (Fedora) | [Using Python on Unix platforms](https://docs.python.org/3/using/unix.html) | None |
| Docker Engine and the Compose plugin | [Install Docker Engine](https://docs.docker.com/engine/install/) (select your distribution) | [Install Docker Engine](https://docs.docker.com/engine/install/) | Do `sudo usermod -aG docker $USER`, then sign out and sign in. See [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) |
| VS Code | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on Linux](https://code.visualstudio.com/docs/setup/linux) | None |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue), or `python3 prefetch_lab3.py` | [Continue documentation](https://docs.continue.dev/) | Lab 3, Part 1b |

Optional software for the optional parts of Labs 1 to 4:

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Obsidian (optional, Lab 3, Part 2) | [obsidian.md/download](https://obsidian.md/download) | [Obsidian Help](https://help.obsidian.md/) | Make a vault with the name `AI Vault` in your `Documents` folder |
| Node.js 22 or newer (optional, for the CLIs and MCP) | [nodejs.org/en/download](https://nodejs.org/en/download) | [nodejs.org/en/download](https://nodejs.org/en/download) | None. To examine the version, do `node --version` |

## 2. Prepare Docker

1. Install Docker Engine and the Compose plugin for your distribution. Use [Install Docker Engine](https://docs.docker.com/engine/install/).
2. Let your user operate Docker without `sudo`:

   ```
   sudo usermod -aG docker $USER
   ```

3. Sign out and sign in again. See [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/).

## 3. Install Python

1. Ubuntu or Debian: `sudo apt update && sudo apt install python3 python3-pip python3-venv`. Fedora: `sudo dnf install python3 python3-pip`.
2. Do `python3 --version`. Make sure that it shows 3.10 or newer.

## 4. Install Docker, VS Code and Continue

**Docker**

1. You installed Docker in Section 2.

Do these commands. The first command shows "Hello from Docker!". The second command shows a version.

```
docker run --rm hello-world
docker compose version
```

**VS Code and Continue**

1. Install VS Code from Section 1. None.
2. Open VS Code. Open **Extensions** (Ctrl+Shift+X). Search for **Continue** (publisher: Continue). Install it.

## 5. Get the lab files

1. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop).
2. Extract it. Use the `Ai-workshop` folder.
3. Put the folder in a location that has no spaces in its path, for example `<HOME_DIR>/ai-workshop`.
4. Make sure that you have these folders. Keep them together. The labs use files from `Lab01`.

| Folder | Contents |
|---|---|
| `Lab01` to `Lab05` | The lab instructions. Each folder has one file for each operating system. Use the files with `Linux` in the name. Some folders also contain lab files (the next rows) |
| `Lab01` (also) | `harness.py`, `inspect_model.py`, `compose.yaml` and the Python requirements. The models go into `Lab01/models` |
| `Lab02` (also) | `bench.py` and the benchmark prompts |
| `Lab04` (also) | `syslog_listen.py` |
| `prefetch` | The download scripts |

## 6. Install the Python packages

In terminal, go to the `Lab01` folder. Do these commands:

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
python3 -m pip install -r requirements-hf.txt
```

If `llama-cpp-python` does not install (pip starts to compile it and fails), continue without it. You can do most of Lab 1 with the safetensors model, the ONNX model and Ollama.

Activate the virtual environment again in each new terminal window. The prompt shows `(.venv)` when it is active.

| Package | Function | Labs |
|---|---|---|
| `llama-cpp-python` | Operates GGUF models in the harness (llama.cpp) | 1 to 4 |
| `gguf` | Reads GGUF files for `inspect_model.py` | 1 |
| `numpy` | Numbers and arrays | 1 to 4 |
| `safetensors` | Reads safetensors files | 1 |
| `onnx`, `onnxruntime` | Read and operate ONNX models | 1, 2 |
| `transformers`, `jinja2` | Tokenizers and chat templates. Operates safetensors models | 1, 2 |
| `torch` (CPU build) | Operates safetensors models and image models | 1, 2 |
| `accelerate`, `diffusers`, `pillow` | Image models (optional, Lab 1, Part 2c) | 1 |

Python contains all other modules that the labs use. To make sure that the installation is correct, do this command. It shows `ok`:

```
python3 -c "import llama_cpp, gguf, onnxruntime, transformers, torch; print('ok')"
```

## 7. GPU software (optional)

Do this step only if your computer has a GPU. Do it before the workshop, because some builds take 10 minutes or more.

1. For GGUF models (`llama-cpp-python`):

   | GPU | Command (it replaces the CPU build) |
   |---|---|
   | NVIDIA (CUDA 12 driver) | `python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124` |
   | AMD or Intel (Vulkan, builds from source) | `CMAKE_ARGS="-DGGML_VULKAN=on" python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` |

   The source build needs the build tools and the Vulkan development files of your distribution. Use the `cu` number that agrees with your driver (`nvidia-smi` shows it).

2. For safetensors models and image models (`torch`): NVIDIA: `python3 -m pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu124`.
3. For ONNX models (`onnxruntime`): NVIDIA: `python3 -m pip uninstall -y onnxruntime`, then `python3 -m pip install onnxruntime-gpu`.
4. For the Docker runtimes: NVIDIA only. Install the NVIDIA Container Toolkit first (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

GPU software instructions: [llama-cpp-python](https://github.com/abetlen/llama-cpp-python#installation), [PyTorch](https://pytorch.org/get-started/locally/), [ONNX Runtime](https://onnxruntime.ai/docs/install/), [NVIDIA drivers](https://www.nvidia.com/en-us/drivers/).

If a GPU installation fails, install the CPU build again:

```
python3 -m pip install --force-reinstall -r requirements.txt
```

## 8. Download the models and the Docker images

**To work without the internet at the workshop (optional).** The scripts `LAB1-4_Linux_pre-fetch.sh`, `LAB1-4_Linux_pre-fetch.ps1` and `LAB1-4_Linux_pre-fetch.py` in the `Ai-workshop` folder download every file for Labs 1 to 4: installers, Python packages, models, Docker images and Ollama models. The files go into the folder `Downloads/Linux` in the `Ai-workshop` folder. Files that are already there are skipped, so you can run a script again after an interruption. Start Docker. Then, in terminal, in the `Ai-workshop` folder, do one of these commands:

```
bash LAB1-4_Linux_pre-fetch.sh
python3 LAB1-4_Linux_pre-fetch.py
```

At the workshop, use the `..._OFFLINE.md` walkthrough in each lab folder. To see what is missing first, add `--dry-run`. For the optional files (image models and Ministral 3), add `--optional`. For the NVIDIA GPU files, add `--gpu`. Each lab folder also has pre-fetch scripts for that lab only.

Or do the steps by hand:

1. Start Docker.
2. In the `prefetch` folder, with the virtual environment active, do this command:

   ```
   python3 prefetch_all.py
   ```

   It downloads all of the items in the tables below (approximately 15 GB) into the `Lab01` folder and into Docker. If it stops, do the command again. It continues from the last file. To see the sizes first, add `--dry-run`. To operate it in the background, add `--background`. To see the progress, do `python3 ai_prefetch.py --status --watch`.

3. When it is complete, go to the `Lab01` folder and do `docker compose --profile ollama down`.

**Model files** (in `Lab01/models/`):

| File or folder | Format | Size | Source | Labs |
|---|---|---|---|---|
| `qwen2.5-1.5b-instruct-q4_k_m.gguf` | GGUF, 4-bit | 1.1 GB | [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF) | 1 to 4 |
| `qwen2.5-0.5b-instruct/` | safetensors, 16-bit | 1.0 GB | [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) | 1 to 3 |
| `qwen2.5-0.5b-instruct-onnx/` | ONNX, 8-bit | 0.6 GB | [onnx-community/Qwen2.5-0.5B-Instruct](https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct) | 1 to 3 |
| `Qwen3-4B-Q4_K_M.gguf` | GGUF, 4-bit | 2.5 GB | [ggml-org/Qwen3-4B-GGUF](https://huggingface.co/ggml-org/Qwen3-4B-GGUF) | 1 to 4 |

These four models have the Apache 2.0 license. A Hugging Face account is not necessary.

**Docker images:**

| Image | Size | Page | Labs |
|---|---|---|---|
| `ollama/ollama:latest` | 1.8 GB | [Docker Hub](https://hub.docker.com/r/ollama/ollama) | 1, 2 |
| `ghcr.io/open-webui/open-webui:main` | 3.5 GB | [Open WebUI documentation](https://docs.openwebui.com/) | 1, 4 |
| `koboldai/koboldcpp:latest` | 1.5 GB | [Docker Hub](https://hub.docker.com/r/koboldai/koboldcpp) | 1 (Part 4b, optional) |
| `ghcr.io/ggml-org/llama.cpp:server` | 0.3 GB | [llama.cpp Docker documentation](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md) | 1 (Part 4c, optional) |

**Models in Ollama** (in the Docker volume `lab01_ollama-data`):

| Model | Size | Page | Labs |
|---|---|---|---|
| `qwen2.5:1.5b` | 1.0 GB | [ollama.com/library/qwen2.5](https://ollama.com/library/qwen2.5) | 1, 2 |
| `qwen3:1.7b` | 1.4 GB | [ollama.com/library/qwen3](https://ollama.com/library/qwen3) | 2 |

**Optional files** (only for the optional parts):

| Item | Command in the `prefetch` folder | Size |
|---|---|---|
| Image models for Lab 1, Part 2c: [google/vit-base-patch16-224](https://huggingface.co/google/vit-base-patch16-224) and [stabilityai/sd-turbo](https://huggingface.co/stabilityai/sd-turbo) | `python3 prefetch_lab1images.py` | 3 GB |
| Ministral 3 for Lab 1, Part 1e, and Lab 2, Part 2f: [unsloth/Ministral-3-3B-Instruct-2512-GGUF](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF) | `python3 prefetch_lab1ministral.py` | 3.2 GB |

## 9. Configure and make sure that the setup is correct

Do these steps one time, in the `Lab01` folder, with the virtual environment active. Some steps also download items that need the internet. Do them before you go offline.

1. **The harness.** Do `python3 harness.py ask --backend echo "hello"`. It shows `(echo) You said: hello`.
2. **The three model formats.** Do these commands. Each `ask` command gives an answer in one or two minutes on the CPU of a laptop.

   ```
   python3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
   python3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."
   python3 harness.py ask --model models/qwen2.5-0.5b-instruct "Say hello in five words."
   python3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx "Say hello in five words."
   ```

3. **Ollama and your Open WebUI admin account** (Labs 1 and 4):
   1. Do `docker compose --profile ollama up -d`.
   2. Do `docker compose exec ollama ollama list`. It shows `qwen2.5:1.5b` and `qwen3:1.7b`.
   3. Open http://localhost:3000. The first start can take some minutes. Make the first account with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. This account is the local admin. It stays in the container on your computer.
   4. Select `qwen2.5:1.5b` and send "hello".
4. **The benchmark** (Lab 2). Keep Ollama on. In the `Lab02` folder, do `python3 bench.py run --only math --target ollama:qwen2.5:1.5b --no-warmup`. It shows one PASS or FAIL row. Then, in the `Lab01` folder, do `docker compose --profile ollama down`.
5. **The harness server** (Labs 3 and 4). Do `python3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370`. Open http://localhost:13370/v1/models. It shows one model. Push Ctrl-C.
6. **VS Code and Continue** (Lab 3). Open VS Code. Click the Continue icon in the side bar. Close the sign-in prompt. A Continue account is not necessary for local models. Continue makes its configuration file `<HOME_DIR>/.continue/config.yaml`.
7. **The syslog listener** (Lab 4). In the `Lab04` folder, do `python3 syslog_listen.py`. It shows that it listens on port 13379. Push Ctrl-C.
8. **The log folder** (Lab 4). Do `python3 harness.py ask --backend echo --log-dir ../logs "test"`. It makes the folder `logs` with one `.log` file.
9. **The firewall** (Lab 4). Open WebUI in Docker connects to the harness on your computer. If you use `ufw`, allow the ports of the harness from the Docker networks only:

   ```
   sudo ufw allow from 172.16.0.0/12 to any port 13370:13375 proto tcp
   ```

   With `firewalld`, add the Docker interface to a trusted zone. See [Docker and ufw](https://docs.docker.com/engine/network/packet-filtering-firewalls/).

**Ports that the labs use.** Docker publishes its ports on `127.0.0.1` only.

| Port | Service | Lab |
|---|---|---|
| 3000 | Open WebUI | 1, 4 |
| 11434 | Ollama | 1, 2 |
| 5001 | KoboldCpp (optional) | 1 (Part 4b) |
| 8080 | llama.cpp server (optional) | 1 (Part 4c) |
| 13370, 13371 | `harness.py serve` | 3, 4 |
| 13372 to 13375 | `harness.py serve` with a cloud model (optional) | 4 (Parts 3b to 3e) |
| 13379 | `syslog_listen.py` | 4 |

## 10. Make sure that the labs operate offline

Labs 1 to 4 operate on your computer. Only the optional cloud models and the optional Security Onion server (Lab 4) need a network.

1. Turn off Wi-Fi. Disconnect the network cable.
2. Do checks 1 to 5 and 7 in Section 9 again.
3. Turn on Wi-Fi again.

If a check fails offline, the software tries to download an item. Do `python3 prefetch_all.py` again while you are online. If the problem continues, send the error to the Discord forum channel.

These items need the internet after the setup: the cloud models, the official AI CLIs and desktop apps, the Surprise Bonus Lab, Security Onion, and new installations.

## 11. Problems and solutions

| Problem | Solution |
|---|---|
| `permission denied` for `docker` | Do `sudo usermod -aG docker $USER`. Sign out and sign in again |
| `docker compose` is not found | Install the Compose plugin (`docker-compose-plugin`) from the Docker repository |
| `llama-cpp-python` starts to compile and fails | Install the build tools: `sudo apt install build-essential cmake` (Ubuntu, Debian) or `sudo dnf install gcc-c++ cmake` (Fedora). Then do the `requirements.txt` command again |
| Open WebUI cannot connect to the harness (Lab 4) | Start the harness with `--host 0.0.0.0` (or `--host <DOCKER_BRIDGE_IP>` for a cloud model). Make sure that the firewall rule in Section 9 is correct |
| A download stops or fails | Do `python3 prefetch_all.py` again. It continues from the last file |

### Placeholders

Some commands contain placeholders. Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `/home/jsmith` |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |
| `<DOCKER_BRIDGE_IP>` | The IP address of the Docker bridge (`docker0`) on your computer |

