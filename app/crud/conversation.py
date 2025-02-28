from typing import List, Optional
from datetime import datetime
from uuid import UUID
from supabase import Client
from app.models.conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationStatus
from app.crud.base import CRUDBase

class CRUDConversation(CRUDBase[Conversation, ConversationCreate, ConversationUpdate]):
    async def get_by_user(
        self, client: Client, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """
        Get all conversations for a specific user.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .order("start_date", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Conversation(**item) for item in response.data]

    async def get_by_tool(
        self, client: Client, *, tool_id: int, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """
        Get all conversations for a specific tool.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("tool_id", tool_id) \
            .order("start_date", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Conversation(**item) for item in response.data]

    async def get_by_status(
        self, client: Client, *, status: ConversationStatus, skip: int = 0, limit: int = 100
    ) -> List[Conversation]:
        """
        Get all conversations with a specific status.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("status", status) \
            .order("start_date", desc=True) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Conversation(**item) for item in response.data]

    async def finish_conversation(
        self, client: Client, *, conversation_id: UUID
    ) -> Optional[Conversation]:
        """
        Mark a conversation as finished and set the end date.
        """
        conversation = await self.get(client, id=conversation_id)
        if conversation:
            update_data = ConversationUpdate(
                status=ConversationStatus.FINISHED,
                end_date=datetime.now()
            )
            return await self.update(client, db_obj=conversation, obj_in=update_data)
        return None

    async def pause_conversation(
        self, client: Client, *, conversation_id: UUID
    ) -> Optional[Conversation]:
        """
        Mark a conversation as paused.
        """
        conversation = await self.get(client, id=conversation_id)
        if conversation:
            update_data = ConversationUpdate(status=ConversationStatus.PAUSED)
            return await self.update(client, db_obj=conversation, obj_in=update_data)
        return None

    async def resume_conversation(
        self, client: Client, *, conversation_id: UUID
    ) -> Optional[Conversation]:
        """
        Resume a paused conversation.
        """
        conversation = await self.get(client, id=conversation_id)
        if conversation and conversation.status == ConversationStatus.PAUSED:
            update_data = ConversationUpdate(status=ConversationStatus.ACTIVE)
            return await self.update(client, db_obj=conversation, obj_in=update_data)
        return None

    async def cancel_conversation(
        self, client: Client, *, conversation_id: UUID
    ) -> Optional[Conversation]:
        """
        Mark a conversation as cancelled and set the end date.
        """
        conversation = await self.get(client, id=conversation_id)
        if conversation:
            update_data = ConversationUpdate(
                status=ConversationStatus.CANCELLED,
                end_date=datetime.now()
            )
            return await self.update(client, db_obj=conversation, obj_in=update_data)
        return None

# Create an instance of the CRUDConversation class
conversation = CRUDConversation(Conversation)