#!/usr/bin/env python3
import minimalmodbus
import struct
import serial
import time
from timeloop import Timeloop
from datetime import timedelta

smartmeter = minimalmodbus.Instrument('/dev/ttyUSB2', 1)  # port name, slave address (in decimal)
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
    try:
        Frequency = smartmeter.read_register(304, 2, 3, True)
        Voltage = smartmeter.read_register(305, 2, 3, True)
        Current = smartmeter.read_long(313, 3, False, 0) / 1000
        ActivePower = smartmeter.read_long(320, 3, False, 0)
        ReactivePower = smartmeter.read_long(328, 3, False, 0)
        ApparentPower = smartmeter.read_long(336, 3, False, 0)
        PowerFactor = smartmeter.read_register(344, 3, 3, True)
        ActiveEnergy = smartmeter.read_registers(40960, 10, 3)
        bits = (ActiveEnergy[0] << 16) + ActiveEnergy[1]
        s = struct.pack('>i', bits)
        tmp = struct.unpack('>L', s)[0]
        tmpFloat1 = tmp / 100
        ReactiveEnergy = smartmeter.read_registers(40990, 10, 3)
        bits = (ReactiveEnergy[0] << 16) + ReactiveEnergy[1]
        s = struct.pack('>i', bits)
        tmp = struct.unpack('>L', s)[0]
        tmpFloat2 = tmp / 100

        if smartmeter.debug:
            print(f"Die Frequenz ist: {Frequency:.2f} Herz")
            print(f"Die Spannung ist: {Voltage:.2f} Volt")
            print(f"Die Stromstärke ist: {Current:.3f} Ampere")
            print(f"Die Wirkleistung ist: {ActivePower:.2f} W")
            print(f"Die Blindleistung ist: {ReactivePower:.2f} Var")
            print(f"Die Scheinleistung ist: {ApparentPower:.2f} VA")
            print(f"Der Leistungsfaktor ist: {PowerFactor:.3f}")
            print(f"Zählerstand Energie ist: {tmpFloat1:.1f} kWh")
            print(f"Zählerstand Blindenergie ist: {tmpFloat2:.1f} kvarh")

        errorcode = "OK"

    except:
        errorcode = "Modbus error. No connection to device"
        return

if __name__ == "__main__":  # main loop
    tl.start(block=True)
