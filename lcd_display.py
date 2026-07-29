"""LCD status display helpers for boot and Wi-Fi state."""

import time

from config import (
    LCD_ENABLED,
    LCD_I2C_ADDRESS,
    LCD_I2C_FREQUENCY,
    LCD_I2C_ID,
    LCD_SCL_PIN,
    LCD_SDA_PIN,
)

_lcd = None
_init_attempted = False


def _fit_16(text):
    if text is None:
        return ""
    value = str(text)
    return value[:16]


def _init_lcd():
    global _lcd, _init_attempted

    if _lcd is not None:
        return _lcd

    if _init_attempted or not LCD_ENABLED:
        return None

    _init_attempted = True

    try:
        from machine import I2C, Pin
        from lcd1602 import LCD

        bus = I2C(
            LCD_I2C_ID,
            sda=Pin(LCD_SDA_PIN),
            scl=Pin(LCD_SCL_PIN),
            freq=LCD_I2C_FREQUENCY,
        )
        _lcd = LCD(bus, addr=LCD_I2C_ADDRESS)
        _lcd.clear()
    except Exception:
        _lcd = None

    return _lcd


def show_lines(line1, line2=""):
    lcd = _init_lcd()
    if lcd is None:
        return False

    try:
        lcd.clear()
        lcd.write(0, 0, _fit_16(line1))
        lcd.write(0, 1, _fit_16(line2))
        return True
    except Exception:
        return False


def show_boot_message():
    show_lines("Pico Car Boot", "Starting...")


def show_wifi_connecting(ssid):
    show_lines("Wi-Fi connect:", _fit_16(ssid))


def show_wifi_connected(ssid, ip_address):
    show_lines("Wi-Fi OK:" + _fit_16(ssid), _fit_16(ip_address))


def show_ap_mode(ap_name, ip_address):
    show_lines("AP Mode:" + _fit_16(ap_name), _fit_16(ip_address))


def show_wifi_error(message):
    show_lines("Wi-Fi issue", _fit_16(message))


def pulse_boot_complete():
    """Briefly show boot-complete text after startup LED sequence."""

    if show_lines("Pico Ready", "Waiting Wi-Fi"):
        time.sleep_ms(700)
