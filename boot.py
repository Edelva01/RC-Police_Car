from machine import Pin
import time
from lcd_display import pulse_boot_complete, show_boot_message

led = Pin("LED", Pin.OUT)

show_boot_message()

# Boot indication
for i in range(3):
    led.on()
    time.sleep(0.2)
    led.off()
    time.sleep(0.2)

# Leave on when ready
led.on()
pulse_boot_complete()