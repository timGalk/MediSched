from datetime import datetime

from Database.database import cluster, db
from  Classes.Clinics import Doctor

async  def create_doctors():
    doctors_data = [
        {'_id': 0, 'name': 'Dr. John Smith', 'spec_id': 0,
         'description': '20 years of experience, certified by the American Board of Cardiology', 'price': 120},
        {'_id': 1, 'name': 'Dr. Emily Davis', 'spec_id': 1,
         'description': '15 years of experience, specializes in child care and developmental disorders', 'price': 100},
        {'_id': 2, 'name': 'Dr. Michael Brown', 'spec_id': 2,
         'description': '18 years of experience, expert in neurodegenerative diseases', 'price': 150},
        {'_id': 3, 'name': 'Dr. Sarah Wilson', 'spec_id': 3,
         'description': '10 years of experience, focuses on skin disorders and cosmetic dermatology', 'price': 90},
        {'_id': 4, 'name': 'Dr. James Miller', 'spec_id': 4,
         'description': '12 years of experience, specializes in sports injuries and joint replacement', 'price': 130},
        {'_id': 5, 'name': 'Dr. Laura Taylor', 'spec_id': 5,
         'description': '20 years of experience, provides therapy for mental health and substance abuse issues',
         'price': 110},
        {'_id': 6, 'name': 'Dr. David Anderson', 'spec_id': 6,
         'description': '25 years of experience, expert in cataract surgery and vision correction', 'price': 140},
        {'_id': 7, 'name': 'Dr. Olivia Martin', 'spec_id': 7,
         'description': '16 years of experience, focuses on diabetes and hormonal disorders', 'price': 115},
        {'_id': 8, 'name': 'Dr. William Thompson', 'spec_id': 8,
         'description': '15 years of experience, certified by the American Board of Surgery', 'price': 135},
        {'_id': 9, 'name': 'Dr. Sophia Moore', 'spec_id': 9,
         'description': '20 years of experience, specializes in women’s reproductive health', 'price': 125},
        {'_id': 10, 'name': 'Dr. Daniel Garcia', 'spec_id': 10,
         'description': '14 years of experience, focuses on respiratory disorders and critical care', 'price': 130}
    ]

    result = await db['doctors'].insert_many(doctors_data)

    # Print the number of documents inserted
    print("inserted %d docs" % (len(result.inserted_ids)))


async def services_info_do_insert():
    """
    Inserts a list of service information into the 'services' collection in the database.

    This function uses the 'insert_many' method to insert multiple documents at once.
    The documents are created as a list of dictionaries, where each dictionary represents a service's information.
    """
    # Define the list of service information
    services = [
        {'_id': i, 'name': name}
        for i, name in enumerate([
            'ENT Specialist', 'Psychiatrist', 'Proctologist', 'Gynecologist',
            'Allergist', 'Ophthalmologist', 'Traumatologist', 'Orthopedist',
            'Surgeon', 'Therapist', 'Blood Analysis'
        ])
    ]

    result = await db.services.insert_many(services)

    # Print the number of documents inserted
    print("inserted %d docs" % (len(result.inserted_ids),))


async def add_available_slots():
    """
    Adds available slots to the 'available_slots' collection in the database.

    This function uses the 'insert_many' method to insert multiple documents at once.
    The documents are created as a list of dictionaries, where each dictionary represents an available slot.
    """
    # Define the list of available slots as tuples of (spec_id, doctor_id, date, time)
    slots_data = [
        (0, 0, '2024-01-01', '10:00'),
        (1, 2, '2024-01-01', '10:00'),
    ]

    # Convert slots_data into a list of dictionaries with proper datetime objects
    available_slots = [
        {
            'spec_id': spec_id,
            'doctor_id': doctor_id,
            'datetime': datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        }
        for spec_id, doctor_id, date, time in slots_data
    ]

    # Insert the slots into the 'available_slots' collection
    result = await db.available_slots.insert_many(available_slots)
    print(f"Inserted {len(result.inserted_ids)} available slots.")


loop = cluster.get_io_loop()
loop.run_until_complete(add_available_slots())