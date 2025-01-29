from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId
from config import MONGO_DB

# Initialize database connection
cluster = AsyncIOMotorClient(MONGO_DB)
db = cluster['MediSched']

def set_user(user_id):
    return dict(
        _id=user_id,
        first_name='',
        last_name='',
        phone_number=0,
        basket=[]
    )


async def services_name():
    """Fetch all service names."""
    names = []
    async for service in db.services.find():
        names.append(service['name'])
    return names


async def services_id():
    """Fetch all service IDs."""
    service_ids = []
    async for service in db.services.find():
        service_ids.append(service['_id'])
    return service_ids


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

async def find_doc(doctor_id):
    return await db.doctors.find_one({"_id": int(doctor_id)})