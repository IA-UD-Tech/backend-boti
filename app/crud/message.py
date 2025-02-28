from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.models.message import Message, MessageCreate, MessageUpdate, SenderType
from app.crud.base import CRUDBase

class CRUDMessage(CRUDBase[Message, MessageCreate, MessageUpdate]):
    async def get_by_conversation(
        self, client: Client, *, conversation_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a specific conversation.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("conversation_id", str(conversation_id)) \
            .order("sent_at") \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Message(**item) for item in response.data]

    async def get_by_sender_type(
        self, client: Client, *, conversation_id: UUID, sender_type: SenderType, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages of a specific sender type in a conversation.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("conversation_id", str(conversation_id)) \
            .eq("sender", sender_type) \
            .order("sent_at") \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Message(**item) for item in response.data]

    async def count_by_conversation(
        self, client: Client, *, conversation_id: UUID
    ) -> int:
        """
        Count the number of messages in a conversation.
        """
        response = client.table(self.table_name) \
            .select("count", count="exact") \
            .eq("conversation_id", str(conversation_id)) \
            .execute()
        
        return response.count

    async def get_last_message(
        self, client: Client, *, conversation_id: UUID
    ) -> Optional[Message]:
        """
        Get the most recent message in a conversation.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("conversation_id", str(conversation_id)) \
            .order("sent_at", desc=True) \
            .limit(1) \
            .execute()
        
        data = response.data
        if data and len(data) > 0:
            return Message(**data[0])
        return None

# Create an instance of the CRUDMessage class
message = CRUDMessage(Message)