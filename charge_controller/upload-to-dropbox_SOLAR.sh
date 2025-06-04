#!/bin/bash
cd ~/Dropbox-Uploader
./dropbox_uploader.sh upload ~/dendro-pi-main/pictures/* /Dorval-1/ | grep "file exists with the same hash" > already_uploaded.txt

while IFS= read -r line; do
  FILENAME=$(echo "$line" | cut -d'"' -f 2)
  rm $FILENAME
done < already_uploaded.txt

# Upload charge controller data SOLAR
cd ~/Dropbox-Uploader
./dropbox_uploader.sh upload ~/home/madlab/charge_controller/controller_log.csv /Dorval-Solar/
