"""RAG Configuration with HuggingFace embeddings"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()


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

    # Groq LLM Configuration (uses existing GROQ_API_KEY from app)
    groq_api_key: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    groq_model: str = field(
        default_factory=lambda: os.getenv("RAG_LLM_MODEL", "qwen/qwen3-32b")
    )

    # Parser Configuration
    parser: str = "mineru"  # or "docling"
    parse_method: str = "auto"  # auto, ocr, txt

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

    def __post_init__(self):
        """Ensure directories exist"""
        self.working_dir = Path(self.working_dir)
        self.parser_output_dir = Path(self.parser_output_dir)
        self.upload_dir = Path(self.upload_dir)

        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.parser_output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Singleton configuration instance
rag_config = RAGConfig()
