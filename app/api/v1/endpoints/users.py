from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.dependencies.dependencies import get_client
from app.crud.user import user as user_crud
from app.models.user import User, UserCreate, UserRead, UserUpdate

router = APIRouter()

@router.post("/", response_model=UserRead)
async def create_user(
    *,
    supabase_client: Client = Depends(get_client),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await user_crud.get_by_email(supabase_client, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = await user_crud.create(supabase_client, obj_in=user_in)
    return user

@router.get("/", response_model=List[UserRead])
async def read_users(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve users.
    """
    users = await user_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserRead)
async def read_user_by_id(
    user_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific user by id.
    """
    user = await user_crud.get(supabase_client, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    *,
    supabase_client: Client = Depends(get_client),
    user_id: UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    user = await user_crud.get(supabase_client, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user = await user_crud.update(supabase_client, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=UserRead)
async def delete_user(
    *,
    supabase_client: Client = Depends(get_client),
    user_id: UUID,
) -> Any:
    """
    Delete a user.
    """
    user = await user_crud.get(supabase_client, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user = await user_crud.remove(supabase_client, id=user_id)
    return user