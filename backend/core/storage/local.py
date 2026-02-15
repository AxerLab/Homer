"""Local filesystem storage service for presentation file management"""

import asyncio
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

from ...config.storage_config import storage_config

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Async-compatible local filesystem storage service"""

    _instance: Optional["LocalStorageService"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._base_path: Path = Path(storage_config.local_output_dir)

    @property
    def base_path(self) -> Path:
        return self._base_path

    @classmethod
    async def get_instance(cls) -> "LocalStorageService":
        """Get singleton instance of LocalStorageService"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Ensure base directories exist"""
        self._base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Local Storage Service initialized (path: {self._base_path})")

    async def upload_presentation(
        self,
        data: bytes,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Write file to local filesystem.

        Args:
            data: File bytes to write
            blob_name: Relative path (e.g., "pptx/uuid.pptx")
            content_type: MIME type (unused for local, kept for interface compat)

        Returns:
            Relative path of the written file
        """
        file_path = self._base_path / blob_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_path.write_bytes(data)
        logger.info(f"Saved file locally: {file_path}")
        return blob_name

    async def upload_from_stream(
        self,
        stream: BytesIO,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """Upload from BytesIO stream"""
        stream.seek(0)
        data = stream.read()
        return await self.upload_presentation(data, blob_name, content_type)

    async def download_presentation(self, blob_name: str) -> bytes:
        """
        Read file from local filesystem.

        Args:
            blob_name: Relative path (e.g., "pptx/uuid.pptx")

        Returns:
            File bytes
        """
        file_path = self._base_path / blob_name
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        data = file_path.read_bytes()
        logger.debug(f"Read local file: {file_path}")
        return data

    async def delete_presentation(self, blob_name: str) -> bool:
        """
        Delete file from local filesystem.

        Args:
            blob_name: Relative path (e.g., "pptx/uuid.pptx")

        Returns:
            True if deleted, False if not found
        """
        file_path = self._base_path / blob_name
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted local file: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False

    def generate_download_url(
        self,
        blob_name: str,
        expiry_minutes: Optional[int] = None,
    ) -> str:
        """
        Generate a local download URL (served via StaticFiles mount).

        Args:
            blob_name: Relative path (e.g., "pptx/uuid.pptx")
            expiry_minutes: Unused for local storage

        Returns:
            URL path for the static file mount
        """
        return f"/{self._base_path}/{blob_name}"

    async def blob_exists(self, blob_name: str) -> bool:
        """Check if a file exists locally"""
        file_path = self._base_path / blob_name
        return file_path.exists()

    async def health_check(self) -> dict[str, str]:
        """Check local storage health"""
        try:
            if self._base_path.exists() and os.access(self._base_path, os.W_OK):
                return {
                    "status": "healthy",
                    "backend": "local",
                    "path": str(self._base_path),
                }
            else:
                return {
                    "status": "error",
                    "message": f"Path {self._base_path} not writable",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        """No-op for local storage"""
        logger.info("Local Storage Service closed")