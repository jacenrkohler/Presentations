# Pre-work: Under the Hood of LLMs

BSidesDFW 2026 workshop, Saturday, November 7, 2026, Nedderman Hall, UTA. Please finish Sections 1 and 2 before you arrive. Allow one to two hours, most of it waiting for downloads (about 15 GB). The venue Wi-Fi will not keep up with a room full of people downloading at once.

## What's in this section

1. [Access to participate (BSidesDFW Discord)](#section-1-access-to-participate-bsidesdfw-discord)
2. [Downloads and Installs (large files)](#section-2-downloads-and-installs-large-files): everything Labs 1 to 4 need
3. [Helpful Knowledge (YouTube Videos)](#section-3-helpful-knowledge-youtube-videos)
4. [Optional extras](#section-4-optional-extras): cloud accounts and API keys, the official AI command-line tools and desktop apps, and files for the optional parts and homework labs

Then a [quick check before you come](#quick-check-before-you-come) and [where to ask questions](#questions).

# Section 1: Access to participate (BSidesDFW Discord)

## 1.1 Join the Discord

Start here: https://discord.gg/faGUQTCe

1. **Accept the Code of Conduct.** In the [#code_of_conduct](https://ptb.discord.com/channels/747866151547306084/794652112851566593) channel, react with a green check mark (✅) on the post.
2. **Get the @ role.** In the [#rules_n_access_ctrl](https://ptb.discord.com/channels/747866151547306084/794697735454457887) channel, react with the cowperson emoji (🤠).
3. **Find the workshop.** Open the **#==x_BSidesDFW_2026==$** category.
   1. Use the forum channel **2026_wkshp_underhood_llm_forum** for text conversation and file sharing.
   2. Remote attendees: use the voice channel **2026_wkshp_underhood_llm_forum** for voice and screen sharing.

# Section 2: Downloads and Installs (large files)

Everything in this section is required for Labs 1 to 4. Do the steps in order.

**Step-by-step guides for your operating system.** These cover the same steps in more detail, with download links, the official installation guides, configuration, and a test that everything works with no internet connection:

- Windows (including WSL 2): [pre-work_downloads-installations_Windows.md](pre-work_downloads-installations_Windows.md)
- macOS: [pre-work_downloads-installations_MacOS.md](pre-work_downloads-installations_MacOS.md)
- Linux: [pre-work_downloads-installations_Linux.md](pre-work_downloads-installations_Linux.md)

Use your operating system's guide if you prefer it; the summary below is the same process.

## 2.1 Check your laptop

| You need | Notes |
|---|---|
| A laptop you can install software on | Windows, macOS, or Linux. |
| A GPU (optional) | **No GPU is required.** Every lab runs on the CPU. If you have one, a GPU makes the labs run faster, especially model replies in Labs 1 to 3. Using it can take extra setup (a GPU-enabled build of the software), so do not worry if you skip it. The workshop is timed for CPU. |
| 16 GB of RAM | The largest model uses about 3 GB while running. Close other heavy programs during the labs. |
| 25 GB of free disk space | About 15 GB of downloads, plus room for Docker to unpack images. |
| Admin rights | You will install Python, Docker and VS Code. |

### Laptop options by operating system

Any of these works. Three things matter most: RAM, free disk space, and whether Python can install `llama-cpp-python` (Lab 1).

| | Windows | macOS | Linux |
|---|---|---|---|
| **Best choice** | Windows 11, 64-bit Intel or AMD, 16 GB RAM or more | Apple Silicon Mac (M1 or newer), 16 GB RAM or more | Any recent 64-bit distribution (Ubuntu, Fedora, Debian), 16 GB RAM or more |
| **Also works** | Windows 10 (22H2) with a current Docker Desktop | Intel Mac with 16 GB RAM, with the caveats below | A Linux virtual machine on another OS, with 16 GB given to it |
| **Free disk** | 25 GB or more | 25 GB or more | 25 GB or more |
| **Docker** | Docker Desktop, with virtualization turned on in the BIOS and WSL 2 enabled | Docker Desktop for your chip (Apple silicon or Intel) | Docker Engine, and your user in the `docker` group |
| **Python** | python.org installer, with "Add python.exe to PATH" ticked. Use `py -3` in commands. | python.org installer or Homebrew. Use `python3`. | The system `python3`, plus `python3-pip` and `python3-venv` |
| **Local model install (Lab 1)** | May try to compile `llama-cpp-python` and fail. Fallback: Ollama, or pair up with a neighbor. | Works on Apple Silicon. On Intel, expect the same compile problem as Windows. | Works. Needs a C compiler only if no ready-made package is found. |
| **Good to know** | Run commands in PowerShell or Windows Terminal. Docker Desktop needs admin rights. | Use the Terminal app. | Start `harness.py serve` with `--host 0.0.0.0` so Docker containers can reach it (Lab 4). |

**If you have 8 GB of RAM:** it is too tight for the larger model alongside Docker and Open WebUI. Pair up with a neighbor, or bring a second machine.

**If you are borrowing or buying:** an Apple Silicon MacBook or a 16 GB Windows or Linux laptop from the last five years or so is plenty. Do not buy anything for this workshop.

## 2.2 Install the software

On Windows, use `py -3` in place of `python3` in every command in this document, and run commands in PowerShell.

### Python 3.10 or newer

- **Windows:** download the installer from https://www.python.org/downloads/windows/. On the first screen, tick **Add python.exe to PATH**, then **Install Now**.
- **macOS:** download the installer from https://www.python.org/downloads/macos/ and run it. (Homebrew users: `brew install python`.)
- **Linux (Ubuntu or Debian):** `sudo apt update && sudo apt install python3 python3-pip python3-venv`. **Fedora:** `sudo dnf install python3 python3-pip`.

Check it in a new terminal: `python3 --version` (Windows: `py -3 --version`) should print 3.10 or higher.

### Docker

- **Windows:**
  1. Install WSL 2 (Windows Subsystem for Linux), which Docker Desktop needs: open PowerShell as Administrator, run `wsl --install`, and restart. (If WSL is already installed, run `wsl --update` instead.) See the Windows guide above for details.
  2. Download Docker Desktop from https://www.docker.com/products/docker-desktop/ and install it with the **Use WSL 2** option.
  3. If Docker says virtualization is off, turn on Intel VT-x or AMD-V (SVM) in your BIOS or UEFI settings.
- **macOS:** download Docker Desktop for your chip (Apple silicon or Intel) from https://www.docker.com/products/docker-desktop/, drag it to Applications, and open it.
- **Linux:** follow the guide for your distribution at https://docs.docker.com/engine/install/ (it includes the `docker compose` plugin). Then let your user run Docker without sudo: `sudo usermod -aG docker $USER`, and log out and back in.

**Configure it:**

- Docker Desktop (Windows and macOS): open **Settings, Resources** and give Docker at least **8 GB of memory** (on Windows with WSL 2, Docker uses up to half your RAM by default, which is fine on 16 GB).
- Docker Desktop: you can skip signing in to a Docker account; it is not needed for these labs.

Check it: `docker run --rm hello-world` prints "Hello from Docker!", and `docker compose version` prints a version.

### VS Code and the Continue extension (Lab 3)

1. Download VS Code from https://code.visualstudio.com/download and install it.
2. Open VS Code, open the **Extensions** view (Ctrl+Shift+X, or Cmd+Shift+X on a Mac), search for **Continue**, and install it (publisher: Continue). Its page: https://marketplace.visualstudio.com/items?itemName=Continue.continue
3. macOS only: open the Command Palette (Cmd+Shift+P) and run **Shell Command: Install 'code' command in PATH**, so scripts can find VS Code.

### A terminal

Windows Terminal or PowerShell (Windows), Terminal (macOS), or your usual terminal (Linux). You will often have two or three open at once.

## 2.3 Get the lab files

1. Download the handout: **[add the link]**.
2. Unzip it into a folder you can find again, ideally with no spaces in its path (for example `Documents/ai-workshop`).
3. You should see these folders: `lab1`, `lab2`, `lab4`, `labs`, `homework`, and `prefetch`. Keep them together: later labs use files from `lab1`.

## 2.4 Install the Python packages

In a terminal, go to the `lab1` folder. We recommend a virtual environment, so these packages do not mix with anything else on your machine:

```
python3 -m venv .venv
source .venv/bin/activate          # macOS and Linux
.venv\Scripts\Activate.ps1         # Windows PowerShell (instead of the line above)
```

(Activate it again in every new terminal you use for the labs. If Windows refuses to run the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once.)

Then install:

```
python3 -m pip install -r requirements.txt
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu     # Linux or Windows
python3 -m pip install torch                                                     # macOS (instead of the line above)
python3 -m pip install -r requirements-hf.txt
```

**If `llama-cpp-python` will not install** (it tries to compile and fails, usually on Windows or an Intel Mac): carry on with everything else. You can still do most of Lab 1 with the safetensors and ONNX models and with Ollama, and you can pair up with a neighbor for the GGUF steps.

**GPU option.** These commands install the CPU builds, which every lab works with. If you have a GPU and want faster replies, follow "Optional: use a GPU" in `lab1/README.md` (in Setup) now: some GPU builds compile for 10 minutes or more.

## 2.5 Download the models and Docker images

Start Docker first. Then, in a terminal in the `prefetch` folder (with your virtual environment active):

```
python3 prefetch_all.py
```

This downloads everything Labs 1 to 4 need, in the order you will use them: about 15 GB. It shows progress bars. Run it again if it stops: finished items are skipped and partial files resume. Files go into the `lab1` folder, where the labs expect them.

To run it hidden in the background and check on it later:

```
python3 prefetch_all.py --background
python3 ai_prefetch.py --status --watch
```

Add `--dry-run` to see the sizes first. If your disk is tight, run `python3 prefetch_models.py` (models only) now and the rest later.

### What gets downloaded

| Lab | What you do | Downloads (about) |
|---|---|---|
| Lab 1 | Run a Model in a Harness | Python packages (if Section 2.4 did not already install them), three small models in GGUF, safetensors and ONNX formats (2.7 GB), the Qwen3-4B model (2.5 GB), and the Docker images for Ollama, Open WebUI, KoboldCpp and llama.cpp, plus a 1 GB model inside Ollama (about 8 GB) |
| Lab 2 | Benchmarking Models and Harnesses | A second Ollama model for the benchmark (qwen3:1.7b, 1.4 GB) |
| Lab 3 | Integrations and Tooling | The Continue extension, if you have not installed it (50 MB) |
| Lab 4 | Logging and Compliance | Nothing new: it uses Open WebUI from Lab 1 and a small syslog listener that comes with the handout |

If any step fails, run the script again, then ask in the Discord forum channel.

## 2.6 Set up and check

Do these once, after the downloads finish. Each takes a minute or two. In a terminal in the `lab1` folder, with your virtual environment active:

1. **The harness runs.** `python3 harness.py ask --backend echo "hello"` should print `(echo) You said: hello`.
2. **A model loads.** `python3 inspect_model.py summary models/qwen2.5-0.5b-instruct` prints the model's layers and size. Then `python3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."` should answer within a minute.
3. **Open WebUI account (Lab 1, Part 4a; Labs 3 and 4).**
   1. `docker compose --profile ollama up -d`
   2. Open http://localhost:3000 in your browser and create the first account. It becomes the **local admin**, stored only inside the container on your laptop. Use any email and a password you will remember.
   3. Pick the model `qwen2.5:1.5b` and say hello.
   4. `docker compose --profile ollama down`
4. **VS Code.** Open VS Code and click the Continue icon in the side bar once, so it creates its settings file. (You will connect it to the harness in Lab 3.)
5. **Syslog listener (Lab 4).** In the `lab4` folder: `python3 syslog_listen.py`. It should say it is listening on port 5514. Stop it with Ctrl-C.

If any of these fail, post the error in the Discord forum channel before the workshop.

# Section 3: Helpful Knowledge (YouTube Videos)

Optional, but they help.

You do not need any math background for the workshop. These videos give you the picture we build on, ordered from simplest to most advanced. Watch the first three before you come, and pick up the rest as you like.

**Quick primers (start here)**

1. [Neural Networks Explained in 5 Minutes](https://youtu.be/jmmW0F0biz0) (IBM Technology)
2. [Simple Neural Network in 3 Minutes](https://youtu.be/iyrmwErURJs) (3-Minute Data Science)
3. [What are Neural Networks? How AIs Think](https://youtu.be/JeVDjExBf7Y) (Code Bullet)

**3Blue1Brown, "Neural networks" playlist**

Whole playlist: https://youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi

If you only watch two: *But what is a neural network?* and *Large Language Models explained briefly*.

4. [But what is a neural network?](https://youtu.be/aircAruvnKk) (Chapter 1)
5. [Gradient descent, how neural networks learn](https://youtu.be/IHZwWFHWa-w) (Chapter 2)
6. [Backpropagation, intuitively](https://youtu.be/Ilg3gGewQ5U) (Chapter 3)
7. [Backpropagation calculus](https://youtu.be/tIeHLnjs5U8) (Chapter 4, the math-heavy one; skip if you like)
8. [Large Language Models explained briefly](https://youtu.be/LPZh9BOjkQs)
9. [Transformers, the tech behind LLMs](https://youtu.be/wjZofJX0v4M) (Chapter 5)
10. [Attention in transformers, step-by-step](https://youtu.be/eMlx5fFNoYc) (Chapter 6)
11. [How might LLMs store facts?](https://youtu.be/9-Jl0dxWQs8) (Chapter 7)
12. [But what is cross-entropy?](https://youtu.be/GlYgs6v2YfU) (Compression is Intelligence, part 2)
13. [But how do AI images and videos actually work?](https://youtu.be/iv-5mZ_9CPY) (guest video by Welch Labs)

How they connect to the day: the neuron and the weights are Lab 1 (you will read a real model's weights), gradient descent and backpropagation are what homework Lab 8 does in a minute on your laptop, and transformers, attention, and temperature are the "What is this?" talk.

# Section 4: Optional extras

Nothing in this section is required for the workshop. It prepares the optional parts of Labs 1 to 4 and the homework labs. Skip anything you do not plan to try.

## 4.1 Optional models and files

| For | What | How |
|---|---|---|
| Lab 1, Part 2c | Image models: a recognizer (ViT) and a generator (sd-turbo), about 3 GB | `python3 prefetch_lab1images.py` in the `prefetch` folder |
| Lab 1, Part 1e; Lab 2, Part 2f | Ministral 3 squeezed to about 1 GB (two GGUF files, plus one in Ollama), about 3.2 GB | `python3 prefetch_lab1ministral.py` |
| Any lab | GPU builds of the model software | "Optional: use a GPU" in `lab1/README.md`, Setup |
| Lab 3, Part 2 | Obsidian, a notes app whose vault becomes the model's memory | Download from https://obsidian.md/download and install. Create a vault called `AI Vault` and note where it is saved |
| Lab 3, Parts 1f and 2f; Section 4.3 | Node.js 22 or newer (for the npm-installed CLIs and the MCP filesystem server) | Download the LTS installer from https://nodejs.org/en/download, or use your package manager. Check: `node --version` |

## 4.2 Cloud accounts and API keys

Used by Lab 1 Part 3, Lab 2 Part 3, Lab 3 Parts 1e and 2e, and Lab 4 Parts 3b to 3e. Each provider bills or rate-limits its API separately from any chat subscription you may already have. Using all four for the workshop's exercises should cost a few dollars at most, but check each provider's current prices.

### The safe way to handle any API key

1. **One key just for the workshop**, per provider, with the least access the provider allows.
2. **A spending limit** (or a small prepaid credit) and, where offered, an **expiry date**.
3. **Store it in a key file only you can read** (below), with the master copy in a password manager. Never put a key in a command line, a script, `.bashrc` or `.profile`, a Git repository, a screenshot, a slide, Discord, or a chat with an AI model.
4. **Delete (revoke) the key when the workshop is over.**

**Make the key folder and a key file.** Copy the key from the provider's page, then:

- macOS and Linux:

  ```
  umask 077
  mkdir -p ~/.config/ai-keys
  cat > ~/.config/ai-keys/anthropic     # paste the key, press Enter, then Ctrl-D
  ```

  `umask 077` makes the file readable only by you; the harness refuses a key file that other users can read. Because you paste the key into `cat`, it is not saved in your shell history.
- Windows PowerShell:

  ```
  New-Item -ItemType Directory -Force "$env:USERPROFILE\.config\ai-keys" | Out-Null
  notepad "$env:USERPROFILE\.config\ai-keys\anthropic.txt"          # paste the key, save, close
  icacls "$env:USERPROFILE\.config\ai-keys" /inheritance:r /grant:r "${env:USERNAME}:(OI)(CI)F"
  ```

  The last line removes everyone else's access to the folder. Keep the folder out of OneDrive and other synced folders.

Use the same pattern for `openai`, `gemini` and `github`. In the labs you point the harness at the file with `--key-file` (on Windows, include the `.txt`). The labs (Lab 1, Part 3) also show how to test each key with `python3 harness.py models --backend PROVIDER --key-file ...`.

### Anthropic (Claude)

1. Create an account at https://console.anthropic.com (the Claude Console). It is separate from a claude.ai chat subscription.
2. Under **Billing**, add a payment method and buy a small amount of credit.
3. Under **Settings, Workspaces**, create a workspace for the workshop and set a low monthly spend limit for it.
4. Under **API keys**, choose **Create key**, pick that workspace, name it `bsides-workshop`, and copy the key (it is shown once). Save it as `anthropic` in your key folder.

### OpenAI

1. Create an account at https://platform.openai.com. It is separate from a ChatGPT subscription.
2. Under **Settings, Billing**, add a payment method and a small prepaid credit, and set a budget limit.
3. Create a **project** for the workshop, then under **API keys** choose **Create new secret key**, owned by that project. If offered, choose **Restricted** permissions and allow only model use.
4. Copy the key (shown once) and save it as `openai` in your key folder.

### Google Gemini

1. Sign in at https://aistudio.google.com with a Google account.
2. Choose **Get API key**, then **Create API key** (in a new Google Cloud project is fine).
3. Recommended: in the Google Cloud console (https://console.cloud.google.com), under **APIs & Services, Credentials**, open the key and restrict it to the **Generative Language API**.
4. Save it as `gemini` in your key folder.

The free tier is rate-limited, and Google's terms for the free tier allow it to use your prompts to improve its products. Read the current terms, and use test data only.

### GitHub (Copilot and GitHub Models)

GitHub Copilot has no public chat API. The labs reach models with a GitHub account through **GitHub Models**, which needs a token, and use the **Copilot** plan for the Copilot CLI and app.

1. Create or sign in to an account at https://github.com.
2. For the Copilot CLI and app (Section 4.3): turn on a Copilot plan (a free plan is available) at https://github.com/features/copilot/plans.
3. For the API (the token): go to **Settings, Developer settings, Personal access tokens, Fine-grained tokens**, and choose **Generate new token**.
   - Name: `bsides-workshop`. Expiration: 7 days.
   - Repository access: **Public repositories** (read-only).
   - Permissions: **Models: Read-only**. Nothing else.
4. Copy the token and save it as `github` in your key folder.

### After the workshop

Revoke every workshop key: Anthropic and OpenAI under API keys, Google in AI Studio (or the Cloud console), and GitHub under Fine-grained tokens. Check each provider's usage page for charges you did not expect, and delete the key files.

## 4.3 The official AI command-line tools (CLIs)

Used by Lab 1 Bonus Part 5, Lab 2 Part 4, and Lab 3 Parts 1f and 2f. These are coding agents: they read files and run commands in the folder you start them in. Only start them in an empty practice folder, keep their approval prompts on, and never use a "skip permissions" or "yolo" mode on your own machine.

| CLI | Install (macOS / Linux) | Install (Windows PowerShell) | Account needed | Sign in |
|---|---|---|---|---|
| Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | `irm https://claude.ai/install.ps1 \| iex` | A Claude Pro, Max, Team or Enterprise plan, or an Anthropic Console account | Run `claude` and follow the browser sign-in |
| OpenAI Codex | `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` (or `npm install -g @openai/codex`) | `irm https://chatgpt.com/codex/install.ps1 \| iex` | A ChatGPT Plus, Pro, Business, Edu or Enterprise plan, or an OpenAI API key | Run `codex` and choose "Sign in with ChatGPT" |
| Gemini CLI | `npm install -g @google/gemini-cli` (needs Node.js) | same | A paid Gemini API key, or a Gemini Code Assist Standard or Enterprise license | Run `gemini` and choose a sign-in method |
| Antigravity CLI (Google's replacement for free and Google AI Pro or Ultra users) | `curl -fsSL https://antigravity.google/cli/install.sh \| bash` | `irm https://antigravity.google/cli/install.ps1 \| iex` | A Google account | Follow the prompts on first run |
| GitHub Copilot CLI | `npm install -g @github/copilot` (Node.js 22+) or `brew install --cask copilot-cli` | `winget install GitHub.Copilot` | A GitHub Copilot plan | Run `copilot`, then type `/login` |

Check each one: `claude --version`, `codex --version`, `gemini --version`, `copilot --version`. Install commands change; if one fails, check the tool's own install page:

- Claude Code: https://code.claude.com/docs/en/setup
- Codex: https://github.com/openai/codex
- Gemini CLI: https://geminicli.com/docs/get-started (and Antigravity: https://antigravity.google/download)
- Copilot CLI: https://docs.github.com/en/copilot/how-tos/copilot-cli

Make the practice folder now: `mkdir ~/ai-cli-test` (Windows: `mkdir $env:USERPROFILE\ai-cli-test`).

## 4.4 The official AI desktop apps (GUIs)

Used by Lab 1 Bonus Part 6. Each sends your messages to the company's servers.

| App | Download | Systems | Account |
|---|---|---|---|
| Claude | https://claude.com/download | macOS, Windows (x64 and ARM64), Linux (beta: Ubuntu, Debian) | A Claude account (free or paid) |
| ChatGPT | https://openai.com/chatgpt/download/ | macOS 14 or newer on Apple Silicon; Windows. Elsewhere, use https://chatgpt.com | An OpenAI account (free or paid) |
| Gemini | https://gemini.google.com in Chrome or Edge, then "Install as app" from the browser menu (we found no Gemini-branded desktop app) | Any system with Chrome or Edge | A Google account |
| GitHub Copilot | The GitHub Copilot app (macOS on Apple Silicon) from https://github.com/features/copilot, or the GitHub Copilot Chat extension in VS Code on any system | macOS app; VS Code everywhere | A GitHub account with a Copilot plan |

After installing each one, open its settings and find: whether your chats are used for training, how long they are kept, and how to delete them.

## 4.5 Homework labs

| Homework lab | What to prepare |
|---|---|
| Lab 6: Attack an agent | `python3 prefetch_lab6.py` (KoboldCpp, Hermes 3 3B and a small Qwen model, about 3 GB). A sandbox: a throwaway virtual machine (VirtualBox, https://www.virtualbox.org/wiki/Downloads, or on a Mac, UTM, https://mac.getutm.app) or a separate user account. OpenClaw can read files and run commands, so never run it in your everyday account. Setup notes for OpenClaw will be posted in the Discord forum channel. Copy `toolcall_test.py` from the handout into the `lab1/kobold` folder |
| Lab 7: VS Code with a local model | Nothing new: VS Code and Continue from Section 2.2 |
| Lab 8: Train your own tiny model | `python3 -m pip install numpy` (already installed if you did Section 2.4) |

# Quick check before you come

- [ ] Joined the Discord, reacted ✅ and 🤠, and found the workshop forum channel
- [ ] Python 3.10 or newer, Docker (running), VS Code and the Continue extension installed
- [ ] Python packages installed in `lab1` (Section 2.4)
- [ ] `python3 prefetch_all.py` finished with nothing left in the "remaining" list
- [ ] The five checks in Section 2.6 passed, including your Open WebUI admin account
- [ ] Watched the three quick-primer videos (optional)
- [ ] Laptop charged, charger packed, and at least 25 GB of disk free
- [ ] Optional: cloud API keys saved in your key folder, CLIs or apps installed (Section 4)

# Questions

Ask in the 2026_wkshp_underhood_llm_forum channel in the Discord, or email [your email].
