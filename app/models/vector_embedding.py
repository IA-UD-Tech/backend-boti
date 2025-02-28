from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from uuid import UUID, uuid4
from pydantic import BaseModel
import sqlalchemy as sa

from app.models.vector_types import Embedding, PgVector

class VectorEmbeddingBase(SQLModel):
    message_id: Optional[UUID] = Field(foreign_key="messages.id", nullable=True)
    document_id: Optional[UUID] = Field(foreign_key="documents.id", nullable=True)
    agent_id: Optional[UUID] = Field(foreign_key="agents.id", nullable=True)

class VectorEmbeddingCreate(VectorEmbeddingBase):
    # The vector field isn't included in the creation model
    # It will be generated before insertion
    pass

class VectorEmbeddingUpdate(SQLModel):
    message_id: Optional[UUID] = None
    document_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None

class VectorEmbedding(VectorEmbeddingBase, table=True):
    __tablename__ = "vector_embeddings"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    # Use sa_column to define the vector field with a custom type
    vector: List[float] = Field(
        sa_column=Column(PgVector, nullable=False)
    )
    created_at: datetime = Field(default_factory=datetime.now)

class VectorEmbeddingRead(BaseModel):
    id: UUID
    message_id: Optional[UUID]
    document_id: Optional[UUID]
    agent_id: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True

class VectorEmbeddingWithVector(VectorEmbeddingRead):
    vector: List[float]
    
    class Config:
        from_attributes = True