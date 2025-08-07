from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.export_service import ExportService
from schemas.exports import ExportFormat
from utils import security
from fastapi.responses import FileResponse

router = APIRouter(tags=["Exports"])

@router.get("/note/{note_id}", response_class=FileResponse)
def export_note(
    note_id: str, 
    format: ExportFormat = ExportFormat.PDF, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    content = ExportService(db).export_note(note_id, current_user["id"], format.value)
    
    if format == ExportFormat.PDF:
        return FileResponse(
            content, 
            media_type='application/pdf', 
            filename=f"note_{note_id}.pdf"
        )
    elif format == ExportFormat.MARKDOWN:
        return FileResponse(
            content, 
            media_type='text/markdown', 
            filename=f"note_{note_id}.md"
        )
    elif format == ExportFormat.HTML:
        return FileResponse(
            content, 
            media_type='text/html', 
            filename=f"note_{note_id}.html"
        )
    elif format == ExportFormat.DOCX:
        return FileResponse(
            content, 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            filename=f"note_{note_id}.docx"
        )

@router.get("/all", response_class=FileResponse)
def export_all_notes(
    format: ExportFormat = ExportFormat.PDF, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    content = ExportService(db).export_all(current_user["id"], format.value)
    
    if format == ExportFormat.PDF:
        return FileResponse(
            content, 
            media_type='application/pdf', 
            filename="all_notes.pdf"
        )
    elif format == ExportFormat.MARKDOWN:
        return FileResponse(
            content, 
            media_type='text/markdown', 
            filename="all_notes.md"
        )
    elif format == ExportFormat.HTML:
        return FileResponse(
            content, 
            media_type='text/html', 
            filename="all_notes.html"
        )
    elif format == ExportFormat.DOCX:
        return FileResponse(
            content, 
            media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            filename="all_notes.docx"
        )