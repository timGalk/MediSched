import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
import pytest



from Database.database import cluster
from Database.database import db
from Database.database import (
    set_user,
    record_appointment,
    fetch_available_slots,
    services_name,
    services_id,
    fetch_doctors_for_service,
    fetch_services,
    fetch_user_details,
    find_doc,
    fetch_doctor_details
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
async def test_set_user(mock_db):
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
    assert services == [
            'ENT Specialist', 'Psychiatrist', 'Proctologist', 'Gynecologist',
            'Allergist', 'Ophthalmologist', 'Traumatologist', 'Orthopedist',
            'Surgeon', 'Therapist',
        ]
    with pytest.raises(AssertionError):
        assert  len(services) == 8

@pytest.mark.asyncio
async def test_services_id(mock_db):
    """Test fetching service IDs."""
    services = await services_id()
    assert isinstance(services, list)
    assert len(services) == 10
    assert services == [i for i in range(10)]
    with pytest.raises(AssertionError):
        assert  len(services) == 8
        assert len(services) == 7

@pytest.mark.asyncio
async def test_find_doc(mock_db):
    """Test finding a doctor by ID."""
    doc_id = 1
    doc = await find_doc(doc_id)
    assert isinstance(doc, dict)
    assert doc["_id"] == doc_id
    assert doc["name"] == "Dr. Emily Davis"
    assert doc["price"] == 100
    assert doc["description"] == "15 years of experience, specializes in child care and developmental disorders"

@pytest.mark.asyncio
async def test_available_slots(mock_db):
    """Test fetching available slots for a doctor."""
    doctor_id = 7
    slots = await fetch_available_slots(doctor_id)
    assert isinstance(slots, list)
    assert len(slots) == 1
    assert slots[0] == datetime(2024, 1, 19, 16, 0)

@pytest.mark.asyncio
async def test_fetch_doctors_for_service(mock_db):
    """Test fetching doctors for a specific service."""
    service_id = 2
    doctors = await fetch_doctors_for_service(service_id)
    assert isinstance(doctors, list)
    assert len(doctors) == 3
    assert doctors[0]["name"] == "Dr. Michael Brown"
    assert doctors[1]["name"] == "Dr. Charles Garcia"
    assert doctors[2]["name"] == "Dr. Richard Davis"

@pytest.mark.asyncio
async def test_fetch_services(mock_db):
    """Test fetching available services."""
    services = await fetch_services(db)
    assert isinstance(services, list)
    assert len(services) == 10

@pytest.mark.asyncio
async def test_fetch_doctor_details(mock_db):
    """Test fetching details of a doctor."""
    doctor_id = 1
    doctor = await fetch_doctor_details(db, doctor_id)
    assert isinstance(doctor, dict)
    assert doctor["_id"] == 1
    assert doctor["name"] == "Dr. Emily Davis"


@pytest.mark.asyncio
async def test_record_appointment(mock_db):
    """Test booking an appointment for a user."""
    user_id = 2
    doctor_id = 18
    selected_date = datetime(2024, 1, 9, 12, 0)
    status = "confirmed"
    await record_appointment(user_id, doctor_id, selected_date, db, status)
    orders = await db.records.find({'user_id': user_id}).to_list(length=None)
    assert orders [0]["status"] == "confirmed"
    assert orders [0]["dateAndTime"] == datetime(2024, 1, 9, 12, 0)
    assert orders [0]["doctor_id"] == 18
    assert orders [0]["user_id"] == 2

