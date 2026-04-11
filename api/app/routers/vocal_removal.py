"""Vocal removal / stem separation endpoints.

POST /api/v1/vocal-removal/generate    – separate vocals or stems
GET  /api/v1/vocal-removal/record-info – poll status
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import SeparateVocalsRequest
from app.pipeline import get_pipeline
from app.service import build_suno_audio_data, ensure_output_dir, resolve_audio_path
from app.task_store import TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Vocal Removal"])


def _make_vocal_removal_job(req: SeparateVocalsRequest, src_path: str, task_id: str):
    """Return a callable that runs vocal/stem separation via ACE-Step."""
    pipeline = get_pipeline()

    def _job():
        save_dir = ensure_output_dir()

        from acestep.inference import GenerationParams, GenerationConfig  # noqa: PLC0415

        params = GenerationParams(
            task_type="extract",
            src_audio=src_path,
            caption="",
            lyrics="[Instrumental]",
            instrumental=True,
        )
        config = GenerationConfig(batch_size=1, audio_format=pipeline.settings.audio_format)
        result = pipeline.generate(params, config, save_dir)

        if not result.success:
            raise RuntimeError(result.error or "Vocal removal failed")

        items = [build_suno_audio_data(audio, i) for i, audio in enumerate(result.audios or [])]
        return {"taskId": task_id, "sunoData": items}

    return _job


@router.post("/vocal-removal/generate")
async def separate_vocals(req: SeparateVocalsRequest, _: AuthToken):
    """Separate vocals or stems from a previously generated audio track."""
    store = get_task_store()
    src_path = resolve_audio_path(req.audioId, store)
    if src_path is None:
        raise HTTPException(status_code=400, detail=err(400, f"audioId '{req.audioId}' not found"))

    task = store.create_task(
        task_type=TaskType.VOCAL_REMOVAL,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    asyncio.create_task(store.enqueue(task.task_id, _make_vocal_removal_job(req, src_path, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/vocal-removal/record-info")
async def get_vocal_removal_details(
    taskId: str = Query(...),
    _: AuthToken = None,
):
    """Retrieve vocal removal task status and output paths."""
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
