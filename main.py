from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import json
import uuid
import aiofiles
from pathlib import Path

from backend.db import crud, models
from backend.api import schemas
from backend.db.session import get_db, engine
from backend.core.generator.generator import generate_presentation
from backend.core.iterator.iterator import regenerate_slide
from backend.core.models.presentation.presentation import (
    SlidePresentation as AISlidesPresentation,
)
from backend.core.engines.pptx.json_handler import structure_to_ppt
from backend.core.engines.tex.generator import generate_tex_and_pdf
from backend.core.engines.converter.pptx_to_pdf import convert_pptx_to_pdf
from backend.config.logs import logger
from backend.core.rag.service import rag_service
from backend.core.rag.config import rag_config
from backend.core.rag.schemas import (
    RAGQueryRequest,
    RAGQueryResponse,
    RAGContextRequest,
    RAGContextResponse,
    RAGDocumentCreate,
)
import logfire

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated files for local development
if OUTPUT_DIR.exists():
    app.mount(
        "/generated_files",
        StaticFiles(directory=str(OUTPUT_DIR)),
        name="generated_files",
    )

# logfire.configure()
# logfire.instrument_pydantic_ai()


@app.post("/api/v1/presentations/", response_model=schemas.PresentationCreateResponse)
def create_presentation(
    presentation: schemas.PresentationCreate, db: Session = Depends(get_db)
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
            presentation.main_topic, presentation.main_topic
        )

        # Convert to JSON string for storage
        json_string = generated_presentation.model_dump_json()
        logger.debug(f"Generated presentation JSON: {json_string}")

        # Create database entry
        db_presentation = crud.create_presentation(
            db=db,
            main_topic=presentation.main_topic,
            json_object=json_string,
            file_type=presentation.file_type,
            theme=presentation.theme,
        )

        # Generate file with UUID as name
        if presentation.file_type == "pptx":
            file_path = PPTX_DIR / f"{db_presentation.id}.pptx"
            structure_to_ppt(
                generated_presentation,
                save_path=str(file_path),
                theme=presentation.theme,
            )

            # Also convert PPTX to PDF for preview
            pdf_path = PDF_DIR / f"{db_presentation.id}.pdf"
            convert_pptx_to_pdf(str(file_path), str(pdf_path))

        elif presentation.file_type == "pdf":
            # Generate PDF with UUID name in the PDF directory
            pdf_output_path = str(PDF_DIR / db_presentation.id)
            generate_tex_and_pdf(
                generated_presentation,
                tex_path=f"{pdf_output_path}.tex",
                output_filename=pdf_output_path,
            )

        return schemas.PresentationCreateResponse(id=str(db_presentation.id))

    except Exception as e:
        logger.error(f"Error creating presentation: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error generating presentation: {str(e)}"
        )


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
                "file_type": getattr(
                    p, "file_type", "pdf"
                ),  # Use getattr for backward compatibility
            }
            for p in presentations
        ],
        "skip": skip,
        "limit": limit,
        "total": len(presentations),
    }


@app.get(
    "/api/v1/presentations/{presentation_id}",
    response_model=schemas.PresentationGetResponse,
)
def get_presentation(presentation_id: str, db: Session = Depends(get_db)):
    """
    Get presentation by UUID
    Returns: UUID, main_topic, file_type, and slides from database
    """
    db_presentation = crud.get_presentation(db, presentation_id=presentation_id)
    if db_presentation is None:
        raise HTTPException(status_code=404, detail="Presentation not found")

    # Parse slide data from stored JSON
    slides_response = []
    if db_presentation.json_object:
        try:
            # Use json.loads instead of model_validate_json to avoid strict validation
            # Some stored presentations may not pass validation (e.g., missing title slide)
            presentation_dict = json.loads(str(db_presentation.json_object))
            slides_list = presentation_dict.get("slides", [])

            for slide in slides_list:
                # Flatten slide content for frontend display
                content_text = ""
                content = slide.get("content", {}) or {}

                # Handle text content
                text = content.get("text", {}) or {}
                if text.get("para"):
                    content_text = text["para"]
                elif text.get("bullet"):
                    content_text = "\n".join(f"• {b}" for b in text["bullet"])

                # Handle text2 content
                text2 = content.get("text2", {}) or {}
                if text2.get("para"):
                    content_text += "\n\n" + text2["para"]
                elif text2.get("bullet"):
                    content_text += "\n\n" + "\n".join(
                        f"• {b}" for b in text2["bullet"]
                    )

                # Handle comparison content
                comparison = content.get("comparison", {}) or {}
                if comparison:
                    left = comparison.get("left", "")
                    right = comparison.get("right", "")
                    if left or right:
                        content_text = f"Left: {left}\nRight: {right}"

                slides_response.append(
                    schemas.SlideResponse(
                        title=slide.get("title", "") or "",
                        content=content_text,
                        layout=slide.get("layout", "unknown"),
                    )
                )
        except Exception as e:
            logger.warning(f"Failed to parse presentation JSON: {e}")

    return schemas.PresentationGetResponse(
        id=str(db_presentation.id),
        main_topic=str(db_presentation.main_topic),
        file_type=getattr(db_presentation, "file_type", "pdf"),
        slides=slides_response,
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


@app.put(
    "/api/v1/presentations/{presentation_id}",
    response_model=schemas.SlideUpdateResponse,
)
def update_slide(
    presentation_id: str, slide_data: schemas.SlideUpdate, db: Session = Depends(get_db)
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
        current_presentation = AISlidesPresentation.model_validate_json(
            str(db_presentation.json_object)
        )

        # Validate slide number
        if slide_data.slide_number > len(current_presentation.slides):
            raise HTTPException(
                status_code=400,
                detail=f"Slide number {slide_data.slide_number} exceeds total slides ({len(current_presentation.slides)})",
            )

        # Regenerate the specific slide
        updated_presentation = regenerate_slide(
            presentation=current_presentation,
            slide_index=slide_data.slide_number - 1,  # Convert to 0-based index
            edit_prompt=slide_data.slide_content,
            original_prompt=str(db_presentation.main_topic),
        )

        # Update database with new JSON
        updated_json = updated_presentation.model_dump_json()
        crud.update_presentation_json(db, presentation_id, updated_json)

        # Regenerate files based on file type
        file_type = getattr(db_presentation, "file_type", "pdf")

        if file_type == "pptx":
            # Regenerate PPTX with original theme
            pptx_file = PPTX_DIR / f"{presentation_id}.pptx"
            theme = getattr(db_presentation, "theme", None)
            structure_to_ppt(
                updated_presentation, save_path=str(pptx_file), theme=theme
            )

            # Convert PPTX to PDF for preview
            pdf_file = PDF_DIR / f"{presentation_id}.pdf"
            convert_pptx_to_pdf(str(pptx_file), str(pdf_file))
            logger.info(f"Regenerated PPTX and PDF for presentation {presentation_id}")
        else:
            # Regenerate TeX and PDF
            pdf_output_path = str(PDF_DIR / presentation_id)
            generate_tex_and_pdf(
                updated_presentation,
                tex_path=f"{pdf_output_path}.tex",
                output_filename=pdf_output_path,
            )
            logger.info(f"Regenerated TeX and PDF for presentation {presentation_id}")

        return schemas.SlideUpdateResponse(id=presentation_id)

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in database")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating slide: {str(e)}")


# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ============ RAG Endpoints ============


@app.post("/api/v1/rag/upload", response_model=RAGDocumentCreate)
async def upload_document(
    background_tasks: BackgroundTasks, file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in rag_config.allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {rag_config.allowed_extensions}",
        )

    doc_id = str(uuid.uuid4())
    file_path = rag_config.upload_dir / f"{doc_id}{file_ext}"

    try:
        async with aiofiles.open(file_path, "wb") as f:
            content = await file.read()
            if len(content) > rag_config.max_file_size:
                raise HTTPException(status_code=400, detail="File too large (max 50MB)")
            await f.write(content)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save uploaded file: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file")

    async def process_doc():
        try:
            await rag_service.initialize()
            await rag_service.process_document(str(file_path), doc_id=doc_id)
            logger.info(f"Document processed: {doc_id}")
        except Exception as e:
            logger.error(f"Background processing failed for {doc_id}: {e}")

    background_tasks.add_task(process_doc)

    return RAGDocumentCreate(id=doc_id, filename=file.filename, status="processing")


@app.post("/api/v1/rag/query", response_model=RAGQueryResponse)
async def query_rag(request: RAGQueryRequest):
    try:
        await rag_service.initialize()
        answer = await rag_service.query(
            question=request.question, mode=request.mode, top_k=request.top_k
        )
        return RAGQueryResponse(
            answer=answer, question=request.question, mode=request.mode
        )
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/api/v1/rag/context", response_model=RAGContextResponse)
async def get_rag_context(request: RAGContextRequest):
    try:
        await rag_service.initialize()
        context = await rag_service.get_context_for_topic(
            topic=request.topic, mode=request.mode
        )
        return RAGContextResponse(context=context, topic=request.topic)
    except Exception as e:
        logger.error(f"RAG context retrieval failed: {e}")
        raise HTTPException(
            status_code=500, detail=f"Context retrieval failed: {str(e)}"
        )


@app.get("/api/v1/rag/status")
async def rag_status():
    return rag_service.get_config_info()
