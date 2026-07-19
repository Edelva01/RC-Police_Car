# Pico W Smart Police Car

MicroPython project for a Raspberry Pi Pico W RC car with browser (Wi-Fi) and USB serial control. Vehicle behavior lives in focused modules; the web page only sends commands and shows status.

## Features

- Browser control pad (cross layout) over Wi-Fi
- Boot Wi-Fi setup portal when no known network is available
- USB serial command input
- Steering servo, drive motor, headlights, turn signals, brake light, police lights
- Engine ON/OFF master switch (OFF stops outputs safely)
- Live car status panel in the web UI

## Requirements

- Raspberry Pi Pico W
- MicroPython with `network` / `socket` support
- PC tools: Python + [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)
- Same Wi-Fi network for phone/PC browser and the Pico W

## Project Structure

| File | Role |
|------|------|
| `main.py` | Startup, control loop, wires modules together |
| `config.py` | Pins, timing, steering angles, Wi-Fi, web port |
| `state.py` | Runtime vehicle state |
| `hardware.py` | Pin / PWM setup, servo pulse, shutdown helpers |
| `driver_commands.py` | Parses serial/web commands and routes to modules |
| `input_serial.py` | Non-blocking USB serial input |
| `web_control.py` | Embedded HTTP UI, `/command`, `/status` |
| `wifi_setup.py` | Join known Wi-Fi, or open setup portal for credentials |
| `distance.py` | HC-SR04 ultrasonic distance sensing |
| `self_driving.py` | Simple obstacle-avoid drive/steer logic |
| `ignition.py` | Engine on / off / toggle + safe resets |
| `driving.py` | Speed and motor PWM (with steering assist) |
| `steering.py` | Steering targets and smooth servo updates |
| `headlights.py` | Headlight on / off |
| `turn_signals.py` | Turn signals and emergency flashers |
| `brake_lights.py` | Brake light timing |
| `police_lights.py` | Police light flash at high speed |
| `helpers.py` | Shared helpers (clamp, PWM conversions) |
| `AGENTS.md` | Rules for coding agents working in this repo |

## Behavior Model

1. UI or serial sends a short command string.
2. `driver_commands.py` routes it.
3. Behavior modules update `VehicleState` and/or call `VehicleHardware`.
4. Each main-loop tick applies motor, steering, and lights from state.

Do not put vehicle logic in the HTML/JS. The page should only send commands and display `/status`.

## Hardware Pins (`config.py`)

| Function | GPIO | Notes |
|----------|------|--------|
| Servo (steering) | **GP13** | Must not share an RP2040 PWM slice with the motors |
| Motor forward | GP19 | PWM |
| Motor reverse | GP18 | PWM |
| Headlight | GP21 | Digital |
| Left turn signal | GP20 | Digital |
| Right turn signal | GP22 | Digital |
| Brake light | GP7 | Digital |
| Police left | GP1 | Digital |
| Police right | GP2 | Digital |
| Ultrasonic TRIG | **GP15** | HC-SR04 |
| Ultrasonic ECHO | **GP14** | HC-SR04 (level-shift to 3.3V) |

### Important: servo vs motor PWM

On the RP2040, PWM is shared by **hardware slice**, not just by pin.

- **GP3** and **GP19** both use PWM slice 1, channel B.
- If the servo is on GP3 while motors use GP18/GP19, speed changes move the servo and steering becomes unreliable.
- This project keeps the servo on **GP13** (PWM slice 6) so it does not fight the motor PWM.

Threading / using the second core does **not** fix that conflict. Correct pin wiring does.

## Steering Angles

Left / Center / Right are **fixed targets** (not step clicks):

| Control | Angle | Config constant |
|---------|-------|-----------------|
| Left | 45° | `STEERING_LEFT_ANGLE` |
| Center | 90° | `STEERING_CENTER_ANGLE` |
| Right | 135° | `STEERING_RIGHT_ANGLE` |

That is ±45° from center. The servo eases toward the target in steps of `STEERING_STEP_DEGREES` (default **6°**).

`Left` / `Right` also start the matching turn signal for `TURN_SIGNAL_DURATION_MS` (default **4 seconds**).

When steering changes while moving, **steering assist** briefly lowers motor power (`STEERING_ASSIST_MOTOR_FACTOR`, default 20% for `STEERING_ASSIST_DURATION_MS`) so the servo can hold better under load.

## Driver Commands

Commands work from the web UI and from USB serial (REPL / mpremote).

### Direction and speed

| Command | Action |
|---------|--------|
| `f` | Forward direction |
| `b` | Reverse direction |
| `s` | Stop motor (speed 0) |
| `0`–`100` | Set motor speed percent |

### Steering

| Command | Action |
|---------|--------|
| `l` | Steer left + left turn signal |
| `r` | Steer right + right turn signal |
| `c` | Center steering |
| `sa:n` | Set steering angle `n` (0–180). Available over serial; not on the main web pad |

### Lights

| Command | Action |
|---------|--------|
| `e` | Toggle emergency flashers |
| `p` | Toggle police lights |
| `auto` | Toggle self-driving (obstacle avoid) |
| `h` | Toggle headlights |
| `ho` | Headlights on |
| `hf` | Headlights off |

### Ignition

| Command | Action |
|---------|--------|
| `eng` | Toggle engine |
| `engon` | Engine on (clean idle) |
| `engoff` | Engine off (outputs low + reset) |

**Engine OFF** forces outputs low, clears speed, and recenters the steering target. **Engine ON** starts from a clean idle state.

## Web UI

When the program starts, the terminal prints the Pico address, for example:

```text
Web control ready at http://10.0.0.189:80
```

Open that URL on a device on the same Wi-Fi. After UI uploads, hard-refresh with **Ctrl+F5** so the browser drops a cached page.

### Layout

1. Brand header (white, bottom border separator)
2. Drive / steer **cross**:
   ```text
         Forward Dir
   Left    Center    Right
         Reverse Dir
   ```
3. Speed slider
4. **Set Speed** | **Stop**
5. Gap
6. **Engine** → **Headlight** → **Emergency** → **Police** → **Auto** → **Refresh Status**
7. Framed **Car status** panel (live `/status` text and brief “sent” feedback)

Toggle buttons use color/text from `/status` (on / off / emergency).

### HTTP endpoints

| Path | Purpose |
|------|---------|
| `/` | Control page HTML |
| `/command?cmd=...` | Send a driver command |
| `/status` | Plain-text vehicle state |

Example status line:

```text
speed=0, direction=forward, steering=90, emergency=off, headlights=on, engine=on
```

The browser queues requests (one in flight) so status polls and commands do not overwhelm the Pico HTTP loop.

## Setup and Deploy

1. Edit `config.py` only if you need pin or tuning changes. Wi-Fi credentials can be left blank.
2. Connect the Pico W over USB (example port: `COM3`).
3. Upload Python files (include the new `wifi_setup.py`):

   ```powershell
   py -m mpremote connect COM3 fs cp *.py :
   ```

   If the wildcard fails in your shell, copy files one by one, for example:

   ```powershell
   py -m mpremote connect COM3 fs cp main.py :main.py
   py -m mpremote connect COM3 fs cp config.py :config.py
   py -m mpremote connect COM3 fs cp wifi_setup.py :wifi_setup.py
   py -m mpremote connect COM3 fs cp web_control.py :web_control.py
   ```

4. Run:

   ```powershell
   py -m mpremote connect COM3 run main.py
   ```

5. **Wi-Fi modes**
   - **Home/school Wi-Fi:** if saved credentials work, the car joins that network and you drive at the printed IP.
   - **Pico Wi-Fi:** if no known network works, join open **`Turtleback-Car-Setup`**, open **`http://192.168.4.1/`**, and **drive right there**. The same page can optionally save home/school Wi-Fi for next time.

   Credentials are stored on the Pico in `wifi_secrets.json`. Optional factory defaults: `WIFI_SSID` / `WIFI_PASSWORD` in `config.py`.

6. Hard-refresh with **Ctrl+F5** if the control UI looks stale after an upload.

### COM port locked

If mpremote reports the port is in use, stop other `mpremote` / `python` sessions that are holding `COM3`, then upload or run again.

## Tuning (`config.py`)

Useful knobs:

| Setting | Meaning |
|---------|---------|
| `STEERING_LEFT_ANGLE` / `RIGHT` / `CENTER` | Button target angles |
| `STEERING_STEP_DEGREES` | Smoothness of servo motion |
| `STEERING_ASSIST_*` | Temporary motor cut during steer |
| `SERVO_MIN_PULSE_US` / `SERVO_MAX_PULSE_US` | Servo pulse calibration |
| `MAIN_LOOP_DELAY_MS` | Main loop pace (default 5 ms) |
| `WEB_PORT` | HTTP port (default 80) |
| `WEB_CONTROL_ENABLED` | Enable / disable Wi-Fi web server |
| `WIFI_SECRETS_FILE` | On-device saved credentials filename |
| `WIFI_SETUP_AP_SSID` | Open setup network name |
| `WIFI_SSID` / `WIFI_PASSWORD` | Optional factory defaults if no secrets file |

## Troubleshooting

| Symptom | Likely cause | What to try |
|---------|--------------|-------------|
| Servo moves when changing speed; Left/Right feel wrong | Servo wired to a PWM pin that conflicts with motors (e.g. GP3 with GP18/GP19) | Wire servo signal to **GP13** and keep `SERVO_PIN = 13` |
| Browser shows `ERR_CONNECTION_RESET` | Too many overlapping HTTP requests, or Pico stopped | Redeploy current `web_control.py`; confirm `main.py` is running; hard-refresh |
| Setup Wi-Fi `Turtleback-Car-Setup` appears | No saved credentials, or known network failed | Join that open network, open `http://192.168.4.1/`, drive there and/or save home Wi-Fi |
| UI looks old after an upload | Browser cache | **Ctrl+F5** |
| Web control never starts | Wi-Fi credentials / timeout | Check SSID/password and `WIFI_CONNECT_TIMEOUT_MS` |
| Nothing moves | Engine is off | Press **Engine** until status shows `engine=on` |
| `crypto.randomUUID is not a function` in console | Browser extension scripts (`content.js` / `read.js`), not this project | Ignore, or test in a private window with extensions off |

## Safety Notes

- Keep Engine OFF when working on wiring.
- Do not store secrets in README or sample docs; put Wi-Fi credentials only in local `config.py` on the device.
- Prefer copy-and-run / explicit mpremote steps over hidden automation for classroom setups.
# RC-Police_Car
