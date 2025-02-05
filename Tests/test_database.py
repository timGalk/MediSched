from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
import pytest
from bson.objectid import ObjectId

# initialize test database
from Database.database import cluster
from Database.database import (
    set_user,
    record_appointment,
    fetch_available_slots,
    services_name,
    services_id,
    fetch_doctors_for_service,
    fetch_services,
    fetch_doctor_details,
    fetch_user_details,
    find_doc
)

@pytest.fixture
def mock_db():
    """Creates a mock database object."""
    db = AsyncMock()

    # Mock user-related methods
    db.users.find_one = AsyncMock()

    # Mock appointment booking methods
    db.records.insert_one = AsyncMock()
    db.available_slots.delete_one = AsyncMock()

    # Mock service-related methods
    db.services.find = AsyncMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[])))
    db.services.find_one = AsyncMock()

    # Mock doctor-related methods
    db.doctors.find = AsyncMock(return_value=AsyncMock(to_list=AsyncMock(return_value=[])))
    db.doctors.find_one = AsyncMock()

    return db

@pytest.mark.asyncio
async def test_set_user():
    """Test setting a new user with default values."""
    user_id = "12345"
    expected_user = {
        "_id": user_id,
        "first_name": "",
        "last_name": "",
        "phone_number": 0,
    }
    assert set_user(user_id) == expected_user

@pytest.mark.asyncio
async def test_fetch_available_slots(mock_db):
    """Test fetching available slots for a doctor."""
    doctor_id = 1
    slots = await fetch_available_slots(doctor_id)
    assert isinstance(slots, list)
    assert len(slots) == 1

@pytest.mark.asyncio
async def test_services_name(mock_db):
    """Test fetching service names."""
    services = await services_name()
    assert isinstance(services, list)
    assert len(services) == 10
    with pytest.raises(AssertionError):
        assert  len(services) == 8

@pytest.mark.asyncio
async def test_services_id(mock_db):
    """Test fetching service IDs."""
    services = await services_id()
    assert isinstance(services, list)
    assert len(services) == 10