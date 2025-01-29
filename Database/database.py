from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from config import MONGO_DB

# Initialize database connection
cluster = AsyncIOMotorClient(MONGO_DB)
db = cluster['UpdDatabase']

def set_user(user_id):
    """Creates a new user document with default values."""
    return dict(
        _id=user_id,
        first_name='',
        last_name='',
        phone_number=0,
        basket=[],
        orders = []
    )


async def record_appointment(user_id, doctor_id, selected_date, db, slot_data):
    """Record an appointment in the database and remove the booked slot from available slots."""
    try:
        # Add the new appointment and remove the booked slot
        await db["records"].insert_one({
            "user_id": user_id,
            "doctor_id": doctor_id,
            "dateAndTime": selected_date,
            "status": "confirmed",
        })
        print("Appointment successfully added to the database.")

        await db.available_slots.delete_one({"_id": ObjectId(slot_data["_id"])})
        print("Removed booked slot from available slots.")
    except Exception as e:
        print(f"Error recording appointment: {e}")

import logging

from datetime import datetime

async def fetch_available_slots(doctor_id):
    """Fetch available slots for a doctor and return only datetime values."""
    doctor_id_int = int(doctor_id)
    slots = []
    async for doctor in db.available_slots.find({'doctor_id': doctor_id_int}):
        slots.append(doctor['datetime'])  # Extract only datetime field
    return slots



async def services_name():
    """Fetches all service names from the database."""
    try:
        # Collect service names from the services collection
        return [service['name'] async for service in db.services.find()]
    except Exception as e:
        # Handle exceptions (e.g., database connection errors)
        print(f"An error occurred: {e}")
        return []



async def services_id():
    """Fetches all service IDs from the database."""
    service_ids = []
    async for service in db.services.find():
        service_ids.append(service['_id'])
    return service_ids


async def fetch_doctors_for_service(service_id):
    """Fetches all doctors associated with a specific service from the database."""
    try:
        doctors = await db.doctors.find({"spec_id": service_id}).to_list(None)
        return doctors
    except Exception as e:
        print(f"Error fetching doctors for service: {e}")
        return []

async def fetch_services(db):
    """Fetches all available services from the database."""
    try:
        services = await db.services.find({}).to_list(None)
        return services
    except Exception as e:
        print(f"Error fetching services: {e}")
        return []


async def fetch_doctor_details(db, doctor_id):
    """Fetches details for a specific doctor from the database."""
    try:
        doctor = await db.doctors.find_one({"_id": int(doctor_id)})
        return doctor
    except Exception as e:
        print(f"Error fetching doctor details: {e}")
        return None

async def fetch_user_details(db, user_id):
    """Fetches details for a specific user from the database, ensuring necessary fields exist."""
    try:
        user = await db.users.find_one({"_id": int(user_id)})
        if user is None:
            print(f"No user found with ID {user_id}")
            return None
        # Ensure that the necessary fields exist
        first_name = user.get('first_name')
        last_name = user.get('last_name')
        if first_name is None or last_name is None:
            print(f"User with ID {user_id} missing first or last name.")
            return None
        return first_name, last_name
    except Exception as e:
        print(f"Error fetching doctor details: {e}")
        return None

#Tsimurs
async def find_doc(doctor_id):
    """Finds a doctor by their ID in the database."""
    return await db.doctors.find_one({"_id": int(doctor_id)})

#loop = cluster.get_io_loop()
#loop.run_until_complete(fetch_doctor_details(2))
