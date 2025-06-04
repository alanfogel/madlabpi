import pandas as pd
import matplotlib.pyplot as plt

# Load cleaned CSV
df = pd.read_csv("cleaned_combined.csv", parse_dates=["datetime"])

# Define the date range to visualize
start_time = pd.to_datetime("2025-05-24 00:00:00")
end_time   = pd.to_datetime("2025-05-27 23:59:59")

# Filter for the desired time range
df = df[(df["datetime"] >= start_time) & (df["datetime"] <= end_time)]

# Step 1: Normalize all channel names
def normalize_channel_name(name):
    # TESTchannel_0_2025-05-24 → TESTchannel_0
    if "TESTchannel" in name:
        return name.split("_2025")[0]
    if "channel_" in name:
        return name.split("_2025")[0]
    if name.startswith("DTA1"):
        return "Hobo1"
    if name.startswith("DTA2"):
        return "Hobo2"
    if name.startswith("DTA3"):
        return "Hobo3"
    if name.startswith("DTA4"):
        return "Hobo4"
    return name

df["normalized_channel"] = df["channel"].apply(normalize_channel_name)

# Group by datetime and normalized_channel
df_grouped = df.groupby(["datetime", "normalized_channel"])["value"].mean().reset_index()

# Pivot so each normalized channel becomes a column
df_pivot = df_grouped.pivot(index="datetime", columns="normalized_channel", values="value")

# Resample to 1-minute intervals and interpolate
df_pivot = df_pivot.resample("1min").mean().interpolate()

# Drop columns with all NaNs
df_pivot.dropna(axis=1, how="all", inplace=True)

# Set up the plot
fig, ax1 = plt.subplots(figsize=(14, 6))

# Plot TESTchannel_0 on second Y-axis
if "TESTchannel_0" in df_pivot.columns:
    ax2 = ax1.twinx()
    color2 = 'tab:green'
    ax2.plot(df_pivot.index, df_pivot["TESTchannel_0"], label="TESTchannel_0", color=color2)
    ax2.set_ylabel("TESTchannel_0", color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
else:
    print("TESTchannel_0 not found in data.")

# Plot Hobo1 on third Y-axis
if "Hobo1" in df_pivot.columns:
    ax3 = ax1.twinx()
    ax3.spines["right"].set_position(("outward", 60))
    color3 = 'tab:red'
    ax3.plot(df_pivot.index, df_pivot["Hobo1"], label="Hobo1", color=color3)
    ax3.set_ylabel("Hobo1", color=color3)
    ax3.tick_params(axis='y', labelcolor=color3)
else:
    print("Hobo1 not found in data.")

# # Plot Hobo1 on third Y-axis
# if "Hobo2" in df_pivot.columns:
#     ax3 = ax1.twinx()
#     ax3.spines["right"].set_position(("outward", 60))
#     color3 = 'tab:red'
#     ax3.plot(df_pivot.index, df_pivot["Hobo2"], label="Hobo2", color=color3)
#     ax3.set_ylabel("Hobo2", color=color3)
#     ax3.tick_params(axis='y', labelcolor=color3)
# else:
#     print("Hobo2 not found in data.")

# Title and labels
plt.title("Comparison of NON-SPLICED DC3 on PI vs HOBO \n2025-05-24 00:00 to 2025-05-27 23:59:59")
ax1.set_xlabel("Time")
fig.autofmt_xdate()

# Combine legends from all axes
handles, labels = [], []
for ax in fig.axes:
    h, l = ax.get_legend_handles_labels()
    handles += h
    labels += l
plt.legend(handles, labels, loc="upper left")

plt.tight_layout()
plt.show()
