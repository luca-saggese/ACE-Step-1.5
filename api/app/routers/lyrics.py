"""Lyrics generation endpoints.

POST /api/v1/lyrics             – generate lyrics
GET  /api/v1/lyrics/record-info – poll lyrics task status
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import GenerateLyricsRequest
from app.pipeline import get_pipeline
from app.service import ensure_output_dir
from app.task_store import TaskStatus, TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Lyrics"])


def _make_lyrics_job(prompt: str, task_id: str):
    """Return a callable that generates lyrics via ACE-Step's LLM."""
    pipeline = get_pipeline()

    def _job():
        llm = pipeline.llm_handler
        if llm is None or not llm.llm_initialized:
            raise RuntimeError("LLM not initialised; cannot generate lyrics.")

        # Use generate_with_stop_condition with infer_type="dit" to get metadata (incl. lyrics)
        # without generating audio codes, saving significant time and VRAM.
        result = llm.generate_with_stop_condition(
            caption=prompt,
            lyrics="",
            infer_type="dit",
            temperature=0.85,
            cfg_scale=2.0,
            negative_prompt="NO USER INPUT",
            use_cot_caption=True,
            use_cot_language=True,
            use_cot_metas=True,
            batch_size=1,
        )

        metadata = result.get("metadata") or {}
        if isinstance(metadata, list):
            metadata = metadata[0] if metadata else {}

        generated_lyrics = (
            metadata.get("lyrics")
            or metadata.get("cot_lyrics")
            or ""
        )
        title = metadata.get("caption") or prompt[:40]

        items = [{
            "text": generated_lyrics,
            "title": title,
            "status": "complete",
            "errorMessage": "",
        }]
        return {"taskId": task_id, "data": items}

    return _job


@router.post("/lyrics")
async def generate_lyrics(req: GenerateLyricsRequest, _: AuthToken):
    """Generate AI-powered lyrics from a prompt."""
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.LYRICS,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl),
    )
    import asyncio
    asyncio.create_task(store.enqueue(task.task_id, _make_lyrics_job(req.prompt, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/lyrics/record-info")
async def get_lyrics_details(
    taskId: str = Query(...),
    _: AuthToken = None,
):
    """Retrieve detailed status of a lyrics generation task."""
    store = get_task_store()
    task = store.get_task(taskId)
    if task is None:
        raise HTTPException(status_code=404, detail=err(404, "Task not found"))

    data = {
        "taskId": task.task_id,
        "param": task.param,
        "response": task.response,
        "status": task.status.value,
        "type": task.task_type.value,
        "errorCode": task.error_code,
        "errorMessage": task.error_message,
    }
    return ok(data)
