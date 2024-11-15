# Author: [Nathanaël BLAVO BALLARIN]
# Date: June 11, 2024
# This script interfaces with a dendrometer to collect data and process it using a moving average filter.

# Import necessary libraries for communication and sensor operation
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np

# Initialize I2C communication
i2c = busio.I2C(board.SCL, board.SDA)
# Initialize the ADC (ADS1115)
ads = ADS.ADS1115(i2c)
adc_channel_0 = AnalogIn(ads, ADS.P0)  # Use channel 0 of the ADS1115
adc_channel_1 = AnalogIn(ads, ADS.P1)  # Use channel 1 of the ADS1115
adc_channel_2 = AnalogIn(ads, ADS.P2)  # Use channel 2 of the ADS1115
adc_channel_3 = AnalogIn(ads, ADS.P3)  # Use channel 3 of the ADS1115

# Define the window size for the moving average filter
window_size = 10

# Create a list to store ADC values for each channel
adc_values_0 = []
adc_values_1 = []
adc_values_2 = []
adc_values_3 = []

# Function to read ADC value, apply calibration, and convert to voltage and microns
def read_adc():
    adc_value = 30000 # Simulate an ADC value for testing
    # Apply calibration if ADC value is below threshold, you need to calibrate your ADC by measuring the minimum dendrometer value
    if adc_value < 275:
        adc_value = 275  # Ensure the ADC value does not go below a certain minimum
    # Calculate voltage and microns based on ADC value, here Vref = 3.3 - 0.012 V
    voltage = ((adc_value - 275) / 65535.0) * (3.3 - 0.012)  # Convert the raw ADC value to voltage
    microns = voltage / (3.3 - 0.012) * 25400  # Convert the voltage to microns (distance)
    return voltage, microns

# Function to calculate the mean ADC value over a number of samples for a specific channel
def mean_adc(adc_channel, adc_values):
    microns_values = []
    voltage_values = []
    # Take 10 samples and calculate their mean
    for _ in range(10):
        voltage, microns = read_adc(adc_channel)  # Read the ADC value
        microns_values.append(microns)  # Append microns to the list
        voltage_values.append(voltage)  # Append voltage to the list
        time.sleep(0.08)  # Wait for a short period before taking the next sample
    mean_microns = sum(microns_values) / len(microns_values)
    mean_voltage = sum(voltage_values) / len(voltage_values)
    adc_values.append(mean_microns)
    # If enough values are collected, apply the moving average filter
    if len(adc_values) > window_size:
        adc_values.pop(0)  # Remove the oldest value
    filtered_value = np.mean(adc_values)  # Calculate the average of the values in the window
    return filtered_value, mean_voltage

# Function to save the mean microns value to a file
def save_mean_microns(mean_microns, channel):
    # Open a file in append mode
    with open(f'micron_values_channel_{channel}.txt', 'a') as file:
        # Write the mean micron value to the file
        file.write(str(mean_microns) + '\n')

# Main loop to continuously read sensors and process data
while True:
    start_time = time.monotonic()  # Get the start time
    
    # Get mean ADC values for each channel
    filtered_value_0, mean_voltage_0 = mean_adc(adc_channel_0, adc_values_0)
    filtered_value_1, mean_voltage_1 = mean_adc(adc_channel_1, adc_values_1)
    filtered_value_2, mean_voltage_2 = mean_adc(adc_channel_2, adc_values_2)
    filtered_value_3, mean_voltage_3 = mean_adc(adc_channel_3, adc_values_3)

    # Print the filtered values and mean voltages for each channel
    print(f"Channel 0 - Filtered Microns: {filtered_value_0}, Mean Voltage: {mean_voltage_0}")
    print(f"Channel 1 - Filtered Microns: {filtered_value_1}, Mean Voltage: {mean_voltage_1}")
    print(f"Channel 2 - Filtered Microns: {filtered_value_2}, Mean Voltage: {mean_voltage_2}")
    print(f"Channel 3 - Filtered Microns: {filtered_value_3}, Mean Voltage: {mean_voltage_3}")

    # Save the filtered values to files
    save_mean_microns(filtered_value_0, 0)
    save_mean_microns(filtered_value_1, 1)
    save_mean_microns(filtered_value_2, 2)
    save_mean_microns(filtered_value_3, 3)

       
    end_time = time.monotonic()  # Get the end time
    # Calculate and print the elapsed time for each loop iteration
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")