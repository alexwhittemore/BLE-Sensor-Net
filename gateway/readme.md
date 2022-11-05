# Gateway

The code in this directory implements a gateway to consume BLE advertising packets in the right MySensorData format, then shuffle those into InfluxDB for analysis in Grafana. 

## Setup

Rough steps:

1. pip install -r requirements.txt
1. `sudo cp ble-gateway.service /etc/systemd/system/`
1. `sudo systemctl start ble-gateway`

I remember a lot of headaches with installing hcitool or something like that, so I need to try reproducing this from scratch. 