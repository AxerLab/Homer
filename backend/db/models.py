from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional
import uuid


class Base(DeclarativeBase):
    pass


class Presentation(Base):
    __tablename__ = "presentations"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    main_topic: Mapped[str] = mapped_column(String, index=True)
    file_type: Mapped[str] = mapped_column(String, default="pdf")
    theme: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    json_object: Mapped[str] = mapped_column(Text)
    storage_backend: Mapped[str] = mapped_column(String, default="local")
    pptx_blob_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    pdf_blob_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Presentation(id='{self.id}', main_topic='{self.main_topic}', file_type='{self.file_type}')>"
