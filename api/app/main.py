"""FastAPI application entry point.

Assembles all routers, runs startup/shutdown lifecycle, and serves static audio files.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from app.config import get_settings
from app.models.common import err
from app.pipeline import get_pipeline
from app.routers import cover, generate, lyrics, style, video, vocal_removal, wav
from app.task_store import get_task_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise ACE-Step pipeline and task worker on startup."""
    settings = get_settings()
    logger.info("Starting ACE-Step Suno-compatible API…")

    pipeline = get_pipeline()
    try:
        pipeline.startup(settings)
    except Exception as exc:
        logger.error(f"Pipeline startup failed: {exc}")
        # Continue: endpoints that need the pipeline will return 503

    store = get_task_store()
    await store.start_worker()
    logger.info("Task worker started.")

    yield

    logger.info("Shutting down…")
    await store.stop_worker()
    logger.info("Task worker stopped.")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="ACE-Step Suno-Compatible API",
        version="1.5.0",
        description="100%% Suno-compatible music generation API powered by ACE-Step.",
        lifespan=lifespan,
    )

    # ── CORS ────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────────────────────────────────
    app.include_router(generate.router)
    app.include_router(lyrics.router)
    app.include_router(vocal_removal.router)
    app.include_router(wav.router)
    app.include_router(video.router)
    app.include_router(cover.router)
    app.include_router(style.router)

    # ── Static audio files ──────────────────────────────────────────────────
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/audio", StaticFiles(directory=str(output_dir)), name="audio")

    # ── Exception handlers ───────────────────────────────────────────────────
    @app.exception_handler(400)
    async def bad_request_handler(request: Request, exc):
        return JSONResponse(status_code=400, content=err(400, "Bad Request"))

    @app.exception_handler(401)
    async def unauthorized_handler(request: Request, exc):
        return JSONResponse(status_code=401, content=err(401, "Unauthorized"))

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(status_code=404, content=err(404, "Not Found"))

    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc):
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(status_code=500, content=err(500, "Internal Server Error"))

    # ── Health check ─────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health():
        """Returns service liveness status."""
        return {"status": "ok"}

    return app


app = create_app()
