import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
file_path = r"C:\Users\ginse\OneDrive\Documents\SG\Projects\Swiftwater - Narenco\Daily Logs/Swiftwater productivity.csv"
df = pd.read_csv(file_path)

# Convert 'Date' to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Apply a rolling average to smooth the data (3-day window)
df_smoothed = df.copy()
df_smoothed['Daily Work Hour'] = df_smoothed['Daily Work Hour'].rolling(window=3, min_periods=1).mean()
df_smoothed['Adjusted % Completion'] = df_smoothed['Adjusted % Completion'].rolling(window=3, min_periods=1).mean()

# Plot the smoothed data with customized colors
fig, ax1 = plt.subplots(figsize=(10, 5))

# Primary y-axis (Mediumpurple for work hours)
ax1.plot(df_smoothed['Date'], df_smoothed['Daily Work Hour'], label='Daily Work Hour (Smoothed)',
         marker='o', markersize=4, color='mediumpurple', alpha=0.8)
ax1.set_ylabel("Hours", color='mediumpurple')
ax1.set_xlabel("Date")
ax1.tick_params(axis='y', labelcolor='mediumpurple')
ax1.legend(loc="upper left", frameon=False)
ax1.grid(True, linestyle='--', alpha=0.4)  # Softer gridlines

# Secondary y-axis for Adjusted % Completion (Olive color)
ax2 = ax1.twinx()
ax2.plot(df_smoothed['Date'], df_smoothed['Adjusted % Completion'],
         label='Adjusted % Completion (Smoothed)', color='olive',
         linestyle='dashed', marker='x', markersize=4, alpha=0.8)
ax2.set_ylabel("Adjusted % Completion", color='olive')
ax2.set_ylim(0, 0.5)  # Set secondary y-axis scale from 0 to 0.5
ax2.tick_params(axis='y', labelcolor='olive')
ax2.legend(loc="upper right", frameon=False)
ax2.grid(True, linestyle='--', alpha=0.4)  # Softer gridlines

plt.title("Swiftwater - Daily Work Hours and Adjusted % Completion", fontsize=12)
plt.xticks(rotation=45)
plt.show()