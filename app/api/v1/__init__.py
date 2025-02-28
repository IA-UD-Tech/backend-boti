from fastapi import APIRouter
from app.api.v1.endpoints import users, roles, tools, agents, conversations, permissions, documents, vector_embeddings

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(tools.router, prefix="/tools", tags=["tools"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(vector_embeddings.router, prefix="/vector-embeddings", tags=["vector-embeddings"])