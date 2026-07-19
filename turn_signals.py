"""Turn signal and emergency light control."""

import time

from config import (
    TURN_SIGNAL_DURATION_MS,
    TURN_SIGNAL_FLASH_INTERVAL_MS,
)


def activate_left_signal(state):
    state.left_signal_active = True
    state.right_signal_active = False
    state.emergency_lights_active = False

    state.turn_signal_start_time = time.ticks_ms()
    state.last_turn_signal_toggle_time = time.ticks_ms()
    state.turn_signal_light_state = True


def activate_right_signal(state):
    state.left_signal_active = False
    state.right_signal_active = True
    state.emergency_lights_active = False

    state.turn_signal_start_time = time.ticks_ms()
    state.last_turn_signal_toggle_time = time.ticks_ms()
    state.turn_signal_light_state = True


def toggle_emergency_lights(state):
    state.emergency_lights_active = not state.emergency_lights_active

    state.left_signal_active = False
    state.right_signal_active = False

    state.turn_signal_light_state = True
    state.last_turn_signal_toggle_time = time.ticks_ms()


def _update_signal_flash_timer(state, current_time):
    elapsed_time = time.ticks_diff(current_time, state.last_turn_signal_toggle_time)

    if elapsed_time >= TURN_SIGNAL_FLASH_INTERVAL_MS:
        state.turn_signal_light_state = not state.turn_signal_light_state
        state.last_turn_signal_toggle_time = current_time


def update_turn_signals(state, hardware):
    current_time = time.ticks_ms()

    if state.emergency_lights_active:
        _update_signal_flash_timer(state, current_time)

        hardware.left_signal_pin.value(1 if state.turn_signal_light_state else 0)
        hardware.right_signal_pin.value(1 if state.turn_signal_light_state else 0)
        return

    if state.left_signal_active or state.right_signal_active:
        elapsed_signal_time = time.ticks_diff(current_time, state.turn_signal_start_time)

        if elapsed_signal_time >= TURN_SIGNAL_DURATION_MS:
            state.left_signal_active = False
            state.right_signal_active = False
            state.turn_signal_light_state = False

            hardware.left_signal_pin.value(0)
            hardware.right_signal_pin.value(0)
            return

    if not state.left_signal_active and not state.right_signal_active:
        hardware.left_signal_pin.value(0)
        hardware.right_signal_pin.value(0)
        state.turn_signal_light_state = False
        return

    _update_signal_flash_timer(state, current_time)

    if state.left_signal_active:
        hardware.left_signal_pin.value(1 if state.turn_signal_light_state else 0)
    else:
        hardware.left_signal_pin.value(0)

    if state.right_signal_active:
        hardware.right_signal_pin.value(1 if state.turn_signal_light_state else 0)
    else:
        hardware.right_signal_pin.value(0)
