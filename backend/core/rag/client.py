"""HTTP Client for RAG Service communication"""

import os
import logging
from typing import Optional, Any, Dict, AsyncGenerator

import httpx

logger = logging.getLogger(__name__)

# RAG Service URL - configurable via environment variable
RAG_SERVICE_URL = os.getenv("RAG_SERVICE_URL", "http://localhost:8002")


class RAGServiceClient:
    """HTTP client for communicating with the RAG microservice"""

    def __init__(self, base_url: Optional[str] = None, timeout: float = 120.0):
        self.base_url = base_url or RAG_SERVICE_URL
        self.timeout = timeout

    async def health_check(self) -> Dict[str, Any]:
        """Check if RAG service is healthy"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()

    async def upload_document(
        self,
        file_content: bytes,
        filename: str,
    ) -> Dict[str, Any]:
        """Upload a document to the RAG service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            files = {"file": (filename, file_content)}
            response = await client.post(
                f"{self.base_url}/upload",
                files=files,
            )
            response.raise_for_status()
            return response.json()

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        top_k: int = 10,
    ) -> Dict[str, Any]:
        """Query the RAG knowledge base"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/query",
                json={"question": question, "mode": mode, "top_k": top_k},
            )
            response.raise_for_status()
            return response.json()

    async def get_context(
        self,
        topic: str,
        mode: str = "hybrid",
    ) -> Dict[str, Any]:
        """Get context for a topic from the RAG knowledge base"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/context",
                json={"topic": topic, "mode": mode},
            )
            response.raise_for_status()
            return response.json()

    async def get_context_for_topic(
        self,
        topic: str,
        mode: str = "hybrid",
    ) -> str:
        """Get context string for a topic (convenience method for generator)"""
        try:
            result = await self.get_context(topic, mode)
            return result.get("context", "")
        except Exception as e:
            logger.warning(f"Failed to get RAG context: {e}")
            return ""

    async def get_status(self) -> Dict[str, Any]:
        """Get RAG service status"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()

    async def get_document_status(self, doc_id: str) -> Dict[str, Any]:
        """Get the processing status of a document"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/document/{doc_id}/status")
            response.raise_for_status()
            return response.json()

    async def stream_document_progress(self, doc_id: str) -> AsyncGenerator[str, None]:
        """Stream document processing progress via SSE"""
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                f"{self.base_url}/document/{doc_id}/progress",
                headers={"Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        yield line + "\n"

    async def list_documents(self) -> Dict[str, Any]:
        """List all documents in the RAG service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/documents")
            response.raise_for_status()
            return response.json()

    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from the RAG service"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.delete(f"{self.base_url}/document/{doc_id}")
            response.raise_for_status()
            return response.json()


# Singleton instance
rag_client = RAGServiceClient()
