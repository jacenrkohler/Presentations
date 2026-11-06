# Pre-work: Under the Hood of LLMs

BSidesDFW 2026 workshop, Saturday, November 7, 2026, Nedderman Hall, UTA. Please finish this before you arrive. The downloads are large (about 9 GB) and the venue Wi-Fi will not keep up with a room full of people.

## Part 1: Join the Discord

Start here: https://discord.gg/faGUQTCe

1. **Accept the Code of Conduct.** In the #code_of_conduct channel, react with a green check mark (✅) on the post: https://ptb.discord.com/channels/747866151547306084/794652112851566593
2. **Get the @ role.** In the #rules_n_access_ctrl channel, react with the cowperson emoji (🤠): https://ptb.discord.com/channels/747866151547306084/794697735454457887
3. **Find the workshop.** Open the **#==x_BSidesDFW_2026==$** category.
   1. Use the forum channel **2026_wkshp_underhood_llm_forum** for text conversation and file sharing.
   2. Remote attendees: use the voice channel **2026_wkshp_underhood_llm_forum** for voice and screen sharing.

## Part 2: Check your laptop

| You need | Notes |
|---|---|
| A laptop you can install software on | Windows, macOS, or Linux. No GPU needed. |
| 16 GB of RAM | The model uses about 3 GB while running. Close other heavy programs during the labs. |
| 20 GB of free disk space | About 9 GB of downloads, plus room for Docker. The optional bonus downloads add about 6 GB. |
| Admin rights | You will install Docker and VS Code. |

## Part 3: Install these first

1. **Python 3.10 or newer** (https://www.python.org/downloads/). On Windows, tick "Add Python to PATH". Check it: `python3 --version` (Windows: `py -3 --version`).
2. **Docker Desktop** (Docker Engine on Linux). Start it and wait until it says it is running. Used in Labs 1 (bonus), 2, and 5.
3. **VS Code** (https://code.visualstudio.com/). Used in homework Lab 6.
4. **A web browser** and a terminal you are comfortable using.

## Part 4: Get the lab files

Download the handout: **[add the link]**. Unzip it. You should see these folders: `lab1`, `labs`, `homework`, and `prefetch`.

Then install the Lab 1 packages from inside the `lab1` folder:

```
python3 -m pip install -r requirements.txt
```

On Windows, use `py -3` in place of `python3` in every command in this document.

## Part 5: Download the models and images

Open a terminal in the `prefetch` folder and run:

```
python3 prefetch_all.py
```

This downloads everything the five labs and the first homework lab need, in the order you will use them, about 9 GB. It shows progress bars, and you can run it again if it stops: finished items are skipped and partial files resume.

To run it hidden in the background and check on it later:

```
python3 prefetch_all.py --background
python3 ai_prefetch.py --status --watch
```

To see sizes first without downloading, add `--dry-run`. If your disk is tight, run `python3 prefetch_models.py` (models only, about 4.8 GB) now and the rest later.

### What gets downloaded

| Lab | What you do | Downloads (about) |
|---|---|---|
| Lab 1 | Open a model, build its harness | Python packages (llama-cpp-python, gguf, numpy) and the Qwen3-4B model, 2.5 GB |
| Lab 2 | Open WebUI, prompts, and logs | Open WebUI Docker image, 3.5 GB |
| Lab 3 | A second runtime and a tool-calling model | KoboldCpp (0.6 GB), Hermes 3 3B model (2 GB), Qwen 0.5B model (0.4 GB) |
| Lab 4 | Attack an agent, then add a control | OpenClaw (not scripted, see below) |
| Lab 5 | Make Gandalf give up the password | Nothing new. Uses a website, with Open WebUI as the backup. |
| Lab 6 (homework) | VS Code with a local model | Continue extension for VS Code, 50 MB |
| Lab 7 (homework) | Train your own tiny model | `python3 -m pip install numpy` |

If any step fails, run the script again, then ask in the Discord forum channel.

## Part 6: Things the scripts do not do

- **Lab 4 sandbox.** OpenClaw can read files and run commands. Do not run it in your everyday account. Set up a throwaway virtual machine or a separate user account, and put the lab files there. If you cannot, you can follow along from the instructor's demo. Setup notes for OpenClaw will be posted in the Discord forum channel.
- **`toolcall_test.py`** for Lab 3 comes from the handout. Copy it into the KoboldCpp folder when the lab starts.
- **Cloud model (optional).** Lab 1 lets you chat with a hosted model using your own API key (Anthropic, OpenAI, Gemini, or GitHub Models). If you want to, make a key just for the workshop, with a low spending limit, and delete it afterward. Never paste a key into Discord, a screenshot, or a slide. Read "Key safety" in `lab1/README.md` first. You can skip this step.
- **Lab 1 bonus (optional, about 6 GB).** Run `python3 prefetch_lab1bonus.py` to get the Ollama, llama.cpp, and KoboldCpp Docker images.
- **Gandalf (Lab 5).** Check that https://gandalf.lakera.ai loads from your network. It is a third-party site.

## Part 7: Suggested videos (optional, but they help)

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

How they connect to the day: the neuron and the weights are Lab 1 (you will read a real model's weights), gradient descent and backpropagation are what Lab 7 does in a minute on your laptop, and transformers, attention, and temperature are the "What is this?" talk.

## Part 8: Quick check before you come

- [ ] Joined the Discord, reacted ✅ and 🤠, and found the workshop forum channel
- [ ] Python 3.10 or newer, Docker Desktop (running), and VS Code installed
- [ ] `python3 prefetch_all.py` finished with nothing left in the "remaining" list
- [ ] Watched the three quick-primer videos (optional)
- [ ] Laptop charged, charger packed, and at least 20 GB of disk free
- [ ] Sandbox ready for Lab 4, or ready to watch the demo

## Questions

Ask in the 2026_wkshp_underhood_llm_forum channel in the Discord, or email [your email].
