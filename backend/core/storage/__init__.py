"""Storage module for file persistence (Azure Blob or local)"""

from .azure_blob import AzureBlobService, get_storage_service

__all__ = ["AzureBlobService", "get_storage_service"]
