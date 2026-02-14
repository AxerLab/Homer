"""Storage Configuration (Local, Azure Blob, or Supabase Storage)"""

import os
from dataclasses import dataclass, field
from typing import Literal, cast

from dotenv import load_dotenv

load_dotenv()


@dataclass
class StorageConfig:
    """Configuration for file storage (local, Azure Blob, or Supabase Storage)"""

    # Storage backend: "local", "azure", or "supabase"
    backend: Literal["local", "azure", "supabase"] = field(
        default_factory=lambda: cast(
            Literal["local", "azure", "supabase"],
            os.getenv("STORAGE_BACKEND", "local"),
        )
    )

    # Azure Storage Configuration
    azure_account_name: str = field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_ACCOUNT_NAME", "")
    )
    azure_connection_string: str = field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    )
    azure_container_presentations: str = field(
        default_factory=lambda: os.getenv(
            "AZURE_STORAGE_CONTAINER_PRESENTATIONS", "presentations"
        )
    )
    azure_container_rag: str = field(
        default_factory=lambda: os.getenv("AZURE_STORAGE_CONTAINER_RAG", "rag-documents")
    )

    # SAS token expiry in minutes
    sas_expiry_minutes: int = field(
        default_factory=lambda: int(os.getenv("AZURE_STORAGE_SAS_EXPIRY_MINUTES", "60"))
    )

    # Supabase Storage Configuration
    supabase_url: str = field(
        default_factory=lambda: os.getenv("SUPABASE_URL", "")
    )
    supabase_service_key: str = field(
        default_factory=lambda: os.getenv("SUPABASE_SERVICE_KEY", "")
    )
    supabase_bucket: str = field(
        default_factory=lambda: os.getenv("SUPABASE_STORAGE_BUCKET", "presentations")
    )

    # Local storage paths (fallback)
    local_output_dir: str = field(
        default_factory=lambda: os.getenv("LOCAL_OUTPUT_DIR", "generated_files")
    )

    @property
    def is_azure(self) -> bool:
        """Check if Azure storage is configured and enabled"""
        return self.backend == "azure" and bool(
            self.azure_connection_string or self.azure_account_name
        )

    @property
    def is_supabase(self) -> bool:
        """Check if Supabase storage is configured and enabled"""
        return self.backend == "supabase" and bool(
            self.supabase_url and self.supabase_service_key
        )

    @property
    def azure_account_url(self) -> str:
        """Get Azure Blob account URL"""
        return f"https://{self.azure_account_name}.blob.core.windows.net"


# Singleton configuration instance
storage_config = StorageConfig()
