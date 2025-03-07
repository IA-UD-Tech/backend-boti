from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from pydantic import BaseModel
from uuid import UUID

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    sub: str
    roles: List[str] = []
    exp: Optional[datetime] = None

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

# JWT token functions
def create_access_token(
    subject: Union[str, Any], 
    roles: List[str] = [], 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Subject of the token (usually user ID)
        roles: List of role names for the user
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token as string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "roles": roles
    }
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        TokenData containing user ID and roles
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        token_data = TokenData(
            sub=payload["sub"],
            roles=payload.get("roles", []),
            exp=datetime.fromtimestamp(payload["exp"])
        )
        
        # Check if token is expired
        if token_data.exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return token_data
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )