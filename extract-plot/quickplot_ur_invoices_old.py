import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
import numpy as np
import os

# Load and clean the dataset
file_dir = r'C:\Users\ginse\OneDrive\Documents\SG\Projects\Swiftwater - Narenco\UR'
file_path = 'Swiftwater_SGI_equipmentUR_2.csv'  # Update this to your file path

# Read data
os.chdir(file_dir)
dataset = pd.read_csv(file_path)

# Convert date columns to datetime format
dataset['First Date'] = pd.to_datetime(dataset['First Date'])
dataset['Last Date'] = pd.to_datetime(dataset['Last Date'])

# Clean "Idle Cost After Oct 18 with reduced equipment" and "Monthly_Charge" columns
dataset['Idle Cost After Oct 18 with reduced equipment'] = pd.to_numeric(
    dataset['Idle Cost After Oct 18 with reduced equipment'].replace('[\$,]', '', regex=True), errors='coerce'
)
dataset['Monthly_Charge'] = pd.to_numeric(
    dataset['Monthly_Charge'].replace('[\$,]', '', regex=True), errors='coerce'
)

# Drop rows with NaN values in critical columns after cleaning
dataset_cleaned = dataset.dropna(
    subset=['Monthly_Charge', 'Idle Cost After Oct 18 with reduced equipment', 'First Date', 'Last Date']
)

# Define a color map based on unique equipment types
equipment_types = dataset_cleaned['Item - Short'].unique()
colors = cm.tab20(np.linspace(0, 1, len(equipment_types)))
color_map = dict(zip(equipment_types, colors))

# Define special styles for specific categories
special_styles = {
    "TOTAL": ("red", "s"),  # Square marker
    "Tax": ("orange", "s"),
    "Fuel": ("blue", "s"),
    "Delivery/Pickup": ("green", "s"),
    "Environmental": ("purple", "s"),
}

# Create the plot
fig, ax = plt.subplots(figsize=(14, 8))

for _, row in dataset_cleaned.iterrows():
    line_style = '-' if row['Include'] == 1 else '--'  # Solid line if "Include" is 1, dashed if 0
    color = color_map[row['Item - Short']]  # Default color based on equipment type
    marker_style = 'o' if row['Include'] == 1 else 'x'  # Default marker
    special_marker = None

    # Check for special categories and update marker and color
    for key, (col, mark) in special_styles.items():
        if key in row['Item - Short']:
            color = col
            special_marker = mark

    # Use square markers for special categories
    if special_marker:
        marker_style = special_marker

    # Plot the equipment timeline
    ax.plot(
        [row['First Date'], row['Last Date']],  # X values (date range)
        [row['Eq. Index'], row['Eq. Index']],  # Y values (equipment index)
        color=color,  # Use special color for categories if applicable
        linestyle=line_style,  # Apply line style based on "Include"
        marker=marker_style,  # Apply special marker style if applicable
    )

    # Add labels with bold "TOTAL" and unique symbols
    label = f"{row['Item - Short']} (Idle: ${row['Idle Cost After Oct 18 with reduced equipment']:.2f}, " \
            f"Monthly: ${row['Monthly_Charge']:.2f})"
    if "TOTAL" in row['Item - Short']:
        label = f"**{row['Item - Short']}** (Idle: ${row['Idle Cost After Oct 18 with reduced equipment']:.2f}, " \
                f"Monthly: ${row['Monthly_Charge']:.2f})"

    ax.text(
        row['Last Date'], row['Eq. Index'],  # Position the label near the end of the line
        label,
        fontsize=9, va='center', ha='left', alpha=0.7
    )

# Add a vertical line at Oct 18, 2024
critical_date = pd.to_datetime("2024-10-18")
ax.axvline(critical_date, color='black', linestyle='--', linewidth=1.5, label="Oct 18, 2024")

# Add detailed X and Y axis labels
ax.set_title("Equipment Timeline with Costs", fontsize=16)
ax.set_xlabel("Date Range (Start Date to End Date)", fontsize=12)
ax.set_ylabel("Equipment Index (e.g., Trailer, Skid Steer, etc.)", fontsize=12)

# Format the X-axis to display more labels
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))  # Set major ticks to weekly intervals
ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))  # Add daily minor ticks
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d, %Y'))  # Format X-axis as dates
plt.xticks(fontsize=10, rotation=45)

# Format the Y-axis with minor ticks
ax.yaxis.set_minor_locator(plt.MultipleLocator(1))  # Add minor ticks to Y-axis
plt.yticks(fontsize=10)

# Add a grid for clarity
plt.grid(axis='x', which='both', linestyle='--', alpha=0.5)
plt.grid(axis='y', which='both', linestyle='--', alpha=0.5)

# Add legend for the equipment types
legend_elements = [plt.Line2D([0], [0], color=color_map[e], lw=4, label=e) for e in equipment_types]
ax.legend(handles=legend_elements, fontsize=10, loc='upper left', title="Equipment Types")

# Show the plot
plt.tight_layout()
plt.show()