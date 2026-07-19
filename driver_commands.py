"""Driver command parser that routes commands to isolated control modules."""

from config import STEERING_CENTER_ANGLE, STEERING_LEFT_ANGLE, STEERING_RIGHT_ANGLE

from ignition import start_engine, stop_engine, toggle_engine
from driving import set_vehicle_speed
from headlights import set_headlights, toggle_headlights
from police_lights import toggle_police_lights
from self_driving import stop_self_driving, toggle_self_driving
from steering import apply_steering_direct, set_steering_target
from turn_signals import (
    activate_left_signal,
    activate_right_signal,
    toggle_emergency_lights,
)


def process_driver_input(state, hardware, driver_input):
    """Convert input commands into state changes and control triggers."""

    if driver_input is None:
        return

    print("Driver input:", driver_input)

    if driver_input == "f":
        state.direction = 1
        print("Direction: forward")
        return

    if driver_input in ("engon", "engine_on", "engineon"):
        start_engine(state)
        print("Engine: ON")
        return

    if driver_input in ("engoff", "engine_off", "engineoff"):
        stop_engine(state, hardware)
        print("Engine: OFF")
        return

    if driver_input in ("eng", "engine"):
        toggle_engine(state, hardware)
        print("Engine:", "ON" if state.engine_enabled else "OFF")
        return

    if driver_input == "b":
        state.direction = -1
        print("Direction: reverse")
        return

    if driver_input == "l":
        set_steering_target(state, STEERING_LEFT_ANGLE)
        activate_left_signal(state)
        print("Steering: left")
        return

    if driver_input == "r":
        set_steering_target(state, STEERING_RIGHT_ANGLE)
        activate_right_signal(state)
        print("Steering: right")
        return

    if driver_input == "c":
        set_steering_target(state, STEERING_CENTER_ANGLE)
        print("Steering: center")
        return

    if driver_input == "e":
        toggle_emergency_lights(state)

        if state.emergency_lights_active:
            print("Emergency lights: ON")
        else:
            print("Emergency lights: OFF")
        return

    if driver_input in ("p", "police"):
        toggle_police_lights(state)
        print("Police lights:", "ON" if state.police_lights_enabled else "OFF")
        return

    if driver_input in ("auto", "sd", "selfdrive"):
        toggle_self_driving(state)
        return

    if driver_input == "h":
        toggle_headlights(state)
        print("Headlights:", "ON" if state.headlights_enabled else "OFF")
        return

    if driver_input in ("ho", "headlights_on", "headlight_on"):
        set_headlights(state, True)
        print("Headlights: ON")
        return

    if driver_input in ("hf", "headlights_off", "headlight_off"):
        set_headlights(state, False)
        print("Headlights: OFF")
        return

    if driver_input == "s":
        # Stop must cancel Auto, otherwise the next auto tick revs speed back up.
        stop_self_driving(state, stop_motor=True, announce=True)
        set_vehicle_speed(state, 0)
        return

    if driver_input.startswith("sa:"):
        try:
            requested_angle = int(driver_input.split(":", 1)[1])
        except ValueError:
            print("Invalid steering angle. Use sa:0-180")
            return

        apply_steering_direct(state, hardware, requested_angle)
        print("Steering angle:", state.steering_angle)
        return

    try:
        requested_speed = int(driver_input)
        set_vehicle_speed(state, requested_speed)
    except ValueError:
        print("Unknown command.")
        print("Use f, b, l, r, c, sa:0-180, e, p, auto, h, ho, hf, eng, engon, engoff, s, or speed 0-100.")
