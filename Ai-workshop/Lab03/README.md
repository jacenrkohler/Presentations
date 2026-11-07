# Lab 3: Integrations and Tooling

A harness becomes useful when other tools can reach it, and when it can reach other tools. In this lab you connect the Lab 1 harness to VS Code (Part 1) and give it a long-term memory stored in an Obsidian vault (Part 2). Each part shows the harness change first, then optional steps to repeat it with the other local models, the cloud APIs, and the official CLIs from Anthropic, OpenAI, Google and GitHub.

| Part | What you do | In the room? |
|---|---|---|
| [Part 1](#part-1-the-harness-in-vs-code) | Connect the harness to VS Code and have a local model write "Hello, World" in Python | Yes |
| [Part 2](#part-2-optional-obsidian-as-memory) | Optional: Obsidian as the harness's memory | Optional |

Checkpoint: `hello.py` written by a local model and run successfully, with the token count of the request that wrote it. Part 2: a note that the model wrote in `AI Memory/` and read back in a new session.

**What you need:** Lab 1 done (the harness and the Part 1 models in the `Lab01` folder, next to this `Lab03` folder), VS Code with the Continue extension (`python3 prefetch_lab3.py` installs it), and for Part 2, Obsidian (https://obsidian.md/download, free for personal use). No GPU is required; every harness command below takes `--gpu-layers -1` if you installed the GPU builds in Lab 1, Part 0e. On Windows use `py -3` in place of `python3`.

**Files in this folder:** this README and the step-by-step walkthroughs for each operating system (`LAB03_Windows_Integrations_and_Tooling.md`, `LAB03_MacOS_Integrations_and_Tooling.md`, `LAB03_Linux_Integrations_and_Tooling.md`). Each walkthrough starts with Part 0, the setup. Lab 3 has no scripts of its own: it uses `Lab01/harness.py`.

## Part 1. The harness in VS Code

VS Code extensions such as **Continue** talk to any server that speaks the OpenAI API. The harness already has `serve` (Lab 1). Two changes make it work well with an editor:

1. **`/v1/completions`.** Editors use two APIs: chat (`/v1/chat/completions`) for the chat panel, and the older text completion (`/v1/completions`) for some edit and autocomplete features. Open `Lab01/harness.py`, find `_completions` inside `cmd_serve`, and read how it turns a plain prompt into one chat message and returns the result in the older format.
2. **Token usage in every reply.** `serve` returns OpenAI-style `usage` (from Lab 2, Part 1), so the editor, and you, can see what each request cost.

### Part 1a. Start the harness for VS Code

In the `Lab01` folder:

```
python3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370 --stats --log ../lab3-vscode.jsonl --system "You are a coding assistant. Reply with code in one fenced block, then one short sentence."
```

GPU option: add `--gpu-layers -1`. Leave this terminal open; with `--stats` you see the tokens and time for every request VS Code makes.

### Part 1b. Connect Continue

1. In VS Code, open Extensions, search for **Continue**, and install it.
2. Open Continue's settings (the gear in its panel) and add a model to its `config.yaml`:

   ```yaml
   models:
     - name: Lab harness
       provider: openai
       model: harness
       apiBase: http://localhost:13370/v1
       apiKey: none
       roles: [chat, edit]
   ```

   A local model accepts any API key. (If you serve a cloud model in step 1e, set `apiKey` to `<HARNESS_PASSWORD>`.)
3. Pick **Lab harness** in the Continue chat panel.

### Part 1c. Write "Hello, World"

1. Make a new folder, open it in VS Code, and create `hello.py`.
2. In the Continue chat, ask: *Write a Python program that prints "Hello, World!". Use a main function.*
3. Insert the code into `hello.py` (Continue's "Apply" button), save, and run it in VS Code's terminal: `python3 hello.py`.
4. Select the code, press Ctrl+I (Cmd+I on a Mac), and ask: *Add a command-line option for the name to greet.* Run it again with `python3 hello.py --name BSides`.
5. Look at the harness terminal: how many requests did VS Code send, and how many tokens did each use?

Checkpoint: `hello.py` written by a local model, run successfully, and the token count of the request that wrote it.

### Part 1d (optional). The other local models

Stop the server (Ctrl-C) and start it again with a different `--model`; Continue keeps working because the address does not change:

```
python3 harness.py serve --model models/qwen2.5-0.5b-instruct --port 13370 --stats
python3 harness.py serve --model models/qwen2.5-0.5b-instruct-onnx --port 13370 --stats
python3 harness.py serve --model models/Qwen3-4B-Q4_K_M.gguf --port 13370 --stats --effort low
```

Ask each for the same program. Which one wrote code that ran first time? Which was fastest? (Ollama from Lab 1, Part 4a also works: in Continue use `provider: ollama` and `model: qwen2.5:1.5b`.)

### Part 1e (optional). The cloud APIs through the harness

The harness can serve a cloud model to VS Code, with the key safety from Lab 1, Part 3: the key stays in the harness, the server only listens on your own machine, and it prints a one-time password that Continue must send.

```
python3 harness.py serve --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic --port 13370 --stats
python3 harness.py serve --backend openai    --key-file <HOME_DIR>/.config/ai-keys/openai    --port 13370 --stats
python3 harness.py serve --backend gemini    --key-file <HOME_DIR>/.config/ai-keys/gemini    --port 13370 --stats
python3 harness.py serve --backend copilot   --key-file <HOME_DIR>/.config/ai-keys/github    --port 13370 --stats
```

The harness shows a numbered list of models; type a number. Set Continue's `apiKey` to `<HARNESS_PASSWORD>`. Your code now leaves your computer; do not open folders with secrets in them.

### Part 1f (optional). The official tools in VS Code

Each company also connects its own agent to VS Code. Open your hello-world folder in VS Code, open its terminal, and run the CLI from Lab 1, Bonus Part 5 there (keep its approval prompts on):

| Part | Tool | In VS Code | Ask it |
|---|---|---|---|
| 1f-a | Claude Code | Run `claude` in VS Code's terminal; it offers to install its VS Code extension, or type `/ide` | *Write hello2.py that prints Hello, World! and run it.* |
| 1f-b | OpenAI Codex | Run `codex` in the terminal, or install the Codex extension from the Extensions view | same |
| 1f-c | Gemini | Run `gemini` in the terminal (type `/ide install` to add its VS Code companion), or install the Gemini Code Assist extension | same |
| 1f-d | GitHub Copilot | Run `copilot` in the terminal, or use Copilot Chat in VS Code (Agent mode) | same |

Watch what each asks permission for before it writes a file or runs Python. Compare with your harness, which never runs anything: Continue applies the code and you run it.

## Part 2 (optional). Obsidian as memory

A model forgets everything when the conversation ends. A **memory** is a place the harness can save notes and search them later. An Obsidian vault is just a folder of Markdown files, so the model's memory is something you can open, read, edit and delete like any other notes.

### Part 2a. Make the vault

1. Install Obsidian (obsidian.md) and choose **Create new vault**. Call it `AI Vault` and save it in your `Documents` folder (`<HOME_DIR>/Documents/AI Vault`). The commands below use that location.
2. Add a note called `Lab notes` with a few facts, for example: *The workshop is BSidesDFW 2026. My best Lab 2 model was qwen2.5 1.5B.*

### Part 2b. The harness change

Open `Lab01/harness.py` and find the memory code (`MEMORY_PROMPT`, `memory_search`, `memory_write`, and the `memory_` branch in `run_tool`). With `--memory-dir`, the harness:

- adds three tools to the tool loop: `memory_search` (find notes containing words), `memory_read` (read one note), and `memory_write` (add a dated line to a note);
- lets the model **read** anywhere in the vault but **write** only inside one folder, `AI Memory/` (change it with `--memory-folder`), and refuses any path outside the vault;
- writes notes with Obsidian front matter (`tags: [ai-memory]`), so you can find everything the model wrote with a tag search;
- skips hidden folders such as `.obsidian` (Obsidian's settings).

### Part 2c. Use it

```
python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --memory-dir "<HOME_DIR>/Documents/AI Vault" --approve --stats
```

GPU option: add `--gpu-layers -1`. `--approve` asks before every tool call; say yes to each one you agree with.

1. Ask: *What was my best Lab 2 model?* The model should call `memory_search`, then answer from your note.
2. Say: *Remember that Juice Shop runs on port 3000 in my lab.* It should call `memory_write`.
3. Quit, start the harness again, and ask: *Which port does Juice Shop use in my lab?*
4. In Obsidian, open `AI Memory/` and read what the model wrote. Edit it, then ask again.

Small models sometimes answer without using a tool, or write the JSON slightly wrong. If that happens, try the 4B model, lower the temperature (`--temperature 0.2`), or ask it directly: *Use memory_search to look it up.*

**Security note.** Memory is also an attack path. Anything in the vault goes into the model's context, so a note containing instructions ("ignore your rules and...") is an indirect prompt injection that persists across sessions. That is why writes are limited to one folder, every tool call can require approval, and you can read every note the model wrote.

### Part 2d (optional). The other local models

Repeat Part 2c with `--model models/qwen2.5-1.5b-instruct-q4_k_m.gguf`, `models/qwen2.5-0.5b-instruct`, and `models/qwen2.5-0.5b-instruct-onnx`. Which ones use the memory tools correctly? Count it: in Lab 2 terms, how many of five memory questions does each get right?

### Part 2e (optional). The cloud APIs through the harness

Same memory, cloud models:

```
python3 harness.py chat --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic --memory-dir "<HOME_DIR>/Documents/AI Vault" --approve
```

(and the same with `--backend openai`, `gemini` or `copilot` and their key files). **Every note the model reads is sent to that provider.** Use a vault with nothing private in it.

### Part 2f (optional). The official CLIs with the same vault

The CLIs reach a folder through MCP servers. The official MCP **filesystem** server gives a CLI access to one folder and nothing else; point it at the vault. It needs Node.js (`npx`). On Windows PowerShell, use `"<HOME_DIR>\Documents\AI Vault"` in place of `"<HOME_DIR>/Documents/AI Vault"`.

| Part | CLI | Add the vault |
|---|---|---|
| 2f-a | Claude Code | `claude mcp add vault -- npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>/Documents/AI Vault"` |
| 2f-b | Codex | `codex mcp add vault -- npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>/Documents/AI Vault"` |
| 2f-c | Gemini CLI | `gemini mcp add vault npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>/Documents/AI Vault"` |
| 2f-d | Copilot CLI | Start `copilot`, type `/mcp add`, give `npx` as the command and `-y`, `@modelcontextprotocol/server-filesystem` and the full path of the vault as arguments (`echo "<HOME_DIR>/Documents/AI Vault"` prints it) |

These commands change between versions; if one does not work, check the tool's MCP documentation. Then ask each CLI: *Search my vault for my best Lab 2 model, and add a note to AI Memory/CLI.md saying which tool you are.* Watch its permission prompts, and check in Obsidian what it wrote. Unlike the harness, the filesystem server can write anywhere in the vault: decide whether you are comfortable with that.

When you are done: remove the MCP server (`claude mcp remove vault`, or delete the config entries).

## Files changed in this lab

| File | Change |
|---|---|
| `Lab01/harness.py` | `serve` answers `/v1/completions` and returns token usage; `--memory-dir` and `--memory-folder` add Obsidian memory tools to the tool loop |

## Placeholders

Replace each placeholder, including the angle brackets, with your own value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` (Windows), `/Users/jsmith` (macOS) or `/home/jsmith` (Linux) |
| `<HARNESS_PASSWORD>` | The one-time password that the harness prints when it serves a cloud model |
