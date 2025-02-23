import re


def extract_rental_items_sunbelt(text, invoice_data):
    lines = text.splitlines()
    equipment_items = []
    current_item = {}

    for i, line in enumerate(lines):
        # Match the main pattern for Rental Items
        match = re.search(
            r"(\d+\.\d{2})\s+([A-Z0-9\-\'\s]+?)\s+(\d+\.\d{2}|N/C)\s+(\d+\.\d{2}|N/C)\s+(\d+\.\d{2}|N/C)\s+(\d+\.\d{2}|N/C)\s+(\d+\.\d{2}|N/C)\s*(\d+\.\d{2}|N/C)?$",
            line, re.IGNORECASE
        )

        if match:
            # Create a rental item dictionary
            current_item = {
                "Quantity": match.group(1),
                "Description": match.group(2).strip(),
                "Min": match.group(3) if match.group(3) else "N/A",
                "Daily Rate": match.group(4) if match.group(4) else "N/A",
                "Weekly Rate": match.group(5) if match.group(5) else "N/A",
                "Four Week Rate": match.group(6) if match.group(6) else "N/A",
                "Rate": match.group(7) if match.group(7) else "N/A",
                "Amount": match.group(8) if match.group(8) else "N/A",
                "Equipment ID": None  # Will be populated from next lines
            }

            # Check the next line for Equipment ID
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                equipment_id_match = re.search(r"(\b[A-Z]{2}\d{4,}\b|\b\d{7,}\b)", next_line)
                if equipment_id_match:
                    current_item["Equipment ID"] = equipment_id_match.group(1)

            equipment_items.append(current_item)

    # Add to invoice_data
    invoice_data["Rental Items"] = equipment_items


# Example Text
text = """
. QTY EQUIPMENT # Min Day Week 4 Week Amount
.
1.00 10K 55' CAB TELEHANDLER FORKLIFT 680.00 680.00 1685.00 3200.00 3200.00
IA2986 Make: SKYJACK Model: SJ1056TH Ser #: 87310272
HR OUT: 1907.753 HR IN: 1911.694 TOTAL: 3.941
#6' forks
long forks on it
1.00 LONG FORKS SET OF 2 - TELEHANDLERS N/C
Rental Sub-total: 3200.00

. QTY EQUIPMENT # Min Day Week 4 Week Amount
.
1.00 2800-3200LB TRACK SKIDSTEER CAB 525.00 525.00 1525.00 3345.00 3345.00
10018499 Make: BOBCAT Model: T740 Ser #: B3CA14001
HR OUT: 2653.700 HR IN: TOTAL: 2653.700
#IF ENCLOSED MUST HAVE AC, CAN BE OPEN
1.00 PALLET FORKS - LARGE SKID 45.00 45.00 175.00 350.00 350.00
10640717 Make: ARROW Model: 503150-4-48-2 Ser #: 82707
1.00 SKIDSTEER LOADER BUCKET N/C
# TOOTH BUCKET
Rental Sub-total: 3695.00

. QTY EQUIPMENT # Min Day Week 4 Week Amount
.
1.00 UTILITY VEHICLE 4 SEAT 4WD GAS 265.00 265.00 325.00 680.00 680.00
10658460 Make: KAWASAKI Model: 4010 TRANS Ser #: JK1ATCB13PB502450
HR OUT: 335.000 HR IN: 335.041 TOTAL: .041
# DIESEL PREFFER IF AVAILABLE
1.00 UTILITY VEHICLE 4 SEAT 4WD GAS 265.00 265.00 325.00 680.00 680.00
10678386 Make: POLARIS Model: D22P4E99B4 Ser #: 4XAP4E992N8129861
HR OUT: 1666.000 HR IN: TOTAL: 1666.000
# DIESEL PREFFER IF AVAILABLE
1.00 UTILITY VEHICLE 4 SEAT 4WD GAS CAB 265.00 265.00 325.00 680.00 680.00
11032228 Make: KAWASAKI Model: 4010 TRANS Ser #: JK1ATCD17PB501945
HR OUT: 89.000 HR IN: 90.581 TOTAL: 1.581
Rental Sub-total: 2040.00
"""

# Initialize Invoice Data Dictionary
invoice_data = {
    "Rental Items": []
}

# Extract Rental Items
extract_rental_items_sunbelt(text, invoice_data)

# Display Results
print("\nRENTAL ITEMS:")
for item in invoice_data["Rental Items"]:
    print(item)
