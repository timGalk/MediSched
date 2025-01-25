from motor.motor_asyncio import AsyncIOMotorClient

from Source.database import cluster, db


async def doctors_info_do_insert():
    """
    Inserts a list of doctor information into the 'doctors' collection in the database.

    This function uses the 'insert_many' method to insert multiple documents at once.
    The documents are created as a list of dictionaries, where each dictionary represents a doctor's information.
    """
    # Define the list of doctor information
    doctors = [
        {'_id': '0', 'd_name': 'Dr. John Smith',
         'description': '20 years of experience, certified by the American Board of Cardiology', 'price': 120},
        {'_id': '1', 'd_name': 'Dr. Emily Davis',
         'description': '15 years of experience, specializes in child care and developmental disorders', 'price': 100},
        {'_id': '2', 'd_name': 'Dr. Michael Brown',
         'description': '18 years of experience, expert in neurodegenerative diseases', 'price': 150},
        {'_id': '3', 'd_name': 'Dr. Sarah Wilson',
         'description': '10 years of experience, focuses on skin disorders and cosmetic dermatology', 'price': 90},
        {'_id': '4', 'd_name': 'Dr. James Miller',
         'description': '12 years of experience, specializes in sports injuries and joint replacement', 'price': 130},
        {'_id': '5', 'd_name': 'Dr. Laura Taylor',
         'description': '20 years of experience, provides therapy for mental health and substance abuse issues',
         'price': 110},
        {'_id': '6', 'd_name': 'Dr. David Anderson',
         'description': '25 years of experience, expert in cataract surgery and vision correction', 'price': 140},
        {'_id': '7', 'd_name': 'Dr. Olivia Martin',
         'description': '16 years of experience, focuses on diabetes and hormonal disorders', 'price': 115},
        {'_id': '8', 'd_name': 'Dr. William Thompson',
         'description': '15 years of experience, certified by the American Board of Surgery', 'price': 135},
        {'_id': '9', 'd_name': 'Dr. Sophia Moore',
         'description': '20 years of experience, specializes in women’s reproductive health', 'price': 125},
        {'_id': '10', 'd_name': 'Dr. Daniel Garcia',
         'description': '14 years of experience, focuses on respiratory disorders and critical care', 'price': 130}
    ]

    # Insert the list of doctors into the database
    result = await db.doctors.insert_many(doctors)

    # Print the number of documents inserted
    print("inserted %d docs" % (len(result.inserted_ids),))


async def services_info_do_insert():
    """
    Inserts a list of service information into the 'services' collection in the database.

    This function uses the 'insert_many' method to insert multiple documents at once.
    The documents are created as a list of dictionaries, where each dictionary represents a service's information.
    """
    # Define the list of service information
    result = await db.services.insert_many([
        {'_id': 'callback_0', 'name': 'ENT Specialist'},
        {'_id': 'callback_1', 'name': 'Psychiatrist'},
        {'_id': 'callback_2', 'name': 'Proctologist'},
        {'_id': 'callback_3', 'name': 'Gynecologist'},
        {'_id': 'callback_4', 'name': 'Allergist'},
        {'_id': 'callback_5', 'name': 'Ophthalmologist'},
        {'_id': 'callback_6', 'name': 'Traumatologist'},
        {'_id': 'callback_7', 'name': 'Orthopedist'},
        {'_id': 'callback_8', 'name': 'Surgeon'},
        {'_id': 'callback_9', 'name': 'Therapist'},
        {'_id': 'callback_10', 'name': 'Blood Analysis'}
    ])

    # Print the number of documents inserted
    print("inserted %d docs" % (len(result.inserted_ids),))


loop = cluster.get_io_loop()
loop.run_until_complete(services_info_do_insert())