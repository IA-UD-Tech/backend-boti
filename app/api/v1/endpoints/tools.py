from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.tool import tool as tool_crud
from app.models.tool import Tool, ToolCreate, ToolRead, ToolUpdate

router = APIRouter()

@router.post("/", response_model=ToolRead)
async def create_tool(
    *,
    supabase_client: Client = Depends(get_client),
    tool_in: ToolCreate,
) -> Any:
    """
    Create new tool.
    """
    tool = await tool_crud.get_by_name(supabase_client, name=tool_in.name)
    if tool:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A tool with this name already exists in the system.",
        )
    tool = await tool_crud.create(supabase_client, obj_in=tool_in)
    return tool

@router.get("/", response_model=List[ToolRead])
async def read_tools(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    creator_id: Optional[UUID] = None,
    tool_type: Optional[str] = None,
) -> Any:
    """
    Retrieve tools with optional filtering by creator or type.
    """
    if creator_id:
        tools = await tool_crud.get_by_creator(
            supabase_client, creator_id=creator_id, skip=skip, limit=limit
        )
    elif tool_type:
        tools = await tool_crud.get_by_type(
            supabase_client, tool_type=tool_type, skip=skip, limit=limit
        )
    else:
        tools = await tool_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return tools

@router.get("/{tool_id}", response_model=ToolRead)
async def read_tool_by_id(
    tool_id: int,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific tool by id.
    """
    tool = await tool_crud.get(supabase_client, id=tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    return tool

@router.put("/{tool_id}", response_model=ToolRead)
async def update_tool(
    *,
    supabase_client: Client = Depends(get_client),
    tool_id: int,
    tool_in: ToolUpdate,
) -> Any:
    """
    Update a tool.
    """
    tool = await tool_crud.get(supabase_client, id=tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Check name uniqueness if name is being updated
    if tool_in.name and tool_in.name != tool.name:
        existing_tool = await tool_crud.get_by_name(supabase_client, name=tool_in.name)
        if existing_tool:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A tool with this name already exists in the system.",
            )
    
    tool = await tool_crud.update(supabase_client, db_obj=tool, obj_in=tool_in)
    return tool

@router.delete("/{tool_id}", response_model=ToolRead)
async def delete_tool(
    *,
    supabase_client: Client = Depends(get_client),
    tool_id: int,
) -> Any:
    """
    Delete a tool.
    """
    tool = await tool_crud.get(supabase_client, id=tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    tool = await tool_crud.remove(supabase_client, id=tool_id)
    return tool