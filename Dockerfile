FROM python:3.11-slim

WORKDIR /app

# Cài ffmpeg + libsodium + node
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsodium-dev \
    nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
