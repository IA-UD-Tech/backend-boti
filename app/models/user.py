from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from app.models.base import UUIDModel, TimestampModel
import uuid
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field as PydanticField

class UserBase(SQLModel):
    email: EmailStr = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    status: bool = Field(default=True)
    avatar_url: Optional[str] = Field(nullable=True)

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    status: Optional[bool] = None
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None

class User(UserBase, table=True):
    __tablename__ = "users"
    
    id: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False
    )
    created_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = Field(default=None)

class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    status: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserWithRoles(UserRead):
    roles: List[str] = []