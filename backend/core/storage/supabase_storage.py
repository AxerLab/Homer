"""Supabase Storage Service for presentation file management"""

import asyncio
import json as json_lib
import logging
from io import BytesIO
from typing import Optional

import httpx

from ...config.storage_config import storage_config

logger = logging.getLogger(__name__)


class SupabaseStorageService:
    """Async Supabase Storage service with connection pooling"""

    _instance: Optional["SupabaseStorageService"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None
        self._base_url: str = ""
        self._bucket: str = ""

    @classmethod
    async def get_instance(cls) -> "SupabaseStorageService":
        """Get singleton instance of SupabaseStorageService"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        if not storage_config.supabase_url or not storage_config.supabase_service_key:
            raise ValueError(
                "Supabase storage not configured. Set SUPABASE_URL and SUPABASE_SERVICE_KEY"
            )

        self._base_url = f"{storage_config.supabase_url.rstrip('/')}/storage/v1"
        self._bucket = storage_config.supabase_bucket
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {storage_config.supabase_service_key}",
                "apikey": storage_config.supabase_service_key,
            },
            timeout=httpx.Timeout(60.0),
        )

        await self._ensure_bucket_exists()
        logger.info(
            f"Supabase Storage Service initialized "
            f"(url: {storage_config.supabase_url}, bucket: {self._bucket})"
        )

    async def _ensure_bucket_exists(self) -> None:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        try:
            resp = await self._client.post(
                f"{self._base_url}/bucket",
                json={"id": self._bucket, "name": self._bucket, "public": False},
            )
            if resp.status_code == 200:
                logger.info(f"Created Supabase bucket: {self._bucket}")
            elif resp.status_code == 409:
                logger.debug(f"Supabase bucket already exists: {self._bucket}")
            else:
                resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise

    async def upload_presentation(
        self,
        data: bytes,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        try:
            resp = await self._client.post(
                f"{self._base_url}/object/{self._bucket}/{blob_name}",
                content=data,
                headers={
                    "Content-Type": content_type,
                    "x-upsert": "true",
                },
            )
            resp.raise_for_status()
            logger.info(f"Uploaded to Supabase: {self._bucket}/{blob_name}")
            return f"{self._bucket}/{blob_name}"
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to upload {blob_name}: {e}")
            raise

    async def upload_from_stream(
        self,
        stream: BytesIO,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        stream.seek(0)
        data = stream.read()
        return await self.upload_presentation(data, blob_name, content_type)

    async def download_presentation(self, blob_name: str) -> bytes:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        try:
            resp = await self._client.get(
                f"{self._base_url}/object/{self._bucket}/{blob_name}"
            )
            resp.raise_for_status()
            logger.debug(f"Downloaded from Supabase: {self._bucket}/{blob_name}")
            return resp.content
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to download {blob_name}: {e}")
            raise

    async def delete_presentation(self, blob_name: str) -> bool:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        try:
            resp = await self._client.request(
                "DELETE",
                f"{self._base_url}/object/{self._bucket}",
                content=json_lib.dumps({"prefixes": [blob_name]}).encode(),
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            logger.info(f"Deleted from Supabase: {self._bucket}/{blob_name}")
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Object not found for deletion: {self._bucket}/{blob_name}")
                return False
            logger.error(f"Failed to delete {blob_name}: {e}")
            raise

    async def generate_download_url(
        self,
        blob_name: str,
        expiry_minutes: Optional[int] = None,
    ) -> str:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        expiry_seconds = (expiry_minutes or storage_config.sas_expiry_minutes) * 60

        try:
            resp = await self._client.post(
                f"{self._base_url}/object/sign/{self._bucket}/{blob_name}",
                json={"expiresIn": expiry_seconds},
            )
            resp.raise_for_status()
            signed_path = resp.json().get("signedURL", "")
            url = f"{storage_config.supabase_url.rstrip('/')}/storage/v1{signed_path}"
            logger.debug(
                f"Generated signed URL for {blob_name} "
                f"(expires in {expiry_minutes or storage_config.sas_expiry_minutes} min)"
            )
            return url
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to generate signed URL for {blob_name}: {e}")
            raise

    async def blob_exists(self, blob_name: str) -> bool:
        if not self._client:
            raise RuntimeError("Supabase Storage Service not initialized")

        try:
            resp = await self._client.head(
                f"{self._base_url}/object/{self._bucket}/{blob_name}"
            )
            return resp.status_code == 200
        except httpx.HTTPError:
            return False

    async def health_check(self) -> dict[str, str]:
        if not self._client:
            return {"status": "error", "message": "Not initialized"}

        try:
            resp = await self._client.get(f"{self._base_url}/bucket/{self._bucket}")
            resp.raise_for_status()
            return {
                "status": "healthy",
                "backend": "supabase",
                "bucket": self._bucket,
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {
                    "status": "warning",
                    "message": f"Bucket {self._bucket} does not exist",
                }
            return {"status": "error", "message": str(e)}
        except httpx.HTTPError as e:
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
            logger.info("Supabase Storage Service closed")
