"""Driving control: speed changes and motor PWM output."""

import time

from config import STEERING_ASSIST_MOTOR_FACTOR
from helpers import clamp, speed_to_pwm


def set_vehicle_speed(state, new_speed, announce=True):
    """Update requested speed and trigger brake light on deceleration."""

    new_speed = clamp(new_speed, 0, 100)

    state.previous_speed = state.speed
    state.speed = new_speed

    if state.speed < state.previous_speed:
        state.brake_light_active = True
        state.brake_light_start_time = time.ticks_ms()

    if announce:
        print("Motor speed:", state.speed)


def update_motor(state, hardware):
    """Apply motor direction and speed to the forward/reverse PWM outputs."""

    effective_speed = state.speed

    # Briefly reduce motor output while steering updates to improve servo authority.
    if state.speed > 0 and time.ticks_diff(state.steering_assist_until_ms, time.ticks_ms()) > 0:
        effective_speed = int(state.speed * STEERING_ASSIST_MOTOR_FACTOR)

    motor_pwm_value = speed_to_pwm(effective_speed)

    if state.speed == 0:
        hardware.motor_forward_pwm.duty_u16(0)
        hardware.motor_reverse_pwm.duty_u16(0)
        return

    if state.direction == 1:
        hardware.motor_forward_pwm.duty_u16(motor_pwm_value)
        hardware.motor_reverse_pwm.duty_u16(0)
        return

    hardware.motor_forward_pwm.duty_u16(0)
    hardware.motor_reverse_pwm.duty_u16(motor_pwm_value)
