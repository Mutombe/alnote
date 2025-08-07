from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session
from db.session import get_db
from services.note_service import NoteService
from schemas.notes import NoteOut, NoteCreate, NoteUpdate, NoteSearchResponse
from utils import security, file_processing
from fastapi import status

router = APIRouter(tags=["Notes"])

@router.post("/", response_model=NoteOut)
def create_note(
    note: NoteCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    return NoteService(db).create_note(current_user["id"], note)

@router.get("/{note_id}", response_model=NoteOut)
def read_note(
    note_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    note = NoteService(db).get_note(note_id, current_user["id"])
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteOut)
def update_note(
    note_id: str, 
    note: NoteUpdate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    updated_note = NoteService(db).update_note(note_id, current_user["id"], note)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    success = NoteService(db).delete_note(note_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return

@router.get("/", response_model=NoteSearchResponse)
def search_notes(
    query: str, 
    limit: int = 10, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    results = NoteService(db).search_notes(current_user["id"], query, limit)
    return {"results": results, "total": len(results)}

@router.post("/{note_id}/media")
async def upload_media(
    note_id: str, 
    file: UploadFile, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    # Save uploaded file
    file_path = await file_processing.save_upload_file(file, current_user["id"])
    
    # Update note with media path
    note_service = NoteService(db)
    note = note_service.get_note(note_id, current_user["id"])
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note_service.update_note(
        note_id, 
        current_user["id"], 
        NoteUpdate(media_path=file_path)
    )