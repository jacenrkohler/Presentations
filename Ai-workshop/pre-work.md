# Pre-work: Under the Hood of AI

BSidesDFW 2026 workshop: *Under the Hood of AI: Run, Measure, Secure, and Break Them*. Saturday, November 7, 2026, Nedderman Hall, UTA.

Do Sections 1 and 2 before the workshop. They take one to two hours. Most of this time is for downloads (approximately 15 GB). The Wi-Fi at the workshop is not sufficient for these downloads. After the setup, Labs 1 to 4 operate without an internet connection. Only their optional cloud-model parts need the internet.

## Contents

1. [Access to participate (BSidesDFW Discord)](#section-1-access-to-participate-bsidesdfw-discord)
2. [Downloads and Installs (large files)](#section-2-downloads-and-installs-large-files): all items that Labs 1 to 4 need
3. [Helpful Knowledge (YouTube Videos)](#section-3-helpful-knowledge-youtube-videos)
4. [Optional extras](#section-4-optional-extras): the optional parts of Labs 1 to 4, cloud accounts and API keys, and the official AI command-line tools and desktop apps

After Section 4: a [checklist](#checklist-before-the-workshop) and [questions](#questions).

## Lab walkthroughs

Each lab has a walkthrough for each operating system. Use the offline walkthrough if you use a USB drive or the pre-fetch scripts.

| Lab | Windows | macOS | Linux |
|---|---|---|---|
| Lab 1: Run a Model in a Harness | [Windows](Lab01/LAB01_Windows_Run_a_Model_in_a_Harness.md) ([offline](Lab01/LAB01_Windows_Run_a_Model_in_a_Harness_OFFLINE.md)) | [macOS](Lab01/LAB01_MacOS_Run_a_Model_in_a_Harness.md) ([offline](Lab01/LAB01_MacOS_Run_a_Model_in_a_Harness_OFFLINE.md)) | [Linux](Lab01/LAB01_Linux_Run_a_Model_in_a_Harness.md) ([offline](Lab01/LAB01_Linux_Run_a_Model_in_a_Harness_OFFLINE.md)) |
| Lab 2: Benchmarking Models and Harnesses | [Windows](Lab02/LAB02_Windows_Benchmarking_Models_and_Harnesses.md) ([offline](Lab02/LAB02_Windows_Benchmarking_Models_and_Harnesses_OFFLINE.md)) | [macOS](Lab02/LAB02_MacOS_Benchmarking_Models_and_Harnesses.md) ([offline](Lab02/LAB02_MacOS_Benchmarking_Models_and_Harnesses_OFFLINE.md)) | [Linux](Lab02/LAB02_Linux_Benchmarking_Models_and_Harnesses.md) ([offline](Lab02/LAB02_Linux_Benchmarking_Models_and_Harnesses_OFFLINE.md)) |
| Lab 3: Integrations and Tooling | [Windows](Lab03/LAB03_Windows_Integrations_and_Tooling.md) ([offline](Lab03/LAB03_Windows_Integrations_and_Tooling_OFFLINE.md)) | [macOS](Lab03/LAB03_MacOS_Integrations_and_Tooling.md) ([offline](Lab03/LAB03_MacOS_Integrations_and_Tooling_OFFLINE.md)) | [Linux](Lab03/LAB03_Linux_Integrations_and_Tooling.md) ([offline](Lab03/LAB03_Linux_Integrations_and_Tooling_OFFLINE.md)) |
| Lab 4: Logging and Compliance | [Windows](Lab04/LAB04_Windows_Logging_and_Compliance.md) ([offline](Lab04/LAB04_Windows_Logging_and_Compliance_OFFLINE.md)) | [macOS](Lab04/LAB04_MacOS_Logging_and_Compliance.md) ([offline](Lab04/LAB04_MacOS_Logging_and_Compliance_OFFLINE.md)) | [Linux](Lab04/LAB04_Linux_Logging_and_Compliance.md) ([offline](Lab04/LAB04_Linux_Logging_and_Compliance_OFFLINE.md)) |
| Lab 5: Surprise Bonus Lab | [Windows](Lab05/LAB05_Windows_Surprise_Bonus_Lab.md) ([offline](Lab05/LAB05_Windows_Surprise_Bonus_Lab_OFFLINE.md)) | [macOS](Lab05/LAB05_MacOS_Surprise_Bonus_Lab.md) ([offline](Lab05/LAB05_MacOS_Surprise_Bonus_Lab_OFFLINE.md)) | [Linux](Lab05/LAB05_Linux_Surprise_Bonus_Lab.md) ([offline](Lab05/LAB05_Linux_Surprise_Bonus_Lab_OFFLINE.md)) |

# Section 1: Access to participate (BSidesDFW Discord)

## 1.1 Join the Discord

Start here: https://discord.gg/faGUQTCe

1. **Accept the Code of Conduct.** In the [#code_of_conduct](https://ptb.discord.com/channels/747866151547306084/794652112851566593) channel, react with a green check mark (✅) on the post.
2. **Get the @ role.** In the [#rules_n_access_ctrl](https://ptb.discord.com/channels/747866151547306084/794697735454457887) channel, react with the cowperson emoji (🤠).
3. **Find the workshop.** Open the **#==x_BSidesDFW_2026==$** category.
   1. Use the forum channel **2026_wkshp_underhood_llm_forum** for text conversation and file sharing.
   2. Remote attendees: use the voice channel **2026_wkshp_underhood_llm_forum** for voice and screen sharing.

# Section 2: Downloads and Installs (large files)

Labs 1 to 4 need all items in this section. Do the steps in the given sequence.

Each operating system has a guide with more information, download links, installation instructions, configuration and an offline test:

- Windows (with WSL 2): [pre-work_downloads-installations_Windows.md](pre-work_downloads-installations_Windows.md)
- macOS: [pre-work_downloads-installations_MacOS.md](pre-work_downloads-installations_MacOS.md)
- Linux: [pre-work_downloads-installations_Linux.md](pre-work_downloads-installations_Linux.md)

Each lab also has a Part 0 with the setup for that lab. The lab files are in the folders `Lab01` to `Lab05`.

On Windows, use `py -3` in place of `python3` in all commands, and use PowerShell.

## 2.1 What the labs need

| Lab | Time | What you do | What the lab uses on your computer |
|---|---|---|---|
| Lab 1: Run a Model in a Harness | 25 min | Examine one model family in three formats (GGUF, safetensors, ONNX) with `inspect_model.py`. Use each model with `harness.py` and change the settings. Use a model in Ollama and Open WebUI in Docker | Python packages, three small Qwen 2.5 models (2.7 GB), Qwen3-4B (2.5 GB), the Ollama and Open WebUI Docker images, and `qwen2.5:1.5b` in Ollama |
| Lab 2: Benchmarking Models and Harnesses | 20 min | Add measurements to the harness. Benchmark the Lab 1 models and Ollama with `bench.py`: time, five token counts and correct answers | The Lab 1 models, Ollama, and `qwen3:1.7b` in Ollama (1.4 GB) |
| Lab 3: Integrations and Tooling | 20 min | Use the harness as a server for VS Code (port 13370). Connect the Continue extension. A local model writes and changes a Python program | VS Code and the Continue extension |
| Lab 4: Logging and Compliance | 15 min | Write a CSV log for each session. Send the log with syslog to a SIEM or to the practice listener (port 13379). Put Open WebUI, with users and model permissions, in front of two harness servers (ports 13370 and 13371) | Open WebUI in Docker, and your Open WebUI admin account from Section 2.7 |
| Lab 5: Surprise Bonus Lab | 10 min | No preparation | A web browser |

All labs have optional parts, for example the cloud models, the image models and the Obsidian memory. [Section 4](#section-4-optional-extras) tells you how to prepare them.

## 2.2 Make sure that your computer is applicable

| Item | Requirement |
|---|---|
| Computer | Windows, macOS or Linux. You must have administrator rights. You install Python, Docker and VS Code. |
| RAM | 16 GB. The largest model (Qwen3-4B) uses approximately 3 GB, together with Docker and Open WebUI. Close other large programs during the labs. With 8 GB, work with the person next to you. |
| Free disk space | 25 GB. The downloads are approximately 15 GB. Docker needs more space to extract images. |
| GPU | **A GPU is not necessary.** All commands in the labs are for the CPU. The workshop time is for the CPU. If you have a GPU, each lab gives a "GPU option" that makes the answers faster. The GPU software needs more setup (Section 4.1). |

| | Windows | macOS | Linux |
|---|---|---|---|
| **Best** | Windows 11, 64-bit Intel or AMD, 16 GB RAM or more | Apple silicon (M1 or newer), 16 GB RAM or more | A recent 64-bit distribution (Ubuntu, Fedora, Debian), 16 GB RAM or more |
| **Also applicable** | Windows 10 (22H2) with a current Docker Desktop | Intel Mac with 16 GB RAM (no GPU option) | A Linux virtual machine with 16 GB of RAM |
| **Docker** | Docker Desktop with WSL 2. Virtualization on in the BIOS | Docker Desktop for your chip (Apple silicon or Intel) | Docker Engine and the Compose plugin. Your user in the `docker` group |
| **Python** | Installer from python.org. Select "Add python.exe to PATH". Use `py -3` | Installer from python.org, or Homebrew. Use `python3` | `python3`, `python3-pip` and `python3-venv` from your package manager |
| **Firewall (Lab 4)** | Allow Python on **Private** networks when Windows asks | Click **Allow** when macOS asks about incoming connections | Allow TCP ports 13370 to 13375 from the Docker networks only (Section 2.7) |

Do not buy a computer for this workshop. An Apple silicon MacBook, or a 16 GB Windows or Linux laptop from the last five years, is sufficient.

## 2.3 Install the software

| Software | Windows | macOS | Linux | Labs |
|---|---|---|---|---|
| Python 3.10 or newer | [Download](https://www.python.org/downloads/windows/). [Instructions](https://docs.python.org/3/using/windows.html). Select **Add python.exe to PATH** | [Download](https://www.python.org/downloads/macos/). [Instructions](https://docs.python.org/3/using/mac.html). After the installation, start **Install Certificates.command** | `sudo apt install python3 python3-pip python3-venv` (Ubuntu, Debian) or `sudo dnf install python3 python3-pip` (Fedora). [Instructions](https://docs.python.org/3/using/unix.html) | 1 to 4 |
| WSL 2 | `wsl --install` in PowerShell as Administrator. [Instructions](https://learn.microsoft.com/windows/wsl/install) | Not applicable | Not applicable | 1, 2, 4 |
| Docker | [Docker Desktop](https://www.docker.com/products/docker-desktop/). [Instructions](https://docs.docker.com/desktop/setup/install/windows-install/). Select **Use WSL 2** | [Docker Desktop](https://www.docker.com/products/docker-desktop/). [Instructions](https://docs.docker.com/desktop/setup/install/mac-install/). Set the memory to 8 GB or more | [Docker Engine](https://docs.docker.com/engine/install/). Then do `sudo usermod -aG docker $USER` ([instructions](https://docs.docker.com/engine/install/linux-postinstall/)) | 1, 2, 4 |
| VS Code | [Download](https://code.visualstudio.com/download). [Instructions](https://code.visualstudio.com/docs/setup/windows) | [Download](https://code.visualstudio.com/download). [Instructions](https://code.visualstudio.com/docs/setup/mac). Do **Shell Command: Install 'code' command in PATH** | [Download](https://code.visualstudio.com/download). [Instructions](https://code.visualstudio.com/docs/setup/linux) | 3 |
| Continue extension | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=Continue.continue). [Documentation](https://docs.continue.dev/) | Same | Same | 3 |
| A terminal | PowerShell or [Windows Terminal](https://aka.ms/terminal) | Terminal | Your usual terminal | 1 to 4 |

To make sure that the installation is correct:

1. Open a new terminal. Do `python3 --version` (Windows: `py -3 --version`). It shows 3.10 or newer.
2. Do `docker run --rm hello-world`. It shows "Hello from Docker!".
3. Do `docker compose version`. It shows a version.
4. Docker Desktop: a Docker account is not necessary.

You use two or three terminal windows at the same time. Lab 4 uses three (two harness servers and the syslog listener).

## 2.4 Get the lab files

1. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop). On the GitHub page, the green **Code** button also has **Download ZIP**.
2. Extract the ZIP file. Use the `Ai-workshop` folder.
3. Put the folder in a location that has no spaces in its path, for example `<HOME_DIR>/ai-workshop`.
4. Make sure that you have these folders. Keep them together. The labs use files from `Lab01`.

| Folder | Contents |
|---|---|
| `Lab01` to `Lab05` | The lab instructions. Each folder has one file for each operating system, for example `LAB01_Windows_Run_a_Model_in_a_Harness.md`. Some folders also contain lab files (the next rows) |
| `Lab01` (also) | `harness.py`, `inspect_model.py`, `compose.yaml` (the Docker setup) and the Python requirements. The models go into `Lab01/models` |
| `Lab02` (also) | `bench.py`, the benchmark prompts and the context file |
| `Lab04` (also) | `syslog_listen.py`, the practice syslog listener |
| `prefetch` | The download scripts |

## 2.5 Install the Python packages

1. In a terminal, go to the `Lab01` folder.
2. Make a virtual environment. The packages then stay separate from other software on your computer:

   ```
   python3 -m venv .venv
   source .venv/bin/activate          # macOS and Linux
   .venv\Scripts\Activate.ps1         # Windows PowerShell (in place of the line above)
   ```

   The prompt shows `(.venv)` when the virtual environment is active. Activate it again in each new terminal. If Windows does not start the script, do `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` one time.

3. Install the packages:

   ```
   python3 -m pip install -r requirements.txt
   python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu     # Linux or Windows
   python3 -m pip install torch                                                     # macOS (in place of the line above)
   python3 -m pip install -r requirements-hf.txt
   ```

| File | Packages | Function |
|---|---|---|
| `requirements.txt` | `llama-cpp-python` (CPU build), `gguf`, `numpy`, `safetensors`, `onnx`, `onnxruntime`, `transformers`, `jinja2` | Read and operate the GGUF, safetensors and ONNX models (Labs 1 to 4) |
| `torch` | PyTorch, CPU build | The safetensors model and the image models |
| `requirements-hf.txt` | `transformers`, `accelerate`, `diffusers`, `pillow` | The safetensors model and the image models (Lab 1, Part 2) |

If `llama-cpp-python` does not install (pip starts to compile it and fails), continue with the other steps. You can do most of Lab 1 with the safetensors model, the ONNX model and Ollama. For the GGUF steps, work with the person next to you. Send the error to the Discord forum channel. Your guide for your operating system tells you how to install the build tools.

## 2.6 Download the models and the Docker images

1. Start Docker.
2. In a terminal, go to the `prefetch` folder. Make sure that the virtual environment is active.
3. Do this command:

   ```
   python3 prefetch_all.py
   ```

   It downloads all items that Labs 1 to 4 need, in the sequence of the labs (approximately 15 GB). It shows progress bars. If it stops, do the command again. It continues from the last file. It puts the files in the `Lab01` folder.

To operate it in the background and see the progress later:

```
python3 prefetch_all.py --background
python3 ai_prefetch.py --status --watch
```

To see the sizes first, add `--dry-run`. If you do not have much disk space, do `python3 prefetch_models.py` (model files only) now and the other items later.

| Lab | Item | Size (approximately) |
|---|---|---|
| Lab 1 | Python packages (only if Section 2.5 did not install them) | 0.5 GB |
| Lab 1 | `models/qwen2.5-1.5b-instruct-q4_k_m.gguf` (GGUF, 4-bit) | 1.1 GB |
| Lab 1 | `models/qwen2.5-0.5b-instruct/` (safetensors, 16-bit) | 1.0 GB |
| Lab 1 | `models/qwen2.5-0.5b-instruct-onnx/` (ONNX, 8-bit) | 0.6 GB |
| Lab 1 | `models/Qwen3-4B-Q4_K_M.gguf` (a reasoning model, Labs 1 to 4) | 2.5 GB |
| Lab 1 | Docker images: Ollama, Open WebUI, KoboldCpp, llama.cpp server | 7.1 GB |
| Lab 1 | `qwen2.5:1.5b` in Ollama | 1.0 GB |
| Lab 2 | `qwen3:1.7b` in Ollama | 1.4 GB |
| Lab 3 | The Continue extension, if it is not installed | 0.05 GB |
| Lab 4 | No new items. Open WebUI is from Lab 1. `syslog_listen.py` is in the lab files | 0 |

If an item fails, do the command again. If it fails again, send a message to the Discord forum channel or to `<INSTRUCTOR_EMAIL>`.

## 2.7 Configure and make sure that the setup is correct

Do these steps one time, after the downloads. Use a terminal in the `Lab01` folder, with the virtual environment active.

1. **The harness.** Do `python3 harness.py ask --backend echo "hello"`. It shows `(echo) You said: hello`.
2. **A model.** Do `python3 inspect_model.py summary models/qwen2.5-0.5b-instruct`. It shows the layers and the size of the model. Then do `python3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."`. It gives an answer in less than one minute.
3. **Your Open WebUI admin account** (Lab 1, Part 4a, and Lab 4):
   1. Do `docker compose --profile ollama up -d`.
   2. Open http://localhost:3000. Make the first account with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. This account is the local admin. It stays in the container on your computer.
   3. Select the model `qwen2.5:1.5b` and send "hello".
   4. Do `docker compose --profile ollama down`.
4. **The harness server** (Labs 3 and 4). Do `python3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370`. Open http://localhost:13370/v1/models in a browser. It shows one model. Push Ctrl-C to stop the server.
5. **VS Code** (Lab 3). Open VS Code. Click the Continue icon in the side bar one time. Continue makes its configuration file.
6. **The syslog listener** (Lab 4). In the `Lab04` folder, do `python3 syslog_listen.py`. It shows that it listens on port 13379. Push Ctrl-C.
7. **The firewall** (Lab 4). Open WebUI in Docker connects to the harness on your computer.
   - Windows: the first time that you start `harness.py serve` with `--host 0.0.0.0`, allow Python on **Private** networks only.
   - macOS: click **Allow** when macOS asks if Python can accept incoming connections.
   - Linux with `ufw`: do `sudo ufw allow from 172.16.0.0/12 to any port 13370:13375 proto tcp`. This allows the Docker networks only.
8. **Offline test.** Turn off Wi-Fi. Do step 2 again. It must operate. Turn on Wi-Fi again.

If a step fails, send the error to the Discord forum channel before the workshop.

### Ports that the labs use

| Port | Service | Lab |
|---|---|---|
| 3000 | Open WebUI | 1, 4 |
| 11434 | Ollama | 1, 2 |
| 5001 | KoboldCpp (optional) | 1 (Part 4b) |
| 8080 | llama.cpp server (optional) | 1 (Part 4c) |
| 13370, 13371 | `harness.py serve` | 3, 4 |
| 13372 to 13375 | `harness.py serve` with a cloud model (optional) | 4 (Parts 3b to 3e) |
| 13379 | `syslog_listen.py` | 4 |

Docker publishes its ports on `127.0.0.1` only. Other computers on the network cannot connect to them.

# Section 3: Helpful Knowledge (YouTube Videos)

These videos are optional, but they help.

You do not need knowledge of mathematics for the workshop. These videos give the basic ideas. They start with the simplest video. Watch the first three before the workshop. Watch the others when you have time.

**Quick primers (start here)**

1. [Neural Networks Explained in 5 Minutes](https://youtu.be/jmmW0F0biz0) (IBM Technology)
2. [Simple Neural Network in 3 Minutes](https://youtu.be/iyrmwErURJs) (3-Minute Data Science)
3. [What are Neural Networks? How AIs Think](https://youtu.be/JeVDjExBf7Y) (Code Bullet)

**3Blue1Brown, "Neural networks" playlist**

All of the playlist: https://youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi

If you watch only two: *But what is a neural network?* and *Large Language Models explained briefly*.

4. [But what is a neural network?](https://youtu.be/aircAruvnKk) (Chapter 1)
5. [Gradient descent, how neural networks learn](https://youtu.be/IHZwWFHWa-w) (Chapter 2)
6. [Backpropagation, intuitively](https://youtu.be/Ilg3gGewQ5U) (Chapter 3)
7. [Backpropagation calculus](https://youtu.be/tIeHLnjs5U8) (Chapter 4. This video has much mathematics. It is optional.)
8. [Large Language Models explained briefly](https://youtu.be/LPZh9BOjkQs)
9. [Transformers, the tech behind LLMs](https://youtu.be/wjZofJX0v4M) (Chapter 5)
10. [Attention in transformers, step-by-step](https://youtu.be/eMlx5fFNoYc) (Chapter 6)
11. [How might LLMs store facts?](https://youtu.be/9-Jl0dxWQs8) (Chapter 7)
12. [But what is cross-entropy?](https://youtu.be/GlYgs6v2YfU) (Compression is Intelligence, part 2)
13. [But how do AI images and videos actually work?](https://youtu.be/iv-5mZ_9CPY) (guest video by Welch Labs)

How the videos are related to the workshop: the neuron and the weights are in Lab 1 (you read the weights of a real model with `inspect_model.py`). Tokens and reasoning are the values that Lab 2 counts. Transformers, attention and temperature are in the "What is it?" talk.

# Section 4: Optional extras

The workshop does not need the items in this section. They prepare the optional parts of Labs 1 to 4. Do only the items for the parts that you want to do.

## 4.1 Optional lab parts

| Part | Item | Procedure |
|---|---|---|
| Lab 1, Part 2c | Image models: a recognizer (ViT, 0.35 GB) and a generator (sd-turbo, 2.6 GB) | In the `prefetch` folder, do `python3 prefetch_lab1images.py` |
| Lab 1, Part 1e; Lab 2, Part 2f | Ministral 3 (3B) at approximately 1 GB: two GGUF files and one model in Ollama (3.2 GB) | `python3 prefetch_lab1ministral.py` |
| Lab 1, Parts 4b and 4c | KoboldCpp and the llama.cpp server in Docker | `prefetch_all.py` downloads them |
| Lab 2, Part 2e, and all "GPU options" | GPU builds of `llama-cpp-python`, `torch` and `onnxruntime`. The GPU Docker profiles (NVIDIA, Linux and Windows) | Lab 1, Part 0e, in the Lab 1 file for your operating system. Do this before the workshop. Some builds take 10 minutes or more. Links: [llama-cpp-python](https://github.com/abetlen/llama-cpp-python#installation), [PyTorch](https://pytorch.org/get-started/locally/), [ONNX Runtime](https://onnxruntime.ai/docs/install/), [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html), [Docker Desktop GPU support](https://docs.docker.com/desktop/features/gpu/) |
| Lab 3, Part 1d | The other local models in VS Code | No new items. Use the Lab 1 models |
| Lab 3, Part 2 | Obsidian, a notes app. Its vault becomes the memory of the model | Install it from [obsidian.md/download](https://obsidian.md/download) ([help](https://help.obsidian.md/)). Make a vault with the name `AI Vault` in `<HOME_DIR>/Documents` |
| Lab 3, Parts 1f and 2f; Section 4.3 | Node.js 22 or newer, for the npm CLIs and the MCP filesystem server | The LTS installer from [nodejs.org/en/download](https://nodejs.org/en/download), or your package manager. To examine the version, do `node --version` |
| Lab 4, Part 2a | A real SIEM (Security Onion) | No installation. Your instructor gives you the address in the workshop. If there is no server, use the practice listener. [Security Onion documentation](https://docs.securityonion.net/) |
| Labs 1 to 4, cloud parts | API keys for Anthropic, OpenAI, Gemini and GitHub | Section 4.2 |

## 4.2 Cloud accounts and API keys

These parts use API keys: Lab 1, Part 3; Lab 2, Part 3; Lab 3, Parts 1e and 2e; Lab 4, Parts 3b to 3e. Each provider charges for its API, or limits it. This is separate from a chat subscription. The exercises of the workshop with all four providers cost a few dollars or less. Examine the current prices of each provider.

When you use a cloud model, the harness shows a numbered list of the models that your key can use. Type a number. You do not need to know the names of the models.

### Rules for each API key

1. **Make one key only for the workshop** for each provider. Give it the minimum access that the provider allows.
2. **Set a spending limit** (or buy a small prepaid credit). If the provider lets you, set an **expiry date**.
3. **Keep the key in a key file that only you can read** (see below). Keep the master copy in a password manager. Do not put a key in a command line, a script, `.bashrc` or `.profile`, a Git repository, a screenshot, a slide, Discord, or a chat with an AI model.
4. **Delete (revoke) the key after the workshop.**

**Make the key folder and a key file.** Copy the key from the page of the provider. Then:

- macOS and Linux:

  ```
  umask 077
  mkdir -p <HOME_DIR>/.config/ai-keys
  cat > <HOME_DIR>/.config/ai-keys/anthropic     # paste <ANTHROPIC_API_KEY>, push Enter, then push Ctrl-D
  ```

  With `umask 077`, only you can read the file. The harness does not use a key file that other users can read. You paste the key into `cat`, thus the shell history does not keep it.

- Windows PowerShell:

  ```
  New-Item -ItemType Directory -Force "<HOME_DIR>\.config\ai-keys" | Out-Null
  notepad "<HOME_DIR>\.config\ai-keys\anthropic.txt"          # paste <ANTHROPIC_API_KEY>, save, close
  icacls "<HOME_DIR>\.config\ai-keys" /inheritance:r /grant:r "<WINDOWS_USERNAME>:(OI)(CI)F"
  ```

  The last command removes the access of all other users to the folder. Do not put the folder in OneDrive or in other synchronized folders.

Do the same steps for `openai` (`<OPENAI_API_KEY>`), `gemini` (`<GEMINI_API_KEY>`) and `github` (`<GITHUB_TOKEN>`). In the labs, you give the file to the harness with `--key-file` (on Windows, with `.txt`). Lab 1, Part 3 examines each key with the harness command `models`.

### Anthropic (Claude)

1. Make an account at https://console.anthropic.com (the Claude Console). This account is separate from a claude.ai chat subscription.
2. In **Billing**, add a payment method and buy a small credit.
3. In **Settings, Workspaces**, make a workspace for the workshop. Set a low monthly spending limit for it.
4. In **API keys**, select **Create key**. Select the workspace. Use the name `bsides-workshop`. Copy the key. The console shows it only one time. Save it as `anthropic` in your key folder.

### OpenAI

1. Make an account at https://platform.openai.com. This account is separate from a ChatGPT subscription.
2. In **Settings, Billing**, add a payment method and a small prepaid credit. Set a budget limit.
3. Make a **project** for the workshop. In **API keys**, select **Create new secret key** for that project. If the page shows **Restricted** permissions, select them and allow only model use.
4. Copy the key. The page shows it only one time. Save it as `openai` in your key folder.

### Google Gemini

1. Sign in at https://aistudio.google.com with a Google account.
2. Select **Get API key**, then **Create API key**. A new Google Cloud project is applicable.
3. Recommended: in the Google Cloud console (https://console.cloud.google.com), go to **APIs & Services, Credentials**. Open the key and limit it to the **Generative Language API**.
4. Save the key as `gemini` in your key folder.

The free tier has rate limits. The terms of the free tier let Google use your prompts to improve its products. Read the current terms. Use test data only.

### GitHub (Copilot and GitHub Models)

GitHub Copilot does not have a public chat API. The labs use **GitHub Models** with a GitHub token. The Copilot CLI and the Copilot app use a **Copilot** plan.

1. Make an account at https://github.com, or sign in.
2. For the Copilot CLI and app (Section 4.3): turn on a Copilot plan at https://github.com/features/copilot/plans. A free plan is available.
3. For the API (the token): go to **Settings, Developer settings, Personal access tokens, Fine-grained tokens**. Select **Generate new token**.
   - Name: `bsides-workshop`. Expiration: 7 days.
   - Repository access: **Public repositories** (read-only).
   - Permissions: **Models: Read-only**. No other permissions.
4. Copy the token. Save it as `github` in your key folder.

### After the workshop

Delete (revoke) all workshop keys: Anthropic and OpenAI in **API keys**, Google in AI Studio (or in the Cloud console), and GitHub in **Fine-grained tokens**. Examine the usage page of each provider for unexpected costs. Delete the key files.

## 4.3 The official AI command-line tools (CLIs)

These parts use the CLIs: Lab 1, Part 5 (bonus, at home); Lab 2, Part 4; Lab 3, Parts 1f and 2f.

**CAUTION:** These tools are coding agents. They read files and do commands in the folder where you start them. Start them only in an empty practice folder. Keep their approval prompts on. Do not use a "skip permissions" or "yolo" mode on your computer.

| CLI | Installation (macOS, Linux) | Installation (Windows PowerShell) | Account | Sign in |
|---|---|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | `irm https://claude.ai/install.ps1 \| iex` | A Claude Pro, Max, Team or Enterprise plan, or an Anthropic Console account | Start `claude` and use the sign-in in the browser |
| OpenAI Codex | `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` (or `npm install -g @openai/codex`) | `irm https://chatgpt.com/codex/install.ps1 \| iex` | A ChatGPT Plus, Pro, Business, Edu or Enterprise plan, or an OpenAI API key | Start `codex` and select "Sign in with ChatGPT" |
| Gemini CLI | `npm install -g @google/gemini-cli` (Node.js is necessary) | Same | A paid Gemini API key, or a Gemini Code Assist Standard or Enterprise license | Start `gemini` and select a sign-in method |
| Antigravity CLI (Google's replacement for free, Google AI Pro and Google AI Ultra users) | `curl -fsSL https://antigravity.google/cli/install.sh \| bash` | `irm https://antigravity.google/cli/install.ps1 \| iex` | A Google account | Follow the instructions at the first start |
| GitHub Copilot CLI | `npm install -g @github/copilot` (Node.js 22 or newer) or `brew install --cask copilot-cli` | `winget install GitHub.Copilot` | A GitHub Copilot plan | Start `copilot`, then type `/login` |

To make sure that each CLI is installed, do `claude --version`, `codex --version`, `gemini --version` and `copilot --version`. The installation commands can change. If a command fails, use the installation page of the tool:

- Claude Code: https://code.claude.com/docs/en/setup
- Codex: https://github.com/openai/codex
- Gemini CLI: https://geminicli.com/docs/get-started (Antigravity: https://antigravity.google/download)
- Copilot CLI: https://docs.github.com/en/copilot/how-tos/copilot-cli

Make the practice folder now: `mkdir <HOME_DIR>/ai-cli-test` (Windows: `mkdir <HOME_DIR>\ai-cli-test`).

## 4.4 The official AI desktop apps (GUIs)

Lab 1, Part 6 (bonus, at home) uses these apps. Each app sends your messages to the servers of its company.

| App | Download | Operating systems | Account |
|---|---|---|---|
| Claude | https://claude.com/download | macOS, Windows (x64 and ARM64), Linux (beta: Ubuntu, Debian) | A Claude account (free or paid) |
| ChatGPT | https://openai.com/chatgpt/download/ | macOS 14 or newer on Apple silicon, and Windows. On other systems, use https://chatgpt.com | An OpenAI account (free or paid) |
| Gemini | https://gemini.google.com in Chrome or Edge. Then select "Install as app" in the browser menu | All systems with Chrome or Edge | A Google account |
| GitHub Copilot | The GitHub Copilot app (macOS on Apple silicon) from https://github.com/features/copilot, or the GitHub Copilot Chat extension in VS Code on all systems | macOS app. VS Code on all systems | A GitHub account with a Copilot plan |

After you install each app, open its settings. Find these items: if the company uses your chats for training, how long it keeps them, and how to delete them.

# Checklist before the workshop

- [ ] You joined the Discord, reacted with ✅ and 🤠, and found the forum channel of the workshop
- [ ] Python 3.10 or newer, Docker (on), VS Code and the Continue extension are installed
- [ ] The virtual environment is in `Lab01`, and the Python packages are installed (Section 2.5)
- [ ] `python3 prefetch_all.py` is complete, with no items in the "remaining" list
- [ ] The steps in Section 2.7 are correct, with your Open WebUI admin account and the offline test
- [ ] Optional: you watched the three quick-primer videos
- [ ] Your computer is charged, you have its charger, and 10 GB or more of disk space is free
- [ ] Optional: cloud API keys are in your key folder. Obsidian, Node.js, the CLIs or the apps are installed (Section 4)

# Questions

Send your questions to the 2026_wkshp_underhood_llm_forum channel in the Discord, or to `<INSTRUCTOR_EMAIL>`.

## Placeholders

Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` (Windows), `/Users/jsmith` (macOS) or `/home/jsmith` (Linux) |
| `<WINDOWS_USERNAME>` | Your Windows user name |
| `<ANTHROPIC_API_KEY>` | Your Anthropic API key |
| `<OPENAI_API_KEY>` | Your OpenAI API key |
| `<GEMINI_API_KEY>` | Your Gemini API key |
| `<GITHUB_TOKEN>` | Your GitHub fine-grained personal access token |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |
| `<INSTRUCTOR_EMAIL>` | The email address of the instructor |
