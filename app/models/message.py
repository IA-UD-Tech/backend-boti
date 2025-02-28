from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from pydantic import BaseModel, Field as PydanticField
from enum import Enum

class SenderType(str, Enum):
    USER = "User"
    AGENT = "Agent"
    SYSTEM = "System"

class MessageBase(SQLModel):
    conversation_id: UUID = Field(foreign_key="conversations.id", nullable=False)
    sender: SenderType = Field(default=SenderType.USER)
    content: str = Field(nullable=False)

class MessageCreate(MessageBase):
    pass

class MessageUpdate(SQLModel):
    content: Optional[str] = None
    sender: Optional[SenderType] = None

class Message(MessageBase, table=True):
    __tablename__ = "messages"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    sent_at: datetime = Field(default_factory=datetime.now)

class MessageRead(BaseModel):
    id: UUID
    conversation_id: UUID
    sender: SenderType
    content: str
    sent_at: datetime
    
    class Config:
        from_attributes = True