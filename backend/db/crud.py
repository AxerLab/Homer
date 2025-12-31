from sqlalchemy.orm import Session
from . import models
from typing import Optional


def create_presentation(
    db: Session,
    main_topic: str,
    json_object: str,
    file_type: str = "pdf",
    theme: Optional[str] = None,
) -> models.Presentation:
    db_presentation = models.Presentation(
        main_topic=main_topic, file_type=file_type, theme=theme, json_object=json_object
    )
    db.add(db_presentation)
    db.commit()
    db.refresh(db_presentation)
    return db_presentation


def get_presentation(
    db: Session, presentation_id: str
) -> Optional[models.Presentation]:
    return (
        db.query(models.Presentation)
        .filter(models.Presentation.id == presentation_id)
        .first()
    )


def get_presentations(
    db: Session, skip: int = 0, limit: int = 100
) -> list[models.Presentation]:
    return db.query(models.Presentation).offset(skip).limit(limit).all()


def update_presentation_json(
    db: Session, presentation_id: str, new_json_object: str
) -> Optional[models.Presentation]:
    db_presentation = (
        db.query(models.Presentation)
        .filter(models.Presentation.id == presentation_id)
        .first()
    )
    if db_presentation:
        db_presentation.json_object = new_json_object
        db.commit()
        db.refresh(db_presentation)
    return db_presentation


def delete_presentation(db: Session, presentation_id: str) -> bool:
    db_presentation = (
        db.query(models.Presentation)
        .filter(models.Presentation.id == presentation_id)
        .first()
    )
    if db_presentation:
        db.delete(db_presentation)
        db.commit()
        return True
    return False
