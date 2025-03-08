#!/bin/bash
cd ~/Dropbox-Uploader
./dropbox_uploader.sh upload ~/dendro-pi-main/pictures/* / | grep "file exists with the same hash" > already_uploaded.txt

while IFS= read -r line; do
  FILENAME=$(echo "$line" | cut -d'"' -f 2)
  rm $FILENAME
done < already_uploaded.txt