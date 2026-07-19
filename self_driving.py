"""Self-driving: cruise with random turns, plus distance-based obstacle escapes."""

import random
import time

from config import (
    SELF_DRIVE_CRUISE_SPEED,
    SELF_DRIVE_ESCAPE_FORWARD_MS,
    SELF_DRIVE_REVERSE_MS,
    SELF_DRIVE_REVERSE_SPEED,
    SELF_DRIVE_SLOW_SPEED,
    SELF_DRIVE_STOP_CM,
    SELF_DRIVE_TURN_HOLD_MS,
    SELF_DRIVE_TURN_MAX_MS,
    SELF_DRIVE_TURN_MIN_MS,
    STEERING_CENTER_ANGLE,
    STEERING_LEFT_ANGLE,
    STEERING_RIGHT_ANGLE,
)
from driving import set_vehicle_speed
from steering import set_steering_target

_PHASE_IDLE = ""
_PHASE_REVERSE_RIGHT = "reverse_right"
_PHASE_FORWARD_LEFT = "forward_left"

_TURN_IDLE = ""
_TURN_ACTIVE = "turning"


def stop_self_driving(state, stop_motor=True, announce=True):
    """Force Auto off and cancel escape/random-turn maneuvers."""

    was_on = state.self_driving_enabled
    state.self_driving_enabled = False
    _reset_escape(state)
    _reset_random_turn(state)
    set_steering_target(state, STEERING_CENTER_ANGLE)

    if stop_motor:
        set_vehicle_speed(state, 0, announce=False)

    if announce and was_on:
        print("Self-driving: OFF")


def toggle_self_driving(state):
    """Enable or disable self-driving. Stopping auto also stops the motor."""

    if state.self_driving_enabled:
        stop_self_driving(state, stop_motor=True, announce=True)
        return

    state.self_driving_enabled = True
    _schedule_next_random_turn(state)
    print("Self-driving: ON")


def update_self_driving(state):
    """
    Main auto tick.

    Distance rules always run first. If they own the vehicle this cycle,
    cruise/random-turn logic is skipped until distance releases control.
    """

    if not state.self_driving_enabled:
        return

    if apply_distance_behavior(state):
        return

    apply_cruise_with_random_turns(state)


def apply_distance_behavior(state):
    """
    Distance-based drive control.

    Returns True when distance logic owns steering/speed this tick.
    Returns False when the path is clear enough for normal cruise.

    Rules:
    - no sensor reading: stop and center
    - <= STOP_CM: escape sequence
        1) reverse + right for SELF_DRIVE_REVERSE_MS
        2) forward + left for SELF_DRIVE_ESCAPE_FORWARD_MS
        3) center, then release back to cruise
    """

    if state.self_drive_phase != _PHASE_IDLE:
        _update_escape_maneuver(state)
        return True

    distance = state.distance_cm

    if distance is None:
        _apply_drive(state, direction=1, speed=0, steering_angle=STEERING_CENTER_ANGLE)
        return True

    if distance <= SELF_DRIVE_STOP_CM:
        _start_escape(state)
        _update_escape_maneuver(state)
        return True

    return False


def apply_cruise_with_random_turns(state):
    """Cruise at full auto speed, usually centered, with occasional random turns."""

    _ensure_turn_schedule(state)

    current_time = time.ticks_ms()

    if state.self_drive_turn_phase == _TURN_ACTIVE:
        elapsed = time.ticks_diff(current_time, state.self_drive_turn_started_ms)
        _apply_drive(
            state,
            direction=1,
            speed=SELF_DRIVE_CRUISE_SPEED,
            steering_angle=state.self_drive_turn_angle,
        )

        if elapsed >= SELF_DRIVE_TURN_HOLD_MS:
            _apply_drive(
                state,
                direction=1,
                speed=SELF_DRIVE_CRUISE_SPEED,
                steering_angle=STEERING_CENTER_ANGLE,
            )
            state.self_drive_turn_phase = _TURN_IDLE
            _schedule_next_random_turn(state)
        return

    if time.ticks_diff(state.self_drive_next_turn_ms, current_time) <= 0:
        _begin_random_turn(state)
        _apply_drive(
            state,
            direction=1,
            speed=SELF_DRIVE_CRUISE_SPEED,
            steering_angle=state.self_drive_turn_angle,
        )
        return

    _apply_drive(
        state,
        direction=1,
        speed=SELF_DRIVE_CRUISE_SPEED,
        steering_angle=STEERING_CENTER_ANGLE,
    )


def _start_escape(state):
    _reset_random_turn(state)
    state.self_drive_phase = _PHASE_REVERSE_RIGHT
    state.self_drive_phase_started_ms = time.ticks_ms()
    print("Self-driving: reverse + right")


def _reset_escape(state):
    state.self_drive_phase = _PHASE_IDLE
    state.self_drive_phase_started_ms = 0


def _update_escape_maneuver(state):
    """Timed reverse-right, then forward-left, then center."""

    current_time = time.ticks_ms()
    elapsed = time.ticks_diff(current_time, state.self_drive_phase_started_ms)

    if state.self_drive_phase == _PHASE_REVERSE_RIGHT:
        _apply_drive(
            state,
            direction=-1,
            speed=SELF_DRIVE_REVERSE_SPEED,
            steering_angle=STEERING_RIGHT_ANGLE,
        )

        if elapsed >= SELF_DRIVE_REVERSE_MS:
            state.self_drive_phase = _PHASE_FORWARD_LEFT
            state.self_drive_phase_started_ms = current_time
            print("Self-driving: forward + left")
        return

    if state.self_drive_phase == _PHASE_FORWARD_LEFT:
        _apply_drive(
            state,
            direction=1,
            speed=SELF_DRIVE_SLOW_SPEED,
            steering_angle=STEERING_LEFT_ANGLE,
        )

        if elapsed >= SELF_DRIVE_ESCAPE_FORWARD_MS:
            _apply_drive(
                state,
                direction=1,
                speed=SELF_DRIVE_CRUISE_SPEED,
                steering_angle=STEERING_CENTER_ANGLE,
            )
            _reset_escape(state)
            _schedule_next_random_turn(state)
            print("Self-driving: center")
        return

    _reset_escape(state)


def _ensure_turn_schedule(state):
    if state.self_drive_next_turn_ms == 0:
        _schedule_next_random_turn(state)


def _schedule_next_random_turn(state):
    wait_ms = random.randint(SELF_DRIVE_TURN_MIN_MS, SELF_DRIVE_TURN_MAX_MS)
    state.self_drive_next_turn_ms = time.ticks_add(time.ticks_ms(), wait_ms)
    state.self_drive_turn_phase = _TURN_IDLE


def _begin_random_turn(state):
    if random.randint(0, 1) == 0:
        state.self_drive_turn_angle = STEERING_LEFT_ANGLE
    else:
        state.self_drive_turn_angle = STEERING_RIGHT_ANGLE

    state.self_drive_turn_phase = _TURN_ACTIVE
    state.self_drive_turn_started_ms = time.ticks_ms()
    print("Self-driving: random turn")


def _reset_random_turn(state):
    state.self_drive_next_turn_ms = 0
    state.self_drive_turn_phase = _TURN_IDLE
    state.self_drive_turn_started_ms = 0
    state.self_drive_turn_angle = STEERING_CENTER_ANGLE


def _apply_drive(state, direction, speed, steering_angle):
    """Apply drive targets only when they change (avoids spam and jitter)."""

    if state.direction != direction:
        state.direction = direction

    if state.speed != speed:
        set_vehicle_speed(state, speed, announce=False)

    if state.steering_angle != steering_angle:
        set_steering_target(state, steering_angle)
