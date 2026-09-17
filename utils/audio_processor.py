import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok = True)

def _get_cookies_file() -> str | None:
    """Check if cookies file or secret is available for YouTube authentication."""
    if os.path.exists("cookies.txt"):
        return "cookies.txt"
    cookies_content = os.environ.get("YOUTUBE_COOKIES")
    if not cookies_content:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "YOUTUBE_COOKIES" in st.secrets:
                cookies_content = st.secrets["YOUTUBE_COOKIES"]
        except Exception:
            pass
    if cookies_content:
        cookies_path = os.path.join(DOWNLOAD_DIR, "cookies.txt")
        with open(cookies_path, "w", encoding="utf-8") as f:
            f.write(cookies_content)
        return cookies_path
    return None


def download_youtube_audio(url: str) -> str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    cookie_file = _get_cookies_file()

    # Combinations of format strings and player_clients designed to bypass YouTube's
    # SABR-only streaming experiment and 403 Forbidden datacenter blocks.
    # Format '18' is YouTube's standard progressive MP4 stream (audio + video), which is
    # immune to the SABR audio token restrictions and 403 Forbidden errors on cloud servers.
    download_configs = [
        {"format": "18/ba/b", "clients": ["android", "ios"]},
        {"format": "18/worst[ext=mp4]/ba/b", "clients": ["android"]},
        {"format": "18/ba/b", "clients": ["mweb", "web_embedded"]},
        {"format": "ba/b", "clients": ["android", "web"]},
        {"format": "bestaudio/best", "clients": ["android", "ios", "mweb", "web"]},
    ]

    last_error = None
    for config in download_configs:
        ydl_opts = {
            "format": config["format"],
            "outtmpl": output_path,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "192",
                }
            ],
            "extractor_args": {
                "youtube": {
                    "player_client": config["clients"],
                }
            },
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
            },
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
        }
        if cookie_file:
            ydl_opts["cookiefile"] = cookie_file

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    continue
                video_id = info.get("id")
                # Look for the generated wav or downloaded media file
                candidates = [
                    os.path.join(DOWNLOAD_DIR, f"{video_id}.wav"),
                    os.path.splitext(ydl.prepare_filename(info))[0] + ".wav",
                    os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4"),
                    ydl.prepare_filename(info),
                ]
                for cand in candidates:
                    if os.path.exists(cand) and os.path.getsize(cand) > 0:
                        return cand
        except Exception as e:
            last_error = e
            continue

    err_str = str(last_error) if last_error else "Unknown download error"
    if "403" in err_str or "Forbidden" in err_str or "Sign in" in err_str:
        raise RuntimeError(
            "YouTube blocked automated downloads from Streamlit Cloud's IP address (HTTP Error 403: Forbidden).\n\n"
            "This happens because YouTube restricts traffic from public cloud hosting providers.\n\n"
            "💡 **How to proceed:**\n"
            "1. **Recommended:** Switch to the **'📁 Upload File'** tab in the sidebar and upload your video/audio file directly.\n"
            "2. Or add a `cookies.txt` file (or `YOUTUBE_COOKIES` in Streamlit Secrets) to authenticate requests."
        )
    raise RuntimeError(f"Failed to download YouTube audio: {err_str}")


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to 16kHz mono WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_16k.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz mono for Whisper
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    if len(audio) == 0:
        return []

    chunk_ms = chunk_minutes * 60 * 1000
    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        # Ignore tail pieces shorter than 1.5 seconds to prevent empty/zero-element tensor errors
        if len(chunk) < 1500 and len(chunks) > 0:
            continue
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    if not chunks and len(audio) > 0:
        chunk_path = f"{wav_path}_chunk_0.wav"
        audio.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected Youtube URL. Downloading audio...")
        raw_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        raw_path = source

    # Always normalize to 16kHz mono WAV for Whisper compatibility
    wav_path = convert_to_wav(raw_path)
    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio - {len(chunks)} chunk(s) created")
    return chunks


def save_uploaded_file(uploaded_file) -> str:
    """Save Streamlit UploadedFile to downloads/ and return absolute path."""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


