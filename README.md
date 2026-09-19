# ☀️ Senior Daily Companion

An AI-powered step-by-step assistant designed for senior citizens (65+), built with Google Gemini and Streamlit.

## Features
- 🧓 Plain-language, single micro-step instructions tailored for seniors
- ⚠️ Automatic scam detection (money, passwords, gift card requests)
- 🔊 Read Out Loud button using Web Speech API
- 🖼️ Visual cues to help identify on-screen elements
- 🎨 High-contrast, large-font accessible UI

## Project Structure
```
senior_companion/
├── app.py              # Gemini AI backend
├── streamlit_app.py    # Streamlit frontend
├── requirements.txt    # Python dependencies
└── .gitignore
```

## Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/Shw-et-a/-Senior-Daily-Companion.git
cd -Senior-Daily-Companion
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key
```bash
# Windows PowerShell
$env:GEMINI_API_KEY = "your-api-key-here"

# macOS / Linux
export GEMINI_API_KEY="your-api-key-here"
```

Get your free API key at [https://aistudio.google.com](https://aistudio.google.com)

### 4. Run the app
```bash
streamlit run streamlit_app.py
```

Open your browser at **http://localhost:8501**

## Tech Stack
| Layer | Technology |
|---|---|
| AI Model | Google Gemini 2.5 Flash |
| Backend | Python + google-genai SDK |
| Frontend | Streamlit |
| Text-to-Speech | Web Speech API (browser-native) |
| API Server (optional) | FastAPI + Uvicorn |

## Deploy to Streamlit Cloud
1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `GEMINI_API_KEY` in Secrets
