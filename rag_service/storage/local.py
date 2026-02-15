"""Local filesystem storage service for RAG documents"""

import asyncio
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class RAGLocalStorageService:
    """Async-compatible local filesystem storage for RAG documents"""

    _instance: Optional["RAGLocalStorageService"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._base_path: Path = Path(os.getenv("RAG_STORAGE_BASE_DIR", "./rag_base"))
        self._upload_dir: Path = self._base_path / "rag_uploads"
        self._parsed_dir: Path = self._base_path / "rag_parsed"
        self._working_dir: Path = self._base_path / "rag_storage"

    @classmethod
    async def get_instance(cls) -> "RAGLocalStorageService":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._parsed_dir.mkdir(parents=True, exist_ok=True)
        self._working_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"RAG Local Storage initialized (upload: {self._upload_dir}, parsed: {self._parsed_dir})")

    @property
    def upload_dir(self) -> Path:
        return self._upload_dir

    @property
    def parsed_dir(self) -> Path:
        return self._parsed_dir

    @property
    def working_dir(self) -> Path:
        return self._working_dir

    async def save_upload(
        self,
        data: bytes,
        filename: str,
    ) -> str:
        """Save uploaded file and return relative path"""
        file_path = self._upload_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(data)
        logger.info(f"Saved upload: {file_path}")
        return filename

    async def save_upload_from_stream(
        self,
        stream: BytesIO,
        filename: str,
    ) -> str:
        """Save uploaded file from stream"""
        stream.seek(0)
        data = stream.read()
        return await self.save_upload(data, filename)

    async def get_upload(self, filename: str) -> bytes:
        """Read uploaded file"""
        file_path = self._upload_dir / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Upload not found: {filename}")
        return file_path.read_bytes()

    async def delete_upload(self, filename: str) -> bool:
        """Delete uploaded file"""
        file_path = self._upload_dir / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted upload: {file_path}")
            return True
        return False

    async def save_parsed(self, doc_id: str, text: str) -> str:
        """Save parsed text content"""
        file_path = self._parsed_dir / f"{doc_id}.txt"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text, encoding="utf-8", errors="ignore")
        logger.info(f"Saved parsed text: {file_path}")
        return str(file_path)

    async def get_parsed(self, doc_id: str) -> Optional[str]:
        """Read parsed text content"""
        file_path = self._parsed_dir / f"{doc_id}.txt"
        if not file_path.exists():
            return None
        return file_path.read_text(encoding="utf-8", errors="ignore")

    async def delete_parsed(self, doc_id: str) -> bool:
        """Delete parsed text file"""
        file_path = self._parsed_dir / f"{doc_id}.txt"
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted parsed: {file_path}")
            return True
        return False

    def get_upload_path(self, filename: str) -> Path:
        """Get full path for upload file (for extraction code)"""
        return self._upload_dir / filename

    def get_parsed_path(self, doc_id: str) -> Path:
        """Get full path for parsed file"""
        return self._parsed_dir / f"{doc_id}.txt"

    async def file_exists(self, filename: str, category: str = "upload") -> bool:
        """Check if file exists in given category"""
        if category == "upload":
            return (self._upload_dir / filename).exists()
        elif category == "parsed":
            return (self._parsed_dir / filename).exists()
        return False

    async def health_check(self) -> dict[str, str]:
        try:
            if self._upload_dir.exists() and os.access(self._upload_dir, os.W_OK):
                return {
                    "status": "healthy",
                    "backend": "local",
                    "upload_dir": str(self._upload_dir),
                    "parsed_dir": str(self._parsed_dir),
                }
            return {"status": "error", "message": "Storage path not writable"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        logger.info("RAG Local Storage closed")
