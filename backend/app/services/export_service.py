from sqlalchemy.orm import Session
from db import models
from utils import file_processing, security
from config import settings
import markdown
from fpdf import FPDF
import html2text
import os

class ExportService:
    def __init__(self, db: Session):
        self.db = db

    def export_note(self, note_id: str, user_id: str, format: str = "markdown") -> str:
        """Export single note to specified format"""
        note = self.db.query(models.Note).filter(
            models.Note.id == note_id,
            models.Note.user_id == user_id
        ).first()
        
        if not note:
            return None
            
        # Decrypt content
        decrypted_content = security.decrypt_content(
            note.content,
            security.get_user_key(user_id))
        
        if format == "markdown":
            return self._to_markdown(note.title, decrypted_content)
        elif format == "pdf":
            return self._to_pdf(note.title, decrypted_content)
        elif format == "html":
            return self._to_html(note.title, decrypted_content)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def export_all(self, user_id: str, format: str = "markdown") -> str:
        """Export all user notes to specified format"""
        notes = self.db.query(models.Note).filter(
            models.Note.user_id == user_id
        ).all()
        
        if not notes:
            return None
            
        # Decrypt all content
        for note in notes:
            note.content = security.decrypt_content(
                note.content,
                security.get_user_key(user_id))
        
        if format == "markdown":
            return "\n\n".join(
                [self._to_markdown(n.title, n.content) for n in notes]
            )
        elif format == "pdf":
            return self._notes_to_pdf(notes)
        elif format == "html":
            return self._notes_to_html(notes)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _to_markdown(self, title: str, content: str) -> str:
        return f"# {title}\n\n{content}"

    def _to_pdf(self, title: str, content: str) -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt=title, ln=True, align='C')
        pdf.multi_cell(0, 10, txt=content)
        return pdf.output(dest='S').encode('latin1')

    def _to_html(self, title: str, content: str) -> str:
        html_content = markdown.markdown(content)
        return f"<html><body><h1>{title}</h1>{html_content}</body></html>"

    def _notes_to_pdf(self, notes: list) -> bytes:
        pdf = FPDF()
        for note in notes:
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=note.title, ln=True, align='C')
            pdf.multi_cell(0, 10, txt=note.content)
        return pdf.output(dest='S').encode('latin1')

    def _notes_to_html(self, notes: list) -> str:
        html = "<html><body>"
        for note in notes:
            html_content = markdown.markdown(note.content)
            html += f"<h1>{note.title}</h1>{html_content}<hr>"
        html += "</body></html>"
        return html