# Lab 4: Logging and Compliance (Linux)

In this lab, the harness writes an audit log, sends it to a SIEM, and operates behind Open WebUI. Open WebUI controls which users can use which models.

Time in the workshop: 15 minutes.

| Part | What you do | Status |
|---|---|---|
| Part 0 | Set up for the lab | Do this before the workshop |
| Part 1 | A CSV log file for each session | Required |
| Part 2 | 2a: send the log to a SIEM with syslog. 2b JSON, 2c CEF, 2d LEEF, 2e compare | 2a required. 2b to 2e optional |
| Part 3 | 3a: Open WebUI in front of the harness: users, model access, logs. 3b Anthropic, 3c OpenAI, 3d Gemini, 3e Copilot | 3a required. 3b to 3e optional |

## Part 0: Set up for the lab

The file `pre-work_downloads-installations_Linux.md` gives the same steps with more information. If you did the pre-work, do only the checks in Part 0d.

### Part 0a: Install the software

| Software | Download | Installation instructions | Configuration |
|---|---|---|---|
| Python 3.10 or newer, pip and venv | Your package manager: `sudo apt install python3 python3-pip python3-venv` (Ubuntu, Debian) or `sudo dnf install python3 python3-pip` (Fedora) | [Using Python on Unix platforms](https://docs.python.org/3/using/unix.html) | None |
| Docker Engine and the Compose plugin | [Install Docker Engine](https://docs.docker.com/engine/install/) (select your distribution) | [Install Docker Engine](https://docs.docker.com/engine/install/) | Do `sudo usermod -aG docker $USER`, then sign out and sign in. See [Linux post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/) |

This lab also uses Open WebUI ([documentation](https://docs.openwebui.com/)) in Docker and the practice syslog listener `Lab04/syslog_listen.py`. For Part 2a with a real SIEM, your instructor gives you the address of the Security Onion server ([Security Onion documentation](https://docs.securityonion.net/)).

### Part 0b: Get the files

1. Get the lab files. Download [the ZIP file](https://github.com/jacenrkohler/Presentations/archive/refs/heads/main.zip) from [GitHub](https://github.com/jacenrkohler/Presentations/tree/main/Ai-workshop). Extract it. Use the `Ai-workshop` folder. Put it in a folder that has no spaces in its path, for example `<HOME_DIR>/ai-workshop`.
2. Start Docker.
3. In terminal, go to the `prefetch` folder and do this command:

   ```
   python3 prefetch_lab4.py
   ```

   It downloads the Open WebUI image. The models come from Lab 1. If it stops, do the command again. It continues from the last file.

### Part 0c: Configure

1. Use the virtual environment from Lab 1, Part 0c.
2. Use your Open WebUI admin account from Lab 1, Part 0c.
3. Firewall: If you use `ufw`, allow the ports of the harness from the Docker networks only:

   ```
   sudo ufw allow from 172.16.0.0/12 to any port 13370:13375 proto tcp
   ```

   With `firewalld`, add the Docker interface to a trusted zone. See [Docker and ufw](https://docs.docker.com/engine/network/packet-filtering-firewalls/).
4. The file `Lab01/compose.yaml` sets `ENABLE_FORWARD_USER_INFO_HEADERS=true` for Open WebUI. Do not change it. See [Open WebUI environment variables](https://docs.openwebui.com/getting-started/env-configuration/).
5. Optional (Parts 3b to 3e): use the key files from Lab 1, Part 3.

### Part 0d: Make sure that the setup is correct

1. In the `Lab04` folder, do `python3 syslog_listen.py`. It shows that it listens on port 13379. Push Ctrl-C.
2. In the `Lab01` folder, do `python3 harness.py ask --backend echo --log-dir ../logs "test"`. It makes the folder `logs` with one `.log` file.
3. Do `docker compose --profile webui up -d`. Open http://localhost:3000 and sign in with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`. Then do `docker compose --profile webui down`.

### Part 0e (optional): GPU software

Install the GPU build of `llama-cpp-python` from Lab 1, Part 0e. Then add `--gpu-layers -1` to each `serve` command.

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
| `<HARNESS_PASSWORD>` | The one-time password that the harness shows when it starts with a cloud model |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |
| `<ANALYST_EMAIL>` | The email that you give to the analyst user in Open WebUI |
| `<ANALYST_PASSWORD>` | The password that you give to the analyst user in Open WebUI |
| `<INTERN_EMAIL>` | The email that you give to the intern user in Open WebUI |
| `<INTERN_PASSWORD>` | The password that you give to the intern user in Open WebUI |
| `<SECURITY_ONION_IP>` | The IP address of the Security Onion server |
| `<DOCKER_BRIDGE_IP>` | The IP address of the Docker bridge (`docker0`) on your computer |

**About the GPU options.** All commands in this file are for a computer without a GPU. They use the CPU. Some commands have a "GPU option". Use a GPU option only if your computer has a GPU and you installed the GPU software (Part 0e). The answers stay almost the same. Only the speed changes.

## Part 1: A CSV log file for each session

### Part 1a: The harness change

Open `Lab01/harness.py` in a text editor. Find `CSV_FIELDS`, `flat_record`, `Session.open_csv` and `Session.add`. With `--log-dir FOLDER`, each session has its own file. The file name contains the date and the time when the session started, and the session ID. For example:

```
logs/harness-20261107-141502-3f9c2a1b.log
```

The file uses comma-separated values (CSV). It has one header row and one row for each model call.

| Columns | Contents |
|---|---|
| `prompt_time`, `response_time` | The date and time of the prompt and of the end of the response, to the millisecond, with the time zone |
| `session`, `turn`, `prompt_no` | The session, the model call and the prompt |
| `user`, `client` | The user who sent the prompt, and the address of the user |
| `backend`, `model`, `device` | The engine, the model, and CPU, GPU, server or cloud |
| `temperature` to `effort` | The settings |
| `prompt`, `response` | The full text |
| `operating_s` to `output_tok_per_s` | The Lab 2 times |
| `input_tokens` to `reasoning_tokens` | The five Lab 2 token counts |
| `token_source` | Reported, counted or estimated |

### Part 1b: Make log data

1. In the `Lab01` folder, do three sessions:

   ```
   python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs
   python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --effort high --log-dir ../logs
   python3 harness.py ask --model models/qwen2.5-0.5b-instruct-onnx --repeat 3 --log-dir ../logs "Write a one-line slogan for a bakery."
   ```

   GPU option: add `--gpu-layers -1` to the command.

2. In each chat, ask some questions. Include one question with a comma, a quotation mark and two lines. Type `/quit`.
3. Open the `logs` folder. Open one file in LibreOffice Calc. Open one file in a text editor.
4. Answer these questions in your workbook:
   1. Which response took the most time? Which model wrote it?
   2. Which session used the most tokens? How many were reasoning tokens?
   3. Is the question with a comma and two lines in one cell?
   4. A compliance officer asks for all prompts between two times. How do you find them in these files?
   5. This log contains all the text that you typed. Who can read it? How long must you keep it?

## Part 2: Send the log to a SIEM

A SIEM (security information and event management system) collects logs from many computers in one location. Syslog is a common way to send logs to a SIEM.

### Part 2a: Syslog to Security Onion

Open `Lab01/harness.py`. Find `SyslogSender`. With `--syslog HOST:PORT`, the harness sends each record as one syslog message (RFC 5424). UDP is the default. `--syslog-proto tcp` uses TCP. The harness cuts prompts and responses after 1,000 characters in syslog. The CSV file keeps the full text.

Security Onion is a SIEM. It is installed as its own operating system on a server or a virtual machine. It needs much more memory than a laptop that also does these labs. Use one of these two procedures:

- If your instructor gives you the address of a Security Onion server, send the log to that server.
- If there is no server, use the practice listener on your computer. It shows each message that a SIEM gets.

1. To use the practice listener, open a second terminal window. Activate the virtual environment. Go to the `Lab04` folder. Do this command:

   ```
   python3 syslog_listen.py
   ```

   It listens on port 13379 and writes all messages to `received.log`.

2. In the first window, in the `Lab01` folder, do this command:

   ```
   python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs --syslog 127.0.0.1:13379
   ```

   This command sends the log to the practice listener. To send the log to Security Onion, use this command:

   ```
   python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs --syslog <SECURITY_ONION_IP>:514
   ```

   GPU option: add `--gpu-layers -1` to the command.

3. Ask some questions. Look at the messages in the listener, or search for `llm-harness` in Security Onion (Hunt or Discover).
4. If no message arrives, examine the address and the port. Try `--syslog-proto tcp`. Make sure that the firewall of Security Onion accepts your computer.

### Parts 2b to 2d (optional): Structured formats

Plain syslog uses `key="value"` text. A SIEM must learn to read it. These formats make the fields available for search immediately. Do one session for each format:

| Part | Format | Add this to the command | Used by |
|---|---|---|---|
| 2b | JSON | `--syslog 127.0.0.1:13379 --syslog-format json` | Elastic, Splunk, most modern SIEMs |
| 2c | CEF (Common Event Format) | `--syslog 127.0.0.1:13379 --syslog-format cef` | ArcSight, many firewalls, Microsoft Sentinel |
| 2d | LEEF (Log Event Extended Format) | `--syslog 127.0.0.1:13379 --syslog-format leef` | IBM QRadar |

Read `SyslogSender.cef` and `SyslogSender.leef` in the harness:

- CEF has a fixed header and then `key=value` pairs. It has a fixed list of standard keys. Other data goes into numbered fields with labels, for example `cs1Label=model cs1=qwen...`.
- LEEF 2.0 has a similar header. You can select the delimiter (`^` here) and use your own attribute names.
- JSON uses the same names as the CSV columns.

### Part 2e (optional): Compare the formats

Send the same three prompts in each format. Then answer these questions in your workbook:

1. Which format lets you search by model or user without a custom parser?
2. Which format lost or changed data, for example cut text or escaped characters?
3. Which format is best for the SIEM of your organization? Why?

## Part 3: Open WebUI: users, models and logs

Open WebUI is a chat application for many users. It has accounts, groups, model access control and a chat history. The harness keeps its own log, with the name of the user.

### Part 3a: Open WebUI in front of the harness

Open `Lab01/harness.py`. Find `_who` in `cmd_serve`. Open WebUI can send the name, the email and the role of the user in request headers (`X-OpenWebUI-User-...`). The file `Lab01/compose.yaml` turns this on with `ENABLE_FORWARD_USER_INFO_HEADERS`. The harness writes this user into the `user` column of its log and into syslog.

1. Start two harness servers, one model in each. Use two terminal windows, in the `Lab01` folder:

   ```
   python3 harness.py serve --model models/Qwen3-4B-Q4_K_M.gguf --host 0.0.0.0 --port 13370 --served-name qwen3-4b --log-dir ../logs
   python3 harness.py serve --model models/qwen2.5-0.5b-instruct-onnx --host 0.0.0.0 --port 13371 --served-name qwen-0.5b --log-dir ../logs
   ```

   GPU option: add `--gpu-layers -1` to the command. To send these logs to the SIEM, add `--syslog` from Part 2. If you use a firewall, allow TCP ports 13370 to 13375 from the Docker network only (see the pre-work file, step 3).

2. Start Open WebUI. In the `Lab01` folder, do `docker compose --profile webui up -d`. Open http://localhost:3000. Sign in with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`.
3. In the **Admin Panel**, go to **Settings, Connections**. Add two OpenAI-compatible connections:
   - `http://host.docker.internal:13370/v1`
   - `http://host.docker.internal:13371/v1`

   Type any text as the key.
4. In the **Admin Panel**, go to **Users**. Add two users with the role *user*: `<ANALYST_EMAIL>` with `<ANALYST_PASSWORD>`, and `<INTERN_EMAIL>` with `<INTERN_PASSWORD>`. Go to **Groups**. Make a group with the name `analysts`. Put only the analyst in it.
5. In the **Admin Panel**, go to **Settings, Models**. Open `qwen3-4b`. Make it **private** and give access to the group `analysts`. Keep `qwen-0.5b` available to all users. (The names of the menus can change between versions of Open WebUI.)
6. Open a private browser window. Sign in as `<INTERN_EMAIL>`. Only `qwen-0.5b` must be visible. Sign in as `<ANALYST_EMAIL>`. The two models must be visible. Ask one question as each user. Use a vague prompt, then a structured prompt (role, task, format).
7. Compare these four records:
   - The harness CSV in `logs`. The `user` column must show the email and the role of each user.
   - The chat history in Open WebUI. As admin, you can see the chats of a user in **Admin Panel, Users**, if admin chat access is on.
   - The audit log of Open WebUI, if your version supports `AUDIT_LOG_LEVEL`: `docker compose exec webui tail -n 5 /app/backend/data/audit.log`
   - The log of the container: `docker compose logs webui`
8. Answer these questions in your workbook:
   1. Which record shows who asked what? Which record shows the answer? Which record can a user delete?
   2. The intern finds the address of port 13370 and sends requests to it directly. What stops the intern? What does the log show?

Open WebUI controls access to its own menu. It does not control access to the server behind it. The address `127.0.0.1` and the passwords of the harness protect the server.

### Parts 3b to 3e (optional): Open WebUI with the cloud models

There are two procedures. The difference is important for compliance.

**Procedure 1: direct connection.** In **Admin Panel, Settings, Connections**, add an OpenAI-compatible connection with the address of the provider and your key (see the table). Open WebUI keeps your key in its database. The harness log does not see these requests.

| Part | Provider | Connection address | Key |
|---|---|---|---|
| 3b | Anthropic | `https://api.anthropic.com/v1` | `<ANTHROPIC_API_KEY>` |
| 3c | OpenAI | `https://api.openai.com/v1` | `<OPENAI_API_KEY>` |
| 3d | Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `<GEMINI_API_KEY>` |
| 3e | Copilot (GitHub Models) | `https://models.github.ai/inference` | `<GITHUB_TOKEN>` |

**Procedure 2: through the harness.** The harness keeps the key, records each request with the name of the user, and asks for a one-time password.

1. Start one server for each provider, each on its own port:

   ```
   python3 harness.py serve --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic --port 13372 --log-dir ../logs
   ```

   The harness shows a numbered list of models. Type the number of a model. Use `--backend openai`, `gemini` or `copilot` with their key files for Parts 3c to 3e. Use ports 13373, 13374 and 13375.

On Linux, add `--host <DOCKER_BRIDGE_IP>` to the command. This is the address of the Docker bridge. Only containers on your computer can connect to it. To see the address, do `ip -4 addr show docker0`.

2. In Open WebUI, add the connection `http://host.docker.internal:13372/v1` (on Linux: `http://<DOCKER_BRIDGE_IP>:13372/v1`). Use `<HARNESS_PASSWORD>` as the key.
3. Make the model private. Give access only to the group `analysts`.
4. Send one prompt as the analyst. Find the request in each record.
5. Answer these questions in your workbook: With procedure 1, where is the only record of the use of the cloud model? With procedure 2, what does the harness log add? What new item can fail?

**CAUTION:** Each prompt to a cloud model goes to the provider. The provider keeps its own logs. Use test data only.

## Checkpoint

- One `.log` file from a session.
- One record that a syslog server received.
- A note or a screenshot that shows that a restricted user cannot see a model.

When you are done, stop the containers. In the `Lab01` folder, do `docker compose --profile webui down`. Stop the harness servers and the listener with Ctrl-C.
