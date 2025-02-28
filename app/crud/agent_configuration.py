from typing import List, Optional, Dict
from uuid import UUID
from supabase import Client
from app.models.agent_configuration import AgentConfiguration, AgentConfigurationCreate, AgentConfigurationUpdate
from app.crud.base import CRUDBase

class CRUDAgentConfiguration(CRUDBase[AgentConfiguration, AgentConfigurationCreate, AgentConfigurationUpdate]):
    async def get_by_agent(
        self, client: Client, *, agent_id: UUID
    ) -> List[AgentConfiguration]:
        """
        Get all configuration parameters for a specific agent.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("agent_id", str(agent_id)) \
            .execute()
        
        return [AgentConfiguration(**item) for item in response.data]
    
    async def get_by_parameter(
        self, client: Client, *, agent_id: UUID, parameter: str
    ) -> Optional[AgentConfiguration]:
        """
        Get a specific configuration parameter for an agent.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("agent_id", str(agent_id)) \
            .eq("parameter", parameter) \
            .execute()
        
        data = response.data
        if data and len(data) > 0:
            return AgentConfiguration(**data[0])
        return None
    
    async def upsert_parameter(
        self, client: Client, *, agent_id: UUID, parameter: str, value: str
    ) -> AgentConfiguration:
        """
        Update a parameter if it exists, or create it if it doesn't.
        """
        existing = await self.get_by_parameter(client, agent_id=agent_id, parameter=parameter)
        
        if existing:
            update_data = AgentConfigurationUpdate(value=value)
            return await self.update(client, db_obj=existing, obj_in=update_data)
        else:
            create_data = AgentConfigurationCreate(
                agent_id=agent_id,
                parameter=parameter,
                value=value
            )
            return await self.create(client, obj_in=create_data)
    
    async def get_config_dict(
        self, client: Client, *, agent_id: UUID
    ) -> Dict[str, str]:
        """
        Get all configuration for an agent as a dictionary.
        """
        configs = await self.get_by_agent(client, agent_id=agent_id)
        return {config.parameter: config.value for config in configs}

# Create an instance of the CRUDAgentConfiguration class
agent_configuration = CRUDAgentConfiguration(AgentConfiguration)