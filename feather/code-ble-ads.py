"""
Advertising-only sensor firmware.
Creates a MySensorData packet with humidity (two decimal places), temp (float), battery voltage (mV), and sequence number (32bit, 136yr @1s)
Broadcasts it for 1s, then sleeps for 10min.
Will wake up and broadcast on 10 minute intervals regardless of how long it's awake.
"""

import time
import microcontroller
# from micropython import const

from adafruit_ble import BLERadio
import random

from SensorAdverts import MySensorData

import board
from analogio import AnalogIn
import adafruit_sht31d
import neopixel

ble = BLERadio()
i2c = board.I2C()
sht31d = adafruit_sht31d.SHT31D(i2c)
name_prefix = "BleSnsr" # Change to to differentiate sensors of different types/groups/etc 
ble.name = f'{name_prefix}{ble.address_bytes[1]:02X}{ble.address_bytes[0]:02X}'

# Time in seconds to wait between sensor polls
sleep_duration = 10 # 600s = 10min

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixels[0] = (0, 0, 0)                           # Turn off neopixel to save a bunch of power (Still burns ~500-700uA, even off.)

vbatpin = AnalogIn(board.BATTERY)
def battVoltage():
    '''Sample battery voltage by taking 1000 averaged samples of the pin, scaling each appropriately. Reported in mV'''
    voltage = 0
    for i in range(1000):
        voltage += (vbatpin.value * 6.6) / 65536 # Battery is scaled by 1/2, w/ analog ref of 3.3V, hence 6.6
    # voltage = voltage/1000 Skip this rescale; report the value in mV
    return int(voltage)

print("Starting")
ble = BLERadio()
advertisement = MySensorData() # advertisement.data has the format [humidity*100 (uint_16), temp (float), batt voltage (uint_16, mV), sequence number (uint_32)]
# Example:
# advertisement.data = [4995, 27.01, 4200, 0]
# means 49.95%, 27.01 deg C, 4.2V, 0th sample.

sequence_num = 0
while True:
    # 1 Collect a set of sample data (temp/humidity/battery)
    # 2 Advertise that data publically for a few seconds
    # 3 Go back to sleep for `sleep_duration` seconds (nominally 10 minutes = 600s in deployment)
    advertisement.data = [  int(sht31d.relative_humidity*100),
                            sht31d.temperature,
                            battVoltage(),
                            sequence_num]
    print(advertisement.data)
    ble.start_advertising(advertisement, timeout=2)
    #time.sleep(2)
    #ble.stop_advertising()
    # Go into low power sleep for sleep_duration. BLE will automatically stop advertising after the timeout. 
    time.sleep(sleep_duration)
    sequence_num += 1
