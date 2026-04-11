"""In-memory async task store with a background worker queue.

All heavy generation runs inside a ``ThreadPoolExecutor`` so they do not block
the asyncio event loop.  Tasks transition through these states:

    PENDING → GENERATING → (TEXT_SUCCESS →) FIRST_SUCCESS → SUCCESS
                                                           → FAILED
"""

from __future__ import annotations

import asyncio
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from loguru import logger


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    TEXT_SUCCESS = "TEXT_SUCCESS"
    FIRST_SUCCESS = "FIRST_SUCCESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CREATE_TASK_FAILED = "CREATE_TASK_FAILED"


class TaskType(str, Enum):
    GENERATE = "GENERATE"
    LYRICS = "LYRICS"
    VOCAL_REMOVAL = "VOCAL_REMOVAL"
    WAV = "WAV"
    MP4 = "MP4"
    COVER = "COVER"
    SOUNDS = "SOUNDS"


@dataclass
class Task:
    """A single tracked generation task."""

    task_id: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    param: str = ""           # JSON-serialised request params
    response: Optional[Any] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    callback_url: Optional[str] = None

    def touch(self) -> None:
        self.updated_at = time.time()


class TaskStore:
    """Thread-safe in-memory store + asyncio work queue."""

    def __init__(self, ttl_seconds: int = 1_296_000, max_workers: int = 1) -> None:
        self._tasks: Dict[str, Task] = {}
        self._ttl = ttl_seconds
        self._queue: asyncio.Queue = asyncio.Queue()
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="acestep-worker")
        self._worker_task: Optional[asyncio.Task] = None

    # ------------------------------------------------------------------
    # Public CRUD
    # ------------------------------------------------------------------

    def create_task(
        self,
        *,
        task_type: TaskType,
        param: str = "",
        callback_url: Optional[str] = None,
    ) -> Task:
        """Create a new PENDING task and return it."""
        task_id = uuid.uuid4().hex
        task = Task(
            task_id=task_id,
            task_type=task_type,
            param=param,
            callback_url=callback_url,
        )
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        *,
        status: Optional[TaskStatus] = None,
        response: Optional[Any] = None,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> None:
        task = self._tasks.get(task_id)
        if task is None:
            return
        if status is not None:
            task.status = status
        if response is not None:
            task.response = response
        if error_code is not None:
            task.error_code = error_code
        if error_message is not None:
            task.error_message = error_message
        task.touch()

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    # ------------------------------------------------------------------
    # Background worker
    # ------------------------------------------------------------------

    async def enqueue(self, task_id: str, fn: Callable[[], Any]) -> None:
        """Put a (task_id, fn) pair onto the work queue."""
        await self._queue.put((task_id, fn))

    async def _worker_loop(self) -> None:
        loop = asyncio.get_event_loop()
        while True:
            task_id, fn = await self._queue.get()
            task = self._tasks.get(task_id)
            if task is None:
                self._queue.task_done()
                continue

            self.update_task(task_id, status=TaskStatus.GENERATING)
            try:
                result = await loop.run_in_executor(self._executor, fn)
                self.update_task(task_id, status=TaskStatus.SUCCESS, response=result)
                if task.callback_url:
                    asyncio.create_task(_fire_callback(task.callback_url, task_id, result))
            except Exception as exc:
                logger.error(f"[task_store] Task {task_id} failed: {exc}")
                self.update_task(
                    task_id,
                    status=TaskStatus.FAILED,
                    error_code=500,
                    error_message=str(exc),
                )
                if task.callback_url:
                    asyncio.create_task(_fire_callback(task.callback_url, task_id, None, error=str(exc)))
            finally:
                self._queue.task_done()

    async def start_worker(self) -> None:
        """Start the background worker coroutine (call once from lifespan)."""
        self._worker_task = asyncio.create_task(self._worker_loop(), name="task-worker")
        logger.info("[task_store] Background worker started.")

    async def stop_worker(self) -> None:
        if self._worker_task:
            self._worker_task.cancel()
        self._executor.shutdown(wait=False)
        logger.info("[task_store] Background worker stopped.")

    def purge_expired(self) -> int:
        """Remove tasks older than TTL. Returns number of removed tasks."""
        deadline = time.time() - self._ttl
        expired = [tid for tid, t in self._tasks.items() if t.updated_at < deadline]
        for tid in expired:
            del self._tasks[tid]
        return len(expired)


# ------------------------------------------------------------------
# Callback delivery
# ------------------------------------------------------------------

async def _fire_callback(url: str, task_id: str, result: Any, error: Optional[str] = None) -> None:
    """POST task result to the caller's webhook URL."""
    try:
        import httpx
        payload = {"code": 200 if error is None else 500, "data": {"taskId": task_id, "data": result}}
        if error:
            payload["msg"] = error
            payload["code"] = 500
        else:
            payload["msg"] = "success"
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(str(url), json=payload)
    except Exception as exc:
        logger.warning(f"[task_store] Callback delivery failed for task {task_id}: {exc}")


# Module-level singleton
_store = TaskStore()


def get_task_store() -> TaskStore:
    """Return the global TaskStore singleton."""
    return _store
