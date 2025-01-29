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
    """
    Generates random medical test results with a 70% probability of being within the normal range.
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
    """Record an appointment in the database."""
    try:
        # Insert test results into MongoDB
        await db["test_results"].insert_one({
            "user_id": user_id,
            "dateAndTime": DateTime.now(),
            "results": test_results
        })
        print("✅ Test results recorded successfully.")
    except Exception as e:
        print(f"❌ Error recording results: {e}")

# Function to generate a PDF with the test results
import os
from fpdf import FPDF

import os
from fpdf import FPDF


def generate_pdf(test_results, filename="med_results.pdf"):
    """Generate a PDF file with medical test results."""
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


'''# FastAPI route to serve the PDF files from the root directory
@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    """Serve the PDF file from the root folder."""
    filepath = os.path.join(ROOT_FOLDER, filename)
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type='application/pdf')
    return {"error": "File not found"}'''

# Callback function for generating and sending medical test results
# Example usage

print()
