"""Storage module for RAG service (local or cloud)"""

import os
from typing import Union

from .local import RAGLocalStorageService
from .azure import RAGAzureStorageService

RAGStorageService = Union[RAGLocalStorageService, RAGAzureStorageService]


def get_storage_backend() -> str:
    """Return configured storage backend from env (default: local)"""
    return os.getenv("RAG_STORAGE_BACKEND", "local")


async def get_storage_service() -> RAGStorageService:
    """Return the configured RAG storage backend.

    Defaults to local filesystem when RAG_STORAGE_BACKEND is unset.
    Set RAG_STORAGE_BACKEND=azure to use Azure Blob Storage.
    """
    backend = get_storage_backend()
    if backend == "azure":
        return await RAGAzureStorageService.get_instance()
    return await RAGLocalStorageService.get_instance()


__all__ = ["RAGStorageService", "get_storage_service", "get_storage_backend"]