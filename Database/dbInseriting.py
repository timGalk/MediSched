from datetime import datetime

from Database.database import cluster, db


async def create_doctors():
    """The function was created by Tsimur"""
    """
    Inserts a predefined list of doctor records into the 'doctors' collection and an initial record in the 'records' collection within the database.

    This asynchronous function performs the following actions:
    - Populates the 'doctors' collection with a predefined list of doctor objects, each containing attributes like:
      - _id: Unique identifier for the doctor
      - name: Full name of the doctor
      - spec_id: ID specifying the specialization
      - description: A brief overview of the doctor's expertise and certifications
      - price: Fee charged for the doctor's consultation
    - Adds a sample record into the 'records' collection. This record contains fields such as:
      - user_id: ID of the user associated with this record
      - doctor_id: ID of the doctor associated with this record
      - dateAndTime: Placeholder value for the appointment's date and time
      - status: Current status of the record (e.g., "confirmed")

    Prints the number of documents inserted into the 'records' collection. If there are errors during insertion, no documents will be printed.
    """
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

    result2 = await db["records"].insert_one({
        "user_id": 1,
        "doctor_id": 2,
        "dateAndTime": 3,
        "status": "confirmed",
    })

    # Print the number of documents inserted
    print("inserted %d docs" % (len(result2.inserted_ids)))


async def services_info_do_insert():
    """The function was created by Tsimur"""
    """
    Inserts a predefined list of service information into the 'services' collection in the database.

    This asynchronous function creates a list of dictionaries, where each dictionary represents a service's information, including an ID and name. The documents are then inserted into the database using the 'insert_many' method.

    The function logs the number of documents successfully inserted.
    """
    # Inserts a list of service information into the 'services' collection in the database.
    # This function uses the 'insert_many' method to insert multiple documents at once.
    # The documents are created as a list of dictionaries, where each dictionary represents a service's information.
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
    """The function was created by Tsimur"""
    """
    Adds available slots to the 'available_slots' collection in the database.

    This function inserts a batch of available slot records into the 'available_slots' collection using the asynchronous 'insert_many' method. Each record is represented as a dictionary and constructed from the provided 'slots_data' list. The 'slots_data' consists of tuples containing specification ID, doctor ID, date, and time information. 

    The function formats the date and time into a single datetime object for each slot and stores these records in the database. It also outputs the number of successfully inserted slot records to the console.
    """

    slots_data = [
        (0, 0, '2024-01-01', '10:00'),
        (1, 2, '2024-01-01', '10:00'),
    ]

    available_slots = [
        {
            'spec_id': spec_id,
            'doctor_id': doctor_id,
            'datetime': datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        }
        for spec_id, doctor_id, date, time in slots_data
    ]

    result = await db.available_slots.insert_many(available_slots)
    print(f"Inserted {len(result.inserted_ids)} available slots.")


loop = cluster.get_io_loop()
loop.run_until_complete(add_available_slots())