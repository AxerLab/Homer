from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import json
import os
from pathlib import Path

from .db import crud, models
from .api import schemas
from .db.session import get_db, engine
from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.iterator.iterator import regenerate_slide
from src.aislides.core.models.presentation.presentation import SlidePresentation as AISlidesPresentation
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.engines.tex.generator import generate_tex_and_pdf

# Create tables
models.Base.metadata.create_all(bind=engine)

# Create output directories if they don't exist
OUTPUT_DIR = Path("generated_files")
OUTPUT_DIR.mkdir(exist_ok=True)
PPTX_DIR = OUTPUT_DIR / "pptx"
PPTX_DIR.mkdir(exist_ok=True)
PDF_DIR = OUTPUT_DIR / "pdf"
PDF_DIR.mkdir(exist_ok=True)

app = FastAPI(title="AI Slides API", version="1.0.0")

# Add CORS for frontend development
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated files for local development
from fastapi.staticfiles import StaticFiles
if OUTPUT_DIR.exists():
    app.mount("/generated_files", StaticFiles(directory=str(OUTPUT_DIR)), name="generated_files")

@app.post("/api/v1/presentations/", response_model=schemas.PresentationCreateResponse)
def create_presentation(
    presentation: schemas.PresentationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new presentation:
    1. Generate presentation JSON from topic
    2. Store in database
    3. Generate requested file type (pptx/pdf) with UUID as filename
    4. Return UUID
    """
    try:
        # Generate presentation from topic
        generated_presentation = generate_presentation(
            presentation.main_topic,
            presentation.main_topic
        )

        # Convert to JSON string for storage
        json_string = generated_presentation.model_dump_json()

        # Create database entry
        db_presentation = crud.create_presentation(
            db=db,
            main_topic=presentation.main_topic,
            json_object=json_string,
            file_type=presentation.file_type
        )

        # Generate file with UUID as name
        if presentation.file_type == "pptx":
            file_path = PPTX_DIR / f"{db_presentation.id}.pptx"
            structure_to_ppt(generated_presentation, save_path=str(file_path))
        elif presentation.file_type == "pdf":
            # Generate PDF with UUID name in the PDF directory
            pdf_output_path = str(PDF_DIR / db_presentation.id)
            pdf_path = generate_tex_and_pdf(
                presentation.main_topic,
                presentation.main_topic,
                tex_path=f"{pdf_output_path}.tex",
                output_filename=pdf_output_path
            )

        return schemas.PresentationCreateResponse(id=db_presentation.id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating presentation: {str(e)}")

@app.get("/api/v1/presentations/{presentation_id}", response_model=schemas.PresentationGetResponse)
def get_presentation(presentation_id: str, db: Session = Depends(get_db)):
    """
    Get presentation by UUID
    Returns: UUID and main_topic from database
    """
    db_presentation = crud.get_presentation(db, presentation_id=presentation_id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation not found")

    return schemas.PresentationGetResponse(
        id=db_presentation.id,
        main_topic=db_presentation.main_topic,
        file_type=getattr(db_presentation, 'file_type', 'pdf')  # Use getattr for backward compatibility
    )

@app.delete("/api/v1/presentations/{presentation_id}")
def delete_presentation(presentation_id: str, db: Session = Depends(get_db)):
    """
    Delete presentation by UUID
    Removes entry from database and deletes associated files
    """
    # Check if presentation exists
    db_presentation = crud.get_presentation(db, presentation_id=presentation_id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation not found")

    # Delete associated files
    pptx_file = PPTX_DIR / f"{presentation_id}.pptx"
    pdf_file = PDF_DIR / f"{presentation_id}.pdf"

    if pptx_file.exists():
        pptx_file.unlink()
    if pdf_file.exists():
        pdf_file.unlink()

    # Delete from database
    deleted = crud.delete_presentation(db, presentation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Presentation not found")

    return {"message": "Presentation deleted successfully", "id": presentation_id}

@app.put("/api/v1/presentations/{presentation_id}", response_model=schemas.SlideUpdateResponse)
def update_slide(
    presentation_id: str,
    slide_data: schemas.SlideUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a specific slide in the presentation
    - Takes slide_number and slide_content
    - Updates the presentation JSON in database
    - Regenerates files with same UUID
    - Returns UUID
    """
    # Get existing presentation
    db_presentation = crud.get_presentation(db, presentation_id=presentation_id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation not found")

    try:
        # Parse existing JSON
        current_presentation = AISlidesPresentation.model_validate_json(db_presentation.json_object)

        # Validate slide number
        if slide_data.slide_number > len(current_presentation.slides):
            raise HTTPException(
                status_code=400,
                detail=f"Slide number {slide_data.slide_number} exceeds total slides ({len(current_presentation.slides)})"
            )

        # Regenerate the specific slide
        updated_presentation = regenerate_slide(
            presentation=current_presentation,
            slide_index=slide_data.slide_number - 1,  # Convert to 0-based index
            edit_prompt=slide_data.slide_content,
            original_prompt=db_presentation.main_topic
        )

        # Update database with new JSON
        updated_json = updated_presentation.model_dump_json()
        crud.update_presentation_json(db, presentation_id, updated_json)

        # Regenerate files with same UUID (optional - you might want this as a separate endpoint)
        # Update PPTX if it exists
        pptx_file = PPTX_DIR / f"{presentation_id}.pptx"
        if pptx_file.exists():
            structure_to_ppt(updated_presentation, save_path=str(pptx_file))

        # Note: PDF regeneration would require re-running the tex generator
        # which might be expensive, so consider making it a separate endpoint

        return schemas.SlideUpdateResponse(id=presentation_id)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating slide: {str(e)}")

@app.get("/api/v1/presentations/")
def list_presentations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    List all presentations with pagination
    """
    presentations = crud.get_presentations(db, skip=skip, limit=limit)
    return {
        "presentations": [
            {
                "id": p.id,
                "main_topic": p.main_topic,
                "file_type": getattr(p, 'file_type', 'pdf')  # Use getattr for backward compatibility
            }
            for p in presentations
        ],
        "skip": skip,
        "limit": limit,
        "total": len(presentations)
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}