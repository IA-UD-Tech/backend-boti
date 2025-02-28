from typing import Optional, List, Union, Dict, Any
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from uuid import UUID, uuid4
from pydantic import BaseModel, field_serializer, field_validator
import sqlalchemy as sa
import json

from app.models.vector_types import Embedding, PgVector

class DocumentBase(SQLModel):
    agent_id: Optional[UUID] = Field(foreign_key="agents.id", nullable=True)
    name: str = Field(nullable=False)
    text_content: str = Field(nullable=False)
    tool_id: Optional[int] = Field(foreign_key="tools.id", nullable=True)

class DocumentCreate(DocumentBase):
    # The vector field isn't included in the creation model
    # It will be generated before insertion
    pass

class DocumentUpdate(SQLModel):
    agent_id: Optional[UUID] = None
    name: Optional[str] = None
    text_content: Optional[str] = None
    tool_id: Optional[int] = None

# Define a table model with a properly typed vector field
class Document(DocumentBase, table=True):
    __tablename__ = "documents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    # Use sa_column to define the vector field with a custom type
    vector: Optional[List[float]] = Field(
        sa_column=Column(PgVector, nullable=True)
    )
    created_at: datetime = Field(default_factory=datetime.now)

class DocumentRead(BaseModel):
    id: UUID
    agent_id: Optional[UUID]
    name: str
    text_content: str
    tool_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentWithVector(DocumentRead):
    vector: Optional[List[float]] = None
    
    class Config:
        from_attributes = True