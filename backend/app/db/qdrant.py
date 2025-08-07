from qdrant_client import QdrantClient
from config import settings

class VectorDB:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            prefer_grpc=True
        )
    
    def upsert(self, vector: list, note_id: str, metadata: dict):
        # Create collection if missing
        if not self.client.collection_exists(settings.VECTOR_COLLECTION):
            self.client.create_collection(
                collection_name=settings.VECTOR_COLLECTION,
                vectors_config={
                    "size": len(vector),
                    "distance": "Cosine"
                }
            )
        
        # Upsert vector
        self.client.upsert(
            collection_name=settings.VECTOR_COLLECTION,
            points=[
                {
                    "id": note_id,
                    "vector": vector,
                    "payload": metadata
                }
            ]
        )
        return note_id
    
    def semantic_search(self, query_vector: list, user_id: int, limit=5):
        return self.client.search(
            collection_name=settings.VECTOR_COLLECTION,
            query_vector=query_vector,
            query_filter={
                "must": [{
                    "key": "user_id",
                    "match": {"value": user_id}
                }]
            },
            limit=limit
        )