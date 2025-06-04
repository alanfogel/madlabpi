import argparse
import csv
import os
import datetime
import RPi.GPIO as GPIO
from renogymodbus import RenogyChargeController, RenogySmartBattery
from renogymodbus.find_slaveaddress import find_slaveaddress

# Setup relay pin location, thresholds for turning on and off
RELAY_PIN = 10
TEMP_ON_THRESHOLD = 23
TEMP_OFF_THRESHOLD = 24
CSV_FILE = "/home/madlab/charge_controller/controller_log.csv"

# Setup GPIO for relay
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--portname", help="Port name for example /dev/ttyUSB0", default="/dev/ttyUSB0"
    )
    parser.add_argument(
        "--slaveaddress", help="Slave address 1-247", default=1, type=int
    )
    parser.add_argument(
        "--device", help="Device to read data from. Either charge_controller or smart_battery", choices=["charge_controller", "smart_battery"], default="charge_controller", type=str
    )
    parser.add_argument(
        "--find-slave-address", help="Find slave address of modbus device", action="store_true", default=False
    )
    args = parser.parse_args()

    if args.find_slave_address:
        print("Finding slave addresses...")
        addresses = find_slaveaddress(args.portname)

        if len(addresses) == 0:
            print("No modbus devices found")
        else:
            print("Found modbus devices at addresses:")
            for address in addresses:
                print(f"{address}")
    elif args.device == "charge_controller":
        print_charge_controller_output(args)
    elif args.device == "smart_battery":
        print_smart_battery_output(args)

def set_relay(on: bool):
    GPIO.output(RELAY_PIN, GPIO.HIGH if on else GPIO.LOW)

def log_data_to_csv(timestamp, controller_temp, battery_voltage, soc, relay_state,
                    solar_voltage, solar_current, solar_power,
                    battery_temp, max_solar_today, min_solar_today,
                    max_batt_v_today, min_batt_v_today):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'Timestamp',
                'Controller Temp (°C)',
                'Battery Voltage (V)',
                'State of Charge (%)',
                'Relay State (On=True)',
                'Solar Voltage (V)',
                'Solar Current (A)',
                'Solar Power (W)',
                'Battery Temp (°C)',
                'Max Solar Today (W)',
                'Min Solar Today (W)',
                'Max Battery V Today (V)',
                'Min Battery V Today (V)'
            ])
        writer.writerow([
            timestamp,
            controller_temp,
            battery_voltage,
            soc,
            relay_state,
            solar_voltage,
            solar_current,
            solar_power,
            battery_temp,
            max_solar_today,
            min_solar_today,
            max_batt_v_today,
            min_batt_v_today
        ])

def print_charge_controller_output(args):
    controller = RenogyChargeController(args.portname, args.slaveaddress)

    # Read all values
    solar_voltage = controller.get_solar_voltage()
    solar_current = controller.get_solar_current()
    solar_power = controller.get_solar_power()
    load_voltage = controller.get_load_voltage()
    load_current = controller.get_load_current()
    load_power = controller.get_load_power()
    battery_voltage = controller.get_battery_voltage()
    battery_soc = controller.get_battery_state_of_charge()
    battery_temp = controller.get_battery_temperature()
    controller_temp = controller.get_controller_temperature()
    max_solar_today = controller.get_maximum_solar_power_today()
    min_solar_today = controller.get_minimum_solar_power_today()
    max_batt_v_today = controller.get_maximum_battery_voltage_today()
    min_batt_v_today = controller.get_minimum_battery_voltage_today()

    # Print as before
    print("Real Time Charge Controller Data")
    print(f"Solar voltage: {solar_voltage}V")
    print(f"Solar current: {solar_current}A")
    print(f"Solar power: {solar_power}W")
    print(f"Load voltage: {load_voltage}V")
    print(f"Load current: {load_current}A")
    print(f"Load power: {load_power}W")
    print(f"Battery voltage: {battery_voltage}V")
    print(f"Battery state of charge: {battery_soc}%")
    print(f"Battery temperature: {battery_temp}°C")
    print(f"Controller temperature: {controller_temp}°C")
    print(f"Maximum solar power today: {max_solar_today}W")
    print(f"Minimum solar power today: {min_solar_today}W")
    print(f"Maximum battery voltage today: {max_batt_v_today}V")
    print(f"Minimum battery voltage today: {min_batt_v_today}V")

    # Relay control logic
    relay_state = None
    if controller_temp > TEMP_ON_THRESHOLD:
        set_relay(True)
        relay_state = True
    elif controller_temp < TEMP_OFF_THRESHOLD:
        set_relay(False)
        relay_state = False

    # Log to CSV
    timestamp = datetime.datetime.now().isoformat()
    log_data_to_csv(
        timestamp,
        controller_temp,
        battery_voltage,
        battery_soc,
        relay_state,
        solar_voltage,
        solar_current,
        solar_power,
        battery_temp,
        max_solar_today,
        min_solar_today,
        max_batt_v_today,
        min_batt_v_today
)

#    GPIO.cleanup()

def print_smart_battery_output(args):
    battery = RenogySmartBattery(args.portname, args.slaveaddress)

    print("Real Time Smart Battery Data")
    print(f"Cell voltages: {battery.get_cell_voltages()}V")
    print(f"Cell temperatures: {battery.get_cell_temperatures()}°C")
    print(f"BMS temperature: {battery.get_bms_temperature()}°C")
    print(f"Environment temperatures: {battery.get_environment_temperatures()}°C")
    print(f"Heater temperatures: {battery.get_heater_temperatures()}°C")
    print(f"Current: {battery.get_current()}A")
    print(f"Voltage: {battery.get_voltage()}V")
    print(f"Remaining capacity: {battery.get_remaining_capacity()}Ah")
    print(f"Total capacity: {battery.get_total_capacity()}Ah")
    print(f"State of charge: {battery.get_state_of_charge()}%")
    print(f"Cycle number: {battery.get_cycle_number()}")
    print(f"Charge voltage limit: {battery.get_charge_voltage_limit()}V")
    print(f"Discharge voltage limit: {battery.get_discharge_voltage_limit()}V")
    print(f"Charge current limit: {battery.get_charge_current_limit()}A")
    print(f"Discharge current limit: {battery.get_discharge_current_limit()}A")

if __name__ == "__main__":
    main()
