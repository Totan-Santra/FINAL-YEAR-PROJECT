# Marvin: Voice Assistant (Final Year Project)

A Python voice assistant that runs from the terminal on macOS and Windows. It combines a language model, speech input and output, long-term memory, and a set of safe local tools.

## Features

- **Voice assistant:** speech in, spoken reply out (code in `voice/`)
- **Long-term memory:** stored locally in `Marvin_chroma/`
- **File manager tool:** create, read, write, append, rename, delete and list files, restricted to a `workspace/` folder
- **System info tool:** operating system, CPU, RAM and disk usage
- **App launcher tool:** opens approved apps on macOS and Windows

## Tools

### File manager
- Works only inside the `workspace/` folder. Paths that escape it are refused.
- Allowed file types: `.txt`, `.py`, `.md`
- Operations: `create`, `read`, `write`, `append`, `delete`, `list`, `rename`
- It will not overwrite an existing file with `create` or `write`. Use `append` instead.

### System info
Reports the operating system, architecture, processor, CPU usage, RAM total and available, and disk total and free space (uses `psutil`).

### App launcher
Opens apps from a fixed allow-list. Anything else is refused.

| macOS | Windows |
|---|---|
| Safari, Chrome, VS Code, Calculator, Terminal, Notes, Finder | Chrome, VS Code, Calculator, Terminal, Notepad, Explorer |

## Project structure

```
main.py             entry point
settings.py         names, paths and options
core/               assistant logic
tools/              file manager, system info, app launcher
voice/              speech input and output
Marvin_chroma/      local memory database
src/final_year_project/
pyproject.toml      project metadata
requirements.txt    dependencies
.python-version     Python version used
```

## Setup

macOS:

```bash
brew install uv portaudio git
git clone https://github.com/Totan-Santra/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
uv venv
uv pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
winget install astral-sh.uv Git.Git
git clone https://github.com/Totan-Santra/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
uv venv
uv pip install -r requirements.txt
```

Add any API keys the project needs to a `.env` file in the project folder. Never commit it.

## Run

```bash
python main.py
```

Allow microphone access for your terminal when asked.

## Privacy and safety

- File access is limited to `workspace/`.
- The app launcher only opens apps on its allow-list.
- Keep `.env`, API keys and `Marvin_chroma/` out of GitHub if they hold personal data.
