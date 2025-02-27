from typing import List, Optional
from uuid import UUID
from datetime import datetime
from supabase import Client
from app.models.user import User, UserCreate, UserUpdate
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, client: Client, *, email: str) -> Optional[User]:
        response = client.table(self.table_name).select("*").eq("email", email).execute()
        data = response.data
        if data and len(data) > 0:
            return User(**data[0])
        return None

    async def create(self, client: Client, *, obj_in: UserCreate) -> User:
        # Here you could add password hashing if needed
        return await super().create(client, obj_in=obj_in)

    async def get_multi_with_filter(
        self, client: Client, *, skip: int = 0, limit: int = 100, estado: bool = None
    ) -> List[User]:
        if estado is None:
            return await self.get_multi(client=client, skip=skip, limit=limit)
        
        response = client.table(self.table_name).select("*").eq("estado", estado).range(skip, skip + limit - 1).execute()
        return [User(**item) for item in response.data]
    
    async def update_last_login(self, client: Client, *, user_id: UUID) -> Optional[User]:
        user = await self.get(client=client, id=user_id)
        if user:
            response = client.table(self.table_name).update({"ultima_conexion": datetime.utcnow().isoformat()}).eq("id", str(user_id)).execute()
            if response.data and len(response.data) > 0:
                return User(**response.data[0])
        return user

# Only pass the model, no need to specify table name separately
user = CRUDUser(User)