"""Music generation endpoints.

POST  /api/v1/generate                  – generate music
GET   /api/v1/generate/record-info      – poll task status
POST  /api/v1/generate/extend           – extend a track
POST  /api/v1/generate/upload-cover     – cover with uploaded audio
POST  /api/v1/generate/upload-extend    – extend uploaded audio
POST  /api/v1/generate/mashup           – mashup two audio files
POST  /api/v1/generate/add-vocals       – overlay vocals on instrumental
POST  /api/v1/generate/add-instrumental – add backing to vocals
POST  /api/v1/generate/sounds           – generate ambient sounds
POST  /api/v1/generate/get-timestamped-lyrics
GET   /api/v1/generate/credit           – remaining credits
"""

from __future__ import annotations

import json
import os
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.config import Settings, get_settings
from app.models.common import ok, err
from app.models.requests import (
    AddInstrumentalRequest,
    AddVocalsRequest,
    ExtendMusicRequest,
    GenerateMashupRequest,
    GenerateMusicRequest,
    GenerateSoundsRequest,
    GetTimestampedLyricsRequest,
    GeneratePersonaRequest,
    UploadCoverRequest,
    UploadExtendRequest,
)
from app.pipeline import get_pipeline
from app.service import (
    _download_audio,
    build_suno_audio_data,
    ensure_output_dir,
    params_for_add_instrumental,
    params_for_add_vocals,
    params_for_extend,
    params_for_generate,
    params_for_mashup,
    params_for_sounds,
    params_for_upload_cover,
    params_for_upload_extend,
    resolve_audio_path,
)
from app.task_store import TaskStatus, TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Music Generation"])


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _make_generate_job(params, config, task_id: str):
    """Return a zero-argument callable that runs generation and stores results."""
    pipeline = get_pipeline()
    store = get_task_store()
    save_dir = ensure_output_dir()

    def _job():
        result = pipeline.generate(params, config, save_dir=save_dir)
        if not result.success:
            raise RuntimeError(result.error or "Generation failed")

        suno_data = [build_suno_audio_data(a, i) for i, a in enumerate(result.audios)]
        response = {"taskId": task_id, "sunoData": suno_data}
        return response

    return _job


def _enqueue_and_respond(task_type: TaskType, job_fn, req_json: str, callback_url: str):
    """Create a task, enqueue the job, return a Suno-style creation response."""
    import asyncio as _asyncio
    store = get_task_store()
    task = store.create_task(task_type=task_type, param=req_json, callback_url=callback_url)
    _asyncio.create_task(store.enqueue(task.task_id, job_fn))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate
# ------------------------------------------------------------------

@router.post("/generate")
async def generate_music(req: GenerateMusicRequest, _: AuthToken):
    """Generate music from a text description."""
    params, config = params_for_generate(req)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )

    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# GET /api/v1/generate/record-info
# ------------------------------------------------------------------

@router.get("/generate/record-info")
async def get_music_generation_details(
    taskId: str = Query(..., description="Task ID returned from generate endpoints."),
    _: AuthToken = None,
):
    """Retrieve detailed status of a music generation task."""
    store = get_task_store()
    task = store.get_task(taskId)
    if task is None:
        raise HTTPException(status_code=404, detail=err(404, "Task not found"))

    data = {
        "taskId": task.task_id,
        "parentMusicId": "",
        "param": task.param,
        "response": task.response,
        "status": task.status.value,
        "type": task.task_type.value,
        "errorCode": task.error_code,
        "errorMessage": task.error_message,
    }
    return ok(data)


# ------------------------------------------------------------------
# POST /api/v1/generate/extend
# ------------------------------------------------------------------

@router.post("/generate/extend")
async def extend_music(req: ExtendMusicRequest, _: AuthToken):
    """Extend an existing track by its audioId."""
    # audioId references a completed task's output – we look up the stored path
    store = get_task_store()
    src_path = _resolve_audio_path(req.audioId, store)
    if src_path is None:
        raise HTTPException(status_code=400, detail=err(400, f"audioId '{req.audioId}' not found in task store"))

    params, config = params_for_extend(req, src_path)
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/upload-cover
# ------------------------------------------------------------------

@router.post("/generate/upload-cover")
async def upload_cover(req: UploadCoverRequest, _: AuthToken):
    """Cover a track from an uploaded audio URL."""
    try:
        ref_path = _download_audio(str(req.uploadUrl))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=err(400, f"Failed to download uploadUrl: {exc}"))

    params, config = params_for_upload_cover(req, ref_path)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/upload-extend
# ------------------------------------------------------------------

@router.post("/generate/upload-extend")
async def upload_extend(req: UploadExtendRequest, _: AuthToken):
    """Extend a track from an uploaded audio URL."""
    try:
        src_path = _download_audio(str(req.uploadUrl))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=err(400, f"Failed to download uploadUrl: {exc}"))

    params, config = params_for_upload_extend(req, src_path)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/mashup
# ------------------------------------------------------------------

@router.post("/generate/mashup")
async def generate_mashup(req: GenerateMashupRequest, _: AuthToken):
    """Create a mashup by blending two uploaded audio files."""
    audio_paths = []
    for url in req.uploadUrlList:
        try:
            audio_paths.append(_download_audio(str(url)))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=err(400, f"Failed to download {url}: {exc}"))

    params, config = params_for_mashup(req, audio_paths)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/add-vocals
# ------------------------------------------------------------------

@router.post("/generate/add-vocals")
async def add_vocals(req: AddVocalsRequest, _: AuthToken):
    """Layer AI vocals on top of an existing instrumental track."""
    try:
        src_path = _download_audio(str(req.uploadUrl))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=err(400, f"Failed to download uploadUrl: {exc}"))

    params, config = params_for_add_vocals(req, src_path)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/add-instrumental
# ------------------------------------------------------------------

@router.post("/generate/add-instrumental")
async def add_instrumental(req: AddInstrumentalRequest, _: AuthToken):
    """Generate an instrumental backing track for a vocal stem."""
    try:
        src_path = _download_audio(str(req.uploadUrl))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=err(400, f"Failed to download uploadUrl: {exc}"))

    params, config = params_for_add_instrumental(req, src_path)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.GENERATE,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/sounds
# ------------------------------------------------------------------

@router.post("/generate/sounds")
async def generate_sounds(req: GenerateSoundsRequest, _: AuthToken):
    """Generate ambient sounds / loopable audio."""
    params, config = params_for_sounds(req)
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.SOUNDS,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    job = _make_generate_job(params, config, task.task_id)
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, job))
    return ok({"taskId": task.task_id})


# ------------------------------------------------------------------
# POST /api/v1/generate/get-timestamped-lyrics
# ------------------------------------------------------------------

@router.post("/generate/get-timestamped-lyrics")
async def get_timestamped_lyrics(req: GetTimestampedLyricsRequest, _: AuthToken):
    """Return timestamped lyrics for a completed track (best-effort)."""
    store = get_task_store()
    task = store.get_task(req.taskId)
    if task is None or task.status != TaskStatus.SUCCESS:
        raise HTTPException(status_code=404, detail=err(404, "Task not found or not completed"))

    response = task.response or {}
    suno_data = response.get("sunoData", [])
    # Find the matching audio entry
    entry = next((a for a in suno_data if a.get("id") == req.audioId), suno_data[0] if suno_data else None)
    lyrics_text = (entry or {}).get("prompt", "")

    # Build a basic aligned-words response from stored lyrics
    words = lyrics_text.split() if lyrics_text else []
    aligned = [{"word": w, "success": True, "startS": 0.0, "endS": 0.0, "palign": 0} for w in words]

    data = {
        "alignedWords": aligned,
        "waveformData": [],
        "hootCer": 0.0,
        "isStreamed": False,
    }
    return ok(data)


# ------------------------------------------------------------------
# POST /api/v1/generate/generate-persona
# ------------------------------------------------------------------

@router.post("/generate/generate-persona")
async def generate_persona(req: GeneratePersonaRequest, _: AuthToken):
    """Create a persona from a completed generation task.

    ACE-Step does not currently have a persona system; we return a synthetic
    personaId derived from the request so that callers can reference it.
    """
    import uuid
    persona_id = uuid.uuid4().hex
    data = {
        "personaId": persona_id,
        "name": req.name,
        "description": req.description,
    }
    return ok(data)


# ------------------------------------------------------------------
# GET /api/v1/generate/credit
# ------------------------------------------------------------------

@router.get("/generate/credit")
async def get_remaining_credits(_: AuthToken, settings: Settings = Depends(get_settings)):
    """Return the simulated credit balance."""
    return ok(settings.simulated_credits)


# ------------------------------------------------------------------
# Private helper
# ------------------------------------------------------------------

def _resolve_audio_path(audio_id: str, store) -> Optional[str]:
    """Delegate to service.resolve_audio_path for consistency."""
    return resolve_audio_path(audio_id, store)
