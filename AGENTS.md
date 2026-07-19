# Agent Rules

## Core Rules

1. Keep behavior logic in dedicated behavior modules.
2. Do not move behavior logic into web HTML/JS.
3. Keep command parsing in `driver_commands.py`.
4. Keep hardware pin/PWM handling in `hardware.py`.
5. Keep all tunable constants in `config.py`.
6. Wi-Fi join / credential portal logic stays in `wifi_setup.py`.

## File Ownership

- `driving.py`: motor speed/direction behavior
- `steering.py`: steering target + servo update behavior
- `headlights.py`: headlight behavior
- `turn_signals.py`: turn/emergency behavior
- `brake_lights.py`: brake behavior
- `police_lights.py`: police lights behavior
- `distance.py`: HC-SR04 distance sensing
- `self_driving.py`: obstacle-avoid self-driving
- `ignition.py`: engine on/off/toggle + reset rules
- `wifi_setup.py`: station join + open setup portal for credentials
- `web_control.py`: car control HTTP UI only (expects Wi-Fi already up)

## Web/UI Contract

1. Web UI should only send commands and display state.
2. `/status` must be the source of truth for button states.
3. Toggle buttons should reflect current ON/OFF state by color and text.

## Safety Rules

1. Engine OFF must force all outputs low.
2. Engine OFF must reset speed to 0 and steering target to center.
3. Engine ON must start from a clean idle state.

## Change Process

1. Update behavior module first.
2. Update `driver_commands.py` routing second.
3. Update web controls last.
4. Validate by running on Pico and checking startup command list.

## Deployment

- Preferred run command:
  - `py -m mpremote connect COM3 run main.py`
- If COM3 is locked, stop stale mpremote/python processes before upload or run.
