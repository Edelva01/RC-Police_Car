"""Main entrypoint for serial and browser control of the smart police car."""

import time

from brake_lights import update_brake_light
from distance import update_distance
from driving import update_motor
from headlights import update_headlights
from police_lights import update_police_lights
from self_driving import update_self_driving
from steering import update_steering
from turn_signals import update_turn_signals
from config import MAIN_LOOP_DELAY_MS, WEB_CONTROL_ENABLED
from driver_commands import process_driver_input
from hardware import VehicleHardware
from input_serial import get_driver_input
from state import VehicleState
from web_control import WebController
from wifi_setup import prepare_wifi


def _print_commands():
    print("RC vehicle ready.")
    print("")
    print("Driver inputs:")
    print("f     = forward direction")
    print("b     = reverse direction")
    print("l     = steer left and signal for 4 seconds")
    print("r     = steer right and signal for 4 seconds")
    print("c     = center steering")
    print("sa:n  = set steering angle n (0-180)")
    print("e     = toggle emergency lights")
    print("p     = toggle police lights")
    print("auto  = toggle self-driving")
    print("h     = toggle headlights")
    print("ho    = headlights ON")
    print("hf    = headlights OFF")
    print("eng   = toggle engine")
    print("engon = engine ON")
    print("engoff= engine OFF (all outputs zero)")
    print("s     = stop motor")
    print("0-100 = set motor speed")
    print("")


def main():
    state = VehicleState()
    hardware = VehicleHardware()
    web = WebController(state)

    hardware.stop_all_hardware()

    # Force the initial center command to be sent.
    state.last_servo_angle = None
    update_steering(state, hardware)

    if WEB_CONTROL_ENABLED:
        wifi_mode, wifi_ip = prepare_wifi()
        if wifi_mode:
            web.start(wifi_mode=wifi_mode, ip_address=wifi_ip)
        else:
            print("Web control skipped: Wi-Fi not ready")

    _print_commands()

    try:
        while True:
            serial_input = get_driver_input(hardware)
            process_driver_input(state, hardware, serial_input)

            web_input = web.poll_for_command()
            process_driver_input(state, hardware, web_input)

            # Keep distance updating even when the engine is off.
            update_distance(state, hardware)

            if not state.engine_enabled:
                hardware.stop_all_hardware()
                time.sleep_ms(MAIN_LOOP_DELAY_MS)
                continue

            update_self_driving(state)
            update_motor(state, hardware)
            update_steering(state, hardware)
            update_headlights(state, hardware)
            update_brake_light(state, hardware)
            update_turn_signals(state, hardware)
            update_police_lights(state, hardware)

            time.sleep_ms(MAIN_LOOP_DELAY_MS)

    except KeyboardInterrupt:
        print("Program stopped by user.")

    except Exception as error:
        print("Program error:", error)

    finally:
        web.stop()
        hardware.stop_all_hardware()
        hardware.deinit()


if __name__ == "__main__":
    main()
