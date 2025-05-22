"""
Photocell and NeoPixel Test Program
This program is for testing the photocell and basic NeoPixel control
based on light levels.
"""

import time
import board
import neopixel
import analogio

# ────────────────────── CONFIG ────────────────────────────────
DEBUG = True  # Set True to see diagnostics

if DEBUG:
    def dbg(*args):
        print(*args)  # Simple print for debug messages
else:
    def dbg(*_):
        pass  # No-op if DEBUG is False

# Pin Definitions (from original code)
PHOTOCELL_PIN = board.A2
NEOPIXEL_PIN = board.D2

# NeoPixel Configuration
NUM_PIXELS = 8  # Number of NeoPixels

# Photocell Thresholds (from original code)
PHOTO_ON_THRESHOLD = 9500   # Value to turn lights ON
PHOTO_OFF_THRESHOLD = 10500 # Value to turn lights OFF (hysteresis)

# Colors
ON_COLOR = (255, 150, 80) # A slightly dimmer white for testing
OFF_COLOR = (0, 0, 0)

# ─────────────────── HARDWARE SET-UP ──────────────────────────
dbg("Setting up hardware...")

# Initialize Photocell
photocell = analogio.AnalogIn(PHOTOCELL_PIN)
dbg("Photocell initialized on pin", PHOTOCELL_PIN)

# Initialize NeoPixels
pixels = neopixel.NeoPixel(
    NEOPIXEL_PIN, NUM_PIXELS, brightness=1.0, auto_write=False
)
dbg("NeoPixels initialized on pin", NEOPIXEL_PIN, "with", NUM_PIXELS, "pixels.")

# ───────────────────────── STATE ──────────────────────────────
pixels_on = False  # Tracks the current state of the NeoPixels

# ──────────────────── STARTUP ─────────────────────────────────
pixels.fill(OFF_COLOR)
pixels.show()
dbg("Startup complete. NeoPixels turned OFF initially.")
dbg("Photocell thresholds: ON <", PHOTO_ON_THRESHOLD, ", OFF >", PHOTO_OFF_THRESHOLD)

# ──────────────────── MAIN LOOP ───────────────────────────────
dbg("Starting main loop...")
while True:
    current_photo_value = photocell.value
    dbg(">value:", current_photo_value, "\r\n")

    # Determine desired LED state based on photocell value and hysteresis
    if pixels_on:
        # Pixels are currently ON, check if they should turn OFF
        if current_photo_value > PHOTO_OFF_THRESHOLD:
            dbg("Condition to turn OFF met:", current_photo_value, ">", PHOTO_OFF_THRESHOLD)
            pixels_on = False
            pixels.fill(OFF_COLOR)
            pixels.show()
            dbg("NeoPixels turned OFF.")
    else:
        # Pixels are currently OFF, check if they should turn ON
        if current_photo_value < PHOTO_ON_THRESHOLD:
            dbg("Condition to turn ON met:", current_photo_value, "<", PHOTO_ON_THRESHOLD)
            pixels_on = True
            pixels.fill(ON_COLOR)
            pixels.show()
            dbg("NeoPixels turned ON.")

    # Small delay to allow USB serial to keep up and prevent overly fast loops
    # Adjust if necessary for "as often as possible" while maintaining stability
    time.sleep(0.05)
