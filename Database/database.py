from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from config import MONGO_DB

# Initialize database connection
cluster = AsyncIOMotorClient(MONGO_DB)
db = cluster['UpdDatabase']

def set_user(user_id):
    return dict(
        _id=user_id,
        first_name='',
        last_name='',
        phone_number=0,
        basket=[],
        orders = []
    )

def set_order(user_id, service_id, doctor_id, date, time):
    return dict(
        _id=user_id,
        service_id=service_id,
        doctor_id=doctor_id,
        date=date,
        time=time,

    )


async def record_appointment(user_id, doctor_id, selected_date, db, slot_data):
    """Record an appointment in the database."""
    try:


        # Add the new appointment
        await db["records"].insert_one({
            "user_id": user_id,
            "doctor_id": doctor_id,
            "dateAndTime": selected_date,
            "status": "confirmed",
        })
        print("Appointment successfully added to the database.")

        # Remove the booked slot from available slots
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
    """Fetch all service names."""
    try:
        # Using list() to directly collect the names from the async iterator
        return [service['name'] async for service in db.services.find()]
    except Exception as e:
        # Handle exceptions (e.g., database connection errors)
        print(f"An error occurred: {e}")
        return []



async def services_id():
    """Fetch all service IDs."""
    service_ids = []
    async for service in db.services.find():
        service_ids.append(service['_id'])
    return service_ids


async def fetch_doctors_for_service(service_id):
    """Fetches doctors associated with a specific service."""
    try:
        doctors = await db.doctors.find({"spec_id": service_id}).to_list(None)
        return doctors
    except Exception as e:
        print(f"Error fetching doctors for service: {e}")
        return []

async def fetch_services(db):
    """Fetches available services."""
    try:
        services = await db.services.find({}).to_list(None)
        return services
    except Exception as e:
        print(f"Error fetching services: {e}")
        return []


async def fetch_doctor_details(db, doctor_id):
    """Fetches details for a specific doctor."""
    try:
        doctor = await db.doctors.find_one({"_id": int(doctor_id)})
        return doctor
    except Exception as e:
        print(f"Error fetching doctor details: {e}")
        return None

async def fetch_user_details(db, user_id):
    """Fetches details for a specific doctor."""
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


async def basket_append(user_id, service_id):
    """
    Appends a service to a user's basket.

    Args:
        user_id (str): The ID of the user.
        service_id (str): The ID of the service to append.

    Returns:
        int: 1 if the service was successfully added, 0 if it was already in the basket.
    """
    # Retrieve the user document from the database
    user = await db.users.find_one({'_id': user_id})

    # Get the user's basket
    basket = user['basket']

    # Check if the service is already in the basket
    flag = any(d.get('_id') == f'basket_{service_id}' for d in basket)

    if not flag:
        # If the service is not in the basket, retrieve the doctor and service documents
        doctor = await db.doctors.find_one({'_id': service_id})
        service = await db.services.find_one({'_id': f'callback_{service_id}'})

        # Add the service to the user's basket
        await db.users.update_one({'_id': user_id}, {'$push': {'basket': dict(
            _id=f'basket_{service_id}',
            name=service['name'],
            price=doctor['price']
        )}})

        # Return 1 to indicate success
        return 1
    else:
        # If the service is already in the basket, return 0
        return 0

    # Add to basket

async def basket(user_id):
    """Retrieve the user's basket details."""
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID.")

    user = await db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    basket = user.get('basket', [])
    items = [d['name'] for d in basket if 'name' in d]
    callbacks = [d['_id'] for d in basket if '_id' in d]
    cost = sum([d['price'] for d in basket if 'price' in d])

    return {
        "items": items,
        "callbacks": callbacks,
        "total_cost": cost
    }


async def basket(user_id):
    user = await db.users.find_one({'_id': user_id})
    basket = user['basket']
    items = [d['name'] for d in basket if 'name' in d]
    callbacks = [d['_id'] for d in basket if '_id' in d]
    cost = sum([d['price'] for d in basket if 'price' in d])

    return items, callbacks, cost


async def trash_can(user_id, item_id):
    await db.users.update_one(
        {'_id': user_id},
        {'$pull': {'basket': {'_id': item_id}}}
    )


#Tsimurs
async def find_doc(doctor_id):
    return await db.doctors.find_one({"_id": int(doctor_id)})

#loop = cluster.get_io_loop()
#loop.run_until_complete(fetch_doctor_details(2))