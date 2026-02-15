"""Azure Blob Storage adapter for RAG documents"""

import asyncio
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _get_azure_config():
    return {
        "connection_string": os.getenv("AZURE_STORAGE_CONNECTION_STRING", ""),
        "account_name": os.getenv("AZURE_STORAGE_ACCOUNT_NAME", ""),
        "container_uploads": os.getenv("AZURE_RAG_UPLOADS_CONTAINER", "rag-uploads"),
        "container_parsed": os.getenv("AZURE_RAG_PARSED_CONTAINER", "rag-parsed"),
    }


class RAGAzureStorageService:
    """Azure Blob Storage adapter for RAG documents"""

    _instance: Optional["RAGAzureStorageService"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._config = _get_azure_config()
        self._client = None

    @classmethod
    async def get_instance(cls) -> "RAGAzureStorageService":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        from azure.storage.blob.aio import BlobServiceClient

        if self._config["connection_string"]:
            self._client = BlobServiceClient.from_connection_string(
                self._config["connection_string"]
            )
        elif self._config["account_name"]:
            from azure.identity.aio import DefaultAzureCredential
            credential = DefaultAzureCredential()
            account_url = f"https://{self._config['account_name']}.blob.core.windows.net"
            self._client = BlobServiceClient(account_url=account_url, credential=credential)
        else:
            raise ValueError("Azure storage not configured. Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_NAME")

        await self._ensure_container(self._config["container_uploads"])
        await self._ensure_container(self._config["container_parsed"])
        logger.info("RAG Azure Storage initialized")

    async def _ensure_container(self, container_name: str) -> None:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container_client = self._client.get_container_client(container_name)
        try:
            await container_client.create_container()
        except Exception as e:
            if "ContainerAlreadyExists" not in str(e):
                raise

    @property
    def upload_dir(self) -> Path:
        return Path(os.getenv("RAG_UPLOAD_DIR", "./rag_uploads"))

    @property
    def parsed_dir(self) -> Path:
        return Path(os.getenv("RAG_PARSER_OUTPUT_DIR", "./rag_parsed"))

    @property
    def working_dir(self) -> Path:
        return Path(os.getenv("RAG_WORKING_DIR", "./rag_storage"))

    async def save_upload(self, data: bytes, filename: str) -> str:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_uploads"])
        blob_client = container.get_blob_client(filename)
        await blob_client.upload_blob(data, overwrite=True)
        logger.info(f"Saved upload to Azure: {filename}")
        return filename

    async def save_upload_from_stream(self, stream: BytesIO, filename: str) -> str:
        stream.seek(0)
        data = stream.read()
        return await self.save_upload(data, filename)

    async def get_upload(self, filename: str) -> bytes:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_uploads"])
        blob_client = container.get_blob_client(filename)
        stream = await blob_client.download_blob()
        return await stream.readall()

    async def delete_upload(self, filename: str) -> bool:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_uploads"])
        blob_client = container.get_blob_client(filename)
        try:
            await blob_client.delete_blob()
            return True
        except Exception:
            return False

    async def save_parsed(self, doc_id: str, text: str) -> str:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_parsed"])
        blob_name = f"{doc_id}.txt"
        blob_client = container.get_blob_client(blob_name)
        await blob_client.upload_blob(text, overwrite=True, encoding="utf-8")
        logger.info(f"Saved parsed to Azure: {blob_name}")
        return blob_name

    async def get_parsed(self, doc_id: str) -> Optional[str]:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_parsed"])
        blob_name = f"{doc_id}.txt"
        blob_client = container.get_blob_client(blob_name)
        try:
            stream = await blob_client.download_blob()
            data = await stream.readall()
            return data.decode("utf-8")
        except Exception:
            return None

    async def delete_parsed(self, doc_id: str) -> bool:
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(self._config["container_parsed"])
        blob_name = f"{doc_id}.txt"
        blob_client = container.get_blob_client(blob_name)
        try:
            await blob_client.delete_blob()
            return True
        except Exception:
            return False

    def get_upload_path(self, filename: str) -> Path:
        return self.upload_dir / filename

    def get_parsed_path(self, doc_id: str) -> Path:
        return self.parsed_dir / f"{doc_id}.txt"

    async def file_exists(self, filename: str, category: str = "upload") -> bool:
        container_name = (
            self._config["container_uploads"] if category == "upload"
            else self._config["container_parsed"]
        )
        if self._client is None:
            raise RuntimeError("Azure BlobServiceClient not initialized")
        container = self._client.get_container_client(container_name)
        blob_client = container.get_blob_client(filename)
        try:
            await blob_client.get_blob_properties()
            return True
        except Exception:
            return False

    async def health_check(self) -> dict[str, str]:
        try:
            if self._client is None:
                raise RuntimeError("Azure BlobServiceClient not initialized")
            await self._client.get_account_information()
            return {
                "status": "healthy",
                "backend": "azure",
                "container_uploads": self._config["container_uploads"],
                "container_parsed": self._config["container_parsed"],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            logger.info("RAG Azure Storage closed")
