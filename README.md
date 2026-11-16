# Marvin: AI Voice & Text Assistant

Marvin is an AI assistant built as a final year B.Tech project. It understands text and voice commands, remembers things about the user, and uses tools to get real work done, such as reading emails, checking the weather, saving notes, searching the web and opening apps.

## Features

- **Text and voice modes**: chat in the terminal, or talk to Marvin using the wake word "Hey Marvin".
- **Tool calling**: the LLM decides when to call a tool, and the tool result is turned into a short answer.
- **Gmail and Google Calendar**: read unread emails, send emails, view and create events. Sending and creating always ask the user to confirm first.
- **Weather**: current weather for any city.
- **Notes and time**: save and read notes, get the current time.
- **Long-term memory**: remembers lasting personal facts and recalls them later (ChromaDB).
- **Web search and browser**: search the web, open websites, summarize web pages.
- **Files, system and apps**: file operations, system actions and opening applications.
- **Conversation history**: chats are saved in SQLite, so Marvin continues where you left off.

## Tech Stack

| Part | Technology |
|------|------------|
| Language | Python |
| Agent framework | LangGraph, LangChain |
| LLM | `openai/gpt-oss-120b` on Groq |
| Conversation storage | SQLite (LangGraph `SqliteSaver`) |
| Long-term memory | ChromaDB |
| Wake word | `hey_marvin` (ONNX model) |
| Google services | Gmail API, Google Calendar API |
| Package manager | uv |

## Project Structure

```
FINAL-YEAR-PROJECT/
├── core/              # Agent logic (LangGraph graph, router, system prompt)
├── tools/             # Tools: google, weather, notes, memory_web, files, system, apps, browser
├── voice/             # Wake word, speech-to-text and text-to-speech
├── Marvin_chroma/     # Vector database for long-term memory
├── src/final_year_project/
├── main.py            # Entry point
├── settings.py        # Model name, paths, wake word, limits
├── Base.ipynb         # Notebook for experiments
├── pyproject.toml
├── requirements.txt
└── uv.lock
```

## How It Works

1. The user sends a message by text or voice.
2. A **router** handles simple commands directly (time, save note, read notes).
3. Everything else goes to the **LLM**, which can call tools.
4. A **tool node** runs the chosen tool and sends the result back to the LLM.
5. The LLM gives a short final answer.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Totan-Santra/FINAL-YEAR-PROJECT.git
cd FINAL-YEAR-PROJECT
```

### 2. Install dependencies

```bash
uv sync
```

or with pip:

```bash
pip install -r requirements.txt
```

### 3. Add your API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
```

### 4. Set up Google access (for Gmail and Calendar)

1. Create a project in Google Cloud Console and enable the **Gmail API** and **Google Calendar API**.
2. Create OAuth credentials (Desktop app) and download them as `credentials.json`.
3. Place `credentials.json` in the project root.
4. Add your Google account as a **Test user** on the OAuth consent screen.
5. The first run opens a browser for login and creates `data/token.json`.

## Usage

Text mode:

```bash
uv run main.py --text
```

Voice mode:

```bash
uv run main.py
```

Type `exit` to quit text mode.

### Example commands

- `read my unread emails`
- `what is the weather in Kolkata`
- `save a note: submit project report`
- `what time is it`
- `open youtube`
- `summarize this page: <link>`

## Troubleshooting

**Marvin keeps repeating an old wrong answer or does not call a tool.**
Old conversation history is saved in `data/Marvin_database.db`. If a wrong reply was saved earlier, the model may repeat it. Rename or delete this file (a new one is created automatically), or use a new `thread_id`.

## Authors

- **Sayan Mete**
- **Totan Santra**

## Acknowledgements

Built with LangGraph, LangChain, Groq, ChromaDB and the Google APIs.
