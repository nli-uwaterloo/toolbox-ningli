import os
import pandas as pd
import re
import rental_class as rc
import extract_functions_ur as ur
import copy
from datetime import datetime
import csv

def read_invoice_sunbelt(dir,fname, invoice_data):
    # Extract text from the PDF
    invoice_data = ur.extract_text_from_pdf_sunbelt(dir, fname, invoice_data)
    return invoice_data

def read_invoice_ur(dir, fname, invoice_data):
    # Extract text from the PDF
    invoice_data = ur.extract_text_from_pdf_ur(dir, fname, invoice_data)
    return invoice_data

def read_sunbelt(dir, invoice_data):
    filenames = list_files_in_directory(dir)
    invoices = {}
    for fname in filenames:
        invoice_data = read_invoice_sunbelt(dir, fname, invoice_data)
        invoice_number = invoice_data["Invoice Number"]
        invoices[invoice_number] = copy.deepcopy(invoice_data)
    return invoices

def read_ur(dir, invoice_data):
    filenames = list_files_in_directory(dir)
    invoices = {}
    for fname in filenames:
        invoice_data = read_invoice_ur(dir, fname, invoice_data)
        invoice_number = invoice_data["Invoice Number"]
        invoices[invoice_number] = copy.deepcopy(invoice_data)
    return invoices

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
    equipmentMap = {}
    environmental = 0.0
    fuel = 0.0
    pickup_dropoff = 0.0
    tax = 0.0
    total = 0.0
    project_last_date = datetime.strptime("01/01/70", "%m/%d/%y")

    # Iterate through all invoices
    for key, invoice_data in invoices.items():
        print("Invoice: ", key)
        # Create individual invoice eg. '236784258-006'
        invoice = rc.Invoice(invoice_data['Invoice Number'],
                             invoice_data['Invoice Date'],
                             invoice_data['Billing Start Date'],
                             invoice_data['Billing End Date'])
        invoice.setSubtotal(invoice_data['Subtotal'])
        invoice.setTax(invoice_data['Tax'])
        invoice.setTotal(invoice_data['Invoice Amount'])
        invoice.setInvoiceGroup(invoice_data['Invoice Group'])
        invoice.setInvoiceGroupNum(invoice_data['Invoice Group Number'])
        invoice.setDateout(invoice_data['Date Out'])
        # update charges
        tax += invoice_data['Tax']
        if isinstance(invoice_data['Invoice Amount'], float):
            total += invoice_data['Invoice Amount']
        else:
            total += float(invoice_data['Invoice Amount'].replace(',', ''))

        # Determine Environmental Service, Fuel, and Pickup/Drop off charge
        for i in invoice_data["Sales/Miscellaneous Items"]:
            if i['Item'] == 'ENVIRONMENTAL SERVICE CHARGE':
                invoice.setEnvironmentalService(i['Extended Amt'])
                environmental += i['Extended Amt']
            if 'FUEL' in i['Item'] or 'DIESEL' in i['Item']:
                invoice.addFuel(i['Extended Amt'])
                fuel += i['Extended Amt']
            if i['Item'] == 'DELIVERY CHARGE' or i['Item'] == 'PICKUP CHARGE':
                invoice.addPickupDropff(i['Extended Amt'])
                pickup_dropoff += i['Extended Amt']

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
                equipment.setInvoiceGroup(invoice_data['Invoice Group'])
                equipment.setType(get_equipment_type_ur(rental['description']))
                equipmentMap[rental['equipment_id']] = equipment
            else:
                equipmentMap[rental['equipment_id']].addInvoice(invoice_data['Invoice Number'], invoice)
                old_last_date = equipmentMap[rental['equipment_id']].getLastdate()
                new_last_date = invoice_data['Billing End Date']
                if new_last_date > old_last_date:
                    equipmentMap[rental['equipment_id']].setLastdate(new_last_date)
                if new_last_date > project_last_date:
                    project_last_date = new_last_date
            # update -
            equipmentMap[rental['equipment_id']].setCost(invoice_data['Invoice Number'], float(rental['amount_charged']))
            equipmentMap[rental['equipment_id']].addCost(float(rental['amount_charged']))

    # Initialize for service charge classes using Equipment class
    # for consistent output format
    equipmentMap['Environmental'] = rc.Equipment("00000001")
    equipmentMap['Fuel'] = rc.Equipment("00000002")
    equipmentMap['Pickup_dropoff'] = rc.Equipment("00000003")
    equipmentMap['Tax'] = rc.Equipment("00000004")
    equipmentMap['Total'] = rc.Equipment("00000005")
    equipmentMap['Environmental'].setName('Environmental')
    equipmentMap['Fuel'].setName('Fuel')
    equipmentMap['Pickup_dropoff'].setName('Pickup_dropoff')
    equipmentMap['Tax'].setName('Tax')
    equipmentMap['Total'].setName('Total')
    equipmentMap['Environmental'].setInvoiceGroup('000000000')
    equipmentMap['Fuel'].setInvoiceGroup('000000000')
    equipmentMap['Pickup_dropoff'].setInvoiceGroup('000000000')
    equipmentMap['Tax'].setInvoiceGroup('000000000')
    equipmentMap['Total'].setInvoiceGroup('000000000')
    equipmentMap['Environmental'].setAmount(environmental)
    equipmentMap['Fuel'].setAmount(fuel)
    equipmentMap['Pickup_dropoff'].setAmount(pickup_dropoff)
    equipmentMap['Tax'].setAmount(tax)
    equipmentMap['Total'].setAmount(total)
    project_last_date = project_last_date
    equipmentMap['Environmental'].setFirstdate(project_last_date)
    equipmentMap['Fuel'].setFirstdate(project_last_date)
    equipmentMap['Pickup_dropoff'].setFirstdate(project_last_date)
    equipmentMap['Tax'].setFirstdate(project_last_date)
    equipmentMap['Total'].setFirstdate(project_last_date)
    equipmentMap['Environmental'].setLastdate(project_last_date)
    equipmentMap['Fuel'].setLastdate(project_last_date)
    equipmentMap['Pickup_dropoff'].setLastdate(project_last_date)
    equipmentMap['Tax'].setLastdate(project_last_date)
    equipmentMap['Total'].setLastdate(project_last_date)
    equipmentMap['Environmental'].setType("Charges")
    equipmentMap['Fuel'].setType("Charges")
    equipmentMap['Pickup_dropoff'].setType("Charges")
    equipmentMap['Tax'].setType("Charges")
    equipmentMap['Total'].setType("Charges")
    return equipmentMap

"""
Header
["id","name", "type" ,"first_date","last_date","invoice_group","amount"]
"""
def write_csv(dir, fname, map):
    olddir = os.getcwd()
    os.chdir(dir)
    with open(fname, mode='w', newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id","name", "type","first_date","last_date","invoice_group","amount"])
        #
        for k, v in map.items():
            row = [v.getId(), v.getName(), v.getType(), v.getFirstDate().date(),
                              v.getLastDate().date(), v.getInvoiceGroup(), v.getAmount()]
            writer.writerow(row)
    os.chdir(olddir)
    return

"""
Return equipment type for given equipment Full Name as listed in invoice

:param full name of equipment appearing in invoice
:return equipment type. If new type, return "other"
"""
def get_equipment_type_ur(name):

    map = {
        "AIR HOSE 2\" X 50'": "Air Hose",
        "BACKHOE BUCKET 24\"": "Excavator bucket",
        "BACKHOE BUCKET 36\"": "Excavator bucket",
        "COMPRESSOR 350-450 CFM 150 PSI T4": "Compressor",
        "DELIVERY CHARGE": "Misc Charge",
        "DIESEL FUEL": "Fuel",
        "DYED DIESEL": "Fuel",
        "ENVIRONMENTAL SERVICE CHARGE": "Misc Charge",
        "EXCAVATOR 19000#": "Mini Excavator",
        "EXCAVATOR 19000# REDUCED TAIL SWING": "Mini Excavator",
        "EXCAVATOR 25000-29999#": "Excavator",
        "EXCAVATOR 35000-39999": "Excavator",
        "EXCAVATOR 35000-39999#": "Excavator",
        "EXCAVATOR BREAKER 3000-3500#": "Rock Hammer",
        "EXCAVATOR BUCKET 30\"": "Excavator bucket",
        "EXCAVATOR BUCKET 36\"": "Excavator bucket",
        "EXCAVATOR BUCKET 42\"": "Excavator bucket",
        "EXCAVATOR BUCKET 48\"": "Excavator bucket",
        "FORKLIFT 6' FORKS": "Telehandler",
        "FORKLIFT VARIABLE REACH 12000# 53'-69'": "Telehandler Fork",
        "Fuel": "Fuel",
        "PICKUP CHARGE": "Misc Charge",
        "POST DRIVER AIR": "Post Driver",
        "ROLLER 24-33\" WALKBEHIND PAD": "Trench roller",
        "SKID STEER FORK ATTACHMENT HEAVY DUTY": "Skid steer",
        "SKID STEER TRACK LOADER": "Skid steer",
        "SKID STEER TRACK LOADER 2400-2799#": "Skid steer",
        "SKID STEER TRACK LOADER 2800-3399#": "Skid steer",
        "SKID STEER TRACK LOADER 3400# AND OVER": "Skid steer",
        "TRAILER EQUIPMENT 14-22' TANDEM AXLE": "Trailer",
        "UTV 4WD DSL 4SEAT CAB": "Buggy",
        "UTV 4WD GAS 2SEAT CAB": "Buggy",
        "VIB PLATE MEDIUM 3000-5000#": "Plate Tamper",
        "VIB PLATE MEDIUM 3000-5000# IMPACT": "Plate Tamper"
    }
    if name in map:
        return map[name]
    else:
        return "other"

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
    "Pickup/Dropoff Amount": 0,
    "Sales/Misc Subtotal": 0,
    "Subtotal": 0,
    "Tax": 0,
    "Total Amount": 0,
    #"Project Name": None,
}

in_dir = r'C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\ur_invoice_all'
in_dir = r'C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\sunbelt_invoice_all'
out_dir = r"C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\output"
invoiceGroupMap = {}
equipmentMap = {} # key: id, val: Equipment
#invoices = read_ur(in_dir, invoice_data)
invoices = read_sunbelt(in_dir, invoice_data)
equipmentMap = create_class(invoices)
write_csv(out_dir,"out.csv", equipmentMap)
i = 0