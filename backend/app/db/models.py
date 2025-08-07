from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    encryption_key = Column(String)  # Client-side encrypted

class Note(Base):
    __tablename__ = 'notes'
    id = Column(String, primary_key=True)  # UUID
    user_id = Column(Integer)
    title = Column(String)
    content = Column(Text)  # Encrypted at application layer
    vector_id = Column(String)  # Qdrant vector ID
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    media_path = Column(String)  # Path to uploaded files
    note_metadata = Column(JSON) 
    
class NoteConnection(Base):
    __tablename__ = 'note_connections'
    id = Column(Integer, primary_key=True)
    source_id = Column(String)
    target_id = Column(String)
    connection_type = Column(String)  # 'semantic', 'user-defined'
    strength = Column(Integer)  # AI-calculated relevance