from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

class RoleBase(SQLModel):
    name: str = Field(nullable=False, unique=True)
    description: Optional[str] = Field(default=None)

class RoleCreate(RoleBase):
    pass

class RoleUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Role(RoleBase, table=True):
    __tablename__ = "roles"
    
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

class RoleRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True