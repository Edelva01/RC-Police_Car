"""Engine state control without stopping the program loop."""

import time

from config import STEERING_CENTER_ANGLE
from self_driving import stop_self_driving


def start_engine(state):
    """Enable normal output updates."""

    stop_self_driving(state, stop_motor=True, announce=False)

    state.engine_enabled = True

    # Start in a known idle state and wait for explicit commands.
    state.speed = 0
    state.previous_speed = 0
    state.direction = 1

    state.steering_angle = STEERING_CENTER_ANGLE

    state.headlights_enabled = True

    state.brake_light_active = False
    state.brake_light_start_time = 0

    state.left_signal_active = False
    state.right_signal_active = False
    state.emergency_lights_active = False

    state.turn_signal_light_state = False
    state.turn_signal_start_time = 0
    state.last_turn_signal_toggle_time = time.ticks_ms()

    state.police_lights_enabled = False
    state.police_light_state = False
    state.last_police_toggle_time = time.ticks_ms()


def toggle_engine(state, hardware):
    if state.engine_enabled:
        stop_engine(state, hardware)
        return

    start_engine(state)


def stop_engine(state, hardware):
    """Disable outputs and force all hardware pins/PWM to zero."""

    stop_self_driving(state, stop_motor=True, announce=True)

    state.engine_enabled = False

    # Reset dynamic outputs so restart begins in a known-safe state.
    state.speed = 0
    state.previous_speed = 0
    state.direction = 1

    state.steering_angle = STEERING_CENTER_ANGLE
    state.last_servo_angle = None

    state.headlights_enabled = False

    state.brake_light_active = False
    state.brake_light_start_time = 0

    state.left_signal_active = False
    state.right_signal_active = False
    state.emergency_lights_active = False

    state.turn_signal_light_state = False
    state.turn_signal_start_time = 0
    state.last_turn_signal_toggle_time = time.ticks_ms()

    state.police_lights_enabled = False
    state.police_light_state = False
    state.last_police_toggle_time = time.ticks_ms()

    # Center steering before output shutdown.
    hardware.set_servo_angle(STEERING_CENTER_ANGLE)

    hardware.stop_all_hardware()
