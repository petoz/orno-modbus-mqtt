#!/usr/bin/env python3
import minimalmodbus
import struct
import serial
import time
from timeloop import Timeloop
from datetime import timedelta

smartmeter = minimalmodbus.Instrument('/dev/ttyUSB0', 1)  # port name, slave address (in decimal)
smartmeter.serial.baudrate = 9600          # Baud
smartmeter.serial.bytesize = 8
smartmeter.serial.parity = serial.PARITY_NONE  # vendor default is EVEN
smartmeter.serial.stopbits = 1
smartmeter.serial.timeout = 0.10           # seconds
smartmeter.mode = minimalmodbus.MODE_RTU    # rtu or ascii mode
smartmeter.clear_buffers_before_each_transaction = True
smartmeter.debug = False                    # set to "True" for debug mode

tl = Timeloop()

@tl.job(interval=timedelta(seconds=10))
def sample_job_every_10s():
    print("Starting data collection...")
    try:
        # Read the frequency from register 0x010A with one decimal place adjustment
        print("Reading Frequency...")
        Frequency = smartmeter.read_register(0x010A, 1, 3, signed=True) / 1
        print(f"Frequency: {Frequency} Hz")

        # Read the voltage from register 0x0100, using two registers (32 bits)
        Voltage = smartmeter.read_long(0x0100, 3, signed=True) / 1000
        print(f"Voltage: {Voltage} V")

        print("Reading Current...")
        Current = smartmeter.read_long(0x102, 3, signed=True) / 1000
        print(f"Current: {Current} A")

        print("Reading ActivePower...")
        ActivePower = smartmeter.read_long(0x104, 3, signed=True)  / 1
        print(f"ActivePower: {ActivePower} W")

        print("Reading ReactivePower...")
        ReactivePower = smartmeter.read_long(0x108, 3, signed=True) / 1
        print(f"ReactivePower: {ReactivePower} Var")

        print("Reading ApparentPower...")
        ApparentPower = smartmeter.read_long(0x106, 3, signed=True) / 1
        print(f"ApparentPower: {ApparentPower} VA")

        print("Reading PowerFactor...")
        PowerFactor = smartmeter.read_register(0x10B, 3, 3, signed=True) / 1
        print(f"PowerFactor: {PowerFactor}")

        print("Reading ActiveEnergy...")
        ActiveEnergy = smartmeter.read_long(0x10E, 3, True) / 100
        print(f"ActiveEnergy: {ActiveEnergy} kWh")

        print("Reading ReactiveEnergy...")
        ReactiveEnergy = smartmeter.read_long(0x118, 3, True) / 100
        print(f"ReactiveEnergy: {ReactiveEnergy} kvarh")

        errorcode = "OK"
        print(f"Data collection completed successfully: {errorcode}")

    except Exception as e:
        errorcode = "Modbus error. No connection to device"
        print(f"Error during data collection: {errorcode} - {e}")
        return

if __name__ == "__main__":  # main loop
    tl.start(block=True)
