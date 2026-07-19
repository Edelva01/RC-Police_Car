"""Brake light control."""

import time

from config import BRAKE_LIGHT_DURATION_MS


def update_brake_light(state, hardware):
    if not state.brake_light_active:
        hardware.brake_light_pin.value(0)
        return

    hardware.brake_light_pin.value(1)

    current_time = time.ticks_ms()
    elapsed_time = time.ticks_diff(current_time, state.brake_light_start_time)

    if elapsed_time >= BRAKE_LIGHT_DURATION_MS:
        state.brake_light_active = False
        hardware.brake_light_pin.value(0)
