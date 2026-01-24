"""SSE (Server-Sent Events) broadcaster for document processing progress"""

import asyncio
import json
from typing import Dict, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum


class ProgressStage(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressEvent:
    doc_id: str
    progress: int
    stage: str
    message: str
    error: Optional[str] = None

    def to_sse(self) -> str:
        data = json.dumps(asdict(self))
        return f"data: {data}\n\n"


ProgressCallback = Callable[[str, int, str, str], None]


class SSEConnectionManager:
    def __init__(self) -> None:
        self._connections: Dict[str, list[asyncio.Queue[ProgressEvent]]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, doc_id: str) -> asyncio.Queue[ProgressEvent]:
        async with self._lock:
            if doc_id not in self._connections:
                self._connections[doc_id] = []
            queue: asyncio.Queue[ProgressEvent] = asyncio.Queue()
            self._connections[doc_id].append(queue)
            return queue

    async def disconnect(
        self, doc_id: str, queue: asyncio.Queue[ProgressEvent]
    ) -> None:
        async with self._lock:
            if doc_id in self._connections:
                try:
                    self._connections[doc_id].remove(queue)
                    if not self._connections[doc_id]:
                        del self._connections[doc_id]
                except ValueError:
                    pass

    async def broadcast(self, event: ProgressEvent) -> None:
        async with self._lock:
            queues = self._connections.get(event.doc_id, [])
            for queue in queues:
                try:
                    await queue.put(event)
                except Exception:
                    pass

    def get_progress_callback(self, doc_id: str) -> ProgressCallback:
        def callback(doc_id: str, progress: int, stage: str, message: str) -> None:
            event = ProgressEvent(
                doc_id=doc_id, progress=progress, stage=stage, message=message
            )
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(self.broadcast(event), loop)
            except RuntimeError:
                pass

        return callback

    async def send_progress(
        self,
        doc_id: str,
        progress: int,
        stage: ProgressStage,
        message: str,
        error: Optional[str] = None,
    ) -> None:
        event = ProgressEvent(
            doc_id=doc_id,
            progress=progress,
            stage=stage.value,
            message=message,
            error=error,
        )
        await self.broadcast(event)


sse_manager = SSEConnectionManager()


async def sse_event_generator(
    doc_id: str, manager: SSEConnectionManager
) -> AsyncGenerator[str, None]:
    queue = await manager.connect(doc_id)
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield event.to_sse()

                if event.stage in (
                    ProgressStage.COMPLETED.value,
                    ProgressStage.FAILED.value,
                ):
                    break
            except asyncio.TimeoutError:
                yield ": keepalive\n\n"
    finally:
        await manager.disconnect(doc_id, queue)
