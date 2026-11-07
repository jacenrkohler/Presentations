# Lab 3: Integrations and Tooling (Windows)

In this lab, you connect the harness to VS Code (Part 1). Then you give the harness a long-term memory in an Obsidian vault (Part 2).

Time in the workshop: 20 minutes.

| Part | What you do | Status |
|---|---|---|
| Part 0 | Set up for the lab | Do this before the workshop |
| Part 1 | Connect the harness to VS Code. A local model writes "Hello, World" in Python. | Required. 1d to 1f are optional |
| Part 2 | Obsidian as the memory of the harness | Optional |

## Part 0: Set up for the lab

The file `pre-work_downloads-installations_Windows.md` gives the same steps with more information. If you did the pre-work, do only the checks in Part 0d.

### Part 0a: Install the software

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Python 3.10 or newer (64-bit) | [python.org/downloads/windows](https://www.python.org/downloads/windows/) | [Using Python on Windows](https://docs.python.org/3/using/windows.html) | On the first screen of the installer, select **Add python.exe to PATH**. Then do this command one time: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| VS Code | [code.visualstudio.com/download](https://code.visualstudio.com/download) | [VS Code on Windows](https://code.visualstudio.com/docs/setup/windows) | On the **Additional tasks** screen, select **Add to PATH** |
| Continue extension for VS Code | [VS Code Marketplace: Continue](https://marketplace.visualstudio.com/items?itemName=Continue.continue), or `py -3 prefetch_lab3.py` | [Continue documentation](https://docs.continue.dev/) | Lab 3, Part 1b |
| Obsidian (optional, Lab 3, Part 2) | [obsidian.md/download](https://obsidian.md/download) | [Obsidian Help](https://help.obsidian.md/) | Make a vault with the name `AI Vault` in your `Documents` folder |
| Node.js 22 or newer (optional, for the CLIs and MCP) | [nodejs.org/en/download](https://nodejs.org/en/download) | [nodejs.org/en/download](https://nodejs.org/en/download) | None. To examine the version, do `node --version` |

For Part 1f and Part 2f (optional), install the official CLIs. Lab 1, Part 5 tells you how.

### Part 0b: Get the files

1. Get the lab files. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop). Extract it. Use the `Ai-workshop` folder. Put it in a folder that has no spaces in its path, for example `<HOME_DIR>\ai-workshop`.
2. Docker is not necessary for this lab.
3. In PowerShell, go to the `prefetch` folder and do this command:

   ```
   py -3 prefetch_lab3.py
   ```

   It downloads the Continue extension. The models come from Lab 1. If it stops, do the command again. It continues from the last file.

### Part 0c: Configure

1. Use the virtual environment from Lab 1, Part 0c.
2. Open VS Code. Click the Continue icon in the side bar one time. Continue makes its configuration file `<HOME_DIR>\.continue\config.yaml`. You change this file in Part 1b. A Continue account is not necessary.
3. Optional (Part 2): start Obsidian and make the vault `AI Vault` in `<HOME_DIR>\Documents\AI Vault`.
4. Optional (Parts 1e and 2e): use the key files from Lab 1, Part 3.

### Part 0d: Make sure that the setup is correct

1. Do `code --version`. It shows the version of VS Code.
2. In the `Lab01` folder, do `py -3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370`.
3. Open http://localhost:13370/v1/models. It shows one model.
4. Push Ctrl-C to stop the server.

### Part 0e (optional): GPU software

Install the GPU build of `llama-cpp-python` from Lab 1, Part 0e. Then add `--gpu-layers -1` to each `serve` command.

### Part 0f: Before each session

Do these steps at the start of each session:

1. Open PowerShell.
2. Go to the `Lab01` folder of the lab files.
3. Activate the virtual environment:

   ```
   .venv\Scripts\Activate.ps1
   ```

   The prompt shows `(.venv)` when the virtual environment is active. Activate it again in each new PowerShell window.

### Placeholders

Some commands contain placeholders. Replace each placeholder and its angle brackets with your value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` |
| `<HARNESS_PASSWORD>` | The one-time password that the harness shows when it starts with a cloud model |

**About the GPU options.** All commands in this file are for a computer without a GPU. They use the CPU. Some commands have a "GPU option". Use a GPU option only if your computer has a GPU and you installed the GPU software (Part 0e). The answers stay almost the same. Only the speed changes.

## Part 1: The harness in VS Code

The VS Code extension Continue can use any server that uses the OpenAI API. The harness has a `serve` command for this. Open `Lab01/harness.py` in a text editor and find these two changes:

1. The function `_completions` in `cmd_serve`. It accepts the older text completion API (`/v1/completions`), which some editor functions use.
2. The `usage` data in each answer. It shows the token cost of each request.

### Part 1a: Start the harness for VS Code

1. In the `Lab01` folder, do this command. Keep this window open.

   ```
   py -3 harness.py serve --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --port 13370 --stats --log ../lab3-vscode.jsonl --system "You are a coding assistant. Reply with code in one fenced block, then one short sentence."
   ```

   GPU option: add `--gpu-layers -1` to the command.

2. If Windows Defender Firewall asks about Python, allow it on Private networks only.

### Part 1b: Connect Continue

1. In VS Code, click the Continue icon in the side bar. Open the settings of Continue (the gear icon).
2. Open the file `config.yaml` (`<HOME_DIR>\.continue\config.yaml`). Add these lines:

   ```yaml
   models:
     - name: Lab harness
       provider: openai
       model: harness
       apiBase: http://localhost:13370/v1
       apiKey: none
       roles: [chat, edit]
   ```

3. Save the file. In the Continue panel, select **Lab harness**.

A local model accepts any API key. For a cloud model (Part 1e), replace `none` with `<HARNESS_PASSWORD>`.

### Part 1c: Write "Hello, World"

1. Make a new folder. Open it in VS Code. Make a file with the name `hello.py`.
2. In the Continue chat, type: *Write a Python program that prints "Hello, World!". Use a main function.*
3. Click **Apply** to put the code into `hello.py`. Save the file.
4. Open the terminal of VS Code. Do this command:

   ```
   py -3 hello.py
   ```

5. Select the code. Push Ctrl+I. Type: *Add a command-line option for the name to greet.*
6. Do the program again with a name:

   ```
   py -3 hello.py --name BSides
   ```

7. Look at the window of the harness. Count the requests from VS Code. Record the tokens of the request that wrote the code.

### Part 1d (optional): The other local models

1. Stop the server (Ctrl-C). Start it again with a different model. Continue does not need a change, because the address stays the same.

   ```
   py -3 harness.py serve --model models/qwen2.5-0.5b-instruct --port 13370 --stats
   py -3 harness.py serve --model models/qwen2.5-0.5b-instruct-onnx --port 13370 --stats
   py -3 harness.py serve --model models/Qwen3-4B-Q4_K_M.gguf --port 13370 --stats --effort low
   ```

   Use one command at a time. GPU option: add `--gpu-layers -1` to the command.

2. Ask each model for the same program. Which model wrote code that operated the first time? Which model was the fastest?

### Part 1e (optional): The cloud APIs through the harness

The harness keeps the key. Only your computer can connect to the server. The server asks for a one-time password.

1. Start one server:

   ```
   py -3 harness.py serve --backend anthropic --key-file <HOME_DIR>\.config\ai-keys\anthropic.txt --port 13370 --stats
   py -3 harness.py serve --backend openai --key-file <HOME_DIR>\.config\ai-keys\openai.txt --port 13370 --stats
   py -3 harness.py serve --backend gemini --key-file <HOME_DIR>\.config\ai-keys\gemini.txt --port 13370 --stats
   py -3 harness.py serve --backend copilot --key-file <HOME_DIR>\.config\ai-keys\github.txt --port 13370 --stats
   ```

   The harness shows a numbered list of models. Type the number of a model.

2. In the Continue configuration, set `apiKey` to `<HARNESS_PASSWORD>`.

**CAUTION:** Your code goes to the cloud provider. Do not open folders that contain secrets.

### Part 1f (optional): The official tools in VS Code

Open your hello-world folder in VS Code. Open the PowerShell terminal of VS Code. Start the CLI from Lab 1, Part 5. Keep its approval prompts on.

| Part | Tool | In VS Code |
|---|---|---|
| 1f-a | Claude Code | Type `claude` in the terminal. It offers to install its VS Code extension. Or type `/ide`. |
| 1f-b | OpenAI Codex | Type `codex` in the terminal, or install the Codex extension. |
| 1f-c | Gemini | Type `gemini` in the terminal, then `/ide install`. Or install the Gemini Code Assist extension. |
| 1f-d | GitHub Copilot | Type `copilot` in the terminal, or use Copilot Chat in VS Code (Agent mode). |

Ask each tool: *Write hello2.py that prints Hello, World! and run it.* Record each time that the tool asks for permission. The harness does not execute code. Continue applies the code, and you start it.

### Checkpoint

`hello.py`, written by a local model, operates correctly. You know the token count of the request that wrote it.

## Part 2 (optional): Obsidian as memory

A model forgets everything at the end of a conversation. A memory is a location where the harness keeps notes and finds them again. An Obsidian vault is a folder of Markdown files. You can open, read, edit and delete each note.

### Part 2a: Make the vault

1. Start Obsidian. Click **Create new vault**. Use the name `AI Vault`. Put it in your `Documents` folder: `<HOME_DIR>\Documents\AI Vault`. The commands in this part use this location.
2. Add a note with the name `Lab notes`. Write some facts in it, for example: *The workshop is BSidesDFW 2026. My best Lab 2 model was qwen2.5 1.5B.*

### Part 2b: The harness change

Open `Lab01/harness.py`. Find `MEMORY_PROMPT`, `memory_search`, `memory_write` and the `memory_` part of `run_tool`. With `--memory-dir`, the harness does these things:

- It adds three tools: `memory_search`, `memory_read` and `memory_write`.
- The model can read all notes in the vault. It can write only in the folder `AI Memory`.
- The harness refuses paths outside the vault.
- The harness does not read hidden folders, for example `.obsidian`.

### Part 2c: Use the memory

1. In the `Lab01` folder, do this command:

   ```
   py -3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --memory-dir "<HOME_DIR>\Documents\AI Vault" --approve --stats
   ```

   GPU option: add `--gpu-layers -1` to the command.

   `--approve` asks before each tool call. Type `y` for each call that you agree with.

2. Ask: *What was my best Lab 2 model?* The model must use `memory_search`.
3. Type: *Remember that Juice Shop runs on port 3000 in my lab.* The model must use `memory_write`.
4. Type `/quit`. Start the chat again. Ask: *Which port does Juice Shop use in my lab?*
5. In Obsidian, open the folder `AI Memory`. Read the note that the model wrote.

If a small model does not use a tool, use `--temperature 0.2`, or ask: *Use memory_search to find it.*

**CAUTION:** Memory can be an attack path. A note that contains instructions is an indirect prompt injection. It stays in the memory for all sessions. For this reason, the model can write in one folder only, you approve each tool call, and you can read each note.

### Part 2d (optional): The other local models

Do Part 2c again with `models/qwen2.5-1.5b-instruct-q4_k_m.gguf`, `models/qwen2.5-0.5b-instruct` and `models/qwen2.5-0.5b-instruct-onnx`. Count the correct answers to five memory questions for each model.

### Part 2e (optional): The cloud APIs through the harness

```
py -3 harness.py chat --backend anthropic --key-file <HOME_DIR>\.config\ai-keys\anthropic.txt --memory-dir "<HOME_DIR>\Documents\AI Vault" --approve
```

Use `openai`, `gemini` or `copilot` with their key files in the same way.

**CAUTION:** Each note that the model reads goes to the provider. Use a vault that does not contain private data.

### Part 2f (optional): The official CLIs with the same vault

The CLIs use an MCP server to get access to a folder. The official MCP filesystem server gives access to one folder only. It needs Node.js (`npx`).

| Part | CLI | Command |
|---|---|---|
| 2f-a | Claude Code | `claude mcp add vault -- npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>\Documents\AI Vault"` |
| 2f-b | Codex | `codex mcp add vault -- npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>\Documents\AI Vault"` |
| 2f-c | Gemini CLI | `gemini mcp add vault npx -y @modelcontextprotocol/server-filesystem "<HOME_DIR>\Documents\AI Vault"` |
| 2f-d | Copilot CLI | Start `copilot` and type `/mcp add`. Give `npx` as the command. Give `-y`, `@modelcontextprotocol/server-filesystem` and `"<HOME_DIR>\Documents\AI Vault"` as the arguments. |

These commands can change between versions. If a command does not operate, read the MCP documentation of the tool.

Then ask each CLI this question:

*Search my vault for my best Lab 2 model, and add a note to AI Memory/CLI.md that says which tool you are.*

Look at the permission prompts. In Obsidian, read what the CLI wrote. The filesystem server can write anywhere in the vault.

When you are done, remove the MCP server (for example `claude mcp remove vault`), or delete the configuration lines.
