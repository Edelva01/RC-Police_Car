"""HC-SR04 ultrasonic distance sensing."""

import time

from machine import disable_irq, enable_irq, time_pulse_us

from config import (
    DISTANCE_MAX_PULSE_US,
    DISTANCE_MIN_PULSE_US,
    DISTANCE_READ_INTERVAL_MS,
    DISTANCE_RETRY_COUNT,
    DISTANCE_STALE_MS,
    DISTANCE_TIMEOUT_US,
)


def update_distance(state, hardware):
    """
    Periodically measure distance into state.distance_cm.

    Keeps the last good reading briefly so Wi-Fi IRQ timeouts do not
    flicker the UI to "--" on every failed ping.
    """

    current_time = time.ticks_ms()
    elapsed = time.ticks_diff(current_time, state.last_distance_read_time)
    if elapsed < DISTANCE_READ_INTERVAL_MS:
        return

    state.last_distance_read_time = current_time
    reading = _read_distance_cm(hardware)

    if reading is not None:
        state.distance_cm = reading
        state.last_distance_good_ms = current_time
        return

    # No new good ping: keep prior value briefly, then clear.
    if state.distance_cm is None:
        return

    if time.ticks_diff(current_time, state.last_distance_good_ms) >= DISTANCE_STALE_MS:
        state.distance_cm = None


def _read_distance_cm(hardware):
    """Trigger HC-SR04 and convert echo pulse to centimeters."""

    for _ in range(DISTANCE_RETRY_COUNT):
        pulse_us = _measure_echo_pulse_us(hardware)
        if pulse_us is None:
            continue
        if pulse_us < DISTANCE_MIN_PULSE_US or pulse_us > DISTANCE_MAX_PULSE_US:
            continue
        return (pulse_us * 0.0343) / 2.0

    return None


def _measure_echo_pulse_us(hardware):
    """
    Fire a 10us TRIG pulse and time the ECHO high pulse.

    Interrupts are disabled during the wait so Wi-Fi activity does not
    abort time_pulse_us with false timeouts.
    """

    try:
        trig = hardware.ultrasonic_trig
        echo = hardware.ultrasonic_echo

        trig.value(0)
        time.sleep_us(5)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)

        irq_state = disable_irq()
        try:
            pulse_us = time_pulse_us(echo, 1, DISTANCE_TIMEOUT_US)
        finally:
            enable_irq(irq_state)
    except OSError:
        return None

    if pulse_us is None or pulse_us < 0:
        return None

    return pulse_us
