# Author: [Nathanaël BLAVO BALLARIN]
# Date: June 11, 2024
# This script interfaces with various sensors to collect environmental 
#data such as temperature, pressure, and humidity. It processes the 
#data using a moving average filter and transmits it over a radio frequency communication module. 
#The script is designed for use with a microcontroller and includes functions for sensor testing, data averaging, 
#and non-acknowledgment data transmission. It also features a section for data logging, which is currently commented out.


# Import necessary libraries for communication and sensor operation
import board
from board import *
import busio
import analogio
import digitalio
import time
from adafruit_dps310.basic import DPS310
import adafruit_sht4x
import adafruit_rfm9x
import ulab.numpy as np

# Initialize I2C communication
i2c = busio.I2C(board.D25, board.D24)
# Initialize ADC (Analog to Digital Converter) on pin A1
adc = analogio.AnalogIn(board.A1)
# Set the frequency for the radio module
RADIO_FREQ_MHZ = 915.0
# Set up chip select and reset pins for the radio module
CS = digitalio.DigitalInOut(RFM_CS)
RESET = digitalio.DigitalInOut(RFM_RST)
# Define acknowledgment timeout for radio communication
ack_timeout=0.1
# Initialize SPI communication
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
# Initialize the RFM9x radio module with the specified settings
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)
# Set the transmit power and node/destination addresses for the radio module
rfm9x.tx_power = 23
rfm9x.node = 1
rfm9x.destination = 2

# Define the window size for the moving average filter
window_size = 10

# Create a list to store ADC values
adc_values = []

# Function to test the DPS310 sensor and return temperature and pressure
def test_dps310():
    dps310 = DPS310(i2c)
    return dps310.temperature, dps310.pressure

# Function to test the SHT41 sensor and return temperature and humidity measurements
def test_sht41():
    sht = adafruit_sht4x.SHT4x(i2c)
    return sht.measurements

# Function to read ADC value, apply calibration, and convert to tension and microns
def lire_adc():
    valeur_adc = adc.value
    # Apply calibration if ADC value is below threshold, you need to calibrate your ADC by measuring the minimum dendrometer value
    if valeur_adc < 275:
        valeur_adc = 275
    # Calculate tension and microns based on ADC value, here Vref = 3.3 - 0.012 V
    tension = ((valeur_adc-275) / 65535.0) * (3.3-0.012)
    microns = tension / (3.3-0.012) * 25400
    return tension, microns

# Function to calculate the mean ADC value over a number of samples
def mean_adc():
    microns_values = []
    tensions_values = []
    # Take 10 samples and calculate their mean
    for i in range(10):
        tensions, microns = lire_adc()
        microns_values.append(microns)
        tensions_values.append(tensions)
        time.sleep(0.08)
    return sum(microns_values) / len(microns_values), sum(tensions_values) / len(tensions_values)

# Function to send data via radio without waiting for an acknowledgment
def send_data_without_ack(data):
    rfm9x.send(data)
    print("Data sent without waiting for acknowledgement")

# Function to save the mean microns value to a file
def save_mean_microns(mean_microns):
    # Open a file in append mode
    with open('/micron_values.txt', 'a') as file:
        # Write the mean micron value to the file
        file.write(str(mean_microns) + '\n')
    # Code to read the file content is commented out

# Main loop to continuously read sensors and send data
while True:
    start_time = time.monotonic()  # Get the start time
    # Get mean ADC values, temperature, and pressure from sensors
    mean_microns, mean_tensions = mean_adc()
    temperature_dps310, pression = test_dps310()
    temperature_sht41, humidite = test_sht41()

    # Add the ADC value to the list for moving average calculation
    adc_values.append(mean_microns)

    # If enough values are collected, apply the moving average filter
    if len(adc_values) > window_size:
        # Remove the oldest value
        adc_values.pop(0)

        # Calculate the average of the values in the window
        filtered_value = np.mean(adc_values)

        # Prepare and send the data packet via radio
        data = f"Filtered Microns: {filtered_value}, Mean Tensions: {mean_tensions}, DPS310 Temperature: {temperature_dps310}, Pressure: {pression}, SHT41 Temperature: {temperature_sht41}, Humidity: {humidite}"
        send_data_without_ack(bytes(data, "UTF-8"))
        print(f"Filtered value: {filtered_value}")
        # Code to save the mean microns value is commented out

    end_time = time.monotonic()  # Get the end time
    # Calculate and print the elapsed time for each loop iteration
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
