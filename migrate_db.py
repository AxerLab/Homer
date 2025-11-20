#!/usr/bin/env python3
"""
Database migration script to add file_type column to existing presentations
and determine file types based on existing files.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = "sqlite:///./aislides.db"

# File directories
PPTX_DIR = Path("generated_files/pptx")
PDF_DIR = Path("generated_files/pdf")

def migrate():
    """Run database migration to add file_type column"""

    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with engine.connect() as conn:
        # Check if file_type column already exists
        result = conn.execute(text("PRAGMA table_info(presentations)"))
        columns = [row[1] for row in result]

        if 'file_type' not in columns:
            print("Adding file_type column to presentations table...")

            # Add the file_type column
            conn.execute(text("ALTER TABLE presentations ADD COLUMN file_type TEXT DEFAULT 'pdf'"))
            conn.commit()

            print("Column added successfully.")
        else:
            print("file_type column already exists.")

        # Update file_type for existing presentations based on file existence
        result = conn.execute(text("SELECT id FROM presentations"))
        presentations = result.fetchall()

        print(f"Updating file_type for {len(presentations)} existing presentations...")

        for row in presentations:
            pres_id = row[0]

            # Check what files exist for this presentation
            pptx_file = PPTX_DIR / f"{pres_id}.pptx"
            pdf_file = PDF_DIR / f"{pres_id}.pdf"

            # Determine file_type based on existing files
            if pptx_file.exists() and not pdf_file.exists():
                file_type = "pptx"
            elif pdf_file.exists() and not pptx_file.exists():
                file_type = "pdf"
            elif pptx_file.exists() and pdf_file.exists():
                # Both exist, prefer the most recently modified
                if pptx_file.stat().st_mtime > pdf_file.stat().st_mtime:
                    file_type = "pptx"
                else:
                    file_type = "pdf"
            else:
                # Default to pdf if no files found
                file_type = "pdf"

            # Update the database
            conn.execute(
                text("UPDATE presentations SET file_type = :file_type WHERE id = :id"),
                {"file_type": file_type, "id": pres_id}
            )
            print(f"  Updated {pres_id}: file_type = {file_type}")

        conn.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate()