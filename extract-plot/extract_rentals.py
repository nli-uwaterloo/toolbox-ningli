import os
import pandas as pd
import re
import rental_class as rc
import extract_functions_ur as ur
import copy
from datetime import datetime

def read_sunbelt(dir, invoice_data):
    fname = '155311570-1.pdf'  # sunbelt
    read_invoice_sunbelt(dir, fname, invoice_data)

def read_invoice_sunbelt(dir,fname, invoice_data):
    i = 0

def read_ur(dir, invoice_data):
    filenames = list_files_in_directory(dir)
    invoices = {}
    for fname in filenames:
        invoice_data = read_invoice_ur(dir, fname, invoice_data)
        invoice_number = invoice_data["Invoice Number"]
        invoices[invoice_number] = copy.deepcopy(invoice_data)
        i = 0
        # invoices[invoice_number]['Rental Items'] = invoice_data['Rental Items']
    return invoices

def read_invoice_ur(dir, fname, invoice_data):
    # Extract text from the PDF
    invoice_data = ur.extract_text_from_pdf(dir, fname, invoice_data)
    return invoice_data

def list_files_in_directory(dir):
    try:
        files = [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]
        return files
    except FileNotFoundError:
        print(f"Error: Directory '{dir}' not found.")
        return []
    except PermissionError:
        print(f"Error: Permission denied to access '{dir}'.")
        return []


"""
Create objects for the following class:

1. Equipment
2. Environmental Change
3. Fuel Charge
4. Pickup/Drop off charge
5. Total Charge
"""
def create_class(invoices):
    invoiceGroupMap = {}
    invoiceMap = {}
    equipmentMap = {}

    for key, invoice_data in invoices.items():
        print("Invoice: ", key)
        # Create individual invoice eg. '236784258-006'
        invoice = rc.Invoice(invoice_data['Invoice Number'],
                             invoice_data['Invoice Date'],
                             invoice_data['Billing Start Date'],
                             invoice_data['Billing End Date'])
        invoice.setTotal(invoice_data['Invoice Amount'])
        invoice.setSubtotal(invoice_data['Subtotal'])
        invoice.setTax(invoice_data['Tax'])
        invoice.setInvoiceGroup(invoice_data['Invoice Group'])
        invoice.setInvoiceGroupNum(invoice_data['Invoice Group Number'])
        invoice.setDateout(invoice_data['Date Out'])
        # 1. Create Equipment using equipment ID (10263593), not the full name (EXCAVATOR 35000-39999#)
        for rental in invoice_data['Rental Items']:
            if rental['equipment_id'] not in equipmentMap:
                print("---Equipment: ", rental["equipment_id"])
                equipment = rc.Equipment(rental['equipment_id'])
                equipment.setName(rental['description'])
                equipment.setDailyRate(rental['daily_rate'])
                equipment.setWeeklyRate(rental['weekly_rate'])
                equipment.setFourWeekRate(rental['four_week_rate'])
                # equipment.setAmount(rental['amount_charged'])
                equipment.addInvoice(invoice_data['Invoice Number'], invoice)
                equipment.setDateout(invoice_data['Date Out'])
                equipment.setFirstdate(invoice_data['Date Out'])
                equipment.setLastdate(invoice_data['Billing End Date'])
                equipmentMap[rental['equipment_id']] = equipment
            else:
                equipmentMap[rental['equipment_id']].addInvoice(invoice_data['Invoice Number'], invoice)
                old_last_date = equipmentMap[rental['equipment_id']].getLastdate()
                new_last_date = invoice_data['Billing End Date']
                if datetime.strptime(new_last_date, "%m/%d/%y") > datetime.strptime(old_last_date, "%m/%d/%y"):
                    equipmentMap[rental['equipment_id']].setLastdate(new_last_date)
            equipmentMap[rental['equipment_id']].setCost(invoice_data['Invoice Number'], float(rental['amount_charged']))
            equipmentMap[rental['equipment_id']].addCost(float(rental['amount_charged']))

        # TODO:
        #   2. Environmental Change
        #   3. Fuel Charge
        #   4. Pickup/Drop off charge
        #   5. Total Charge

        i = 0
    return equipmentMap


# Invoice data structure
invoice_data = {
    "Invoice Number": None,
    "Invoice Amount": 0,
    "Invoice Date": None,
    "Billing Start Date": None,
    "Billing End Date": None,
    "Date Out": None,
    "Rental Items": [],
    "Sales/Miscellaneous Items": [],
    "Environmental Service Amount": 0,
    "Fuel Amount": 0,
    "Subtotal": 0,
    "Tax": 0,
    "Total Amount": 0,
    #"Project Name": None,
    #"Project Address": None,
    #"Job Contact": None,
}

dir = r'C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\ur_invoice'
#dir = r'C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\sunbelt_invoice'
fname = "236899786-005.PDF" #ur
#fname = '155311570-1.pdf' #sunbelt
invoiceGroupMap = {}
equipmentMap = {} # key: id, val: Equipment
invoices_ur = read_ur(dir, invoice_data)
# read_sunbelt(dir, invoice_data)
equipmentMap = create_class(invoices_ur)


#group = rc.InvoiceGroup(invoice_data["Invoice Group"])
i = 0