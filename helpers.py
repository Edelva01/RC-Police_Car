"""General utility helpers used across modules."""


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def speed_to_pwm(speed_percent):
    """Convert a speed percentage from 0-100 into a 16-bit PWM value."""

    speed_percent = clamp(speed_percent, 0, 100)
    return int(speed_percent * 65535 / 100)


def microseconds_to_duty_u16(pulse_us):
    """Convert a servo pulse width in microseconds into duty_u16."""

    pwm_period_us = 20000
    return int(pulse_us * 65535 / pwm_period_us)
