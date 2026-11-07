# Workshop download scripts

Python 3.10 or newer (Lab 1 installs llama-cpp-python, gguf and numpy through pip). The scripts themselves need no extra packages. Works on Windows, macOS, and Linux. Keep this folder next to the `Lab01` folder: the scripts save models, the KoboldCpp program and the Ollama data where `Lab01` expects them (or pass `--dir`).

Install first: Docker Desktop (Docker Engine on Linux), VS Code, and Python 3. Start Docker and wait until it says it is running.

## Run them in this order

| Script | When to start it | What it fetches (about) |
| --- | --- | --- |
| `prefetch_lab1.py` | Before the workshop, or right away | Python packages (including PyTorch, CPU build), three small Part 1 models (GGUF, safetensors, ONNX, about 2.7 GB), Qwen3-4B (2.5 GB), and the Part 4 Docker images and model (Ollama, Open WebUI, KoboldCpp, llama.cpp, about 8 GB) |
| `prefetch_lab1images.py` | Optional, before the workshop | Lab 1 Part 2c image models: ViT recognizer (0.35 GB) and sd-turbo generator (2.6 GB) |
| `prefetch_lab2.py` | While Lab 1 runs | Lab 2 benchmark models in Ollama: qwen2.5:1.5b (1 GB) and qwen3:1.7b (1.4 GB) |
| `prefetch_lab3.py` | While Lab 2 runs | Continue extension for VS Code (the model comes from Lab 1) |
| `prefetch_lab4.py` | While Lab 3 runs | Open WebUI image (already part of `prefetch_lab1.py`) |
| `prefetch_lab5.py` | Any time | Surprise Bonus Lab: nothing to download (only checks that Docker is running) |
| `prefetch_lab6.py` | Before homework Lab 6 | Michael Nielsen's network code and the MNIST data (17 MB), into `Lab06` (extract `Lab06.zip` first) |
| `prefetch_lab7.py` | Before homework Lab 7 | The Lab 1 GGUF model to copy to a phone (already part of `prefetch_lab1.py`), plus a note for the phone apps |
| `prefetch_lab8.py` | Before homework Lab 8 | KoboldCpp program (0.6 GB), Hermes 3 3B (2 GB), Qwen 0.5B (0.4 GB), plus OpenClaw notes (not scripted) |
| `prefetch_lab9.py` | Before homework Lab 9 | An abliterated Qwen2.5 1.5B GGUF (about 1 GB) to compare with the Lab 1 model |
| `prefetch_lab1ministral.py` | Optional | Lab 1 Part 1e and Lab 2 Part 2f: Ministral 3 3B at about 1 GB (two GGUF files plus one in Ollama, 3.2 GB) |
| `prefetch_all.py` | At the start of the day | The five workshop labs, in order, about 15 GB |
| `prefetch_models.py` | When bandwidth is tight | Only the model files (the three Part 1 models, Qwen3-4B, Hermes 3 3B, Qwen 0.5B GGUF), about 7.5 GB |
| `prefetch_lab1bonus.py` | Only if you skipped them | Just the Lab 1 Part 4 Docker images and the Ollama model (they are already part of `prefetch_lab1.py`) |
| `prefetch_bonus.py` | At home | Benchmark models (3.2 GB), llama.cpp image, notes for the other bonus labs |

Commands: `python3 prefetch_lab1.py` on macOS and Linux, `py -3 prefetch_lab1.py` on Windows.

## What you see

An overall bar, one bar per download, and three lists: downloaded, in progress, and remaining. Docker image bars count layers. Model and file bars count bytes.

## Run it in the background

Open a second terminal and run the script there. Or add `--background`. It runs without a window and writes to `Lab01/prefetch/prefetch.log`. Check progress at any time:

```
python3 ai_prefetch.py --status --watch
```

## Good to know

- Run any script again to resume. Finished items are skipped, and partial files continue where they stopped.
- Files from Hugging Face are checked against the published sha256. A mismatch deletes the file.
- Use `--dry-run` to see sizes before you download. Use `--dir` to put the files somewhere other than the `Lab01` folder.
- Not scripted: OpenClaw, `toolcall_test.py`, Data Concierge, and the Intel Mac build of KoboldCpp. The script lists each one as manual.
- Bonus options: `--with-mistral` (needs 16 GB of RAM) and `--big` (qwen2.5:7b).
- The scripts were tested here with mock servers and a stand-in for Docker. Run the full set once on a clean Windows, macOS, and Linux machine before the event.
