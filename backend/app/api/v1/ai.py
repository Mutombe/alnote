from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import session
from schemas import ai as schemas
from services import ai_service
from utils import security

router = APIRouter()


@router.post("/link-notes", response_model=schemas.NoteLinksResponse)
def find_related_notes(
    request: schemas.NoteLinkRequest,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return ai_service.find_related_notes_for_user(
        current_user["id"], request.note_id, request.threshold
    )


@router.get("/knowledge-graph", response_model=schemas.KnowledgeGraphResponse)
def get_knowledge_graph(
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return ai_service.generate_knowledge_graph(current_user["id"])


@router.post("/describe-image", response_model=schemas.ImageDescription)
def describe_image(
    image_url: str,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return ai_service.describe_image(image_url)


@router.post("/process-content", response_model=schemas.ProcessedContent)
def process_content(
    request: schemas.ContentProcessingRequest,
    db: Session = Depends(session.get_db),
    current_user: dict = Depends(security.get_current_user),
):
    return ai_service.process_content(request.content)
