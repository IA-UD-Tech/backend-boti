from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.models.agent import Agent, AgentCreate, AgentUpdate
from app.crud.base import CRUDBase

class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    async def get_by_name(self, client: Client, *, name: str) -> Optional[Agent]:
        """
        Get an agent by name.
        """
        response = client.table(self.table_name).select("*").eq("name", name).execute()
        data = response.data
        if data and len(data) > 0:
            return Agent(**data[0])
        return None

    async def get_by_tool(
        self, client: Client, *, tool_id: int, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """
        Get all agents associated with a specific tool.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("tool_id", tool_id) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Agent(**item) for item in response.data]

    async def get_by_type(
        self, client: Client, *, agent_type: str, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        """
        Get all agents of a specific type.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("type", agent_type) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Agent(**item) for item in response.data]

# Create an instance of the CRUDAgent class
agent = CRUDAgent(Agent)