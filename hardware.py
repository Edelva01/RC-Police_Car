"""Hardware setup and low-level pin/PWM control."""

from machine import Pin, PWM
import sys
import uselect

from config import (
    BRAKE_LIGHT_PIN,
    HEADLIGHT_PIN,
    LEFT_SIGNAL_PIN,
    MOTOR_FORWARD_PIN,
    MOTOR_PWM_FREQUENCY,
    MOTOR_REVERSE_PIN,
    POLICE_LEFT_PIN,
    POLICE_RIGHT_PIN,
    RIGHT_SIGNAL_PIN,
    SERVO_MAX_PULSE_US,
    SERVO_MIN_PULSE_US,
    SERVO_PIN,
    SERVO_PWM_FREQUENCY,
    ULTRASONIC_ECHO_PIN,
    ULTRASONIC_TRIG_PIN,
)
from helpers import clamp, microseconds_to_duty_u16


class VehicleHardware:
    def __init__(self):
        # Digital outputs
        self.headlight_pin = Pin(HEADLIGHT_PIN, Pin.OUT)

        self.police_left_pin = Pin(POLICE_LEFT_PIN, Pin.OUT)
        self.police_right_pin = Pin(POLICE_RIGHT_PIN, Pin.OUT)

        self.brake_light_pin = Pin(BRAKE_LIGHT_PIN, Pin.OUT)

        self.left_signal_pin = Pin(LEFT_SIGNAL_PIN, Pin.OUT)
        self.right_signal_pin = Pin(RIGHT_SIGNAL_PIN, Pin.OUT)

        # HC-SR04 ultrasonic (TRIG out, ECHO in — ECHO must be 3.3V-safe)
        self.ultrasonic_trig = Pin(ULTRASONIC_TRIG_PIN, Pin.OUT)
        self.ultrasonic_echo = Pin(ULTRASONIC_ECHO_PIN, Pin.IN, Pin.PULL_DOWN)
        self.ultrasonic_trig.value(0)

        # Servo PWM
        self.servo_pwm = PWM(Pin(SERVO_PIN))
        self.servo_pwm.freq(SERVO_PWM_FREQUENCY)

        # Motor PWM
        self.motor_forward_pwm = PWM(Pin(MOTOR_FORWARD_PIN))
        self.motor_reverse_pwm = PWM(Pin(MOTOR_REVERSE_PIN))

        self.motor_forward_pwm.freq(MOTOR_PWM_FREQUENCY)
        self.motor_reverse_pwm.freq(MOTOR_PWM_FREQUENCY)

        self.motor_forward_pwm.duty_u16(0)
        self.motor_reverse_pwm.duty_u16(0)

        # Non-blocking serial input poller
        self.driver_input_poll = uselect.poll()
        self.driver_input_poll.register(sys.stdin, uselect.POLLIN)

    def set_servo_angle(self, angle):
        """Convert 0-180 degrees into a calibrated servo pulse."""

        angle = clamp(angle, 0, 180)

        pulse_range = SERVO_MAX_PULSE_US - SERVO_MIN_PULSE_US
        pulse_us = SERVO_MIN_PULSE_US + (angle * pulse_range / 180)

        duty_value = microseconds_to_duty_u16(pulse_us)
        self.servo_pwm.duty_u16(duty_value)

    def stop_all_hardware(self):
        self.motor_forward_pwm.duty_u16(0)
        self.motor_reverse_pwm.duty_u16(0)

        self.police_left_pin.value(0)
        self.police_right_pin.value(0)

        self.headlight_pin.value(0)
        self.brake_light_pin.value(0)

        self.left_signal_pin.value(0)
        self.right_signal_pin.value(0)

    def deinit(self):
        self.servo_pwm.duty_u16(0)
        self.servo_pwm.deinit()
        self.motor_forward_pwm.deinit()
        self.motor_reverse_pwm.deinit()
