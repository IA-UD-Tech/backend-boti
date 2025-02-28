from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.role import role as role_crud
from app.crud.user_role import user_role as user_role_crud
from app.models.role import Role, RoleCreate, RoleRead, RoleUpdate
from app.models.user_role import UserRoleCreate

router = APIRouter()

@router.post("/", response_model=RoleRead)
async def create_role(
    *,
    supabase_client: Client = Depends(get_client),
    role_in: RoleCreate,
) -> Any:
    """
    Create new role.
    """
    role = await role_crud.get_by_name(supabase_client, name=role_in.name)
    if role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The role with this name already exists in the system.",
        )
    role = await role_crud.create(supabase_client, obj_in=role_in)
    return role

@router.get("/", response_model=List[RoleRead])
async def read_roles(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve roles.
    """
    roles = await role_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return roles

@router.get("/{role_id}", response_model=RoleRead)
async def read_role_by_id(
    role_id: int,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific role by id.
    """
    role = await role_crud.get(supabase_client, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.put("/{role_id}", response_model=RoleRead)
async def update_role(
    *,
    supabase_client: Client = Depends(get_client),
    role_id: int,
    role_in: RoleUpdate,
) -> Any:
    """
    Update a role.
    """
    role = await role_crud.get(supabase_client, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    role = await role_crud.update(supabase_client, db_obj=role, obj_in=role_in)
    return role

@router.delete("/{role_id}", response_model=RoleRead)
async def delete_role(
    *,
    supabase_client: Client = Depends(get_client),
    role_id: int,
) -> Any:
    """
    Delete a role.
    """
    role = await role_crud.get(supabase_client, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    role = await role_crud.remove(supabase_client, id=role_id)
    return role

# User-Role relationship endpoints
@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_role_to_user(
    *,
    supabase_client: Client = Depends(get_client),
    user_id: UUID,
    role_id: int,
) -> Any:
    """
    Assign a role to a user.
    """
    # Check if role exists
    role = await role_crud.get(supabase_client, id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    # Assign role to user
    result = await user_role_crud.assign_role_to_user(
        supabase_client, user_id=user_id, role_id=role_id
    )
    
    if not result:
        return {"message": "Role assignment already exists"}
    
    return {"message": "Role assigned successfully"}

@router.delete("/remove", status_code=status.HTTP_200_OK)
async def remove_role_from_user(
    *,
    supabase_client: Client = Depends(get_client),
    user_id: UUID,
    role_id: int,
) -> Any:
    """
    Remove a role from a user.
    """
    result = await user_role_crud.remove_role_from_user(
        supabase_client, user_id=user_id, role_id=role_id
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role assignment not found"
        )
    
    return {"message": "Role removed successfully"}

@router.get("/user/{user_id}", response_model=List[RoleRead])
async def get_user_roles(
    user_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get all roles assigned to a user.
    """
    role_ids = await user_role_crud.get_roles_for_user(supabase_client, user_id=user_id)
    roles = []
    
    for role_id in role_ids:
        role = await role_crud.get(supabase_client, id=role_id)
        if role:
            roles.append(role)
    
    return roles