"""RAG Service - Singleton wrapper around RAGAnything"""

import asyncio
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import logging

from raganything import RAGAnything, RAGAnythingConfig

from .config import rag_config
from .llm_adapter import get_llm_model_func, get_vision_model_func, get_embedding_func

logger = logging.getLogger(__name__)


class DocumentStatus(str, Enum):
    """Status of document processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class DocumentProcessingInfo:
    """Tracks the processing status of a document"""
    doc_id: str
    filename: str
    status: DocumentStatus = DocumentStatus.PENDING
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class RAGService:
    _instance: Optional["RAGService"] = None
    _rag: Optional[RAGAnything] = None
    _initialized: bool = False
    _lock: asyncio.Lock = asyncio.Lock()
    _documents_processed: bool = False
    _document_status: Dict[str, DocumentProcessingInfo] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._lock = asyncio.Lock()
            cls._documents_processed = cls._check_existing_data()
            cls._document_status = {}
        return cls._instance
    
    def register_document(self, doc_id: str, filename: str) -> DocumentProcessingInfo:
        """Register a new document for processing tracking"""
        info = DocumentProcessingInfo(
            doc_id=doc_id,
            filename=filename,
            status=DocumentStatus.PENDING,
            started_at=datetime.now()
        )
        self._document_status[doc_id] = info
        return info
    
    def get_document_status(self, doc_id: str) -> Optional[DocumentProcessingInfo]:
        """Get the processing status of a document"""
        return self._document_status.get(doc_id)
    
    def _update_document_status(
        self, 
        doc_id: str, 
        status: DocumentStatus, 
        error: Optional[str] = None
    ) -> None:
        """Update the status of a document"""
        if doc_id in self._document_status:
            self._document_status[doc_id].status = status
            if error:
                self._document_status[doc_id].error = error
            if status in (DocumentStatus.COMPLETED, DocumentStatus.FAILED):
                self._document_status[doc_id].completed_at = datetime.now()

    @classmethod
    def _check_existing_data(cls) -> bool:
        working_dir = Path(rag_config.working_dir)
        if not working_dir.exists():
            return False
        kv_store = working_dir / "kv_store_full_docs.json"
        graph_store = working_dir / "graph_chunk_entity_relation.graphml"
        return kv_store.exists() or graph_store.exists()

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
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Process a document and add it to the knowledge base.

        Args:
            file_path: Path to the document file
            doc_id: Optional custom document ID
            filename: Optional original filename for status tracking

        Returns:
            Dict with processing results
        """
        rag = await self._ensure_initialized()
        
        # Update status to processing
        if doc_id and doc_id in self._document_status:
            self._update_document_status(doc_id, DocumentStatus.PROCESSING)

        try:
            await rag.process_document_complete(
                file_path=file_path,
                output_dir=str(rag_config.parser_output_dir),
                parse_method=rag_config.parse_method,
                doc_id=doc_id,
                display_stats=False,
                # Use 'pipeline' backend for MinerU 2.7+ compatibility
                # The default 'hybrid-auto-engine' outputs to 'hybrid_auto/' which
                # RAGAnything's _read_output_files doesn't correctly handle
                backend="pipeline",
            )
            self._documents_processed = True
            
            # Update status to completed
            if doc_id:
                self._update_document_status(doc_id, DocumentStatus.COMPLETED)
            
            logger.info(f"Document processed successfully: {file_path}")
            return {"success": True, "file_path": file_path, "doc_id": doc_id}
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to process document {file_path}: {error_msg}")
            
            # Update status to failed
            if doc_id:
                self._update_document_status(doc_id, DocumentStatus.FAILED, error_msg)
            
            return {"success": False, "error": error_msg, "file_path": file_path}

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
        if not self._documents_processed:
            logger.info(
                "No documents in RAG knowledge base, skipping context retrieval"
            )
            return ""

        prompt = f"""Based on the documents in the knowledge base, provide relevant 
        background information, facts, and key points about: {topic}
        
        Focus on information that would be useful for creating an educational presentation.
        Include specific data, examples, and important concepts if available."""

        return await self.query(prompt, mode=mode)

    def get_config_info(self) -> Dict[str, Any]:
        return {
            "working_dir": str(rag_config.working_dir),
            "parser": rag_config.parser,
            "embedding_model": rag_config.embedding_model,
            "embedding_dim": rag_config.embedding_dim,
            "llm_model": rag_config.groq_model,
            "initialized": self._initialized,
            "has_documents": self._documents_processed,
        }


# Singleton instance
rag_service = RAGService()


async def get_rag_service() -> RAGService:
    """Dependency to get RAG service (initializes if needed)"""
    await rag_service.initialize()
    return rag_service
