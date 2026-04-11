"""Application configuration via environment variables or .env file."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ------------------------------------------------------------------ ACE-Step model init
    # DiT model name, e.g.  "acestep-v15-turbo" or "acestep-v15-base"
    config_path: str = "acestep-v15-turbo"
    # Device: "auto", "cuda", "mps", "xpu", "cpu"
    device: str = "auto"
    # LLM model; empty string = skip LLM (no CoT reasoning)
    lm_model_path: str = "acestep-5Hz-lm-1.7B"
    # Whether to initialize the LLM at startup (costs VRAM)
    init_llm: bool = True
    # Flash-attention (pass True only when the package is available)
    use_flash_attention: bool = False
    # Compile the DiT model with torch.compile (faster, slower startup)
    compile_model: bool = False
    # Offload to CPU to save VRAM
    offload_to_cpu: bool = False
    offload_dit_to_cpu: bool = False
    # LLM backend: "vllm", "nano_vllm", "transformers"
    lm_backend: str = "transformers"
    # Generation batch size (2 tracks per request, matching Suno behavior)
    batch_size: int = 2
    # Default output format: "flac", "mp3", "wav"
    audio_format: str = "flac"

    # ------------------------------------------------------------------ API auth
    # If set, all requests must supply `Authorization: Bearer <api_key>`
    api_key: Optional[str] = None

    # ------------------------------------------------------------------ Server
    host: str = "0.0.0.0"
    port: int = 7080
    log_level: str = "info"

    # ------------------------------------------------------------------ Task store
    # Completed tasks are kept this many seconds (≈15 days, matching Suno)
    task_ttl_seconds: int = 1_296_000

    # ------------------------------------------------------------------ Credits simulation
    simulated_credits: int = 9_999

    # ------------------------------------------------------------------ Callback delivery
    callback_timeout_seconds: int = 10
    callback_max_retries: int = 3


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached settings singleton."""
    return Settings()
