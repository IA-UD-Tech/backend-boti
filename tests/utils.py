import uuid
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, date
from unittest.mock import MagicMock

def generate_uuid() -> uuid.UUID:
    """Generate a random UUID."""
    return uuid.uuid4()

def create_mock_response(data: Union[Dict[str, Any], List[Dict[str, Any]]], count: Optional[int] = None) -> MagicMock:
    """
    Create a mock response object similar to what Supabase would return.
    
    Args:
        data: The data to include in the response
        count: Optional count for pagination responses
        
    Returns:
        A MagicMock with data and count attributes
    """
    mock_response = MagicMock()
    mock_response.data = data if isinstance(data, list) else [data]
    
    if count is not None:
        mock_response.count = count
    
    return mock_response

def serialize_dates(obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert datetime and date objects to strings for JSON serialization.
    
    Args:
        obj: Dictionary that may contain datetime objects
        
    Returns:
        Dictionary with datetime objects converted to strings
    """
    result = {}
    for key, value in obj.items():
        if isinstance(value, (datetime, date)):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_dates(value)
        elif isinstance(value, list):
            result[key] = [
                serialize_dates(item) if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, uuid.UUID):
            result[key] = str(value)
        else:
            result[key] = value
    return result

def dict_to_model_dict(model_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare a dictionary to be compared with a model's dictionary representation.
    
    Args:
        model_dict: Dictionary to prepare
        
    Returns:
        Dictionary suitable for comparison with a model
    """
    # Serialize any dates and UUIDs
    return serialize_dates(model_dict)