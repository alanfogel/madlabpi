#!/bin/bash

# --- Upload pictures ---
cd ~/Dropbox-Uploader
./dropbox_uploader.sh upload ~/dendro-pi-main/pictures/* / | grep "file exists with the same hash" > already_uploaded.txt

while IFS= read -r line; do
  FILENAME=$(echo "$line" | cut -d'"' -f 2)
  rm "$FILENAME"
done < already_uploaded.txt


# --- Upload dendrometer data ---
cd ~/Dropbox-Uploader

# Find files that haven't been modified in the last 60 minutes
find ~/dendro_logger/* -mmin +60 > files_to_upload.txt

while IFS= read -r file; do
  # Check if the file still hasn't been modified in the last 60 minutes
  if [ $(find "$file" -mmin +60) ]; then
    ./dropbox_uploader.sh upload "$file" /
    # If the file was uploaded successfully, move it to the backup directory
    mkdir -p ~/dendro_logger/DD_backup
    mv "$file" ~/dendro_logger/DD_backup/
  fi
done < files_to_upload.txt


# --- New logic for dendrometer data ---
# DATA_DIR=~/dendro_logger
# UPLOAD_DIR="/DD_Dorval-#"  # Dropbox directory - CHANGE TO "/DD_Dorval-#"
# DATE=$(date +"%Y-%m-%d")        # Daily timestamp

# # Process each channel
# for CHANNEL in 0 1 2 3; do  
#   INPUT_FILE="${DATA_DIR}/micron_values_channel_${CHANNEL}.txt"
#   DAILY_FILE="${DATA_DIR}/micron_values_channel_${CHANNEL}_${DATE}.txt"
  
#   # Create a daily copy (if data exists)
#   if [ -s "$INPUT_FILE" ]; then
#     cp "$INPUT_FILE" "$DAILY_FILE"
#     ./dropbox_uploader.sh upload "$DAILY_FILE" "$UPLOAD_DIR/"
#     # rm "$DAILY_FILE"  # Remove local daily copy after upload
#     # Instead of removing the daily copy we move it to ~/dendro_logger/DD_backup
#     mkdir -p ~/dendro_logger/DD_backup
#     mv "$DAILY_FILE" ~/dendro_logger/DD_backup/"$(basename "$DAILY_FILE")"
#     # and remove the input file to start fresh
#     rm "$INPUT_FILE"
#   fi
# done