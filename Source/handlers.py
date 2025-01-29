from datetime import datetime

from aiogram import F, Router, Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from pymongo.errors import DuplicateKeyError

import traceback
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.exc import DatabaseError, OperationalError  # Correct imports


from Source.keyboards import inline_builder
from Database.database import services_name, services_id, basket_append, basket, trash_can, set_user, \
    fetch_doctors_for_service, fetch_doctor_details, record_appointment, fetch_available_slots

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: MDB):
    """Handle the /start command."""
    with suppress(DuplicateKeyError):
        await db.users.insert_one(set_user(message.from_user.id))

    pattern = {
        'text': 'Welcome to our Medical center',
        'reply_markup': inline_builder(
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us'],
            ['services', 'basket', 'contact', 'about']
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
            ['📝 Services', '🛒 Basket', '✉️ Contact us', '📑 About us'],
            ['services', 'basket', 'contact', 'about']
        )
    )

@router.callback_query(F.data.in_(['services', 'to_services']))
async def show_services(callback_query: CallbackQuery, db: MDB):
    """Display a list of available services."""
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
        print(f"Error: {e}")





@router.callback_query(lambda c: c.data not in ['services', 'to_services', 'main_page', 'back_to_services'] and not c.data.startswith(('doctor_', 'callback_', 'appointment_', 'picktime_')))
async def handle_service_selection(callback_query: CallbackQuery, db: MDB):
    """Handle the user selection of a service and show available doctors."""
    # Extract only the numeric part of the callback data


    selected_service_id = callback_query.data.split('_')[-1]  # Extract the last segment after '_'

    if selected_service_id.isdigit():
        selected_service_id = int(selected_service_id)
    # Fetch and display doctors for the selected service

        doctors = await fetch_doctors_for_service(selected_service_id)

        if not doctors:
            await callback_query.answer("No doctors available for this service.")
            return

        doctor_names = [doctor['name'] for doctor in doctors]
        doctor_ids = [f"doctor_{doctor['_id']}" for doctor in doctors]  # Use f-strings here

        doctor_names.append('⬅️Back to services')
        doctor_ids.append('back_to_services')

        await callback_query.answer()
        await callback_query.message.edit_text(
            text=f"Choose a doctor for service ID {selected_service_id}",
            reply_markup=inline_builder(doctor_names, doctor_ids)
        )


    #else :


@router.callback_query(F.data.startswith('doctor_'))
async def show_doctor(callback_query: CallbackQuery, db: MDB):
    """Display doctor details based on the selected doctor."""
    doctor_id = callback_query.data.split('_')[1]  # Extract doctor_id from callback data

    # Pass the database object (db) and the doctor_id
    doctor = await fetch_doctor_details(db, doctor_id)

    if not doctor:
        await callback_query.answer("Doctor not found.", show_alert=True)
        return

    await callback_query.answer()

    # Create inline buttons for the doctor details
    appointment_button = InlineKeyboardButton(text="Make an Appointment 🗓️", callback_data=f"appointment_{doctor_id}")
    add_to_cart_button = InlineKeyboardButton(text="Add to Cart 🛒", callback_data=f"cart_{doctor['_id']}")
    back_button = InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_services")

    # Inline keyboard for options (buttons need to be in a 2D list)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [appointment_button],  # Each sub-list represents a row of buttons
            [add_to_cart_button],
            [back_button]
        ]
    )

    # Show doctor details
    await callback_query.message.edit_text(
        text=(
            f"{doctor['name']}\n"
            f"{doctor['description']}\n"
            f"Price: {doctor['price']} zlt per consultation\n"
        ),
        reply_markup=keyboard
    )

from datetime import datetime
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import traceback
from datetime import datetime, timedelta



from datetime import datetime
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import traceback

@router.callback_query(F.data.startswith("appointment"))
async def handle_appointment(callback_query: CallbackQuery, db):
    """Handle appointment slot selection."""
    try:
        # Extract doctor ID from the callback data
        doctor_id = callback_query.data.split('_')[1]
        print(f"Triggered appointment callback for doctor_id={doctor_id}")  # Debug log

        # Fetch available slots for the doctor
        available_slots = await fetch_available_slots(doctor_id)
        print(f"Fetched slots: {available_slots}")  # Debug log

        if not available_slots:
            await callback_query.answer("No available slots for this doctor.", show_alert=True)
            return

        # Process slots into unique dates
        available_dates = []
        for slot in available_slots:
            try:
                if isinstance(slot, datetime):
                    available_dates.append(slot.date())
                elif isinstance(slot, (str, int, float)):
                    # Convert to datetime if it's a timestamp or string
                    try:
                        datetime_obj = datetime.fromtimestamp(float(slot))
                    except ValueError:
                        datetime_obj = datetime.strptime(str(slot), "%Y-%m-%d %H:%M:%S UTC")
                    available_dates.append(datetime_obj.date())
                else:
                    print(f"Unexpected slot type: {type(slot)}, value: {slot}")
            except (ValueError, TypeError) as e:
                print(f"Error converting slot: {slot}, error: {e}")

        # Ensure unique and sorted dates
        available_dates = sorted(set(available_dates))
        print(f"Processed available dates: {available_dates}")  # Debug log

        if not available_dates:
            await callback_query.answer("No valid dates available.", show_alert=True)
            return

        # Create inline buttons for each available date
        date_buttons = [
            InlineKeyboardButton(
                text=date.strftime("%Y-%m-%d"),
                callback_data=f"picktime_{doctor_id}_{date.strftime('%Y-%m-%d')}"
            )
            for date in available_dates
        ]

        # Add back button and create the keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[btn] for btn in date_buttons] + [
                [InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_services")]
            ]
        )

        # Edit message with available dates
        await callback_query.message.edit_text(
            text="Choose an available date for your appointment:",
            reply_markup=keyboard
        )

    except Exception as e:
        await callback_query.answer("An unexpected error occurred. Please try again.", show_alert=True)
        print(f"Error in handle_appointment: {e}")
        traceback.print_exc()


@router.callback_query(F.data.startswith("picktime"))
async def handle_time_selection(callback_query: CallbackQuery, db):
    """Handle appointment confirmation and record it."""
    try:
        # Extract doctor ID and selected slot (date) from callback data
        _, doctor_id, selected_slot = callback_query.data.split('_')
        print(f"Triggered time selection: doctor_id={doctor_id}, selected_slot={selected_slot}")  # Debug log

        # Fetch slot data from database (assuming slot date is stored)
        slot_data = await db.available_slots.find_one({"doctor_id": int(doctor_id)})
        print(f"Fetched slot data: {slot_data}")  # Debug log

        if not slot_data:
            await callback_query.answer("The selected time slot is no longer available.", show_alert=True)
            return

        # Get the datetime for the selected slot
        selected_datetime = slot_data.get("datetime", None)
        if not selected_datetime:
            await callback_query.answer("Failed to retrieve the selected time. Please try again.", show_alert=True)
            return

        # Record the appointment in the database
        await record_appointment(
            user_id=callback_query.from_user.id,
            doctor_id=int(doctor_id),
            selected_date=selected_datetime,
            db=db, slot_data=slot_data
        )

        # Notify the user and show confirmation message
        await callback_query.answer("Your order is confirmed!", show_alert=True)
        await callback_query.message.edit_text(
            text=f"Your appointment is confirmed for {selected_datetime}. Thank you!",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_page")]]
            )
        )

    except Exception as e:
        await callback_query.answer("Failed to confirm your appointment. Please try again.", show_alert=True)
        print(f"Error in handle_time_selection: {e}")

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
@router.callback_query(F.data == 'basket_')
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
