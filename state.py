"""Vehicle runtime state container."""

import time

from config import STEERING_CENTER_ANGLE


class VehicleState:
    def __init__(self):
        # Speed and direction
        self.speed = 0
        self.previous_speed = 0
        self.direction = 1

        # Steering
        self.steering_angle = STEERING_CENTER_ANGLE
        self.last_servo_angle = None
        self.last_servo_update_time = 0
        self.last_servo_write_time = 0
        self.steering_assist_until_ms = 0

        # Headlights
        self.headlights_enabled = True

        # Engine output master state
        self.engine_enabled = True

        # Turn signals
        self.left_signal_active = False
        self.right_signal_active = False
        self.emergency_lights_active = False

        self.turn_signal_light_state = False
        self.turn_signal_start_time = 0
        self.last_turn_signal_toggle_time = time.ticks_ms()

        # Brake light
        self.brake_light_active = False
        self.brake_light_start_time = 0

        # Police lights
        self.police_lights_enabled = False
        self.police_light_state = False
        self.last_police_toggle_time = time.ticks_ms()

        # Ultrasonic distance (cm); None means no valid reading yet / timeout
        self.distance_cm = None
        self.last_distance_read_time = 0
        self.last_distance_good_ms = 0

        # Self-driving (obstacle avoid)
        self.self_driving_enabled = False
        self.self_drive_phase = ""
        self.self_drive_phase_started_ms = 0
        self.self_drive_next_turn_ms = 0
        self.self_drive_turn_phase = ""
        self.self_drive_turn_started_ms = 0
        self.self_drive_turn_angle = STEERING_CENTER_ANGLE
