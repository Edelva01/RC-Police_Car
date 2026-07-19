"""Police light control."""

import time

from config import POLICE_FLASH_INTERVAL_MS, POLICE_SPEED_THRESHOLD


def toggle_police_lights(state):
    """Toggle manual police-light flashing on or off."""

    state.police_lights_enabled = not state.police_lights_enabled

    if not state.police_lights_enabled:
        state.police_light_state = False


def set_police_lights(state, enabled):
    """Force police lights on or off."""

    state.police_lights_enabled = bool(enabled)

    if not state.police_lights_enabled:
        state.police_light_state = False


def update_police_lights(state, hardware):
    """Flash police lights when enabled or when speed is above threshold."""

    active = state.police_lights_enabled or state.speed > POLICE_SPEED_THRESHOLD

    if not active:
        hardware.police_left_pin.value(0)
        hardware.police_right_pin.value(0)
        state.police_light_state = False
        state.last_police_toggle_time = time.ticks_ms()
        return

    current_time = time.ticks_ms()
    elapsed_time = time.ticks_diff(current_time, state.last_police_toggle_time)

    if elapsed_time >= POLICE_FLASH_INTERVAL_MS:
        state.police_light_state = not state.police_light_state
        state.last_police_toggle_time = current_time

    if state.police_light_state:
        hardware.police_left_pin.value(1)
        hardware.police_right_pin.value(0)
    else:
        hardware.police_left_pin.value(0)
        hardware.police_right_pin.value(1)
