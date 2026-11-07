"""Project-scoped asynchronous event delivery for workflow progress updates."""

import asyncio
import threading
from collections.abc import Mapping
from typing import Any


class ProjectEventManager:
    """Route workflow events to an asyncio queue for each project."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[dict[str, Any]]] = {}
        self._loops: dict[str, asyncio.AbstractEventLoop] = {}
        self._lock = threading.Lock()

    def subscribe(
        self,
        project_id: str,
        loop: asyncio.AbstractEventLoop,
    ) -> asyncio.Queue[dict[str, Any]]:
        """Create or reuse the queue associated with a project."""
        with self._lock:
            event_queue = self._queues.setdefault(project_id, asyncio.Queue())
            self._loops[project_id] = loop
            return event_queue

    def unsubscribe(self, project_id: str) -> None:
        """Release a project's queue after its stream has finished."""
        with self._lock:
            self._queues.pop(project_id, None)
            self._loops.pop(project_id, None)

    def publish(self, project_id: str, event: Mapping[str, Any]) -> None:
        """Publish an event from synchronous workflow code or a worker thread."""
        with self._lock:
            event_queue = self._queues.get(project_id)
            loop = self._loops.get(project_id)

        if event_queue is None or loop is None or loop.is_closed():
            return

        event_data = dict(event)
        loop.call_soon_threadsafe(event_queue.put_nowait, event_data)
