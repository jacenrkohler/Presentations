# Pre-work: downloads and installations (Windows)

This guide prepares your computer for Labs 1 to 4 of the BSidesDFW 2026 workshop *Under the Hood of AI: Run, Measure, Secure, and Break Them*. After you complete it, Labs 1 to 4 operate **offline**. Only the optional parts with cloud models need the internet.

Do this guide at home. It takes one to two hours. Most of this time is for downloads (approximately 15 GB). The Wi-Fi at the workshop is not sufficient for these downloads.

You need:

- Windows 10 (22H2) or Windows 11, 64-bit
- 16 GB of RAM
- 25 GB of free disk space
- Administrator rights

A GPU is not necessary. All commands are for a computer without a GPU. Section 7 gives the GPU options.

Use PowerShell for all commands. Use `py -3` where other guides use `python3`.

**Lab walkthroughs for Windows.** Use the online walkthrough if you download the files at home. Use the offline walkthrough if you use a USB drive or the pre-fetch scripts (section 8).

| Lab | Walkthrough | Offline walkthrough |
|---|---|---|
| Lab 1: Run a Model in a Harness | [LAB01_Windows_Run_a_Model_in_a_Harness.md](Lab01/LAB01_Windows_Run_a_Model_in_a_Harness.md) | [LAB01_Windows_Run_a_Model_in_a_Harness_OFFLINE.md](Lab01/LAB01_Windows_Run_a_Model_in_a_Harness_OFFLINE.md) |
| Lab 2: Benchmarking Models and Harnesses | [LAB02_Windows_Benchmarking_Models_and_Harnesses.md](Lab02/LAB02_Windows_Benchmarking_Models_and_Harnesses.md) | [LAB02_Windows_Benchmarking_Models_and_Harnesses_OFFLINE.md](Lab02/LAB02_Windows_Benchmarking_Models_and_Harnesses_OFFLINE.md) |
| Lab 3: Integrations and Tooling | [LAB03_Windows_Integrations_and_Tooling.md](Lab03/LAB03_Windows_Integrations_and_Tooling.md) | [LAB03_Windows_Integrations_and_Tooling_OFFLINE.md](Lab03/LAB03_Windows_Integrations_and_Tooling_OFFLINE.md) |
| Lab 4: Logging and Compliance | [LAB04_Windows_Logging_and_Compliance.md](Lab04/LAB04_Windows_Logging_and_Compliance.md) | [LAB04_Windows_Logging_and_Compliance_OFFLINE.md](Lab04/LAB04_Windows_Logging_and_Compliance_OFFLINE.md) |
| Lab 5: Surprise Bonus Lab | [LAB05_Windows_Surprise_Bonus_Lab.md](Lab05/LAB05_Windows_Surprise_Bonus_Lab.md) | [LAB05_Windows_Surprise_Bonus_Lab_OFFLINE.md](Lab05/LAB05_Windows_Surprise_Bonus_Lab_OFFLINE.md) |

| Section | Contents |
|---|---|
| 1 | Download links |
| 2 | Turn on virtualization and install WSL 2 |
| 3 | Install Python |
| 4 | Install Docker, VS Code and Continue |
| 5 | Get the lab files |
| 6 | Install the Python packages |
| 7 | GPU software (optional) |
| 8 | Download the models and the Docker images |
| 8a | Download each item directly (without a script) |
| 9 | Configure and make sure that the setup is correct |
| 10 | Make sure that the labs operate offline |
| 11 | Problems and solutions |

## 1. Download links

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| WSL 2 (Windows Subsystem for Linux) | Part of Windows: `wsl --install` in PowerShell as Administrator | [Microsoft: Install WSL](https://learn.microsoft.com/windows/wsl/install) | Turn on virtualization (Intel VT-x or AMD-V) in the BIOS or UEFI settings. Docker uses up to half of the RAM through WSL 2. To change this value, see [WSL configuration](https://learn.microsoft.com/windows/wsl/wsl-config) |
| Python 3.10 or newer (64-bit) | [python.org/downloads/windows](https://www.python.org/downloads/windows/) | [Using Python on Windows](https://docs.python.org/3/using/windows.html) | On the first screen of the installer, select **Add python.exe to PATH**. Then do this command one time: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Docker Desktop | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | [Install Docker Desktop on Windows](https://docs.docker.com/desktop/setup/install/windows-install/) | Select **Use WSL 2 instead of Hyper-V**. A Docker account is not necessary |
| VS Code | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on Windows](https://code.visualstudio.com/docs/setup/windows) | On the **Additional tasks** screen, select **Add to PATH** |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue), or `py -3 prefetch_lab3.py` | [Continue documentation](https://docs.continue.dev/) | Lab 3, Part 1b |
| Windows Terminal (recommended) | [Microsoft Store: Windows Terminal](https://aka.ms/terminal) | [Windows Terminal](https://learn.microsoft.com/windows/terminal/) | Use the PowerShell profile |

Optional software for the optional parts of Labs 1 to 4:

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Obsidian (optional, Lab 3, Part 2) | [obsidian.md/download](https://obsidian.md/download) | [Obsidian Help](https://help.obsidian.md/) | Make a vault with the name `AI Vault` in your `Documents` folder |
| Node.js 22 or newer (optional, for the CLIs and MCP) | [nodejs.org/en/download](https://nodejs.org/en/download) | [nodejs.org/en/download](https://nodejs.org/en/download) | None. To examine the version, do `node --version` |
| Build Tools for Visual Studio (only if `llama-cpp-python` does not install in Section 6) | [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) | [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) | Select the **Desktop development with C++** workload |

## 2. Turn on virtualization and install WSL 2

Docker Desktop uses WSL 2 to operate Linux containers. WSL 2 is a small virtual machine in Windows.

1. Open Task Manager (Ctrl+Shift+Esc). Go to **Performance, CPU**. Make sure that it shows **Virtualization: Enabled**.
2. If it shows **Disabled**, restart the computer and open the BIOS or UEFI settings. Turn on Intel VT-x (Intel Virtualization Technology) or AMD-V (SVM Mode). The support website of the manufacturer of your computer shows how.
3. Open PowerShell as Administrator (right-click, **Run as administrator**). Do this command:

   ```
   wsl --install
   ```

4. Restart the computer when Windows tells you to. After the restart, Ubuntu asks for a Linux user name and a password. Make them and record them. If WSL was already installed, do `wsl --update`.
5. Do `wsl --status`. Make sure that the default version is 2.
6. Optional: WSL 2 uses up to half of the RAM. To set a limit, make the file `<HOME_DIR>\.wslconfig` with this text:

   ```
   [wsl2]
   memory=8GB
   ```

   Then do `wsl --shutdown`. See [WSL configuration](https://learn.microsoft.com/windows/wsl/wsl-config).

## 3. Install Python

1. Start the Python installer from Section 1. On the first screen, select **Add python.exe to PATH**. Click **Install Now**. If the installer shows **Disable path length limit**, click it.
2. Open a new PowerShell window. Do `py -3 --version`. Make sure that it shows 3.10 or newer.
3. Let PowerShell start the activation script of the virtual environment. Do this command one time:

   ```
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```

## 4. Install Docker, VS Code and Continue

**Docker**

1. Start the Docker Desktop installer. Make sure that **Use WSL 2 instead of Hyper-V** is selected.
2. Restart the computer if Windows tells you to. Start Docker Desktop and accept the terms. A Docker account is not necessary.
3. In **Settings, General**, make sure that **Use the WSL 2 based engine** is selected.

Do these commands. The first command shows "Hello from Docker!". The second command shows a version.

```
docker run --rm hello-world
docker compose version
```

**VS Code and Continue**

1. Install VS Code from Section 1. On the **Additional tasks** screen, select **Add to PATH**.
2. Open VS Code. Open **Extensions** (Ctrl+Shift+X). Search for **Continue** (publisher: Continue). Install it.

## 5. Get the lab files

1. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop).
2. Extract it. Use the `Ai-workshop` folder.
3. Put the folder in a location that has no spaces in its path, for example `<HOME_DIR>\ai-workshop`. Do not put it in OneDrive or in other synchronized folders.
4. Make sure that you have these folders. Keep them together. The labs use files from `Lab01`.

| Folder | Contents |
|---|---|
| `Lab01` to `Lab05` | The lab instructions. Each folder has one file for each operating system. Use the files with `Windows` in the name. Some folders also contain lab files (the next rows) |
| `Lab01` (also) | `harness.py`, `inspect_model.py`, `compose.yaml` and the Python requirements. The models go into `Lab01/models` |
| `Lab02` (also) | `bench.py` and the benchmark prompts |
| `Lab04` (also) | `syslog_listen.py` |
| `prefetch` | The download scripts |

## 6. Install the Python packages

In PowerShell, go to the `Lab01` folder. Do these commands:

```
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt
py -3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
py -3 -m pip install -r requirements-hf.txt
```

If `llama-cpp-python` does not install (pip starts to compile it and fails), continue without it. You can do most of Lab 1 with the safetensors model, the ONNX model and Ollama. To compile it, install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the **Desktop development with C++** workload. Then do the `requirements.txt` command again.

Activate the virtual environment again in each new PowerShell window. The prompt shows `(.venv)` when it is active.

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
py -3 -c "import llama_cpp, gguf, onnxruntime, transformers, torch; print('ok')"
```

## 7. GPU software (optional)

Do this step only if your computer has a GPU. Do it before the workshop, because some builds take 10 minutes or more.

1. For GGUF models (`llama-cpp-python`):

   | GPU | Command (it replaces the CPU build) |
   |---|---|
   | NVIDIA (CUDA 12 driver) | `py -3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124` |
   | AMD or Intel (Vulkan, builds from source) | `$env:CMAKE_ARGS="-DGGML_VULKAN=on"; py -3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` |

   The source build needs Build Tools for Visual Studio with the "Desktop development with C++" workload. Use the `cu` number that agrees with your driver (`nvidia-smi` shows it).

2. For safetensors models and image models (`torch`): NVIDIA: `py -3 -m pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu124`.
3. For ONNX models (`onnxruntime`): NVIDIA: `py -3 -m pip uninstall -y onnxruntime`, then `py -3 -m pip install onnxruntime-gpu`. Any DirectX 12 GPU: `py -3 -m pip uninstall -y onnxruntime`, then `py -3 -m pip install onnxruntime-directml`.
4. For the Docker runtimes: NVIDIA only. Docker Desktop gives the GPU to containers through WSL 2. Use a current NVIDIA driver. See [Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/).

GPU software instructions: [llama-cpp-python](https://github.com/abetlen/llama-cpp-python#installation), [PyTorch](https://pytorch.org/get-started/locally/), [ONNX Runtime](https://onnxruntime.ai/docs/install/), [NVIDIA drivers](https://www.nvidia.com/en-us/drivers/).

If a GPU installation fails, install the CPU build again:

```
py -3 -m pip install --force-reinstall -r requirements.txt
```

## 8. Download the models and the Docker images

**To work without the internet at the workshop (optional).** The scripts `LAB1-4_Windows_pre-fetch.sh`, `LAB1-4_Windows_pre-fetch.ps1` and `LAB1-4_Windows_pre-fetch.py` in the `Ai-workshop` folder download every file for Labs 1 to 4: installers, Python packages, models, Docker images and Ollama models. The files go into the folder `Downloads/Windows` in the `Ai-workshop` folder. Files that are already there are skipped, so you can run a script again after an interruption. Start Docker Desktop. Then, in PowerShell, in the `Ai-workshop` folder, do one of these commands:

```
powershell -ExecutionPolicy Bypass -File .\LAB1-4_Windows_pre-fetch.ps1
py -3 LAB1-4_Windows_pre-fetch.py
```

At the workshop, use the `..._OFFLINE.md` walkthrough in each lab folder. To see what is missing first, add `--dry-run`. For the optional files (image models and Ministral 3), add `--optional`. For the NVIDIA GPU files, add `--gpu`. Each lab folder also has pre-fetch scripts for that lab only.

Or do the steps by hand:

1. Start Docker Desktop.
2. In the `prefetch` folder, with the virtual environment active, do this command:

   ```
   py -3 prefetch_all.py
   ```

   It downloads all of the items in the tables below (approximately 15 GB) into the `Lab01` folder and into Docker. If it stops, do the command again. It continues from the last file. To see the sizes first, add `--dry-run`. To operate it in the background, add `--background`. To see the progress, do `py -3 ai_prefetch.py --status --watch`.

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
| Image models for Lab 1, Part 2c: [google/vit-base-patch16-224](https://huggingface.co/google/vit-base-patch16-224) and [stabilityai/sd-turbo](https://huggingface.co/stabilityai/sd-turbo) | `py -3 prefetch_lab1images.py` | 3 GB |
| Ministral 3 for Lab 1, Part 1e, and Lab 2, Part 2f: [unsloth/Ministral-3-3B-Instruct-2512-GGUF](https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF) | `py -3 prefetch_lab1ministral.py` | 3.2 GB |

## 8a. Download each item directly (without a script)

Use this section if you do not want to use a script, or if a script fails. Each item has a link and a command. Do the commands in the `Ai-workshop` folder. The commands use `curl.exe` (it is part of Windows 10 and 11; do not use `curl` in Windows PowerShell 5.1, because it is a different command). The `-L` option follows redirects. `--create-dirs` makes the folders. If a download stops, add `-C -` and do the command again: it continues the file.

**Installers and programs.** Save the installers in a folder of your choice. The KoboldCpp program goes into `Lab01/kobold`.

| File | Link | Command | Labs |
|---|---|---|---|
| `python-3.12.10-amd64.exe` | [Download](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe) | `curl.exe -L --create-dirs -o "python-3.12.10-amd64.exe" "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"` | 1 to 4 |
| `wsl.3.0.3.0.x64.msi` | [Download](https://github.com/microsoft/WSL/releases/download/3.0.3/wsl.3.0.3.0.x64.msi) | `curl.exe -L --create-dirs -o "wsl.3.0.3.0.x64.msi" "https://github.com/microsoft/WSL/releases/download/3.0.3/wsl.3.0.3.0.x64.msi"` | 1, 2, 4 |
| `Docker Desktop Installer.exe` | [Download](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe) | `curl.exe -L --create-dirs -o "Docker Desktop Installer.exe" "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"` | 1, 2, 4 |
| `VSCodeUserSetup-x64.exe` | [Download](https://update.code.visualstudio.com/latest/win32-x64-user/stable) | `curl.exe -L --create-dirs -o "VSCodeUserSetup-x64.exe" "https://update.code.visualstudio.com/latest/win32-x64-user/stable"` | 3 |
| `continue-win32-x64-1.3.40.vsix` | [Download](https://github.com/continuedev/continue/releases/download/v1.3.40-vscode/continue-win32-x64-1.3.40.vsix) | `curl.exe -L --create-dirs -o "continue-win32-x64-1.3.40.vsix" "https://github.com/continuedev/continue/releases/download/v1.3.40-vscode/continue-win32-x64-1.3.40.vsix"` | 3 |
| `Obsidian-1.15.0.exe` | [Download](https://github.com/obsidianmd/obsidian-releases/releases/download/v1.15.0/Obsidian-1.15.0.exe) | `curl.exe -L --create-dirs -o "Obsidian-1.15.0.exe" "https://github.com/obsidianmd/obsidian-releases/releases/download/v1.15.0/Obsidian-1.15.0.exe"` | 3 |
| `koboldcpp-nocuda.exe` | [Download](https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp-nocuda.exe) | `curl.exe -L --create-dirs -o "Lab01/kobold/koboldcpp-nocuda.exe" "https://github.com/LostRuins/koboldcpp/releases/download/v1.124.2/koboldcpp-nocuda.exe"` | 1 |

You can also install WSL with `wsl --install` in PowerShell as Administrator. That command downloads WSL from the internet.

**Python packages.** Section 6 gives the `pip install` commands. pip downloads each package from [PyPI](https://pypi.org/) and PyTorch from PyPI. The prebuilt `llama-cpp-python` file for Windows is also on [GitHub](https://github.com/abetlen/llama-cpp-python/releases/tag/v0.3.36):

```
curl.exe -L -O "https://github.com/abetlen/llama-cpp-python/releases/download/v0.3.36/llama_cpp_python-0.3.36-py3-none-win_amd64.whl"
```

Then install that file with `pip install` and the file name, before `pip install -r requirements.txt`.

**Models.** The files go into `Lab01/models`. The safetensors and ONNX models are folders: download all files of each folder. The model pages are [Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF), [ggml-org/Qwen3-4B-GGUF](https://huggingface.co/ggml-org/Qwen3-4B-GGUF), [Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) and [onnx-community/Qwen2.5-0.5B-Instruct](https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct).

```
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf" "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf"
curl.exe -L --create-dirs -o "Lab01/models/Qwen3-4B-Q4_K_M.gguf" "https://huggingface.co/ggml-org/Qwen3-4B-GGUF/resolve/main/Qwen3-4B-Q4_K_M.gguf"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct/config.json" "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct/generation_config.json" "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct/tokenizer.json" "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct/tokenizer_config.json" "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct/model.safetensors" "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/resolve/main/model.safetensors"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct-onnx/config.json" "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct-onnx/generation_config.json" "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/generation_config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct-onnx/tokenizer.json" "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct-onnx/tokenizer_config.json" "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/tokenizer_config.json"
curl.exe -L --create-dirs -o "Lab01/models/qwen2.5-0.5b-instruct-onnx/onnx/model_quantized.onnx" "https://huggingface.co/onnx-community/Qwen2.5-0.5B-Instruct/resolve/main/onnx/model_quantized.onnx"
```

**Docker images.** Start Docker Desktop first.

```
docker pull ollama/ollama:latest
docker pull ghcr.io/open-webui/open-webui:main
docker pull koboldai/koboldcpp:latest
docker pull ghcr.io/ggml-org/llama.cpp:server
```

**Models in Ollama.** In the `Lab01` folder, start Ollama, download the two models, then stop Ollama:

```
docker compose --profile ollama up -d
docker compose exec ollama ollama pull qwen2.5:1.5b
docker compose exec ollama ollama pull qwen3:1.7b
docker compose --profile ollama down
```

**Optional models** (Lab 1 Part 1e and Part 2c, Lab 2 Part 2f):

```
curl.exe -L --create-dirs -o "Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf" "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf"
curl.exe -L --create-dirs -o "Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf" "https://huggingface.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF/resolve/main/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf"
curl.exe -L --create-dirs -o "Lab01/models/vit-base-patch16-224/config.json" "https://huggingface.co/google/vit-base-patch16-224/resolve/main/config.json"
curl.exe -L --create-dirs -o "Lab01/models/vit-base-patch16-224/preprocessor_config.json" "https://huggingface.co/google/vit-base-patch16-224/resolve/main/preprocessor_config.json"
curl.exe -L --create-dirs -o "Lab01/models/vit-base-patch16-224/model.safetensors" "https://huggingface.co/google/vit-base-patch16-224/resolve/main/model.safetensors"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/model_index.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/model_index.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/scheduler/scheduler_config.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/scheduler/scheduler_config.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/text_encoder/config.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/config.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/text_encoder/model.fp16.safetensors" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/text_encoder/model.fp16.safetensors"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/tokenizer/merges.txt" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/merges.txt"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/tokenizer/special_tokens_map.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/special_tokens_map.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/tokenizer/tokenizer_config.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/tokenizer_config.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/tokenizer/vocab.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/tokenizer/vocab.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/unet/config.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/config.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/unet/diffusion_pytorch_model.fp16.safetensors" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/unet/diffusion_pytorch_model.fp16.safetensors"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/vae/config.json" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/config.json"
curl.exe -L --create-dirs -o "Lab01/models/sd-turbo/vae/diffusion_pytorch_model.fp16.safetensors" "https://huggingface.co/stabilityai/sd-turbo/resolve/main/vae/diffusion_pytorch_model.fp16.safetensors"
```

## 9. Configure and make sure that the setup is correct

Do these steps one time, in the `Lab01` folder, with the virtual environment active. Some steps also download items that need the internet. Do them before you go offline.

1. **The harness.** Do `py -3 harness.py ask --backend echo "hello"`. It shows `(echo) You said: hello`.
2. **The three model formats.** Do these commands. Each `ask` command gives an answer in one or two minutes on the CPU of a laptop.

   ```
   py -3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
   py -3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."
   py -3 harness.py ask --model models/qwen2.5-0.5b-instruct "Say hello in five words."
   py -3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx "Say hello in five words."
   ```

3. **Ollama and your Open WebUI admin account** (Labs 1 and 4):
   1. Do `docker compose --profile ollama up -d`.
   2. Do `docker compose exec ollama ollama list`. It shows `qwen2.5:1.5b` and `qwen3:1.7b`.
   3. Open http://localhost:3000. The first start can take some minutes. Make the first account with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. This account is the local admin. It stays in the container on your computer.
   4. Select `qwen2.5:1.5b` and send "hello".
4. **The benchmark** (Lab 2). Keep Ollama on. In the `Lab02` folder, do `py -3 bench.py run --only math --target ollama:qwen2.5:1.5b --no-warmup`. It shows one PASS or FAIL row. Then, in the `Lab01` folder, do `docker compose --profile ollama down`.
5. **The harness server** (Labs 3 and 4). Do `py -3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370`. Open http://localhost:13370/v1/models. It shows one model. Push Ctrl-C.
6. **VS Code and Continue** (Lab 3). Open VS Code. Click the Continue icon in the side bar. Close the sign-in prompt. A Continue account is not necessary for local models. Continue makes its configuration file `<HOME_DIR>\.continue\config.yaml`.
7. **The syslog listener** (Lab 4). In the `Lab04` folder, do `py -3 syslog_listen.py`. It shows that it listens on port 13379. Push Ctrl-C.
8. **The log folder** (Lab 4). Do `py -3 harness.py ask --backend echo --log-dir ../logs "test"`. It makes the folder `logs` with one `.log` file.
9. **The firewall** (Lab 4). Open WebUI in Docker connects to the harness on your computer. The first time that you start `harness.py serve` with `--host 0.0.0.0`, Windows Defender Firewall asks about Python. Allow it on **Private networks** only.

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

If a check fails offline, the software tries to download an item. Do `py -3 prefetch_all.py` again while you are online. If the problem continues, send the error to the Discord forum channel.

These items need the internet after the setup: the cloud models, the official AI CLIs and desktop apps, the Surprise Bonus Lab, Security Onion, and new installations.

## 11. Problems and solutions

| Problem | Solution |
|---|---|
| `py` is not recognized | Install Python again with **Add python.exe to PATH** selected. Open a new PowerShell window |
| `.venv\Scripts\Activate.ps1 cannot be loaded` | Do `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` one time |
| Docker Desktop: "WSL 2 installation is incomplete" or "Virtualization not enabled" | Do `wsl --update` as Administrator. Turn on virtualization in the BIOS (Section 2) |
| `docker` operates only as Administrator | Sign out and sign in again. Make sure that your account is in the `docker-users` group ([Docker documentation](https://docs.docker.com/desktop/setup/install/windows-install/)) |
| `llama-cpp-python` does not install | Install Build Tools for Visual Studio (Section 1). Then do the `requirements.txt` command again. Or use the Linux guide in WSL Ubuntu |
| Open WebUI cannot connect to the harness (Lab 4) | Start the harness with `--host 0.0.0.0`. Allow Python through the firewall on Private networks |
| Path or permission errors | Do not put the lab folder in OneDrive. Use a path that has no spaces |
| A download stops or fails | Do `py -3 prefetch_all.py` again. It continues from the last file |

### Placeholders

Some commands contain placeholders. Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |

