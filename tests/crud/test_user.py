import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.crud.user import CRUDUser
from app.models.user import User, UserCreate, UserUpdate

from tests.factories import create_user_dict, create_user_create
from tests.utils import create_mock_response, dict_to_model_dict

@pytest.mark.asyncio
async def test_get_user():
    # Create mock client
    mock_client = MagicMock()
    user_id = uuid.uuid4()
    user_dict = create_user_dict(id=user_id)
    
    # Setup the mock response
    mock_response = create_mock_response(user_dict)
    mock_client.table().select().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.get(mock_client, id=user_id)
    
    # Check the result
    assert result is not None
    assert result.id == user_id
    assert result.email == user_dict["email"]
    assert result.name == user_dict["name"]
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().select.assert_called_once_with("*")
    mock_client.table().select().eq.assert_called_once_with("id", str(user_id))
    mock_client.table().select().eq().execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_not_found():
    # Create mock client
    mock_client = MagicMock()
    user_id = uuid.uuid4()
    
    # Setup the mock response with no data
    mock_response = create_mock_response([])
    mock_client.table().select().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.get(mock_client, id=user_id)
    
    # Check the result
    assert result is None

@pytest.mark.asyncio
async def test_get_by_email():
    # Create mock client
    mock_client = MagicMock()
    email = "test@example.com"
    user_dict = create_user_dict(email=email)
    
    # Setup the mock response
    mock_response = create_mock_response(user_dict)
    mock_client.table().select().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.get_by_email(mock_client, email=email)
    
    # Check the result
    assert result is not None
    assert result.email == email
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().select.assert_called_once_with("*")
    mock_client.table().select().eq.assert_called_once_with("email", email)
    mock_client.table().select().eq().execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_user():
    # Create mock client
    mock_client = MagicMock()
    user_create = create_user_create()
    user_dict = create_user_dict(email=user_create.email, name=user_create.name)
    
    # Setup the mock response
    mock_response = create_mock_response(user_dict)
    mock_client.table().insert().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.create(mock_client, obj_in=user_create)
    
    # Check the result
    assert result is not None
    assert result.email == user_create.email
    assert result.name == user_create.name
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().insert.assert_called_once()
    mock_client.table().insert().execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_user():
    # Create mock client
    mock_client = MagicMock()
    user_id = uuid.uuid4()
    user_dict = create_user_dict(id=user_id)
    user = User(**user_dict)
    
    # Create update data
    new_name = "Updated Name"
    user_update = UserUpdate(name=new_name)
    
    # Updated user dict
    updated_user_dict = dict_to_model_dict(user_dict)
    updated_user_dict["name"] = new_name
    
    # Setup the mock response
    mock_response = create_mock_response(updated_user_dict)
    mock_client.table().update().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.update(mock_client, db_obj=user, obj_in=user_update)
    
    # Check the result
    assert result is not None
    assert result.id == user_id
    assert result.name == new_name
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().update.assert_called_once()
    mock_client.table().update().eq.assert_called_once_with("id", str(user_id))
    mock_client.table().update().eq().execute.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user():
    # Create mock client
    mock_client = MagicMock()
    user_id = uuid.uuid4()
    user_dict = create_user_dict(id=user_id)
    
    # Setup the mock response
    mock_response = create_mock_response(user_dict)
    mock_client.table().delete().eq().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.remove(mock_client, id=user_id)
    
    # Check the result
    assert result is not None
    assert result.id == user_id
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().delete.assert_called_once()
    mock_client.table().delete().eq.assert_called_once_with("id", str(user_id))
    mock_client.table().delete().eq().execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_multi_users():
    # Create mock client
    mock_client = MagicMock()
    user_dicts = [create_user_dict(), create_user_dict()]
    
    # Setup the mock response
    mock_response = create_mock_response(user_dicts)
    mock_client.table().select().range().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.get_multi(mock_client, skip=0, limit=10)
    
    # Check the result
    assert result is not None
    assert len(result) == 2
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().select.assert_called_once_with("*")
    mock_client.table().select().range.assert_called_once_with(0, 9)
    mock_client.table().select().range().execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_multi_with_filter():
    # Create mock client
    mock_client = MagicMock()
    status = True
    user_dicts = [create_user_dict(status=status), create_user_dict(status=status)]
    
    # Setup the mock response
    mock_response = create_mock_response(user_dicts)
    mock_client.table().select().eq().range().execute.return_value = mock_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.get_multi_with_filter(mock_client, skip=0, limit=10, status=status)
    
    # Check the result
    assert result is not None
    assert len(result) == 2
    assert all(u.status is status for u in result)
    
    # Verify the mock was called correctly
    mock_client.table.assert_called_once_with(user_crud.table_name)
    mock_client.table().select.assert_called_once_with("*")
    mock_client.table().select().eq.assert_called_once_with("status", status)
    mock_client.table().select().eq().range.assert_called_once_with(0, 9)
    mock_client.table().select().eq().range().execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_last_login():
    # Create mock client
    mock_client = MagicMock()
    user_id = uuid.uuid4()
    user_dict = create_user_dict(id=user_id)
    
    # Setup the mock responses
    get_response = create_mock_response(user_dict)
    update_response = create_mock_response({**user_dict, "last_login": datetime.now().isoformat()})
    
    # Configure the mock to return the appropriate responses
    mock_client.table().select().eq().execute.return_value = get_response
    mock_client.table().update().eq().execute.return_value = update_response
    
    # Create the CRUD object
    user_crud = CRUDUser(User)
    
    # Call the method
    result = await user_crud.update_last_login(mock_client, user_id=user_id)
    
    # Check the result
    assert result is not None
    assert result.id == user_id
    assert result.last_login is not None
    
    # Verify the mocks were called correctly
    assert mock_client.table.call_count == 2
    assert mock_client.table().select.call_count == 1
    assert mock_client.table().update.call_count == 1
    assert mock_client.table().select().eq.call_count == 1
    assert mock_client.table().update().eq.call_count == 1
    assert mock_client.table().select().eq().execute.call_count == 1
    assert mock_client.table().update().eq().execute.call_count == 1