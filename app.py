import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Synchronize Streamlit Community Cloud secrets into os.environ
try:
    if hasattr(st, "secrets"):
        for sec_key, sec_val in st.secrets.items():
            if isinstance(sec_val, str) and sec_key not in os.environ:
                os.environ[sec_key] = sec_val
except Exception:
    pass

from utils.audio_processor import process_input, save_uploaded_file
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import extract_action_items, extract_key_decisions, extract_questions
from core.rag_engine import build_rag_chain, ask_question

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EchoMind AI | Meeting & Video Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom responsive CSS with dark glassmorphism theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Overall Background and Text */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }

    /* Gradient Title Banner */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
        margin-bottom: 0.25rem;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.98rem;
        margin-bottom: 1.5rem;
    }

    /* Glassmorphic Cards */
    .glass-card {
        background: rgba(22, 27, 34, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.5);
    }

    /* Badge Pills */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.18); color: #93c5fd; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-purple { background: rgba(168, 85, 247, 0.18); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-emerald { background: rgba(16, 185, 129, 0.18); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-amber { background: rgba(245, 158, 11, 0.18); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); }

    /* Custom Streamlit Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 8px 8px 0 0;
        font-weight: 600;
        font-size: 0.88rem;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(99, 102, 241, 0.15) !important;
        color: #a5b4fc !important;
        border-bottom: 2px solid #818cf8 !important;
    }

    /* Buttons Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }

    /* Chat Messages styling */
    .stChatMessage {
        background: rgba(30, 41, 59, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        margin-bottom: 0.75rem !important;
    }

    /* Mobile Responsive Queries */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 1.65rem;
        }
        .glass-card {
            padding: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 6px 10px;
            font-size: 0.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "rag_chain" not in st.session_state:
    st.session_state.rag_chain = None

# -----------------------------------------------------------------------------
# Sidebar: Controls & Input
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
            <div style="background: linear-gradient(135deg, #6366f1, #a855f7); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px;">⚡</div>
            <div>
                <h2 style="margin: 0; font-size: 1.25rem; font-weight: 700;">EchoMind AI</h2>
                <p style="margin: 0; font-size: 0.78rem; color: #94a3b8;">Video & Meeting Intelligence</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 📥 Media Source")
    input_type = st.radio("Choose Input Mode", ["YouTube Link", "Upload File"], horizontal=True, label_visibility="collapsed")

    source_path = None
    if input_type == "YouTube Link":
        youtube_url = st.text_input("Paste YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
        if youtube_url.strip():
            source_path = youtube_url.strip()
    else:
        uploaded_file = st.file_uploader("Upload Audio or Video", type=["wav", "mp3", "m4a", "mp4", "webm"])
        if uploaded_file is not None:
            source_path = save_uploaded_file(uploaded_file)
            st.caption(f"📁 `{uploaded_file.name}` uploaded successfully")

    st.markdown("#### 🌐 Transcription Language")
    language = st.selectbox(
        "Select Language Mode",
        options=["english", "hinglish"],
        format_func=lambda x: "English (Whisper Local)" if x == "english" else "Hinglish (Sarvam AI Translation)",
    )

    # Key status checkers
    mistral_ready = bool(os.getenv("MISTRAL_API_KEY"))
    sarvam_ready = bool(os.getenv("SARVAM_API_KEY"))

    with st.expander("⚙️ System Status", expanded=False):
        st.markdown(f"**Mistral AI Key:** {'🟢 Active' if mistral_ready else '🔴 Missing'}")
        st.markdown(f"**Sarvam AI Key:** {'🟢 Active' if sarvam_ready else '🔴 Missing'}")
        st.markdown(f"**Whisper Model:** `{os.getenv('WHISPER_MODEL', 'small')}`")

    st.markdown("---")
    run_btn = st.button("🚀 Analyze Meeting", type="primary", use_container_width=True)

    if st.session_state.analysis_data is not None:
        if st.button("🔄 Reset / Start New", use_container_width=True):
            st.session_state.analysis_data = None
            st.session_state.chat_history = []
            st.session_state.rag_chain = None
            st.rerun()

# -----------------------------------------------------------------------------
# Pipeline Execution Logic
# -----------------------------------------------------------------------------
if run_btn:
    if not source_path:
        st.sidebar.error("⚠️ Please provide a YouTube link or upload an audio/video file.")
    elif language == "hinglish" and not sarvam_ready:
        st.sidebar.error("⚠️ Sarvam AI API key is missing from `.env` (required for Hinglish).")
    elif not mistral_ready:
        st.sidebar.error("⚠️ Mistral API key is missing from `.env`.")
    else:
        with st.status("🔍 Processing and analyzing your media...", expanded=True) as status:
            try:
                import time

                # Step 1: Process input audio
                status.update(label="🎵 1/5 Extracting & normalizing audio...", state="running")
                chunks = process_input(source_path)
                if not chunks:
                    raise RuntimeError("No valid audio content could be extracted from this media source.")

                # Step 2: Transcribe
                engine_name = "Sarvam AI" if language == "hinglish" else "Whisper"
                status.update(label=f"🎙️ 2/5 Transcribing with {engine_name} ({len(chunks)} chunk(s))...", state="running")
                transcript = transcribe_all(chunks, language=language)

                if not transcript or not transcript.strip():
                    raise RuntimeError("Transcription completed but returned no spoken text (audio might be silent).")

                # Step 3: Summarize & Title (spaced to respect LLM rate limits)
                status.update(label="📝 3/5 Generating title & executive summary...", state="running")
                title = generate_title(transcript)
                time.sleep(1)
                summary = summarize(transcript)

                # Step 4: Extract Insights
                status.update(label="💡 4/5 Extracting action items, key decisions & questions...", state="running")
                time.sleep(1)
                action_items = extract_action_items(transcript)
                time.sleep(1)
                decisions = extract_key_decisions(transcript)
                time.sleep(1)
                questions = extract_questions(transcript)

                # Step 5: Build RAG vector store & chain
                status.update(label="🧠 5/5 Building semantic vector index for Q&A...", state="running")
                rag_chain = build_rag_chain(transcript)

                # Save in session state
                st.session_state.analysis_data = {
                    "title": title,
                    "transcript": transcript,
                    "summary": summary,
                    "action_items": action_items,
                    "key_decisions": decisions,
                    "open_questions": questions,
                    "language": language,
                    "chunks_count": len(chunks),
                }
                st.session_state.rag_chain = rag_chain
                st.session_state.chat_history = []

                status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                st.rerun()

            except Exception as e:
                import traceback
                err_str = str(e)
                trace_str = traceback.format_exc()
                print(f"Pipeline Error: {err_str}\n{trace_str}")
                status.update(label="❌ Pipeline execution failed", state="error", expanded=True)
                if "429" in err_str or "rate" in err_str.lower() or "capacity" in err_str.lower():
                    st.error("⚠️ **Mistral AI Rate Limit / Capacity**: Mistral API capacity was reached on free tier. Please wait 15–30 seconds and click Analyze again.")
                else:
                    st.error(f"Error details: {err_str}")
                with st.expander("Show Technical Traceback"):
                    st.code(trace_str)

# -----------------------------------------------------------------------------
# Main Dashboard Display
# -----------------------------------------------------------------------------
data = st.session_state.analysis_data

if data is None:
    # Landing / Hero state
    st.markdown('<div class="hero-title">Turn Any Meeting or Video Into Actionable Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Upload your recording or paste a YouTube URL. Get instant executive summaries, key decisions, action items, and chat interactively with your meeting transcript using RAG.</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 24px; margin-bottom: 8px;">📑</div>
                <h4 style="margin: 0 0 6px 0;">Executive Summaries</h4>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">Comprehensive meeting digest, agenda highlights, and clear context breakdown.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 24px; margin-bottom: 8px;">🎯</div>
                <h4 style="margin: 0 0 6px 0;">Action Items & Decisions</h4>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">Auto-detect who is responsible for what, deadlines, and agreed strategic milestones.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div class="glass-card">
                <div style="font-size: 24px; margin-bottom: 8px;">💬</div>
                <h4 style="margin: 0 0 6px 0;">Chat via RAG</h4>
                <p style="color: #94a3b8; font-size: 0.88rem; margin: 0;">Ask questions directly against your meeting transcript with semantic search & precision answers.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info("👈 Enter a YouTube URL or upload a file in the sidebar to get started!")

else:
    # Header & Badges
    st.markdown(f'<div class="hero-title">{data["title"]}</div>', unsafe_allow_html=True)

    engine_tag = "Sarvam AI (Hinglish)" if data["language"] == "hinglish" else "Whisper (English)"
    st.markdown(
        f"""
        <div style="margin-bottom: 1.25rem;">
            <span class="badge badge-purple">⚡ Engine: {engine_tag}</span>
            <span class="badge badge-blue">🧩 Chunks: {data["chunks_count"]}</span>
            <span class="badge badge-emerald">✨ Intelligence Ready</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main Tabs
    tab_summary, tab_actions, tab_decisions, tab_questions, tab_chat, tab_transcript = st.tabs(
        [
            "📋 Executive Summary",
            "✅ Action Items",
            "🔑 Key Decisions",
            "❓ Open Questions",
            "💬 Chat with Meeting",
            "📝 Full Transcript",
        ]
    )

    with tab_summary:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(data["summary"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_actions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(data["action_items"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_decisions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(data["key_decisions"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_questions:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(data["open_questions"])
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_chat:
        st.markdown("#### 💬 Ask anything about this meeting")
        st.caption("Powered by Chroma Vector Store & Mistral AI RAG Pipeline")

        # Quick Suggestion Chips
        sug_cols = st.columns([1, 1, 1])
        with sug_cols[0]:
            if st.button("📌 Summarize main takeaways", use_container_width=True):
                st.session_state.pending_query = "Summarize the top takeaways of this meeting in 3 bullet points."
        with sug_cols[1]:
            if st.button("⏰ What were the deadlines?", use_container_width=True):
                st.session_state.pending_query = "What deadlines or timeframes were discussed?"
        with sug_cols[2]:
            if st.button("👤 Who owns which tasks?", use_container_width=True):
                st.session_state.pending_query = "Which persons or teams were assigned specific action items?"

        # Render Chat History
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Chat Input Handlers
        chat_query = st.chat_input("Ask a question about the meeting discussion...")
        if hasattr(st.session_state, "pending_query") and st.session_state.pending_query:
            chat_query = st.session_state.pending_query
            st.session_state.pending_query = None

        if chat_query:
            st.session_state.chat_history.append({"role": "user", "content": chat_query})
            with st.chat_message("user"):
                st.markdown(chat_query)

            with st.chat_message("assistant"):
                with st.spinner("Searching transcript context..."):
                    try:
                        if st.session_state.rag_chain is None:
                            st.session_state.rag_chain = build_rag_chain(data["transcript"])
                        answer = ask_question(st.session_state.rag_chain, chat_query)
                    except Exception as ex:
                        answer = f"⚠️ Could not retrieve answer: {str(ex)}"
                    st.markdown(answer)
                    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    with tab_transcript:
        st.markdown("#### 📜 Complete Transcription")
        st.caption(f"Total length: {len(data['transcript'])} characters")
        st.text_area("Transcript Text", value=data["transcript"], height=400, label_visibility="collapsed")

    # Export Section
    st.markdown("---")
    st.markdown("#### 💾 Export Report")

    full_report_md = f"""# {data['title']}

**Engine:** {engine_tag}  
**Chunks:** {data['chunks_count']}  

## 📋 Executive Summary
{data['summary']}

## ✅ Action Items
{data['action_items']}

## 🔑 Key Decisions
{data['key_decisions']}

## ❓ Open Questions
{data['open_questions']}

## 📝 Full Transcript
{data['transcript']}
"""

    down_col1, down_col2 = st.columns([1, 3])
    with down_col1:
        st.download_button(
            label="📥 Download Markdown Report",
            data=full_report_md,
            file_name=f"{data['title'].replace(' ', '_').lower()}_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with down_col2:
        st.download_button(
            label="📄 Download Plain Text Transcript",
            data=data["transcript"],
            file_name=f"{data['title'].replace(' ', '_').lower()}_transcript.txt",
            mime="text/plain",
            use_container_width=False,
        )
