from celery import shared_task
from db.session import SessionLocal
from services import export_service
import tempfile
import os

@shared_task
def export_note_task(note_id: str, user_id: int, format: str):
    db = SessionLocal()
    try:
        content = export_service.ExportService(db).export_note(note_id, user_id, format)
        
        # For formats that return binary data (like PDF)
        if format == "pdf":
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            return tmp_path
        return content
    finally:
        db.close()

@shared_task
def export_all_notes_task(user_id: int, format: str):
    db = SessionLocal()
    try:
        content = export_service.ExportService(db).export_all(user_id, format)
        
        # For formats that return binary data (like PDF)
        if format == "pdf":
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            return tmp_path
        return content
    finally:
        db.close()