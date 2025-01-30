import random
from aiogram.types import DateTime
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB
import os

cluster = AsyncIOMotorClient(MONGO_DB)
db = cluster['UpdDatabase']

# Folder to store PDF files
PDF_FOLDER = "pdfs"
os.makedirs(PDF_FOLDER, exist_ok=True)

ROOT_FOLDER = "./"  # Save to the current directory (root)

# Function to generate random medical test results
def generate_medical_tests_results_and_return_it():
    """The function was created by Nazarii"""
    """
    Generates a dictionary containing simulated medical test results for CBC, Biochemistry, and Hormones.

    random_value(normal_range, abnormal_range, probability)
        Generates a random value based on a given normal and abnormal range, with a specified probability favoring the normal range.

    Returns:
        A dictionary with the following structure:
            - "CBC": Complete Blood Count with Hemoglobin, White Blood Cells, and Platelets.
            - "Biochemistry": Includes Glucose, ALT, AST, and Creatinine values.
            - "Hormones": Contains TSH and Vitamin D levels.
    """
    def random_value(normal_range, abnormal_range, probability=0.7):
        """Chooses a value from the normal or abnormal range."""
        if random.random() < probability:
            return round(random.uniform(*normal_range), 2)  # Normal range
        return round(random.uniform(*abnormal_range), 2)  # Abnormal range

    return {
        "CBC": {  # Complete Blood Count
            "Hemoglobin": random_value((120, 160), (90, 190)),  # g/L
            "White Blood Cells": random_value((4.0, 9.0), (2.0, 15.0)),  # *10^9/L
            "Platelets": random_value((150, 400), (90, 600)),  # *10^9/L
        },
        "Biochemistry": {
            "Glucose": random_value((3.9, 5.5), (2.5, 10.0)),  # mmol/L
            "ALT": random_value((7, 40), (41, 120)),  # U/L
            "AST": random_value((10, 40), (41, 100)),  # U/L
            "Creatinine": random_value((60, 110), (30, 200)),  # µmol/L
        },
        "Hormones": {
            "TSH": random_value((0.4, 4.0), (0.1, 10.0)),  # µIU/mL
            "Vitamin D": random_value((30, 100), (10, 150)),  # ng/mL
        }
    }

async def make_a_med_test_record(user_id, test_results):
    """The function was created by Nazarii"""
    """
    Inserts medical test results into the MongoDB database for a given user.

    Parameters:
    user_id (str): The ID of the user whose test results are being recorded.
    test_results (dict): A dictionary containing the medical test results.

    Behavior:
    This asynchronous function attempts to insert a record into the "test_results" collection
    within the MongoDB database. The inserted document includes the user's ID, current date 
    and time, and the provided test results. If the insertion is successful, a confirmation
    message is printed to the console. If an error occurs during the insertion, an error message
    with information about the exception is printed to the console.

    Exceptions:
    Logs any exceptions raised during the database operation.
    """
    try:
        # Insert test results into MongoDB
        await db["test_results"].insert_one({
            "user_id": user_id,
            "dateAndTime": DateTime.now(),
            "results": test_results
        })
        print("✅ Test results recorded successfully.")
    except Exception as e:
        print(f" Error recording results: {e}")

import os
from fpdf import FPDF


def generate_pdf(test_results, filename="med_results.pdf"):
    """The function was created by Nazarii"""
    """
    Generates a PDF document containing medical test results.

    Args:
        test_results (dict): A dictionary containing categories as keys and their corresponding test results as sub-dictionaries. 
                             Each sub-dictionary contains test names as keys and their respective values.
        filename (str, optional): The name of the output PDF file. Default is "med_results.pdf".

    Returns:
        str: The file path of the generated PDF.

    Raises:
        ValueError: If the 'filename' argument is not a string.

    Notes:
        - The function creates a PDF in the current working directory.
        - Test results are organized by categories, with test names and their values listed under each category.
    """
    # Ensure filename is a string and represents a valid file path
    if not isinstance(filename, str):
        raise ValueError("The 'filename' argument must be a string representing the file path.")

    # Join the file path correctly
    filepath = os.path.join(os.getcwd(), filename)  # Use current working directory to join with filename
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Medical Test Results", ln=True, align='C')

    pdf.ln(10)  # Line break
    for category, tests in test_results.items():
        pdf.cell(200, 10, txt=f"{category}", ln=True)
        for test, value in tests.items():
            pdf.cell(200, 10, txt=f"{test}: {value}", ln=True)
        pdf.ln(5)

    pdf.output(filepath)
    return filepath