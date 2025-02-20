import fitz  # PyMuPDF
import re
import os
from datetime import datetime

def extract_text_from_pdf(dir, fname, invoice_data):
    """Extracts text from all pages of a given PDF file."""
    olddir = os.getcwd()
    os.chdir(dir)
    doc = fitz.open(fname)
    text = "\n".join([page.get_text("text") for page in doc])

    # Extract invoice details
    extract_invoice_details(text, invoice_data)

    # Extract rental items
    extract_rental_items(text, invoice_data)

    # Extract sales/miscellaneous items
    extract_sales_misc_items(text, invoice_data)

    # Extract cost information
    extract_costs(text, invoice_data)

    # Extract project name
    # extract_project_name(text, invoice_data)

    # Extract project site address
    # extract_project_address(text, invoice_data)

    os.chdir(olddir)
    return invoice_data

def extract_invoice_details(text, invoice_data):
    """Extracts general invoice details using regex patterns."""
    invoice_data["Invoice Number"] = re.search(r"#\s*(\d{9}-\d{3})", text)
    invoice_data["Invoice Amount"] = re.search(r"Invoice Amount:\s*\$([\d,]+\.\d+)", text)
    invoice_data["Billing Start Date"] = re.search(r"Billing period:.*?From\s*([\d/]+)", text)
    invoice_data["Billing End Date"] = re.search(r"Thru\s*([\d/]+)", text)
    invoice_data["Job Contact"] = re.search(r"CONTACT:\s*(.+)", text)
    #invoice_data["Customer"] = re.search(r"Customer\s*#\s*:\s*(\d+)", text)

    # Clean extracted values
    for key, match in invoice_data.items():
        # print(key)
        if (isinstance(match, str)
                or match is None
                or isinstance(match, list)
                or isinstance(match, int)
                or isinstance(match, float)
                or isinstance(match, datetime)):
            invoice_data[key] = match
        else:
            invoice_data[key] = match.group(1).strip()

    # Seperate Invoice Number "236844732-006" into Group and Group #
    invoicetext = invoice_data["Invoice Number"]
    m = re.match(r"(\d+)-(\d+)", invoicetext)
    if m:
        invoice_data['Invoice Group'] = m.group(1)
        invoice_data['Invoice Group Number'] = m.group(2)

    # Search for Invoice Date
    start_keyword = "Invoice Date"
    invoice_date = find_nth_date_between(text, start_keyword, 1)
    if invoice_date:
        invoice_data["Invoice Date"] = invoice_date

    # Search for Date Out
    start_keyword = "Date Out"
    dateout = find_nth_date_between(text, start_keyword, 2)
    if dateout:
        invoice_data["Date Out"] = dateout

    # Resolve Date issue
    if isinstance(invoice_data["Invoice Date"], str):
        invoice_data["Invoice Date"] = datetime.strptime(invoice_data["Invoice Date"], "%m/%d/%y")
    if isinstance(invoice_data["Date Out"], str):
        invoice_data["Date Out"] = datetime.strptime(invoice_data["Date Out"], "%m/%d/%y")

    if invoice_data["Billing Start Date"] is None:
        invoice_data["Billing Start Date"] = invoice_data["Date Out"]
    elif isinstance(invoice_data["Billing Start Date"], str):
        invoice_data["Billing Start Date"] = datetime.strptime(invoice_data["Billing Start Date"],"%m/%d/%y")

    if invoice_data["Billing End Date"] is None:
        invoice_data["Billing End Date"] = invoice_data["Date Out"]
    elif isinstance(invoice_data["Billing End Date"], str):
        invoice_data["Billing End Date"] = datetime.strptime(invoice_data["Billing End Date"],"%m/%d/%y")

    i = 0

def find_nth_date_between(text, start_keyword, n):
    """
    Finds the nth date appearing after the given start_keyword
    and extracts the nth date between these occurrences.

    :param text: The input text to search.
    :param start_keyword: The keyword to start searching from.
    :param n: The position (1-based index) of the date to find after the first occurrence.
    :return: The nth date found between the start keyword and the next date occurrence.
    """
    start_index = text.find(start_keyword)

    if start_index == -1:
        return None  # Return None if start keyword is not found

    # Extract text after the start keyword
    text_after_start = text[start_index:]

    # Regex pattern to find all dates in MM/DD/YY format
    date_pattern = r"(\d{2}/\d{2}/\d{2})"
    dates = re.findall(date_pattern, text_after_start)

    if len(dates) < n + 1:  # Need at least (n+1) dates to find the nth one between occurrences
        return None

    # Get the nth date (1-based index)
    return dates[n - 1] if n > 0 else None

def extract_rental_items(text, invoice_data):
    """
    Extracts rental items including equipment numbers, descriptions, and rental rates.

    :param text: The input invoice text.
    :return: A list of dictionaries containing rental item details.
    """
    rental_items = []

    # Regex pattern to match rental items including equipment numbers
    pattern = re.compile(
        r"\s+(\d+)\s+"  # Qty
        r"((?:\d{8}|\d{3}\/\d{4}|N\d{2}-\d{4}|[A-Z]{4}\d{4}))\s+"  # Equipment (8 character constraint)
        r"([A-Z0-9-\"'#\s]+?)\s+"                 # Description
        r"((?:\d{1,4},?\d{0,4}\.\d{2})|N/C|)\s*"  # Day
        r"((?:\d{1,4},?\d{0,4}\.\d{2})|N/C|)\s*"  # week
        r"((?:\d{1,4},?\d{0,4}\.\d{2})|N/C|)\s*"  # 5 Week
        r"((?:\d{1,4},?\d{0,4}\.\d{2})|N/C)"      # Amount
        , re.IGNORECASE | re.MULTILINE
    )
    matches = pattern.findall(text)

    for match_uncleaned in matches:
        # replace N/C with ""
        match = tuple('' if value == 'N/C' else value for value in match_uncleaned)
        rental_items.append({
            "quantity": int(match[0]),
            "equipment_id": match[1],  # Extracted Equipment Number (e.g., 11861988)
            "description": match[2].strip(),
            "minimum": float(0), # UR doesnt include any minimum charge so make it 0
            "daily_rate": float(match[3].replace(",", "")) if match[3] else 0.00,
            "weekly_rate": float(match[4].replace(",", "")) if match[4] else 0.00,
            "four_week_rate": float(match[5].replace(",", "")) if match[5] else 0.00,
            "amount_charged": float(match[6].replace(",", "")) if match[6] else 0.00
        })
        i = 0

    invoice_data['Rental Items'] = rental_items

def extract_sales_misc_items(text, invoice_data):
    """
    Extracts Qty, Item, Price, Unit of Measure, and Extended Amount from invoice text.

    :param text: The input invoice text.
    :return: A list of dictionaries containing sales/miscellaneous item details.
    """
    sales_misc_items = []

    # Regex pattern to match the required fields
    pattern = re.compile(
        r"(\d+)\s+([A-Z\s\/\d-]+)(?:\s+\[.*?\])?\s+([\d,]+\.\d+)\s+([A-Z]+)\s+([\d,]+\.\d+)",
        re.IGNORECASE
    )
    # (\d+)\s+([A-Z\s\/\d-]+)\s+\[.*?\]\s+([\d,]+\.\d+)\s+([A-Z]+)\s+([\d,]+\.\d+)
    matches = pattern.findall(text)

    for match in matches:
        sales_misc_items.append({
            "Qty": int(match[0]),
            "Item": match[1].strip(),
            "Price": float(match[2].replace(",", "")),
            "Unit of Measure": match[3].strip(),
            "Extended Amt": float(match[4].replace(",", ""))
        })
    invoice_data["Sales/Miscellaneous Items"] = sales_misc_items

def extract_costs(text, invoice_data):
    """Extracts subtotal, tax, and total amounts."""
    invoice_data["Subtotal"] = re.search(r"Agreement Subtotal:\s+([\d,]+\.\d+)", text)
    invoice_data["Tax"] = re.search(r"Tax:\s+([\d,]+\.\d+)", text)
    invoice_data["Total Amount"] = re.search(r"Total:\s+([\d,]+\.\d+)", text)
    # label = "Total"
    # pattern = rf"{re.escape(label)}:\s+([\d,]+\.\d+)"
    # s = re.search(pattern,text)
    # Clean extracted values
    for key in ["Subtotal", "Tax", "Total Amount"]:
        if invoice_data[key]:
            f = invoice_data[key].group(1).replace(",", "")
            invoice_data[key] = float(invoice_data[key].group(1).replace(",", ""))
        else:
            invoice_data[key] = 0.0


def extract_project_name(text, invoice_data):
    """
    Extracts the project name that appears immediately after the 'Billing period' line.

    :param text: The input invoice text.
    :return: The extracted project name or None if not found.
    """
    # Regex pattern to find the Billing Period line
    billing_period_pattern = r"Billing period:.*?\n(.+)"

    match = re.search(billing_period_pattern, text, re.IGNORECASE)

    if match:
        project_name = match.group(1).strip()
        invoice_data['Project Name'] = project_name


def extract_project_address(text, invoice_data):
    """
    Extracts the project address, which is found on the 2nd and 3rd lines after the 'Billing period' line.

    :param text: The input invoice text.
    :return: The extracted project address or None if not found.
    """
    # Regex pattern to find the Billing Period line and the next three lines
    billing_period_pattern = r"Billing period:.*?\n(.+)\n(.+)\n(.+)"

    match = re.search(billing_period_pattern, text, re.IGNORECASE)

    if match:
        project_name = match.group(1).strip()  # The first line after Billing Period
        project_address_line1 = match.group(2).strip()  # 2nd line (Address Line 1)
        project_address_line2 = match.group(3).strip()  # 3rd line (Address Line 2)

        project_address = f"{project_address_line1}, {project_address_line2}"
        invoice_data['Project Address'] = project_address