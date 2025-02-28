from typing import List, Optional, Dict, Any, Tuple, cast
from uuid import UUID
import json
from supabase import Client
from app.models.vector_embedding import VectorEmbedding, VectorEmbeddingCreate, VectorEmbeddingUpdate
from app.crud.base import CRUDBase
from app.services.embedding_service import embedding_service
from app.models.vector_types import Embedding

class CRUDVectorEmbedding(CRUDBase[VectorEmbedding, VectorEmbeddingCreate, VectorEmbeddingUpdate]):
    async def create_for_text(
        self, client: Client, *, text: str, obj_in: VectorEmbeddingCreate
    ) -> VectorEmbedding:
        """
        Create a vector embedding for a given text content.
        """
        # Generate embedding for the text
        vector = await embedding_service.get_embedding(text)
        
        # Convert the model to a dictionary
        obj_dict = obj_in.model_dump()
        
        # Add the vector to the object
        obj_dict["vector"] = vector
        
        # Insert into database
        response = client.table(self.table_name).insert(obj_dict).execute()
        
        # Convert the response data to a VectorEmbedding model
        return VectorEmbedding(**response.data[0])

    async def get_by_message(
        self, client: Client, *, message_id: UUID
    ) -> Optional[VectorEmbedding]:
        """
        Get the vector embedding for a specific message.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("message_id", str(message_id)) \
            .execute()
        
        data = response.data
        if data and len(data) > 0:
            return VectorEmbedding(**data[0])
        return None

    async def get_by_document(
        self, client: Client, *, document_id: UUID
    ) -> Optional[VectorEmbedding]:
        """
        Get the vector embedding for a specific document.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("document_id", str(document_id)) \
            .execute()
        
        data = response.data
        if data and len(data) > 0:
            return VectorEmbedding(**data[0])
        return None

    async def get_by_agent(
        self, client: Client, *, agent_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[VectorEmbedding]:
        """
        Get vector embeddings for a specific agent.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("agent_id", str(agent_id)) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [VectorEmbedding(**item) for item in response.data]

    async def search_similar(
        self, client: Client, *, query_text: str, limit: int = 5
    ) -> List[Tuple[VectorEmbedding, float]]:
        """
        Search for similar vector embeddings by semantic similarity to the query text.
        Returns vector embeddings with their similarity scores.
        """
        # Generate embedding for the query text
        query_vector = await embedding_service.get_embedding(query_text)
        
        # For RPC, we need to convert to JSON
        query_vector_json = json.dumps(query_vector)
        
        try:
            # Call Supabase RPC function for vector similarity search
            response = client.rpc(
                "match_vector_embeddings",
                {
                    "query_embedding": query_vector_json,
                    "match_threshold": 0.5,
                    "match_count": limit
                }
            ).execute()
            
            # Convert results to VectorEmbedding objects with scores
            results = []
            for item in response.data:
                # Exclude the similarity value from the embedding attributes
                embed_data = {k: v for k, v in item.items() if k != "similarity"}
                embedding = VectorEmbedding(**embed_data)
                similarity = item.get("similarity", 0.0)
                results.append((embedding, similarity))
            
            return results
        except Exception as e:
            # Fallback if RPC is not available
            print(f"Vector similarity search not available: {str(e)}")
            
            # Return empty results
            return []

# Create an instance of the CRUDVectorEmbedding class
vector_embedding = CRUDVectorEmbedding(VectorEmbedding)