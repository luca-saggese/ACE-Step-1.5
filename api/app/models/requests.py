"""Request/response models for all Suno API endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional

from pydantic import AnyHttpUrl, BaseModel, Field, model_validator

from app.models.common import ModelVersion, PersonaModel, VocalGender


# ------------------------------------------------------------------ generate

class GenerateMusicRequest(BaseModel):
    """POST /api/v1/generate"""

    customMode: bool
    instrumental: bool
    model: ModelVersion
    callBackUrl: AnyHttpUrl
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    personaId: Optional[str] = None
    personaModel: PersonaModel = PersonaModel.style_persona
    negativeTags: Optional[str] = None
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_required_fields(self) -> "GenerateMusicRequest":
        if self.customMode:
            missing = []
            if not self.style:
                missing.append("style")
            if not self.title:
                missing.append("title")
            if not self.instrumental and not self.prompt:
                missing.append("prompt")
            if missing:
                raise ValueError(f"customMode=true requires: {', '.join(missing)}")
        else:
            if not self.prompt:
                raise ValueError("customMode=false requires 'prompt'.")
        return self


# ------------------------------------------------------------------ extend

class ExtendMusicRequest(BaseModel):
    """POST /api/v1/generate/extend"""

    defaultParamFlag: bool
    audioId: str
    model: ModelVersion
    callBackUrl: AnyHttpUrl
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    continueAt: Optional[float] = Field(None, gt=0)
    personaId: Optional[str] = None
    personaModel: PersonaModel = PersonaModel.style_persona
    negativeTags: Optional[str] = None
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def check_custom_fields(self) -> "ExtendMusicRequest":
        if self.defaultParamFlag:
            missing = [f for f in ("prompt", "style", "title", "continueAt") if getattr(self, f) is None]
            if missing:
                raise ValueError(f"defaultParamFlag=true requires: {', '.join(missing)}")
        return self


# ------------------------------------------------------------------ upload-cover / upload-extend

class UploadCoverRequest(BaseModel):
    """POST /api/v1/generate/upload-cover"""

    uploadUrl: AnyHttpUrl
    customMode: bool
    instrumental: bool
    model: ModelVersion
    callBackUrl: AnyHttpUrl
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    personaId: Optional[str] = None
    personaModel: PersonaModel = PersonaModel.style_persona
    negativeTags: Optional[str] = None
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)


class UploadExtendRequest(BaseModel):
    """POST /api/v1/generate/upload-extend"""

    uploadUrl: AnyHttpUrl
    defaultParamFlag: bool
    model: ModelVersion
    callBackUrl: AnyHttpUrl
    instrumental: Optional[bool] = None
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    continueAt: Optional[float] = Field(None, gt=0)
    personaId: Optional[str] = None
    personaModel: PersonaModel = PersonaModel.style_persona
    negativeTags: Optional[str] = None
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)


# ------------------------------------------------------------------ mashup

class GenerateMashupRequest(BaseModel):
    """POST /api/v1/generate/mashup"""

    uploadUrlList: List[AnyHttpUrl] = Field(..., min_length=2, max_length=2)
    customMode: bool
    model: ModelVersion
    callBackUrl: AnyHttpUrl
    prompt: Optional[str] = None
    style: Optional[str] = None
    title: Optional[str] = None
    instrumental: Optional[bool] = None
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)


# ------------------------------------------------------------------ add-vocals / add-instrumental

class AddVocalsRequest(BaseModel):
    """POST /api/v1/generate/add-vocals"""

    prompt: str
    title: str
    negativeTags: str
    style: str
    uploadUrl: AnyHttpUrl
    callBackUrl: AnyHttpUrl
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    model: str = "V4_5PLUS"


class AddInstrumentalRequest(BaseModel):
    """POST /api/v1/generate/add-instrumental"""

    uploadUrl: AnyHttpUrl
    title: str
    negativeTags: str
    tags: str
    callBackUrl: AnyHttpUrl
    vocalGender: Optional[VocalGender] = None
    styleWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    weirdnessConstraint: Optional[float] = Field(None, ge=0.0, le=1.0)
    audioWeight: Optional[float] = Field(None, ge=0.0, le=1.0)
    model: str = "V4_5PLUS"


# ------------------------------------------------------------------ timestamped lyrics

class GetTimestampedLyricsRequest(BaseModel):
    """POST /api/v1/generate/get-timestamped-lyrics"""

    taskId: str
    audioId: str


# ------------------------------------------------------------------ generate-persona

class GeneratePersonaRequest(BaseModel):
    """POST /api/v1/generate/generate-persona"""

    taskId: str
    audioId: str
    name: str
    description: str
    vocalStart: float = Field(0.0, ge=0)
    vocalEnd: float = Field(30.0, ge=0)
    style: Optional[str] = None


# ------------------------------------------------------------------ lyrics

class GenerateLyricsRequest(BaseModel):
    """POST /api/v1/lyrics"""

    prompt: str = Field(..., max_length=200)
    callBackUrl: AnyHttpUrl


# ------------------------------------------------------------------ vocal removal

class SeparationType(str, Enum):
    separate_vocal = "separate_vocal"
    split_stem = "split_stem"


class SeparateVocalsRequest(BaseModel):
    """POST /api/v1/vocal-removal/generate"""

    taskId: str
    audioId: str
    callBackUrl: Optional[AnyHttpUrl] = None
    type: SeparationType = SeparationType.separate_vocal


# ------------------------------------------------------------------ WAV

class ConvertToWavRequest(BaseModel):
    """POST /api/v1/wav/generate"""

    taskId: str
    audioId: str
    callBackUrl: Optional[AnyHttpUrl] = None


# ------------------------------------------------------------------ Music Video

class CreateMusicVideoRequest(BaseModel):
    """POST /api/v1/mp4/generate"""

    taskId: str
    audioId: str
    callBackUrl: Optional[AnyHttpUrl] = None
    author: Optional[str] = Field(None, max_length=50)
    domainName: Optional[str] = Field(None, max_length=50)
    title: Optional[str] = Field(None, max_length=100)


# ------------------------------------------------------------------ Cover image

class GenerateCoverRequest(BaseModel):
    """POST /api/v1/suno/cover/generate"""

    taskId: str
    callBackUrl: AnyHttpUrl
    prompt: Optional[str] = Field(None, max_length=300, description="Optional image generation prompt")
    style: Optional[str] = Field(None, max_length=100, description="Optional image style hint")


# ------------------------------------------------------------------ Sounds

class SoundKey(str, Enum):
    Any = "Any"
    Cm = "Cm"; Csm = "C#m"; Dm = "Dm"; Dsm = "D#m"
    Em = "Em"; Fm = "Fm"; Fsm = "F#m"; Gm = "Gm"
    Gsm = "G#m"; Am = "Am"; Asm = "A#m"; Bm = "Bm"
    C = "C"; Cs = "C#"; D = "D"; Ds = "D#"
    E = "E"; F = "F"; Fs = "F#"; G = "G"
    Gs = "G#"; A = "A"; As = "A#"; B = "B"


class GenerateSoundsRequest(BaseModel):
    """POST /api/v1/generate/sounds"""

    prompt: str = Field(..., max_length=500)
    model: str = "V5"
    soundLoop: bool = False
    soundTempo: Optional[int] = Field(None, ge=1, le=300)
    soundKey: SoundKey = SoundKey.Any
    grabLyrics: bool = False
    callBackUrl: Optional[AnyHttpUrl] = None


# ------------------------------------------------------------------ Boost style

class BoostStyleRequest(BaseModel):
    """POST /api/v1/style/generate"""

    style: str = Field(..., alias="content", description="Style description, e.g. 'Pop, Mysterious'")
    callBackUrl: Optional[AnyHttpUrl] = None

    model_config = {"populate_by_name": True}
