from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import session
from schemas import exports as schemas
from services import export_service
from utils import security
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/note/{note_id}", response_class=FileResponse)
def export_note(note_id: str, format: schemas.ExportFormat = schemas.ExportFormat.PDF, 
               db: Session = Depends(session.get_db), 
               current_user: dict = Depends(security.get_current_user)):
    content = export_service.ExportService(db).export_note(note_id, current_user['id'], format.value)
    
    if format == schemas.ExportFormat.PDF:
        return FileResponse(
            content, 
            media_type='application/pdf', 
            filename=f"note_{note_id}.pdf"
        )
    elif format == schemas.ExportFormat.MARKDOWN:
        return FileResponse(
            content, 
            media_type='text/markdown', 
            filename=f"note_{note_id}.md"
        )
    elif format == schemas.ExportFormat.HTML:
        return FileResponse(
            content, 
            media_type='text/html', 
            filename=f"note_{note_id}.html"
        )

@router.get("/all", response_class=FileResponse)
def export_all_notes(format: schemas.ExportFormat = schemas.ExportFormat.PDF, 
                    db: Session = Depends(session.get_db), 
                    current_user: dict = Depends(security.get_current_user)):
    content = export_service.ExportService(db).export_all(current_user['id'], format.value)
    
    if format == schemas.ExportFormat.PDF:
        return FileResponse(
            content, 
            media_type='application/pdf', 
            filename="all_notes.pdf"
        )
    elif format == schemas.ExportFormat.MARKDOWN:
        return FileResponse(
            content, 
            media_type='text/markdown', 
            filename="all_notes.md"
        )
    elif format == schemas.ExportFormat.HTML:
        return FileResponse(
            content, 
            media_type='text/html', 
            filename="all_notes.html"
        )