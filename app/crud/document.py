from typing import List, Optional, Dict, Any, Tuple, cast
from uuid import UUID
import json
from supabase import Client
from app.models.document import Document, DocumentCreate, DocumentUpdate, DocumentWithVector
from app.crud.base import CRUDBase
from app.services.embedding_service import embedding_service
from app.models.vector_types import Embedding

class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def create_with_vector(
        self, client: Client, *, obj_in: DocumentCreate
    ) -> Document:
        """
        Create a document with its embedding vector.
        """
        # Generate embedding for the document text
        vector = await embedding_service.get_embedding(obj_in.text_content)
        
        # Convert the model to a dictionary
        obj_dict = obj_in.model_dump()
        
        # Add the vector directly (our PgVector type handles the conversion)
        obj_dict["vector"] = vector
        
        # Insert into database
        response = client.table(self.table_name).insert(obj_dict).execute()
        
        # Convert the response data to a Document model
        return Document(**response.data[0])

    async def update_with_vector(
        self, client: Client, *, db_obj: Document, obj_in: DocumentUpdate
    ) -> Document:
        """
        Update a document and its embedding vector if text content changes.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        
        # If text content is being updated, regenerate the vector
        if "text_content" in update_data:
            vector = await embedding_service.get_embedding(update_data["text_content"])
            update_data["vector"] = vector
        
        # Update in database
        response = client.table(self.table_name).update(update_data).eq("id", str(db_obj.id)).execute()
        
        # Convert the response data to a Document model
        return Document(**response.data[0])

    async def get_by_agent(
        self, client: Client, *, agent_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Get all documents associated with a specific agent.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("agent_id", str(agent_id)) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Document(**item) for item in response.data]

    async def get_by_tool(
        self, client: Client, *, tool_id: int, skip: int = 0, limit: int = 100
    ) -> List[Document]:
        """
        Get all documents associated with a specific tool.
        """
        response = client.table(self.table_name) \
            .select("*") \
            .eq("tool_id", tool_id) \
            .range(skip, skip + limit - 1) \
            .execute()
        
        return [Document(**item) for item in response.data]

    async def search_by_vector(
        self, client: Client, *, query_text: str, limit: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for documents by semantic similarity to the query text.
        Returns documents with their similarity scores.
        """
        # Generate embedding for the query text
        query_vector = await embedding_service.get_embedding(query_text)
        
        # For RPC, we still need to convert to JSON
        query_vector_json = json.dumps(query_vector)
        
        # Because we're using Supabase and can't directly use pgvector operators,
        # we'll use a stored procedure (match_documents) to perform the search
        try:
            response = client.rpc(
                "match_documents",
                {
                    "query_embedding": query_vector_json,
                    "match_threshold": 0.5,
                    "match_count": limit
                }
            ).execute()
            
            # Convert results to Document objects with scores
            results = []
            for item in response.data:
                # Exclude the similarity value from the document attributes
                doc_data = {k: v for k, v in item.items() if k != "similarity"}
                doc = Document(**doc_data)
                similarity = item.get("similarity", 0.0)
                results.append((doc, similarity))
            
            return results
        except Exception as e:
            # Fallback if RPC is not available
            # This would happen if the match_documents function is not defined in Supabase
            print(f"Vector search not available: {str(e)}")
            
            # Return empty results
            return []

# Create an instance of the CRUDDocument class
document = CRUDDocument(Document)