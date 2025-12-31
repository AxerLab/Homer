"""RAG Service - Singleton wrapper around RAGAnything"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
import logging

from raganything import RAGAnything, RAGAnythingConfig

from .config import rag_config
from .llm_adapter import get_llm_model_func, get_vision_model_func, get_embedding_func

logger = logging.getLogger(__name__)


class RAGService:
    """Singleton service for RAG operations using HuggingFace embeddings + Groq LLM"""

    _instance: Optional["RAGService"] = None
    _rag: Optional[RAGAnything] = None
    _initialized: bool = False
    _lock: asyncio.Lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._lock = asyncio.Lock()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize RAGAnything instance (lazy initialization, thread-safe)"""
        async with self._lock:
            if self._initialized:
                return

            logger.info("Initializing RAG service with HuggingFace embeddings...")

            config = RAGAnythingConfig(
                working_dir=str(rag_config.working_dir),
                parser=rag_config.parser,
                parse_method=rag_config.parse_method,
                enable_image_processing=rag_config.enable_image_processing,
                enable_table_processing=rag_config.enable_table_processing,
                enable_equation_processing=rag_config.enable_equation_processing,
            )

            self._rag = RAGAnything(
                config=config,
                llm_model_func=get_llm_model_func(),
                vision_model_func=get_vision_model_func(),
                embedding_func=get_embedding_func(),
            )

            self._initialized = True
            logger.info(f"RAG service initialized: model={rag_config.embedding_model}")

    async def _ensure_initialized(self) -> RAGAnything:
        """Ensure RAG is initialized before operations"""
        if not self._initialized:
            await self.initialize()
        if self._rag is None:
            raise RuntimeError("RAG service failed to initialize")
        return self._rag

    async def process_document(
        self,
        file_path: str,
        doc_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a document and add it to the knowledge base.

        Args:
            file_path: Path to the document file
            doc_id: Optional custom document ID

        Returns:
            Dict with processing results
        """
        rag = await self._ensure_initialized()

        try:
            await rag.process_document_complete(
                file_path=file_path,
                output_dir=str(rag_config.parser_output_dir),
                parse_method=rag_config.parse_method,
                doc_id=doc_id,
                display_stats=False,
            )
            logger.info(f"Document processed successfully: {file_path}")
            return {"success": True, "file_path": file_path, "doc_id": doc_id}
        except Exception as e:
            logger.error(f"Failed to process document {file_path}: {e}")
            return {"success": False, "error": str(e), "file_path": file_path}

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        top_k: int = 10,
    ) -> str:
        """
        Query the RAG knowledge base.

        Args:
            question: The query string
            mode: Query mode - "hybrid", "local", "global", or "naive"
            top_k: Number of top results to consider

        Returns:
            Generated answer string
        """
        rag = await self._ensure_initialized()

        try:
            result = await rag.aquery(
                question,
                mode=mode,
                top_k=top_k,
            )
            return result
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise

    async def get_context_for_topic(
        self,
        topic: str,
        mode: str = "hybrid",
    ) -> str:
        """
        Get relevant context from RAG for presentation generation.

        Args:
            topic: Presentation topic
            mode: Query mode

        Returns:
            Contextual information string
        """
        prompt = f"""Based on the documents in the knowledge base, provide relevant 
        background information, facts, and key points about: {topic}
        
        Focus on information that would be useful for creating an educational presentation.
        Include specific data, examples, and important concepts if available."""

        return await self.query(prompt, mode=mode)

    def get_config_info(self) -> Dict[str, Any]:
        """Get current configuration info"""
        return {
            "working_dir": str(rag_config.working_dir),
            "parser": rag_config.parser,
            "embedding_model": rag_config.embedding_model,
            "embedding_dim": rag_config.embedding_dim,
            "llm_model": rag_config.groq_model,
            "initialized": self._initialized,
        }


# Singleton instance
rag_service = RAGService()


async def get_rag_service() -> RAGService:
    """Dependency to get RAG service (initializes if needed)"""
    await rag_service.initialize()
    return rag_service
