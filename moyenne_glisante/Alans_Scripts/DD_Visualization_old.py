import pandas as pd
import matplotlib.pyplot as plt

# Load your cleaned CSV
df = pd.read_csv("cleaned_combined.csv", parse_dates=["datetime"])

# Filter for the desired time range
start_time = pd.to_datetime("2025-05-23 00:00:00")
end_time = pd.to_datetime("2025-05-27 23:59:59")
df_filtered = df[(df["datetime"] >= start_time) & (df["datetime"] <= end_time)]

# Pivot so each channel becomes a column
df_pivot = df_filtered.pivot(index="datetime", columns="channel", values="value")

# print("------------------------- debugging stuff now -------------------------")

# print("Available datetime range:", df_pivot.index.min(), "to", df_pivot.index.max())

# # Check how many rows remain after filtering
# df_pivot = df_pivot[(df_pivot.index >= start_time) & (df_pivot.index <= end_time)]

# print("Rows after filtering:", len(df_pivot))
# print("Columns available in df_pivot:", df_pivot.columns.tolist())
# # print(df_pivot[["channel_1", "DTA1, UM (LGR S/N: 10530128)"]].head())

# rename_map = {}
# if "DTA1, UM (LGR S/N: 10530128)" in df_pivot.columns:
#     rename_map["DTA1, UM (LGR S/N: 10530128)"] = "Hobo1"
# if "DTA2, UM (LGR S/N: 10530128)" in df_pivot.columns:
#     rename_map["DTA2, UM (LGR S/N: 10530128)"] = "Hobo2"
# df_pivot = df_pivot.rename(columns=rename_map)

# # print(df_pivot[["channel_0", "channel_0_bis", "DTA1, UM (LGR S/N: 10530128)"]].head())
# # print(df_pivot[["channel_1", "channel_1_bis", "DTA1, UM (LGR S/N: 10530128)"]].head())
# # print(df_pivot[["channel_1", "channel_1_bis", "Hobo1"]].head())

# print("------------------------- Done -------------------------")

# Set up the plot
fig, ax1 = plt.subplots(figsize=(14, 6))

# --- Filter and align data ---
# Keep only relevant time range
df_pivot = df_pivot[(df_pivot.index >= start_time) & (df_pivot.index <= end_time)]

# Rename columns for clarity
df_pivot = df_pivot.rename(columns={
    # "channel_0": "channel_0",
    "channel_0_bis": "TESTchannel_0",
    # "channel_1": "channel_1",
    # "channel_1_bis": "TESTchannel_1",
    "DTA1, UM (LGR S/N: 10530128)": "Hobo1"
    # "DTA2, UM (LGR S/N: 10530128)": "Hobo2"
})

# Resample all data to 1-minute intervals and interpolate missing values
df_pivot = df_pivot.resample("1T").mean().interpolate()


# --- Plotting ---
# Normalize channel names by stripping date suffixes (e.g., _2025-05-23)
df["normalized_channel"] = df["channel"].str.extract(r"(channel_\d+|TESTchannel_\d+|Hobo\d+)", expand=False)
df = df.dropna(subset=["normalized_channel"])

# Group by datetime and normalized_channel, taking the mean in case of duplicates
df_grouped = df.groupby(["datetime", "normalized_channel"])["value"].mean().reset_index()

# Pivot so each normalized channel becomes a column
df_pivot = df_grouped.pivot(index="datetime", columns="normalized_channel", values="value")

# Rename long HOBO column names to short ones
rename_map = {}
for i in range(1, 5):  # Adjust range if more DTA channels exist
    long_name = f"DTA{i}, UM (LGR S/N: 10530128)"
    short_name = f"Hobo{i}"
    if long_name in df_pivot.columns:
        rename_map[long_name] = short_name

df_pivot = df_pivot.rename(columns=rename_map)
# Optional: sort and clean
df_pivot.sort_index(inplace=True)
df_pivot.dropna(axis=1, how="all", inplace=True)

df_pivot = df_pivot.resample("1min").mean().interpolate()




# Plot channel_0 on ax1
# color1 = 'tab:blue'
# ax1.plot(df_pivot.index, df_pivot["channel_0"], label="channel_0", color=color1)
# # ax1.plot(df_pivot.index, df_pivot["channel_1"], label="channel_1", color=color1)
# ax1.tick_params(axis='y', labelcolor=color1)

# Create a second y-axis sharing the same x-axis
ax2 = ax1.twinx()
color2 = 'tab:green'
ax2.plot(df_pivot.index, df_pivot["TESTchannel_0"], label="TESTchannel_0", color=color2)
# ax2.plot(df_pivot.index, df_pivot["TESTchannel_1"], label="TESTchannel_1", color=color2)
ax2.tick_params(axis='y', labelcolor=color2)

# Create a third y-axis
ax3 = ax1.twinx()
color3 = 'tab:red'
ax3.spines["right"].set_position(("outward", 60))  # move third axis to the right
ax3.plot(df_pivot.index, df_pivot["Hobo1"], label="Hobo1", color=color3)
# ax3.plot(df_pivot.index, df_pivot["Hobo2"], label="Hobo2", color=color3)
ax3.tick_params(axis='y', labelcolor=color3)


# Y-axis labels
# ax1.set_ylabel("channel_0", color=color1)
ax2.set_ylabel("TESTchannel_0", color=color2)
# ax1.set_ylabel("channel_1", color=color1)
# ax2.set_ylabel("TESTchannel_1", color=color2)
ax3.set_ylabel("Hobo1", color=color3)
# ax3.set_ylabel("Hobo2", color=color3)

# Title and X-axis label
# plt.title("Comparison of Channels vs DTA1\n2025-05-23 00:00 to 23:59")
plt.title("Comparison of DC2 on PI vs HOBO DC3\n2025-05-23 00:00 to 2025-05-27 23:59:59")
ax1.set_xlabel("Time")

# Optional: format x-axis labels for better readability
fig.autofmt_xdate()

# Combine legends from all axes
# lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
lines_3, labels_3 = ax3.get_legend_handles_labels()
# plt.legend(lines_1 + lines_2 + lines_3, labels_1 + labels_2 + labels_3, loc="upper left")
plt.legend(lines_2 + lines_3, labels_2 + labels_3, loc="upper left")

plt.tight_layout()
plt.show()