"""Singleton wrapper around AceStepHandler + LLMHandler.

Initialised once at application startup via ``startup()``.
All routers obtain handles via ``get_pipeline()``.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from loguru import logger

# Make sure the ACE-Step package root is importable when running from /api/
_API_DIR = Path(__file__).resolve().parent.parent      # …/api/
_PROJECT_ROOT = _API_DIR.parent                         # …/ACE-Step-1.5/
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from acestep.handler import AceStepHandler              # noqa: E402
from acestep.llm_inference import LLMHandler            # noqa: E402
from acestep.inference import (                          # noqa: E402
    GenerationConfig,
    GenerationParams,
    GenerationResult,
    generate_music,
)

from app.config import Settings


class AceStepPipeline:
    """Holds the initialised handlers and exposes a single ``generate`` method."""

    def __init__(self) -> None:
        self.dit_handler: Optional[AceStepHandler] = None
        self.llm_handler: Optional[LLMHandler] = None
        self._ready: bool = False
        self._error: Optional[str] = None

    # ------------------------------------------------------------------
    # Startup / teardown
    # ------------------------------------------------------------------

    def startup(self, settings: Settings) -> None:
        """Initialise DiT + (optionally) LLM handlers from *settings*.

        Raises:
            RuntimeError: if DiT initialisation fails.
        """
        project_root = str(_PROJECT_ROOT)
        checkpoint_dir = os.path.join(project_root, "checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)

        # --- DiT handler ---
        self.dit_handler = AceStepHandler()
        flash = settings.use_flash_attention
        if flash is None:
            flash = self.dit_handler.is_flash_attention_available(settings.device)

        logger.info(f"[pipeline] Initialising DiT model '{settings.config_path}' on device '{settings.device}'")
        status_msg, ok = self.dit_handler.initialize_service(
            project_root=project_root,
            config_path=settings.config_path,
            device=settings.device,
            use_flash_attention=flash,
            compile_model=settings.compile_model,
            offload_to_cpu=settings.offload_to_cpu,
            offload_dit_to_cpu=settings.offload_dit_to_cpu,
        )
        if not ok:
            self._error = status_msg
            raise RuntimeError(f"DiT init failed: {status_msg}")
        logger.info(f"[pipeline] DiT ready: {status_msg}")

        # --- LLM handler (optional) ---
        self.llm_handler = LLMHandler()
        if settings.init_llm and settings.lm_model_path:
            logger.info(f"[pipeline] Initialising LLM '{settings.lm_model_path}' backend='{settings.lm_backend}'")
            lm_status, lm_ok = self.llm_handler.initialize(
                checkpoint_dir=checkpoint_dir,
                lm_model_path=settings.lm_model_path,
                backend=settings.lm_backend,
                device=settings.device,
            )
            if not lm_ok:
                logger.warning(f"[pipeline] LLM init failed (running without LLM): {lm_status}")
            else:
                logger.info(f"[pipeline] LLM ready: {lm_status}")
        else:
            logger.info("[pipeline] LLM disabled by settings.")

        self._ready = True

    def shutdown(self) -> None:
        """Release model resources."""
        self.dit_handler = None
        self.llm_handler = None
        self._ready = False

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    def generate(
        self,
        params: GenerationParams,
        config: GenerationConfig,
        save_dir: Optional[str] = None,
    ) -> GenerationResult:
        """Run synchronous music generation.

        Args:
            params: ``GenerationParams`` populated by the request handler.
            config: ``GenerationConfig`` (batch size, format, seeds …).
            save_dir: Directory where output audio files are stored.

        Returns:
            ``GenerationResult`` with ``audios`` list on success.

        Raises:
            RuntimeError: if the pipeline is not ready.
        """
        if not self._ready:
            raise RuntimeError("Pipeline not initialised. Call startup() first.")
        return generate_music(
            dit_handler=self.dit_handler,
            llm_handler=self.llm_handler,
            params=params,
            config=config,
            save_dir=save_dir,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def ready(self) -> bool:
        return self._ready

    @property
    def error(self) -> Optional[str]:
        return self._error

    @property
    def settings(self) -> Settings:
        """Return the application settings singleton."""
        from app.config import get_settings
        return get_settings()


# Module-level singleton
_pipeline = AceStepPipeline()


def get_pipeline() -> AceStepPipeline:
    """Return the global pipeline singleton."""
    return _pipeline
