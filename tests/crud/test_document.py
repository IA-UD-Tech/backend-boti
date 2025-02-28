import pytest
import uuid
import json
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from app.crud.document import CRUDDocument
from app.models.document import Document, DocumentCreate, DocumentUpdate
from app.services.embedding_service import embedding_service

from tests.factories import create_document_dict, create_document_create
from tests.utils import create_mock_response, dict_to_model_dict, generate_uuid

@pytest.mark.asyncio
async def test_create_with_vector(mock_embedding_service):
    # Create mock client
    mock_client = MagicMock()
    doc_create = create_document_create()
    
    # Test vector (normally provided by embedding_service)
    test_vector = [0.1] * 1536
    mock_embedding_service.get_embedding.return_value = test_vector
    
    # Setup document data for the mock response
    doc_id = generate_uuid()
    created_doc = {
        **doc_create.model_dump(),
        "id": doc_id,
        "vector": json.dumps(test_vector),
        "created_at": datetime.now().isoformat()
    }
    
    # Setup the mock response
    mock_response = create_mock_response(created_doc)
    mock_client.table().insert().execute.return_value = mock_response
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method
    result = await document_crud.create_with_vector(mock_client, obj_in=doc_create)
    
    # Check the result
    assert result is not None
    assert result.id == doc_id
    assert result.name == doc_create.name
    assert result.text_content == doc_create.text_content
    
    # Verify mock calls
    mock_embedding_service.get_embedding.assert_called_once_with(doc_create.text_content)
    mock_client.table.assert_called_once_with(document_crud.table_name)
    mock_client.table().insert.assert_called_once()
    
    # Check that vector was included in the insert
    insert_call_args = mock_client.table().insert.call_args
    assert "vector" in insert_call_args[0][0]
    assert insert_call_args[0][0]["vector"] == json.dumps(test_vector)

@pytest.mark.asyncio
async def test_update_with_vector(mock_embedding_service):
    # Create mock client
    mock_client = MagicMock()
    doc_id = generate_uuid()
    doc_dict = create_document_dict(id=doc_id)
    doc = Document(**doc_dict)
    
    # Create update data
    new_text = "Updated document content"
    doc_update = DocumentUpdate(text_content=new_text)
    
    # Test vector (normally provided by embedding_service)
    test_vector = [0.2] * 1536  # Different from original vector
    mock_embedding_service.get_embedding.return_value = test_vector
    
    # Updated document dict
    updated_doc_dict = {**doc_dict, "text_content": new_text, "vector": json.dumps(test_vector)}
    
    # Setup the mock response
    mock_response = create_mock_response(updated_doc_dict)
    mock_client.table().update().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method
    result = await document_crud.update_with_vector(mock_client, db_obj=doc, obj_in=doc_update)
    
    # Check the result
    assert result is not None
    assert result.id == doc_id
    assert result.text_content == new_text
    
    # Verify mock calls
    mock_embedding_service.get_embedding.assert_called_once_with(new_text)
    mock_client.table.assert_called_once_with(document_crud.table_name)
    mock_client.table().update.assert_called_once()
    mock_client.table().update().eq.assert_called_once_with("id", str(doc_id))
    
    # Check that vector was included in the update
    update_call_args = mock_client.table().update.call_args
    assert "vector" in update_call_args[0][0]
    assert update_call_args[0][0]["vector"] == json.dumps(test_vector)

@pytest.mark.asyncio
async def test_update_without_text_change(mock_embedding_service):
    # Create mock client
    mock_client = MagicMock()
    doc_id = generate_uuid()
    doc_dict = create_document_dict(id=doc_id)
    doc = Document(**doc_dict)
    
    # Create update data (no text_content change)
    new_name = "Updated document name"
    doc_update = DocumentUpdate(name=new_name)
    
    # Updated document dict
    updated_doc_dict = {**doc_dict, "name": new_name}
    
    # Setup the mock response
    mock_response = create_mock_response(updated_doc_dict)
    mock_client.table().update().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method
    result = await document_crud.update_with_vector(mock_client, db_obj=doc, obj_in=doc_update)
    
    # Check the result
    assert result is not None
    assert result.id == doc_id
    assert result.name == new_name
    assert result.text_content == doc.text_content
    
    # Verify mock calls - embedding should NOT be called
    mock_embedding_service.get_embedding.assert_not_called()
    mock_client.table.assert_called_once_with(document_crud.table_name)
    mock_client.table().update.assert_called_once()
    
    # Check that vector was NOT included in the update
    update_call_args = mock_client.table().update.call_args
    assert "vector" not in update_call_args[0][0]

@pytest.mark.asyncio
async def test_search_by_vector(mock_embedding_service):
    # Create mock client
    mock_client = MagicMock()
    query_text = "Search query"
    
    # Test vector (normally provided by embedding_service)
    test_vector = [0.1] * 1536
    mock_embedding_service.get_embedding.return_value = test_vector
    
    # Sample document results
    doc1_id = generate_uuid()
    doc2_id = generate_uuid()
    search_results = [
        {**create_document_dict(id=doc1_id), "similarity": 0.95},
        {**create_document_dict(id=doc2_id), "similarity": 0.85}
    ]
    
    # Setup the mock RPC response
    mock_response = create_mock_response(search_results)
    mock_client.rpc().execute.return_value = mock_response
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method
    results = await document_crud.search_by_vector(mock_client, query_text=query_text, limit=2)
    
    # Check the results
    assert results is not None
    assert len(results) == 2
    
    doc1, similarity1 = results[0]
    assert doc1.id == doc1_id
    assert similarity1 == 0.95
    
    doc2, similarity2 = results[1]
    assert doc2.id == doc2_id
    assert similarity2 == 0.85
    
    # Verify mock calls
    mock_embedding_service.get_embedding.assert_called_once_with(query_text)
    mock_client.rpc.assert_called_once_with(
        "match_documents",
        {
            "query_embedding": json.dumps(test_vector),
            "match_threshold": 0.5,
            "match_count": 2
        }
    )

@pytest.mark.asyncio
async def test_search_by_vector_rpc_error(mock_embedding_service):
    # Create mock client
    mock_client = MagicMock()
    query_text = "Search query"
    
    # Test vector
    test_vector = [0.1] * 1536
    mock_embedding_service.get_embedding.return_value = test_vector
    
    # Setup the mock RPC to raise an exception
    mock_client.rpc().execute.side_effect = Exception("RPC function not found")
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method - should not raise exception
    results = await document_crud.search_by_vector(mock_client, query_text=query_text)
    
    # Check the results - should be empty but no exception
    assert results is not None
    assert len(results) == 0
    
    # Verify mock calls
    mock_embedding_service.get_embedding.assert_called_once_with(query_text)
    mock_client.rpc.assert_called_once()

@pytest.mark.asyncio
async def test_get_by_agent():
    # Create mock client
    mock_client = MagicMock()
    agent_id = generate_uuid()
    doc_dicts = [
        create_document_dict(agent_id=agent_id),
        create_document_dict(agent_id=agent_id)
    ]
    
    # Setup the mock response
    mock_response = create_mock_response(doc_dicts)
    mock_client.table().select().eq().range().execute.return_value = mock_response
    
    # Create the CRUD object
    document_crud = CRUDDocument(Document)
    
    # Call the method
    results = await document_crud.get_by_agent(mock_client, agent_id=agent_id)
    
    # Check the results
    assert results is not None
    assert len(results) == 2
    assert all(doc.agent_id == agent_id for doc in results)
    
    # Verify mock calls
    mock_client.table.assert_called_once_with(document_crud.table_name)
    mock_client.table().select.assert_called_once_with("*")
    mock_client.table().select().eq.assert_called_once_with("agent_id", str(agent_id))