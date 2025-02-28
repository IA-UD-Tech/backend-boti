from typing import Optional
from datetime import date, datetime
from sqlmodel import Field, SQLModel
from uuid import UUID, uuid4
from pydantic import BaseModel
from enum import Enum

class PermissionType(str, Enum):
    ADMINISTRATOR = "Administrator"
    MANAGER = "Manager"
    USER = "User"

class PermissionBase(SQLModel):
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    tool_id: int = Field(foreign_key="tools.id", nullable=False)
    permission_type: PermissionType = Field(default=PermissionType.USER)
    interaction_count: int = Field(default=0)

class PermissionCreate(PermissionBase):
    pass

class PermissionUpdate(SQLModel):
    permission_type: Optional[PermissionType] = None
    interaction_count: Optional[int] = None
    updated_at: Optional[date] = None

class Permission(PermissionBase, table=True):
    __tablename__ = "permissions"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True, nullable=False)
    updated_at: date = Field(default_factory=lambda: date.today())

class PermissionRead(BaseModel):
    id: UUID
    user_id: UUID
    tool_id: int
    permission_type: PermissionType
    interaction_count: int
    updated_at: date
    
    class Config:
        from_attributes = True