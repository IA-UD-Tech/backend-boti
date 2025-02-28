from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from uuid import UUID

class UserRoleBase(SQLModel):
    # For a composite primary key, mark both fields as primary_key=True
    user_id: UUID = Field(primary_key=True, foreign_key="users.id")
    role_id: int = Field(primary_key=True, foreign_key="roles.id")
    assigned_at: datetime = Field(default_factory=datetime.now)

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleUpdate(SQLModel):
    assigned_at: Optional[datetime] = None

class UserRole(UserRoleBase, table=True):
    __tablename__ = "user_role"