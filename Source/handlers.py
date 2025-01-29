from datetime import datetime

from aiogram import F, Router, Bot, Dispatcher
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from pymongo.errors import DuplicateKeyError

from aiogram.fsm.context import FSMContext

from aiogram import Router, F



from Source.keyboards import inline_builder
from Database.database import services_name, services_id, basket_append, basket, trash_can, set_user, \
    fetch_doctors_for_service, fetch_doctor_details, record_appointment, fetch_available_slots

router = Router()

specialities = ['ENT Specialist', 'Psychiatrist', 'Proctologist', 'Gynecologist', 'Allergist', 'Ophthalmologist',
                'Traumatologist', 'Orthopedist', 'Surgeon', 'Therapist', 'Blood Analysis']
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
    """Displays the main menu to the user.
    Args:
        callback_query: The incoming callback query.
        db: The database instance.

    Returns:
        None
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Main page',
        reply_markup=inline_builder(
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us', '👤 Profile'],
            ['services', 'basket', 'contact', 'about', 'profile']
        )
    )
@router.callback_query(F.data.startswith('services'))
async def show_services(callback_query: CallbackQuery, db: MDB):
    """
    Display a list of available services.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        db (MDB): The database instance.

    Returns:
        None

    Raises:
        Exception: If an error occurs while fetching services.
    """
    try:
        service_names = await services_name()
        service_ids = await services_id()

        service_ids = [str(id) for id in service_ids]  # Ensure service IDs are strings

        service_names.append('⬅️Back to main menu')
        service_ids.append('main_page')

        await callback_query.answer()
        await callback_query.message.edit_text(
            text='Choose a service',
            reply_markup=inline_builder(service_names, service_ids)
        )

    except Exception as e:
        await callback_query.answer("An error occurred while fetching services. Please try again.")

# @router.callback_query(F.data in specialities )
# async def show_doctors(callback_query: CallbackQuery, db: MDB):
#     await callback_query.answer()
#     await callback_query.message.edit_text(
#         text=f"Choose a doctor for {callback_query.data}",
#         reply_markup=inline_builder(
#             ['⬅️Back to services'],

    # except Exception as e:
    #     await callback_query.answer("An error occurred while fetching services. Please try again.")

#
#
#
# @router.callback_query(lambda c: c.data not in ['services', 'to_services', 'main_page', 'back_to_services'] and not c.data.startswith(('doctor_', 'callback_', 'appointment_', 'picktime_')))
# async def handle_service_selection(callback_query: CallbackQuery, db: MDB):
#     """Handle the user selection of a service and show available doctors."""
#
#
#     selected_service_id = callback_query.data.split('_')[-1]  # Extract the last segment after '_'
#
#     if selected_service_id.isdigit():
#         selected_service_id = int(selected_service_id)
#     # Fetch and display doctors for the selected service
#
#         doctors = await fetch_doctors_for_service(selected_service_id)
#
#         if not doctors:
#             await callback_query.answer("No doctors available for this service.")
#             return
#
#         doctor_names = [doctor['name'] for doctor in doctors]
#         doctor_ids = [f"doctor_{doctor['_id']}" for doctor in doctors]  # Use f-strings here
#
#         doctor_names.append('⬅️Back to services')
#         doctor_ids.append('back_to_services')
#
#         await callback_query.answer()
#         await callback_query.message.edit_text(
#             text=f"Choose a doctor for service ID {selected_service_id}",
#             reply_markup=inline_builder(doctor_names, doctor_ids)
#         )
#
#
#
# @router.callback_query(F.data.startswith('doctor_'))
# async def show_doctor(callback_query: CallbackQuery, db: MDB):
#     """Display doctor details based on the selected doctor."""
#     doctor_id = callback_query.data.split('_')[1]  # Extract doctor_id from callback data
#
#     # Pass the database object (db) and the doctor_id
#     doctor = await fetch_doctor_details(db, doctor_id)
#
#     if not doctor:
#         await callback_query.answer("Appointments weren't found.", show_alert=True)
#
#     await callback_query.answer()
#
#     # Create inline buttons for the doctor details
#     appointment_button = InlineKeyboardButton(text="Make an Appointment 🗓️", callback_data=f"appointment_{doctor_id}")
#     back_button = InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_services")
#
#     # Inline keyboard for options (buttons need to be in a 2D list)
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[
#             [appointment_button],  # Each sub-list represents a row of buttons
#             [back_button]
#         ]
#     )
# @router.callback_query(F.data.startswith("appointment"))
# async def handle_appointment(callback_query: CallbackQuery, db):
#     """Handle appointment slot selection."""
#     # Extract doctor ID from the callback data
#     doctor_id = callback_query.data.split('_')[1]
#
#     # Fetch available slots for the doctor
#     available_slots = await fetch_available_slots(doctor_id)
#     print(f"Fetched slots: {available_slots}")  # Debug log
#
#     if not available_slots:
#         await callback_query.answer("No available slots for this doctor.", show_alert=True)
#
#     # Process slots into unique dates
#     available_dates = []
#     for slot in available_slots:
#         if isinstance(slot, datetime):
#             available_dates.append(slot.date())
#         elif isinstance(slot, (str, int, float)):
#             # Convert to datetime if it's a timestamp or string
#
#             datetime_obj = datetime.fromtimestamp(float(slot))
#             datetime_obj = datetime.strptime(str(slot), "%Y-%m-%d %H:%M:%S UTC")
#             available_dates.append(datetime_obj.date())
#
#     # Ensure unique and sorted dates
#     available_dates = sorted(set(available_dates))
#
#     if not available_dates:
#         await callback_query.answer("No valid dates available.", show_alert=True)
#         return
#
#     # Create inline buttons for each available date
#     date_buttons = [
#         InlineKeyboardButton(
#             text=date.strftime("%Y-%m-%d"),
#             callback_data=f"picktime_{doctor_id}_{date.strftime('%Y-%m-%d-%H:%M')}"
#         )
#         for date in available_dates
#     ]
#
#     # Add back button and create the keyboard
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=[[btn] for btn in date_buttons] + [
#             [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_services")]
#         ]
#     )
#
#     # Edit message with available dates
#     await callback_query.message.edit_text(
#         text="Choose an available date for your appointment:",
#         reply_markup=keyboard
#     )
#
# @router.callback_query(F.data.startswith("picktime"))
# async def handle_time_selection(callback_query: CallbackQuery, db):
#     """Handle appointment confirmation and record it."""
#     try:
#         # Extract doctor ID and selected slot (date) from callback data
#         _, doctor_id, selected_slot = callback_query.data.split('_')
#         print(f"Triggered time selection: doctor_id={doctor_id}, selected_slot={selected_slot}")  # Debug log
#
#         # Fetch slot data from database (assuming slot date is stored)
#         slot_data = await db.available_slots.find_one({"doctor_id": int(doctor_id)})
#         print(f"Fetched slot data: {slot_data}")  # Debug log
#
#         if not slot_data:
#             await callback_query.answer("The selected time slot is no longer available.", show_alert=True)
#             return
#
#         # Get the datetime for the selected slot
#         selected_datetime = slot_data.get("datetime", None)
#         if not selected_datetime:
#             await callback_query.answer("Failed to retrieve the selected time. Please try again.", show_alert=True)
#             return
#
#         # Record the appointment in the database
#         await record_appointment(
#             user_id=callback_query.from_user.id,
#             doctor_id=int(doctor_id),
#             selected_date=selected_datetime,
#             db=db, slot_data=slot_data
#         )
#
#         # Notify the user and show confirmation message
#         await callback_query.answer("Your order is confirmed!", show_alert=True)
#         await callback_query.message.edit_text(
#             text=f"Your appointment is confirmed for {selected_datetime}. Thank you!",
#             reply_markup=InlineKeyboardMarkup(
#                 inline_keyboard=[[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_page")]]
#             )
#         )
#
#     except Exception as e:
#         await callback_query.answer("Failed to confirm your appointment. Please try again.", show_alert=True)
#         print(f"Error in handle_time_selection: {e}")


@router.callback_query(F.data == 'contact')
async def show_contact(callback_query: CallbackQuery, db: MDB):
    """
    Show contact information to the user.

    This function is triggered when the user clicks on the 'Contact us' button.
    It displays a message with the contact information and provides a 'Back to main menu' button.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        db (MDB): The database instance.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Contact us',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

# About menu

@router.callback_query(F.data == 'about')
async def show_about(callback_query: CallbackQuery, db: MDB):
    """
    Display information about the organization.

    This function is triggered when the user selects the 'About us' menu item.
    It answers the callback query, updates the message text to display the 'About us' information,
    and provides a 'Back to main menu' button to navigate back to the main menu.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        db (MDB): The database instance.
    """
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='About us\n',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )


# Profile menu
class UpdateProfileState(StatesGroup):
    updating_first_name = State()
    updating_last_name = State()
    updating_phone_number = State()

@router.callback_query(F.data == 'profile')
async def show_profile_menu(callback_query: CallbackQuery, db: MDB):
    """
    Show the profile menu for users to input personal information.

    This function is triggered when a user clicks on the 'profile' button in the main menu.
    It displays a menu with options to update the user's first name, last name, phone number, and profile info.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        db (MDB): The database instance.

    Returns:
        None
    """
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
    """
    Prompt the user to enter their first name.

    This function is triggered when the user clicks on the 'Update First Name' button in the profile menu.
    It answers the callback query, sends a message to the user prompting them to enter their first name,
    and sets the state to 'updating_first_name' to await the user's input.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        state (FSMContext): The finite state machine context.

    Returns:
        None
    """
    await callback_query.answer()
    await callback_query.message.answer("Please enter your first name:")
    await state.set_state(UpdateProfileState.updating_first_name)

@router.callback_query(F.data.startswith("update_last_name"))
async def update_last_name(callback_query: CallbackQuery, state: FSMContext):
    """Prompt the user to enter their last name.

    This function is triggered when the user clicks on the 'Update Last Name' button in the profile menu.
    It answers the callback query, sends a message to the user prompting them to enter their last name,
    and sets the state to 'updating_last_name' to await the user's input.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        state (FSMContext): The finite state machine context.

    Returns:
        None
    """
    await callback_query.answer()
    await callback_query.message.answer("Please enter your last name:")
    await state.set_state(UpdateProfileState.updating_last_name)

@router.callback_query(F.data.startswith("update_phone"))
async def update_phone_number(callback_query: CallbackQuery, state: FSMContext):
    """    Prompt the user to enter their phone number.

    This function is triggered when the user clicks on the 'Update Phone Number' button in the profile menu.
    It answers the callback query, sends a message to the user prompting them to enter their phone number,
    and sets the state to 'updating_phone_number' to await the user's input.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        state (FSMContext): The finite state machine context.

    Returns:
        None
    """
    await callback_query.answer()
    await callback_query.message.answer("Please enter your phone number:")
    await state.set_state(UpdateProfileState.updating_phone_number)

@router.message(UpdateProfileState.updating_first_name)
async def handle_first_name_input(message: Message, state: FSMContext, db: MDB):
    """
        Handle user input for first name.

    This function is triggered when the user sends a message while in the state of updating their first name.
    It updates the user's first name in the database and sends a confirmation message to the user.
    It then clears the state of the FSMContext.

    Args:
        message (Message): The incoming message.
        state (FSMContext): The finite state machine context.
        db (MDB): The MongoDB database connection.

    Returns:
        None
    """
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"first_name": message.text}}
    )
    await message.answer("Your first name has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.message(UpdateProfileState.updating_last_name)
async def handle_last_name_input(message: Message, state: FSMContext, db: MDB):
    """
        Handle user input for last name.

    This function is triggered when the user sends a message while in the state of updating their last name.
    It updates the user's last name in the database, sends a confirmation message to the user, and clears the state of the FSMContext.

    Args:
        message (Message): The incoming message.
        state (FSMContext): The finite state machine context.
        db (MDB): The MongoDB database connection.

    Returns:
        None
    """
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"last_name": message.text}}
    )
    await message.answer("Your last name has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.message(UpdateProfileState.updating_phone_number)
async def handle_phone_number_input(message: Message, state: FSMContext, db: MDB):
    """ Handle user input for phone number.

    This function is triggered when the user sends a message while in the state of updating their phone number.
    It updates the user's phone number in the database, sends a confirmation message to the user, and clears the state of the FSMContext.

    Args:
        message (Message): The incoming message.
        state (FSMContext): The finite state machine context.
        db (MDB): The MongoDB database connection.

    Returns:
        None
    """
    await db.users.update_one(
        {"_id": message.from_user.id},
        {"$set": {"phone_number": message.text}}
    )
    await message.answer("Your phone number has been updated.", reply_markup=inline_builder([
        "⬅️ Back to Profile"], ["profile"]))
    await state.clear()

@router.callback_query(F.data == 'profile_info')
async def profile_info(callback_query: CallbackQuery, db: MDB):
    """
    Display user information.

    This function is triggered when the user clicks on the 'Profile Info' button.
    It retrieves the user's information from the database and displays it in a message.

    Args:
        callback_query (CallbackQuery): The incoming callback query.
        db (MDB): The MongoDB database connection.

    Returns:
        None
    """
    user = await db.users.find_one({"_id": callback_query.from_user.id})
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=f"First Name: {user['first_name']}\n"
             f"Last Name: {user['last_name']}\n"
             f"Phone Number: {user['phone_number']}\n",
        reply_markup=inline_builder(['⬅️Back to Profile menu'], ['profile'])
    )
