from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from supabase import Client
import httpx
import logging

# Set up logging
logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A Pydantic model class with table_name in Config
        """
        self.model = model
        # Get table name from various possible locations with fallbacks
        try:
            # Try to get from model.Config.__tablename__
            self.table_name = getattr(model, "Config", None) and getattr(model.Config, "__tablename__", None)
            # If not found, try direct __tablename__ attribute
            if not self.table_name and hasattr(model, "__tablename__"):
                self.table_name = model.__tablename__
            # Fallback to model name in lowercase
            if not self.table_name:
                self.table_name = model.__name__.lower()
        except AttributeError:
            # Final fallback
            self.table_name = model.__name__.lower()
        
    async def get(self, client: Client, id: UUID) -> Optional[ModelType]:
        try:
            response = client.table(self.table_name).select("*").eq("id", str(id)).execute()
            data = response.data
            if data and len(data) > 0:
                return self.model(**data[0])
            return None
        except httpx.ConnectError as e:
            logger.error(f"Connection error when getting item by id {id}: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting item by id {id}: {str(e)}")
            raise

    async def get_multi(
        self, client: Client, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            print(client)
            response = client.table(self.table_name).select("*").range(skip, skip + limit - 1).execute()
            return [self.model(**item) for item in response.data]
        except httpx.ConnectError as e:
            logger.error(f"Connection error when getting multiple items: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting multiple items: {str(e)}")
            raise
        
    async def count(self, client: Client) -> int:
        try:
            response = client.table(self.table_name).select("count", count="exact").execute()
            return response.count
        except httpx.ConnectError as e:
            logger.error(f"Connection error when counting items: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error counting items: {str(e)}")
            raise

    async def create(self, client: Client, *, obj_in: CreateSchemaType) -> ModelType:
        try:
            obj_in_data = jsonable_encoder(obj_in)
            response = client.table(self.table_name).insert(obj_in_data).execute()
            return self.model(**response.data[0])
        except httpx.ConnectError as e:
            logger.error(f"Connection error when creating item: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            raise

    async def update(
        self,
        client: Client,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)
            
            obj_id = getattr(db_obj, "id")
            response = client.table(self.table_name).update(update_data).eq("id", str(obj_id)).execute()
            return self.model(**response.data[0])
        except httpx.ConnectError as e:
            logger.error(f"Connection error when updating item: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            raise

    async def remove(self, client: Client, *, id: UUID) -> ModelType:
        try:
            response = client.table(self.table_name).delete().eq("id", str(id)).execute()
            if response.data and len(response.data) > 0:
                return self.model(**response.data[0])
            return None
        except httpx.ConnectError as e:
            logger.error(f"Connection error when removing item with id {id}: {str(e)}")
            raise ValueError(f"Database connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Error removing item with id {id}: {str(e)}")
            raise