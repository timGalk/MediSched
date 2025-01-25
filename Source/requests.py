async def set_user(user_id):
    return dict(
        _id = user_id,
        first_name = '',
        last_name = '',
        phone_number = 0,
        basket = []
    )
