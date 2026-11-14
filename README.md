# Marvin: Voice Assistant

> A terminal-based AI voice assistant for macOS and Windows. Say the wake word, speak a request, and Marvin answers aloud while using tools for email, calendar, files, notes, weather, web search, apps and the browser. It also keeps long-term memory about you.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Agent](https://img.shields.io/badge/Agent-LangGraph-green)
![LLM](https://img.shields.io/badge/LLM-Groq-orange)
![Memory](https://img.shields.io/badge/Memory-ChromaDB-purple)
![Platforms](https://img.shields.io/badge/Platforms-macOS%20%7C%20Windows-lightgrey)

**Final year group project** by Debajyoti, Totan Santra and Sayan Mete.

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
   - [Step 1: Install the tools](#step-1-install-the-tools)
   - [Step 2: Get the code](#step-2-get-the-code)
   - [Step 3: Install dependencies](#step-3-install-dependencies)
   - [Step 4: Add your Groq API key](#step-4-add-your-groq-api-key)
   - [Step 5: Connect Gmail and Calendar (optional)](#step-5-connect-gmail-and-calendar-optional)
   - [Step 6: Run Marvin](#step-6-run-marvin)
   - [Step 7: Make a one-word command (optional)](#step-7-make-a-one-word-command-optional)
4. [Permissions](#permissions)
5. [What You Can Say](#what-you-can-say)
6. [Tools Reference](#tools-reference)
7. [Configuration](#configuration)
8. [Project Structure](#project-structure)
9. [Working as a Team with Git](#working-as-a-team-with-git)
10. [Troubleshooting](#troubleshooting)
11. [Safety Design](#safety-design)
12. [Limitations and Future Work](#limitations-and-future-work)
13. [Authors](#authors)

---

## Features

| Area | Capability |
|---|---|
| Voice | Wake word "hey marvin", 5-second speech capture, speech-to-text, spoken replies |
| Text mode | The same agent without a microphone, for testing |
| Reasoning | LangGraph agent with tool calling and a fast path for simple commands |
| Memory | Long-term facts about the user in a local ChromaDB store |
| Conversation | Recent context saved in SQLite, trimmed to the last 20 messages |
| Email and calendar | Read unread Gmail, send email, list events, create events (with confirmation) |
| Notes and time | Save, read and delete notes; current date and time |
| Files | Create, read, write, append, rename, delete, list inside a sandboxed workspace |
| System | OS, CPU, RAM and disk report |
| Apps | Open and close approved applications |
| Browser | Open a site, search inside the default browser, read and summarize a web page |
| Weather | Current conditions and today's high and low for any city |
| Web | DuckDuckGo search for current facts |

---

## Architecture

![Marvin architecture diagram](diagram.png)

1. **Wake word.** `voice/audio.py` listens through the microphone using openWakeWord (`hey_marvin_v0.1`).
2. **Speech to text.** Five seconds of audio is sent to Groq's `whisper-large-v3-turbo`.
3. **Router.** `core/agent.py` answers simple requests ("what time is it", "save a note: ...", "read notes") directly, with no LLM call.
4. **Agent.** Everything else goes to `openai/gpt-oss-120b` on Groq, which picks tools, reads results and gives a short final answer.
5. **Confirmation.** Sending email, creating events and deleting notes pause for a spoken yes or no.
6. **Reply.** The answer is printed and spoken (`say` on macOS, built-in speech on Windows).

---

## Installation

Marvin runs on **macOS** and **Windows**. Do these steps once per computer. The Python version (3.14) is installed automatically by `uv`, so you do not need to install Python yourself.

### Step 1: Install the tools

**macOS (Terminal)**

```bash
brew install uv git portaudio
```

No Homebrew? Install it first from https://brew.sh.

**Windows (PowerShell)**

```powershell
winget install astral-sh.uv Git.Git
```

Close PowerShell and open a new window so the new commands are found.

### Step 2: Get the code

```bash
git clone https://github.com/Totan-Santra/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
```

Use a folder path without spaces to avoid editor and quoting problems.

### Step 3: Install dependencies

```bash
uv sync
```

This reads `pyproject.toml` and `uv.lock` and installs the exact versions the project was built with. The wake-word model is bundled inside the `openwakeword` package, so there is nothing else to download.

### Step 4: Add your Groq API key

Get a free key at https://console.groq.com, then create a file named `.env` in the project folder.

**macOS**

```bash
nano .env
```

**Windows**

```powershell
notepad .env
```

Write one line and save:

```env
GROQ_API_KEY=your_key_here
```

On macOS in `nano`, save with `Ctrl+O`, `Enter`, then exit with `Ctrl+X`. Never commit this file. It is already in `.gitignore`.

### Step 5: Connect Gmail and Calendar (optional)

Skip this step if you do not need email or calendar. Marvin works without it and will say the credentials are not set up.

**Part A: create the permission file (once per project)**

1. Open https://console.cloud.google.com and sign in with the Gmail account Marvin should use.
2. Click the project picker, then **New project**. Name it `Marvin` and click **Create**.
3. Open **APIs & Services**, then **Library**. Search for **Gmail API** and click **Enable**. Do the same for **Google Calendar API**.
4. Open **OAuth consent screen** (also called **Google Auth Platform**) and click **Get started**. Enter the app name `Marvin` and your email, and choose **External** as the audience.
5. Open **Audience**, find **Test users**, click **Add users**, and add the Gmail address you will log in with. Without this, Google blocks the login.
6. Open **Credentials**, click **Create credentials**, then **OAuth client ID**. Choose **Desktop app**, click **Create**, then **Download JSON**.

**Part B: place the file**

Rename the download to `credentials.json` and put it in the project folder, next to `main.py`.

```bash
# macOS example
mv ~/Downloads/client_secret*.json ~/FINAL-YEAR-PROJECT/credentials.json
```

Check that it is the right type. This should print `1`:

```bash
grep -c '"installed"' credentials.json
```

**Part C: first login**

Start Marvin (Step 6) and ask `any unread emails?`. A browser window opens:

1. Choose your Google account.
2. If Google says "hasn't verified this app", click **Advanced**, then **Go to Marvin (unsafe)**. This is normal for your own project.
3. Tick the Gmail and Calendar permissions and click **Continue**.

Marvin saves the login in `data/token.json`, so you will not be asked again on that computer. While the Google project stays in "Testing" status, the login expires after 7 days. If it stops working, delete `data/token.json` and log in again.

`credentials.json` and `token.json` are git-ignored. Copy `credentials.json` to each new computer by hand, and repeat Part C there.

### Step 6: Run Marvin

```bash
uv run python main.py --text    # typing mode: test this first
uv run python main.py           # voice mode: say "hey marvin"
```

In voice mode, wait for "Yes?" after the wake word, then speak. Say "goodbye", "stop listening", "exit" or "quit" to end, or press `Ctrl+C`.

Always start with `--text`. If it works but voice does not, the problem is the microphone or its permission, not the agent.

### Step 7: Make a one-word command (optional)

Type `marvin` from any folder instead of the long command. Change the folder name in the line if you cloned somewhere else.

**macOS**

```bash
echo 'marvin() { uv run --directory ~/FINAL-YEAR-PROJECT python main.py "$@"; }' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell)**

```powershell
if (!(Test-Path $PROFILE)) { New-Item -Path $PROFILE -Force }
notepad $PROFILE
```

Add this line, save, and open a new PowerShell window:

```powershell
function marvin { uv run --directory "$HOME\FINAL-YEAR-PROJECT" python main.py @args }
```

If PowerShell says scripts are disabled, run this once and reopen it:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then use `marvin` for voice mode and `marvin --text` for typing mode.

---

## Permissions

| System | Permission | When |
|---|---|---|
| macOS | Microphone access for Terminal | First voice run |
| macOS | Automation: "Terminal wants to control Safari" (or another app) | First time Marvin closes that app. Click **Allow** |
| Windows | Settings, Privacy and security, Microphone, allow desktop apps | First voice run |
| Both | Browser login to Google | First email or calendar request |

---

## What You Can Say

| You say | What happens |
|---|---|
| "What time is it?" | Instant answer, no LLM call |
| "Save a note: submit report on Friday" | Saves the note |
| "Read notes" | Reads all saved notes |
| "What's the weather in Kolkata?" | Current weather |
| "Any unread emails? Summarize by importance" | Reads and summarizes your inbox |
| "What's on my calendar tomorrow?" | Lists events |
| "Email Sam about the meeting" | Drafts, reads it back, waits for yes or no |
| "Remember that I study BCA" | Stores a lasting fact |
| "What do you know about me?" | Searches stored facts |
| "Open VS Code" / "Close Safari" | Opens or closes an approved app |
| "Open github.com" | Opens the site in your default browser |
| "Search for keyboards on Amazon" | Runs the search in your browser |
| "Summarize https://en.wikipedia.org/wiki/Alan_Turing" | Reads the page and summarizes it |
| "How much disk space is left?" | System report |
| "Create a file called todo.txt" | Creates it in the workspace |
| "Who built you?" | Names the team |

Replies are kept to two sentences by default. Say "in detail" for a longer answer.

---

## Tools Reference

| Tool | File | Purpose |
|---|---|---|
| `get_time`, `save_note`, `read_notes`, `delete_notes` | `tools/notes.py` | Date, time and notes (delete asks for confirmation) |
| `remember_facts`, `recall_facts` | `tools/memory_web.py` | Long-term memory in ChromaDB |
| `web_search` | `tools/memory_web.py` | DuckDuckGo search, top 4 results |
| `get_weather` | `tools/weather.py` | Current weather from wttr.in |
| `read_unread_emails`, `get_events`, `send_email`, `create_event` | `tools/google.py` | Gmail and Calendar (send and create ask for confirmation) |
| `file_manager` | `tools/files.py` | Sandboxed file operations in `data/workspace/` (`.txt`, `.py`, `.md`) |
| `system_info` | `tools/system.py` | OS, CPU, RAM, disk |
| `open_app`, `close_app` | `tools/apps.py` | Allow-listed app control |
| `open_website`, `search_in_browser`, `summarize_website` | `tools/browser.py` | Default browser actions and page reading |

**Apps Marvin can open**

| macOS | Windows |
|---|---|
| Safari, Chrome, VS Code, Calculator, Terminal, Notes, Finder | Chrome, VS Code, Calculator, Terminal, Notepad, Explorer |

**Apps Marvin can close**

| macOS | Windows |
|---|---|
| Safari, Chrome, VS Code, Calculator, Notes | Chrome, VS Code, Calculator, Notepad |

Terminal and Finder or Explorer are never closed, because closing the terminal would stop Marvin itself. App names are matched loosely, so "VS Code", "vscode" and "Visual Studio Code" all work. Closing sends a normal quit request, so apps with unsaved work will still ask you to save.

**Browser notes.** Opening and searching use your default browser. Summarizing fetches the page text in the background, since a browser window cannot be read by a program. It accepts only `http` and `https` links, refuses private network addresses, and reads at most 5,000 characters. Pages that need JavaScript to show their content may return nothing.

---

## Configuration

Edit `settings.py`:

| Setting | Meaning | Default |
|---|---|---|
| `ASSISTANT_NAME` | Name used in prompts and output | `Marvin` |
| `MODEL` | Groq model | `openai/gpt-oss-120b` |
| `MAX_MESSAGES` | Messages of context sent to the model | `20` |
| `WAKE_MODEL` | Wake-word model file | `hey_marvin_v0.1.onnx` |
| `WAKE_THRESHOLD` | Detection sensitivity (lower is more sensitive) | `0.4` |
| `DEFAULT_CITY` | City used when none is spoken | empty |

The assistant's personality and rules live in `SYSTEM_PROMPT` inside `core/agent.py`.

At run time Marvin creates a `data/` folder containing the notes file, conversation database, ChromaDB memory, Google token and the file workspace. It is git-ignored.

---

## Project Structure

```
FINAL-YEAR-PROJECT/
├── main.py                 Entry point: voice loop and text loop
├── settings.py             Names, paths, model and wake-word options
├── core/
│   └── agent.py            LangGraph agent, system prompt, router, confirmation loop
├── voice/
│   └── audio.py            Wake word, recording, transcription, speech output
├── tools/
│   ├── apps.py             Open and close approved apps
│   ├── browser.py          Open sites, browser search, page summarizing
│   ├── files.py            Sandboxed file manager
│   ├── google.py           Gmail and Google Calendar
│   ├── memory_web.py       Long-term memory and web search
│   ├── notes.py            Notes, date and time
│   ├── system.py           System information
│   ├── weather.py          Weather lookup
│   └── common.py           Shared helpers
├── diagram.png             Architecture diagram
├── pyproject.toml          Project metadata and dependencies (source of truth)
├── uv.lock                 Locked dependency versions
└── .python-version         Python version pin
```

---

## Working as a Team with Git

Several people push to the same repository, so always bring in the latest changes before pushing.

```bash
git pull --rebase
git push
```

If you see `rejected ... fetch first`, you skipped the pull. If Git reports a `CONFLICT`, two people edited the same lines. Open the named file, keep the correct version, then run `git add <file>` and `git rebase --continue`. If your commit only repeats work already on GitHub, `git rebase --skip` drops it.

Habits that prevent most problems:

- Keep one copy of the project per computer. Two copies drift apart.
- Run `git pull --rebase` before you start work, not only before you push.
- After pulling, run `uv sync` so dependencies match.
- Add packages with `uv add package-name` so `pyproject.toml` and `uv.lock` both update.
- Never commit `.env`, `credentials.json`, `token.json` or the `data/` folder.

---

## Troubleshooting

| Problem | Cause and fix |
|---|---|
| Editor Run button fails with a doubled path like `'"/Users/.../file.py"'` | The editor adds extra quotes around paths with spaces. Run from the terminal instead: `uv run python main.py` |
| `No module named ...` after cloning | Dependencies are not installed. Run `uv sync`. For a missing package, use `uv add package-name` |
| `GROQ_API_KEY` or authentication error | Check that `.env` is in the project root and contains the key with no quotes or spaces |
| `Updates were rejected ... fetch first` on push | Run `git pull --rebase`, then `git push` |
| Marvin says Gmail credentials are not set up | Complete Step 5. Confirm `credentials.json` is in the project root |
| Google shows "Access blocked" or error 403 | Add your address under OAuth consent screen, Audience, Test users |
| Google shows "API has not been used" | Enable both Gmail API and Google Calendar API in the project |
| Email worked last week, fails now | The 7-day Testing token expired. Run `rm data/token.json` (macOS) or `del data\token.json` (Windows) and log in again |
| No browser opens for Google login | Copy the link printed in the terminal into your browser |
| Marvin says an app is "not supported" | The app is not on the allow-list. Add it in `tools/apps.py` |
| Closing an app does nothing on macOS | Allow the Automation prompt, or enable it in System Settings, Privacy and Security, Automation |
| Wake word never triggers | Check microphone permission and the input device. Lower `WAKE_THRESHOLD` (for example `0.3`) |
| Wake word triggers by accident | Raise `WAKE_THRESHOLD` (for example `0.6`) |
| No sound on Windows | Check the default output device. Marvin uses the built-in Windows speech engine |
| PowerShell says running scripts is disabled | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once |
| Marvin repeats an old wrong answer | Old chat is stored. Delete `data/Marvin_database.db` to clear conversation history. Saved facts and notes are kept |
| Weather shows an error | The city name was not recognised, or wttr.in was unreachable. Try again with a full city name |

---

## Safety Design

- **Confirm before acting.** Sending email, creating events and deleting notes require explicit approval of the exact action.
- **Sandboxed files.** The file manager cannot read or write outside its workspace and will not overwrite existing files.
- **Allow-listed apps.** Only named applications can be opened or closed.
- **Prompt-injection guard.** Text from emails and web pages is treated as data, never as instructions.
- **Private network block.** The page summarizer refuses local and private addresses.
- **Bounded loops.** A recursion limit and a trimmed message window cap cost and runaway behaviour.
- **Secrets stay local.** `.env`, `credentials.json`, `token.json` and `data/` are git-ignored.

---

## Limitations and Future Work

- Recording lasts a fixed five seconds rather than stopping when you stop speaking.
- Speech recognition and the language model need an internet connection through Groq.
- Replies are two sentences by default, so detailed answers must be requested.
- Page summarizing cannot read pages that load their text with JavaScript.
- Ideas: voice activity detection, an offline model option, browser automation for clicking and typing, a wider tool set, automated tests.

---

## Authors

- **Totan Santra**
- **Sayan Mete**

Final Year Project

Repository: https://github.com/Totan-Santra/FINAL-YEAR-PROJECT
