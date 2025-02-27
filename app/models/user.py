from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship
from app.models.base import UUIDModel, TimestampModel
import uuid
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field as PydanticField

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, nullable=False)
    nombre: str = Field(nullable=False)
    estado: bool = Field(default=True)

class UserCreate(UserBase):
    pass

class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    estado: Optional[bool] = None
    ultima_conexion: Optional[datetime] = None

class User(UserBase, table=True):
    __tablename__ = "usuarios"
    
    id_usuario: Optional[UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        nullable=False,
        alias="id"  # Add alias to match CRUD expectations
    )
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    ultima_conexion: Optional[datetime] = Field(default=None)
    
    # Property to access id_usuario as id for compatibility with CRUD operations
    @property
    def id(self) -> UUID:
        return self.id_usuario

class UserRead(BaseModel):
    id_usuario: UUID
    email: EmailStr
    nombre: str
    estado: bool
    fecha_creacion: datetime
    ultima_conexion: Optional[datetime] = None
    
    class Config:
        from_attributes = True