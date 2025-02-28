from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.conversation import conversation as conversation_crud
from app.crud.message import message as message_crud
from app.models.conversation import Conversation, ConversationCreate, ConversationRead, ConversationUpdate, ConversationStatus
from app.models.message import Message, MessageCreate, MessageRead, SenderType

router = APIRouter()

@router.post("/", response_model=ConversationRead)
async def create_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_in: ConversationCreate,
) -> Any:
    """
    Create a new conversation.
    """
    conversation = await conversation_crud.create(supabase_client, obj_in=conversation_in)
    return conversation

@router.get("/", response_model=List[ConversationRead])
async def read_conversations(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    tool_id: Optional[int] = None,
    status: Optional[ConversationStatus] = None,
) -> Any:
    """
    Retrieve conversations with optional filtering.
    """
    if user_id:
        conversations = await conversation_crud.get_by_user(
            supabase_client, user_id=user_id, skip=skip, limit=limit
        )
    elif tool_id:
        conversations = await conversation_crud.get_by_tool(
            supabase_client, tool_id=tool_id, skip=skip, limit=limit
        )
    elif status:
        conversations = await conversation_crud.get_by_status(
            supabase_client, status=status, skip=skip, limit=limit
        )
    else:
        conversations = await conversation_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return conversations

@router.get("/{conversation_id}", response_model=ConversationRead)
async def read_conversation(
    conversation_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific conversation by ID.
    """
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation

@router.put("/{conversation_id}", response_model=ConversationRead)
async def update_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
    conversation_in: ConversationUpdate,
) -> Any:
    """
    Update a conversation.
    """
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    conversation = await conversation_crud.update(
        supabase_client, db_obj=conversation, obj_in=conversation_in
    )
    return conversation

@router.post("/{conversation_id}/finish", response_model=ConversationRead)
async def finish_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
) -> Any:
    """
    Mark a conversation as finished.
    """
    conversation = await conversation_crud.finish_conversation(
        supabase_client, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation

@router.post("/{conversation_id}/pause", response_model=ConversationRead)
async def pause_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
) -> Any:
    """
    Mark a conversation as paused.
    """
    conversation = await conversation_crud.pause_conversation(
        supabase_client, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation

@router.post("/{conversation_id}/resume", response_model=ConversationRead)
async def resume_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
) -> Any:
    """
    Resume a paused conversation.
    """
    conversation = await conversation_crud.resume_conversation(
        supabase_client, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or not paused"
        )
    return conversation

@router.post("/{conversation_id}/cancel", response_model=ConversationRead)
async def cancel_conversation(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
) -> Any:
    """
    Mark a conversation as cancelled.
    """
    conversation = await conversation_crud.cancel_conversation(
        supabase_client, conversation_id=conversation_id
    )
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    return conversation

# Message endpoints

@router.post("/{conversation_id}/messages", response_model=MessageRead)
async def create_message(
    *,
    supabase_client: Client = Depends(get_client),
    conversation_id: UUID,
    content: str,
    sender: SenderType = SenderType.USER,
) -> Any:
    """
    Add a message to a conversation.
    """
    # Check if conversation exists
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Check if conversation is not finished or cancelled
    if conversation.status in [ConversationStatus.FINISHED, ConversationStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add messages to a conversation with status: {conversation.status}"
        )
    
    message_in = MessageCreate(
        conversation_id=conversation_id,
        content=content,
        sender=sender
    )
    
    message = await message_crud.create(supabase_client, obj_in=message_in)
    return message

@router.get("/{conversation_id}/messages", response_model=List[MessageRead])
async def read_messages(
    conversation_id: UUID,
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    sender: Optional[SenderType] = None,
) -> Any:
    """
    Get messages from a conversation with optional filtering by sender type.
    """
    # Check if conversation exists
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    if sender:
        messages = await message_crud.get_by_sender_type(
            supabase_client, 
            conversation_id=conversation_id, 
            sender_type=sender,
            skip=skip, 
            limit=limit
        )
    else:
        messages = await message_crud.get_by_conversation(
            supabase_client,
            conversation_id=conversation_id,
            skip=skip,
            limit=limit
        )
    
    return messages

@router.get("/{conversation_id}/messages/{message_id}", response_model=MessageRead)
async def read_message(
    conversation_id: UUID,
    message_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific message by ID.
    """
    message = await message_crud.get(supabase_client, id=message_id)
    if not message or message.conversation_id != conversation_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this conversation"
        )
    return message

@router.get("/{conversation_id}/messages/latest", response_model=MessageRead)
async def read_latest_message(
    conversation_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get the most recent message in a conversation.
    """
    # Check if conversation exists
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    message = await message_crud.get_last_message(
        supabase_client, conversation_id=conversation_id
    )
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found in this conversation"
        )
    
    return message

@router.get("/{conversation_id}/messages/count", response_model=int)
async def count_messages(
    conversation_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Count the number of messages in a conversation.
    """
    # Check if conversation exists
    conversation = await conversation_crud.get(supabase_client, id=conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    count = await message_crud.count_by_conversation(
        supabase_client, conversation_id=conversation_id
    )
    
    return count