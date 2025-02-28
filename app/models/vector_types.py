from typing import List, NewType, Any, Optional, cast
from pydantic import Field, field_serializer, field_validator
import json
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# Define a type for vector embeddings
# This is a list of floats with a specific length (1536 for OpenAI embeddings)
Embedding = NewType('Embedding', List[float])

# SQL Alchemy type for PostgreSQL vector
class PgVector(sa.types.TypeDecorator):
    """PostgreSQL vector type for SQLAlchemy."""
    impl = sa.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert a list of floats to a JSON string for storage."""
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        """Convert a JSON string back to a list of floats."""
        if value is None:
            return None
        return json.loads(value)