from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import get_db

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=schemas.NotesRead)
def create_note(note: schemas.NotesCreate, db: Session = Depends(get_db)):
    new_note = models.Notes(
        title=note.title,
        content=note.content,
        user_id=note.user_id,
    )
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/", response_model=list[schemas.NotesRead])
def get_notes(db: Session = Depends(get_db)):
    return db.query(models.Notes).all()


@router.get("/{notes_id}", response_model=schemas.NotesRead)
def get_single(notes_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Notes).filter(models.Notes.id == notes_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    return row


@router.delete("/{notes_id}")
def delete_single(notes_id: int, db: Session = Depends(get_db)):
    row = db.query(models.Notes).filter(models.Notes.id == notes_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(row)
    db.commit()
    return {"message": "Note deleted"}
