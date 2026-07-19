# RC Police Car (Pico W)

MicroPython RC car for the **Raspberry Pi Pico W**: drive from a phone/PC browser over Wi‑Fi, or from USB serial. Vehicle behavior lives in focused Python modules; the web page only sends commands and shows live status.

**GitHub:** [Edelva01/RC-Police_Car](https://github.com/Edelva01/RC-Police_Car)

## Quick start

1. Flash [MicroPython](https://micropython.org/download/RPI_PICO_W/) on a Pico W.
2. On a PC with Python + [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html), open a terminal in this folder.
3. Upload and run (example USB port `COM3` on Windows):

```powershell
py -m mpremote connect COM3 fs cp *.py :
py -m mpremote connect COM3 run main.py
```

4. Open the printed URL (or join setup Wi‑Fi — see [Wi‑Fi](#wi-fi-setup)).
5. Hard-refresh the page with **Ctrl+F5** after UI uploads.

## Features

- Cross-layout drive pad (forward/reverse direction, left/center/right steer)
- Speed slider, **Set Speed**, and **Stop**
- **Engine** master switch (OFF zeros all outputs safely)
- Headlights, emergency flashers, police lights, brake light, turn signals
- Front **HC-SR04** distance in the status panel
- **Auto** self-driving: cruise, random turns, short obstacle escape
- **Stop** and **Engine OFF** both cancel Auto (so cruise cannot restart the motor)
- Boot Wi‑Fi setup portal when no home/school network is available
- USB serial commands (same language as the web UI)

## Requirements

| Item | Notes |
|------|--------|
| Raspberry Pi Pico W | MicroPython with `network` / `socket` |
| PC tools | Python 3 + `mpremote` |
| Browser | Same Wi‑Fi as the car (or join the Pico setup AP) |
| HC-SR04 (optional) | Needs **5 V** power; ECHO must be level-shifted to **3.3 V** for the Pico |

## Project structure

| File | Role |
|------|------|
| `main.py` | Startup, control loop, wires modules together |
| `config.py` | Pins, timing, steering, Wi‑Fi, web, distance, Auto tunables |
| `state.py` | Runtime vehicle state |
| `hardware.py` | Pin / PWM setup, servo pulse, shutdown helpers |
| `driver_commands.py` | Parses serial/web commands and routes to modules |
| `input_serial.py` | Non-blocking USB serial input |
| `web_control.py` | Embedded HTTP UI, `/command`, `/status`, `/wifi` |
| `wifi_setup.py` | Join known Wi‑Fi, or open setup portal for credentials |
| `distance.py` | HC-SR04 ultrasonic distance sensing |
| `self_driving.py` | Auto cruise, random turns, obstacle escape |
| `ignition.py` | Engine on / off / toggle + safe resets |
| `driving.py` | Speed and motor PWM (with steering assist) |
| `steering.py` | Steering targets and smooth servo updates |
| `headlights.py` | Headlight on / off |
| `turn_signals.py` | Turn signals and emergency flashers |
| `brake_lights.py` | Brake light timing |
| `police_lights.py` | Manual police flash + auto flash at high speed |
| `helpers.py` | Shared helpers (clamp, PWM conversions) |
| `.gitignore` | Ignores on-device `wifi_secrets.json` |
| `AGENTS.md` | Rules for coding agents working in this repo |

## How control works

1. UI or serial sends a short command string.
2. `driver_commands.py` routes it.
3. Behavior modules update `VehicleState` and/or call `VehicleHardware`.
4. Each main-loop tick applies motor, steering, lights, distance, and Auto from state.

Do **not** put vehicle logic in the HTML/JS. The page only sends commands and displays `/status`.

## Hardware pins (`config.py`)

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
| Ultrasonic ECHO | **GP14** | HC-SR04 — **level-shift 5 V → 3.3 V** |

### Servo vs motor PWM (important)

On the RP2040, PWM is shared by **hardware slice**, not only by pin.

- **GP3** and **GP19** both use PWM slice 1, channel B.
- If the servo is on GP3 while motors use GP18/GP19, speed changes move the servo.
- This project keeps the servo on **GP13** (PWM slice 6) so it does not fight the motor PWM.

Threading / the second core does **not** fix that conflict. Correct pin wiring does.

### Ultrasonic (HC-SR04)

| Wire | Connect to |
|------|------------|
| VCC | **5 V** (USB VBUS or a 5 V rail) — not ~2 V from two AA cells |
| GND | Common ground with the Pico |
| TRIG | GP15 (direct; 3.3 V is enough to trigger) |
| ECHO | Voltage divider or level shifter → **GP14** |

Example divider: ECHO → **1 kΩ** → GP14, and GP14 → **2 kΩ** → GND.

## Steering angles

Left / Center / Right are **fixed targets** (not step clicks):

| Control | Angle | Config constant |
|---------|-------|-----------------|
| Left | 45° | `STEERING_LEFT_ANGLE` |
| Center | 90° | `STEERING_CENTER_ANGLE` |
| Right | 135° | `STEERING_RIGHT_ANGLE` |

The servo eases toward the target in steps of `STEERING_STEP_DEGREES` (default **6°**).

`Left` / `Right` also start the matching turn signal for `TURN_SIGNAL_DURATION_MS` (default **4 seconds**).

While moving, **steering assist** briefly lowers motor power when steering changes (`STEERING_ASSIST_*` in `config.py`).

## Driver commands

Same commands work from the web UI and from USB serial (REPL / mpremote).

### Direction and speed

| Command | Action |
|---------|--------|
| `f` | Forward direction |
| `b` | Reverse direction |
| `s` | Stop motor **and cancel Auto** |
| `0`–`100` | Set motor speed percent |

### Steering

| Command | Action |
|---------|--------|
| `l` | Steer left + left turn signal |
| `r` | Steer right + right turn signal |
| `c` | Center steering |
| `sa:n` | Set steering angle `n` (0–180). Serial / command URL; not on the main pad |

### Lights and Auto

| Command | Action |
|---------|--------|
| `e` | Toggle emergency flashers |
| `p` | Toggle police lights |
| `auto` | Toggle self-driving |
| `h` | Toggle headlights |
| `ho` | Headlights on |
| `hf` | Headlights off |

### Ignition

| Command | Action |
|---------|--------|
| `eng` | Toggle engine |
| `engon` | Engine on (clean idle; Auto cleared) |
| `engoff` | Engine off (outputs low + reset; **Auto cancelled**) |

**Engine OFF** forces outputs low, clears speed, recenters steering, and turns Auto off. **Engine ON** starts from a clean idle state.

## Auto (self-driving)

When Auto is on:

- Cruise at `SELF_DRIVE_CRUISE_SPEED` (default **100**), steering centered
- Random left/right turns every **10–25 s**, held ~**1.5 s**, then re-center
- If distance ≤ `SELF_DRIVE_STOP_CM` (default **10 cm**): reverse + right turn, then forward + left, then center
- If distance is unavailable (`none`), Auto stops and centers

**Stop** (`s`) and **Engine OFF** both call `stop_self_driving()` so Auto cannot keep forcing speed.

## Web UI

When the program starts, the terminal prints the address, for example:

```text
Web control ready at http://10.0.0.189:80
```

Open that URL on a device on the same Wi‑Fi. After UI uploads, hard-refresh with **Ctrl+F5**.

### Layout

1. Brand header (tap the Wi‑Fi banner to open `/wifi` when available)
2. Drive / steer cross:
   ```text
         Forward Dir
   Left    Center    Right
         Reverse Dir
   ```
3. Speed slider
4. **Set Speed** | **Stop**
5. **Engine** → **Headlight** → **Emergency** → **Police** → **Auto** → **Refresh Status**
6. Framed **Car status** panel (live `/status` and brief “sent” feedback)

Toggle buttons take on/off color from `/status`.

### HTTP endpoints

| Path | Purpose |
|------|---------|
| `/` | Control page HTML |
| `/command?cmd=...` | Send a driver command |
| `/status` | Plain-text vehicle state |
| `/wifi` | Change / save Wi‑Fi credentials (STA mode) |

Example status line:

```text
mode=home-wifi, speed=0, direction=forward, steering=90, emergency=off, police=off, auto=off, headlights=on, engine=on, distance=324.5
```

The browser queues requests (one in flight) so status polls and commands do not overwhelm the Pico’s single-accept HTTP loop.

## Wi‑Fi setup

| Mode | What happens |
|------|----------------|
| **Home / school Wi‑Fi** | Saved credentials work → car joins that network → drive at the printed IP |
| **Setup AP** | No known network → join open **`Turtleback-Car-Setup`** → open **`http://192.168.4.1/`** → drive and/or save home Wi‑Fi |

Credentials are stored **on the Pico only** in `wifi_secrets.json` (gitignored). Optional empty factory defaults: `WIFI_SSID` / `WIFI_PASSWORD` in `config.py` — do not commit real passwords.

### Deploy tips

```powershell
# Full upload (if shell wildcard works)
py -m mpremote connect COM3 fs cp *.py :

# Or copy one file at a time
py -m mpremote connect COM3 fs cp main.py :main.py
py -m mpremote connect COM3 fs cp web_control.py :web_control.py

py -m mpremote connect COM3 run main.py
```

If mpremote says the port is in use, stop other `mpremote` / Python sessions holding `COM3`, then retry.

## Tuning (`config.py`)

| Setting | Meaning |
|---------|---------|
| `STEERING_LEFT_ANGLE` / `RIGHT` / `CENTER` | Button target angles |
| `STEERING_STEP_DEGREES` | Smoothness of servo motion |
| `STEERING_ASSIST_*` | Temporary motor cut during steer |
| `SERVO_MIN_PULSE_US` / `SERVO_MAX_PULSE_US` | Servo pulse calibration |
| `POLICE_SPEED_THRESHOLD` | Auto police flash above this speed |
| `POLICE_FLASH_INTERVAL_MS` | Police blink rate |
| `SELF_DRIVE_STOP_CM` | Obstacle distance that triggers escape |
| `SELF_DRIVE_CRUISE_SPEED` | Auto cruise speed |
| `SELF_DRIVE_REVERSE_MS` / `ESCAPE_FORWARD_MS` | Escape maneuver timings |
| `SELF_DRIVE_TURN_*` | Random cruise turn window / hold |
| `DISTANCE_*` | Ultrasonic poll / timeout / stale hold |
| `MAIN_LOOP_DELAY_MS` | Main loop pace (default 5 ms) |
| `WEB_PORT` | HTTP port (default 80) |
| `WIFI_SETUP_AP_SSID` | Open setup network name |

## Troubleshooting

| Symptom | Likely cause | What to try |
|---------|--------------|-------------|
| Servo jumps when changing speed | Servo on PWM slice shared with motors (e.g. GP3) | Wire servo to **GP13** |
| Distance always `--` / useless | Sensor on ~2 V, or ECHO not level-shifted | Power HC-SR04 at **5 V**; divider on ECHO → GP14 |
| Auto comes back after Stop | Old firmware without interrupt fix | Redeploy `self_driving.py`, `driver_commands.py`, `ignition.py` |
| Browser `ERR_CONNECTION_RESET` | Overlapping HTTP, or Pico stopped | Confirm `main.py` running; hard-refresh; current `web_control.py` |
| Setup Wi‑Fi appears | No saved credentials or join failed | Join `Turtleback-Car-Setup`, open `http://192.168.4.1/` |
| UI looks old after upload | Browser cache | **Ctrl+F5** |
| Nothing moves | Engine off | Press **Engine** until `engine=on` |
| `crypto.randomUUID` console noise | Browser extension, not this project | Ignore or use a private window |

## Safety

- Keep **Engine OFF** when working on wiring.
- Never commit Wi‑Fi passwords; use the on-device portal / `wifi_secrets.json` only on the Pico.
- Prefer explicit mpremote upload/run steps in classroom labs (no hidden automation).
- Pico GPIO is **3.3 V** — do not feed 5 V ECHO straight into GP14.
