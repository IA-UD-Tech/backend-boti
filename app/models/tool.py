from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID
from pydantic import BaseModel

class ToolBase(SQLModel):
    name: str = Field(unique=True, nullable=False)
    type: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    creator_id: UUID = Field(foreign_key="users.id", nullable=True)

class ToolCreate(ToolBase):
    pass

class ToolUpdate(SQLModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[UUID] = None

class Tool(ToolBase, table=True):
    __tablename__ = "tools"
    
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

class ToolRead(BaseModel):
    id: int
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True