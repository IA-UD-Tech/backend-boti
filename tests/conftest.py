import os
import pytest
import json
from typing import AsyncGenerator, Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from supabase import Client

from app.main import app
from app.api.dependencies.dependencies import get_client
from app.services.embedding_service import EmbeddingService


# Mock Supabase client fixture
@pytest.fixture
def mock_supabase_client():
    """
    Create a mock Supabase client for testing.
    """
    mock_client = MagicMock(spec=Client)
    
    # Mock the table() method and its chain of methods
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_insert = MagicMock()
    mock_update = MagicMock()
    mock_delete = MagicMock()
    mock_eq = MagicMock()
    mock_range = MagicMock()
    mock_limit = MagicMock()
    mock_order = MagicMock()
    mock_execute = MagicMock()
    
    # Setup the chain
    mock_table.select.return_value = mock_select
    mock_table.insert.return_value = mock_insert
    mock_table.update.return_value = mock_update
    mock_table.delete.return_value = mock_delete
    
    mock_select.eq.return_value = mock_eq
    mock_select.range.return_value = mock_range
    mock_select.execute.return_value = mock_execute
    
    mock_insert.execute.return_value = mock_execute
    mock_update.eq.return_value = mock_eq
    mock_delete.eq.return_value = mock_eq
    
    mock_eq.eq.return_value = mock_eq
    mock_eq.range.return_value = mock_range
    mock_eq.execute.return_value = mock_execute
    mock_eq.order.return_value = mock_order
    
    mock_range.execute.return_value = mock_execute
    mock_order.execute.return_value = mock_execute
    mock_limit.execute.return_value = mock_execute
    
    # Setup the rpc method
    mock_rpc = MagicMock()
    mock_rpc.execute.return_value = mock_execute
    mock_client.rpc.return_value = mock_rpc
    
    # Set default return value for table method
    mock_client.table.return_value = mock_table
    
    return mock_client


# Override the get_client dependency
@pytest.fixture
def client(mock_supabase_client):
    """
    Create a FastAPI test client with mocked dependencies.
    """
    # Override the get_client dependency
    async def override_get_client():
        return mock_supabase_client
    
    app.dependency_overrides[get_client] = override_get_client
    
    # Create the test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the dependency overrides after the test
    app.dependency_overrides.clear()


# Mock embedding service
@pytest.fixture
def mock_embedding_service():
    """
    Create a mock embedding service that returns fixed vector embeddings.
    """
    with patch('app.services.embedding_service.embedding_service') as mock:
        # Create a fixed embedding vector of appropriate length
        fixed_embedding = [0.1] * 1536  # OpenAI ada-002 embeddings are 1536-dimensional
        
        # Mock get_embedding method
        mock.get_embedding = AsyncMock(return_value=fixed_embedding)
        
        # Mock get_embeddings method
        mock.get_embeddings = AsyncMock(return_value=[fixed_embedding])
        
        yield mock