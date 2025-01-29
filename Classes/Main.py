import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from Database.database import services_name, fetch_doctor_details, fetch_available_slots
from Database.database import fetch_doctors_for_service
#from Source.handlers import show_doctor
from config import MONGO_DB



import asyncio


# Assuming you have an async function that runs the tests
async def main():
    cluster = AsyncIOMotorClient(MONGO_DB)
    db = cluster['UpdDatabase']
    # db is your database connection object, make sure it's properly initialized.
    #db = await initialize_db()  # Your database initialization method

    # Call the async function to fetch doctors for a service with a sample service ID "1"
    #doctor = await show_doctor(1)
    doctor1 = fetch_doctors_for_service(1)
    print(doctor1)

    print(fetch_doctor_details(1))
    #record_appointment(1, 2, )
    # Print the results to see the fetched doctors
    #print(doctors)  # This will print the list of doctors related to service_id "1"


# Ensure to run the main async function in an event loop
if __name__ == '__main__':
    asyncio.run(main())
    # This runs the main function asynchronously

