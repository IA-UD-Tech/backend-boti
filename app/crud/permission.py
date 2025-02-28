from typing import List, Optional
from datetime import date
from uuid import UUID
from supabase import Client
from app.models.permission import Permission, PermissionCreate, PermissionUpdate, PermissionType
from app.crud.base import CRUDBase

class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    async def get_by_user_and_tool(
        self, client: Client, *, user_id: UUID, tool_id: int
    ) -> Optional[Permission]:
        """
        Get a permission by user_id and tool_id.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .eq("tool_id", tool_id) \
            .execute()
        
        data = response.data
        if data and len(data) > 0:
            return Permission(**data[0])
        return None

    async def get_by_user(
        self, client: Client, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Permission]:
        """
        Get all permissions for a specific user.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Permission(**item) for item in response.data]

    async def get_by_tool(
        self, client: Client, *, tool_id: int, skip: int = 0, limit: int = 100
    ) -> List[Permission]:
        """
        Get all permissions for a specific tool.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("tool_id", tool_id) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Permission(**item) for item in response.data]

    async def get_by_permission_type(
        self, client: Client, *, permission_type: PermissionType, skip: int = 0, limit: int = 100
    ) -> List[Permission]:
        """
        Get all permissions of a specific type.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("permission_type", permission_type) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Permission(**item) for item in response.data]

    async def increment_interaction_count(
        self, client: Client, *, user_id: UUID, tool_id: int
    ) -> Optional[Permission]:
        """
        Increment the interaction count for a user-tool permission.
        """
        permission = await self.get_by_user_and_tool(client, user_id=user_id, tool_id=tool_id)
        if permission:
            update_data = PermissionUpdate(
                interaction_count=permission.interaction_count + 1,
                updated_at=date.today()
            )
            return await self.update(client, db_obj=permission, obj_in=update_data)
        return None

    async def get_or_create(
        self, client: Client, *, user_id: UUID, tool_id: int, permission_type: PermissionType = PermissionType.USER
    ) -> Permission:
        """
        Get a permission if it exists, or create it if it doesn't.
        """
        permission = await self.get_by_user_and_tool(client, user_id=user_id, tool_id=tool_id)
        if permission:
            return permission
        
        permission_data = PermissionCreate(
            user_id=user_id,
            tool_id=tool_id,
            permission_type=permission_type,
            interaction_count=0
        )
        
        return await self.create(client, obj_in=permission_data)

# Create an instance of the CRUDPermission class
permission = CRUDPermission(Permission)