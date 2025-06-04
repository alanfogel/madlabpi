# Date: May 21, 2025
# This script reads dendrometer data from 4 channels, processes it, and saves the results.

import datetime
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
ads.gain = 1  # ±4.096V range, for 3.3V signals

# Sensor type per channel: DC2 = 15,000 μm, DC3 = 25,400 μm
MICRON_SCALE = {
    0: 25400,  # DC3
    1: 15000,  # DC2
    2: 25400,  # DC3
    3: 25400   # DC3
}

# Initialize all 4 ADC channels
channels = {
    0: AnalogIn(ads, ADS.P0),
    1: AnalogIn(ads, ADS.P1),
    2: AnalogIn(ads, ADS.P2),
    3: AnalogIn(ads, ADS.P3)
}


# Sample each channel N times, average, and log to file
def read_and_log(samples=10, delay=0.1):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    datestamp = datetime.date.today().strftime("%Y-%m-%d")

    for chan_num, chan in channels.items():
        readings = []
        for _ in range(samples):
            try:
                voltage = chan.voltage # max(chan.voltage, 0.012)  # Apply noise floor
                readings.append(voltage)
            except Exception as e:
                print(f"Channel {chan_num} read error: {e}")
                continue
            time.sleep(delay)

        if not readings:
            print(f"Channel {chan_num} failed to collect valid samples.")
            continue

        avg_voltage = sum(readings) / len(readings)
        microns = avg_voltage / 3.3 * MICRON_SCALE[chan_num] # (3.3 - 0.012) 

        file_path = f"/home/madlab/dendro_logger/channel_{chan_num}_{datestamp}.txt"
        with open(file_path, "a") as f:
            f.write(f"{timestamp}, {microns:.2f}\n")
        print(f"Ch{chan_num}: {microns:.2f} µm, {avg_voltage:.4f} V (avg of {len(readings)} samples)")
        # print(f"Ch{chan_num}: {microns:.2f} µm (avg of {len(readings)} samples)")

if __name__ == "__main__":
    read_and_log()
    ## For testing:
    # try:
    #     while True:
    #         read_and_log()
    #         time.sleep(0.1)  # Wait 0.1 seconds between runs (adjust as needed)
    # except KeyboardInterrupt:
    #     print("Logging stopped by user.")
