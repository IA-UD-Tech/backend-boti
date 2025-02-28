import pytest
import uuid
import json
from typing import Dict, Any
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.models.user import User, UserCreate, UserUpdate
from tests.factories import create_user_dict, create_user_create
from tests.utils import create_mock_response, dict_to_model_dict, generate_uuid

def test_create_user(client, mock_supabase_client):
    # Setup test data
    user_create = create_user_create()
    user_create_dict = user_create.model_dump()
    
    # Configure the mock to handle get_by_email (no existing user)
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response([])
    
    # Configure the mock to return a created user
    user_id = generate_uuid()
    created_user = {
        **user_create_dict,
        "id": user_id,
        "created_at": "2025-01-01T00:00:00",
        "last_login": None
    }
    mock_supabase_client.table().insert().execute.return_value = create_mock_response(created_user)
    
    # Make the request
    response = client.post(
        "/api/v1/users/",
        json=user_create_dict
    )
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["email"] == user_create.email
    assert data["name"] == user_create.name
    assert data["status"] is True

def test_create_user_duplicate_email(client, mock_supabase_client):
    # Setup test data
    user_create = create_user_create()
    existing_user = create_user_dict(email=user_create.email)
    
    # Configure the mock to return an existing user
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response(existing_user)
    
    # Make the request
    response = client.post(
        "/api/v1/users/",
        json=user_create.model_dump()
    )
    
    # Check the response
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already exists" in data["detail"]

def test_read_users(client, mock_supabase_client):
    # Setup test data
    users = [create_user_dict(), create_user_dict()]
    
    # Configure the mock
    mock_supabase_client.table().select().range().execute.return_value = create_mock_response(users)
    
    # Make the request
    response = client.get("/api/v1/users/")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert "id" in data[0]
    assert "name" in data[0]
    assert "email" in data[0]

def test_read_user_by_id(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    user = create_user_dict(id=user_id)
    
    # Configure the mock
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response(user)
    
    # Make the request
    response = client.get(f"/api/v1/users/{user_id}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["name"] == user["name"]
    assert data["email"] == user["email"]

def test_read_user_not_found(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    
    # Configure the mock to return no data
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response([])
    
    # Make the request
    response = client.get(f"/api/v1/users/{user_id}")
    
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_update_user(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    user = create_user_dict(id=user_id)
    
    # Update data
    update_data = {"name": "Updated Name"}
    
    # Configure the mock for the get request
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response(user)
    
    # Configure the mock for the update request
    updated_user = {**user, "name": update_data["name"]}
    mock_supabase_client.table().update().eq().execute.return_value = create_mock_response(updated_user)
    
    # Make the request
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["name"] == update_data["name"]
    assert data["email"] == user["email"]

def test_update_user_not_found(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    
    # Update data
    update_data = {"name": "Updated Name"}
    
    # Configure the mock to return no data
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response([])
    
    # Make the request
    response = client.put(f"/api/v1/users/{user_id}", json=update_data)
    
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]

def test_delete_user(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    user = create_user_dict(id=user_id)
    
    # Configure the mock
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response(user)
    mock_supabase_client.table().delete().eq().execute.return_value = create_mock_response(user)
    
    # Make the request
    response = client.delete(f"/api/v1/users/{user_id}")
    
    # Check the response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user_id)
    assert data["name"] == user["name"]
    assert data["email"] == user["email"]

def test_delete_user_not_found(client, mock_supabase_client):
    # Setup test data
    user_id = generate_uuid()
    
    # Configure the mock to return no data
    mock_supabase_client.table().select().eq().execute.return_value = create_mock_response([])
    
    # Make the request
    response = client.delete(f"/api/v1/users/{user_id}")
    
    # Check the response
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"]