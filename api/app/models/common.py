"""Standard Suno API response envelope and shared enums."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional


def ok(data: Any = None) -> dict:
    """Build a 200-OK Suno response dict."""
    return {"code": 200, "msg": "success", "data": data}


def err(code: int, msg: str) -> dict:
    """Build an error Suno response dict."""
    return {"code": code, "msg": msg, "data": None}


class ModelVersion(str, Enum):
    """Supported Suno AI model versions (mapped to ACE-Step models)."""

    V4 = "V4"
    V4_5 = "V4_5"
    V4_5PLUS = "V4_5PLUS"
    V4_5ALL = "V4_5ALL"
    V5 = "V5"
    V5_5 = "V5_5"


class PersonaModel(str, Enum):
    style_persona = "style_persona"
    voice_persona = "voice_persona"


class VocalGender(str, Enum):
    male = "m"
    female = "f"
