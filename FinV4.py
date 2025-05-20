"""
Streetcar NeoPixel Controller
Emory Temple-Asheim, May 2025
*** Sections of this program were generated using Gemini and other AI tools ***
"""

import time
import gc

import board
import neopixel
import analogio
from digitalio import DigitalInOut, Direction, Pull

# ────────────────────── CONFIG ────────────────────────────────
DEBUG = True                      # ← set True to see diagnostics

if DEBUG:
    def dbg(*args):
        print(*args)               # no string building
else:
    def dbg(*_):
        pass                       # stub → zero run-time cost

M_SWITCH_PIN = board.D4            # momentary switch (pull-up)
L_SWITCH_PIN = board.D1            # latching  switch (pull-up)
PHOTOCELL_PIN = board.A2
NEOPIXEL_PIN = board.D2

NUM_PIXELS = 8
DOUBLE_CLICK_WINDOW = 0.25         # s

PHOTO_ON_THRESHOLD = 9500
PHOTO_OFF_THRESHOLD = 10500

ALERT_BLINKS = 3
ALERT_BLINK_TIME = 0.10            # s

RAINBOW_SPEED = 1                  # wheel step / loop

BREATH_MIN = 0.10
BREATH_MAX = 1.00
BREATH_STEP = 0.02

FADE_STEPS = 8
FADE_DELAY = 0.0135                # s

# ────────────────────── COLORS ───────────────────────────────
OFF        = (0, 0, 0)
CUST_YL    = (255, 150, 20)
CUST_RD    = (255,  30, 30)
WHITE      = (255, 255, 100)

S_RED      = (255,   0,   0)
S_ORANGE   = (255, 120,   0)
S_YELLOW   = (255, 200,   0)
S_GREEN    = (  0, 255,   0)
S_BLUE     = (  0,   0, 255)
S_VIOLET   = (148,   0, 211)
S_LBLUE    = (100, 180, 255)

GREEN_OK   = (0, 255, 0)
RED_ALERT  = (255, 0, 0)

OFF_LIST = [OFF] * NUM_PIXELS      # reusable “blank” buffer

# ─────────────────── HARDWARE SET-UP ──────────────────────────
m_switch = DigitalInOut(M_SWITCH_PIN)
m_switch.direction = Direction.INPUT
m_switch.pull = Pull.UP
m_prev = True
m_click_time = 0.0

l_switch = DigitalInOut(L_SWITCH_PIN)
l_switch.direction = Direction.INPUT
l_switch.pull = Pull.UP

photocell = analogio.AnalogIn(PHOTOCELL_PIN)
photocell_enabled = True

pixels = neopixel.NeoPixel(
    NEOPIXEL_PIN, NUM_PIXELS, brightness=1.0, auto_write=False
)

# ───────────────────────── STATE ──────────────────────────────
pixels_on = False
mode_idx = 0

rainbow_offset = 0
breath_intensity = BREATH_MIN
breath_dir = 1

# ─────────────────────── HELPERS ──────────────────────────────
def wheel(pos):
    if not 0 <= pos <= 255:
        return OFF
    if pos < 85:
        return pos * 3, 255 - pos * 3, 0
    if pos < 170:
        pos -= 85
        return 255 - pos * 3, 0, pos * 3
    pos -= 170
    return 0, pos * 3, 255 - pos * 3


def lerp(c1, c2, t):
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def fade(src, dst):
    for step in range(FADE_STEPS + 1):
        t = step / FADE_STEPS
        for i in range(NUM_PIXELS):
            pixels[i] = lerp(src[i], dst[i], t)
        pixels.show()
        time.sleep(FADE_DELAY)


def snapshot():
    return list(pixels)            # copy current strip buffer


def capture(index):
    original = pixels.brightness
    pixels.brightness = 0.0
    MODES[index][1]()
    buf = list(pixels)
    pixels.brightness = original
    return buf


def blink(color):
    for _ in range(ALERT_BLINKS):
        pixels.fill(color)
        pixels.show()
        time.sleep(ALERT_BLINK_TIME)
        pixels.fill(OFF)
        pixels.show()
        time.sleep(ALERT_BLINK_TIME)

# ───────────────────────── MODES ──────────────────────────────
def mode_default():
    buf = [WHITE] * NUM_PIXELS
    buf[0] = CUST_YL
    buf[4] = CUST_RD
    pixels[:] = buf
    pixels.show()


def mode_rainbow():
    global rainbow_offset
    for i in range(NUM_PIXELS):
        idx = (i * 256 // NUM_PIXELS) + rainbow_offset
        pixels[i] = wheel(idx & 255)
    pixels.show()
    rainbow_offset = (rainbow_offset + RAINBOW_SPEED) & 255


def mode_static(color):
    pixels.fill(color)
    pixels.show()


def mode_breathe():
    global breath_intensity, breath_dir
    breath_intensity += BREATH_STEP * breath_dir
    if breath_intensity >= BREATH_MAX:
        breath_intensity = BREATH_MAX
        breath_dir = -1
    elif breath_intensity <= BREATH_MIN:
        breath_intensity = BREATH_MIN
        breath_dir = 1
    scaled = (
        int(WHITE[0] * breath_intensity),
        int(WHITE[1] * breath_intensity),
        int(WHITE[2] * breath_intensity),
    )
    pixels.fill(scaled)
    pixels.show()


MODES = (
    ("Default",        mode_default),
    ("Static Red",     lambda: mode_static(S_RED)),
    ("Static Orange",  lambda: mode_static(S_ORANGE)),
    ("Static Yellow",  lambda: mode_static(S_YELLOW)),
    ("Static Green",   lambda: mode_static(S_GREEN)),
    ("Static Blue",    lambda: mode_static(S_BLUE)),
    ("Static Violet",  lambda: mode_static(S_VIOLET)),
    ("Static LBlue",   lambda: mode_static(S_LBLUE)),
    ("Breathe White",  mode_breathe),
    ("Rainbow",        mode_rainbow),
)

# ──────────────────── STARTUP ─────────────────────────────────
pixels.fill(OFF)
pixels.show()
gc.collect()
dbg("Startup complete")

# ──────────────────── MAIN LOOP ───────────────────────────────
while True:
    now = time.monotonic()
    m_state = m_switch.value          # pull-up: True → not pressed
    l_active = not l_switch.value
    photo_val = photocell.value

    # ── momentary switch events ───────────────────────────────
    if m_prev and not m_state:        # falling edge
        dbg("M-switch press @", now)
        if m_click_time and (now - m_click_time < DOUBLE_CLICK_WINDOW):
            photocell_enabled = not photocell_enabled
            dbg("Double-click: photocell enabled?", photocell_enabled)
            blink(GREEN_OK if photocell_enabled else RED_ALERT)
            m_click_time = 0.0
        else:
            m_click_time = now

    if m_click_time and (now - m_click_time >= DOUBLE_CLICK_WINDOW):
        dbg("Single-click: advance mode")
        if pixels_on:
            fade(snapshot(), OFF_LIST)
            mode_idx = (mode_idx + 1) % len(MODES)
            fade(OFF_LIST, capture(mode_idx))
        else:
            mode_idx = (mode_idx + 1) % len(MODES)
        dbg("Current mode →", mode_idx, MODES[mode_idx][0])
        m_click_time = 0.0

    m_prev = m_state

    # ── desired LED state calculation ────────────────────────
    want_on = l_active
    if not want_on and photocell_enabled:
        if pixels_on:
            want_on = photo_val <= PHOTO_OFF_THRESHOLD
        else:
            want_on = photo_val < PHOTO_ON_THRESHOLD

    # ── state transition handling ─────────────────────────────
    if want_on and not pixels_on:
        dbg("Turn ON: fade-in")
        fade(OFF_LIST, capture(mode_idx))
        pixels_on = True

    elif not want_on and pixels_on:
        dbg("Turn OFF: fade-out")
        fade(snapshot(), OFF_LIST)
        pixels.fill(OFF)
        pixels.show()
        pixels_on = False

    elif pixels_on:
        MODES[mode_idx][1]()           # run animation frame

    gc.collect()
    time.sleep(0.01)
