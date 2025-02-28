import uuid
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from app.models.user import User, UserCreate, UserUpdate
from app.models.role import Role, RoleCreate, RoleUpdate
from app.models.tool import Tool, ToolCreate, ToolUpdate
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.models.agent_configuration import AgentConfiguration, AgentConfigurationCreate
from app.models.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationStatus
from app.models.message import Message, MessageCreate, MessageUpdate, SenderType
from app.models.permission import Permission, PermissionCreate, PermissionUpdate, PermissionType
from app.models.document import Document, DocumentCreate, DocumentUpdate
from app.models.vector_embedding import VectorEmbedding, VectorEmbeddingCreate

from tests.utils import generate_uuid

def create_user_dict(
    id: Optional[uuid.UUID] = None,
    email: str = "test@example.com",
    name: str = "Test User",
    status: bool = True,
    created_at: Optional[datetime] = None,
    last_login: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a user."""
    return {
        "id": id or generate_uuid(),
        "email": email,
        "name": name,
        "status": status,
        "created_at": created_at or datetime.now(),
        "last_login": last_login
    }

def create_user_create(
    email: str = "test@example.com",
    name: str = "Test User",
    status: bool = True
) -> UserCreate:
    """Create a UserCreate object."""
    return UserCreate(
        email=email,
        name=name,
        status=status
    )

def create_role_dict(
    id: int = 1,
    name: str = "Test Role",
    description: Optional[str] = "A test role"
) -> Dict[str, Any]:
    """Create a dictionary representing a role."""
    return {
        "id": id,
        "name": name,
        "description": description
    }

def create_role_create(
    name: str = "Test Role",
    description: Optional[str] = "A test role"
) -> RoleCreate:
    """Create a RoleCreate object."""
    return RoleCreate(
        name=name,
        description=description
    )

def create_tool_dict(
    id: int = 1,
    name: str = "Test Tool",
    type: Optional[str] = "test",
    description: Optional[str] = "A test tool",
    creator_id: Optional[uuid.UUID] = None,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a tool."""
    return {
        "id": id,
        "name": name,
        "type": type,
        "description": description,
        "creator_id": creator_id or generate_uuid(),
        "created_at": created_at or datetime.now()
    }

def create_tool_create(
    name: str = "Test Tool",
    type: Optional[str] = "test",
    description: Optional[str] = "A test tool",
    creator_id: Optional[uuid.UUID] = None
) -> ToolCreate:
    """Create a ToolCreate object."""
    return ToolCreate(
        name=name,
        type=type,
        description=description,
        creator_id=creator_id or generate_uuid()
    )

def create_agent_dict(
    id: Optional[uuid.UUID] = None,
    name: str = "Test Agent",
    description: Optional[str] = "A test agent",
    type: Optional[str] = "test",
    tool_id: Optional[int] = 1,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing an agent."""
    return {
        "id": id or generate_uuid(),
        "name": name,
        "description": description,
        "type": type,
        "tool_id": tool_id,
        "created_at": created_at or datetime.now()
    }

def create_agent_create(
    name: str = "Test Agent",
    description: Optional[str] = "A test agent",
    type: Optional[str] = "test",
    tool_id: Optional[int] = 1
) -> AgentCreate:
    """Create an AgentCreate object."""
    return AgentCreate(
        name=name,
        description=description,
        type=type,
        tool_id=tool_id
    )

def create_agent_config_dict(
    id: Optional[uuid.UUID] = None,
    agent_id: Optional[uuid.UUID] = None,
    parameter: str = "test_param",
    value: str = "test_value",
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing an agent configuration."""
    return {
        "id": id or generate_uuid(),
        "agent_id": agent_id or generate_uuid(),
        "parameter": parameter,
        "value": value,
        "created_at": created_at or datetime.now()
    }

def create_conversation_dict(
    id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    tool_id: Optional[int] = 1,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: ConversationStatus = ConversationStatus.ACTIVE,
    mode: str = "Standard",
    estimated_cost: float = 0.0
) -> Dict[str, Any]:
    """Create a dictionary representing a conversation."""
    return {
        "id": id or generate_uuid(),
        "user_id": user_id or generate_uuid(),
        "tool_id": tool_id,
        "start_date": start_date or datetime.now(),
        "end_date": end_date,
        "status": status,
        "mode": mode,
        "estimated_cost": estimated_cost
    }

def create_conversation_create(
    user_id: Optional[uuid.UUID] = None,
    tool_id: Optional[int] = 1,
    status: ConversationStatus = ConversationStatus.ACTIVE,
    mode: str = "Standard",
    estimated_cost: float = 0.0
) -> ConversationCreate:
    """Create a ConversationCreate object."""
    return ConversationCreate(
        user_id=user_id or generate_uuid(),
        tool_id=tool_id,
        status=status,
        mode=mode,
        estimated_cost=estimated_cost
    )

def create_message_dict(
    id: Optional[uuid.UUID] = None,
    conversation_id: Optional[uuid.UUID] = None,
    sender: SenderType = SenderType.USER,
    content: str = "Test message",
    sent_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a message."""
    return {
        "id": id or generate_uuid(),
        "conversation_id": conversation_id or generate_uuid(),
        "sender": sender,
        "content": content,
        "sent_at": sent_at or datetime.now()
    }

def create_message_create(
    conversation_id: Optional[uuid.UUID] = None,
    sender: SenderType = SenderType.USER,
    content: str = "Test message"
) -> MessageCreate:
    """Create a MessageCreate object."""
    return MessageCreate(
        conversation_id=conversation_id or generate_uuid(),
        sender=sender,
        content=content
    )

def create_permission_dict(
    id: Optional[uuid.UUID] = None,
    user_id: Optional[uuid.UUID] = None,
    tool_id: int = 1,
    permission_type: PermissionType = PermissionType.USER,
    interaction_count: int = 0,
    updated_at: Optional[date] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a permission."""
    return {
        "id": id or generate_uuid(),
        "user_id": user_id or generate_uuid(),
        "tool_id": tool_id,
        "permission_type": permission_type,
        "interaction_count": interaction_count,
        "updated_at": updated_at or date.today()
    }

def create_permission_create(
    user_id: Optional[uuid.UUID] = None,
    tool_id: int = 1,
    permission_type: PermissionType = PermissionType.USER,
    interaction_count: int = 0
) -> PermissionCreate:
    """Create a PermissionCreate object."""
    return PermissionCreate(
        user_id=user_id or generate_uuid(),
        tool_id=tool_id,
        permission_type=permission_type,
        interaction_count=interaction_count
    )

def create_document_dict(
    id: Optional[uuid.UUID] = None,
    agent_id: Optional[uuid.UUID] = None,
    name: str = "Test Document",
    text_content: str = "This is a test document",
    tool_id: Optional[int] = 1,
    vector: Optional[List[float]] = None,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a document."""
    return {
        "id": id or generate_uuid(),
        "agent_id": agent_id,
        "name": name,
        "text_content": text_content,
        "tool_id": tool_id,
        "vector": vector or [0.1] * 1536,  # 1536-dimensional vector
        "created_at": created_at or datetime.now()
    }

def create_document_create(
    agent_id: Optional[uuid.UUID] = None,
    name: str = "Test Document",
    text_content: str = "This is a test document",
    tool_id: Optional[int] = 1
) -> DocumentCreate:
    """Create a DocumentCreate object."""
    return DocumentCreate(
        agent_id=agent_id,
        name=name,
        text_content=text_content,
        tool_id=tool_id
    )

def create_vector_embedding_dict(
    id: Optional[uuid.UUID] = None,
    message_id: Optional[uuid.UUID] = None,
    document_id: Optional[uuid.UUID] = None,
    agent_id: Optional[uuid.UUID] = None,
    vector: Optional[List[float]] = None,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """Create a dictionary representing a vector embedding."""
    return {
        "id": id or generate_uuid(),
        "message_id": message_id,
        "document_id": document_id,
        "agent_id": agent_id,
        "vector": vector or [0.1] * 1536,  # 1536-dimensional vector
        "created_at": created_at or datetime.now()
    }

def create_vector_embedding_create(
    message_id: Optional[uuid.UUID] = None,
    document_id: Optional[uuid.UUID] = None,
    agent_id: Optional[uuid.UUID] = None
) -> VectorEmbeddingCreate:
    """Create a VectorEmbeddingCreate object."""
    return VectorEmbeddingCreate(
        message_id=message_id,
        document_id=document_id,
        agent_id=agent_id
    )