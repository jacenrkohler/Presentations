# Lab 4: Logging and Compliance

If an AI system is used at work, someone will ask: who asked it what, when, with which model, what did it answer, and what did it cost? In this lab the harness writes its own audit log (Part 1), sends it to a SIEM over syslog (Part 2), and sits behind Open WebUI, where you control which users can use which models and compare what each layer records (Part 3).

**Step-by-step walkthrough for your operating system** (each starts with Part 0, the setup for the lab):

- [Windows](LAB04_Windows_Logging_and_Compliance.md)
- [macOS](LAB04_MacOS_Logging_and_Compliance.md)
- [Linux](LAB04_Linux_Logging_and_Compliance.md)

| Part | What you do | In the room? |
|---|---|---|
| [Part 1](#part-1-a-csv-log-for-every-session) | A date-stamped CSV `.log` file for every harness session | Yes |
| [Part 2](#part-2-send-the-log-to-a-siem-over-syslog) | 2a send it over syslog to Security Onion (or the practice listener); optional 2b JSON, 2c CEF, 2d LEEF, 2e compare them in the SIEM | Yes (2b to 2e optional) |
| [Part 3](#part-3-open-webui-users-models-and-logs) | 3a Open WebUI in front of the harness: users, model access, and logs; optional 3b Anthropic, 3c OpenAI, 3d Gemini, 3e Copilot | Yes (3b to 3e optional) |

Checkpoint: one session `.log` file, one record received by a syslog server, and a screenshot or note showing that a restricted user cannot see a model.

What you need: Lab 1 (the harness, the Part 1 models, and Open WebUI from Part 4a) and Lab 2 (the metrics). No GPU is required; every harness command takes `--gpu-layers -1` if you installed the GPU builds in Lab 1, Part 0e. On Windows use `py -3` in place of `python3`. 

**Files in this folder:** this README, `syslog_listen.py` (the practice syslog listener), and the walkthroughs for each operating system. The harness is in `Lab01`.

## Part 1. A CSV log for every session

### Part 1a. The harness change

Open `Lab01/harness.py` and find the Lab 4 logging code (`CSV_FIELDS`, `flat_record`, and `Session.open_csv` and `Session.add`). With `--log-dir FOLDER`, every session gets its own file, named with the date and time it started and the session id:

```
logs/harness-20261107-141502-3f9c2a1b.log
```

The file is comma-separated values with one header row, and one row per model call:

| Column | What it holds |
|---|---|
| `prompt_time`, `response_time` | When the prompt was sent and the response finished, to the millisecond, with the time zone |
| `session`, `turn`, `prompt_no` | Which session, which model call, which prompt (a tool loop can make several calls per prompt) |
| `user`, `client` | Who submitted the prompt (your login name for `chat` and `ask`; the signed-in Open WebUI user for `serve`, Part 3) and from which address |
| `backend`, `model`, `device` | The engine, the model, and CPU, GPU, server or cloud |
| `temperature` to `effort` | The settings used |
| `prompt`, `response` | The full text |
| `operating_s`, `first_token_s`, `generate_s`, `output_tok_per_s` | The Lab 2 timings (your typing time is never counted) |
| `input_tokens` to `reasoning_tokens` | The five Lab 2 token counts |
| `token_source` | Whether the counts were reported, counted or estimated |

Commas, quotes and line breaks inside prompts and responses are quoted the CSV way, so spreadsheets and SIEMs read the file correctly.

### Part 1b. Run some sessions

In the `Lab01` folder, run at least three sessions with different models and settings:

```
python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs
python3 harness.py chat --model models/Qwen3-4B-Q4_K_M.gguf --effort high --log-dir ../logs
python3 harness.py ask  --model models/qwen2.5-0.5b-instruct-onnx --repeat 3 --log-dir ../logs "Write a one-line slogan for a bakery."
```

GPU option: add `--gpu-layers -1`. In each chat, ask a few questions, including one with a comma, a quote and a line break in it (paste two lines), then `/quit`.

Open the `logs` folder. Open one file in a spreadsheet (Excel, LibreOffice or Google Sheets) and one in a text editor.

Answer in your workbook:

1. How long did your longest response take, and which model wrote it?
2. Which session used the most tokens? How many were reasoning tokens?
3. Did the prompt with a comma and a line break stay in one cell?
4. A compliance officer asks for every prompt you sent between two times. How would you answer from these files?
5. This log contains everything you typed. Who should be allowed to read it, and how long should it be kept?

## Part 2. Send the log to a SIEM over syslog

A local file is easy to delete or forget. A SIEM (security information and event management) system collects logs from many machines in one place, keeps them, and lets analysts search them. Syslog is the oldest common way to send them.

### Part 2a. Syslog to Security Onion

**The harness change.** Find `SyslogSender` in `Lab01/harness.py`. With `--syslog HOST:PORT`, every record (the same fields as the CSV) is also sent as one RFC 5424 syslog message: facility `local0`, severity informational, app name `llm-harness`. UDP is the default; `--syslog-proto tcp` uses TCP with RFC 6587 octet counting. Prompts and responses longer than 1,000 characters are cut in syslog (the full text stays in the CSV), because many syslog servers drop very long UDP messages.

**About Security Onion.** Security Onion is a free, open SIEM and network monitoring platform. It runs its parts in Docker containers, but it is installed as its own operating system (from its ISO, in a virtual machine or on a server), not as a single container you can start on a laptop, and it needs far more memory than a 16 GB laptop can spare alongside these labs. Check the current hardware requirements at securityonion.net before you plan.

So there are two ways to do this part:

- **With the workshop's Security Onion server**, if your instructor provides one. Your instructor allows your network to send syslog to it (in Security Onion, by adding it to the syslog firewall host group) and gives you its address and a login for its web console.
- **With the practice listener** on your own laptop, if there is no server. It prints and saves whatever arrives, so you can see exactly what a SIEM would receive.

Practice listener (in a second terminal, in the `Lab04` folder):

```
python3 syslog_listen.py
```

It listens on port 13379 (UDP and TCP) on your own machine and saves everything to `received.log`.

Send a session (in the `Lab01` folder):

```
python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs --syslog 127.0.0.1:13379
```

That sends to the practice listener. For the workshop's Security Onion, use:

```
python3 harness.py chat --model models/qwen2.5-1.5b-instruct-q4_k_m.gguf --log-dir ../logs --syslog <SECURITY_ONION_IP>:514
```

In Security Onion, open the web console, go to Hunt or Discover, and search for `llm-harness`. If nothing arrives: check the address and port, try `--syslog-proto tcp`, and check that your machine is allowed through Security Onion's firewall.

GPU option: add `--gpu-layers -1`.

### Parts 2b to 2d (optional). Structured formats

Plain syslog is `key="value"` text that a SIEM has to be taught to read. Three common structured formats make the fields searchable right away. Run one session per format, with the listener or Security Onion running:

| Part | Format | Command (add your `--model`) | Used by |
|---|---|---|---|
| 2b | JSON | `--syslog 127.0.0.1:13379 --syslog-format json` | Elastic, Splunk, most modern SIEMs |
| 2c | CEF (Common Event Format) | `--syslog 127.0.0.1:13379 --syslog-format cef` | ArcSight, many firewalls, Microsoft Sentinel |
| 2d | LEEF (Log Event Extended Format) | `--syslog 127.0.0.1:13379 --syslog-format leef` | IBM QRadar |

Read `SyslogSender.cef` and `SyslogSender.leef` in the harness:

- **CEF** has a fixed header (`CEF:0|vendor|product|version|event id|name|severity|`) and then `key=value` extensions. It has a fixed list of standard keys (`rt` for time, `suser` for user, `src` for address), so custom data goes into numbered slots with labels: `cs1Label=model cs1=qwen...`, `cn1Label=inputTokens cn1=58`. Pipes in the header and `=` in values must be escaped with a backslash.
- **LEEF 2.0** has a similar header, but you name the delimiter yourself (`^` here) and may use your own attribute names (`model=`, `inputTokens=`), next to standard ones (`usrName`, `devTime`).
- **JSON** keeps the CSV column names exactly.

### Part 2e (optional). Compare them in the SIEM

Send the same three prompts in each format (plain, JSON, CEF, LEEF) to Security Onion or the listener. Then, in your workbook:

1. Which format could you search by model or user without writing a parser?
2. Which one lost or changed information (for example, cut text, or a pipe or equals sign that had to be escaped)?
3. Which would you choose for your organization's SIEM, and why?

## Part 3. Open WebUI: users, models and logs

Open WebUI is a multi-user chat app. Put it in front of the harness and you get accounts, groups, model access control, and its own chat history, while the harness keeps its own log with the user's name in it.

### Part 3a. Open WebUI in front of the harness

**The harness change.** Find `_who` in `cmd_serve` in `Lab01/harness.py`. Open WebUI can forward the signed-in user in request headers (`X-OpenWebUI-User-Email`, `-Name` and `-Role`); the Lab 1 `compose.yaml` turns this on with `ENABLE_FORWARD_USER_INFO_HEADERS`. The harness writes that user into the `user` column of its log, and syslog. Without the header, the log says `unknown (no user header)`.

1. Start two harness servers, one model each, with logging (two terminals, in the `Lab01` folder):

   ```
   python3 harness.py serve --model models/Qwen3-4B-Q4_K_M.gguf --host 0.0.0.0 --port 13370 --served-name qwen3-4b --log-dir ../logs
   python3 harness.py serve --model models/qwen2.5-0.5b-instruct-onnx --host 0.0.0.0 --port 13371 --served-name qwen-0.5b --log-dir ../logs
   ```

   GPU option: add `--gpu-layers -1`. Add `--syslog ...` from Part 2 to send these to the SIEM too.
2. Start Open WebUI (`docker compose --profile webui up -d` in the `Lab01` folder; if you changed `compose.yaml`, this recreates the container) and open http://localhost:3000. Sign in with `<ADMIN_EMAIL>` and `<ADMIN_PASSWORD>`.
3. In the **Admin Panel**, under **Settings, Connections**, add two OpenAI-compatible connections: `http://host.docker.internal:13370/v1` and `http://host.docker.internal:13371/v1`, each with any text as the key.
4. **Users and groups.** In the Admin Panel, under **Users**, add two users with role *user*: `<ANALYST_EMAIL>` / `<ANALYST_PASSWORD>` and `<INTERN_EMAIL>` / `<INTERN_PASSWORD>`. Under **Groups**, make a group `analysts` and put only the analyst in it.
5. **Restrict a model.** In the Admin Panel, under **Settings, Models**, open `qwen3-4b`, make it **private**, and give the `analysts` group access. Leave `qwen-0.5b` available to everyone. (Menu names change between Open WebUI versions; look for model visibility or access control.)
6. **Test it.** In a private browser window, sign in as `<INTERN_EMAIL>`: you should see only `qwen-0.5b`. Sign in as `<ANALYST_EMAIL>`: you should see both. Ask a question as each. Try a vague prompt and then a structured one (role, task, format), so the log has something to compare.
7. **Inspect the logs.** Compare four places:
   - the harness CSV in `logs/` (the `user` column should show each person's email and role);
   - Open WebUI's chat history (as admin, in the Admin Panel, under Users, you can view a user's chats if admin chat access is on);
   - Open WebUI's audit log, if your version supports `AUDIT_LOG_LEVEL` (turned on in `compose.yaml`): `docker compose exec webui tail -n 5 /app/backend/data/audit.log`;
   - `docker compose logs webui`, the container's own log.

Answer in your workbook: which place recorded who asked what, which recorded the model's answer, and which could a user delete? If the intern found the harness address (port 13370) and called it directly, what would stop them using the restricted model, and what would the log show? (Hint: Open WebUI controls access to its own menu, not to the server behind it. Part 3 of Lab 1's key safety rules, and binding servers to `127.0.0.1`, are what protect the server itself.)

### Parts 3b to 3e (optional). Open WebUI with the cloud models

There are two ways to add a cloud model to Open WebUI, and the difference matters for compliance.

**Way 1: directly.** In the Admin Panel, under **Settings, Connections**, add an OpenAI-compatible connection with the provider's address and your key. Open WebUI then calls the provider itself. Your key is stored in Open WebUI's database, and the harness log sees nothing.

| Part | Provider | Connection address | Key |
|---|---|---|---|
| 3b | Anthropic | `https://api.anthropic.com/v1` (Anthropic's OpenAI-compatible endpoint) | `<ANTHROPIC_API_KEY>` |
| 3c | OpenAI | `https://api.openai.com/v1` | `<OPENAI_API_KEY>` |
| 3d | Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `<GEMINI_API_KEY>` |
| 3e | Copilot (GitHub Models) | `https://models.github.ai/inference` | `<GITHUB_TOKEN>` (Models: read) |

**Way 2: through the harness.** The harness serves the cloud model, keeps the key in its own memory, logs every request with the user's name, and requires a one-time password. On macOS and Windows (Docker Desktop):

```
python3 harness.py serve --backend anthropic --key-file <HOME_DIR>/.config/ai-keys/anthropic --port 13372 --log-dir ../logs
```

On Linux, add `--host <DOCKER_BRIDGE_IP>` (Docker's bridge, reachable only from containers on your machine) and use `http://<DOCKER_BRIDGE_IP>:13372/v1` as the connection address. The harness shows a numbered list of models; type a number. Use `--backend openai`, `gemini` or `copilot` with their key files for 3c to 3e, on ports 13373, 13374 and 13375. In Open WebUI, add the connection `http://host.docker.internal:13372/v1` with `<HARNESS_PASSWORD>` as the key.

For each provider you try: restrict the model to the `analysts` group, send one prompt as the analyst, and find the request in each log. Then answer: with Way 1, where is the only record of who used the cloud model? With Way 2, what does the harness log add, and what new thing could fail?

**Data note.** Every prompt to a cloud model leaves your computer, and the provider keeps its own logs under its own retention policy. Use test data only.

## Files changed in this lab

| File | Change |
|---|---|
| `Lab01/harness.py` | `--log-dir` (CSV `.log` per session), `--syslog`, `--syslog-proto`, `--syslog-format` (plain, json, cef, leef); `serve` records the Open WebUI user; cloud models may be served on Docker's bridge address on Linux |
| `Lab01/compose.yaml` | Open WebUI forwards user headers and writes an audit log |
| `Lab04/syslog_listen.py` | a practice syslog receiver |

## Placeholders

Replace each placeholder, including the angle brackets, with your own value.

| Placeholder | Your value |
|---|---|
| `<HOME_DIR>` | The full path of your home folder, for example `C:\Users\jsmith` (Windows), `/Users/jsmith` (macOS) or `/home/jsmith` (Linux) |
| `<ANTHROPIC_API_KEY>` | Your Anthropic API key |
| `<OPENAI_API_KEY>` | Your OpenAI API key |
| `<GEMINI_API_KEY>` | Your Gemini API key |
| `<GITHUB_TOKEN>` | Your GitHub fine-grained personal access token |
| `<HARNESS_PASSWORD>` | The one-time password that the harness prints when it serves a cloud model |
| `<ADMIN_EMAIL>` | The email of your Open WebUI admin account |
| `<ADMIN_PASSWORD>` | The password of your Open WebUI admin account |
| `<ANALYST_EMAIL>` | The email you give the analyst user in Open WebUI |
| `<ANALYST_PASSWORD>` | The password you give the analyst user |
| `<INTERN_EMAIL>` | The email you give the intern user in Open WebUI |
| `<INTERN_PASSWORD>` | The password you give the intern user |
| `<SECURITY_ONION_IP>` | The IP address of the workshop's Security Onion server |
| `<DOCKER_BRIDGE_IP>` | The IP address of Docker's bridge on Linux (`ip -4 addr show docker0`) |
