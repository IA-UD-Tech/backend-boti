from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.models.tool import Tool, ToolCreate, ToolUpdate
from app.crud.base import CRUDBase

class CRUDTool(CRUDBase[Tool, ToolCreate, ToolUpdate]):
    async def get_by_name(self, client: Client, *, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        """
        response = client.table(self.table_name).select("*").eq("name", name).execute()
        data = response.data
        if data and len(data) > 0:
            return Tool(**data[0])
        return None

    async def get_by_creator(
        self, client: Client, *, creator_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Tool]:
        """
        Get all tools created by a specific user.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("creator_id", str(creator_id)) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Tool(**item) for item in response.data]

    async def get_by_type(
        self, client: Client, *, tool_type: str, skip: int = 0, limit: int = 100
    ) -> List[Tool]:
        """
        Get all tools of a specific type.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("type", tool_type) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Tool(**item) for item in response.data]

# Create an instance of the CRUDTool class
tool = CRUDTool(Tool)