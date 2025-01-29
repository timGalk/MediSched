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



@router.callback_query(F.data.startswith("appointment"))
async def handle_appointment(callback_query: CallbackQuery, db):
    doctor_id = callback_query.data.split('_')[1]

    try:
        available_slots = await fetch_available_slots(doctor_id)  # Your function to get slots

        if not available_slots:
            await callback_query.answer("No available slots for this doctor.", show_alert=True)
            return

        available_dates = []
        for slot in available_slots:
            try:
                if isinstance(slot, datetime):
                    available_dates.append(slot.date())
                elif isinstance(slot, (str, int, float)):  # Attempt conversion if needed
                    try:
                        datetime_object = datetime.fromtimestamp(float(slot))
                    except ValueError:
                        datetime_object = datetime.strptime(str(slot), "%Y-%m-%d %H:%M:%S UTC")  # Your date format!!!
                    available_dates.append(datetime_object.date())
                else:
                    print(f"Unexpected slot type: {type(slot)}, value: {slot}")
            except (ValueError, TypeError) as conversion_error:
                print(f"Error converting slot to datetime: {conversion_error}, slot: {slot}")

        available_dates = sorted(set(available_dates))

        if not available_dates:
            await callback_query.answer("No valid dates found after processing.", show_alert=True)
            return

        date_buttons = [
            InlineKeyboardButton(text=date.strftime("%Y-%m-%d"), callback_data=f"pickdate_{doctor_id}_{date.strftime('%Y-%m-%d')}")
            for date in available_dates
        ]


        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[btn] for btn in date_buttons] + [[InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_services")]]
        )

        await callback_query.message.edit_text(
            text="Choose an available date for your appointment:",
            reply_markup=keyboard
        )

    except (DatabaseError, OperationalError) as db_error:  # SQLAlchemy exceptions (or your database library's)
        await callback_query.answer("Database error. Please try again later.", show_alert=True)
        print(f"Database error fetching slots: {db_error}")
        traceback.print_exc()

    except Exception as e:  # General exception (last resort)
        await callback_query.answer("An unexpected error occurred. Please try again.", show_alert=True)
        print(f"Unhandled error fetching slots: {e}")
        traceback.print_exc()
# ... rest of your bot code (including fetch_available_slots, etc.) ...
'''@router.callback_query(F.data.startswith("pickdate"))
async def handle_date_selection(callback_query: CallbackQuery, db: MDB):
    """Handle date selection and show available times."""
    _, doctor_id, selected_date = callback_query.data.split('_')

    try:
        # Fetch available slots for the doctor
        available_slots = await fetch_available_slots(db, doctor_id)

        print(available_slots)
        print("po")
        # Filter slots for the selected date
        time_slots = [slot for slot in available_slots if slot.startswith(selected_date)]

        if not time_slots:
            await callback_query.answer("No available times for the selected date.", show_alert=True)
            return

        # Create buttons for time slots
        time_buttons = [
            InlineKeyboardButton(text=slot.split(" ")[1], callback_data=f"picktime_{doctor_id}_{slot}")
            for slot in time_slots
        ]

        # Create a keyboard for time slots
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[btn] for btn in time_buttons] + [[InlineKeyboardButton("⬅️ Back", callback_data=f"appointment_{doctor_id}")]]
        )

        await callback_query.message.edit_text(
            text=f"Available times for {selected_date}:",
            reply_markup=keyboard
        )

    except Exception as e:
        await callback_query.answer("Failed to fetch time slots. Please try again.", show_alert=True)
        print(f"Error fetching time slots: {e}")'''

@router.callback_query(F.data.startswith('callback'))
async def back_to_doctors(callback_query: CallbackQuery, db: MDB):
    """Handle navigation back to the list of doctors."""
    selected_service_id = callback_query.message.reply_markup.inline_keyboard[0][0].callback_data.split('_')[1]
    doctors = await fetch_doctors_for_service(selected_service_id)

    if not doctors:
        await callback_query.answer("No doctors available.")
        return

    doctor_names = [doctor['name'] for doctor in doctors]
    doctor_ids = [f"doctor_{doctor['_id']}" for doctor in doctors]

    doctor_names.append('⬅️Back to services')
    doctor_ids.append('back_to_services')

    await callback_query.answer()
    await callback_query.message.edit_text(
        text=f"Choose a doctor for service ID {selected_service_id}",
        reply_markup=inline_builder(doctor_names, doctor_ids)
    )


@router.callback_query(F.data.startswith("picktime"))
async def handle_time_selection(callback_query: CallbackQuery, db: MDB):
    """Finalize the appointment booking."""
    _, doctor_id, selected_slot = callback_query.data.split('_')

    try:
        # Fetch the slot date-time from available slots collection
        slot_data = await db.available_slots.find_one({"doctor_id": int(doctor_id), "slots": selected_slot})
        if not slot_data:
            await callback_query.answer("Selected time slot is no longer available.", show_alert=True)
            return

        selected_datetime = slot_data["datetime"]

        # Record the appointment in the database
        await record_appointment(callback_query.from_user.id, int(doctor_id), selected_slot, selected_datetime, db)

        await callback_query.answer("Appointment successfully booked!", show_alert=True)

        # Confirm appointment details
        await callback_query.message.edit_text(
            text=f"Your appointment with the doctor is confirmed for {selected_datetime}.",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="main_page")]]
            )
        )

    except Exception as e:
        await callback_query.answer("Failed to book the appointment. Please try again.", show_alert=True)
        print(f"Error booking appointment: {e}")


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
