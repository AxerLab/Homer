#!/usr/bin/env python3
"""
Populate database with existing presentations based on files
"""

import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.aislides.db.models import Base, Presentation

# Database configuration
DATABASE_URL = "sqlite:///./aislides.db"

# File directories
PPTX_DIR = Path("generated_files/pptx")
PDF_DIR = Path("generated_files/pdf")
JSON_DIR = Path("generated_files/json")

# Known presentations
PRESENTATIONS = [
    ("4ec2ffc5-ec47-46c3-b675-a61a1ae1aaf5", "delhi red fort blast", "pdf"),
    ("dbda8706-b56b-4aed-8baa-81a882e58181", "nowgram blast 2025", "pptx"),
    ("263ee014-ac47-46d2-a899-90917b911dd0", "Introduction to Machine Learning", "pptx"),
    ("54c44c40-0602-4d5c-a7a3-6aa20972522e", "Introduction to Quantum Computing", "pdf"),
]

def populate():
    """Populate database with existing presentations"""

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()

    try:
        for pres_id, main_topic, file_type in PRESENTATIONS:
            # Check if presentation already exists
            existing = db.query(Presentation).filter(Presentation.id == pres_id).first()

            if existing:
                print(f"Presentation {pres_id} already exists, updating file_type...")
                existing.file_type = file_type
            else:
                # Try to load JSON if it exists
                json_file = JSON_DIR / f"{pres_id}.json"
                json_object = "{}"

                if json_file.exists():
                    with open(json_file, 'r') as f:
                        json_object = f.read()

                # Create new presentation
                presentation = Presentation(
                    id=pres_id,
                    main_topic=main_topic,
                    file_type=file_type,
                    json_object=json_object
                )
                db.add(presentation)
                print(f"Added presentation: {pres_id} ({main_topic}) - {file_type}")

        db.commit()
        print("Database populated successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate()