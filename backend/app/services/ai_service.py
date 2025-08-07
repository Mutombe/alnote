from ai import embeddings, linking, titling, multimodal
from tasks.ai_tasks import process_note_async
from db.qdrant import VectorDB

vector_db = VectorDB()

class AIService:
    def __init__(self):
        self.embedding_model = embeddings.LocalEmbeddingModel()
        self.multimodal_processor = multimodal.MultimodalProcessor()
    
    async def process_note(self, note_data: dict):
        # For heavy processing, use background task
        if note_data.get('content_length', 0) > 5000:
            from tasks.ai_tasks import process_note_async  # Local import
            return process_note_async.delay(note_data)
        
        # Real-time processing for small notes
        return await self._process_note_sync(note_data)
    
    async def _process_note_sync(self, note_data: dict):
        # Generate embedding
        embedding = self.embedding_model.generate(
            note_data['content'],
            note_data.get('media_path')
        )
        
        # Store in vector DB
        vector_id = vector_db.upsert(
            embedding, 
            note_data['id'],
            metadata={
                'user_id': note_data['user_id'],
                'created_at': note_data['created_at']
            }
        )
        
        # Generate title if missing
        if not note_data.get('title'):
            note_data['title'] = titling.generate_title(
                note_data['content'],
                embedding
            )
        
        # Find related notes
        related_notes = linking.find_related_notes(
            embedding, 
            note_data['user_id'],
            threshold=0.75
        )
        
        return {
            'vector_id': vector_id,
            'title': note_data['title'],
            'related_notes': related_notes
        }