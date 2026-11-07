# Lab 2: Benchmarking Models and Harnesses

A benchmark runs the same prompts the same way against different models, settings, runtimes or hardware, and measures two things: **how good the answers are** and **what they cost** in time and tokens. In this lab you add measurements to your harness (Part 1), then build a benchmark that runs against the harness and Ollama, shows results live, and scores each model's effectiveness (Part 2). Optional parts measure the cloud APIs (Part 3) and the official CLIs (Part 4).

**Step-by-step walkthrough for your operating system** (each starts with Part 0, the setup for the lab):

- [Windows](LAB02_Windows_Benchmarking_Models_and_Harnesses.md)
- [macOS](LAB02_MacOS_Benchmarking_Models_and_Harnesses.md)
- [Linux](LAB02_Linux_Benchmarking_Models_and_Harnesses.md)

**Without the internet** (from a USB drive, or after you ran the pre-fetch script): [Windows](LAB02_Windows_Benchmarking_Models_and_Harnesses_OFFLINE.md) · [macOS](LAB02_MacOS_Benchmarking_Models_and_Harnesses_OFFLINE.md) · [Linux](LAB02_Linux_Benchmarking_Models_and_Harnesses_OFFLINE.md)

**Pre-fetch scripts** (download every file for this lab into `Downloads/<OS>`; each runs on any operating system): Windows: [.sh](LAB02_Windows_pre-fetch.sh) [.ps1](LAB02_Windows_pre-fetch.ps1) [.py](LAB02_Windows_pre-fetch.py) · macOS: [.sh](LAB02_MacOS_pre-fetch.sh) [.ps1](LAB02_MacOS_pre-fetch.ps1) [.py](LAB02_MacOS_pre-fetch.py) · Linux: [.sh](LAB02_Linux_pre-fetch.sh) [.ps1](LAB02_Linux_pre-fetch.ps1) [.py](LAB02_Linux_pre-fetch.py)

| Part | What you do | In the room? |
|---|---|---|
| [Part 1](#part-1-add-metrics-to-the-harness) | Add metrics to `harness.py`: time and tokens, per prompt and per session | Yes |
| [Part 2](#part-2-benchmark-the-harness-and-ollama) | `bench.py` against the harness and Ollama, live; effectiveness; CPU against GPU; 2f optional Lab 1 models | Yes (2f optional) |
| [Part 3](#part-3-optional-benchmark-the-cloud-apis) | Optional: 3a Anthropic, 3b OpenAI, 3c Gemini, 3d Copilot through the harness | Optional |
| [Part 4](#part-4-optional-benchmark-the-official-clis) | Optional: 4a Claude Code, 4b Codex, 4c Gemini CLI, 4d Copilot CLI | Optional |

Checkpoint: one results file with at least two targets, the summary table, and a sentence on which model you would choose and why.

**What you need:** everything from Lab 1 (the `Lab01` folder sits next to this `Lab02` folder), the Part 1 models, and Ollama from Lab 1 Part 4a. Run `python3 prefetch_lab2.py` for the Ollama models used here. No GPU is required; Part 2e shows how to compare CPU and GPU if you have one.

Files in this folder: `bench.py` (the benchmark), `prompts.jsonl` (the test prompts and their answer checks), `bench_context.md` (a long system prompt for the caching tests). On Windows use `py -3` in place of `python3`.

## What gets measured

For **every prompt** and for **every session** (one run of all the prompts against one target):

| Measure | What it means |
|---|---|
| Prompt sent | The exact text, plus the system prompt used |
| Response generated | The full reply, and whether it passed its check |
| Operating time | Seconds the model spent working, from sending the request to the last token. Time spent waiting for you (typing, or approving a tool call) is never counted |
| Time to first token | How long until the reply started (mostly prompt processing, plus loading the model on the first call) |
| Output tokens per second | Writing speed once the reply started |
| Input tokens | Every prompt token the model read, including any that came from a cache |
| Output tokens | Every token it wrote, including reasoning |
| Cache read tokens | Prompt tokens reused from a cache instead of being processed again |
| Cache write tokens | Prompt tokens processed and stored in a cache for next time |
| Reasoning tokens | The part of the output spent thinking (`<think>...</think>`, or as reported by the provider) |

Not every runtime reports every number. A `-` means "not reported", never zero. The `token_source` field in each record says whether numbers were **reported** by the provider, **counted** with the model's own tokenizer, or **estimated** (about four characters per token).

## Part 1. Add metrics to the harness

The Lab 1 harness streams replies but throws away everything it learns about them. Part 1 adds a record for every model call. Open `../Lab01/harness.py` and find these additions:

1. **`run_turn` and `record_call`.** `run_turn` notes the time before the request, when the first piece arrives, and when the last one arrives, then calls `record_call`, which builds one record: prompt, response, operating time, first-token time, tokens per second, and the five token counts. Because the clock only runs inside `run_turn`, your typing time and tool approvals (`input()` in the chat loop and in `turn_with_tools`) are never counted.
2. **`backend.usage` in every backend.** Each backend fills the same five fields its own way:
   - `LlamaCppBackend` renders the model's chat template, tokenizes it, and compares it with what is already in llama.cpp's KV cache. The shared beginning is the **cache read**; the rest is processed and stored (**cache write**). That is why the second question in a chat is faster than the first.
   - `TransformersBackend` and `OnnxBackend` count with the model's tokenizer. They rebuild the cache every turn, so cache read is always 0.
   - `OpenAICompatBackend` asks the server for usage (`stream_options: include_usage`) and also reads llama.cpp's `timings`.
   - `AnthropicBackend` reads `message_start` and `message_delta`. Anthropic's `input_tokens` does not include cached tokens, so the harness adds them back, to keep "input" meaning the same thing everywhere.
   - `GeminiBackend` reads `usageMetadata`, where thinking (`thoughtsTokenCount`) is counted outside the output; the harness adds it in, as OpenAI does.
   - Reasoning: local models are counted from the text between `<think>` and `</think>`.
3. **`Session`.** Collects the records, adds up per-session totals, and can append each record to a JSONL file.
4. **`serve`** now records its calls too, and returns OpenAI-style `usage` so Open WebUI and other clients can see token counts.

Try it:

```
cd ../Lab01
python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --stats --log ../Lab02/results/chat.jsonl
```

Ask two questions, then type `/stats`, then a third question, then `/quit`. After each reply you see a line like:

```
  [in 64 (cache read 0, write 64) | out 41 (reasoning 0) | 3.12 s, first token 0.84 s, 18.0 tok/s | cpu]
```

Answer in your workbook: why does **cache read** jump on the second question? Why is the first-token time shorter? Now try `--effort high` and look at **reasoning**.

GPU option: add `--gpu-layers -1` (needs the GPU build from Lab 1, Setup) and compare the line.

**Your turn (pick one):**

- Add a `prefill_tok_per_s` field to `record_call`: (input minus cache read) divided by the first-token time. Which model processes prompts fastest?
- Make `/stats` also print the slowest prompt of the session.
- Add `--log` support to `harness.py image` (Lab 1, Part 2c), recording seconds per image.

## Part 2. Benchmark the harness and Ollama

`bench.py` runs every prompt in `prompts.jsonl` against each target, checks the answer, and shows each result as it finishes. It imports `../Lab01/harness.py`, so the harness targets use exactly the metrics you just read.

The eight prompts cover arithmetic, a fact, strict formatting, JSON, a trick question, a security fact, a **tool call** (does the model answer with the right JSON tool request, as the harness expects?), and a short explanation. Each has a check, so the benchmark can score answers without a person reading them.

### Part 2a. Your first run, live

Start Ollama (Lab 1, Part 4a): `docker compose --profile ollama up -d` in the `Lab01` folder. Then, in this folder:

```
python3 bench.py run --target harness:../Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf --target ollama:qwen2.5:1.5b --live-html live.html
```

While it runs you see a live line (seconds, pieces received, time to first token, speed), then one row per prompt:

```
  math      PASS  in     58 out     4 cache r    52 w     6 reas     0 |   0.71 s | first  0.52 s |   21.0 tok/s
```

Open `live.html` in your browser: it reloads every two seconds with the results so far. At the end you get one summary row per target (the session) and the results file in `results/`.

### Part 2b. The default Lab 1 models

The models every attendee has from Lab 1: the three Part 1 models, Qwen3-4B, and the Part 4a Ollama model.

```
python3 bench.py run --label cpu --live-html live.html \
  --target harness:../Lab01/models/qwen2.5-1.5b-instruct-q4_k_m.gguf \
  --target harness:../Lab01/models/qwen2.5-0.5b-instruct \
  --target harness:../Lab01/models/qwen2.5-0.5b-instruct-onnx \
  --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf \
  --target ollama:qwen2.5:1.5b
```

(On Windows PowerShell, put it on one line or end lines with a backtick instead of `\`.) Same 1.5B model in the harness and in Ollama: which harness is faster? Same 0.5B model as safetensors and as ONNX: which runtime is faster, and do they get the same answers?

### Part 2c. Reasoning tokens

```
python3 bench.py run --label think --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --effort high
python3 bench.py run --label think --target ollama:qwen3:1.7b --think true
python3 bench.py run --label nothink --target ollama:qwen3:1.7b --think false
```

Does thinking fix the trick question (`riddle`)? What does it cost in reasoning tokens and seconds on the easy ones?

### Part 2d. Effectiveness: which model would you choose?

```
python3 bench.py report results/*.jsonl --out report.html
```

`report.html` has one row per session and one per prompt (click a row to see the prompt and the response). The columns that decide effectiveness:

| Column | Meaning | Better is |
|---|---|---|
| pass | Correct answers out of checked prompts | Higher |
| correct/min | Correct answers per minute of operating time: quality and speed together | Higher |
| tokens/correct | Input plus output tokens spent per correct answer: what each right answer costs | Lower |
| first token s, tok/s | Medians: how responsive it feels | Lower, higher |
| $ | Dollars, when you give prices (Part 3) | Lower |

A small model that is fast but often wrong can lose to a slower one on correct/min. Write one sentence in your workbook: which model would you run for a coding helper, and which for a quick yes/no classifier, and why?

Run `--repeat 3` to see how much the numbers move from run to run before you trust a small difference.

### Part 2e. With and without a GPU

Only if your laptop has a GPU and you installed the GPU builds (Lab 1, Setup). Run the same prompts twice, changing only the device, and give each run a label and its own file:

```
python3 bench.py run --label cpu --out results/cpu.jsonl --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --target ollama:qwen2.5:1.5b --ollama-num-gpu 0
python3 bench.py run --label gpu --out results/gpu.jsonl --target harness:../Lab01/models/Qwen3-4B-Q4_K_M.gguf --target ollama:qwen2.5:1.5b --gpu-layers -1
python3 bench.py compare results/cpu.jsonl results/gpu.jsonl
python3 bench.py report results/cpu.jsonl results/gpu.jsonl --out cpu-vs-gpu.html
```

- `--gpu-layers -1` puts harness models on the GPU; `0` (the default) keeps them on the CPU.
- `--ollama-num-gpu 0` forces Ollama onto the CPU; leaving it out lets Ollama use the GPU. Check with `docker compose exec ollama ollama ps` (the PROCESSOR column). On a Mac, use the native Ollama app for GPU runs (Docker on macOS cannot reach the GPU).
- `compare` prints the speedup of each run against the first. Look at first-token time (prompt processing) and tok/s (writing) separately: GPUs usually help both, but by different amounts.
- The pass column should not change much. If the GPU run gets different answers, why might that be? (Hint: GPU math rounds differently, and temperature 0 still picks between near-ties.)
- Try `--gpu-layers 10` and `20` too: partial offload shows how speed grows with the share of the model on the GPU.

### Part 2f (optional). The optional Lab 1 models and runtimes

Benchmark whatever optional parts of Lab 1 you did. Run only the lines for what you have.

**Ministral 3 at about 1 GB (Lab 1, Part 1e).** 3-billion-parameter models squeezed to 1 to 2 bits per weight:

```
python3 bench.py run --label optional \
  --target harness:../Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf \
  --target harness:../Lab01/models/Ministral-3-3B-Instruct-2512-UD-IQ1_M.gguf \
  --target ollama:hf.co/unsloth/Ministral-3-3B-Instruct-2512-GGUF:UD-IQ2_XXS
```

Compare them with the 1.5B Qwen at 4 bits, which is about the same size on disk: is a bigger model at very low precision better than a smaller one at moderate precision? If the harness reports an unknown architecture, your `llama-cpp-python` is older than Ministral 3 support; use the Ollama target (Ollama 0.13.1 or newer) or the llama.cpp container below instead.

**KoboldCpp and llama.cpp (Lab 1, Parts 4b and 4c).** Start one runtime at a time in the `Lab01` folder, benchmark it as a server, then stop it:

```
docker compose --profile kobold up -d
python3 bench.py run --label optional --target server:http://localhost:5001/v1#qwen
docker compose --profile kobold down

docker compose --profile llamacpp up -d
python3 bench.py run --label optional --target server:http://localhost:8080/v1#qwen
docker compose --profile llamacpp down
```

The same GGUF file now runs in four places (harness, Ollama, KoboldCpp, llama.cpp): which runtime is fastest on your laptop, and do they agree on the answers? llama.cpp reports cache reads and writes; KoboldCpp may report only estimated tokens (the `token_source` field says which). To benchmark Ministral 3 in llama.cpp, start it with `MODEL=Ministral-3-3B-Instruct-2512-UD-IQ2_XXS.gguf docker compose --profile llamacpp up -d`.

GPU option: use the `kobold-gpu` and `llamacpp-gpu` profiles (NVIDIA), and give the run `--label gpu`.

### Your own prompts

Add lines to `prompts.jsonl` (or make your own file and pass `--prompts`). Each line is one prompt:

```
{"id": "port-ssh", "prompt": "Which TCP port does SSH use? Just the number.", "check": {"number": 22}}
```

Checks: `number`, `contains` (all of a list), `contains_any`, `regex`, `json` (keys and values), `max_sentences`. Add `"system": "tools"` to use the harness's tool prompt. `--only id1,id2` runs a subset.

## Part 3 (optional). Benchmark the cloud APIs

The same benchmark against cloud models, through the harness. Use the key files from Lab 1, Part 3 (never put a key on the command line). Each run sends the eight prompts once, which costs a few cents or less.

To make **caching** visible, give a long, fixed system prompt with `--system-file bench_context.md` (about 1,500 tokens, above the providers' minimum for caching). The first prompt writes the cache and the next ones read it.

| Part | Command |
|---|---|
| 3a Anthropic | `python3 bench.py run --label cloud --system-file bench_context.md --cache --key-file anthropic=<HOME_DIR>/.config/ai-keys/anthropic --target anthropic:` |
| 3b OpenAI | `python3 bench.py run --label cloud --system-file bench_context.md --key-file openai=<HOME_DIR>/.config/ai-keys/openai --target openai:` |
| 3c Gemini | `python3 bench.py run --label cloud --system-file bench_context.md --key-file gemini=<HOME_DIR>/.config/ai-keys/gemini --target gemini:` |
| 3d Copilot | `python3 bench.py run --label cloud --system-file bench_context.md --key-file github=<HOME_DIR>/.config/ai-keys/github --target copilot:` |

At the start of each run, the benchmark shows the models your key can use, with numbers: type the number of the one to test.

What to look for:

- **Anthropic** caches only what you mark: with `--cache`, prompt 1 shows a **cache write** and later prompts a **cache read**. Without `--cache`, both stay 0.
- **OpenAI** and **Gemini** cache automatically and report **cache read** only (cache write shows `-`). Caching can take a request or two to appear.
- **Reasoning** appears for reasoning models (OpenAI's o-series and GPT-5 family, Gemini thinking models), even though you never see the thinking text.
- **Copilot** here means GitHub Models; its free tier has small per-request token limits, so if the long system prompt is refused, run without `--system-file`.

**Cost.** Add `--price` to the `report` command to see dollars per correct answer. Its value is the target name exactly as the report shows it, then `=`, then the input price and the output price in dollars per million tokens, separated by a comma (optionally followed by the cache-read and cache-write prices).

Copy the prices from the provider's pricing page on the day; they change. Compare a cloud model with your best local one on correct/min and on dollars per correct answer (local is $0 in API fees, but not in your time or electricity).

## Part 4 (optional). Benchmark the official CLIs

The CLIs from Lab 1, Bonus Part 5 can report their own usage in JSON. `bench.py` runs each prompt in a new, empty temporary folder with a read-only or plan mode, waits for the tool to finish, and reads the token counts from its output.

| Part | Target | What bench.py runs |
|---|---|---|
| 4a | `cli:claude` | `claude -p PROMPT --output-format json --permission-mode plan` |
| 4b | `cli:codex` | `codex exec --json --sandbox read-only --skip-git-repo-check PROMPT` |
| 4c | `cli:gemini` | `gemini -p PROMPT --output-format json --approval-mode plan` |
| 4d | `cli:copilot` | `copilot -p PROMPT --output-format json` |

```
python3 bench.py run --label cli --target cli:claude --target cli:codex --target cli:gemini --target cli:copilot --raw
```

Sign in to each CLI first (Lab 1, Part 5). `--raw` keeps each CLI's raw output in the results file, so you can check what it reported.

What to look for:

- **Input tokens are huge.** Each CLI sends its own long system prompt and tool list with every request, so a one-line question can cost thousands of input tokens. Most of it should show up as **cache read**, which is why agents are affordable.
- There is no first-token time or tok/s for CLIs: they return the whole answer at once, so only operating time is measured (and it includes the CLI starting up).
- Claude Code also reports its own cost estimate (`$` column).
- CLI output formats change between versions. Claude Code's fields are documented; for Codex, Gemini CLI and Copilot CLI, `bench.py` searches the JSON for token fields by name. If a column shows `-`, open the record's `raw` field to see what your version printed. If Copilot CLI does not support `--output-format json` in your version, you still get the answer and the time.
- If a CLI waits for a sign-in or a permission prompt, `bench.py` stops it after `--cli-timeout` seconds (default 300).

## Files

| File | What it is |
|---|---|
| `bench.py` | `run`, `report` and `compare` |
| `prompts.jsonl` | the prompts and their checks |
| `bench_context.md` | a long, fixed system prompt for the caching tests |
| `results/` | one JSONL file per run (created by `run`) |
| `../Lab01/harness.py` | the harness, with the Part 1 metrics |

## Placeholders

Replace each placeholder, including the angle brackets, with your own value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` (Windows), `/Users/jsmith` (macOS) or `/home/jsmith` (Linux) |
