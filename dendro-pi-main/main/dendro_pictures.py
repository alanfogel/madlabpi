import os

from picamera2 import Picamera2, Preview
import time
from datetime import datetime

PICTURES_PATH = r"/home/madlab/dendro-pi-main/pictures/"
CAMERA_NAME = "DorvalTest"  # Edit this to change name picture file

def get_filename():
    return CAMERA_NAME + get_date_and_time()

def get_date_and_time():
    return str(datetime.now().year) + "-" + \
        str(datetime.now().month) + "-" + \
        str(datetime.now().day) + "-" + \
        str(datetime.now().hour)

def take_picture():
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration(main={"size": (2592, 1944)}, lores={"size": (640, 480)}, display="lores")

    picam2.configure(camera_config)

    picam2.start_preview(Preview.NULL)
    picam2.start()
    time.sleep(2)
    file_name = get_filename()

    # Capture the file
    os.chdir(PICTURES_PATH)
    picam2.capture_file(file_name + ".jpeg")

    picam2.close()


# def setup_camera(camera):
#    camera.resolution = (2592, 1944)
#    camera.start_preview()
#    time.sleep(2)  # Camera warm-up time


if __name__ == '__main__':
    take_picture()
