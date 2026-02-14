import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv

load_dotenv()


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


@dataclass
class RAGConfig:

    working_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_WORKING_DIR", "./rag_storage"))
    )
    parser_output_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_PARSER_OUTPUT_DIR", "./rag_parsed"))
    )
    upload_dir: Path = field(
        default_factory=lambda: Path(os.getenv("RAG_UPLOAD_DIR", "./rag_uploads"))
    )

    fastembed_model: str = field(
        default_factory=lambda: os.getenv("RAG_FASTEMBED_MODEL", "BAAI/bge-small-en-v1.5")
    )
    embedding_dim: int = field(default_factory=lambda: _env_int("RAG_EMBEDDING_DIM", 384))
    chunk_size_chars: int = field(
        default_factory=lambda: _env_int("RAG_CHUNK_SIZE_CHARS", 1200)
    )
    chunk_overlap_chars: int = field(
        default_factory=lambda: _env_int("RAG_CHUNK_OVERLAP_CHARS", 200)
    )
    min_chunk_chars: int = field(
        default_factory=lambda: _env_int("RAG_MIN_CHUNK_CHARS", 120)
    )
    per_retriever_k: int = field(
        default_factory=lambda: _env_int("RAG_PER_RETRIEVER_K", 15)
    )
    final_context_k: int = field(
        default_factory=lambda: _env_int("RAG_FINAL_CONTEXT_K", 5)
    )
    rrf_k: int = field(default_factory=lambda: _env_int("RAG_RRF_K", 60))

    groq_api_key: str = field(
        default_factory=lambda: os.getenv("RAG_GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    )
    groq_model: str = field(
        default_factory=lambda: os.getenv("RAG_GROQ_MODEL", "llama-3.3-70b-versatile")
    )
    groq_chat_completions_url: str = field(
        default_factory=lambda: os.getenv(
            "RAG_GROQ_CHAT_COMPLETIONS_URL",
            "https://api.groq.com/openai/v1/chat/completions",
        )
    )
    llm_timeout_seconds: int = field(
        default_factory=lambda: _env_int("RAG_LLM_TIMEOUT_SECONDS", 45)
    )
    query_timeout_seconds: int = field(
        default_factory=lambda: _env_int("RAG_QUERY_TIMEOUT_SECONDS", 45)
    )
    synthesis_max_chars: int = field(
        default_factory=lambda: _env_int("RAG_SYNTHESIS_MAX_CHARS", 6000)
    )
    groq_max_tokens: int = field(
        default_factory=lambda: _env_int("RAG_GROQ_MAX_TOKENS", 1024)
    )

    parser: str = field(default_factory=lambda: os.getenv("RAG_PARSER", "hybrid_fast"))
    embedding_model: str = field(default_factory=lambda: os.getenv("RAG_EMBEDDING_MODEL", "fastembed"))

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
    max_file_size: int = 50 * 1024 * 1024

    def __post_init__(self) -> None:
        self.working_dir = Path(self.working_dir)
        self.parser_output_dir = Path(self.parser_output_dir)
        self.upload_dir = Path(self.upload_dir)

        self.working_dir.mkdir(parents=True, exist_ok=True)
        self.parser_output_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


# Singleton configuration instance
rag_config = RAGConfig()
