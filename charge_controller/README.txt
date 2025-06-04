Pi Solar Monitor
https://www.youtube.com/shorts/s6DtEMxQv3A

Activate venv:
> cd to weather/weatherstation/zero
> source venv/bin/activate
> pip install renogymodbus

Update upload-to-dropbox.sh script to upload .csv file
Update command_line.py – Found at: madlab@Dorval-1:~/weather/weatherstation/zero/venv/lib/python3.11/site-packages/renogymodbus


New Restore Instructions for solar monitor:
1. Transfer Backup Files from Local to Pi
On your Windows machine, in PowerShell:
> scp C:\Users\alanj\Documents\School\MadLab\RaspberryPi\charge_controller\* madlab@<PI-IP>:/home/madlab/charge_controller/

Might need to make the folder first if it doesn’t exist.
> mkdir -p /home/madlab/charge_controller/

2. On the Pi: Create Virtual Environment & Install Dependencies
SSH into the Pi:

> ssh madlab@<PI-IP>
> cd /home/madlab/charge_controller/
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt

3. Overwrite the installed command_line.py with the modified version
	> cp command_line.py venv/lib/python3.11/site-packages/renogymodbus/command_line.py

4. Install the Dropbox Upload Script
Move the script and make it executable:
> cp upload-to-dropbox_SOLAR.sh /home/madlab/dendro-pi-main/upload-to-dropbox.sh
> chmod +x /home/madlab/dendro-pi-main/upload-to-dropbox.sh

5. Restore the Crontab
> crontab my_crontab_backup.txt
If you want to confirm:
> crontab -l
Should look like this:
# Upload Charge Controller Data every day (3am)
3 0 * * * sh /home/madlab/dendro-pi-main/upload-to-dropbox.sh

# Take Solar Charge Controller measurements every 5 minutes
*/5 * * * * /home/madlab/charge_controller/venv/bin/renogymodbus --device charge_controller --portname /dev/ttyUSB0 --slaveaddress 17
