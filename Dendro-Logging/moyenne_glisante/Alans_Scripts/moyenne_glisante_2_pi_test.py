# Author: [Nathanaël BLAVO BALLARIN]
# Date: June 11, 2024
# This script interfaces with a dendrometer to collect data and process it using a moving average filter.

import datetime
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

# # Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
# # Initialize the ADC (ADS1115)
ads = ADS.ADS1115(i2c)
adc_channel = AnalogIn(ads, ADS.P0)  # Use channel 0 of the ADS1115

# Define the window size for the moving average filter
window_size = 10

# Create a list to store ADC values
adc_values = []

# Function to read ADC value, apply calibration, and convert to voltage and microns
def read_adc():
    try:
        adc_value = adc_channel.value # Read the current value from the ADC
    except Exception as e:
        print(f"I2C communication error: {e}")
        return None, None

    if adc_value < 0 or adc_value > 65535:
        print(f"Invalid ADC value detected. Skipping this reading.")
        return None, None

# Apply calibration if ADC value is below threshold, you need to calibrate your ADC by measuring the minimum dendrometer value
    if adc_value < 275:
        adc_value = 275  # Ensure the ADC value does not go below a certain minimum
    # Calculate voltage and microns based on ADC value, here Vref = 3.3 - 0.012 V
    voltage = ((adc_value - 275) / 65535.0) * (3.3 - 0.012)  # Convert the raw ADC value to voltage
    microns = voltage / (3.3 - 0.012) * 25400  # Convert the voltage to microns (distance)
    return voltage, microns

# Function to calculate the mean ADC value over a number of samples
def mean_adc():
    microns_values = []
    voltage_values = []
    # Take 10 samples and calculate their mean
    for _ in range(10):
        voltage, microns = read_adc()  # Read the ADC value

        # Skip invalid readings
        if voltage is None or microns is None:
                time.sleep(0.1)
                continue
        microns_values.append(microns)  # Append microns to the list
        voltage_values.append(voltage)  # Append voltage to the list
        time.sleep(0.1)  # Wait for a short period before taking the next sample
        # If no valid samples were collected, return None
        if not microns_values or not voltage_values:
            return None, None
        return sum(microns_values) / len(microns_values), sum(voltage_values) / len(voltage_values)

# Function to save the mean microns value to a file
def save_mean_microns(mean_microns):
    # Get the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Open a file in append mode
    with open('micron_values.txt', 'a') as file:
        # Write the mean micron value to the file
        file.write(f"{timestamp}, {mean_microns}\n")

# Main loop to continuously read sensors and process data
while True:
    start_time = time.monotonic()  # Get the start time
    # Get mean ADC values
    mean_microns, mean_voltage = mean_adc()
    # Skip this iteration if the readings are invalid
    if mean_microns is None or mean_voltage is None:
        print("Invalid readings detected. Skippingthis iteration.")
        time.sleep(1)
        continue

    # Add the ADC value to the list for moving average calculation
    adc_values.append(mean_microns)

    # If enough values are collected, apply the moving average filter
    if len(adc_values) > window_size:
        # Remove the oldest value
        adc_values.pop(0)

        # Calculate the average of the values in the window
        filtered_value = np.mean(adc_values)
        
        print(f"Filtered Microns: {filtered_value}, Mean Voltage: {mean_voltage}")
        # Save the filtered value to a file
        save_mean_microns(filtered_value)
    
    time.sleep(1)
    end_time = time.monotonic()  # Get the end time
    # Calculate and print the elapsed time for each loop iteration
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")

