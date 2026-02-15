"""Storage module for file persistence (Azure Blob or local)"""

from typing import Union

from ...config.storage_config import storage_config
from .azure_blob import AzureBlobService
from .local import LocalStorageService

StorageService = Union[AzureBlobService, LocalStorageService]


async def get_storage_service() -> StorageService:
    """Return the configured storage backend (reads STORAGE_BACKEND env).

    Defaults to local filesystem when STORAGE_BACKEND is unset.
    """
    if storage_config.is_azure:
        return await AzureBlobService.get_instance()
    return await LocalStorageService.get_instance()


__all__ = ["StorageService", "get_storage_service"]
