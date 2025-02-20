import pandas as pd
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Category20
from bokeh.transform import factor_cmap
import os
from datetime import timedelta
# Load the dataset from the uploaded file

# Modified plot function to work with the new out.csv
def plot(dir, fname):
    olddir = os.getcwd()
    os.chdir(dir)

    # Load the dataset
    dataset = pd.read_csv(fname)

    # Sort the data by first_date
    dataset['first_date'] = pd.to_datetime(dataset['first_date'], errors='coerce')
    dataset['last_date'] = pd.to_datetime(dataset['last_date'], errors='coerce')
    dataset = dataset.dropna(subset=['first_date', 'last_date']).reset_index(drop=True)
    dataset = dataset.sort_values(by='first_date').reset_index(drop=True)

    # Enumerate the Y-axis for better visualization
    dataset['y_axis'] = dataset.index + 1  # Enumerated values starting from 1

    # Ensure 'type' column is available and use it for color mapping
    if 'type' not in dataset.columns:
        raise ValueError("The dataset does not have a 'type' column. Please include it in out.csv.")

    # Prepare the labels with detailed information
    dataset['label'] = dataset['name'] + " (Cost: $" + dataset['amount'].astype(str) + ")"

    # Define unique equipment types and assign colors
    equipment_types = list(dataset['type'].unique())
    num_types = len(equipment_types)
    if num_types > 20:
        colors = (Category20[20] * (num_types // 20 + 1))[:num_types]
    else:
        colors = Category20[num_types]

    color_map = factor_cmap('type', palette=colors, factors=equipment_types)

    # Prepare data for Bokeh
    source = ColumnDataSource(dataset)

    # Create Bokeh figure with datetime x-axis
    p = figure(
        title="Equipment Timeline with Costs",
        x_axis_type='datetime',
        height=600,  # Updated for latest Bokeh versions
        width=1500,  # Updated for latest Bokeh versions
        tools="pan,zoom_in,zoom_out,reset,save",
        toolbar_location="above"
    )

    # Plot each equipment's timeline
    p.segment(
        x0='first_date',
        y0='y_axis',
        x1='last_date',
        y1='y_axis',
        source=source,
        line_width=4,
        color=color_map,
        legend_field='type'
    )

    # Add circle markers for start and end dates
    p.circle(
        x='first_date',
        y='y_axis',
        source=source,
        size=8,
        color=color_map,
        legend_field='type'
    )
    p.circle(
        x='last_date',
        y='y_axis',
        source=source,
        size=8,
        color=color_map,
        legend_field='type'
    )

    # Add hover tooltips for better interactivity
    hover = HoverTool()
    hover.tooltips = [
        ("Equipment", "@name"),
        ("Type", "@type"),
        ("Cost", "@amount{$0,0.00}"),
        ("Start Date", "@first_date{%F}"),
        ("End Date", "@last_date{%F}")
    ]
    hover.formatters = {'@first_date': 'datetime', '@last_date': 'datetime'}
    p.add_tools(hover)

    # Add labels to the right of the last_date
    for i, row in dataset.iterrows():
        p.text(
            x=[row['last_date']],
            y=[row['y_axis']],
            text=[row['label']],
            text_align="left",
            text_baseline="middle",
            text_font_size="10pt",
            x_offset=10  # Add some space to the right
        )

    # Calculate the maximum end date
    max_date = dataset['last_date'].max()

    # Add padding only to the right side by extending the end of the x_range
    padding_days = 50  # Adjust the number of days for padding
    p.x_range.end = max_date + timedelta(days=padding_days)

    # Axis labels and title
    p.xaxis.axis_label = "Date Range (Start Date to End Date)"
    p.yaxis.axis_label = "Equipment Order (Sorted by Start Date)"

    # Place the legend on the right side
    p.legend.title = "Equipment Types"
    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    p.add_layout(p.legend[0], 'right')

    # Output and show the plot
    output_file("equipment_timeline_bokeh_type_color_out.html")
    show(p)
    os.chdir(olddir)

dir = r"C:\Users\ginse\OneDrive\Documents\Tools\toolbox-ningli\extract-plot\output"
fname = r"out.csv"
plot(dir, fname)