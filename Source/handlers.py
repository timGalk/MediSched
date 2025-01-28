from gc import callbacks

from aiogram import F, Router, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from pymongo.errors import DuplicateKeyError

from Source.keyboards import inline_builder
from Source.database import services_name, services_id, basket_append, basket, trash_can, set_user


router = Router()

@router.message(CommandStart())
async def start(message: Message, db: MDB):
    """Handle the /start command."""
    with suppress(DuplicateKeyError):
        await db.users.insert_one(set_user(message.from_user.id))

    pattern = {
        'text': 'Welcome to our Medical center',
        'reply_markup': inline_builder(
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us', '👤 Profile'],
            ['services', 'basket', 'contact', 'about', 'profile']
        )
    }

    if isinstance(message, Message):
        await message.answer(**pattern)
    elif isinstance(message, CallbackQuery):
        await message.message.edit_text(**pattern)


@router.callback_query(F.data == 'main_page')
async def main_menu(callback_query: CallbackQuery, db: MDB):
    """Show the main menu."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Main page',
        reply_markup=inline_builder(
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us', '👤 Profile'],
            ['services', 'basket', 'contact', 'about', 'profile']
        )
    )


@router.callback_query(F.data == 'services')
@router.callback_query(F.data == 'to_services')
async def show_services(callback_query: CallbackQuery, db: MDB):
    """Display a list of available services."""
    service_names = await services_name()
    service_ids = await services_id()
    service_names.append('⬅️Back to main menu')
    service_ids.append('main_page')

    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Choose a service',
        reply_markup=inline_builder(service_names, service_ids)
    )


@router.callback_query(F.data.startswith('callback'))
async def show_doctors(callback_query: CallbackQuery, db: MDB):
    """Display doctor details based on the selected service."""
    doctor_id = callback_query.data.split('_')[1]
    doctor = await db.doctors.find_one({'_id': doctor_id})

    if not doctor:
        await callback_query.answer("Doctor not found.", show_alert=True)
        return

    await callback_query.answer()
    await callback_query.message.edit_text(
        text=(
            f"{doctor['d_name']}\n"
            f"{doctor['description']}\n"
            f"{doctor['price']}zlt per consultation\n"
        ),
        reply_markup=inline_builder(
            ['Add to cart 🛒', '⬅️Back'],
            [f'cart_{doctor_id}', 'to_services']
        )
    )


@router.callback_query(F.data.startswith('cart'))
async def add_to_cart(callback_query: CallbackQuery, db: MDB):
    """Add a service to the user's cart."""
    service_id = callback_query.data.split('_')[1]
    flag = await basket_append(callback_query.from_user.id, service_id)

    if flag == 0:
        await callback_query.answer('You have already added this service to the cart.')
    else:
        await callback_query.answer('Service added to the cart.')

    await callback_query.message.edit_text(
        text='Main menu',
        reply_markup=inline_builder(
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us'],
            ['services', 'basket', 'contact', 'about']
        )
    )


@router.callback_query(F.data == 'basket')
async def show_basket(callback_query: CallbackQuery, db: MDB):
    """Display the user's cart contents."""
    if F.data.startswith('basket'):
        await trash_can(callback_query.from_user.id, callback_query.data)
    items, item_ids, cost = await basket(callback_query.from_user.id)
    items.append('⬅️Back to main menu')
    item_ids.append('main_page')
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=f'Total cost: {cost}zlt \n\n '
             f'In order to remove service from basket click on it',
        reply_markup=inline_builder(items, item_ids, 1)
    )


@router.callback_query(F.data.startswith('basket_'))
async def remove_from_basket(callback_query: CallbackQuery, db: MDB):
    """Remove an item from the user's cart."""
    await trash_can(callback_query.from_user.id, callback_query.data)
    await show_basket(callback_query, db)


@router.callback_query(F.data == 'contact')
async def show_contact(callback_query: CallbackQuery, db: MDB):
    """Show contact information."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Contact us',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )


@router.callback_query(F.data == 'about')
async def show_about(callback_query: CallbackQuery, db: MDB):
    """Display information about the organization."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='About us\n',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )



class UpdateProfileState(StatesGroup):
    updating_first_name = State()
    updating_last_name = State()
    updating_phone_number = State()

@router.callback_query(F.data == 'profile')
async def show_profile_menu(callback_query: CallbackQuery, db: MDB):
    """Show the profile menu for users to input personal information."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text="Please choose what you'd like to update:",
        reply_markup=inline_builder(
            ["First Name", "Last Name", "Phone Number", "Profile Info", "⬅️ Back to Main Menu"],
            ["update_first_name", "update_last_name", "update_phone", "profile_info", "main_page"]
        )
    )

@router.callback_query(F.data.startswith("update_first_name"))
async def update_first_name(callback_query: CallbackQuery, state: FSMContext):
    """Prompt the user to enter their first name."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your first name:")
    await state.set_state(UpdateProfileState.updating_first_name)

@router.callback_query(F.data.startswith("update_last_name"))
async def update_last_name(callback_query: CallbackQuery, state: FSMContext):
    """Prompt the user to enter their last name."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your last name:")
    await state.set_state(UpdateProfileState.updating_last_name)

@router.callback_query(F.data.startswith("update_phone"))
async def update_phone_number(callback_query: CallbackQuery, state: FSMContext):
    """Prompt the user to enter their phone number."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your phone number:")
    await state.set_state(UpdateProfileState.updating_phone_number)

@router.message(UpdateProfileState.updating_first_name)
async def handle_first_name_input(message: Message, state: FSMContext, db: MDB):
    """Handle user input for first name."""
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"first_name": message.text}}
    )
    await message.answer("Your first name has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.message(UpdateProfileState.updating_last_name)
async def handle_last_name_input(message: Message, state: FSMContext, db: MDB):
    """Handle user input for last name."""
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"last_name": message.text}}
    )
    await message.answer("Your last name has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.message(UpdateProfileState.updating_phone_number)
async def handle_phone_number_input(message: Message, state: FSMContext, db: MDB):
    """Handle user input for phone number."""
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"phone_number": message.text}}
    )
    await message.answer("Your phone number has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.callback_query(F.data == 'profile_info')
async def profile_info(callback_query: CallbackQuery, db: MDB):
    """Display user information."""
    user = await db.users.find_one({"_id": callback_query.from_user.id})
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=f"First Name: {user['first_name']}\n"
             f"Last Name: {user['last_name']}\n"
             f"Phone Number: {user['phone_number']}\n",
        reply_markup=inline_builder(['⬅️Back to Profile menu'], ['profile'])
    )
