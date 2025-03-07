from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Body
from supabase import Client
from uuid import UUID

from app.api.dependencies.dependencies import get_client, get_current_user
from app.crud.user import user as user_crud
from app.crud.role import role as role_crud
from app.crud.user_role import user_role as user_role_crud
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(
    supabase_client: Client = Depends(get_client),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information including roles.
    """
    # Get user roles
    role_ids = await user_role_crud.get_roles_for_user(supabase_client, user_id=current_user.id)
    roles = []
    for role_id in role_ids:
        role = await role_crud.get(supabase_client, id=role_id)
        if role:
            roles.append(role.name)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "avatar_url": getattr(current_user, "avatar_url", None),
        "status": current_user.status,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login,
        "roles": roles
    }

#TODO: Assign the default role depending on the user's email domain
@router.post("/assign-default-role")
async def assign_default_role(
    supabase_client: Client = Depends(get_client),
    user_id: UUID = Body(...),
) -> Dict[str, str]:
    """
    Assign the default 'Estudiante' role to a user after signup.
    This endpoint should be called from your frontend after successful signup.
    """
    # Get the user
    user = await user_crud.get(supabase_client, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get the 'Estudiante' role
    student_role = await role_crud.get_by_name(supabase_client, name="Estudiante")
    if not student_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Default role 'Estudiante' not found"
        )
    
    # Check if user already has this role
    role_ids = await user_role_crud.get_roles_for_user(supabase_client, user_id=user_id)
    if student_role.id in role_ids:
        return {"message": "User already has the 'Estudiante' role"}
    
    # Assign the role to the user
    await user_role_crud.assign_role_to_user(
        supabase_client, user_id=user_id, role_id=student_role.id
    )
    
    return {"message": "Default role 'Estudiante' assigned successfully"}