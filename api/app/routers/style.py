"""Style boost and MIDI endpoints.

POST /api/v1/style/generate     – boost / expand a style description
GET  /api/v1/midi/record-info   – poll MIDI task status (not-implemented stub)
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import BoostStyleRequest
from app.pipeline import get_pipeline
from app.task_store import TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Style"])


def _make_style_job(req: BoostStyleRequest, task_id: str):
    """Return a callable that boosts a style prompt using the LLM."""
    pipeline = get_pipeline()

    def _job():
        style_text = req.style or ""
        boosted = style_text  # default: return unchanged

        llm = pipeline.llm_handler
        if llm and llm.llm_initialized:
            try:
                # Use infer_type="dit" with a descriptive prompt to elicit a richer caption
                result = llm.generate_with_stop_condition(
                    caption=style_text,
                    lyrics="",
                    infer_type="dit",
                    temperature=0.9,
                    cfg_scale=2.0,
                    negative_prompt="NO USER INPUT",
                    use_cot_caption=True,
                    use_cot_language=False,
                    use_cot_metas=False,
                    batch_size=1,
                )
                metadata = result.get("metadata") or {}
                if isinstance(metadata, list):
                    metadata = metadata[0] if metadata else {}
                boosted = metadata.get("caption") or style_text
            except Exception as exc:
                logger.warning(f"Style boost LLM call failed: {exc}")

        return {
            "taskId": task_id,
            "data": {
                "original": style_text,
                "boosted": boosted,
                "status": "complete",
            },
        }

    return _job


@router.post("/style/generate")
async def boost_style(req: BoostStyleRequest, _: AuthToken):
    """Boost and expand a music style description using the LLM."""
    store = get_task_store()
    task = store.create_task(
        task_type=TaskType.LYRICS,          # reuse LYRICS worker type
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    asyncio.create_task(store.enqueue(task.task_id, _make_style_job(req, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/midi/record-info")
async def get_midi_details(taskId: str = Query(...), _: AuthToken = None):
    """MIDI conversion is not implemented; returns the stored task state."""
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
