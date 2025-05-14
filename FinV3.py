--- START OF FILE code.py ---
import board # type: ignore
import neopixel # type: ignore
import time # type: ignore
import analogio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore

# --- Configuration Constants ---
SWITCH_PIN = board.D3
PHOTOCELL_PIN = board.A2
PIXEL_PIN = board.D2

NUM_PIXELS = 8
PIXEL_BRIGHTNESS = 0.3

CLICK_INTERVAL = 0.5  # Seconds to distinguish single/double click
MAIN_LOOP_DELAY = 0.12 # Seconds, affects responsiveness and loop frequency

PHOTOCELL_THRESHOLD = 35000  # ADC value, lower means darker
FADE_STEPS = 250 # Number of steps in the fade-in effect for defMode.

# PhotoAlert blink timings
ALERT_ON_TIME = 0.25
ALERT_OFF_TIME = 0.1
ALERT_REPETITIONS = 2

DEBUG_PRINT = False # Set to True for debug console output

# --- Color Definitions ---
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)
# Custom colors used in defMode
CUSTYL = (255, 150, 20)  # Custom Yellow
CUSTRD = (255, 30, 30)   # Custom Red
WHITE = (255, 255, 100)  # Soft White

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
last_switch_state = True  # Assuming switch is initially not pressed (True due to Pull.UP)
override_mode_active = False # When True, defMode is on regardless of photocell
photocell_control_enabled = True # Whether photocell input affects lights
# click_time stores the timestamp of the first click to detect double-clicks.
# A value of 0 means no click is currently being processed.
click_time = 0

# --- Helper Functions ---
def scale_color(color_tuple, factor):
    """Scales an RGB color tuple by a factor (0.0 to 1.0)."""
    # Ensure factor is within bounds, though current usage should guarantee this.
    factor = max(0.0, min(1.0, factor))
    return tuple(int(c * factor) for c in color_tuple)

# --- LED Effect Functions ---
def defMode():
    """Displays the default light pattern with a fade-in effect."""
    if FADE_STEPS <= 0:
        # Fallback for invalid FADE_STEPS: set to full color instantly
        r_color = CUSTRD
        y_color = CUSTYL
        w_color = WHITE
        pixels[0] = r_color
        pixels[4] = y_color
        for i in range(NUM_PIXELS):
            if i not in [0, 4]:
                pixels[i] = w_color
        pixels.show()
        return

    for j in range(FADE_STEPS): # j from 0 to FADE_STEPS-1
        # Factor smoothly goes from (1/FADE_STEPS) to 1.0
        # This makes the light start dim and reach full brightness at the last step.
        factor = (j + 1) / float(FADE_STEPS)

        r_color = scale_color(CUSTRD, factor)
        y_color = scale_color(CUSTYL, factor)
        w_color = scale_color(WHITE, factor)

        pixels[0] = r_color
        pixels[4] = y_color
        # Assign white to remaining pixels
        for i in range(NUM_PIXELS):
            if i not in [0, 4]:
                pixels[i] = w_color
        pixels.show()
        # Optional small delay per step for very slow fades or few steps.
        # time.sleep(0.001) # For FADE_STEPS=250, pixels.show() latency is usually sufficient.

def off():
    """Turns all pixels off."""
    pixels.fill(OFF)
    pixels.show()

def photoAlert():
    """Flashes pixels to indicate a mode change (e.g., photocell enabled/disabled)."""
    alert_color = WHITE if photocell_control_enabled else CYAN
    for _ in range(ALERT_REPETITIONS):
        pixels.fill(alert_color)
        pixels.show()
        time.sleep(ALERT_ON_TIME)
        pixels.fill(OFF)
        pixels.show()
        time.sleep(ALERT_OFF_TIME)

# --- Main Loop ---
while True:
    current_switch_state = switch.value

    if DEBUG_PRINT:
        # Using f-strings for cleaner print statements
        print(f"Switch: {current_switch_state}, Last: {last_switch_state}, Override: {override_mode_active}, PC_Enabled: {photocell_control_enabled}")
        print(f"Photocell: {photocell.value}, ClickTime: {click_time:.2f}\n") # Format click_time

    # --- Button Press Detection (Falling Edge: True to False) ---
    if last_switch_state and not current_switch_state:
        time_now = time.monotonic()
        # Check if this press is close enough to the previous one to be a double-click
        if click_time > 0 and (time_now - click_time) < CLICK_INTERVAL:
            # Double-click detected
            photocell_control_enabled = not photocell_control_enabled
            if DEBUG_PRINT:
                print(f"Double-click: Photocell Enabled toggled to {photocell_control_enabled}")
            photoAlert() # Visual feedback for the double-click action
            click_time = 0  # Reset click_time: double-click processed, no single click action
        else:
            # First click of a potential double-click, or a single click. Record its time.
            click_time = time_now

    # --- Single Click Timeout Detection ---
    # If click_time is set (a first click happened) and CLICK_INTERVAL has passed without a second click
    if click_time > 0 and (time.monotonic() - click_time) >= CLICK_INTERVAL:
        override_mode_active = not override_mode_active
        if DEBUG_PRINT:
            print(f"Single-click: Override toggled to {override_mode_active}")
        # No photoAlert() here, as single click just changes mode silently unless desired
        click_time = 0  # Reset click_time: single-click processed

    # --- Update LEDS ---
    # Only update lights if no click is currently being timed (i.e., click_time is 0).
    # This prevents light changes during the double-click detection window.
    if click_time == 0:
        if override_mode_active:
            defMode()
        elif photocell_control_enabled and photocell.value < PHOTOCELL_THRESHOLD:
            # Photocell control is on, and it's dark enough
            defMode()
        else:
            # Override is off, AND (photocell is disabled OR it's bright enough)
            off()

    last_switch_state = current_switch_state
    time.sleep(MAIN_LOOP_DELAY)
--- END OF FILE code.py ---
