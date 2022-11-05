# BLE Sensor Net

This code is part of a talk given at Hackaday Supercon 2022.

The gist is two parts:

1. Sensor code, written in CircuitPython 7.x, that runs on an [Adafruit Feather Bluefruit Sense](https://www.adafruit.com/product/4516), and advertises temp and humidity values in a particular format.
2. Gateway code, which runs on a Raspberry Pi that also has InfluxDB and Grafana installed. The gateway code listens for the right advertisements, and puts the data in InfluxDB for review in Grafana.

## Setup

1. Download and copy the 'feather' code onto your BLE Feather
1. Download the 'gateway' code onto a Raspberry Pi 4B+
1. Install InfluxDB on the Pi (Instructions TBD, sorry)
1. Install Grafana on the Pi (Instructions TBD, sorry)
1. Install the gateway code according to the instructions in that directory
1. Set up your grafana dashboards - this is an exercise left to the user unless I can find a convenient way to save the configuration for your later import. 