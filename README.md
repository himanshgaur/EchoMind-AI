# ⚡ EchoMind AI — Meeting & Video Intelligence

Turn any meeting recording, audio file, or YouTube video into actionable intelligence. Get instant executive summaries, key decisions, action item assignments, and chat interactively with your transcript using a Retrieval-Augmented Generation (RAG) pipeline.

---

## 🌟 Key Features

- **Multi-Source Ingestion**: Input YouTube video URLs or upload audio/video files directly (`.mp3`, `.wav`, `.m4a`, `.mp4`, `.webm`).
- **Dual Engine Transcription**:
  - **Local Whisper (English)**: Offline, privacy-conscious transcription.
  - **Sarvam AI (Hinglish)**: Speech-to-text with English translation for Indian multilingual contexts.
- **Structured Intelligence Dashboard**:
  - 📋 **Executive Summaries**: High-level digest with bullet points.
  - ✅ **Action Items**: Tasks with assigned owners and deadlines.
  - 🔑 **Key Decisions**: Strategic milestones and agreed takeaways.
  - ❓ **Open Questions**: Unresolved topics and follow-ups.
- **💬 Interactive Meeting Chat (RAG)**: Chat directly with the meeting transcript powered by Chroma vector database and Mistral AI.
- **📱 Responsive UI**: Beautiful dark glassmorphic design optimized for both desktop and mobile screens.
- **💾 Report Export**: Download complete reports in Markdown or Plain Text.

---

## 🚀 Quickstart (Local Development)

### 1. Clone the Repository
```bash
git clone https://github.com/himanshgaur/EchoMind-AI.git
cd EchoMind-AI
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r Requirements.txt
```

*Note: Ensure `ffmpeg` is installed on your system:*
- **Windows**: `choco install ffmpeg` or `winget install Gyan.FFmpeg`
- **macOS**: `brew install ffmpeg`
- **Ubuntu/Debian**: `sudo apt install ffmpeg`

### 3. Configure API Keys
Create a `.env` file in the root folder:
```env
MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=ministral-3b-latest
SARVAM_API_KEY=your_sarvam_api_key
SARVAM_STT_MODEL=saaras:v3
WHISPER_MODEL=small
```

### 4. Run the Streamlit App
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ☁️ Deployment on Streamlit Community Cloud

1. Fork or push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and click **New App**.
3. Select your repository `himanshgaur/EchoMind-AI` and main file path `app.py`.
4. Under **Advanced Settings > Secrets**, configure:
   ```toml
   MISTRAL_API_KEY = "your_key"
   MISTRAL_MODEL = "ministral-3b-latest"
   SARVAM_API_KEY = "your_key"
   SARVAM_STT_MODEL = "saaras:v3"
   WHISPER_MODEL = "small"
   ```
5. Click **Deploy!**
