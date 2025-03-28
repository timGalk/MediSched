from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from pymongo.errors import DuplicateKeyError

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from Database.medicalTestsAndPdfOutput import generate_medical_tests_results_and_return_it, make_a_med_test_record
from Source.keyboards import inline_builder
from Database.database import services_name, services_id, set_user, \
    fetch_doctors_for_service, fetch_doctor_details, record_appointment, fetch_available_slots, fetch_services, find_doc

router = Router()

@router.message(CommandStart())
async def start(message: Message, db: MDB):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Handle the /start command.

    This function is triggered when the /start command is issued by the user. It performs the following actions:
    1. Adds the user to the database using their unique ID. If the user already exists, it suppresses the DuplicateKeyError.
    2. Sends a welcome message to the user with an inline keyboard providing options for various actions.

    Parameters:
    - message: The user's input, which can be a Message or CallbackQuery object.
    - db: The database connection object (MDB).

    Behavior:
    - Inserts a new user into the database using their Telegram user ID.
    - Displays a welcome message with options for services, orders, medical tests, and more, using an inline keyboard.
    - Adapts the response method depending on whether the input is a Message or CallbackQuery.
    """
    """Handle the /start command."""
    with suppress(DuplicateKeyError):
        await db.users.insert_one(set_user(message.from_user.id))

    pattern = {
        'text': 'Welcome to our Medical center',
        'reply_markup': inline_builder(
            ['📝 Services', '🛒 Orders','💉 Make a Med Test','📁 Show Med Tests', '✉️ Contact us', '📑 About us', '👤 Profile'],
            ['services', 'orders','test', 'show_tests', 'contact', 'about', 'profile']
        )
    }

    if isinstance(message, Message):
        await message.answer(**pattern)
    elif isinstance(message, CallbackQuery):
        await message.message.edit_text(**pattern)

@router.callback_query(F.data == 'main_page')
async def main_menu(callback_query: CallbackQuery, db: MDB):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Handles the callback query to display the main menu.

    Parameters:
    callback_query (CallbackQuery): The callback query object triggered by the user action.
    db (MDB): The database connection instance.

    Behavior:
    - Responds to the callback query to confirm receipt.
    - Edits the message text to display the main menu options.
    - Updates the reply markup with the main menu buttons, linking user actions to corresponding functionalities.
    """
    """Displays the main menu to the user."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Main page',
        reply_markup=inline_builder(
            ['📝 Services', '🛒 Orders','💉 Make a Med Test','📁 Show Med Tests', '✉️ Contact us', '📑 About us', '👤 Profile'],
            ['services', 'orders','test', 'show_tests', 'contact', 'about', 'profile']
        )
    )

@router.callback_query(lambda c: c.data == "test")
async def generate_med_results(callback_query: CallbackQuery):
    """The function was created by Nazarii"""
    """
    Handles the callback query when the data equals "test" to generate and display medical test results.

    Parameters:
    - callback_query (CallbackQuery): The incoming callback query from Telegram.

    Functionality:
    - Generates a set of medical test results using the `generate_medical_tests_results_and_return_it` function.
    - Uses the `make_a_med_test_record` function to record the test results for the specified user.
    - Formats the generated test results as a text message with markdown styling.
    - Sends the formatted test results to the user and updates the existing message in the chat with the results.
    - Uses an inline button to navigate back to the main menu.

    Requirements:
    - The callback query must have a `data` field set to "test" for this function to execute.
    - Requires access to the user's Telegram `id` for recording the test results.
    - Inline buttons should be built using `inline_builder` for navigation.
    """
    """Generates test results and displays them in Telegram chat."""
    test_results = generate_medical_tests_results_and_return_it()
    user_id = callback_query.from_user.id  # Replace with the target user_id
    await make_a_med_test_record(user_id, test_results)

    # Format test results as a text message
    results_text = "🩺 Your Medical Test Results:\n\n"
    for category, tests in test_results.items():
        results_text += f"*{category}:*\n"
        for test, value in tests.items():
            results_text += f"  - {test}: *{value}*\n"
        results_text += "\n"

    # Send the test results
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=results_text,
        parse_mode="Markdown",
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

@router.callback_query(F.data == 'show_tests')
async def show_all_med_results(callback_query: CallbackQuery, db: MDB):
    """The function was created by Nazarii"""
    """
    Fetches and displays all medical test results for the user when the associated callback query is triggered.

    Parameters:
    callback_query (CallbackQuery): The callback query object containing information about the user and their interaction.
    db (MDB): The database connection object for accessing test results.

    Behavior:
    1. Retrieves the test results for the user from the database.
    2. Formats the test results into a readable string for display.
    3. If no test results are available, sends a message informing the user there are no tests.
    4. If test results are available, presents them in a formatted message.
    5. Displays options for the user to navigate back to the main menu.
    """
    """Fetches and displays all medical test results for the user."""
    await callback_query.answer()

    user_id = callback_query.from_user.id  # Replace with the target user_id

    tests_results = await db.test_results.find({'user_id': user_id}).to_list(length=None)

    formatted_orders = []

    def format_lab_results(results):
        """Formats the medical test results into a readable string."""
        formatted_message = ""

        for category, tests in results.items():
            formatted_message += f"\n**{category}**\n"
            for test, value in tests.items():
                formatted_message += f"  - {test}: {value}\n"

        return formatted_message

    for test in tests_results:
        formatted_orders.append(
            f"Test ID: {test['_id']}\n"
            f"Date and Time: {test['dateAndTime'].strftime('%Y-%m-%d %H:%M')}\n"
            f"Results: {format_lab_results(test['results'])}\n"
        )

    if not formatted_orders:
        await callback_query.message.edit_text(
            text='You have no med tests.',
            reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
        )
        return

    result_text = "\n".join(formatted_orders)

    await callback_query.message.edit_text(
        text=f'Your lab results:\n{result_text}',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

@router.callback_query(F.data == 'contact')
async def show_contact(callback_query: CallbackQuery, db: MDB):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Handles callback query with data 'contact' to show contact information.

    Parameters:
    callback_query (CallbackQuery): The callback query instance triggered by the user.
    db (MDB): The database instance, representing a connection to the database.

    Returns:
    Coroutine: Asynchronous interaction for sending a specific response to the user.

    Functionality:
    - Answers the callback query to confirm the user interaction.
    - Edits the message text with the contact information.
    - Provides an inline keyboard button to return to the main menu.
    """
    """Show contact information."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text='Contact us \n'
             'Telegram @iinazar24\n'
             'Telegram @byte_tim',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

@router.callback_query(F.data == 'about')
async def show_about(callback_query: CallbackQuery, db: MDB):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Handles the callback query when the user selects the "about" option.

    This function is responsible for displaying detailed information about the organization to the user. It provides an overview of the medical services offered, including doctor appointment scheduling and medical testing, highlighting the center’s commitment to patient care and convenience. The information is displayed as a formatted message, along with an inline button to navigate back to the main menu.
    """
    """Display information about the organization."""
    await callback_query.answer()
    await callback_query.message.edit_text(
        text="""
                    🌟 Welcome to our Medical Center, where we prioritize your health and well-being. Our center offers the following key features:

                    1. 🩺 **Doctor Appointment Scheduling**:
                    You can easily schedule an appointment with one of our experienced doctors. Whether you need a routine check-up or specialized consultation, we provide a seamless booking process to ensure timely care.

                    2. 🔬 **Medical Analysis & Testing**:
                    We offer a wide range of medical tests and analyses to support accurate diagnosis and effective treatment plans.  Our state-of-the-art facilities ensure the highest standards of care.

                    Our goal is to provide comprehensive healthcare services with a focus on convenience, quality, and patient satisfaction. Feel free to contact us 📞 for more details or to book an appointment today! 💬
        """
        ,
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

@router.callback_query(F.data == 'orders')
async def show_orders(callback_query: CallbackQuery, db: MDB):
    """The function was created by Tsimur and updated by Nazarii"""
    """
    Handles a callback query to display all orders for a specific user.

    This function is triggered when a callback query with the data value 'orders' is received.
    It interacts with a MongoDB database instance to retrieve all orders associated with the current user based on their user ID.

    Parameters:
    callback_query (CallbackQuery): The received callback query object containing information about the query.
    db (MDB): The MongoDB database instance used to fetch order details.

    Functionality:
    1. Retrieves the user's ID from the callback query.
    2. Queries the database to fetch orders associated with the user ID.
    3. For each order, retrieves and includes additional details like the doctor's name.
    4. Formats the order data for display.
    5. If no orders are found, sends a message indicating the absence of orders.
    6. If orders exist, sends a formatted response listing all the user's orders.
    7. A reply markup is added to allow navigation back to the main menu.
    """
    """Fetches and displays all orders for the user."""
    await callback_query.answer()

    user_id = callback_query.from_user.id  # Replace with the target user_id

    orders = await db.records.find({'user_id': user_id}).to_list(length=None)

    formatted_orders = []
    for order in orders:
        doctor = await find_doc(order['doctor_id'])  # Await the async function
        doctor_name = doctor.get('name')

        formatted_orders.append(
            f"Order ID: {order['_id']}\n"
            f"Doctor ID: {doctor_name}\n"
            f"Date and Time: {order['dateAndTime'].strftime('%Y-%m-%d %H:%M')}\n"
            f"Status: {order['status']}\n"
        )

    if not formatted_orders:
        await callback_query.message.edit_text(
            text='You have no orders.',
            reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
        )
        return

    result_text = "\n".join(formatted_orders)

    await callback_query.message.edit_text(
        text=f'Your orders:\n{result_text}',
        reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page'])
    )

#Start

# Profile menu
class UpdateProfileState(StatesGroup):
    """The class was created by Tsimur"""
    """
    Represents a state machine for updating user profile details in a system.

    This class is a subclass of `StatesGroup` used to manage the different states involved in the process of updating user profile information.

    States:
    - `updating_first_name`: State for updating the user's first name.
    - `updating_last_name`: State for updating the user's last name.
    - `updating_phone_number`: State for updating the user's phone number.
    """
    updating_first_name = State()
    updating_last_name = State()
    updating_phone_number = State()

@router.callback_query(F.data == 'profile')
async def show_profile_menu(callback_query: CallbackQuery, db: MDB):
    """The class was created by Tsimur"""

    """
    Show the profile menu for users to input personal information.

    This function is triggered when a user interacts with the 'profile' callback query. It displays a menu
    containing options for updating personal details such as first name, last name, phone number, or other profile information.

    Parameters:
    callback_query (CallbackQuery): The callback query object triggered by the user interaction.
    db (MDB): The MongoDB connection object utilized to manage database operations.

    Returns:
    None
    """
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
    """The class was created by Tsimur"""
    """
    Handles the callback query that starts with "update_first_name" to prompt the user to update their first name.

    Parameters:
    callback_query (CallbackQuery): The callback query object received from the user interaction.
    state (FSMContext): The finite state machine context to manage and update the user's state.

    Flow:
    1. Answers the callback query to inform Telegram that it is handled.
    2. Prompts the user with a message to enter their first name.
    3. Sets the FSM state to "updating_first_name" in UpdateProfileState.
    """
    """Prompt the user to enter their first name."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your first name:")
    await state.set_state(UpdateProfileState.updating_first_name)

@router.callback_query(F.data.startswith("update_last_name"))
async def update_last_name(callback_query: CallbackQuery, state: FSMContext):
    """The class was created by Tsimur"""
    """
    Handles the callback query for updating the user's last name.

    Parameters:
    callback_query (CallbackQuery): The callback query object containing the user's input.
    state (FSMContext): The current finite state machine context for maintaining conversation state.

    Actions:
    1. Responds to the callback query to provide feedback to the user.
    2. Prompts the user to enter their last name.
    3. Sets the finite state machine state to updating_last_name for further processing.
    """
    """Prompt the user to enter their last name."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your last name:")
    await state.set_state(UpdateProfileState.updating_last_name)

@router.callback_query(F.data.startswith("update_phone"))
async def update_phone_number(callback_query: CallbackQuery, state: FSMContext):
    """The class was created by Tsimur"""
    """
    Handle the callback query for updating the phone number.

    This function responds to a callback query that starts with "update_phone" and prompts the user 
    to provide their phone number. It also updates the state to indicate that the user is in the 
    process of updating their phone number.

    Parameters:
    callback_query: The callback query object containing the user's interaction data.
    state: The FSMContext object used to manage the user's state.

    Actions:
    - Answers the callback query.
    - Sends a message to the user requesting their phone number.
    - Updates the user's state to 'updating_phone_number' for the profile update process.
    """
    """Prompt the user to enter their phone number."""
    await callback_query.answer()
    await callback_query.message.answer("Please enter your phone number:")
    await state.set_state(UpdateProfileState.updating_phone_number)

@router.message(UpdateProfileState.updating_first_name)
async def handle_first_name_input(message: Message, state: FSMContext, db: MDB):
    """The class was created by Tsimur"""
    """
    Handle user input for updating the first name.

    Parameters:
    message (Message): The message object containing user input.
    state (FSMContext): The finite-state machine context for the current user state.
    db (MDB): The database client instance used to interact with the MongoDB database.

    This function updates the user's first name in the database based on the provided input.
    After updating, the user receives a confirmation message, and their state is cleared.
    """
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
    """The class was created by Tsimur"""
    """
    Handle user input for last name.

    This function operates within a state machine context handling user messages when they are in
    the 'updating_last_name' state. It updates the user's last name in the database, sends a
    confirmation message to the user, and then clears the state.

    Parameters:
    message (Message): The incoming message object from the user.
    state (FSMContext): The finite state machine context for tracking conversation states.
    db (MDB): An instance of the MongoDB database for performing database operations.
    """
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
    """The class was created by Tsimur"""
    """
    Handle user input for phone number.

    This function is triggered when the user provides a phone number during the "updating_phone_number" state.
    It updates the user's phone number in the database and sends a confirmation message back to the user.

    Parameters:
    - message: An instance of the Message object representing the user's input message.
    - state: An instance of FSMContext to manage the user's finite state.
    - db: An instance of MDB, representing the database connection.

    The function performs the following:
    - Updates the "phone_number" field for the user in the database using their user ID.
    - Sends a confirmation message to the user about the phone number update.
    - Provides an inline keyboard option to navigate back to the profile section.
    - Clears the current finite state for the user.
    """
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
    """The class was created by Tsimur"""
    """
    Handles the callback query for displaying user profile information.

    Parameters:
    callback_query: The CallbackQuery object received from the user interaction.
    db: The MDB database instance used to query user information.

    Functionality:
    - Retrieves the user information from the database using the user's ID.
    - Responds to the callback query to prevent timeout.
    - Edits the message to display the user's first name, last name, and phone number, providing a button to navigate back to the profile menu.
    """
    """Display user information."""
    user = await db.users.find_one({"_id": callback_query.from_user.id})
    await callback_query.answer()
    await callback_query.message.edit_text(
        text=f"First Name: {user['first_name']}\n"
             f"Last Name: {user['last_name']}\n"
             f"Phone Number: {user['phone_number']}\n",
        reply_markup=inline_builder(['⬅️Back to Profile menu'], ['profile'])
    )

#End
@router.callback_query(F.data.in_(['services', 'to_services']))
async def show_services(callback_query: CallbackQuery, db: MDB):
    """The class was created by Tsimur and updated by Nazarii"""
    """
    Handles the callback query to display a list of available services.

    Parameters:
    callback_query (CallbackQuery): The callback query object triggered by the user.
    db (MDB): The database instance for interacting with the database.

    Raises:
    Exception: Catches and handles any exception that occurs during the processing of the callback query.

    Behavior:
    Fetches the available service names and service IDs.
    Appends a 'Back to Main Menu' option to the list of services.
    Ensures the service IDs are converted to strings.
    Updates the message text and displays an inline keyboard with the list of services.
    Handles any errors that occur, responds to the user with an error message, and logs the error.
    """
    """Display a list of available services."""
    try:
        service_names = await services_name()
        service_ids = await services_id()

        service_ids = [str(id) for id in service_ids]  # Ensure service IDs are strings

        service_names.append('⬅️ Back to Main Menu')
        service_ids.append('main_page')

        await callback_query.answer()
        await callback_query.message.edit_text(
            text='Choose a service',
            reply_markup=inline_builder(service_names, service_ids)
        )

    except Exception as e:
        await callback_query.answer("An error occurred while fetching services. Please try again.")
        print(f"Error: {e}")

@router.callback_query(
    lambda c: c.data not in ['services', 'to_services', 'main_page', 'back_to_services', 'back_to_doctors'] and not c.data.startswith(
        ('doctor_', 'callback_', 'appointment_', 'picktime_')))
async def handle_service_selection(callback_query: CallbackQuery, db: MDB):
    """The class was created by Tsimur and updated by Nazarii"""
    """
    Handles the user's selection of a service and displays the list of available doctors for the chosen service.

    Parameters:
      callback_query (CallbackQuery): The callback query object containing the user's selection data.
      db (MDB): The database instance used to query service and doctor information.

    Behavior:
      - Extracts the selected service ID from the callback query data.
      - Verifies the extracted service ID is a valid digit.
      - Queries the database to fetch doctors associated with the selected service.
      - If no doctors are available, sends an alert to the user indicating the unavailability.
      - Prepares and displays a list of doctor names with associated callback data.
      - Adds a 'Back to Services' button to allow the user to navigate back to the services list.
      - Retrieves the service name from the database and includes it in the message text.
      - Updates the message text and inline keyboard with the list of doctors.

    Dependencies:
      fetch_doctors_for_service: An asynchronous function to fetch doctors related to a service.
      inline_builder: A utility function to create an inline keyboard with the list of options.
    """
    """Handle the user selection of a service and show available doctors."""
    selected_service_id = callback_query.data.split('_')[-1]  # Extract the last segment after '_'

    if selected_service_id.isdigit():
        selected_service_id = int(selected_service_id)

        # Fetch doctors for the selected service
        doctors = await fetch_doctors_for_service(selected_service_id)

        if not doctors:
            await callback_query.answer("No doctors available for this service.")
            return

        doctor_names = [doctor['name'] for doctor in doctors]
        doctor_ids = [f"doctor_{doctor['_id']}" for doctor in doctors]

        # Add a back button to return directly to the main services list
        doctor_names.append('⬅️ Back to Services')
        doctor_ids.append('services')

        # Correct usage with Motor (asynchronous)
        service = await db.services.find_one({'_id': selected_service_id})
        service_name = service['name'] if service else None
        await callback_query.answer()
        await callback_query.message.edit_text(
            text=f"Choose a doctor for service {service_name}\n",
            reply_markup=inline_builder(doctor_names, doctor_ids)
        )

@router.callback_query(F.data == 'back_to_services')
async def back_to_services(callback_query: CallbackQuery, db: MDB):
    """The class was created by Nazarii"""
    """
    Handle the callback query to navigate back to the services list.

    Parameters:
    callback_query (CallbackQuery): The callback query object containing data about the triggered callback.
    db (MDB): Database instance used to perform any necessary operations.

    This function redirects the user to the services list by invoking the show_services function.
    """
    """Handle going back to the services list."""
    await show_services(callback_query, db)  # Directly call show_services to avoid an extra window

@router.callback_query(F.data.startswith('doctor_'))
async def show_doctor(callback_query: CallbackQuery, db: MDB):
    """The class was created by Nazarii"""
    """
    Handle a callback query to show doctor details when a callback data starting with 'doctor_' is received.

    Parameters:
    callback_query (CallbackQuery): The callback query received from the user when interacting with the bot.
    db (MDB): The database object used for retrieving doctor details.

    Functionality:
    1. Extracts `doctor_id` from the callback data.
    2. Retrieves the details of the doctor with the given `doctor_id` from the database.
    3. If no doctor is found, alerts the user with a "Doctor not found" message.
    4. If a doctor is found:
       - Prepares an inline keyboard with options to make an appointment or go back to the doctor list.
       - Edits the relevant message to display the doctor's details such as name, description, and price.

    Notes:
    The database query and button construction are asynchronous operations and must be awaited.
    """
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
    back_button = InlineKeyboardButton(text="⬅️ Back to Doctors", callback_data=f"back_to_doctors_{doctor['spec_id']}")

    # Inline keyboard for options (buttons need to be in a 2D list)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [appointment_button],  # Each sub-list represents a row of buttons
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

from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
import traceback
from datetime import datetime, timedelta

@router.callback_query(F.data.startswith('back_to_doctors'))
async def back_to_doctors(callback_query: CallbackQuery, db: MDB):
    """The class was created by Nazarii"""
    """
    Handle the callback query when the user wants to go back to the doctors' list for the selected service.

    Parameters:
    callback_query (CallbackQuery): The callback query event from the user interaction.
    db (MDB): An instance of the database for data operations.

    Behavior:
    Splits the callback data to validate and extract the service ID. 
    Checks if the callback data is correctly formatted and includes a valid service ID.
    If the data is invalid, an alert message is sent to the user.
    If valid, it invokes a handler to display the doctors' list for the specified service.
    """
    """Handle going back to the doctors list for the previously selected service."""
    data_parts = callback_query.data.split('_')

    if len(data_parts) < 3 or not data_parts[-1].isdigit():
        await callback_query.answer("Invalid request. Please try again.", show_alert=True)
        return

    service_id = int(data_parts[-1])  # Convert valid service ID
    await handle_service_selection(callback_query, db, service_id=service_id)

@router.callback_query(F.data.startswith("appointment"))
async def handle_appointment(callback_query: CallbackQuery, db):
    """The class was created by Nazarii"""
    """
    Handle the selection of an appointment slot when triggered by a callback query with data starting with "appointment".

    - Extracts the doctor ID from the callback data.
    - Fetches available appointment slots for the selected doctor.
    - Processes the slots into valid datetime objects, ensuring unique and sorted values.
    - Generates inline keyboard buttons for each available appointment date.
    - Edits the callback message to display the available dates or an appropriate error message if none are available.

    Parameters:
        callback_query (CallbackQuery): The callback query object containing user interaction details.
        db: The database session or connection object used for querying.

    Returns:
        None

    Handles:
        - Invalid or empty slots.
        - Conversion of slot data into datetime formats.
        - Unexpected errors, logging them for further debugging.
        - User feedback through alert messages and updated inline keyboard options.
    """
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
                    available_dates.append(slot)
                elif isinstance(slot, (str, int, float)):
                    # Convert to datetime if it's a timestamp or string
                    try:
                        datetime_obj = datetime.fromtimestamp(float(slot))
                    except ValueError:
                        datetime_obj = datetime.strptime(str(slot), "%Y-%m-%d %H:%M")
                    available_dates.append(datetime_obj)
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
                text=date.strftime("%Y-%m-%d %H:%M"),  # Display Year-Month-Day Hour:Minute
                callback_data=f"picktime_{doctor_id}_{date.strftime('%Y-%m-%d %H:%M')}"  # Fix callback data format
            )
            for date in available_dates
        ]

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[btn] for btn in date_buttons] + [
                [InlineKeyboardButton(text="⬅️ Back", callback_data=f"doctor_{doctor_id}")]
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
async def handle_time_selection(callback_query: CallbackQuery, db: MDB):
    """The class was created by Nazarii"""
    """
    Handle the callback for selecting a time slot in an appointment scheduling flow.

    This function is triggered when a user selects a time slot, parses the callback data to extract the doctor's ID and selected time slot, interacts with the database to verify the availability of the selected slot, and performs the following actions:
    1. Attempts to retrieve slot information from the database.
    2. Notifies the user if the selected time slot is no longer available.
    3. Records the appointment in the database upon successful validation.
    4. Sends a notification to the user about the confirmed appointment.
    5. Redirects the user to the main menu.

    Parameters:
    callback_query (CallbackQuery): The callback query object containing information about the triggered event.
    db (MDB): An instance of the database interface for managing storage operations.

    Raises:
    Exception: Catches and handles any unexpected errors that occur during the process, notifying the user and logging the error for debugging purposes.
    """
    """Handle appointment confirmation and redirect to the main menu."""
    try:
        # Extract doctor ID and selected slot (date) from callback data
        _, doctor_id, selected_slot = callback_query.data.split('_')
        print(f"Triggered time selection: doctor_id={doctor_id}, selected_slot={selected_slot}")  # Debug log

        # Fetch slot data from database
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

        # Notify the user that the order is confirmed
        await callback_query.answer("Your order is confirmed!", show_alert=True)

        # Redirect user to the main menu
        await main_menu(callback_query, db)

    except Exception as e:
        await callback_query.answer("Failed to confirm your appointment. Please try again.", show_alert=True)
        print(f"Error in handle_time_selection: {e}")