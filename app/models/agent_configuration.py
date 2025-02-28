from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from pydantic import BaseModel

class AgentConfigurationBase(SQLModel):
    agent_id: UUID = Field(foreign_key="agents.id", nullable=False)
    parameter: str = Field(nullable=False)
    value: str = Field(nullable=False)

class AgentConfigurationCreate(AgentConfigurationBase):
    pass

class AgentConfigurationUpdate(SQLModel):
    agent_id: Optional[UUID] = None
    parameter: Optional[str] = None
    value: Optional[str] = None

class AgentConfiguration(AgentConfigurationBase, table=True):
    __tablename__ = "agent_configuration"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.now)

class AgentConfigurationRead(BaseModel):
    id: UUID
    agent_id: UUID
    parameter: str
    value: str
    created_at: datetime
    
    class Config:
        from_attributes = True