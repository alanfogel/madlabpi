import pandas as pd
import os
import glob

def clean_csv_file(file_path):
    df = pd.read_csv(file_path, skiprows=1)  # Skip only the title line
    datetime_col = [col for col in df.columns if "Date Time" in col][0]
    df[datetime_col] = pd.to_datetime(df[datetime_col], format="%m/%d/%y %I:%M:%S %p")
    channel_cols = [col for col in df.columns if col.startswith("DTA")]
    df_long = df.melt(id_vars=[datetime_col], value_vars=channel_cols,
                      var_name="channel", value_name="value")
    df_long.rename(columns={datetime_col: "datetime"}, inplace=True)
    return df_long


def clean_txt_file(file_path, channel_name):
    df = pd.read_csv(file_path, header=None, names=["datetime", "value"],
                     parse_dates=["datetime"], sep=r",\s*", engine="python")
    df["channel"] = channel_name
    return df

def main():
    # Clean CSV file with multiple channels
    df_csv = clean_csv_file("Dorval_Test12.csv")
# Find and clean all TXT files in the folder
    txt_files = glob.glob("*.txt")
    df_txt_list = []
    for file in txt_files:
        base = os.path.basename(file)
        channel_name = base.split(".")[0]  # Use filename without extension
        df_txt = clean_txt_file(file, channel_name)
        df_txt_list.append(df_txt)

    # Combine everything
    df_all = pd.concat([df_csv] + df_txt_list, ignore_index=True)
    df_all["datetime"] = pd.to_datetime(df_all["datetime"], errors="coerce")
    df_all.sort_values("datetime", inplace=True)
    df_all.to_csv("cleaned_combined.csv", index=False)

    print("Rows per channel:")
    print(df_all.groupby("channel").size())

    # # Clean the two text files, give unique channel names
    # df_txt1 = clean_txt_file("channel_0_2025-05-23.txt", "channel_0")
    # df_txt2 = clean_txt_file("TESTchannel_0_2025-05-23.txt", "TESTchannel_0")
    # # df_txt1 = clean_txt_file("channel_1_2025-05-23.txt", "channel_1")
    # # df_txt2 = clean_txt_file("TESTchannel_1_2025-05-23.txt", "TESTchannel_1")


    # # Combine all dataframes into one long format
    # df_all = pd.concat([df_csv, df_txt1, df_txt2], ignore_index=True)
    # df_all["datetime"] = pd.to_datetime(df_all["datetime"], errors="coerce")

    # # Sort by datetime if you want
    # df_all.sort_values("datetime", inplace=True)

    # # Save combined cleaned data to CSV
    # df_all.to_csv("cleaned_combined.csv", index=False)

    # print("Rows per channel:")
    # print(df_all.groupby("channel").size())

if __name__ == "__main__":
    main()
