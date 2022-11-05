import struct
from micropython import const
from adafruit_ble.advertising import Advertisement, LazyObjectField
from adafruit_ble.advertising.standard import ManufacturerData, ManufacturerDataField

_MANUFACTURING_DATA_ADT = const(0xFF)
_HOOKE_COMPANY_ID = const(0x14B5)
_COLOR_DATA_ID = const(0x0000)

class MySensorData(Advertisement):
    """Broadcast a single RGB color."""

    # This single prefix matches all color advertisements.
    match_prefixes = (
        struct.pack(
            "<BHBH",
            _MANUFACTURING_DATA_ADT,
            _HOOKE_COMPANY_ID,
            struct.calcsize("<HHfHI"),
            _COLOR_DATA_ID,
        ),
    )
    manufacturer_data = LazyObjectField(
        ManufacturerData,
        "manufacturer_data",
        advertising_data_type=_MANUFACTURING_DATA_ADT,
        company_id=_HOOKE_COMPANY_ID,
        key_encoding="<H",
    )
    # Humidity - Unsigned short. Humidity in % = value/100.
    # Temp - Float in degrees C
    # Battery voltage - Unsigned short in mV.
    # Sequence - Unsigned int. Measurement serial number. 136y worth of room @ 1s/measurement.
    data = ManufacturerDataField(_COLOR_DATA_ID, "<HfHI", ['Humidity', 'Temperature', 'Battery V', 'Sequence Num'])
    """Data making up a Noah sample."""