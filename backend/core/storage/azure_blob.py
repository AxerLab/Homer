"""Azure Blob Storage Service for presentation file management"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from io import BytesIO
from typing import Optional

from azure.core.exceptions import AzureError, ResourceNotFoundError
from azure.storage.blob import BlobSasPermissions, ContentSettings, generate_blob_sas
from azure.storage.blob.aio import BlobServiceClient

from ...config.storage_config import storage_config

logger = logging.getLogger(__name__)


class AzureBlobService:
    """Async Azure Blob Storage service with connection pooling"""

    _instance: Optional["AzureBlobService"] = None
    _lock: asyncio.Lock = asyncio.Lock()

    def __init__(self) -> None:
        self._client: Optional[BlobServiceClient] = None
        self._account_key: Optional[str] = None

    @classmethod
    async def get_instance(cls) -> "AzureBlobService":
        """Get singleton instance of AzureBlobService"""
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance._initialize()
        return cls._instance

    async def _initialize(self) -> None:
        """Initialize the blob service client"""
        if storage_config.azure_connection_string:
            self._client = BlobServiceClient.from_connection_string(
                storage_config.azure_connection_string
            )
            # Extract account key from connection string for SAS generation
            self._account_key = self._extract_account_key(
                storage_config.azure_connection_string
            )
            logger.info(
                f"Azure Blob Service initialized with connection string "
                f"(account: {storage_config.azure_account_name or 'from-conn-string'})"
            )
        elif storage_config.azure_account_name:
            # Use DefaultAzureCredential for production
            from azure.identity.aio import DefaultAzureCredential

            credential = DefaultAzureCredential()
            self._client = BlobServiceClient(
                account_url=storage_config.azure_account_url, credential=credential
            )
            logger.info(
                f"Azure Blob Service initialized with DefaultAzureCredential "
                f"(account: {storage_config.azure_account_name})"
            )
        else:
            raise ValueError(
                "Azure storage not configured. Set AZURE_STORAGE_CONNECTION_STRING "
                "or AZURE_STORAGE_ACCOUNT_NAME"
            )

    @staticmethod
    def _extract_account_key(connection_string: str) -> Optional[str]:
        """Extract account key from connection string for SAS generation"""
        for part in connection_string.split(";"):
            if part.startswith("AccountKey="):
                return part[len("AccountKey=") :]
        return None

    @staticmethod
    def _extract_account_name(connection_string: str) -> Optional[str]:
        """Extract account name from connection string"""
        for part in connection_string.split(";"):
            if part.startswith("AccountName="):
                return part[len("AccountName=") :]
        return None

    async def upload_presentation(
        self,
        data: bytes,
        blob_name: str,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        Upload presentation file to Azure Blob Storage.

        Args:
            data: File bytes to upload
            blob_name: Name of the blob (e.g., "pptx/uuid.pptx")
            content_type: MIME type of the file

        Returns:
            Blob path (container/blob_name)
        """
        if not self._client:
            raise RuntimeError("Azure Blob Service not initialized")

        container_name = storage_config.azure_container_presentations
        container_client = self._client.get_container_client(container_name)

        # Ensure container exists
        try:
            await container_client.create_container()
            logger.debug(f"Created container: {container_name}")
        except AzureError as e:
            if "ContainerAlreadyExists" not in str(e):
                raise

        blob_client = container_client.get_blob_client(blob_name)

        try:
            await blob_client.upload_blob(
                data,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )
            logger.info(f"Uploaded blob: {container_name}/{blob_name}")
            return f"{container_name}/{blob_name}"
        except AzureError as e:
            logger.error(f"Failed to upload blob {blob_name}: {e}")
            raise

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
        Download presentation file from Azure Blob Storage.

        Args:
            blob_name: Name of the blob (e.g., "pptx/uuid.pptx")

        Returns:
            File bytes
        """
        if not self._client:
            raise RuntimeError("Azure Blob Service not initialized")

        container_name = storage_config.azure_container_presentations
        container_client = self._client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        try:
            download_stream = await blob_client.download_blob()
            data = await download_stream.readall()
            logger.debug(f"Downloaded blob: {container_name}/{blob_name}")
            return data
        except ResourceNotFoundError:
            logger.error(f"Blob not found: {container_name}/{blob_name}")
            raise
        except AzureError as e:
            logger.error(f"Failed to download blob {blob_name}: {e}")
            raise

    async def delete_presentation(self, blob_name: str) -> bool:
        """
        Delete presentation file from Azure Blob Storage.

        Args:
            blob_name: Name of the blob (e.g., "pptx/uuid.pptx")

        Returns:
            True if deleted, False if not found
        """
        if not self._client:
            raise RuntimeError("Azure Blob Service not initialized")

        container_name = storage_config.azure_container_presentations
        container_client = self._client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        try:
            await blob_client.delete_blob()
            logger.info(f"Deleted blob: {container_name}/{blob_name}")
            return True
        except ResourceNotFoundError:
            logger.warning(f"Blob not found for deletion: {container_name}/{blob_name}")
            return False
        except AzureError as e:
            logger.error(f"Failed to delete blob {blob_name}: {e}")
            raise

    def generate_download_url(
        self,
        blob_name: str,
        expiry_minutes: Optional[int] = None,
    ) -> str:
        """
        Generate a SAS URL for temporary download access.

        Args:
            blob_name: Name of the blob (e.g., "pptx/uuid.pptx")
            expiry_minutes: URL validity in minutes (default from config)

        Returns:
            Pre-signed URL with SAS token
        """
        if not self._account_key:
            raise RuntimeError(
                "Cannot generate SAS URL without account key. "
                "Use connection string authentication."
            )

        account_name = storage_config.azure_account_name or self._extract_account_name(
            storage_config.azure_connection_string
        )
        if not account_name:
            raise RuntimeError("Cannot determine account name for SAS generation")

        container_name = storage_config.azure_container_presentations
        expiry = expiry_minutes or storage_config.sas_expiry_minutes

        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=blob_name,
            account_key=self._account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(timezone.utc) + timedelta(minutes=expiry),
        )

        url = (
            f"https://{account_name}.blob.core.windows.net/"
            f"{container_name}/{blob_name}?{sas_token}"
        )
        logger.debug(f"Generated SAS URL for {blob_name} (expires in {expiry} min)")
        return url

    async def blob_exists(self, blob_name: str) -> bool:
        """Check if a blob exists"""
        if not self._client:
            raise RuntimeError("Azure Blob Service not initialized")

        container_name = storage_config.azure_container_presentations
        container_client = self._client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)

        try:
            await blob_client.get_blob_properties()
            return True
        except ResourceNotFoundError:
            return False

    async def health_check(self) -> dict:
        """Check Azure Blob Storage connectivity"""
        if not self._client:
            return {"status": "error", "message": "Not initialized"}

        try:
            container_name = storage_config.azure_container_presentations
            container_client = self._client.get_container_client(container_name)
            await container_client.get_container_properties()
            return {
                "status": "healthy",
                "backend": "azure",
                "container": container_name,
            }
        except ResourceNotFoundError:
            return {
                "status": "warning",
                "message": f"Container {container_name} does not exist",
            }
        except AzureError as e:
            return {"status": "error", "message": str(e)}

    async def close(self) -> None:
        """Close the blob service client"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Azure Blob Service closed")


# Convenience function for dependency injection
async def get_storage_service() -> AzureBlobService:
    """Get the Azure Blob Storage service instance"""
    return await AzureBlobService.get_instance()
