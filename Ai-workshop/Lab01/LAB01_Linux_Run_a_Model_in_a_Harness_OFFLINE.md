# Lab 1: Run a Model in a Harness (Linux, offline)

In this lab, you examine three small language models in three file formats. Then you use them in a harness, change their settings, and use them in three local runtimes.

Time in the workshop: 25 minutes.

| Part | What you do | Status |
|---|---|---|
| Part 0 | Set up for the lab | Do this before the workshop |
| Part 1 | Examine three model formats: GGUF, safetensors, ONNX | Required. 1e is optional |
| Part 2 | Use the models in the harness | Required. 2c is optional |
| Part 3 | Cloud models with API keys: 3a Anthropic, 3b OpenAI, 3c Gemini, 3d Copilot | Optional |
| Part 4 | Local runtimes in Docker: 4a Ollama, 4b KoboldCpp, 4c llama.cpp | 4a required. 4b and 4c optional |
| Part 5 | Bonus: the official AI command-line tools | At home |
| Part 6 | Bonus: the official AI desktop apps | At home |

## Part 0: Set up for the lab (from the USB drive)

This file is for the USB copy of the workshop. Use it if you cannot download the files (slow or limited internet). `<USB_DIR>` is the folder with the downloaded files: the `Downloads/Linux` folder of the USB drive, or the same folder in your `Ai-workshop` folder after you ran the pre-fetch script (`LAB01_Linux_pre-fetch` in the lab folder, or `LAB1-4_..._pre-fetch` for Labs 1 to 4). You do not need the internet for this setup.

**Parts that need the internet:** Part 3 (cloud models), Part 5 (official CLIs) and Part 6 (desktop apps). Do them later, or skip them.

### Part 0a: Install the software from the USB drive

| Software | File on the USB drive | Installation and configuration |
|---|---|---|
| Python 3.12, pip and venv | Your distribution (Ubuntu 24.04 and Fedora 40 or newer have Python 3.12), or `<USB_DIR>/cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz` | Make sure that `python3 --version` shows 3.12. If your distribution has an older Python, extract the file from the USB drive: `mkdir -p ~/python312 && tar -xzf <USB_DIR>/cpython-3.12.16+20261026-x86_64-unknown-linux-gnu-install_only.tar.gz -C ~/python312`. Then use `~/python312/python/bin/python3` instead of `python3` to make the virtual environment. This Python contains pip and venv |
| Docker Engine and the Compose plugin | `<USB_DIR>/docker-*.tgz` and `<USB_DIR>/docker-compose-linux-x86_64` | If Docker is already installed from your distribution, skip this row. Otherwise, in `<USB_DIR>`, do `sudo tar -xzf docker-*.tgz --strip-components=1 -C /usr/local/bin`, then `sudo mkdir -p /usr/local/lib/docker/cli-plugins && sudo cp docker-compose-linux-x86_64 /usr/local/lib/docker/cli-plugins/docker-compose && sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose`, then `sudo groupadd -f docker && sudo usermod -aG docker $USER`. Sign out and sign in. Start Docker with `sudo dockerd > /tmp/dockerd.log 2>&1 &` (do this again after each restart). `iptables` must be installed |

### Part 0b: Get the files from the USB drive

1. Copy the folder `<USB_DIR>/Ai-workshop` to your computer. Put it in a folder that has no spaces in its path, for example `<HOME_DIR>/ai-workshop`. If you ran the pre-fetch script in your own `Ai-workshop` folder, you already have the lab files: skip this step.
2. Make the folder `Lab01/models`. Copy these items from `<USB_DIR>` into it: all of the `.gguf` files, and the folders `qwen2.5-0.5b-instruct` and `qwen2.5-0.5b-instruct-onnx`. The optional models (Ministral 3 `.gguf` files, the folders `vit-base-patch16-224` and `sd-turbo`) are there only if your instructor added them.
3. Start Docker. Load the Docker images from the USB drive:

   ```
   docker load -i "<USB_DIR>/ollama_ollama_latest_amd64.tar"
   docker load -i "<USB_DIR>/ghcr.io_open-webui_open-webui_main_amd64.tar"
   docker load -i "<USB_DIR>/koboldai_koboldcpp_latest_amd64.tar"
   docker load -i "<USB_DIR>/ghcr.io_ggml-org_llama.cpp_server_amd64.tar"
   ```

   Each command takes one to three minutes.

4. Copy the Ollama models into Docker:

   ```
   docker volume create lab01_ollama-data
   docker run --rm -v lab01_ollama-data:/root/.ollama -v "<USB_DIR>/ollama:/src:ro" --entrypoint cp ollama/ollama:latest -a /src/. /root/.ollama/
   ```

   This copies the Ollama models `qwen2.5:1.5b` and `qwen3:1.7b` from the USB drive into the Docker volume of Lab 1.

5. Optional (Part 4b): the KoboldCpp program, CPU build, is in `<USB_DIR>` (`koboldcpp-linux-x64-nocuda`). Copy it into the folder `Lab01/kobold`.

### Part 0c: Configure

1. Make the virtual environment and install the Python packages. In terminal, go to the `Lab01` folder. Do these commands. They install the packages from the USB drive. They do not use the internet.

   ```
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m pip install --no-index --find-links "<USB_DIR>" -r requirements.txt
   python3 -m pip install --no-index --find-links "<USB_DIR>" torch
   python3 -m pip install --no-index --find-links "<USB_DIR>" -r requirements-hf.txt
   ```

   The packages on the USB drive are for Python 3.12. If pip shows "No matching distribution", examine the Python version with `python3 --version`.

   If `<USB_DIR>` does not contain a `torch` file, the last two commands fail: `accelerate` in `requirements-hf.txt` needs `torch`. The GGUF and ONNX parts operate without them. Do the two commands later, when you are online: for `torch`, use `--index-url https://download.pytorch.org/whl/cpu` instead of `--no-index --find-links ...`.

2. Make your Open WebUI admin account. In the `Lab01` folder, do `docker compose --profile ollama up -d`. Open http://localhost:3000. Make the first account with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. Then do `docker compose --profile ollama down`.

### Part 0d: Make sure that the setup is correct

1. In the `Lab01` folder, `python3 harness.py ask --backend echo "hello"` shows `(echo) You said: hello`.
2. The `models` folder contains `qwen2.5-1.5b-instruct-q4_k_m.gguf`, `qwen2.5-0.5b-instruct`, `qwen2.5-0.5b-instruct-onnx` and `Qwen3-4B-Q4_K_M.gguf`.
3. Do `docker images`. The list shows `ollama/ollama` and `ghcr.io/open-webui/open-webui`.
4. Turn off Wi-Fi. Do `python3 harness.py ask --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf "Say hello in five words."`. It gives an answer.

### Part 0e: GPU software

The normal files on the USB drive are for the CPU. Use the GPU options in this file only if all of these conditions are true: your computer has an NVIDIA GPU, the NVIDIA driver (version 550 or newer) is installed, and the USB drive has the folder `<USB_DIR>/gpu`. If one condition is false, ignore the GPU options.

To install the GPU software:

1. Activate the virtual environment of Lab 1. In terminal, in the `Lab01` folder, do these commands:

   ```
   python3 -m pip uninstall -y llama-cpp-python onnxruntime torch
   python3 -m pip install --no-index --find-links <USB_DIR>/gpu --find-links <USB_DIR> <USB_DIR>/gpu/llama_cpp_python-*.whl <USB_DIR>/gpu/torch-*.whl onnxruntime-gpu
   docker load -i <USB_DIR>/gpu/ghcr.io_ggml-org_llama.cpp_server-cuda_amd64.tar
   cp <USB_DIR>/gpu/koboldcpp-linux-x64 kobold/ && chmod +x kobold/koboldcpp-linux-x64
   ```

2. To make sure that the GPU software operates, do `python3 -c "import llama_cpp, torch, onnxruntime; print(llama_cpp.llama_supports_gpu_offload(), torch.cuda.is_available(), onnxruntime.get_available_providers())"`. The result shows `True True` and a list that contains `CUDAExecutionProvider`.
3. For the KoboldCpp GPU option (Lab 1 Part 4b), use `./kobold/koboldcpp-linux-x64` instead of the CPU build.

For the Docker GPU options (the `-gpu` profiles), you must also install the NVIDIA Container Toolkit. It is not on the USB drive and needs the internet: [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html).

To go back to the CPU software, do `python3 -m pip uninstall -y llama-cpp-python onnxruntime-gpu torch`. Then do the pip commands of Part 0c again.

### Part 0f: Before each session

Do these steps at the start of each session:

1. Open terminal.
2. Go to the `Lab01` folder of the lab files.
3. Activate the virtual environment:

   ```
   source .venv/bin/activate
   ```

   The prompt shows `(.venv)` when the virtual environment is active. Activate it again in each new terminal window.

### Placeholders

Some commands contain placeholders. Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `/home/jsmith` |
| `<ANTHROPIC_API_KEY>` | Your Anthropic API key |
| `<OPENAI_API_KEY>` | Your OpenAI API key |
| `<GEMINI_API_KEY>` | Your Gemini API key |
| `<GITHUB_TOKEN>` | Your GitHub fine-grained personal access token |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |
| `<USB_DIR>` | The folder for your operating system on the USB drive, for example `E:\Downloads\Windows` or `/Volumes/USB/Downloads/MacOS` |

**About the GPU options.** All commands in this file use the CPU. Use a GPU option only if your USB drive has the folder `gpu` and you installed the GPU software (Part 0e). The answers stay almost the same. Only the speed changes.

## Part 1: Examine three model formats

A model file contains settings and tensors. A tensor is a table of numbers (the weights). These three files contain models of the same family (Qwen 2.5). Each file uses a different format.

| File or folder | Format | Model | Size |
|---|---|---|---|
| `models/qwen2.5-1.5b-instruct-q4_k_m.gguf` | GGUF | Qwen2.5 1.5B, 4-bit | 1.1 GB |
| `models/qwen2.5-0.5b-instruct/` | safetensors | Qwen2.5 0.5B, 16-bit | 1.0 GB |
| `models/qwen2.5-0.5b-instruct-onnx/` | ONNX | Qwen2.5 0.5B, 8-bit | 0.6 GB |

The tool `inspect_model.py` reads all three formats. It does not start the model. It does not execute code from the file.

### Part 1a: GGUF

GGUF is one file. It contains the settings, the tokenizer and the weights.

1. Show the summary:

   ```
   python3 inspect_model.py summary models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

2. Show the values of one tensor:

   ```
   python3 inspect_model.py tensor models/qwen2.5-1.5b-instruct-q4_k_m.gguf blk.0.attn_q.weight
   ```

### Part 1b: safetensors

A safetensors file contains a JSON header and the numbers. The settings are in `config.json`. The tokenizer is in `tokenizer.json`.

1. Show the summary:

   ```
   python3 inspect_model.py summary models/qwen2.5-0.5b-instruct
   ```

2. Show the values of one tensor:

   ```
   python3 inspect_model.py tensor models/qwen2.5-0.5b-instruct model.layers.0.self_attn.q_proj.weight
   ```

### Part 1c: ONNX

An ONNX file contains a full computation graph: the operators and the weights.

1. Show the summary:

   ```
   python3 inspect_model.py summary models/qwen2.5-0.5b-instruct-onnx
   ```

2. Find the line that starts with `Next:` at the end of the summary. Do the command on that line.

### Part 1d: Compare and draw

1. Compare the three files:

   ```
   python3 inspect_model.py compare models/qwen2.5-1.5b-instruct-q4_k_m.gguf models/qwen2.5-0.5b-instruct models/qwen2.5-0.5b-instruct-onnx
   ```

2. Make a picture of one tensor and a map of the model:

   ```
   python3 inspect_model.py heatmap models/qwen2.5-0.5b-instruct model.layers.0.mlp.up_proj.weight --out ffn.png
   python3 inspect_model.py graph models/qwen2.5-0.5b-instruct --out model.html
   ```

3. Open the two files:

   ```
   xdg-open ffn.png
   xdg-open model.html
   ```

### Part 1e (optional): Ministral 3 at approximately 1 GB

Ministral 3 has 3 billion parameters. Only GGUF files of this model are near 1 GB. These files use 1 to 2 bits for each weight.

1. Download the files. Go to the `prefetch` folder and do this command:

   ```
   python3 prefetch_lab1ministral.py
   ```

2. Go back to the `Lab01` folder. Compare the Ministral files with the Qwen file:

   ```
   python3 inspect_model.py compare models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   ```

3. If the harness shows "unknown architecture" in Part 2, your `llama-cpp-python` is too old for this model. Use the llama.cpp container instead:

   ```
   MODEL=Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf docker compose --profile llamacpp up -d
   ```

### Security note: pickle files

Old PyTorch model files (`.bin`, `.pt`, `.pth`) use the Python pickle format. A pickle file can execute code when a program opens it. Safetensors does not have this problem. The inspector and the harness do not open pickle files. To see what a pickle file can import, use the `scan` command. It does not open the file. For example, for a file with the name `pytorch_model.bin`, do `python3 inspect_model.py scan pytorch_model.bin`.

### Questions

Write the answers in your workbook.

1. The 1.5B model has three times more parameters than the 0.5B model. Why are the two files approximately the same size? Look at "bits/weight" in the output of `compare`.
2. How many layers does each model have? Which group of tensors has the most parameters?
3. Find the minimum and the maximum of one tensor in each format. Why does the ONNX tensor show whole numbers from 0 to 255?
4. What does the ONNX file contain that the other two files do not contain?

## Part 2: Use the models in the harness

### Part 2a: Chat with each model

The harness selects the engine from the model path. A `.gguf` file uses llama.cpp. A safetensors folder uses PyTorch. An ONNX folder uses ONNX Runtime.

1. Start a chat with each model. Ask each model the same two questions. Type `/quit` to stop each chat.

   ```
   python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf
   python3 harness.py chat --model models/qwen2.5-0.5b-instruct
   python3 harness.py chat --model models/qwen2.5-0.5b-instruct-onnx
   python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf
   ```

   GPU option: add `--gpu-layers -1` to the command.

2. Compare the speed and the quality of the answers.
3. Open `harness.py` in a text editor. Find these parts: the classes `LlamaCppBackend`, `TransformersBackend` and `OnnxBackend`, the function `run_turn`, and the table `DEFAULTS`.

Chat commands: `/set NAME VALUE` changes a setting. `/system TEXT` changes the system prompt. `/reset` clears the conversation. `/show` shows the settings. `/quit` stops the chat.

### Part 2b: Change the settings

1. Ask the same question three times at temperature 0. Then do it at temperature 1.2:

   ```
   python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --temperature 0.0 --repeat 3 "Write a one-line slogan for a bakery."
   python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --temperature 1.2 --repeat 3 "Write a one-line slogan for a bakery."
   ```

2. Compare low effort and high effort:

   ```
   python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --effort low "Is 91 prime?"
   python3 harness.py ask --model models/Qwen3-4B-Q4_K_M.gguf --effort high "Is 91 prime?"
   ```

   GPU option: add `--gpu-layers -1` to the command.

| Parameter | What it does |
|---|---|
| `--temperature` | Sets the randomness of the next token. At 0, the answers are almost always the same. |
| `--top-p`, `--top-k` | Decrease the list of possible next tokens before the harness selects one. |
| `--max-tokens` | Sets the maximum length of the answer. |
| `--seed` | The same seed and the same settings give the same answer on the same computer. |
| `--repeat-penalty` | Decreases repeated tokens. |
| `--stop` | The model stops when it writes this text. |
| `--system` | Sets the instructions that come before the conversation. |
| `--ctx` | Sets the size of the context window. A larger window uses more memory. |
| `--effort low/medium/high` | A harness setting for Qwen3 only. High lets the model think before it answers. This is slower. |
| `--gpu-layers` | 0 (the default) uses only the CPU. -1 puts all layers on the GPU. |

### Part 2c (optional): Small image models

1. Download the image models (approximately 3 GB). Go to the `prefetch` folder and do `python3 prefetch_lab1images.py`. Then go back to the `Lab01` folder.
2. Copy a photo into the `Lab01` folder. Give it the name `photo.jpg`. Identify the contents of the photo:

   ```
   python3 harness.py image classify photo.jpg
   ```

3. Make a picture from a sentence:

   ```
   python3 harness.py image generate "a robot reading a book in a library, watercolor" --out robot.png
   ```

   GPU option: add `--gpu-layers -1` to the command. On a CPU, one picture takes approximately 5 to 30 seconds. On a GPU, it takes approximately 1 second.

4. Classify the picture that you made. Compare the result with your sentence.

The generator (sd-turbo) has a license for non-commercial use and small businesses.

## Part 3 (optional): Cloud models with API keys

In this part, your messages go to a cloud provider. The provider can charge you for each request. Nothing later in the workshop needs this part.

**CAUTION:** An API key is like a password. A person with your key can use your account and spend your money. Obey these rules:

1. Make a new key only for the workshop.
2. Give the key the minimum access. Set a low limit for cost.
3. Keep the key in a key file that only you can read.
4. Do not put the key on the command line, in a script, in a screenshot, in a chat, or in Git.
5. Delete the key after the workshop.

### Make a key file

The pre-work file, section 4.2, shows how to get a key from each provider. Save each key in its own file. Do these commands for the first key:

   ```
   umask 077
   mkdir -p <HOME_DIR>/.config/ai-keys
   cat > <HOME_DIR>/.config/ai-keys/anthropic
   ```

   Paste `<ANTHROPIC_API_KEY>`, push Enter, and then push Ctrl-D. Only you can read the file. The key does not go into your shell history.

Use the same steps for `openai` (`<OPENAI_API_KEY>`), `gemini` (`<GEMINI_API_KEY>`) and `github` (`<GITHUB_TOKEN>`).

### Part 3a: Anthropic

```
python3 harness.py models --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic
python3 harness.py chat --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic
```

The first command shows the models that your key can use. The second command shows the same list with numbers. Type the number of a model to start the chat. To go directly to a model the next time, add `--model` and the ID that the harness shows.

### Part 3b: OpenAI

```
python3 harness.py models --backend openai --key-file <HOME_DIR>/.config/ai-keys/openai
python3 harness.py chat --backend openai --key-file <HOME_DIR>/.config/ai-keys/openai
```

### Part 3c: Gemini

```
python3 harness.py models --backend gemini --key-file <HOME_DIR>/.config/ai-keys/gemini
python3 harness.py chat --backend gemini --key-file <HOME_DIR>/.config/ai-keys/gemini
```

### Part 3d: Copilot (GitHub Models)

GitHub Copilot does not have a public chat API. The API for a GitHub account is GitHub Models. It uses a GitHub token with the "Models: read" permission.

```
python3 harness.py models --backend copilot --key-file <HOME_DIR>/.config/ai-keys/github
python3 harness.py chat --backend copilot --key-file <HOME_DIR>/.config/ai-keys/github
```

The settings `--effort`, `--ctx` and `--gpu-layers` have no effect on cloud models.

## Part 4: The same model in three local runtimes

A runtime loads a model and gives access to it. In this part, you use the Part 1 GGUF model in Docker containers. Only your computer can connect to these containers. Start Docker before you start this part. Use only one runtime at a time.

### Part 4a: Ollama, first the CLI, then the GUI

1. Start Ollama and Open WebUI:

   ```
   docker compose --profile ollama up -d
   ```

   GPU option: NVIDIA only. Install the NVIDIA Container Toolkit first (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Use `--profile ollama-gpu` instead of `--profile ollama`. Use `exec ollama-gpu` instead of `exec ollama`.

2. Make sure that the model is available, then start a chat on the command line. Type `/bye` to stop the chat.

   ```
   docker compose exec ollama ollama list
   docker compose exec ollama ollama run qwen2.5:1.5b
   ```

3. Examine the model and the runtime:

   ```
   docker compose exec ollama ollama list
   docker compose exec ollama ollama show qwen2.5:1.5b
   docker compose exec ollama ollama ps
   ```

   The `PROCESSOR` column of `ollama ps` shows if the model uses the CPU or the GPU.

4. Open http://localhost:3000 in your browser. Sign in with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. Select `qwen2.5:1.5b` and start a chat.
5. Send a question to Ollama from the harness:

   ```
   python3 harness.py ask --backend server --url http://localhost:11434/v1 --model qwen2.5:1.5b "What is a context window?"
   ```

6. Stop Ollama and Open WebUI:

   ```
   docker compose --profile ollama down
   ```

### Part 4b (optional): KoboldCpp

1. Start KoboldCpp:

   ```
   docker compose --profile kobold up -d
   ```

   GPU option: NVIDIA only. Install the NVIDIA Container Toolkit first (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Use `--profile kobold-gpu` instead of `--profile kobold`.

2. Open http://localhost:5001. Start a chat. Find the temperature and top-p settings.
3. Send a question from the harness:

   ```
   python3 harness.py ask --backend server --url http://localhost:5001/v1 --model qwen "What is a context window?"
   ```

4. Stop KoboldCpp:

   ```
   docker compose --profile kobold down
   ```

If the container does not start, use the KoboldCpp program (CPU build). You copied it into the folder `Lab01/kobold` in Part 0b, step 5. Do this command:

```
chmod +x ./kobold/koboldcpp-linux-x64-nocuda
./kobold/koboldcpp-linux-x64-nocuda --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 5001 --usecpu
```

GPU option: NVIDIA: use the CUDA build `./kobold/koboldcpp-linux-x64` (Part 0e copies it from the USB drive). Replace `--usecpu` with `--usecuda --gpulayers 99`. AMD or Intel: use the CPU build and replace `--usecpu` with `--usevulkan --gpulayers 99`.

### Part 4c (optional): llama.cpp

1. Start the llama.cpp server:

   ```
   docker compose --profile llamacpp up -d
   ```

   GPU option: NVIDIA only. Install the NVIDIA Container Toolkit first (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html). Use `--profile llamacpp-gpu` instead of `--profile llamacpp`.

2. Open http://localhost:8080. Start a chat.
3. Send a question from the harness:

   ```
   python3 harness.py ask --backend server --url http://localhost:8080/v1 --model qwen "What is a context window?"
   ```

4. Stop the server:

   ```
   docker compose --profile llamacpp down
   ```

Compare the runtimes. Use the same question and `--temperature 0 --seed 1` each time. Which runtime is the fastest on your computer?

## Part 5 (bonus, at home): The official AI command-line tools

These tools are agents. They can read files, write files and execute commands in the folder where you start them.

**CAUTION:** Start these tools only in an empty practice folder. Keep their approval prompts on. Do not use a "skip permissions" or "yolo" mode on your computer.

1. Make the practice folder and go to it:

   ```
   mkdir <HOME_DIR>/ai-cli-test && cd <HOME_DIR>/ai-cli-test
   ```

2. Install the tools that you want to use:

| Part | Tool | Install command | Account |
|---|---|---|---|
| 5a | Claude Code | `curl -fsSL https://claude.ai/install.sh | bash` | A Claude Pro, Max, Team or Enterprise plan, or an Anthropic Console account |
| 5b | OpenAI Codex | `curl -fsSL https://chatgpt.com/codex/install.sh | sh` | A ChatGPT Plus, Pro, Business, Edu or Enterprise plan, or an OpenAI API key |
| 5c | Gemini CLI | `npm install -g @google/gemini-cli` (needs Node.js) | A paid Gemini API key, or a Gemini Code Assist Standard or Enterprise license |
| 5c | Antigravity CLI | `curl -fsSL https://antigravity.google/cli/install.sh | bash` | A Google account (free, Google AI Pro, or Google AI Ultra) |
| 5d | GitHub Copilot CLI | `npm install -g @github/copilot` (Node.js 22 or newer) | A GitHub Copilot plan |

3. Start each tool once (`claude`, `codex`, `gemini` or `copilot`) and sign in. For Copilot CLI, type `/login`.
4. Ask each tool the same question in a read-only mode:

| Part | Command |
|---|---|
| 5a | `claude -p "In two sentences, what is a context window?" --permission-mode plan` |
| 5b | `codex exec --sandbox read-only "In two sentences, what is a context window?"` |
| 5c | `gemini -p "In two sentences, what is a context window?" --approval-mode plan` |
| 5d | `copilot -p "In two sentences, what is a context window?" -s` |

5. If a tool does not accept a flag, do the command with `--help` to see the current flags.
6. Start each tool without `-p`. Ask: "List the files here and tell me what you can do." Record each time that the tool asks for permission.
7. When you are done, sign out (`/logout` in Claude Code and Copilot CLI). Delete the practice folder.

## Part 6 (bonus, at home): The official AI desktop apps

These apps send your messages to the servers of the company.

| Part | App | Where to get it on Linux |
|---|---|---|
| 6a | Claude | https://claude.com/download (beta for Ubuntu and Debian) |
| 6b | ChatGPT | No Linux app. Use https://chatgpt.com in a browser. |
| 6c | Gemini | https://gemini.google.com in Chrome. Use the browser menu to install it as an app. |
| 6d | GitHub Copilot | Copilot Chat in VS Code (install the GitHub Copilot Chat extension) |

For each app:

1. Ask the same three questions that you asked the local models in Part 2. Compare the quality and the speed.
2. Open the settings. Find these items: the control for the use of your chats to train models, the time that the company keeps your chats, and the procedure to delete them.
3. Find what the app can access on your computer (files, screen, microphone). Turn off the access that you do not need.

## Checkpoint

- A table from `compare` for the three model files.
- One chat with each model.
- The Part 1 GGUF model gives an answer in Ollama, on the command line and in the GUI.

## Problems and solutions

| Problem | Solution |
|---|---|
| The computer is very slow, or there is not sufficient memory | Close the browser tabs that you do not need. Stop the containers that you do not use. Use `--ctx 2048`, or use a 0.5B model. |
| `--gpu-layers` has no effect | You have the CPU build. Install a GPU build (Part 0e). |
| GPU out of memory | Use a smaller number, for example `--gpu-layers 20`. |
| `No config.json next to ...` | A safetensors model or an ONNX model needs its full folder, not only the weights file. |
| `Could not reach http://...` | The server or the container is not started, or the port is different. `docker compose ps` shows the containers that operate. |
| A Docker port is in use | Another runtime is still on. Stop it with `docker compose --profile NAME down`. |
| HTTP 401 or 403 from a cloud model | The key is incorrect, or it cannot use that model. |
| HTTP 404 from a cloud model | The model ID is incorrect. Do the `models` command again. |
| HTTP 429 from a cloud model | You have no credit, or you sent too many requests. |
