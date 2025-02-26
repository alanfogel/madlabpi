# Date: February 22, 2025
# This script interfaces with dendrometers on 4 channels to collect data and process using moving average filters.

import datetime
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
# # Initialize the ADC (ADS1115)
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

# Data storage for moving averages
channel_data = {
    chan: {'values': [], 'filtered': 0.0}
    for chan in channels
}

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
        
        # Update moving average
        channel_data[chan_num]['values'].append(mean_microns)
        if len(channel_data[chan_num]['values']) > WINDOW_SIZE:
            channel_data[chan_num]['values'].pop(0)
        
        filtered = np.mean(channel_data[chan_num]['values'])
        results[chan_num] = (filtered, mean_voltage)
    
    return results

def save_channel_data(chan_num, filtered_value):
    """Save data only if valid signal present"""
    if filtered_value > NOISE_FLOOR:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(f'micron_values_channel_{chan_num}.txt', 'a') as f:
            f.write(f"{timestamp}, {filtered_value}\n")

def main_loop():
    """Main processing loop"""
    while True:
        start_time = time.monotonic()
        
        # Sample all channels in parallel
        samples = sample_all_channels()
        
        # Process samples for all channels
        results = process_samples(samples)
        
        # Save and print results
        for chan_num, (filtered, voltage) in results.items():
            if filtered is not None:
                save_channel_data(chan_num, filtered)
                print(f"Ch{chan_num}: {filtered:.2f}µm | {voltage:.4f}V")
        
        # Control loop timing
        elapsed = time.monotonic() - start_time
        sleep_time = max(1.0 - elapsed, 0.1)
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")