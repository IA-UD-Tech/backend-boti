import os
import json
import httpx
from typing import List, Dict, Any, cast
from app.core.config import settings
from app.models.vector_types import Embedding

class EmbeddingService:
    """Service for generating text embeddings using OpenAI's API."""
    
    api_key: str
    model: str = "text-embedding-ada-002"
    
    def __init__(self, api_key: str = None):
        """Initialize the embedding service with an API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
    
    async def get_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text.
        
        Args:
            text: The text to embed
            
        Returns:
            A list of floats representing the embedding vector
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": text
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Error getting embedding: {response.text}")
            
            result = response.json()
            embedding = result["data"][0]["embedding"]
            
            # Ensure we return the correct type with proper length
            # OpenAI's ada-002 embeddings are 1536-dimensional
            vector = cast(List[float], embedding)
            return vector
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.get_embedding(text)
            embeddings.append(embedding)
        return embeddings

embedding_service = EmbeddingService()