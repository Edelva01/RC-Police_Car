"""LCD status display helpers for boot and Wi-Fi state."""

import time

from config import (
    LCD_ENABLED,
    LCD_I2C_ADDRESS,
    LCD_I2C_FREQUENCY,
    LCD_I2C_ID,
    LCD_SCROLL_CYCLES,
    LCD_SCROLL_ENABLED,
    LCD_SCROLL_PAUSE_MS,
    LCD_SCROLL_STEP_MS,
    LCD_SCL_PIN,
    LCD_SDA_PIN,
    LCD_WIDTH,
)

_lcd = None
_init_attempted = False
_BRAND = "Turtleback Robotics Academy"


def _fit_16(text):
    if text is None:
        return ""
    value = str(text)
    return value[:LCD_WIDTH]


def _line_frames(text):
    raw = "" if text is None else str(text)
    if len(raw) <= LCD_WIDTH:
        return [raw.ljust(LCD_WIDTH)]

    # Add spacing so wrapped text is readable before the next cycle.
    padded = raw + "   "
    frames = []
    for index in range(len(padded) - LCD_WIDTH + 1):
        frames.append(padded[index : index + LCD_WIDTH])
    return frames


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
        text1 = "" if line1 is None else str(line1)
        text2 = "" if line2 is None else str(line2)

        if not LCD_SCROLL_ENABLED:
            lcd.write(0, 0, _fit_16(text1))
            lcd.write(0, 1, _fit_16(text2))
            return True

        frames1 = _line_frames(text1)
        frames2 = _line_frames(text2)

        if len(frames1) == 1 and len(frames2) == 1:
            lcd.write(0, 0, frames1[0])
            lcd.write(0, 1, frames2[0])
            return True

        steps = max(len(frames1), len(frames2)) * max(1, LCD_SCROLL_CYCLES)
        for index in range(steps):
            lcd.write(0, 0, frames1[index % len(frames1)])
            lcd.write(0, 1, frames2[index % len(frames2)])
            time.sleep_ms(LCD_SCROLL_STEP_MS)

        time.sleep_ms(LCD_SCROLL_PAUSE_MS)
        return True
    except Exception:
        return False


def show_boot_message():
    show_lines(_BRAND, "Starting...")


def show_wifi_connecting(ssid):
    ssid_text = "Wi-Fi: " + ("" if ssid is None else str(ssid))
    show_lines(_BRAND, ssid_text)


def show_wifi_connected(ssid, ip_address):
    ssid_text = "Wi-Fi: " + ("" if ssid is None else str(ssid))
    ip_text = "IP: " + ("" if ip_address is None else str(ip_address))
    show_lines(ssid_text, ip_text)


def show_ap_mode(ap_name, ip_address):
    ap_text = "AP: " + ("" if ap_name is None else str(ap_name))
    ip_text = "IP: " + ("" if ip_address is None else str(ip_address))
    show_lines(ap_text, ip_text)


def show_wifi_error(message):
    show_lines(_BRAND, "Wi-Fi issue: " + ("" if message is None else str(message)))


def pulse_boot_complete():
    """Briefly show boot-complete text after startup LED sequence."""

    if show_lines(_BRAND, "Waiting Wi-Fi"):
        time.sleep_ms(700)
