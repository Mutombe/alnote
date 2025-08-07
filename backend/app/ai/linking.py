from db.qdrant import VectorDB
from config import settings
from typing import List

vector_db = VectorDB()
def find_related_notes(embedding: List[float], user_id: str, threshold: float = 0.7) -> list:
    """Find semantically related notes"""
    results = vector_db.semantic_search(
        embedding, 
        user_id,
        threshold=threshold
    )
    
    return [
        {
            "note_id": hit.id,
            "similarity": hit.score,
            "snippet": hit.payload.get('snippet', '')
        }
        for hit in results
    ]

def generate_knowledge_graph(user_id: str) -> dict:
    """Generate knowledge graph of user's concepts"""
    # Get all note embeddings for user
    # This is a simplified implementation
    # Production would use graph algorithms
    results = vector_db.get_all_vectors(user_id)
    
    nodes = []
    links = []
    
    for i, note in enumerate(results):
        nodes.append({
            "id": note.id,
            "label": note.payload.get('title', 'Note'),
            "group": note.payload.get('domain', 'general')
        })
        
        # Connect to nearest neighbors
        neighbors = vector_db.semantic_search(
            note.embedding, 
            user_id,
            limit=3,
            exclude_ids=[note.id]
        )
        
        for neighbor in neighbors:
            links.append({
                "source": note.id,
                "target": neighbor.id,
                "value": neighbor.score
            })
    
    return {"nodes": nodes, "links": links}