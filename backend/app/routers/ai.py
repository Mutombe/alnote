from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.session import get_db
from services.ai_service import AIService
from schemas.ai import (
    NoteLinksResponse, 
    KnowledgeGraphResponse,
    ContentProcessingRequest,
    ProcessedContent,
    NoteLinkRequest
)
from utils import security

router = APIRouter(tags=["AI"])

@router.post("/link-notes", response_model=NoteLinksResponse)
def find_related_notes(
    request: NoteLinkRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    # Initialize service inside endpoint
    ai_service = AIService()
    return ai_service.find_related_notes_for_user(
        current_user["id"], request.note_id, request.threshold
    )

@router.get("/knowledge-graph", response_model=KnowledgeGraphResponse)
def get_knowledge_graph(
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    # Initialize service inside endpoint
    ai_service = AIService()
    return ai_service.generate_knowledge_graph(current_user["id"])

@router.post("/process-content", response_model=ProcessedContent)
def process_content(
    request: ContentProcessingRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    # Initialize service inside endpoint
    ai_service = AIService()
    return ai_service.process_content(request.content, request.operation)

@router.post("/auto-title")
def generate_title(
    content: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(security.get_current_user)
):
    # Initialize service inside endpoint
    ai_service = AIService()
    return ai_service.generate_title(content)