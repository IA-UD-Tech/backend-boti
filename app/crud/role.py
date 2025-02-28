from typing import List, Optional
from supabase import Client
from app.models.role import Role, RoleCreate, RoleUpdate
from app.crud.base import CRUDBase

class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    async def get_by_name(self, client: Client, *, name: str) -> Optional[Role]:
        """
        Get a role by name.
        """
        response = client.table(self.table_name).select("*").eq("name", name).execute()
        data = response.data
        if data and len(data) > 0:
            return Role(**data[0])
        return None

    async def create(self, client: Client, *, obj_in: RoleCreate) -> Role:
        """
        Create a new role.
        """
        return await super().create(client, obj_in=obj_in)

    async def get_multi(
        self, client: Client, *, skip: int = 0, limit: int = 100
    ) -> List[Role]:
        """
        Get multiple roles with pagination.
        """
        response = client.table(self.table_name).select("*").range(skip, skip + limit - 1).execute()
        return [Role(**item) for item in response.data]

# Create an instance of the CRUDRole class
role = CRUDRole(Role)