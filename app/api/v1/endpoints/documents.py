from typing import Any, List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from pydantic import BaseModel

from app.api.dependencies.dependencies import get_client
from app.crud.document import document as document_crud
from app.models.document import Document, DocumentCreate, DocumentRead, DocumentUpdate

router = APIRouter()

class SearchResult(BaseModel):
    document: DocumentRead
    similarity: float

class SearchResponse(BaseModel):
    results: List[SearchResult]

@router.post("/", response_model=DocumentRead)
async def create_document(
    *,
    supabase_client: Client = Depends(get_client),
    document_in: DocumentCreate,
) -> Any:
    """
    Create a new document with automatic embedding generation.
    """
    document = await document_crud.create_with_vector(supabase_client, obj_in=document_in)
    return document

@router.get("/", response_model=List[DocumentRead])
async def read_documents(
    supabase_client: Client = Depends(get_client),
    skip: int = 0,
    limit: int = 100,
    agent_id: Optional[UUID] = None,
    tool_id: Optional[int] = None,
) -> Any:
    """
    Retrieve documents with optional filtering by agent or tool.
    """
    if agent_id:
        documents = await document_crud.get_by_agent(
            supabase_client, agent_id=agent_id, skip=skip, limit=limit
        )
    elif tool_id:
        documents = await document_crud.get_by_tool(
            supabase_client, tool_id=tool_id, skip=skip, limit=limit
        )
    else:
        documents = await document_crud.get_multi(supabase_client, skip=skip, limit=limit)
    return documents

@router.get("/{document_id}", response_model=DocumentRead)
async def read_document(
    document_id: UUID,
    supabase_client: Client = Depends(get_client),
) -> Any:
    """
    Get a specific document by ID.
    """
    document = await document_crud.get(supabase_client, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return document

@router.put("/{document_id}", response_model=DocumentRead)
async def update_document(
    *,
    supabase_client: Client = Depends(get_client),
    document_id: UUID,
    document_in: DocumentUpdate,
) -> Any:
    """
    Update a document with automatic re-embedding if text content changes.
    """
    document = await document_crud.get(supabase_client, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document = await document_crud.update_with_vector(
        supabase_client, db_obj=document, obj_in=document_in
    )
    return document

@router.delete("/{document_id}", response_model=DocumentRead)
async def delete_document(
    *,
    supabase_client: Client = Depends(get_client),
    document_id: UUID,
) -> Any:
    """
    Delete a document.
    """
    document = await document_crud.get(supabase_client, id=document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    document = await document_crud.remove(supabase_client, id=document_id)
    return document

@router.post("/search", response_model=SearchResponse)
async def search_documents(
    *,
    supabase_client: Client = Depends(get_client),
    query: str,
    limit: int = 5,
) -> Any:
    """
    Search for documents by semantic similarity to the query text.
    """
    results = await document_crud.search_by_vector(
        supabase_client, query_text=query, limit=limit
    )
    
    search_results = [
        SearchResult(document=doc, similarity=score)
        for doc, score in results
    ]
    
    return SearchResponse(results=search_results)