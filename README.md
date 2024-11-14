# dendro-pi

Program to take periodic pictures and retrieve data from dendrometers at Dorval and BERMS
 - --
## Getting started
### Setting up Raspberry Pi for ssh
1. Insert SD card into computer
2. Download wpa_supplicant.conf file
   1. Edit the following lines to match the name and password of your wifi network. 
   2. Place in the root directory of the boot drive of the SD card
3. If on mac open the terminal and run the following commands
> cd /Volumes/boot/

> touch ssh
5. Remove SD from computer and insert into raspberry pi
6. Reboot the Raspberry Pi

Raspberry PI imager from website


### Configuring Raspberry Pi
1. Connect to same network on computer that the raspberry pi is configured to connect to 
2. ssh into raspberry pi by running the following command (without braces)

> ssh pi@{ip address}
> ssh username@{hostname}.local


3. Run the following command to configure the Raspberry Pi

> sudo raspi-config

4. Change the password of the raspberry pi
5. Change the timezone in localization settings
6. Finish and reboot to save your changes
7. After rebooting ssh back into the Raspberry Pi. Use the new password that you created

8. Check to see if pycamera is installed by running the following command
   > python -c "import picamera"
   
   if not run the following commands to download picamera
   > sudo apt-get update 
 
   >sudo apt-get install python-picamera python3-picamera

	Takes a picture and saves to test.jpg
	> rpicam-jpeg -o test.jpg 


### Installing 
1. Download dendro-pi from gitlab using the following command

    > git clone https://gitlab.com/domdneufeld/dendro-pi.git

   Once picamera is installed, enter the dendro-pi/test/ directory and run:
   > python test_dendro.py 
   
   This checks if the python module is working

No permission to view file

Exit SSH
	Recursively copies 
scp -r C:\Users\alanj\Documents\School\RaspberryPi\dendro-pi-main madlab@DorvalTest.local:~/

   Once picamera is installed, enter the dendro-pi/test/ directory and run:
   > python test_dendro.py 



2. Open dendro_pictures.py in a text editor and insert name of camera on 
   > CAMERA_NAME = "ADD NAME HERE"  # Edit this to change name picture file

3. Follow this guide to install dropbox-uploader.sh https://linuxhint.com/install-use-dropbox-raspberry-pi/
4. Run "crontab -e" and follow the directions. Save and close the file without editing
5. Run the script add_cron.sh to schedule hourly pictures and daily file uploads by running the following command
   > sh add_cron.sh
6. Create a new directory in dropbox to upload to
7. Open upload-to-dropbox.sh in a text editor and insert the directory name in line 3 as shown below
   > ./dropbox_uploader.sh upload ~/dendro-pi/pictures/* /Directory_Name_Here/ | grep "file exists with the same hash" > already_uploaded.txt

### Testing
1. To test that the uploader is working run the following command in dendro-pi/main/
   > python dendro_pictures.py

2. Run the following command in dendro-pi/
   > sh upload-to-dropbox.sh
 
3. Once the previous command finishes running check to see if a picture was uploaded to dropbox

### Copying pictures from Raspberry Pi local storage via ssh
1. Connect to same network on computer that the Raspberry Pi is connected to.
2. Find the ip address of the Raspberry Pi that you wish to copy pictues from
3. Run the following command
   > scp pi@<ip address>:~/dendro-pi/pictures/* .
4. Enter password for Raspberry Pi when prompted

