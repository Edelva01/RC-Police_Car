"""Project configuration for the Pico W smart police car."""

# =========================================================
# PIN ASSIGNMENTS
# =========================================================

HEADLIGHT_PIN = 21

POLICE_LEFT_PIN = 1
POLICE_RIGHT_PIN = 2

BRAKE_LIGHT_PIN = 7

LEFT_SIGNAL_PIN = 20
RIGHT_SIGNAL_PIN = 22

# Servo MUST NOT share an RP2040 PWM slice with the motor pins.
# GP3 is PWM slice 1 channel B — the same as motor reverse on GP19.
# Using GP3 and GP18/GP19 together makes speed changes move the servo
# and prevents reliable steering. GP13 is PWM slice 6 (no conflict).
SERVO_PIN = 13

MOTOR_FORWARD_PIN = 19
MOTOR_REVERSE_PIN = 18


# =========================================================
# VEHICLE SETTINGS
# =========================================================

MOTOR_PWM_FREQUENCY = 1000
SERVO_PWM_FREQUENCY = 50

POLICE_SPEED_THRESHOLD = 70
POLICE_FLASH_INTERVAL_MS = 125

TURN_SIGNAL_FLASH_INTERVAL_MS = 350
TURN_SIGNAL_DURATION_MS = 4000

BRAKE_LIGHT_DURATION_MS = 700

MAIN_LOOP_DELAY_MS = 5


# =========================================================
# STEERING SETTINGS
# =========================================================

STEERING_LEFT_ANGLE = 45
STEERING_CENTER_ANGLE = 90
STEERING_RIGHT_ANGLE = 135

# Servo movement tuning.
# Smaller step gives smoother turns; larger step gives faster response.
STEERING_STEP_DEGREES = 6

# Minimum time between steering updates.
STEERING_UPDATE_INTERVAL_MS = 10

# Re-send the current target occasionally to keep hold stable.
STEERING_HOLD_REFRESH_MS = 100

# Steering assist lowers motor power briefly when steering changes.
# This helps when servo and motor share power and steering stalls under throttle.
STEERING_ASSIST_DURATION_MS = 280
STEERING_ASSIST_MOTOR_FACTOR = 0.20

# Servo pulse calibration in microseconds.
SERVO_MIN_PULSE_US = 950
SERVO_MAX_PULSE_US = 2050


# =========================================================
# WEB CONTROL SETTINGS
# =========================================================

WEB_CONTROL_ENABLED = True
WEB_PORT = 80
WIFI_CONNECT_TIMEOUT_MS = 10000

# Optional factory defaults used when wifi_secrets.json is missing.
# Prefer saving credentials via the boot setup portal (open AP).
WIFI_SSID = ""
WIFI_PASSWORD = ""

# Saved credentials file on the Pico flash (created by the setup portal).
WIFI_SECRETS_FILE = "wifi_secrets.json"

# Open setup network shown when no Wi-Fi works yet.
WIFI_SETUP_AP_SSID = "Turtleback-Car-Setup"
WIFI_SETUP_AP_CHANNEL = 6


# =========================================================
# ULTRASONIC DISTANCE (HC-SR04)
# =========================================================

# ECHO must be level-shifted to 3.3V (sensor ECHO is 5V).
ULTRASONIC_TRIG_PIN = 15
ULTRASONIC_ECHO_PIN = 14

# How often to ping the sensor (keeps the main loop responsive).
DISTANCE_READ_INTERVAL_MS = 100

# Max wait for echo (about 3+ meters). Negative return means timeout.
DISTANCE_TIMEOUT_US = 20000

# Valid echo pulse window (~2 cm to ~4 m).
DISTANCE_MIN_PULSE_US = 100
DISTANCE_MAX_PULSE_US = 25000

# Retries per update (helps when Wi-Fi briefly interferes).
DISTANCE_RETRY_COUNT = 3

# Keep last good reading this long before UI shows "--".
DISTANCE_STALE_MS = 800


# =========================================================
# SELF-DRIVING (simple obstacle avoid)
# =========================================================

# Distance bands in centimeters (front HC-SR04).
SELF_DRIVE_STOP_CM = 10

# Speeds used by self-driving (0-100).
SELF_DRIVE_CRUISE_SPEED = 100
SELF_DRIVE_SLOW_SPEED = 40
SELF_DRIVE_REVERSE_SPEED = 40

# Close-obstacle escape maneuver timings.
SELF_DRIVE_REVERSE_MS = 5000
SELF_DRIVE_ESCAPE_FORWARD_MS = 2500

# Random cruise turns (steering leaves center for TURN_HOLD, then re-centers).
SELF_DRIVE_TURN_MIN_MS = 10000
SELF_DRIVE_TURN_MAX_MS = 25000
SELF_DRIVE_TURN_HOLD_MS = 1500
