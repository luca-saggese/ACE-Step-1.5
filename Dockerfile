FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        git \
        python3.11 \
        python3.11-venv \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3.11 -m pip install --upgrade pip \
    && python3.11 -m pip install uv

WORKDIR /app

COPY . /app

RUN uv sync

EXPOSE 7860

VOLUME ["/app/checkpoints"]

RUN chmod +x /app/docker-entrypoint.sh

CMD ["/app/docker-entrypoint.sh"]
