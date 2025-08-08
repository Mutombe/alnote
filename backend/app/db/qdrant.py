# db/qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models as rest
from config import settings
import logging
import uuid
from typing import List, Dict, Optional, Any
import asyncio

logger = logging.getLogger(__name__)

class VectorDB:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
            timeout=30,
            # Remove prefer_grpc=True for cloud instances
        )
        self.collection_name = settings.VECTOR_COLLECTION
        
    async def initialize_collection(self, vector_size: int = 384):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection {self.collection_name} already exists")
                
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collection: {e}")
            raise
    
    def upsert_note_vector(
        self, 
        vector: List[float], 
        note_id: str, 
        user_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Upsert a note vector with metadata"""
        try:
            # Ensure collection exists
            if not self._collection_exists():
                self.initialize_collection(len(vector))
            
            # Prepare payload
            payload = {
                "user_id": user_id,
                "note_id": note_id,
                **(metadata or {})
            }
            
            # Create point
            point = PointStruct(
                id=note_id,
                vector=vector,
                payload=payload
            )
            
            # Upsert vector
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"Upserted vector for note {note_id}")
            return note_id
            
        except Exception as e:
            logger.error(f"Failed to upsert vector for note {note_id}: {e}")
            raise
    
    def semantic_search(
        self, 
        query_vector: List[float], 
        user_id: int, 
        limit: int = 5,
        score_threshold: float = 0.5,
        additional_filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search for similar notes"""
        try:
            # Build filter conditions
            filter_conditions = [
                FieldCondition(
                    key="user_id",
                    match=MatchValue(value=user_id)
                )
            ]
            
            # Add additional filters if provided
            if additional_filters:
                for key, value in additional_filters.items():
                    filter_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=Filter(must=filter_conditions),
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            results = []
            for result in search_results:
                results.append({
                    "note_id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            logger.debug(f"Found {len(results)} similar notes for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed for user {user_id}: {e}")
            raise
    
    def delete_note_vector(self, note_id: str) -> bool:
        """Delete a note vector from the collection"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=rest.PointIdsList(
                    points=[note_id]
                )
            )
            logger.debug(f"Deleted vector for note {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vector for note {note_id}: {e}")
            return False
    
    def delete_user_vectors(self, user_id: int) -> bool:
        """Delete all vectors for a specific user"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=user_id)
                        )
                    ]
                )
            )
            logger.info(f"Deleted all vectors for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors for user {user_id}: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection"""
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "status": info.status,
                "vectors_count": info.vectors_count,
                "indexed_vectors_count": info.indexed_vectors_count,
                "points_count": info.points_count,
                "config": {
                    "vector_size": info.config.params.vectors.size,
                    "distance": info.config.params.vectors.distance
                }
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def _collection_exists(self) -> bool:
        """Check if collection exists"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return self.collection_name in collection_names
        except Exception as e:
            logger.error(f"Failed to check collection existence: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check if Qdrant is healthy"""
        try:
            collections = self.client.get_collections()
            logger.debug("Qdrant health check passed")
            return True
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False

# Singleton instance
vector_db = VectorDB()