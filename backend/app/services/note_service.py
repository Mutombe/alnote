from sqlalchemy.orm import Session
from db import models
from schemas import notes as schemas
from utils import security, file_processing
from ai import embeddings
from config import settings
import json

class NoteService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = embeddings.LocalEmbeddingModel()

    def create_note(self, user_id: str, note_data: schemas.NoteCreate) -> models.Note:
        # Encrypt content
        encrypted_content = security.encrypt_content(
            note_data.content, 
            security.get_user_key(user_id)
        )
        
        # Create database record
        db_note = models.Note(
            user_id=user_id,
            title=note_data.title,
            content=encrypted_content,
            media_path=note_data.media_path,
            metadata=json.dumps(note_data.metadata) if note_data.metadata else None
        )
        
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        
        # Process with AI
        self.process_note_ai(db_note)
        
        return db_note

    def get_note(self, note_id: str, user_id: str) -> models.Note:
        note = self.db.query(models.Note).filter(
            models.Note.id == note_id,
            models.Note.user_id == user_id
        ).first()
        
        if note:
            note.content = security.decrypt_content(
                note.content,
                security.get_user_key(user_id)
            )
            
        return note

    def update_note(self, note_id: str, user_id: str, update_data: schemas.NoteUpdate) -> models.Note:
        note = self.get_note(note_id, user_id)
        if not note:
            return None
        
        if update_data.content:
            note.content = security.encrypt_content(
                update_data.content,
                security.get_user_key(user_id)
            )
        
        if update_data.title:
            note.title = update_data.title
            
        if update_data.media_path:
            note.media_path = update_data.media_path
            
        if update_data.metadata:
            note.metadata = json.dumps(update_data.metadata)
            
        note.updated_at = update_data.updated_at
        self.db.commit()
        
        # Reprocess with AI if content changed
        if update_data.content:
            self.process_note_ai(note)
            
        return note

    def process_note_ai(self, note: models.Note):
        """Process note content with AI services"""
        # Generate embedding
        content = security.decrypt_content(
            note.content,
            security.get_user_key(note.user_id)
        )
        embedding = self.ai_service.generate(content)
        
        # Store in vector DB
        vector_id = embeddings.vector_db.upsert(
            embedding, 
            note.id,
            metadata={
                'user_id': note.user_id,
                'created_at': str(note.created_at)
            }
        )
        
        # Generate title if missing
        if not note.title or note.title.strip() == "":
            note.title = embeddings.generate_title(content)
            self.db.commit()
            
        return vector_id

    def delete_note(self, note_id: str, user_id: str) -> bool:
        note = self.get_note(note_id, user_id)
        if not note:
            return False
            
        self.db.delete(note)
        self.db.commit()
        return True

    def search_notes(self, user_id: str, query: str, limit: int = 10) -> list:
        """Semantic search of user's notes"""
        # Generate query embedding
        embedding = self.ai_service.generate(query)
        
        # Search vector DB
        results = embeddings.vector_db.semantic_search(
            embedding, 
            user_id,
            limit=limit
        )
        
        # Get full note objects
        note_ids = [hit.id for hit in results]
        return self.db.query(models.Note).filter(
            models.Note.id.in_(note_ids)
        ).all()