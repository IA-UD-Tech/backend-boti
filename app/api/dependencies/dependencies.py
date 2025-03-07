from typing import List, Optional, Tuple
from fastapi import Depends, HTTPException, status, Header
from supabase import Client
from uuid import UUID

from app.db.session import get_supabase_client
from app.models.user import User
from app.crud.user import user as user_crud
from app.crud.role import role as role_crud
from app.crud.user_role import user_role as user_role_crud

async def get_client() -> Client:
    """Get Supabase client."""
    return await anext(get_supabase_client())

async def get_current_user(
    client: Client = Depends(get_client),
    authorization: Optional[str] = Header(None)
) -> User:
    """
    Get the current authenticated user based on the JWT token.
    
    Supabase handles token verification, we just need to extract user info.
    
    Args:
        client: Supabase client
        authorization: Bearer token from request header
        
    Returns:
        User: The authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Use Supabase's auth to get the user from the token
        response = client.auth.get_user(token)
        supabase_user = response.user
        
        if not supabase_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get or create user in our database based on Supabase auth user
        user = await user_crud.get_by_email(client, email=supabase_user.email)
        
        if not user:
            # Create the user if it doesn't exist in our database
            user_data = {
                "email": supabase_user.email,
                "name": supabase_user.user_metadata.get("full_name", supabase_user.email.split("@")[0]),
                "avatar_url": supabase_user.user_metadata.get("avatar_url"),
                "status": True,
            }
            user = await user_crud.create(client, obj_in=user_data)
        
        # Update last login
        await user_crud.update_last_login(client, user_id=user.id)
        
        return user
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_roles(
    client: Client,
    user_id: UUID
) -> List[str]:
    """
    Get all roles for a user.
    
    Args:
        client: Supabase client
        user_id: User ID
        
    Returns:
        List of role names
    """
    # Get role IDs for the user
    role_ids = await user_role_crud.get_roles_for_user(client, user_id=user_id)
    
    # Get role names
    roles = []
    for role_id in role_ids:
        role = await role_crud.get(client, id=role_id)
        if role:
            roles.append(role.name)
    
    return roles

async def get_current_user_with_roles(
    client: Client = Depends(get_client),
    current_user: User = Depends(get_current_user)
) -> Tuple[User, List[str]]:
    """
    Get the current user and their roles.
    
    Args:
        client: Supabase client
        current_user: Current authenticated user
        
    Returns:
        Tuple of (User, List[str]) containing the user and their role names
    """
    roles = await get_user_roles(client, current_user.id)
    return current_user, roles

def requires_roles(required_roles: List[str] = None):
    """
    Create a dependency that checks if the user has any of the required roles.
    
    Args:
        required_roles: List of role names. If None, any authenticated user is allowed.
        
    Returns:
        Dependency function that validates user roles
    """
    
    async def role_checker(
        user_with_roles: Tuple[User, List[str]] = Depends(get_current_user_with_roles)
    ) -> User:
        """
        Check if the user has any of the required roles.
        
        Args:
            user_with_roles: Tuple of (User, List[str]) containing the user and their roles
            
        Returns:
            User if validation passes
            
        Raises:
            HTTPException: If user doesn't have the required roles
        """
        user, roles = user_with_roles
        
        # If no specific roles are required, any authenticated user is allowed
        if not required_roles:
            return user
        
        # For Admin role, always allow access
        if "Admin" in roles:
            return user
        
        # Check if user has any of the required roles
        if not any(role in roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(required_roles)}",
            )
        
        return user
    
    return role_checker