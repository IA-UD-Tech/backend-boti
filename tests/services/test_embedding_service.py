import pytest
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.embedding_service import EmbeddingService


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx AsyncClient."""
    with patch('httpx.AsyncClient') as mock:
        # Setup the mock
        mock_client_instance = AsyncMock()
        mock.return_value = mock_client_instance
        
        # Setup response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {
                    "embedding": [0.1] * 1536,  # 1536-dimensional vector
                    "index": 0,
                    "object": "embedding"
                }
            ],
            "model": "text-embedding-ada-002",
            "object": "list",
            "usage": {
                "prompt_tokens": 5,
                "total_tokens": 5
            }
        }
        
        mock_client_instance.post.return_value = mock_response
        
        yield mock_client_instance


@pytest.mark.asyncio
async def test_embedding_service_init():
    """Test that the embedding service initializes correctly."""
    # Test with explicit API key
    service = EmbeddingService(api_key="test_key")
    assert service.api_key == "test_key"
    assert service.model == "text-embedding-ada-002"
    
    # Test with environment variable
    with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
        service = EmbeddingService()
        assert service.api_key == "env_key"
    
    # Test with no API key
    with patch.dict(os.environ, clear=True):
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = "settings_key"
            service = EmbeddingService()
            assert service.api_key == "settings_key"


@pytest.mark.asyncio
async def test_embedding_service_init_no_key():
    """Test that the embedding service raises an error when no API key is provided."""
    with patch.dict(os.environ, clear=True):
        with patch('app.core.config.settings') as mock_settings:
            mock_settings.OPENAI_API_KEY = ""
            with pytest.raises(ValueError):
                EmbeddingService()


@pytest.mark.asyncio
async def test_get_embedding(mock_httpx_client):
    """Test getting an embedding for a single text."""
    service = EmbeddingService(api_key="test_key")
    text = "This is a test"
    
    # Call the method
    embedding = await service.get_embedding(text)
    
    # Check the result
    assert embedding is not None
    assert len(embedding) == 1536
    assert all(isinstance(value, float) for value in embedding)
    
    # Verify the HTTP request
    mock_httpx_client.post.assert_called_once_with(
        "https://api.openai.com/v1/embeddings",
        headers={
            "Authorization": "Bearer test_key",
            "Content-Type": "application/json"
        },
        json={
            "model": "text-embedding-ada-002",
            "input": text
        },
        timeout=30.0
    )


@pytest.mark.asyncio
async def test_get_embedding_error(mock_httpx_client):
    """Test handling API errors when getting embeddings."""
    service = EmbeddingService(api_key="test_key")
    
    # Set up the mock to return an error
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_httpx_client.post.return_value = mock_response
    
    # Call the method and expect an exception
    with pytest.raises(Exception) as excinfo:
        await service.get_embedding("This is a test")
    
    # Check the exception message
    assert "Error getting embedding" in str(excinfo.value)


@pytest.mark.asyncio
async def test_get_embeddings(mock_httpx_client):
    """Test getting embeddings for multiple texts."""
    service = EmbeddingService(api_key="test_key")
    texts = ["First text", "Second text", "Third text"]
    
    # Call the method
    embeddings = await service.get_embeddings(texts)
    
    # Check the result
    assert embeddings is not None
    assert len(embeddings) == 3
    assert all(len(emb) == 1536 for emb in embeddings)
    
    # Verify the HTTP requests - one per text
    assert mock_httpx_client.post.call_count == 3