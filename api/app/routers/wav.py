"""WAV conversion endpoints.

POST /api/v1/wav/generate    – convert stored audio to WAV
GET  /api/v1/wav/record-info – poll status
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import ConvertToWavRequest
from app.service import ensure_output_dir, resolve_audio_path
from app.task_store import TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["WAV"])


def _make_wav_job(req: ConvertToWavRequest, src_path: str, task_id: str):
    """Return a callable that converts audio to WAV."""

    def _job():
        save_dir = ensure_output_dir()
        out_path = str(Path(save_dir) / f"{task_id}.wav")

        # Convert using soundfile (available via librosa / torchaudio dependencies)
        try:
            import soundfile as sf

            data, samplerate = sf.read(src_path)
            sf.write(out_path, data, samplerate, format="WAV", subtype="PCM_16")
        except Exception as exc:
            logger.warning(f"soundfile conversion failed ({exc}), trying pydub fallback")
            from pydub import AudioSegment
            audio = AudioSegment.from_file(src_path)
            audio.export(out_path, format="wav")

        audio_url = f"/audio/{task_id}.wav"
        return {
            "taskId": task_id,
            "sunoData": [{
                "id": f"{task_id}_wav",
                "audioUrl": audio_url,
                "streamAudioUrl": audio_url,
                "status": "complete",
                "errorMessage": "",
            }],
        }

    return _job


@router.post("/wav/generate")
async def convert_to_wav(req: ConvertToWavRequest, _: AuthToken):
    """Convert a previously generated track to WAV format."""
    store = get_task_store()
    src_path = resolve_audio_path(req.audioId, store)
    if src_path is None:
        raise HTTPException(status_code=400, detail=err(400, f"audioId '{req.audioId}' not found"))

    task = store.create_task(
        task_type=TaskType.WAV,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    asyncio.create_task(store.enqueue(task.task_id, _make_wav_job(req, src_path, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/wav/record-info")
async def get_wav_details(taskId: str = Query(...), _: AuthToken = None):
    """Retrieve WAV conversion task status."""
    store = get_task_store()
    task = store.get_task(taskId)
    if task is None:
        raise HTTPException(status_code=404, detail=err(404, "Task not found"))

    return ok({
        "taskId": task.task_id,
        "param": task.param,
        "response": task.response,
        "status": task.status.value,
        "type": task.task_type.value,
        "errorCode": task.error_code,
        "errorMessage": task.error_message,
    })
