from typing import Any, List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.agent import agent as agent_crud
from app.crud.agent_configuration import agent_configuration as config_crud
from app.models.agent import Agent, AgentCreate, AgentRead, AgentUpdate
from app.models.agent_configuration import AgentConfigurationCreate, AgentConfigurationRead, AgentConfigurationUpdate

router = APIRouter()

@router.post("/", response_model=AgentRead)
async def create_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_in: AgentCreate,
) -> Any:
    """
    Create new agent.
    """
    agent = await agent_crud.create(supabase_client, obj_in=agent_in)
    return agent

@router.get("/", response_model=List[AgentRead])
async def read_agents(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    tool_id: Optional[int] = None,
    agent_type: Optional[str] = None,
) -> Any:
    """
    Retrieve agents with optional filtering by tool or type.
    """
    if tool_id:
        agents = await agent_crud.get_by_tool(
            supabase_client, tool_id=tool_id, skip=skip, limit=limit
        )
    elif agent_type:
        agents = await agent_crud.get_by_type(
            supabase_client, agent_type=agent_type, skip=skip, limit=limit
        )
    else:
        agents = await agent_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return agents

@router.get("/{agent_id}", response_model=AgentRead)
async def read_agent_by_id(
    agent_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific agent by id.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    return agent

@router.put("/{agent_id}", response_model=AgentRead)
async def update_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    agent_in: AgentUpdate,
) -> Any:
    """
    Update an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    agent = await agent_crud.update(supabase_client, db_obj=agent, obj_in=agent_in)
    return agent

@router.delete("/{agent_id}", response_model=AgentRead)
async def delete_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
) -> Any:
    """
    Delete an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    agent = await agent_crud.remove(supabase_client, id=agent_id)
    return agent

# Agent Configuration Endpoints

@router.get("/{agent_id}/config", response_model=List[AgentConfigurationRead])
async def read_agent_config(
    agent_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get all configuration for an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    config = await config_crud.get_by_agent(supabase_client, agent_id=agent_id)
    return config

@router.get("/{agent_id}/config/dict", response_model=Dict[str, str])
async def read_agent_config_dict(
    agent_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get all configuration for an agent as a dictionary.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    config_dict = await config_crud.get_config_dict(supabase_client, agent_id=agent_id)
    return config_dict

@router.post("/{agent_id}/config", response_model=AgentConfigurationRead)
async def create_agent_config(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    parameter: str,
    value: str,
) -> Any:
    """
    Add a configuration parameter to an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    config = AgentConfigurationCreate(agent_id=agent_id, parameter=parameter, value=value)
    return await config_crud.create(supabase_client, obj_in=config)

@router.put("/{agent_id}/config/{parameter}", response_model=AgentConfigurationRead)
async def update_agent_config(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    parameter: str,
    value: str,
) -> Any:
    """
    Update a configuration parameter for an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    config = await config_crud.get_by_parameter(
        supabase_client, agent_id=agent_id, parameter=parameter
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration parameter '{parameter}' not found for this agent"
        )
    
    update_data = AgentConfigurationUpdate(value=value)
    return await config_crud.update(supabase_client, db_obj=config, obj_in=update_data)

@router.patch("/{agent_id}/config/{parameter}", response_model=AgentConfigurationRead)
async def upsert_agent_config(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    parameter: str,
    value: str,
) -> Any:
    """
    Update a configuration parameter if it exists, or create it if it doesn't.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return await config_crud.upsert_parameter(
        supabase_client, agent_id=agent_id, parameter=parameter, value=value
    )

@router.delete("/{agent_id}/config/{parameter}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_config(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    parameter: str,
):
    """
    Delete a configuration parameter from an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    config = await config_crud.get_by_parameter(
        supabase_client, agent_id=agent_id, parameter=parameter
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration parameter '{parameter}' not found for this agent"
        )
    
    await config_crud.remove(supabase_client, id=config.id)