# Lab 1: Run a Model in a Harness

You will look inside three small models stored in three popular formats, run them in a harness you can read, change their settings, and then run the same kind of model in three other local runtimes. Optional parts add image models and cloud models, and the bonus parts try the official command-line tools and desktop apps of four AI companies.

**Step-by-step walkthrough for your operating system** (each starts with Part 0, the setup for the lab):

- [Windows](LAB01_Windows_Run_a_Model_in_a_Harness.md)
- [macOS](LAB01_MacOS_Run_a_Model_in_a_Harness.md)
- [Linux](LAB01_Linux_Run_a_Model_in_a_Harness.md)

**Without the internet** (from a USB drive, or after you ran the pre-fetch script): [Windows](LAB01_Windows_Run_a_Model_in_a_Harness_OFFLINE.md) · [macOS](LAB01_MacOS_Run_a_Model_in_a_Harness_OFFLINE.md) · [Linux](LAB01_Linux_Run_a_Model_in_a_Harness_OFFLINE.md)

**Pre-fetch scripts** (download every file for this lab into `Downloads/<OS>`; each runs on any operating system): Windows: [.sh](LAB01_Windows_pre-fetch.sh) [.ps1](LAB01_Windows_pre-fetch.ps1) [.py](LAB01_Windows_pre-fetch.py) · macOS: [.sh](LAB01_MacOS_pre-fetch.sh) [.ps1](LAB01_MacOS_pre-fetch.ps1) [.py](LAB01_MacOS_pre-fetch.py) · Linux: [.sh](LAB01_Linux_pre-fetch.sh) [.ps1](LAB01_Linux_pre-fetch.ps1) [.py](LAB01_Linux_pre-fetch.py)

| Part | What you do | In the room? |
|---|---|---|
| Setup | Install and download | Before the workshop |
| [Part 1](#part-1-look-inside-three-model-formats) | Look inside three models: GGUF, safetensors, ONNX (1e: optional Ministral 3) | Yes |
| [Part 2](#part-2-run-the-models-in-the-harness) | 2a run them in the harness, 2b change settings, 2c image models (optional) | Yes (2c optional) |
| [Part 3](#part-3-optional-cloud-models-with-api-keys-safely) | Cloud models with API keys: 3a Anthropic, 3b OpenAI, 3c Gemini, 3d Copilot | Optional |
| [Part 4](#part-4-the-same-model-in-three-local-runtimes-docker) | Local runtimes in Docker: 4a Ollama (CLI, then GUI); optional 4b KoboldCpp and 4c llama.cpp | Yes (4b, 4c optional) |
| [Part 5](#bonus-part-5-the-official-ai-command-line-tools) | Bonus: CLIs: 5a Claude Code, 5b Codex, 5c Gemini, 5d Copilot | At home |
| [Part 6](#bonus-part-6-the-official-ai-desktop-apps) | Bonus: GUIs: 6a Claude, 6b ChatGPT, 6c Gemini, 6d Copilot | At home |

Checkpoint: one table comparing the three model files, one chat with each, and the Part 1 GGUF model answering in Ollama, by command line and GUI.

## What you need

- Python 3.10 or newer
- 16 GB of RAM. The largest model uses about 3 GB while running.
- About 20 GB of free disk for this lab (models about 6 GB, Docker images about 7 GB), plus 3 GB for the optional image models.
- Docker Desktop (Docker Engine on Linux) for Part 4
- No GPU is required. Every step runs on the CPU. If you have a GPU, each step that can use one shows an optional GPU command.
- The files in this folder: `inspect_model.py`, `harness.py`, `requirements.txt`, `requirements-hf.txt`, `compose.yaml`

On Windows use `py -3` in place of `python3` in every command.

## Setup. Install and download

```
python3 -m pip install -r requirements.txt
```

Then install PyTorch (needed for the safetensors model in Part 2 and the image models in Part 2c), from the right place for your computer:

```
# Linux or Windows (CPU only, a small download):
python3 -m pip install torch --index-url https://download.pytorch.org/whl/cpu
# macOS:
python3 -m pip install torch

python3 -m pip install -r requirements-hf.txt
```

Download everything (run it from the `prefetch` folder; it resumes if it stops):

```
python3 prefetch_lab1.py                 # the models for Parts 1 and 2, and the Docker images for Part 4
python3 prefetch_lab1images.py           # optional: the image models for Part 2c (about 3 GB)
python3 prefetch_lab1ministral.py        # optional: Ministral 3 at about 1 GB for Part 1e (about 3.2 GB)
```

**Optional: use a GPU.** The commands above install CPU builds, which work everywhere. To let the harness use a GPU, replace them with GPU builds, then add `--gpu-layers -1` to any `harness.py` command that loads a local model.

For GGUF models (`llama-cpp-python`), pick the line for your hardware:

| Your GPU | Install command (replaces the CPU build) |
|---|---|
| NVIDIA (Windows or Linux, CUDA 12 driver) | `python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124` |
| Apple Silicon (M1 or newer, Metal) | `python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal` |
| AMD or Intel (Vulkan, builds from source) | Linux/macOS: `CMAKE_ARGS="-DGGML_VULKAN=on" python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` · Windows PowerShell: `$env:CMAKE_ARGS="-DGGML_VULKAN=on"; py -3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` |
| NVIDIA, if no ready-made wheel matches | Linux/macOS: `CMAKE_ARGS="-DGGML_CUDA=on" python3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` · Windows PowerShell: `$env:CMAKE_ARGS="-DGGML_CUDA=on"; py -3 -m pip install llama-cpp-python --force-reinstall --no-cache-dir` (needs the CUDA Toolkit and a C++ compiler) |

`cu124` matches CUDA 12.4; use `cu121` to `cu125` to match your driver (`nvidia-smi` shows it). Building from source needs a compiler and can take 10 minutes or more, so do it before the workshop. `--gpu-layers -1` puts every layer on the GPU; a smaller number (for example `20`) splits a GGUF model between GPU and CPU when the GPU has little memory.

For safetensors and image models (PyTorch): NVIDIA: `python3 -m pip install torch --force-reinstall --index-url https://download.pytorch.org/whl/cu124`. Apple Silicon: the normal macOS `torch` already uses the GPU (Metal). For ONNX models: NVIDIA: `python3 -m pip install onnxruntime-gpu` (uninstall `onnxruntime` first); Windows with any DirectX 12 GPU: `python3 -m pip install onnxruntime-directml`.

If a GPU build fails, reinstall the CPU build with the Setup commands; nothing else changes. On a CPU-only build the harness says it is ignoring `--gpu-layers` and carries on.

**If llama-cpp-python will not install.** Linux and Apple Silicon Macs normally work. On Windows or an Intel Mac pip may try to compile it and fail. You can still do Part 1 (the inspector does not need it), chat with the safetensors and ONNX models in Part 2, and use Ollama in Part 4. Or pair up with a neighbor.

## Part 1. Look inside three model formats

A model file is settings plus tensors (tables of numbers). The three files below hold models of the same family (Qwen 2.5, Apache-2.0 license), stored three different ways:

| File | Format | Model | Size | Used by |
|---|---|---|---|---|
| `models/qwen2.5-1.5b-instruct-q4_k_m.gguf` | GGUF | Qwen2.5 1.5B, 4-bit | about 1.1 GB | llama.cpp, Ollama, KoboldCpp, LM Studio |
| `models/qwen2.5-0.5b-instruct/` | safetensors | Qwen2.5 0.5B, 16-bit | about 1.0 GB | Hugging Face Transformers, PyTorch |
| `models/qwen2.5-0.5b-instruct-onnx/` | ONNX | Qwen2.5 0.5B, 8-bit | about 0.6 GB | ONNX Runtime, Windows ML, browsers |

`inspect_model.py` reads all three without running them, and never runs code from a file.

**1a. GGUF.** One file that carries its own settings and tokenizer. Usually quantized.

```
python3 inspect_model.py summary models/qwen2.5-1.5b-instruct-q4_k_m.gguf
python3 inspect_model.py tensor  models/qwen2.5-1.5b-instruct-q4_k_m.gguf blk.0.attn_q.weight
```

**1b. safetensors.** A JSON header plus raw numbers. The settings live next to it in `config.json`, the tokenizer in `tokenizer.json`.

```
python3 inspect_model.py summary models/qwen2.5-0.5b-instruct
python3 inspect_model.py tensor  models/qwen2.5-0.5b-instruct model.layers.0.self_attn.q_proj.weight
```

**1c. ONNX.** A whole computation graph: operators (MatMul, Add, Softmax...) plus the weights. The summary lists the most common operators. Quantized weights are stored as integers with a scale, and exporters often rename them (`onnx::MatMul_123`); the inspector names each one after the graph step that uses it.

```
python3 inspect_model.py summary models/qwen2.5-0.5b-instruct-onnx
```

Copy a tensor name from the summary (the `Next:` line suggests one) into `tensor`.

**1d. Compare and draw.**

```
python3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
python3 inspect_model.py heatmap models/qwen2.5-0.5b-instruct model.layers.0.mlp.up_proj.weight --out ffn.png
python3 inspect_model.py graph   models/qwen2.5-0.5b-instruct --out model.html
```

Open `ffn.png` and `model.html`. The graph page shows the path from tokens to embedding to the repeated block to the output, with the real shapes.

**Optional: Netron.** `python3 -m pip install netron`, then `netron models/qwen2.5-0.5b-instruct-onnx/onnx/model_quantized.onnx`. Netron draws the ONNX graph node by node. Its GGUF support is experimental.

**Security sidebar: pickle files.** Older PyTorch models come as `.bin`, `.pt` or `.pth` files in Python's pickle format, and loading one can run code hidden inside it. That is why safetensors exists. The inspector and the harness refuse pickle files. To see what a pickle would import, without loading it: `python3 inspect_model.py scan pytorch_model.bin` (use the name of your `.bin` file).

**1e (optional). Ministral 3, squeezed to about 1 GB.** Mistral AI's Ministral 3 family (Apache-2.0) starts at 3 billion parameters. Its official files are 2.1 GB (GGUF, 4-bit) and 4.7 GB (safetensors), and there is no ONNX build, so the only versions near 1 GB are community GGUF files quantized to 1 to 2 bits per weight. Download them with `python3 prefetch_lab1ministral.py` (about 2.1 GB, plus 1.1 GB in Ollama):

| File | Bits | Size |
|---|---|---|
| `models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf` | about 2 | 1.1 GB |
| `models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf` | about 1.5 | 1.0 GB |

Both come from `unsloth/Ministral-3-3B-Instruct-2512-GGUF` on Hugging Face. Ministral 3 can also read images; these labs use it for text only.

```
python3 inspect_model.py summary models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf
python3 inspect_model.py compare models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf models/qwen2.5-1.5b-instruct-q4_k_m.gguf
```

Look at the storage types: IQ quantization mixes very low-bit types for most weights with higher precision for the most sensitive ones. In Part 2a, chat with them and judge whether a 3B model at 1 to 2 bits beats a 1.5B model at 4 bits. In Lab 2 you can benchmark them (Part 2f).

To chat with them: `python3 harness.py chat --model models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf`. Ministral 3 is newer than some builds of `llama-cpp-python`; if the harness reports an unknown architecture, use Ollama (0.13.1 or newer) instead: `docker compose exec ollama ollama run hf.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF:UD-IQ2_XXS`, or the llama.cpp container: `MODEL=Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf docker compose --profile llamacpp up -d` (on Windows PowerShell, set `$env:MODEL` first).

Questions to answer in your workbook:

1. The 1.5B model has three times the parameters of the 0.5B model. Why are their files about the same size? (Look at bits per weight in `compare`.)
2. How many layers does each model have? Which group holds the most parameters?
3. What are the min and max of a GGUF tensor, a safetensors tensor and an ONNX tensor? Why does the ONNX one show whole numbers from 0 to 255?
4. What does the ONNX file contain that the other two do not?

## Part 2. Run the models in the harness

### Part 2a. Chat with each model

`harness.py` is a few hundred lines with no framework. It picks the right engine from the `--model` path: a `.gguf` file runs in llama.cpp, a safetensors folder in PyTorch, an ONNX folder in ONNX Runtime.

```
python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf
python3 harness.py chat --model models/qwen2.5-0.5b-instruct
python3 harness.py chat --model models/qwen2.5-0.5b-instruct-onnx
python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf
```

GPU option: add `--gpu-layers -1` to any of these (after the GPU installs in Setup).

The last one, Qwen3-4B (2.5 GB), is the larger model the later labs use. Optional: the Ministral 3 files from Part 1e work the same way. Ask each model the same two questions and compare speed and quality.

Commands inside the chat: `/set NAME VALUE`, `/system TEXT`, `/reset`, `/show`, `/help`, `/quit`.

Read `harness.py`. Find these pieces: the three local backend classes (`LlamaCppBackend`, `TransformersBackend`, `OnnxBackend`), `run_turn` which streams a reply, the settings table, and the message list that holds the conversation. `OnnxBackend.stream` writes the generation loop out by hand: run the graph, pick one token, feed it back, repeat.

### Part 2b. Change settings and try again

Ask the same question each time and compare the replies. Use `ask --repeat 3` to see variety:

```
python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --temperature 0.0 --repeat 3 "Write a one-line slogan for a bakery."
python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --temperature 1.2 --repeat 3 "Write a one-line slogan for a bakery."
python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --effort low  "Is 91 prime?"
python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --effort high "Is 91 prime?"
python3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx --temperature 0.0 --repeat 3 "Write a one-line slogan for a bakery."
```

With a GPU build, add `--gpu-layers -1` to each of these. The settings work the same; replies just arrive faster.

| Setting | What it does | Try |
|---|---|---|
| `--temperature` | How much randomness when picking the next token. 0 is almost always the same answer. | 0, 0.7, 1.2 |
| `--top-p`, `--top-k` | Cut the list of candidate tokens before picking. | top-k 1 vs 80 |
| `--max-tokens` | Hard cap on reply length. A reply cut off by it has finish reason `length`. | 20 vs 512 |
| `--seed` | Same seed and same settings give the same reply on the same machine. | 42 twice |
| `--repeat-penalty` | Discourages repeating tokens. | 1.0 vs 1.5 |
| `--stop` | The model stops when it writes this text. | `--stop "."` |
| `--system` | Instructions that come first. | "Answer like a pirate." |
| `--ctx` | Context window size. Bigger needs more memory. | 1024 vs 4096 |
| `--effort low/medium/high` | **A harness preset, not a model feature.** It turns Qwen3's thinking mode on or off (the `/think` and `/no_think` switch) and sets a token cap. High lets the model write a long chain of thought first, which is slower and costs more tokens. | low vs high |
| `--gpu-layers` | Local models only. 0 (the default) is CPU only; -1 puts the model on the GPU. Needs a GPU build (Setup). | 0 vs -1 |

### Part 2c (optional). Small image models

Copy a photo into the `Lab01` folder and name it `photo.jpg`. Two kinds of image model, both run with the same harness (needs `prefetch_lab1images.py` and the PyTorch install from Setup):

| Task | Model | Size | What it does |
|---|---|---|---|
| Recognition | `google/vit-base-patch16-224` (Apache-2.0) | about 0.35 GB | Names what is in a photo, from 1,000 everyday categories |
| Generation | `stabilityai/sd-turbo` (Stability AI Community License: non-commercial and small-business use) | about 2.6 GB | Draws a 512x512 picture from a sentence in one step |

```
python3 harness.py image classify photo.jpg
python3 harness.py image generate "a robot reading a book in a library, watercolor" --out robot.png
python3 harness.py image generate "a robot reading a book in a library, watercolor" --steps 4 --seed 7 --out robot4.png
```

GPU option: add `--gpu-layers -1`. On a laptop CPU one picture takes roughly 5 to 30 seconds; on a GPU it takes about a second.

Try it: classify a photo from your phone, then a picture you generated. Does the recognizer agree with what you asked the generator to draw? Change `--seed` and `--steps` and compare. The generator only knows what its training pictures showed, so look for what it gets wrong (hands, text, counting).

## Part 3 (optional). Cloud models with API keys, safely

The same `chat`, `ask` and `models` commands work with hosted models. You need your own API key. Cloud use is billed or rate-limited by the provider, and **your messages leave your computer**. Skip this part if you do not want to create keys; nothing later depends on it.

**The safe pattern for every provider:**

1. Make a key just for the workshop, with the least access the provider allows, a low spending limit, and an expiry if the provider offers one.
2. Save it in a key file only you can read (below), not in a command, a script, `.bashrc` or git.
3. List the models the key can use, then chat.
4. **Delete the key when the workshop ends.**

### Key safety on Linux (and macOS)

The provider documentation (Anthropic, Google, GitHub) agrees on the basics: treat a key like a password, keep it out of code and git, load it from the environment or a secret store, limit what it can do, and rotate or delete it. This is how that works on a Linux laptop.

**Before you start**

- Make a key just for the workshop. Give it the least access the provider allows (a fine-grained GitHub token with only `models:read`, a Gemini key restricted to the Gemini API) and a low spending limit or billing alert.
- Set an expiry where the provider allows one, and **delete the key when the workshop ends**.

**How to give the key to the harness** (checked in this order)

1. **A key file only you can read.** The harness refuses a file other users can read.

   ```
   umask 077
   mkdir -p <HOME_DIR>/.config/ai-keys
   cat > <HOME_DIR>/.config/ai-keys/anthropic     # paste <ANTHROPIC_API_KEY>, press Enter, then Ctrl-D
   python3 harness.py chat --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic
   ```

   Because the key goes to `cat` as typed input, it is not in your shell history.
2. **An environment variable for one command, from a keyring.** On a desktop with a keyring, install `libsecret-tools`, store the key once with `secret-tool store --label="Anthropic key" service anthropic`, then:

   ```
   ANTHROPIC_API_KEY="$(secret-tool lookup service anthropic)" python3 harness.py chat --backend anthropic
   ```

   The key is in the environment of that one program only. `pass show NAME` works the same way.
3. **The hidden prompt.** Set nothing. The harness asks and shows nothing as you type. This is the easiest choice for a class.

**On Windows:** use the hidden prompt (option 3), or a key file in your own profile folder, for example `<HOME_DIR>\.config\ai-keys\anthropic`, created in Notepad. Windows does not use Linux file modes, so the harness cannot check who else can read the file; keep it inside your own user folder and off shared or synced drives (OneDrive, Dropbox).

**What the harness does for you**

- There is no `--api-key` option. Anything on a command line is visible to every user on the machine through `ps` and is saved in shell history.
- The key is held in memory only, removed from the program's environment after it is read (so nothing the harness starts inherits it), kept out of core dumps, and blanked in any error text.
- `serve` will not share a cloud model on the network. It also asks for a random password on localhost, because on a shared Linux machine any other user can connect to localhost. It prints the password at startup. Enter it as the "API key" in Open WebUI or Continue.

**Do not**

- Put a key in `~/.bashrc`, `~/.profile` or `export` it for the whole session. Every program you run inherits it, and it sits on disk in plain text.
- Type `export ANTHROPIC_API_KEY=sk-...` at the prompt. It is saved in `~/.bash_history`. If you must, start the line with a space after `export HISTCONTROL=ignorespace`, then remove the line from history.
- Paste a key into a slide, a shared screen, a chat, a screenshot or a git repository. Keep `.env` files and key files out of git (the lab folder's `.gitignore` already does).
- Give a key to a third-party tool you do not trust. It gets everything the key can do.
- Pass a key to Docker with `-e KEY=value` or put it in `compose.yaml`. It shows up in `docker inspect` and shell history. Use `--env-file` with a mode 600 file, or Docker secrets. The Lab 1 containers do not need any key.

**What this cannot protect against.** The `root` user, and any program running as you, can read your process's memory and `/proc/<pid>/environ` (the environment the program started with, even after the harness removes the variable). A shared screen, a keylogger or malware also defeats it. On a shared machine, use your own account and do not leave the harness running.

**If a key leaks or you are unsure:** delete or revoke it at the provider's console at once, create a new one, and check the provider's usage page for charges you did not make.

### Part 3a. Anthropic (Claude)

Create a key at console.anthropic.com, under API keys. Use a workspace with a monthly spend limit.

```
python3 harness.py models --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic
python3 harness.py chat   --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic
```

### Part 3b. OpenAI

Create a project key at platform.openai.com, under API keys. Give it only the permissions it needs and set a project budget.

```
python3 harness.py models --backend openai --key-file <HOME_DIR>/.config/ai-keys/openai
python3 harness.py chat   --backend openai --key-file <HOME_DIR>/.config/ai-keys/openai
```

### Part 3c. Google Gemini

Create a key in Google AI Studio (aistudio.google.com, "Get API key"). In the Google Cloud console, restrict the key to the Generative Language API.

```
python3 harness.py models --backend gemini --key-file <HOME_DIR>/.config/ai-keys/gemini
python3 harness.py chat   --backend gemini --key-file <HOME_DIR>/.config/ai-keys/gemini
```

### Part 3d. Copilot (GitHub Models)

**GitHub Copilot itself has no public chat API**, so a Copilot subscription does not give you an API key. The API route for a GitHub account is GitHub Models. Create a fine-grained personal access token (GitHub, Settings, Developer settings) with only the **Models: read** permission and a short expiry.

```
python3 harness.py models --backend copilot --key-file <HOME_DIR>/.config/ai-keys/github
python3 harness.py chat   --backend copilot --key-file <HOME_DIR>/.config/ai-keys/github 
```

Without `--model`, `chat` shows the provider's current list of models with numbers: type a number to pick one. (`--backend copilot` and `--backend github` are the same thing.) The Copilot CLI and app in Parts 5d and 6d use your Copilot subscription instead.

Try the same prompts on a local model and a cloud model. Settings work a little differently: Anthropic accepts temperature from 0 to 1, `--effort`, `--ctx` and `--gpu-layers` apply only to local models, and `--seed` and `--repeat-penalty` are ignored by providers that do not support them.

## Part 4. The same model in three local runtimes (Docker)

A runtime loads a model and serves it. Here the Part 1 GGUF model runs in Ollama (Part 4a), and optionally in two more popular runtimes (Parts 4b and 4c), one at a time, each in a Docker container with its own web GUI. Every port is bound to `127.0.0.1`, so only your laptop can reach it. Start Docker Desktop first, and stop one runtime before starting the next (`docker compose --profile NAME down`).

### Part 4a. Ollama: CLI first, then a GUI

```
docker compose --profile ollama up -d
docker compose exec ollama ollama pull qwen2.5:1.5b
docker compose exec ollama ollama run qwen2.5:1.5b
```

That is the Ollama CLI: type a question, `/?` for help, `/bye` to leave. Then look around:

```
docker compose exec ollama ollama list          # models on disk
docker compose exec ollama ollama show qwen2.5:1.5b   # its settings and template
docker compose exec ollama ollama ps            # what is loaded, and on CPU or GPU
```

Now the GUI: open http://localhost:3000 (Open WebUI, started by the same profile). Create the first account (it is a local admin stored only in the container), pick `qwen2.5:1.5b`, and chat. Then point the harness at Ollama's API:

```
python3 harness.py ask --backend server --url http://localhost:11434/v1 --model qwen2.5:1.5b "What is a context window?"
docker compose --profile ollama down
```

GPU option (NVIDIA on Linux, or Windows with WSL 2): use `--profile ollama-gpu` in place of `--profile ollama`, and `ollama-gpu` in place of `ollama` after `exec`. On a Mac, Docker cannot use the GPU; the native Ollama app for macOS (ollama.com) uses Metal and runs the same commands without `docker compose exec ollama`.

### Part 4b (optional). KoboldCpp

```
docker compose --profile kobold up -d
```

Open http://localhost:5001 for its GUI (KoboldAI Lite) and chat. Try its settings panel: the same temperature and top-p you changed in Part 2b. Then:

```
python3 harness.py ask --backend server --url http://localhost:5001/v1 --model qwen "What is a context window?"
docker compose --profile kobold down
```

If the container will not start (the image is built mainly for GPUs), run the KoboldCpp program instead (`prefetch_lab8.py` downloads it): `./kobold/koboldcpp-linux-x64 --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 5001 --usecpu` (use your system's file name, as in Lab 8, Part 1 (in `Lab08.zip`)).

GPU option: `--profile kobold-gpu` (NVIDIA). With the program instead: replace `--usecpu` with `--usecuda --gpulayers 99` (NVIDIA), `--usevulkan --gpulayers 99` (AMD or Intel), or `--gpulayers 99` (Apple Silicon).

### Part 4c (optional). llama.cpp

```
docker compose --profile llamacpp up -d
```

Open http://localhost:8080 for llama.cpp's own web GUI and chat. Then:

```
python3 harness.py ask --backend server --url http://localhost:8080/v1 --model qwen "What is a context window?"
docker compose --profile llamacpp down
```

GPU option: `--profile llamacpp-gpu` (NVIDIA; uses the `server-cuda` image with `-ngl 99`).

If you did the optional parts, compare: same model file, same question, `--temperature 0 --seed 1` everywhere. Do the answers match? Which runtime was fastest on your laptop? Ollama applies its own chat template and defaults, so its replies differ a little.

## Bonus Part 5. The official AI command-line tools

These are agents: they read files, run commands and edit code in the folder you start them in. **Always start them in an empty practice folder**, keep their approval prompts on, and never use a "skip all permissions" or "yolo" option on your own machine.

```
mkdir <HOME_DIR>/ai-cli-test && cd <HOME_DIR>/ai-cli-test
```

Each needs an account or subscription with that company. Install commands change; check the linked page if one fails.

| Part | Tool | Install (macOS / Linux) | Install (Windows) | Sign in |
|---|---|---|---|---|
| 5a | Claude Code | `curl -fsSL https://claude.ai/install.sh \| bash` | PowerShell: `irm https://claude.ai/install.ps1 \| iex` | Run `claude`, sign in with a Pro, Max, Team or Enterprise plan, or a Console (API) account |
| 5b | OpenAI Codex CLI | `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` or `npm install -g @openai/codex` | PowerShell: `irm https://chatgpt.com/codex/install.ps1 \| iex` | Run `codex`, choose "Sign in with ChatGPT" (Plus, Pro, Business, Edu, Enterprise) or an API key |
| 5c | Gemini CLI | `npm install -g @google/gemini-cli` (needs Node.js) | same | Run `gemini`. See the note below |
| 5d | GitHub Copilot CLI | `npm install -g @github/copilot` (Node.js 22+), or `brew install --cask copilot-cli` | `winget install GitHub.Copilot` | Run `copilot`, then `/login`. Needs a Copilot plan |

**Note for 5c.** Since June 18, 2026, Google AI Pro and Ultra subscribers and free users reach Google's coding agent through the **Antigravity CLI** instead of Gemini CLI (install: `curl -fsSL https://antigravity.google/cli/install.sh | bash`, or PowerShell `irm https://antigravity.google/cli/install.ps1 | iex`). Gemini CLI still works with a paid Gemini API key or a Gemini Code Assist Standard or Enterprise license. With a key, use the key-file pattern from Part 3 for one command: `GEMINI_API_KEY="$(cat <HOME_DIR>/.config/ai-keys/gemini)" gemini`.

**Test each one the same way**, with a one-shot question in a safe, read-only mode:

| Part | Test command |
|---|---|
| 5a | `claude -p "In two sentences, what is a context window?" --permission-mode plan` |
| 5b | `codex exec --sandbox read-only "In two sentences, what is a context window?"` |
| 5c | `gemini -p "In two sentences, what is a context window?" --approval-mode plan` |
| 5d | `copilot -p "In two sentences, what is a context window?" -s` |

Flags change often; if one is not accepted, run the tool with `--help`. Then start each one interactively, ask it to "list the files here and explain what you could do", and watch when it asks permission. Write down: which actions needed approval, and how you would stop it (Ctrl-C, closing the terminal, revoking the sign-in).

When you are done: sign out (`/logout` in Claude Code and Copilot CLI), and delete `<HOME_DIR>/ai-cli-test`.

## Bonus Part 6. The official AI desktop apps

The same companies' chat apps, for comparison with the local GUIs in Part 4. Each sends your messages to the company's servers.

| Part | App | Where | Systems |
|---|---|---|---|
| 6a | Claude desktop app | claude.com/download | macOS, Windows (x64 and ARM64), Linux (beta: Ubuntu, Debian) |
| 6b | ChatGPT desktop app | openai.com/chatgpt/download | macOS 14+ on Apple Silicon; Windows. Elsewhere use chatgpt.com in a browser |
| 6c | Gemini | gemini.google.com in Chrome or Edge, then "Install as app" from the browser menu | Any system with Chrome or Edge (we found no Gemini-branded desktop app; Google's desktop app is the Antigravity coding agent at antigravity.google/download) |
| 6d | GitHub Copilot | The GitHub Copilot app (macOS, Apple Silicon: github.com/features/copilot), or Copilot Chat in VS Code on any system | macOS app; VS Code everywhere. (Microsoft's "Copilot" app for Windows is a different product.) |

**Test each one the same way:**

1. Ask the same three questions you asked the local models in Part 2. Compare quality and speed.
2. Open its settings and find: whether your chats are used for training, how long chats are kept, and how to delete them. Write down where each setting is.
3. Check what the app can reach on your computer (files, screen, microphone, browser) and turn off anything you do not need.

## Using the harness in later labs

The same file is reused:

- **Tools:** `python3 harness.py chat --model ... --tools --tool-dir .` The model writes a JSON tool call, the harness runs `list_dir`, `read_file` or `calculator` and feeds the result back. File access is limited to `--tool-dir`. Add `--approve` to confirm every call. (GPU option: add `--gpu-layers -1`.)
- **Lab 4 (Logging and Compliance):** `--log-dir` and `--syslog` log every request; Open WebUI sits in front of `serve`: `python3 harness.py serve --model models/Qwen3-4B-Q4_K_M.gguf --host 0.0.0.0 --port 13370` (GPU option: add `--gpu-layers -1`). It speaks the OpenAI chat API, so Open WebUI points at `http://host.docker.internal:13370/v1`. Docker on Linux needs `--host 0.0.0.0`.
- **Lab 3 (Integrations and Tooling):** start `serve` as above, then point Continue at `http://localhost:13370/v1` as an OpenAI-compatible provider.
- `serve` works with any of the Part 1 models too.
- **Lab 2 (benchmarking)** adds `--stats` and `--log` to measure time and tokens for every reply. **Lab 4** adds `--log-dir` (a CSV `.log` per session) and `--syslog` (plain, JSON, CEF or LEEF).

Test it without a model: `--backend echo` replies with your own words. Useful to check the plumbing.

## Troubleshooting

- *Out of memory or the laptop crawls:* close the browser, stop Docker containers you are not using, use `--ctx 2048`, or use the 0.5B models.
- *Very slow:* check that you ran a 4-bit or 8-bit file and not an F16 one. A laptop CPU writes a few to a dozen words per second. With a GPU, install a GPU build (Setup) and add `--gpu-layers -1`.
- *`--gpu-layers` is ignored:* the installed package is the CPU build. Reinstall with a GPU line from Setup.
- *GPU out of memory:* use a smaller number, for example `--gpu-layers 20`, so part of a GGUF model stays on the CPU.
- *`No config.json next to ...`:* a safetensors or ONNX model needs its whole folder, not just the weights file.
- *`Could not reach http://...`:* the server or container is not running, or the port is different. `docker compose ps` shows what is running.
- *A Docker port is already in use:* another runtime is still running. Stop it with `docker compose --profile NAME down`.
- *HTTP 401 or 403 from a cloud backend:* the key is wrong or not allowed to use that model. *HTTP 404:* the model name is wrong (run `models`). *HTTP 429:* no credit or a rate limit.
- *A tensor name is not found:* run `summary` and copy a name from the list.

## Files

| File | What it is |
|---|---|
| `inspect_model.py` | summary, tensor, heatmap, graph, compare and scan, for GGUF, safetensors and ONNX |
| `harness.py` | chat, ask, serve, models and image commands. Local (GGUF, safetensors, ONNX) and cloud backends |
| `requirements.txt` | core pip packages |
| `requirements-hf.txt` | PyTorch packages for the safetensors and image models |
| `compose.yaml` | Part 4 Docker services: Ollama with Open WebUI, KoboldCpp, llama.cpp, and GPU versions |
| `.gitignore` | keeps keys, `.env` files and models out of git |

## Placeholders

Replace each placeholder, including the angle brackets, with your own value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` (Windows), `/Users/jsmith` (macOS) or `/home/jsmith` (Linux) |
| `<ANTHROPIC_API_KEY>` | Your Anthropic API key |
