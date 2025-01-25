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
    """Add a service to the user's basket."""
    # Validate user_id and service_id
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID.")
    if not ObjectId.is_valid(service_id):
        raise ValueError("Invalid service ID.")

    # Fetch user and ensure they exist
    user = await db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        raise ValueError(f"User with ID {user_id} not found.")

    basket = user.get('basket', [])
    # Check if the service is already in the basket
    if any(d.get('_id') == f'basket_{service_id}' for d in basket):
        return 0  # Service already in the basket

    # Fetch doctor and service details
    doctor = await db.doctors.find_one({'_id': ObjectId(service_id)})
    service = await db.services.find_one({'_id': f'callback_{service_id}'})

    if not doctor or not service:
        raise ValueError(f"Doctor or service with ID {service_id} not found.")

    # Add to basket
    await db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'basket': dict(
            _id=f'basket_{service_id}',
            name=service['name'],
            price=doctor['price']
        )}}
    )
    return 1  # Successfully added


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


async def trash_can(user_id, item_id):
    """Remove an item from the user's basket."""
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID.")

    await db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$pull': {'basket': {'_id': item_id}}}
    )
