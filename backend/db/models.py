from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
import uuid

Base = declarative_base()

class Presentation(Base):
    __tablename__ = "presentations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    main_topic = Column(String, index=True)
    file_type = Column(String, default="pdf")  # Store the file type (pdf or pptx)
    json_object = Column(Text) # Store the entire JSON object as text

    def __repr__(self):
        return f"<Presentation(id='{self.id}', main_topic='{self.main_topic}', file_type='{self.file_type}')>"
