import uuid
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import validator

class UUIDModel(SQLModel):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )

class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default=None)
    
    @validator("updated_at", always=True)
    def set_updated_at(cls, v, values, **kwargs):
        return datetime.utcnow()