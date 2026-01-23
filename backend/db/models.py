from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()


class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    main_topic = Column(String, index=True)
    file_type = Column(String, default="pdf")
    theme = Column(String, nullable=True)
    json_object = Column(Text)
    storage_backend = Column(String, default="local", nullable=False)
    pptx_blob_path = Column(String, nullable=True)
    pdf_blob_path = Column(String, nullable=True)

    def __repr__(self):
        return f"<Presentation(id='{self.id}', main_topic='{self.main_topic}', file_type='{self.file_type}')>"
