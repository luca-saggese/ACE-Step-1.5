"""Translates Suno API request models into ACE-Step GenerationParams/Config.

This is the only place where the Suno ↔ ACE-Step semantic mapping lives.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from loguru import logger

from app.models.requests import (
    AddInstrumentalRequest,
    AddVocalsRequest,
    ExtendMusicRequest,
    GenerateMashupRequest,
    GenerateMusicRequest,
    GenerateSoundsRequest,
    SeparateVocalsRequest,
    UploadCoverRequest,
    UploadExtendRequest,
)

# Lazy import to avoid loading torch at module init time
def _imports():
    from acestep.inference import GenerationConfig, GenerationParams
    return GenerationParams, GenerationConfig


# Directory where generated audio files are saved  (api/output/)
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


def ensure_output_dir() -> str:
    """Create and return the output directory path."""
    path = os.path.abspath(OUTPUT_DIR)
    os.makedirs(path, exist_ok=True)
    return path


# ------------------------------------------------------------------
# Audio download helper
# ------------------------------------------------------------------

def _download_audio(url: str) -> str:
    """Download a remote audio file into a local temp file and return its path.

    Raises:
        httpx.HTTPError: on network failure.
    """
    resp = httpx.get(str(url), follow_redirects=True, timeout=60)
    resp.raise_for_status()
    suffix = Path(str(url)).suffix or ".mp3"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(resp.content)
        return f.name


# ------------------------------------------------------------------
# Suno → ACE-Step field translators
# ------------------------------------------------------------------

def _make_base_config(batch_size: int = 2) -> Any:
    _, GenerationConfig = _imports()
    return GenerationConfig(batch_size=batch_size, use_random_seed=True, audio_format="flac")


def params_for_generate(req: GenerateMusicRequest) -> Tuple[Any, Any]:
    """Build ``(GenerationParams, GenerationConfig)`` from a GenerateMusicRequest.

    Mapping:
    - customMode=True, instrumental=False  → caption=style, lyrics=prompt (exact)
    - customMode=True, instrumental=True   → caption=style, lyrics="[Instrumental]"
    - customMode=False                     → caption=prompt, lyrics="", thinking=True
    """
    GenerationParams, GenerationConfig = _imports()

    if req.customMode:
        caption = req.style or ""
        lyrics = req.prompt if not req.instrumental else "[Instrumental]"
        thinking = False          # user provided lyrics → skip LM
        instrumental = req.instrumental
    else:
        caption = req.prompt or ""
        lyrics = ""
        thinking = True           # let LM generate lyrics
        instrumental = req.instrumental

    params = GenerationParams(
        task_type="text2music",
        caption=caption,
        lyrics=lyrics or "",
        instrumental=instrumental,
        thinking=thinking,
        use_cot_metas=thinking,
        use_cot_caption=thinking,
        use_cot_language=thinking,
    )
    config = _make_base_config()
    return params, config


def params_for_extend(req: ExtendMusicRequest, src_audio_path: str) -> Tuple[Any, Any]:
    """Build params for music extension (repaint/continue task)."""
    GenerationParams, _ = _imports()

    if req.defaultParamFlag:
        caption = req.style or ""
        lyrics = req.prompt or ""
        thinking = False
    else:
        # Use original track's style — we can only pass the reference audio
        caption = ""
        lyrics = ""
        thinking = True

    params = GenerationParams(
        task_type="repaint",
        src_audio=src_audio_path,
        repainting_start=req.continueAt or 0.0,
        repainting_end=-1.0,
        caption=caption,
        lyrics=lyrics,
        thinking=thinking,
        use_cot_metas=thinking,
        use_cot_caption=thinking,
    )
    config = _make_base_config()
    return params, config


def params_for_upload_cover(req: UploadCoverRequest, ref_audio_path: str) -> Tuple[Any, Any]:
    """Build params for upload+cover (style-transfer cover task)."""
    GenerationParams, _ = _imports()

    if req.customMode:
        caption = req.style or ""
        lyrics = req.prompt if not req.instrumental else "[Instrumental]"
        thinking = False
        instrumental = req.instrumental
    else:
        caption = req.prompt or ""
        lyrics = ""
        thinking = True
        instrumental = req.instrumental

    params = GenerationParams(
        task_type="cover",
        reference_audio=ref_audio_path,
        caption=caption,
        lyrics=lyrics,
        instrumental=instrumental,
        thinking=thinking,
        use_cot_metas=thinking,
        use_cot_caption=thinking,
    )
    config = _make_base_config()
    return params, config


def params_for_upload_extend(req: UploadExtendRequest, src_audio_path: str) -> Tuple[Any, Any]:
    """Build params for upload+extend (repaint uploaded audio)."""
    GenerationParams, _ = _imports()

    if req.defaultParamFlag:
        caption = req.style or ""
        lyrics = req.prompt if not req.instrumental else "[Instrumental]"
        thinking = False
        instrumental = req.instrumental if req.instrumental is not None else False
    else:
        caption = req.prompt or ""
        lyrics = ""
        thinking = True
        instrumental = False

    params = GenerationParams(
        task_type="repaint",
        src_audio=src_audio_path,
        repainting_start=req.continueAt or 0.0,
        repainting_end=-1.0,
        caption=caption,
        lyrics=lyrics,
        instrumental=instrumental,
        thinking=thinking,
        use_cot_metas=thinking,
        use_cot_caption=thinking,
    )
    config = _make_base_config()
    return params, config


def params_for_mashup(req: GenerateMashupRequest, audio_paths: List[str]) -> Tuple[Any, Any]:
    """Build params for mashup (cover from blended references)."""
    GenerationParams, _ = _imports()

    if req.customMode:
        caption = req.style or req.prompt or ""
        lyrics = req.prompt if not req.instrumental else "[Instrumental]"
        thinking = False
        instrumental = req.instrumental if req.instrumental is not None else False
    else:
        caption = req.prompt or ""
        lyrics = ""
        thinking = True
        instrumental = False

    # Use the first audio as reference, second as src (best approximation with ACE-Step)
    params = GenerationParams(
        task_type="cover",
        reference_audio=audio_paths[0] if audio_paths else None,
        src_audio=audio_paths[1] if len(audio_paths) > 1 else None,
        caption=caption,
        lyrics=lyrics,
        instrumental=instrumental,
        thinking=thinking,
        use_cot_metas=thinking,
        use_cot_caption=thinking,
    )
    config = _make_base_config()
    return params, config


def params_for_add_vocals(req: AddVocalsRequest, src_audio_path: str) -> Tuple[Any, Any]:
    """Build params for adding vocals to an instrumental track."""
    GenerationParams, _ = _imports()

    params = GenerationParams(
        task_type="repaint",
        src_audio=src_audio_path,
        caption=req.style,
        lyrics=req.prompt,
        instrumental=False,
        thinking=False,
        use_cot_metas=False,
        use_cot_caption=False,
    )
    config = _make_base_config()
    return params, config


def params_for_add_instrumental(req: AddInstrumentalRequest, src_audio_path: str) -> Tuple[Any, Any]:
    """Build params for adding an instrumental backing to a vocal track."""
    GenerationParams, _ = _imports()

    params = GenerationParams(
        task_type="repaint",
        src_audio=src_audio_path,
        caption=req.tags,
        lyrics="[Instrumental]",
        instrumental=True,
        thinking=False,
        use_cot_metas=False,
        use_cot_caption=False,
    )
    config = _make_base_config()
    return params, config


def params_for_sounds(req: GenerateSoundsRequest) -> Tuple[Any, Any]:
    """Build params for ambient sound generation."""
    GenerationParams, GenerationConfig = _imports()

    caption = req.prompt
    if req.soundTempo:
        caption = f"BPM:{req.soundTempo}, Key:{req.soundKey.value}, {caption}"
    if req.soundLoop:
        caption = f"[Loop] {caption}"

    params = GenerationParams(
        task_type="text2music",
        caption=caption,
        lyrics="[Instrumental]",
        instrumental=True,
        thinking=False,
        use_cot_metas=True,
        use_cot_caption=False,
    )
    config = GenerationConfig(batch_size=2, use_random_seed=True, audio_format="flac")
    return params, config


# ------------------------------------------------------------------
# Result helpers
# ------------------------------------------------------------------

def build_suno_audio_data(result_audio: Dict[str, Any], idx: int) -> Dict[str, Any]:
    """Convert an ACE-Step audio dict into a Suno sunoData dict."""
    import uuid as _uuid

    audio_path = result_audio.get("audio_path") or result_audio.get("path") or ""
    # Build a file:// URL or relative URL that clients can retrieve
    # In production callers should configure a static file server / CDN.
    audio_url = f"/audio/{os.path.basename(audio_path)}" if audio_path else None

    return {
        "id": _uuid.uuid4().hex,
        "audioUrl": audio_url,
        "streamAudioUrl": audio_url,
        "imageUrl": None,
        "prompt": result_audio.get("lyrics") or result_audio.get("caption") or "",
        "modelName": "ACE-Step-v1.5",
        "title": result_audio.get("title") or f"Track {idx + 1}",
        "tags": result_audio.get("style") or result_audio.get("caption") or "",
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
        "duration": result_audio.get("audio_duration"),
    }


# ------------------------------------------------------------------
# Task-store audio resolution
# ------------------------------------------------------------------

def resolve_audio_path(audio_id: str, store) -> Optional[str]:
    """Find the local filesystem path for a previously generated audioId.

    Scans all SUCCESS tasks in *store* and matches the ``id`` field inside
    ``sunoData`` entries.

    Args:
        audio_id: The Suno-style ``audioId`` (UUID hex) returned at generation time.
        store: The ``TaskStore`` singleton.

    Returns:
        Absolute path to the local audio file, or ``None`` if not found.
    """
    from app.task_store import TaskStatus  # local import to avoid circular deps

    for task in store.list_tasks():
        if task.status != TaskStatus.SUCCESS or not task.response:
            continue
        for entry in (task.response or {}).get("sunoData", []):
            if entry.get("id") == audio_id:
                audio_url = entry.get("audioUrl", "")
                filename = os.path.basename(audio_url)
                if not filename:
                    continue
                full_path = os.path.join(ensure_output_dir(), filename)
                if os.path.exists(full_path):
                    return full_path
    return None
