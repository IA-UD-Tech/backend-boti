from typing import Any, List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from pydantic import BaseModel

from app.api.dependencies.dependencies import get_client
from app.crud.vector_embedding import vector_embedding as vector_embedding_crud
from app.crud.message import message as message_crud
from app.crud.document import document as document_crud
from app.models.vector_embedding import VectorEmbedding, VectorEmbeddingCreate, VectorEmbeddingRead, VectorEmbeddingWithVector

router = APIRouter()

class SearchResult(BaseModel):
    embedding: VectorEmbeddingRead
    similarity: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@router.post("/message/{message_id}", response_model=VectorEmbeddingRead)
async def create_for_message(
    *,
    supabase_client: Client = Depends(get_client),
    message_id: UUID,
) -> Any:
    """
    Create a vector embedding for a message.
    """
    # Check if message exists
    message = await message_crud.get(supabase_client, id=message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Check if embedding already exists
    existing = await vector_embedding_crud.get_by_message(supabase_client, message_id=message_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vector embedding already exists for this message"
        )
    
    # Create the embedding
    embedding_in = VectorEmbeddingCreate(message_id=message_id)
    embedding = await vector_embedding_crud.create_for_text(
        supabase_client, text=message.content, obj_in=embedding_in
    )
    
    return embedding

@router.post("/document/{document_id}", response_model=VectorEmbeddingRead)
async def create_for_document(
    *,
    supabase_client: Client = Depends(get_client),
    document_id: UUID,
) -> Any:
    """
    Create a vector embedding for a document.
    """
    # Check if document exists
    document = await document_crud.get(supabase_client, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check if embedding already exists
    existing = await vector_embedding_crud.get_by_document(supabase_client, document_id=document_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vector embedding already exists for this document"
        )
    
    # Create the embedding
    embedding_in = VectorEmbeddingCreate(document_id=document_id)
    embedding = await vector_embedding_crud.create_for_text(
        supabase_client, text=document.text_content, obj_in=embedding_in
    )
    
    return embedding

@router.get("/", response_model=List[VectorEmbeddingRead])
async def read_vector_embeddings(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[UUID] = None,
) -> Any:
    """
    Retrieve vector embeddings with optional filtering by agent.
    """
    if agent_id:
        embeddings = await vector_embedding_crud.get_by_agent(
            supabase_client, agent_id=agent_id, skip=skip, limit=limit
        )
    else:
        embeddings = await vector_embedding_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return embeddings

@router.get("/{embedding_id}", response_model=VectorEmbeddingRead)
async def read_vector_embedding(
    embedding_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific vector embedding by ID.
    """
    embedding = await vector_embedding_crud.get(supabase_client, id=embedding_id)
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector embedding not found"
        )
    return embedding

@router.get("/message/{message_id}", response_model=VectorEmbeddingRead)
async def get_for_message(
    message_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get the vector embedding for a specific message.
    """
    embedding = await vector_embedding_crud.get_by_message(supabase_client, message_id=message_id)
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector embedding not found for this message"
        )
    return embedding

@router.get("/document/{document_id}", response_model=VectorEmbeddingRead)
async def get_for_document(
    document_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get the vector embedding for a specific document.
    """
    embedding = await vector_embedding_crud.get_by_document(supabase_client, document_id=document_id)
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector embedding not found for this document"
        )
    return embedding

@router.delete("/{embedding_id}", response_model=VectorEmbeddingRead)
async def delete_vector_embedding(
    *,
    supabase_client: Client = Depends(get_client),
    embedding_id: UUID,
) -> Any:
    """
    Delete a vector embedding.
    """
    embedding = await vector_embedding_crud.get(supabase_client, id=embedding_id)
    if not embedding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vector embedding not found"
        )
    embedding = await vector_embedding_crud.remove(supabase_client, id=embedding_id)
    return embedding

@router.post("/search", response_model=SearchResponse)
async def search_vector_embeddings(
    *,
    supabase_client: Client = Depends(get_client),
    query: str,
    limit: int = 5,
) -> Any:
    """
    Search for similar vector embeddings by semantic similarity to the query text.
    """
    results = await vector_embedding_crud.search_similar(
        supabase_client, query_text=query, limit=limit
    )
    
    search_results = [
        SearchResult(embedding=embedding, similarity=score)
        for embedding, score in results
    ]
    
    return SearchResponse(results=search_results)