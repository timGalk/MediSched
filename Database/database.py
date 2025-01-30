from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from config import MONGO_DB

# Initialize database connection
cluster = AsyncIOMotorClient(MONGO_DB)
db = cluster['UpdDatabase']

def set_user(user_id):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Sets up a new user with default fields.

    Parameters:
    user_id (str): The unique identifier for the user.

    Returns:
    dict: A dictionary containing the following default user fields:
        - _id: The provided user ID.
        - first_name: An empty string to store the user's first name.
        - last_name: An empty string to store the user's last name.
        - phone_number: Default value set to 0.
        - basket: An empty list to store items in the user's basket.
        - orders: An empty list to store the user's previous orders.
    """
    return dict(
        _id=user_id,
        first_name='',
        last_name='',
        phone_number=0,
    )


async def record_appointment(user_id, doctor_id, selected_date, db, slot_data):
    """The function was created by Nazarii"""
    """
    Records a new appointment for a user with a specified doctor and removes the booked time slot from the available slots in the database.

    Parameters:
    user_id: Identifier of the user booking the appointment.
    doctor_id: Identifier of the doctor with whom the appointment is being booked.
    selected_date: The date and time selected for the appointment.
    db: The database connection object.
    slot_data: A dictionary containing details of the slot being booked.

    Functionality:
    - Adds a new appointment record to the database with a confirmed status.
    - Deletes the specified slot from the list of available slots to prevent double-booking.

    Exceptions:
    Logs an error message if any exception occurs during the operation.
    """
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

async def fetch_available_slots(doctor_id):
    """The function was created by Nazarii"""
    """
    Fetches available appointment slots for a specific doctor from the database.

    Parameters:
    doctor_id (str or int): The unique identifier for the doctor whose availability is being queried.

    Returns:
    list: A list of available appointment slots as datetime objects for the specified doctor.
    """
    doctor_id_int = int(doctor_id)
    slots = []
    async for doctor in db.available_slots.find({'doctor_id': doctor_id_int}):
        slots.append(doctor['datetime'])  # Extract only datetime field
    return slots



async def services_name():
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Fetches and returns a list of service names from the database's services collection.

    This asynchronous function queries the services collection in the database
    and retrieves all documents, extracting the 'name' field from each document.
    If an exception occurs (e.g., issues with database connection), it handles
    the exception by printing an error message and returning an empty list.

    Returns:
        list: A list of service names if the operation is successful, or an
        empty list if an error occurs.
    """
    try:
        # Collect service names from the services collection
        return [service['name'] async for service in db.services.find()]
    except Exception as e:
        # Handle exceptions (e.g., database connection errors)
        print(f"An error occurred: {e}")
        return []

async def services_id():
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Asynchronously retrieves a list of all service IDs from the database.

    This function iterates through all documents in the 'services' collection of the database,
    fetching the '_id' field for each document and appending it to a list.

    Returns:
        list: A list containing the IDs of all services in the 'services' collection.
    """
    service_ids = []
    async for service in db.services.find():
        service_ids.append(service['_id'])
    return service_ids


async def fetch_doctors_for_service(service_id):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Fetches the list of doctors associated with a specific service ID asynchronously.

    This function queries the database to retrieve all doctors who match the given service ID. If an error occurs during the database query, it handles the exception and returns an empty list.

    Parameters:
    - service_id: The ID of the service whose associated doctors are to be fetched.

    Returns:
    - A list of doctors matching the given service ID. Returns an empty list if an error occurs.
    """
    try:
        doctors = await db.doctors.find({"spec_id": service_id}).to_list(None)
        return doctors
    except Exception as e:
        print(f"Error fetching doctors for service: {e}")
        return []

async def fetch_services(db):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Asynchronously fetches all services from the database.

    Parameters:
    db: The database connection object, expected to have a `services` collection.

    Returns:
    A list of services retrieved from the database.
    If an error occurs during the database operation, an empty list is returned.

    Notes:
    Logs an error message to the console in case of an exception.
    """
    try:
        services = await db.services.find({}).to_list(None)
        return services
    except Exception as e:
        print(f"Error fetching services: {e}")
        return []


async def fetch_doctor_details(db, doctor_id):
    """The function was created by Nazarii"""
    """
    Fetches details of a doctor from the database based on the provided doctor ID.

    Parameters:
    db: A database connection object used to perform the query.
    doctor_id: The ID of the doctor whose details need to be fetched.

    Returns:
    A dictionary containing the doctor's details if found, otherwise None.

    Raises:
    Logs an exception message to the console and returns None in case of an error while querying the database.
    """
    try:
        doctor = await db.doctors.find_one({"_id": int(doctor_id)})
        return doctor
    except Exception as e:
        print(f"Error fetching doctor details: {e}")
        return None

async def fetch_user_details(db, user_id):
    """The function was created by Nazarii"""
    """
    Fetches user details from the database for a given user ID.

    Parameters:
    db: The database connection object.
    user_id: The ID of the user to fetch details for.

    Returns:
    A tuple containing the first name and last name of the user if found and valid, else None.

    Handles:
    Prints appropriate error messages if the user is not found, if the user details are incomplete, or if any exceptions occur during the fetch operation.
    """
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
    """The function was created by Tsimur"""
    """
    Finds a doctor document in the database based on the provided doctor ID.

    Parameters:
    doctor_id (int): The unique identifier of the doctor to find.

    Returns:
    dict or None: The doctor document if found, otherwise None.
    """
    return await db.doctors.find_one({"_id": int(doctor_id)})