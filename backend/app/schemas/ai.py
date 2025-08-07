from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any

class NoteLink(BaseModel):
    note_id: str
    similarity: float
    snippet: str

class NoteLinksResponse(BaseModel):
    links: List[NoteLink]

class KnowledgeGraphNode(BaseModel):
    id: str
    label: str
    group: str

class KnowledgeGraphLink(BaseModel):
    source: str
    target: str
    value: float

class KnowledgeGraphResponse(BaseModel):
    nodes: List[KnowledgeGraphNode]
    links: List[KnowledgeGraphLink]

class ImageDescription(BaseModel):
    description: str
    tags: List[str]

class ContentProcessingRequest(BaseModel):
    content: str
    operation: str = Field("summarize", example="summarize|extract_keywords|generate_title")

class ProcessedContent(BaseModel):
    result: str
    metadata: Dict[str, Any]

class NoteLinkRequest(BaseModel):
    note_id: str
    threshold: float = 0.7