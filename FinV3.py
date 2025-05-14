import board
import neopixel
import time
import analogio
from digitalio import DigitalInOut, Direction, Pull

# --- Configuration Constants ---
SWITCH_PIN = board.D3
PHOTOCELL_PIN = board.A2
PIXEL_PIN = board.D2

NUM_PIXELS = 8
PIXEL_BRIGHTNESS = 0.1 # Lowered brightness for testing, reduces power draw

CLICK_INTERVAL = 0.5  # Seconds to distinguish single/double click
MAIN_LOOP_DELAY = 0.1 # Seconds, affects responsiveness and loop frequency

PHOTOCELL_THRESHOLD = 35000  # ADC value, lower means darker

# PhotoAlert blink timings
ALERT_ON_TIME = 0.2
ALERT_OFF_TIME = 0.1
ALERT_REPETITIONS = 2 # Number of ON-OFF cycles for the alert

DEBUG_PRINT = False # Set to True for verbose debug console output

# --- Color Definitions (Simplified) ---
# Using dim colors to reduce power draw
SIMPLE_ON_COLOR_PIXEL_0 = (50, 0, 0) # Dim Red for the first pixel
OFF_COLOR = (0, 0, 0)
ALERT_COLOR_PHOTOCELL_ENABLED = (0, 30, 30) # Dim Cyan
ALERT_COLOR_PHOTOCELL_DISABLED = (30, 30, 0) # Dim Yellow


# --- Hardware Setup ---
# Switch
switch = DigitalInOut(SWITCH_PIN)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# Photocell
photocell = analogio.AnalogIn(PHOTOCELL_PIN)

# NeoPixels
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=PIXEL_BRIGHTNESS, auto_write=False)

# --- Global State Variables ---
last_switch_state = True
override_mode_active = False
photocell_control_enabled = True
click_time = 0
leds_currently_on = False # Tracks if the simple pattern is physically displayed

# --- LED Effect Functions (Simplified) ---
def set_simple_pattern_on():
    """Turns on a very simple pattern (first pixel red, rest off)."""
    global leds_currently_on
    # This function is called when we know the LEDs *should* be on and *are not*.
    for i in range(NUM_PIXELS):
        pixels[i] = OFF_COLOR
    pixels[0] = SIMPLE_ON_COLOR_PIXEL_0
    pixels.show()
    leds_currently_on = True
    if DEBUG_PRINT: print("LEDs: Simple Pattern ON")

def set_pixels_off():
    """Turns all pixels off."""
    global leds_currently_on
    # This function is called when we know the LEDs *should* be off and *are not*.
    pixels.fill(OFF_COLOR)
    pixels.show()
    leds_currently_on = False
    if DEBUG_PRINT: print("LEDs: All OFF")

def photoAlert():
    """Flashes pixels to indicate a mode change."""
    global leds_currently_on
    if DEBUG_PRINT: print("PhotoAlert: Starting...")

    alert_color = ALERT_COLOR_PHOTOCELL_ENABLED if photocell_control_enabled else ALERT_COLOR_PHOTOCELL_DISABLED

    for _ in range(ALERT_REPETITIONS):
        pixels.fill(alert_color)
        pixels.show()
        time.sleep(ALERT_ON_TIME)
        pixels.fill(OFF_COLOR)
        pixels.show()
        time.sleep(ALERT_OFF_TIME)

    # After the alert, the LEDs are physically off.
    # Update our state tracking variable. The main loop will decide the next state.
    leds_currently_on = False
    if DEBUG_PRINT: print("PhotoAlert: Finished. LEDs left off, leds_currently_on = False.")

# --- Main Loop ---
if DEBUG_PRINT: print("Device starting... Initializing LEDs to OFF.")
pixels.fill(OFF_COLOR)
pixels.show()
leds_currently_on = False

while True:
    current_time = time.monotonic()
    current_switch_state = switch.value
    photocell_value = photocell.value

    if DEBUG_PRINT:
        print("Loop: Time={:.2f}, Switch={}, LastSw={}, Override={}, PCtrl={}, PCval={}, ClickT={:.2f}, LEDsOn={}".format(
            current_time, current_switch_state, last_switch_state, override_mode_active,
            photocell_control_enabled, photocell_value, click_time, leds_currently_on
        ))

    # --- Button Press Detection (Falling Edge: True to False) ---
    if last_switch_state and not current_switch_state:
        if DEBUG_PRINT: print("Button Press Detected (Falling Edge)")
        if click_time > 0 and (current_time - click_time) < CLICK_INTERVAL:
            photocell_control_enabled = not photocell_control_enabled
            if DEBUG_PRINT:
                print("Double-click: photocell_control_enabled toggled to {}".format(photocell_control_enabled))
            photoAlert() # This will leave LEDs off and set leds_currently_on=False
            click_time = 0
        else:
            click_time = current_time
            if DEBUG_PRINT: print("First click registered at {:.2f}".format(click_time))

    # --- Single Click Timeout Detection ---
    if click_time > 0 and (current_time - click_time) >= CLICK_INTERVAL:
        override_mode_active = not override_mode_active
        if DEBUG_PRINT:
            print("Single-click: override_mode_active toggled to {}".format(override_mode_active))
        click_time = 0

    # --- LED Control Logic ---
    # Determine if LEDs *should* be on based on the current mode states
    should_leds_be_on_now = False
    if override_mode_active:
        should_leds_be_on_now = True
    elif photocell_control_enabled and photocell_value < PHOTOCELL_THRESHOLD:
        should_leds_be_on_now = True

    # Update physical LEDs only if the desired state differs from the current physical state
    if should_leds_be_on_now:
        if not leds_currently_on: # If they should be on, but are currently physically off
            set_simple_pattern_on()
    else: # They should be off
        if leds_currently_on: # If they should be off, but are currently physically on
            set_pixels_off()

    last_switch_state = current_switch_state
    time.sleep(MAIN_LOOP_DELAY)
