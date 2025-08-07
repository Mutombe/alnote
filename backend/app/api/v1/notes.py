from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from db import session
from schemas import notes as schemas
from services import note_service
from utils import security
from utils import file_processing

router = APIRouter()


@router.post("/", response_model=schemas.NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(
    note_create: schemas.NoteCreate,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return note_service.NoteService(db).create_note(current_user["id"], note_create)


@router.get("/{note_id}", response_model=schemas.NoteOut)
def get_note(
    note_id: str,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    note = note_service.NoteService(db).get_note(note_id, current_user["id"])
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}", response_model=schemas.NoteOut)
def update_note(
    note_id: str,
    note_update: schemas.NoteUpdate,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    note = note_service.NoteService(db).update_note(
        note_id, current_user["id"], note_update
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    success = note_service.NoteService(db).delete_note(note_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return


@router.get("/", response_model=list[schemas.NoteOut])
def search_notes(
    query: str,
    limit: int = 10,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return note_service.NoteService(db).search_notes(current_user["id"], query, limit)


@router.post("/{note_id}/media", response_model=schemas.NoteOut)
async def upload_media(
    note_id: str,
    file: UploadFile,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    # Save uploaded file
    file_path = await file_processing.save_upload_file(file, current_user["id"])

    # Process file
    file_type = file.content_type.split("/")[0]
    if file_type == "image":
        file_processing.process_image(file_path)

    # Update note
    note_service = note_service.NoteService(db)
    note = note_service.get_note(note_id, current_user["id"])
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note_service.update_note(
        note_id, current_user["id"], schemas.NoteUpdate(media_path=file_path)
    )
