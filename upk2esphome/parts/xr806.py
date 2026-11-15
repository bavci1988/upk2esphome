#  Copyright (c) 2026 bavci1988.

from upk2esphome.config import ConfigData
from upk2esphome.opts import Opts
from upk2esphome.result import YamlResult

# XR806 GPIOs that can wake the chip from standby (see the xr806 component)
STANDBY_WAKE_GPIOS = (11, 12, 13, 19, 20)


def tuya_io_to_pin(io: int) -> str | None:
    """Tuya GPIO number on a WXU to XR806 pin name: PA0..PA23 are 0..23, PB0.. follow."""
    if 0 <= io < 24:
        return f"PA{io}"
    if 24 <= io < 24 + 16:
        return f"PB{io - 24}"
    return None


def generate(yr: YamlResult, config: ConfigData, opts: Opts):
    meta = config.xr806
    if meta is None:
        return

    if config.is_tuya_mcu and "uart" in yr.data:
        # UART0 of the WXU is wired to the MCU
        yr.data["uart"] = dict(
            id="mcu_uart",
            tx_pin="PB0",
            rx_pin="PB1",
            baud_rate=yr.data["uart"].get("baud_rate"),
            rx_buffer_size=256,
        )
        yr.data.setdefault("tuya", {})["uart_id"] = "mcu_uart"

    reasons = meta.get("low_power") or []
    if not reasons or "tuya" not in yr.data:
        return
    yr.log(f"Low-power TuyaMCU device: {', '.join(reasons)}")
    product = meta.get("product") or {}
    tuya = yr.data["tuya"]
    tuya["protocol"] = "low_power"

    wake = config.data.get("wake_up_mcu_io")
    if not opts.xr806_mcu_wake_pin:
        yr.log("MCU wake pin left to the MCU's product info at run time")
    elif isinstance(wake, dict) and (pin := tuya_io_to_pin(wake.get("io", -1))):
        tuya["mcu_wake_pin"] = {
            "number": pin,
            "inverted": wake.get("level", 0) == 0,
        }
    elif len(product.get("mwk", [])) == 1 and (
        pin := tuya_io_to_pin(product["mwk"][0])
    ):
        # the original firmware drives the wake line low by default
        tuya["mcu_wake_pin"] = {"number": pin, "inverted": True}

    if not opts.xr806_standby:
        return
    # Standby is decided at run time: the tuya component reads wk, mwk and sm from
    # the MCU's product info, takes the wake pins from it when they are not set
    # here, and only lets the module sleep with sm 1 or 2.
    standby = {"enabled": True, "require_external_sync": True}
    wk = product.get("wk", [])
    if len(wk) == 1 and wk[0] in STANDBY_WAKE_GPIOS:
        standby["wake_pin"] = f"PA{wk[0]}"
        standby["wake_edge"] = "falling"
    elif wk:
        yr.warn(f"MCU wake line wk={wk} cannot wake the XR806")
    if product and not set(product.get("sm", [])) & {1, 2}:
        yr.log("The MCU product info allows no standby (sm); it stays off at run time")

    if opts.xr806_wlan_connected:
        try:
            dtim = int(opts.xr806_dtim)
        except ValueError:
            dtim = 3
        wlan = {
            "_1": "In standby the WLAN stays connected: Home Assistant sees the device",
            "_2": "online, and every packet to it (HA, web, OTA) wakes the CPU",
            "dtim": min(max(dtim, 1), 30),
            "stay_connected": True,
        }
        if isinstance(yr.data.get("wifi"), dict):
            # stay_connected needs a Wi-Fi power save mode
            yr.data["wifi"]["power_save_mode"] = "light"
    else:
        wlan = {
            "_1": "In standby the WLAN is off: the device is offline while it sleeps",
            "network_suspend": True,
        }
    xr806 = yr.data.setdefault("xr806", {"board": "wxu"})
    xr806["standby"] = standby
    xr806["wlan"] = wlan
