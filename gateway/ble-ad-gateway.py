# Advertising-only BLE gateway prototype
# This version of the gateway will look like it's working with non-hcitool backend,
# but probably requires hcitool for stability, especially at higher ad frequency.
# At present, records EVERY AD that comes through, with no deduplication.

# ERRATA/TODO:
# Possible BLE backends to use with this script are Bleak (default) and hcitool (if hcitool is installed/working.)
# I switch between them by renaming /usr/bin/hcitool to /usr/bin/hcitool_disabled.
# 
# The Bleak backend amalgamates scan responses with the original ad packet, meaning you get the manufacturer data payload along with
# whatever's in the scan response. Namely, you get an advert.complete_name and advert.data in the same object. The cost of this is
# that the Bleak backend also eats duplicate advertisements, and apparently returns values very slowly. It's ideal, and seems to
# mostly work for us, but drops some ad packets that are absolutely getting through at the physical layer.
# 
# The hcitool backend takes advertisements as they come in and just shuffles them along to python as quickly as possible.
# In other words, if a scannable ad comes in and DOES trigger a response request+scan response, two ads will surface to python:
# one containing the original manufacturer data, and a second containing the scan response and thus complete_name.
# 
# Figuring out how to best handle this sparse menu of options is an annoying task, so as of this revision of the gateway, I just won't.
# The code below stores sensor data based entirely on MAC address, not at all on complete_name.

# The included service ble-gateway.service can be installed with 
# sudo cp ble-gateway.service /etc/systemd/system/
# And started with
# sudo systemctl start ble-gateway

import time
import board
from adafruit_ble import BLERadio
from SensorAdverts import MySensorData

from influxdb import InfluxDBClient

# Reset hcitool because it never works after unclean exit:
import os
os.system("sudo hciconfig hci0 reset")

ble = BLERadio()

## Configure DB connection
InfluxDBUsername = 'admin'
InfluxDBPassword = 'password'
InfluxDBDatabase = 'sensors'

print("Scanning for MySensorData")

def get_time_string():
    now = time.time()
    mlsec = repr(now).split('.')[1][:3]
    return time.strftime(f"%a %d %b %Y %H:%M:%S.{mlsec} %z", time.localtime(now))

# Connect to InfluxDB running on the local machine
# ssl=True, verify_ssl=True
client = InfluxDBClient(host='localhost', port=8086, username=InfluxDBUsername, password=InfluxDBPassword)
#client = InfluxDBClient(host='hooke.alexw.io', port=8086, username=InfluxDBUsername, password=InfluxDBPassword, ssl=True, verify_ssl=True)
client.switch_database(InfluxDBDatabase)

# while True:
for ble_advert in ble.start_scan(MySensorData, minimum_rssi=-200):
    time_string = get_time_string()

    # print(f"{time_string} {noah_advert.address.string}({noah_advert.complete_name}): {noah_advert.data}")
    sensor_name = ble_advert.address.string.replace(":","-") # Swap colons for dashes, so the file names are windows-acceptable.
    filename_str = f"{sensor_name}.csv"
    humidity = ble_advert.data[0]/100
    temp_c = ble_advert.data[1]
    battery_voltage = ble_advert.data[2]/1000
    seq_num = ble_advert.data[3]
    report_string = f"{time_string}, {ble_advert.address.string}, {ble_advert.rssi}, {humidity:.2f}, {temp_c:.2f}, {battery_voltage:.3f}, {seq_num}"
    #print(report_string)
    # logging.warning("Got data from {}: '{}".format(current_name, uart_data.decode()))

    with open(filename_str, "a") as f: # Open the individual sensor stream output for append
        f.write(report_string+"\n")

    with open("sensor_log.csv", "a") as f: # Open the all-sensors stream output for append
        f.write(report_string+"\n")


    # Add a measurement for this advertisement to InfluxDB
    json_body = [
    {
        "measurement": "sensorData",
        "tags": {
            "sensor_address": ble_advert.address.string
        },
        # "time": "2018-03-28T8:01:00Z", ## Eventually we'll use a timestamp closer to the measurement sample time, but for now, let Influx handle it.
        "fields": {
            "rssi": ble_advert.rssi,
            "humidity": humidity,
            "temp_c": temp_c,
            "battery_voltage": battery_voltage,
            "sequence_number": seq_num
        }
    }]
    if not client.write_points(json_body):
        print("BLE Gateway: Failed to write points to DB")
ble.stop_scan()
