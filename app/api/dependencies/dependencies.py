from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from supabase import Client

from app.db.session import get_supabase_client
from app.crud.user import user as user_crud
from app.models.user import User

async def get_client() -> Client:
    return await anext(get_supabase_client())

# async def get_current_user(
#     client: Client = Depends(get_client),
#     # Add authentication logic here
# ) -> User:
#     # This is a placeholder. In a real application, you would authenticate the user
#     # For example, using JWT tokens, OAuth, etc.
#     user = await user_crud.get(client, id="some-uuid")  # Replace with actual authentication
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Could not validate credentials",
#         )
#
#     return user