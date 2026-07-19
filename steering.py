"""Steering control: smooth, timed servo position updates."""

import time

from config import (
    STEERING_ASSIST_DURATION_MS,
    STEERING_HOLD_REFRESH_MS,
    STEERING_STEP_DEGREES,
    STEERING_UPDATE_INTERVAL_MS,
)
from helpers import clamp


def set_steering_target(state, angle):
    """Set a steering target angle and start steering assist window."""

    state.steering_angle = clamp(int(angle), 0, 180)
    state.steering_assist_until_ms = time.ticks_add(
        time.ticks_ms(),
        STEERING_ASSIST_DURATION_MS,
    )


def apply_steering_direct(state, hardware, angle):
    """Apply steering immediately for direct UI bar control."""

    set_steering_target(state, angle)

    current_time = time.ticks_ms()
    hardware.set_servo_angle(state.steering_angle)
    state.last_servo_angle = state.steering_angle
    state.last_servo_update_time = current_time
    state.last_servo_write_time = current_time


def _step_toward(current_value, target_value, step_size):
    if current_value < target_value:
        return min(current_value + step_size, target_value)

    if current_value > target_value:
        return max(current_value - step_size, target_value)

    return current_value


def update_steering(state, hardware):
    """Move toward target steering angle in timed steps and refresh hold."""

    current_time = time.ticks_ms()

    if state.last_servo_angle is None:
        hardware.set_servo_angle(state.steering_angle)
        state.last_servo_angle = state.steering_angle
        state.last_servo_update_time = current_time
        state.last_servo_write_time = current_time
        return

    elapsed_update_time = time.ticks_diff(current_time, state.last_servo_update_time)
    if elapsed_update_time < STEERING_UPDATE_INTERVAL_MS:
        return

    if state.last_servo_angle != state.steering_angle:
        next_angle = _step_toward(
            state.last_servo_angle,
            state.steering_angle,
            STEERING_STEP_DEGREES,
        )

        hardware.set_servo_angle(next_angle)
        state.last_servo_angle = next_angle
        state.last_servo_update_time = current_time
        state.last_servo_write_time = current_time
        return

    elapsed_hold_time = time.ticks_diff(current_time, state.last_servo_write_time)
    if elapsed_hold_time >= STEERING_HOLD_REFRESH_MS:
        hardware.set_servo_angle(state.steering_angle)
        state.last_servo_write_time = current_time
        state.last_servo_update_time = current_time
