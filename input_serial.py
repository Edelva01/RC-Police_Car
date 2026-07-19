"""Serial command input helpers."""

import sys


def get_driver_input(hardware):
    """Return a new serial command, or None if no command is available."""

    events = hardware.driver_input_poll.poll(0)
    if not events:
        return None

    driver_input = sys.stdin.readline().strip().lower()
    if driver_input == "":
        return None

    return driver_input
