from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class NoteBase(BaseModel):
    title: Optional[str] = Field(None, example="My Note Title")
    content: str = Field(..., example="This is the content of my note")
    media_path: Optional[str] = Field(None, example="/media/image.png")
    metadata: Optional[Dict] = Field(None, example={"category": "research"})

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media_path: Optional[str] = None
    metadata: Optional[Dict] = None
    updated_at: datetime = Field(default_factory=datetime.now)

class NoteOut(NoteBase):
    id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    vector_id: Optional[str]
    
    # Updated configuration for Pydantic V2
    model_config = ConfigDict(from_attributes=True)

class NoteSearchResponse(BaseModel):
    results: List[NoteOut]
    total: int

class MediaType(str, Enum):
    image = "image"
    pdf = "pdf"
    sketch = "sketch"
    document = "document"