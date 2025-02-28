from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.permission import permission as permission_crud
from app.models.permission import Permission, PermissionCreate, PermissionRead, PermissionUpdate, PermissionType

router = APIRouter()

@router.post("/", response_model=PermissionRead)
async def create_permission(
    *,
    supabase_client: Client = Depends(get_client),
    permission_in: PermissionCreate,
) -> Any:
    """
    Create a new permission.
    """
    # Check if permission already exists
    existing = await permission_crud.get_by_user_and_tool(
        supabase_client, 
        user_id=permission_in.user_id, 
        tool_id=permission_in.tool_id
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permission already exists for this user and tool"
        )
    
    permission = await permission_crud.create(supabase_client, obj_in=permission_in)
    return permission

@router.get("/", response_model=List[PermissionRead])
async def read_permissions(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    tool_id: Optional[int] = None,
    permission_type: Optional[PermissionType] = None,
) -> Any:
    """
    Retrieve permissions with optional filtering.
    """
    if user_id:
        permissions = await permission_crud.get_by_user(
            supabase_client, user_id=user_id, skip=skip, limit=limit
        )
    elif tool_id:
        permissions = await permission_crud.get_by_tool(
            supabase_client, tool_id=tool_id, skip=skip, limit=limit
        )
    elif permission_type:
        permissions = await permission_crud.get_by_permission_type(
            supabase_client, permission_type=permission_type, skip=skip, limit=limit
        )
    else:
        permissions = await permission_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return permissions

@router.get("/{permission_id}", response_model=PermissionRead)
async def read_permission(
    permission_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific permission by ID.
    """
    permission = await permission_crud.get(supabase_client, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    return permission

@router.put("/{permission_id}", response_model=PermissionRead)
async def update_permission(
    *,
    supabase_client: Client = Depends(get_client),
    permission_id: UUID,
    permission_in: PermissionUpdate,
) -> Any:
    """
    Update a permission.
    """
    permission = await permission_crud.get(supabase_client, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    
    permission = await permission_crud.update(
        supabase_client, db_obj=permission, obj_in=permission_in
    )
    return permission

@router.delete("/{permission_id}", response_model=PermissionRead)
async def delete_permission(
    *,
    supabase_client: Client = Depends(get_client),
    permission_id: UUID,
) -> Any:
    """
    Delete a permission.
    """
    permission = await permission_crud.get(supabase_client, id=permission_id)
    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )
    permission = await permission_crud.remove(supabase_client, id=permission_id)
    return permission

@router.get("/check/{user_id}/{tool_id}", response_model=PermissionRead)
async def check_permission(
    user_id: UUID,
    tool_id: int,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Check if a user has permission for a tool. Creates a default permission if none exists.
    """
    permission = await permission_crud.get_or_create(
        supabase_client, user_id=user_id, tool_id=tool_id
    )
    return permission

@router.post("/increment/{user_id}/{tool_id}", response_model=PermissionRead)
async def increment_interaction(
    user_id: UUID,
    tool_id: int,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Increment the interaction count for a user-tool permission.
    """
    permission = await permission_crud.get_or_create(
        supabase_client, user_id=user_id, tool_id=tool_id
    )
    
    updated_permission = await permission_crud.increment_interaction_count(
        supabase_client, user_id=user_id, tool_id=tool_id
    )
    
    return updated_permission