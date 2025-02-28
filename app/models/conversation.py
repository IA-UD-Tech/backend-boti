from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from pydantic import BaseModel, Field as PydanticField
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "Active"
    FINISHED = "Finished"
    PAUSED = "Paused"
    CANCELLED = "Cancelled"

class ConversationBase(SQLModel):
    user_id: UUID = Field(foreign_key="users.id", nullable=True)
    tool_id: Optional[int] = Field(foreign_key="tools.id", nullable=True)
    status: ConversationStatus = Field(default=ConversationStatus.ACTIVE)
    mode: str = Field(default="Standard")
    estimated_cost: float = Field(default=0)

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(SQLModel):
    user_id: Optional[UUID] = None
    tool_id: Optional[int] = None
    status: Optional[ConversationStatus] = None
    end_date: Optional[datetime] = None
    mode: Optional[str] = None
    estimated_cost: Optional[float] = None

class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    start_date: datetime = Field(default_factory=datetime.now)
    end_date: Optional[datetime] = Field(default=None)

class ConversationRead(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    tool_id: Optional[int]
    start_date: datetime
    end_date: Optional[datetime]
    status: ConversationStatus
    mode: str
    estimated_cost: float
    
    class Config:
        from_attributes = True