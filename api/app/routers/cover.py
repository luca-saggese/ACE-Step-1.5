"""Cover art generation endpoints.

POST /api/v1/suno/cover/generate    – generate album cover art
GET  /api/v1/suno/cover/record-info – poll status
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import GenerateCoverRequest
from app.service import ensure_output_dir
from app.task_store import TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Cover"])


def _make_cover_job(req: GenerateCoverRequest, prompt: str, style: str | None, task_id: str):
    """Return a callable that generates album cover art."""

    def _job():
        save_dir = ensure_output_dir()
        img_path = str(Path(save_dir) / f"{task_id}_cover.png")

        _generate_cover_image(prompt, style, img_path)

        img_url = f"/audio/{task_id}_cover.png"
        return {
            "taskId": task_id,
            "sunoData": [{
                "id": f"{task_id}_cover",
                "imageUrl": img_url,
                "status": "complete",
                "errorMessage": "",
            }],
        }

    return _job


def _generate_cover_image(prompt: str, style: str | None, out_path: str) -> None:
    """Generate a cover image; falls back to a solid-colour placeholder."""
    full_prompt = f"{style} — {prompt}" if style else prompt

    # Try diffusion-based local generation (optional dependency)
    try:
        from diffusers import StableDiffusionPipeline  # noqa: F401 – optional
        import torch
        pipe = StableDiffusionPipeline.from_pretrained(
            "stabilityai/stable-diffusion-2-1-base",
            torch_dtype=torch.float16,
            safety_checker=None,
        ).to("cuda" if torch.cuda.is_available() else "cpu")
        image = pipe(full_prompt, num_inference_steps=20).images[0]
        image.save(out_path)
        return
    except Exception as exc:
        logger.debug(f"SD cover generation skipped: {exc}")

    # Fallback: create a simple gradient placeholder with PIL
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (512, 512), color=(30, 30, 45))
        draw = ImageDraw.Draw(img)
        draw.text((20, 230), full_prompt[:60], fill=(200, 200, 220))
        img.save(out_path)
        return
    except Exception as exc:
        logger.debug(f"PIL cover generation skipped: {exc}")

    # Last resort: write empty PNG (1×1 black pixel)
    import struct, zlib
    def _png_1x1() -> bytes:
        header = b"\x89PNG\r\n\x1a\n"
        def chunk(n, d):
            c = zlib.crc32(n + d) & 0xFFFFFFFF
            return struct.pack(">I", len(d)) + n + d + struct.pack(">I", c)
        ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        idat = chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00"))
        iend = chunk(b"IEND", b"")
        return header + ihdr + idat + iend
    Path(out_path).write_bytes(_png_1x1())


@router.post("/suno/cover/generate")
async def generate_cover(req: GenerateCoverRequest, _: AuthToken):
    """Generate album cover art; derives prompt from the referenced generation task."""
    store = get_task_store()

    # Use explicit prompt if provided, otherwise pull from original task
    prompt = req.prompt or ""
    style = req.style
    if not prompt:
        src_task = store.get_task(req.taskId)
        if src_task and src_task.response:
            first = (src_task.response.get("sunoData") or [{}])[0]
            prompt = first.get("tags") or first.get("prompt") or ""
            if not style:
                style = first.get("tags") or None

    task = store.create_task(
        task_type=TaskType.COVER,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    asyncio.create_task(store.enqueue(task.task_id, _make_cover_job(req, prompt, style, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/suno/cover/record-info")
async def get_cover_details(taskId: str = Query(...), _: AuthToken = None):
    """Retrieve cover art generation task status."""
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
