# Lab 2: Benchmarking Models and Harnesses (macOS)

A benchmark sends the same prompts in the same way to different models, settings or computers. It measures two things: the quality of the answers and their cost in time and tokens.

Time in the workshop: 20 minutes.

| Part | What you do | Status |
|---|---|---|
| Part 0 | Set up for the lab | Do this before the workshop |
| Part 1 | Add measurements to the harness | Required |
| Part 2 | Benchmark the harness and Ollama, compare the CPU and the GPU | Required. 2f is optional |
| Part 3 | Benchmark the cloud APIs: 3a Anthropic, 3b OpenAI, 3c Gemini, 3d Copilot | Optional |
| Part 4 | Benchmark the official CLIs: 4a Claude Code, 4b Codex, 4c Gemini CLI, 4d Copilot CLI | Optional |

## Part 0: Set up for the lab

The file `pre-work_downloads-installations_MacOS.md` gives the same steps with more information. If you did the pre-work, do only the checks in Part 0d.

### Part 0a: Install the software

This lab uses the software from Lab 1.

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Python 3.10 or newer | [python.org/downloads/macos](https://www.python.org/downloads/macos/) | [Using Python on macOS](https://docs.python.org/3/using/mac.html) | After the installation, open the Python folder in **Applications** and start **Install Certificates.command** |
| Docker Desktop (Apple silicon or Intel) | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) | [Install Docker Desktop on Mac](https://docs.docker.com/desktop/setup/install/mac-install/) | In **Settings, Resources**, set the memory limit to 8 GB or more. A Docker account is not necessary |

For Part 4 (optional), install the official CLIs. Lab 1, Part 5 tells you how. Some CLIs need Node.js 22 or newer ([nodejs.org/en/download](https://nodejs.org/en/download)).

### Part 0b: Get the files

**Pre-fetch script (to work without the internet).** The scripts [LAB02_MacOS_pre-fetch.sh](LAB02_MacOS_pre-fetch.sh), [LAB02_MacOS_pre-fetch.ps1](LAB02_MacOS_pre-fetch.ps1) and [LAB02_MacOS_pre-fetch.py](LAB02_MacOS_pre-fetch.py) in the `Lab02` folder download every file that this lab needs on macOS: installers, Python packages, models, Docker images and Ollama models. The files go into the folder `Downloads/MacOS` in the `Ai-workshop` folder. Files that are already there are skipped, so you can run a script again after an interruption. In Terminal, in the `Lab02` folder, do one of these commands:

```
bash LAB02_MacOS_pre-fetch.sh
python3 LAB02_MacOS_pre-fetch.py
```

Then follow [LAB02_MacOS_Benchmarking_Models_and_Harnesses_OFFLINE.md](LAB02_MacOS_Benchmarking_Models_and_Harnesses_OFFLINE.md) instead of this file. It installs everything from the downloaded files. To see what is missing first, add `--dry-run`. For the optional files, add `--optional`. For the NVIDIA GPU files, add `--gpu`. The script `LAB1-4_MacOS_pre-fetch` in the `Ai-workshop` folder downloads the files for Labs 1 to 4 together.

1. Get the lab files. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop). Extract it. Use the `Ai-workshop` folder. Put it in a folder that has no spaces in its path, for example `<HOME_DIR>/ai-workshop`.
2. This lab uses the Lab 1 models and Ollama. Do Lab 1, Part 0b first.
3. Start Docker Desktop. In the `Lab01` folder, start Ollama and download the second model from the [Ollama library](https://ollama.com/library/qwen3) (1.4 GB):

   ```
   docker compose --profile ollama up -d
   docker compose exec ollama ollama pull qwen3:1.7b
   ```

4. Optional (Part 2f): the Ministral 3 files from Lab 1, Part 0b, step 4.

### Part 0c: Configure

1. Use the virtual environment from Lab 1, Part 0c.
2. Optional (Part 3): use the key files from Lab 1, Part 3.

### Part 0d: Make sure that the setup is correct

1. In the `Lab01` folder, do `docker compose --profile ollama up -d`.
2. Do `docker compose exec ollama ollama list`. The list shows `qwen2.5:1.5b` and `qwen3:1.7b`.
3. In the `Lab02` folder, do `python3 bench.py run --only math --target ollama:qwen2.5:1.5b --no-warmup`. It shows one PASS or FAIL row.

### Part 0e (optional): GPU software

Install the GPU software from Lab 1, Part 0e. For Ollama on an NVIDIA GPU, use the `ollama-gpu` profile. Docker on macOS cannot use the GPU. For GPU speed, use the native Ollama app for macOS (https://ollama.com/download) and the KoboldCpp program.

### Part 0f: Before each session

Do these steps at the start of each session:

1. Open Terminal.
2. Go to the `Lab01` folder of the lab files.
3. Activate the virtual environment:

   ```
   source .venv/bin/activate
   ```

   The prompt shows `(.venv)` when the virtual environment is active. Activate it again in each new Terminal window.
4. Go to the `Lab02` folder. Keep the `Lab01` folder next to it.
5. Start Ollama. In the `Lab01` folder, do `docker compose --profile ollama up -d`. Then go back to the `Lab02` folder.

### Placeholders

Some commands contain placeholders. Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `/Users/jsmith` |

**About the GPU options.** All commands in this file are for a computer without a GPU. They use the CPU. Some commands have a "GPU option". Use a GPU option only if your computer has a GPU and you installed the GPU software (Part 0e). The answers stay almost the same. Only the speed changes.

## What the benchmark measures

The benchmark records these values for each prompt and for each session. A session is one run of all the prompts with one target.

| Value | Description |
|---|---|
| Prompt | The text that the harness sent, and the system prompt |
| Response | The full answer, and the result of its check (PASS or FAIL) |
| Operating time | The seconds from the request to the last token. The time that you use to type is not included. |
| Time to first token | The time until the answer starts |
| Output tokens per second | The speed of the answer after it starts |
| Input tokens | All prompt tokens that the model read, also the tokens from a cache |
| Output tokens | All tokens that the model wrote, also the reasoning tokens |
| Cache read tokens | Prompt tokens that the model used again from a cache |
| Cache write tokens | Prompt tokens that the model processed and kept in a cache |
| Reasoning tokens | The part of the output that the model used to think |

A dash (`-`) means "not reported". It does not mean zero. The field `token_source` tells you if the numbers are reported, counted or estimated.

## Part 1: Add measurements to the harness

The harness in `Lab01/harness.py` now records each model call. Open it in a text editor and find these parts:

1. The functions `run_turn` and `record_call`. `run_turn` records the time before the request, at the first token and at the last token. Then `record_call` makes one record with the prompt, the response, the times and the five token counts. The clock operates only inside `run_turn`. Thus, the time that you use to type is not included.
2. The dictionary `backend.usage` in each backend. Each backend fills the same five token fields.
3. The class `Session`. It adds the totals for the session and can write each record to a JSONL file.

Do these steps:

1. Go to the `Lab01` folder. Start a chat with measurements:

   ```
   python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --stats --log ../Lab02/results/chat.jsonl
   ```

   GPU option: add `--gpu-layers -1` to the command.

2. Ask two questions. Type `/stats`. Ask a third question. Type `/quit`.
3. Look at the line after each answer. It shows the tokens, the time and the speed.
4. Answer these questions in your workbook:
   - Why does "cache read" increase at the second question?
   - Why is the time to the first token shorter at the second question?
5. Do step 1 again with `--effort high`. Look at the reasoning tokens.
6. Go back to the `Lab02` folder.

Optional task: add a field `prefill_tok_per_s` to `record_call`. Calculate it as (input tokens minus cache read tokens) divided by the time to the first token.

## Part 2: Benchmark the harness and Ollama

The file `prompts.jsonl` has eight prompts. Each prompt has a check. Thus, the benchmark can give PASS or FAIL without a person. One prompt tests a tool call: the model must answer with the correct JSON request.

### Part 2a: The first run

1. Do this command:

   ```
   python3 bench.py run --target harness:../Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf --target ollama:qwen2.5:1.5b --live-html live.html
   ```

   GPU option: add `--gpu-layers -1` to the command. This applies only to the `harness:` targets.

2. Look at the live line during each prompt. It shows the time, the pieces received, the time to the first token and the speed.
3. Open `live.html` in your browser. The page updates every two seconds.
4. At the end, look at the summary table. It has one row for each target (one session).

### Part 2b: The default Lab 1 models

1. Do this command:

   ```
   python3 bench.py run --label cpu --live-html live.html \
     --target harness:../Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
     --target harness:../Lab01/models/qwen2.5-0.5b-instruct \
     --target harness:../Lab01/models/qwen2.5-0.5b-instruct-onnx \
     --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf \
     --target ollama:qwen2.5:1.5b
   ```

2. Compare the same 1.5B model in the harness and in Ollama. Which one is faster?
3. Compare the same 0.5B model as safetensors and as ONNX. Which one is faster? Do they give the same answers?

### Part 2c: Reasoning tokens

1. Do these commands:

   ```
   python3 bench.py run --label think --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --effort high
   python3 bench.py run --label think --target ollama:qwen3:1.7b --think true
   python3 bench.py run --label nothink --target ollama:qwen3:1.7b --think false
   ```

   GPU option: add `--gpu-layers -1` to the first command.

2. With high effort, does the model give the correct answer to the prompt `riddle`? How many reasoning tokens and seconds does high effort add to the easy prompts?

### Part 2d: Effectiveness

1. Make a report:

   ```
   python3 bench.py report results/*.jsonl --out report.html
   ```

2. Open `report.html`. Use these columns to compare the models:

| Column | Description | Better is |
|---|---|---|
| pass | Correct answers out of checked prompts | Higher |
| correct/min | Correct answers for each minute of operating time | Higher |
| tokens/correct | Tokens used for each correct answer | Lower |
| first token s, tok/s | Medians of the response time and the speed | Lower, higher |

3. Write one sentence in your workbook: which model do you select to help you write code, and which model for a fast yes or no classifier? Why?
4. To see how much the numbers change from run to run, add `--repeat 3` to a command.

### Part 2e: CPU and GPU

Do this part only if your computer has a GPU and you installed the GPU software (Lab 1, Part 0e).

1. Do the CPU run. `--ollama-num-gpu 0` keeps Ollama on the CPU:

   ```
   python3 bench.py run --label cpu --out results/cpu.jsonl --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --target ollama:qwen2.5:1.5b --ollama-num-gpu 0
   ```

2. Prepare Ollama for the GPU. Docker on macOS cannot use the GPU. For Ollama on the GPU, stop the Ollama container and start the native Ollama app (https://ollama.com/download). It uses the same port, 11434. Pull the models into it with `ollama pull qwen2.5:1.5b` and `ollama pull qwen3:1.7b`.
3. Do the GPU run:

   ```
   python3 bench.py run --label gpu --out results/gpu.jsonl --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --target ollama:qwen2.5:1.5b --gpu-layers -1
   ```

4. Compare the two runs:

   ```
   python3 bench.py compare results/cpu.jsonl results/gpu.jsonl
   python3 bench.py report results/cpu.jsonl results/gpu.jsonl --out cpu-vs-gpu.html
   ```

5. Look at the time to the first token and the speed (tok/s) separately. The pass column must stay almost the same.
6. Optional: do the GPU run again with `--gpu-layers 10` and with `--gpu-layers 20`. The speed increases with the number of layers on the GPU.

### Part 2f (optional): The optional Lab 1 models and runtimes

Do only the steps for the optional parts of Lab 1 that you did.

1. Ministral 3 (Lab 1, Part 1e):

   ```
   python3 bench.py run --label optional \
     --target harness:../Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf \
     --target harness:../Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf \
     --target ollama:hf.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF:UD-IQ2_XXS
   ```

   GPU option: add `--gpu-layers -1` to the command.

   Compare these models with the Qwen 1.5B model at 4 bits. The files are approximately the same size. Is a larger model at very low precision better than a smaller model at medium precision?

2. KoboldCpp and llama.cpp (Lab 1, Parts 4b and 4c). Use one runtime at a time. Stop Ollama first. In the `Lab01` folder, do the `docker compose` commands. In the `Lab02` folder, do the `bench.py` commands:

   ```
   docker compose --profile kobold up -d
   python3 bench.py run --label optional --target server:http://localhost:5001/v1#qwen
   docker compose --profile kobold down
   docker compose --profile llamacpp up -d
   python3 bench.py run --label optional --target server:http://localhost:8080/v1#qwen
   docker compose --profile llamacpp down
   ```

   GPU option: Docker on macOS cannot use the GPU. For GPU speed, use the native Ollama app for macOS (https://ollama.com/download) and the KoboldCpp program.

### Your own prompts

Add lines to `prompts.jsonl`. Each line is one prompt:

```
{"id": "port-ssh", "prompt": "Which TCP port does SSH use? Just the number.", "check": {"number": 22}}
```

The checks are `number`, `contains`, `contains_any`, `regex`, `json` and `max_sentences`. `--only id1,id2` runs only those prompts.

## Part 3 (optional): Benchmark the cloud APIs

Use the key files from Lab 1, Part 3. The file `bench_context.md` is a long system prompt. It makes the prompt cache visible. At the start, the benchmark shows the models that your key can use. Type the number of a model.

| Part | Command |
|---|---|
| 3a | `python3 bench.py run --label cloud --system-file bench_context.md --cache --key-file anthropic=<HOME_DIR>/.config/ai-keys/anthropic --target anthropic:` |
| 3b | `python3 bench.py run --label cloud --system-file bench_context.md --key-file openai=<HOME_DIR>/.config/ai-keys/openai --target openai:` |
| 3c | `python3 bench.py run --label cloud --system-file bench_context.md --key-file gemini=<HOME_DIR>/.config/ai-keys/gemini --target gemini:` |
| 3d | `python3 bench.py run --label cloud --system-file bench_context.md --key-file github=<HOME_DIR>/.config/ai-keys/github --target copilot:` |

Look for these items:

- Anthropic caches only the text that you mark. With `--cache`, the first prompt shows a cache write and the next prompts show a cache read.
- OpenAI and Gemini cache automatically. They report only the cache read.
- Reasoning models report reasoning tokens. You do not see the reasoning text.
- If GitHub Models refuses the long system prompt, do the command again without `--system-file`.

To calculate the cost, add `--price` to the `report` command. The value of `--price` is the target name from the report, then `=`, then the price for one million input tokens, a comma, and the price for one million output tokens. You can add the price for cache reads and the price for cache writes after two more commas. Use the current prices from the website of the provider.

## Part 4 (optional): Benchmark the official CLIs

Install and sign in to the CLIs first (Lab 1, Part 5). The benchmark starts each CLI in a new empty folder, in a read-only mode or a plan mode.

```
python3 bench.py run --label cli --target cli:claude --target cli:codex --target cli:gemini --target cli:copilot --raw
```

| Part | Target | Command that the benchmark uses |
|---|---|---|
| 4a | `cli:claude` | `claude -p PROMPT --output-format json --permission-mode plan` |
| 4b | `cli:codex` | `codex exec --json --sandbox read-only --skip-git-repo-check PROMPT` |
| 4c | `cli:gemini` | `gemini -p PROMPT --output-format json --approval-mode plan` |
| 4d | `cli:copilot` | `copilot -p PROMPT --output-format json` |

Look for these items:

- The input tokens are very high. Each CLI sends its own long system prompt and its list of tools. Most of these tokens are cache reads.
- The CLIs give the full answer at one time. Thus, there is no time to the first token.
- `--raw` keeps the raw output of each CLI in the results file. If a column shows `-`, examine the field `raw`.
- If a CLI waits for a sign-in or a permission, the benchmark stops it after 300 seconds (`--cli-timeout`).

## Checkpoint

- One results file with a minimum of two targets.
- The summary table.
- One sentence: the model that you select, and why.

When you are done, stop Ollama. In the `Lab01` folder, do `docker compose --profile ollama down`.
