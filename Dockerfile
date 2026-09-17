FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install ffmpeg and system dependencies required for audio/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Render dynamically sets $PORT (defaults to 10000)
EXPOSE 10000

CMD ["sh", "-c", "streamlit run app.py --server.port ${PORT:-10000} --server.address 0.0.0.0 --server.enableCORS false --server.enableXsrfProtection false"]
