"""RAG Configuration with HuggingFace embeddings"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Tuple, Literal

from dotenv import load_dotenv

load_dotenv()


# Embedding provider types
EmbeddingProvider = Literal["huggingface", "fastembed"]


@dataclass
class RAGConfig:
    """Configuration for RAG service using free HuggingFace embeddings"""

    # Directory Configuration
    working_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_WORKING_DIR", "./rag_storage"))
    )
    parser_output_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_PARSER_OUTPUT_DIR", "./rag_parsed"))
    )
    upload_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_UPLOAD_DIR", "./rag_uploads"))
    )

    # Embedding Provider Toggle
    # Options: "huggingface" (remote API, sequential) or "fastembed" (local, batched, faster)
    # Set RAG_EMBEDDING_PROVIDER=fastembed for significantly faster processing
    embedding_provider: EmbeddingProvider = field(
        default_factory=lambda: os.getenv("RAG_EMBEDDING_PROVIDER", "huggingface")  # type: ignore[return-value]
    )

    # HuggingFace Inference API (FREE tier, remote - no local model needed)
    hf_api_token: str = field(default_factory=lambda: os.getenv("HF_API_TOKEN", ""))
    embedding_model: str = field(
        default_factory=lambda: os.getenv(
            "RAG_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )
    )
    embedding_dim: int = field(
        default_factory=lambda: int(os.getenv("RAG_EMBEDDING_DIM", "384"))
    )

    # FastEmbed Configuration (local ONNX-based, batched processing)
    # Model options: "BAAI/bge-small-en-v1.5" (384d), "BAAI/bge-base-en-v1.5" (768d)
    fastembed_model: str = field(
        default_factory=lambda: os.getenv(
            "RAG_FASTEMBED_MODEL",
            "BAAI/bge-small-en-v1.5",
        )
    )
    fastembed_max_length: int = field(
        default_factory=lambda: int(os.getenv("RAG_FASTEMBED_MAX_LENGTH", "512"))
    )

    # Parser Configuration (switch via RAG_PARSER env var)
    parser: str = field(default_factory=lambda: os.getenv("RAG_PARSER", "docling"))
    parse_method: str = field(
        default_factory=lambda: os.getenv("RAG_PARSE_METHOD", "auto")
    )

    # Processing options
    enable_image_processing: bool = True
    enable_table_processing: bool = True
    enable_equation_processing: bool = True

    # Allowed file extensions
    allowed_extensions: Tuple[str, ...] = (
        ".pdf",
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".xlsx",
        ".xls",
        ".png",
        ".jpg",
        ".jpeg",
        ".txt",
        ".md",
    )
    max_file_size: int = 50 * 1024 * 1024  # 50MB

    def __post_init__(self) -> None:
        """Ensure directories exist"""
        self.working_dir = Path(self.working_dir)
        self.parser_output_dir = Path(self.parser_output_dir)
        self.upload_dir = Path(self.upload_dir)

        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.parser_output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Singleton configuration instance
rag_config = RAGConfig()
