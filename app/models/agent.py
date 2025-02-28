from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from pydantic import BaseModel

class AgentBase(SQLModel):
    name: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    type: Optional[str] = Field(default=None)
    tool_id: Optional[int] = Field(default=None, foreign_key="tools.id")

class AgentCreate(AgentBase):
    pass

class AgentUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    tool_id: Optional[int] = None

class Agent(AgentBase, table=True):
    __tablename__ = "agents"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

class AgentRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    type: Optional[str] = None
    tool_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True