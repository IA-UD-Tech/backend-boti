from typing import Any, List, Dict, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.agent import agent as agent_crud
from app.models.agent import Agent, AgentCreate, AgentUpdate, AgentRead
from app.models.user import User
from app.api.dependencies.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=AgentRead)
async def create_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_in: AgentCreate,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new agent.
    """
    # Set the created_by field to the current user's ID if not provided
    if not agent_in.created_by:
        agent_in.created_by = current_user.id
        
    agent = await agent_crud.create(supabase_client, obj_in=agent_in)
    return agent

@router.get("/", response_model=List[AgentRead])
async def read_agents(
    *,
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    created_by: Optional[UUID] = None,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Retrieve agents with optional filtering by creator.
    """
    # If created_by is specified, filter by that user
    if created_by:
        agents = await agent_crud.get_by_created_by(
            supabase_client, created_by=created_by, skip=skip, limit=limit
        )
    else:
        agents = await agent_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return agents

@router.get("/{agent_id}", response_model=AgentRead)
async def read_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific agent by ID.
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
    current_user: User = Depends(get_current_user)
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
    # Optional: Check if user is allowed to update this agent
    if str(agent.created_by) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent"
        )
    agent = await agent_crud.update(supabase_client, db_obj=agent, obj_in=agent_in)
    return agent

@router.delete("/{agent_id}", response_model=AgentRead)
async def delete_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    current_user: User = Depends(get_current_user)
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
    # Optional: Check if user is allowed to delete this agent
    if str(agent.created_by) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this agent"
        )
    agent = await agent_crud.remove(supabase_client, id=agent_id)
    return agent

@router.post("/{agent_id}/subscribe", response_model=AgentRead)
async def subscribe_student_to_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    student_email: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Subscribe a student (identified by email) to an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check if user has permission to modify this agent
    if str(agent.created_by) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent"
        )
    
    # Get current list of subscribed students
    students = agent.students if agent.students else []
    
    # Add new student if not already subscribed
    if student_email not in students:
        students.append(student_email)
    
    # Update the agent with the new student list
    update_data = AgentUpdate(students=students)
    updated_agent = await agent_crud.update(supabase_client, db_obj=agent, obj_in=update_data)
    return updated_agent

@router.delete("/{agent_id}/unsubscribe", response_model=AgentRead)
async def unsubscribe_student_from_agent(
    *,
    supabase_client: Client = Depends(get_client),
    agent_id: UUID,
    student_email: str = Body(..., embed=True),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Unsubscribe a student from an agent.
    """
    agent = await agent_crud.get(supabase_client, id=agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Check permissions
    if str(agent.created_by) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this agent"
        )
    
    # Remove student from list
    students = agent.students if agent.students else []
    if student_email in students:
        students.remove(student_email)
    
    # Update the agent
    update_data = AgentUpdate(students=students)
    updated_agent = await agent_crud.update(supabase_client, db_obj=agent, obj_in=update_data)
    return updated_agent

@router.get("/by-student/{student_email}", response_model=List[AgentRead])
async def get_agents_by_student(
    *,
    supabase_client: Client = Depends(get_client),
    student_email: str,
    skip: int = 0, 
    limit: int = 100
) -> Any:
    """
    Get all agents a student is subscribed to.
    """
    agents = await agent_crud.get_by_student_email(
        supabase_client, student_email=student_email, skip=skip, limit=limit
    )
    return agents