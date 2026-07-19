"""Headlight control."""


def set_headlights(state, enabled):
    state.headlights_enabled = bool(enabled)


def toggle_headlights(state):
    state.headlights_enabled = not state.headlights_enabled


def update_headlights(state, hardware):
    """Apply requested headlight state."""

    hardware.headlight_pin.value(1 if state.headlights_enabled else 0)
