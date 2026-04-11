"""Music video (MP4) generation endpoints.

POST /api/v1/mp4/generate    – create a music video from audio
GET  /api/v1/mp4/record-info – poll status
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from app.auth import AuthToken
from app.models.common import ok, err
from app.models.requests import CreateMusicVideoRequest
from app.service import ensure_output_dir, resolve_audio_path
from app.task_store import TaskType, get_task_store

router = APIRouter(prefix="/api/v1", tags=["Video"])


def _make_video_job(req: CreateMusicVideoRequest, src_path: str, title: str, task_id: str):
    """Return a callable that generates a basic waveform music video."""

    def _job():
        save_dir = ensure_output_dir()
        out_path = str(Path(save_dir) / f"{task_id}.mp4")

        _render_waveform_video(src_path, out_path, title)

        video_url = f"/audio/{task_id}.mp4"
        return {
            "taskId": task_id,
            "sunoData": [{
                "id": f"{task_id}_mp4",
                "videoUrl": video_url,
                "streamVideoUrl": video_url,
                "status": "complete",
                "errorMessage": "",
            }],
        }

    return _job


def _render_waveform_video(audio_path: str, out_path: str, title: str) -> None:
    """Create a minimal MP4 with static title text and audio stream."""
    try:
        import subprocess
        import shutil

        if not shutil.which("ffmpeg"):
            raise RuntimeError("ffmpeg not found")

        # Draw the title on a black background and mux the audio
        safe_title = title[:60].replace(":", "\\\\:")
        filter_graph = (
            "[0:a]showwaves=s=1280x360:mode=line:colors=0x00cfff[v];"
            "[v]scale=1280:720:flags=lanczos,"
            "pad=1280:720:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawtext=text='{safe_title}':"
            "fontsize=36:fontcolor=white:x=(w-text_w)/2:y=40[out]"
        )
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", audio_path,
                "-filter_complex", filter_graph,
                "-map", "[out]", "-map", "0:a",
                "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest", out_path,
            ],
            check=True,
            capture_output=True,
        )
    except Exception as exc:
        logger.warning(f"Video render via ffmpeg failed: {exc}. Producing audio-only MP4.")
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-c:a", "aac", "-b:a", "192k", out_path],
            check=True,
            capture_output=True,
        )


@router.post("/mp4/generate")
async def create_music_video(req: CreateMusicVideoRequest, _: AuthToken):
    """Generate a music video MP4 from a previously generated audio track."""
    store = get_task_store()
    src_path = resolve_audio_path(req.audioId, store)
    if src_path is None:
        raise HTTPException(status_code=400, detail=err(400, f"audioId '{req.audioId}' not found"))

    # Retrieve title from original task response if not provided
    title = req.title or ""
    if not title:
        src_task = store.get_task(req.taskId)
        if src_task and src_task.response:
            for entry in (src_task.response or {}).get("sunoData", []):
                if entry.get("id") == req.audioId:
                    title = entry.get("title") or ""
                    break

    task = store.create_task(
        task_type=TaskType.MP4,
        param=req.model_dump_json(),
        callback_url=str(req.callBackUrl) if req.callBackUrl else None,
    )
    asyncio.create_task(store.enqueue(task.task_id, _make_video_job(req, src_path, title, task.task_id)))
    return ok({"taskId": task.task_id})


@router.get("/mp4/record-info")
async def get_mp4_details(taskId: str = Query(...), _: AuthToken = None):
    """Retrieve MP4 generation task status."""
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
