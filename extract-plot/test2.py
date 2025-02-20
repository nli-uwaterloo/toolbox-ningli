import os
import fitz  # PyMuPDF
import re


def extract_text_from_pdf(pdf_path):
    """Extracts text from all pages of a given PDF file."""
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text


def extract_equipment_details(pattern, text):
    """Extracts details of equipment based on regex pattern."""
    match = pattern.search(text)
    if match:
        equipment_data = {
            "quantity": int(match.group(1)),
            "description": match.group(2),
            "daily_rate": float(match.group(3).replace(",", "")),
            "weekly_rate": float(match.group(4).replace(",", "")),
            "four_week_rate": float(match.group(5).replace(",", "")),
            "amount_charged": float(match.group(6).replace(",", ""))
        }

        # Extract Make, Model, and Serial Number
        make_model_serial_pattern = re.search(
            rf"Make:\s+(\w+)\s+Model:\s+([\w\d-]+)\s+Serial:\s+([\w\d-]+)", text
        )

        if make_model_serial_pattern:
            equipment_data["make"] = make_model_serial_pattern.group(1)
            equipment_data["model"] = make_model_serial_pattern.group(2)
            equipment_data["serial"] = make_model_serial_pattern.group(3)

        return equipment_data
    return None


# Define regex patterns for Excavator and VIB Plate
excavator_pattern = re.compile(
    r"(\d+)\s+[\d-]+\s+EXCAVATOR\s+(\d+#\s+REDUCED\s+TAIL\s+SWING)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)",
    re.IGNORECASE
)

vib_plate_pattern = re.compile(
    r"(\d+)\s+[\d-]+\s+VIB\s+PLATE\s+MEDIUM\s+(\d+-\d+#\s+IMPACT)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)\s+([\d,]+\.\d+)",
    re.IGNORECASE
)

# Path to the PDF file (update this with your actual file path)
pdf_path = "invoice.pdf"
dir = r'C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\ur_invoice_dec2024'
fname = "236784258-006.PDF"
fname = r'236844732-006.PDF'

os.chdir(dir)

# Extract text from the PDF
invoice_text = extract_text_from_pdf(fname)

# Extract details for both equipment
excavator_details = extract_equipment_details(excavator_pattern, invoice_text)
vib_plate_details = extract_equipment_details(vib_plate_pattern, invoice_text)

# Print results
if excavator_details:
    print("Excavator Details:", excavator_details)
else:
    print("Excavator not found.")

if vib_plate_details:
    print("VIB Plate Details:", vib_plate_details)
else:
    print("VIB Plate not found.")
