from typing import List, Optional
from uuid import UUID
from supabase import Client
from app.models.user_role import UserRole, UserRoleCreate
from app.crud.base import CRUDBase

class CRUDUserRole(CRUDBase[UserRole, UserRoleCreate, None]):
    async def get_roles_for_user(self, client: Client, *, user_id: UUID) -> List[int]:
        """
        Get all role IDs associated with a user.
        """
        response = client.table(self.table_name).select("role_id").eq("user_id", str(user_id)).execute()
        return [item["role_id"] for item in response.data] if response.data else []
    
    async def get_users_for_role(self, client: Client, *, role_id: int) -> List[UUID]:
        """
        Get all user IDs associated with a role.
        """
        response = client.table(self.table_name).select("user_id").eq("role_id", role_id).execute()
        return [UUID(item["user_id"]) for item in response.data] if response.data else []
    
    async def assign_role_to_user(self, client: Client, *, user_id: UUID, role_id: int) -> Optional[UserRole]:
        """
        Assign a role to a user.
        """
        role_assignment = UserRoleCreate(
            user_id=user_id,
            role_id=role_id
        )
        
        try:
            return await super().create(client, obj_in=role_assignment)
        except Exception:
            # Handle case where the assignment already exists
            return None
    
    async def remove_role_from_user(self, client: Client, *, user_id: UUID, role_id: int) -> bool:
        """
        Remove a role from a user.
        """
        response = client.table(self.table_name).delete() \
            .eq("user_id", str(user_id)) \
            .eq("role_id", role_id) \
            .execute()
            
        return bool(response.data)

# Create an instance of CRUDUserRole
user_role = CRUDUserRole(UserRole)