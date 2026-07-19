"""Boot Wi-Fi: join a known network, or open Pico AP for direct drive + setup."""

import json
import time

from config import (
    WIFI_CONNECT_TIMEOUT_MS,
    WIFI_PASSWORD,
    WIFI_SECRETS_FILE,
    WIFI_SETUP_AP_CHANNEL,
    WIFI_SETUP_AP_SSID,
    WIFI_SSID,
)


def load_wifi_credentials():
    """Load SSID/password from flash file, else fall back to config.py values."""

    try:
        with open(WIFI_SECRETS_FILE, "r") as handle:
            data = json.load(handle)
        ssid = str(data.get("ssid", "")).strip()
        password = str(data.get("password", ""))
        if ssid:
            return ssid, password
    except (OSError, ValueError, TypeError):
        pass

    return WIFI_SSID.strip(), WIFI_PASSWORD


def save_wifi_credentials(ssid, password):
    """Persist Wi-Fi credentials to flash. Never log the password."""

    ssid = (ssid or "").strip()
    password = password or ""

    if ssid == "":
        return False, "Wi-Fi name cannot be empty."

    if len(ssid) > 32:
        return False, "Wi-Fi name is too long."

    if len(password) > 64:
        return False, "Password is too long."

    payload = {"ssid": ssid, "password": password}

    try:
        with open(WIFI_SECRETS_FILE, "w") as handle:
            json.dump(payload, handle)
    except OSError:
        return False, "Could not save Wi-Fi settings on the car."

    return True, "Saved."


def url_decode(value):
    if value is None:
        return ""

    value = value.replace("+", " ")
    out = []
    index = 0

    while index < len(value):
        ch = value[index]
        if ch == "%" and index + 2 < len(value):
            hex_text = value[index + 1 : index + 3]
            try:
                out.append(chr(int(hex_text, 16)))
                index += 3
                continue
            except ValueError:
                pass

        out.append(ch)
        index += 1

    return "".join(out)


def parse_form_body(body_text):
    """Parse application/x-www-form-urlencoded body into a dict."""

    fields = {}
    if not body_text:
        return fields

    for part in body_text.split("&"):
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        fields[url_decode(key)] = url_decode(value)

    return fields


def connect_station(ssid, password, timeout_ms=None):
    """Try joining an access point. Returns (ok, ip_or_message)."""

    if timeout_ms is None:
        timeout_ms = WIFI_CONNECT_TIMEOUT_MS

    if not ssid:
        return False, "No Wi-Fi name set."

    try:
        import network
    except ImportError:
        return False, "network module missing"

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    try:
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep_ms(200)
    except OSError:
        pass

    print("Connecting Wi-Fi to:", ssid)
    try:
        wlan.connect(ssid, password)
    except OSError as error:
        return False, "Connect failed: %s" % error

    start_time = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start_time) >= timeout_ms:
            return False, "Wi-Fi connection timeout"
        time.sleep_ms(200)

    ip_address = wlan.ifconfig()[0]
    print("Wi-Fi connected:", ip_address)
    return True, ip_address


def stop_access_point():
    try:
        import network
    except ImportError:
        return

    ap = network.WLAN(network.AP_IF)
    try:
        if ap.active():
            ap.active(False)
    except OSError:
        pass


def start_open_access_point():
    """Start open Pico setup/drive AP. Returns (ok, ip_or_error)."""

    try:
        import network
    except ImportError:
        return False, "network module missing"

    sta = network.WLAN(network.STA_IF)
    sta.active(True)

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    try:
        ap.config(
            essid=WIFI_SETUP_AP_SSID,
            channel=WIFI_SETUP_AP_CHANNEL,
            security=0,
        )
    except (OSError, ValueError, TypeError):
        try:
            ap.config(essid=WIFI_SETUP_AP_SSID)
        except OSError as error:
            return False, "Could not start Pico Wi-Fi: %s" % error

    ip_address = ap.ifconfig()[0]
    return True, ip_address


def prepare_wifi():
    """
    Join known Wi-Fi, or start Pico open AP for direct drive + credential setup.

    Returns:
      ("sta", ip) — joined a known network
      ("ap", ip) — Pico AP is up (drive + setup at that address)
      (None, None) — networking unavailable
    """

    try:
        import network
    except ImportError:
        print("Web control unavailable: network module not found")
        return None, None

    ssid, password = load_wifi_credentials()

    if ssid:
        ok, result = connect_station(ssid, password)
        if ok:
            return "sta", result
        print("Known Wi-Fi failed:", result)
    else:
        print("No saved Wi-Fi credentials.")

    ap_ok, ap_info = start_open_access_point()
    if not ap_ok:
        print(ap_info)
        return None, None

    print("Pico Wi-Fi ready for direct drive + setup.")
    print("1) Join open Wi-Fi:", WIFI_SETUP_AP_SSID)
    print("2) Open http://%s/" % ap_info)
    print("   Drive the car here, or save home/school Wi-Fi below on the page.")
    return "ap", ap_info
