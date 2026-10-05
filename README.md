# CONSOLE AI Chatbot

A modern dark-themed Streamlit AI chatbot powered by Google's Gemini API. It provides a polished chat experience with conversation memory, multiple model selection, streaming responses, Markdown/LaTeX rendering, code blocks, regeneration, and modular architecture for future tools.

## Features

- Real Gemini API integration — no fake/hard-coded AI responses
- Streaming model output
- Conversation memory in Streamlit session state
- New chat, chat switching, deletion and clearing
- Automatic conversation titles
- Gemini model selector
- API-key status indicator without exposing the key
- Markdown, code, tables and LaTeX support through Streamlit rendering
- Regenerate the latest response
- User-friendly API/quota/network/model error handling
- Responsive dark UI
- Modular code structure ready for search, files, voice, authentication, database persistence and tools

## Requirements

- Python 3.10+ recommended
- A Gemini API key from Google AI Studio / Gemini API
- Internet access for Gemini requests

## Installation

Open a terminal in this folder:

```bash
python -m venv .venv
```

Activate it:

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
.venv\Scripts\activate
```

### macOS/Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Gemini API key setup

The project includes `.streamlit/secrets.toml` as a template. Replace:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
```

with your real key.

Alternatively set an environment variable:

### Windows PowerShell

```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
```

### macOS/Linux

```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```

**Never commit a real API key.** `.streamlit/secrets.toml` is included in `.gitignore`.

## Run

```bash
streamlit run app.py
```

Streamlit will print a local URL, normally something similar to `http://localhost:8501`.

## Changing the AI model

The sidebar contains a model selector. The default list is defined in `modules/gemini.py`:

```python
DEFAULT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]
```

Add or remove model IDs there as your Gemini API access changes. If a model is unavailable to your API key, the app displays a friendly error instead of crashing.

## Project structure

```text
console-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   └── secrets.toml
└── modules/
    ├── __init__.py
    ├── gemini.py
    ├── chat_manager.py
    └── ui.py
```

### `app.py`
Application entry point. Coordinates Streamlit UI, conversations and Gemini streaming.

### `modules/gemini.py`
Gemini client, model configuration, system instruction, message conversion, streaming and error normalization.

### `modules/chat_manager.py`
Conversation/session-state operations. This abstraction makes it possible to replace session state with SQLite/PostgreSQL later.

### `modules/ui.py`
Reusable CSS and interface components.

## Troubleshooting

### API key missing

Make sure `GEMINI_API_KEY` exists in `.streamlit/secrets.toml` or the environment, then restart Streamlit.

### Invalid API key / permission error

Create/check the Gemini API key and make sure the selected model is available to that key/project.

### Quota exceeded

Wait for the quota window to reset or switch to a model with available quota.

### Model unavailable

Use the sidebar model selector. Model availability can vary by account, region, API version and service status.

### Streamlit command not found

Run the command through Python:

```bash
python -m streamlit run app.py
```

### Port already in use

```bash
streamlit run app.py --server.port 8502
```

## Architecture for future upgrades

The current app intentionally keeps provider logic, conversation management and UI separate. This makes it straightforward to add:

- Web search / grounding tools
- PDF/document upload and RAG
- Image input and vision
- Voice input and text-to-speech
- File generation
- Sandboxed code execution
- User authentication
- SQLite/PostgreSQL persistence
- Chat export to TXT/Markdown/PDF/DOCX
- Additional AI providers/models
- Conversation search
- Theme switching
- Image generation
- Gemini function/tool calling
- Agentic workflows

For autonomous or computer-control capabilities, add explicit per-action confirmation and a dedicated permission layer rather than granting unrestricted access.

## Security notes

- API keys are read from secrets/environment variables.
- The key is not displayed in the UI.
- Never commit `.streamlit/secrets.toml` containing a real key.
- Do not place API keys in client-side JavaScript.
- For a production deployment, add authentication, server-side rate limits, usage controls and persistent storage with appropriate access controls.
