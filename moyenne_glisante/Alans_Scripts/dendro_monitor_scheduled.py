# Date: June 11, 2024
# This script reads dendrometer data from 4 channels, processes it, and saves the results.

import datetime
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)

# Initialize all 4 ADC channels
channels = {
    0: AnalogIn(ads, ADS.P0),
    1: AnalogIn(ads, ADS.P1),
    2: AnalogIn(ads, ADS.P2),
    3: AnalogIn(ads, ADS.P3)
}

# Configuration
WINDOW_SIZE = 10
SAMPLE_DELAY = 0.1
NOISE_FLOOR = 1  # Minimum micron value to consider valid signal

def read_adc(adc_channel):
    """Read ADC value with error handling and calibration"""
    try:
        adc_value = adc_channel.value
    except Exception as e:
        print(f"I2C error on channel {adc_channel}: {e}")
        return None, None

    if not (0 <= adc_value <= 65535):
        return None, None

    # Apply calibration floor
    adc_value = max(adc_value, 275)
    
    # Convert to voltage and microns
    voltage = ((adc_value - 275) / 65535.0) * (3.3 - 0.012)
    microns = voltage / (3.3 - 0.012) * 25400
    
    return voltage, microns

def sample_all_channels():
    """Sample all 4 channels in parallel"""
    samples = {chan: [] for chan in channels}
    
    # Take 10 samples for all channels
    for _ in range(10):
        for chan_num, adc_channel in channels.items():
            voltage, microns = read_adc(adc_channel)
            if voltage is not None and microns is not None:
                samples[chan_num].append((voltage, microns))
        time.sleep(SAMPLE_DELAY)
    
    return samples

def process_samples(samples):
    """Process samples for all channels"""
    results = {}
    for chan_num, data in samples.items():
        if not data:
            results[chan_num] = (None, None)
            continue
        
        # Calculate means
        voltages, microns = zip(*data)
        mean_microns = sum(microns) / len(microns)
        mean_voltage = sum(voltages) / len(voltages)
        
        results[chan_num] = (mean_microns, mean_voltage)
    
    return results

def save_channel_data(chan_num, mean_microns):
    """Save data only if valid signal present"""
    if mean_microns > NOISE_FLOOR:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        datestamp = datetime.date.today().strftime("%Y-%m-%d")
        file_path = f'/home/madlab/dendro_logger/channel_{chan_num}_{datestamp}.txt'
        with open(file_path, 'a') as f:
            f.write(f"{timestamp}, {mean_microns}\n")

def main():
    """Main function to sample, process, and save data"""
    # Sample all channels
    samples = sample_all_channels()
    
    # Process samples
    results = process_samples(samples)
    
    # Save and print results
    for chan_num, (mean_microns, mean_voltage) in results.items():
        if mean_microns is not None:
            save_channel_data(chan_num, mean_microns)
            print(f"Ch{chan_num}: {mean_microns:.2f}µm | {mean_voltage:.4f}V")

if __name__ == "__main__":
    main()