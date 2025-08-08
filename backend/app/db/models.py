# db/models.py
from sqlalchemy import Column, Integer, String, JSON, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    
    # OAuth fields
    provider = Column(String, nullable=True)  # 'google', 'github', etc.
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    
    # Security fields
    hashed_password = Column(String, nullable=True)  # For email/password auth
    encryption_key = Column(String, nullable=True)  # Client-side encrypted
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Content fields
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)  # Encrypted at application layer
    summary = Column(Text, nullable=True)  # AI-generated summary
    
    # Vector and search fields
    vector_id = Column(String, unique=True, index=True)  # Qdrant vector ID
    embedding_model = Column(String, default="all-MiniLM-L6-v2")  # Track which model was used
    
    # Media and files
    media_path = Column(String, nullable=True)  # Path to uploaded files
    media_type = Column(String, nullable=True)  # 'image', 'audio', 'video', 'document'
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Metadata and categorization
    note_metadata = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    category = Column(String, nullable=True)
    priority = Column(Integer, default=0)  # 0=low, 1=medium, 2=high
    
    # Status and workflow
    status = Column(String, default="active")  # 'active', 'archived', 'deleted'
    is_favorite = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notes")
    source_connections = relationship(
        "NoteConnection", 
        foreign_keys="NoteConnection.source_id",
        back_populates="source_note",
        cascade="all, delete-orphan"
    )
    target_connections = relationship(
        "NoteConnection", 
        foreign_keys="NoteConnection.target_id",
        back_populates="target_note",
        cascade="all, delete-orphan"
    )

class NoteConnection(Base):
    __tablename__ = 'note_connections'
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, ForeignKey('notes.id'), nullable=False, index=True)
    target_id = Column(String, ForeignKey('notes.id'), nullable=False, index=True)
    
    # Connection properties
    connection_type = Column(String, nullable=False)  # 'semantic', 'user-defined', 'temporal'
    strength = Column(Float, nullable=True)  # AI-calculated relevance (0.0 to 1.0)
    description = Column(String, nullable=True)  # User-defined description
    
    # Metadata
    created_by = Column(String, default="system")  # 'system', 'user'
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    source_note = relationship("Note", foreign_keys=[source_id], back_populates="source_connections")
    target_note = relationship("Note", foreign_keys=[target_id], back_populates="target_connections")

class UserSession(Base):
    """Track user sessions for security and analytics"""
    __tablename__ = 'user_sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Session details
    session_token = Column(String, unique=True, index=True)
    refresh_token = Column(String, unique=True, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Status and timestamps
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User")

class NoteVersion(Base):
    """Track note version history"""
    __tablename__ = 'note_versions'
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(String, ForeignKey('notes.id'), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    
    # Content snapshot
    title = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Change tracking
    change_type = Column(String, nullable=False)  # 'create', 'update', 'delete'
    change_description = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    note = relationship("Note")