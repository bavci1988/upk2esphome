#  Copyright (c) Kuba Szczodrzyński 2023-4-22.

from dataclasses import dataclass


@dataclass
class Opts:
    esphome_block: bool = True
    name_mac: bool = False
    common: bool = True
    web_server: bool = True
    restart: bool = False
    uptime: bool = False
    lt_version: bool = True
    wifi_ssid: str = "!secret wifi_ssid"
    wifi_password: str = "!secret wifi_password"
    ota_password: str = ""
    api_password: str = ""
    xr806_standby: bool = True
    xr806_wlan_connected: bool = True
    xr806_mcu_wake_pin: bool = True
    xr806_dtim: str = "3"

    FLAGS = {
        "esphome_block": "Include esphome: block",
        "name_mac": "Add MAC to device name",
        "common": "Add common components",
        "web_server": "Add Web Server & Captive Portal",
        "restart": "Add restart button & sensor",
        "uptime": "Add uptime sensor",
        "lt_version": "Add LT version sensor",
        "xr806_standby": "XR806 low power: set up standby",
        "xr806_wlan_connected": "XR806 low power: WLAN stays connected in standby",
        "xr806_mcu_wake_pin": "XR806 low power: MCU wake pin from the dump",
    }
    INPUTS = {
        "wifi_ssid": "Wi-Fi SSID",
        "wifi_password": "Wi-Fi password",
        "ota_password": "OTA password",
        "api_password": "API password",
        "xr806_dtim": "XR806 low power: DTIM in standby",
    }
