# Standard library imports
import time # For time-based operations like delays and debouncing
import gc   # Import garbage collector

# CircuitPython specific imports
import board # Provides access to board pins
import neopixel # For controlling NeoPixel LEDs
import analogio # For reading analog values (like from a photocell)
from digitalio import DigitalInOut, Direction, Pull # For digital I/O (switches)

# --- Configuration Constants ---
debugMode = False

# Momentary Switch Configuration
mSwitchPin = board.D3
doubleClickWindow = 0.25

# Latching Switch Configuration
lSwitchPin = board.D1

# Photocell Configuration
photocellPin = board.A2
photocellOnThreshold = 9500
photocellOffThreshold = 10500

# NeoPixel Configuration
neopixelPin = board.D2
numPixels = 8
alertBlinks = 3
alertBlinkDuration = 0.1
rainbowCycleSpeed = 1

breathingMin = 0.1
breathingMax = 1.0
breathingStep = 0.02

fadeSteps = 8
fadeDelay = 0.0135

# --- Hardware Setup ---
mSwitch = DigitalInOut(mSwitchPin)
mSwitch.direction = Direction.INPUT
mSwitch.pull = Pull.UP
mSwitchLastState = True
mSwitchClickTime = 0

lSwitch = DigitalInOut(lSwitchPin)
lSwitch.direction = Direction.INPUT
lSwitch.pull = Pull.UP

photocell = analogio.AnalogIn(photocellPin)
photocellEnabled = True

pixels = neopixel.NeoPixel(neopixelPin, numPixels, brightness=1.0, auto_write=False)

# --- Global State Variables ---
pixelState = False
currentModeIndex = 0
rainbowOffset = 0
breathingIntensity = breathingMin
breathingDirection = 1

# --- Color Definitions & Pre-allocated Lists ---
OFF_COLOR = (0, 0, 0)
OFF_COLOR_LIST = [OFF_COLOR] * numPixels

_CUSTYL = (255, 150, 20); _CUSTRD = (255, 30, 30); _WHITE_DEFAULT = (255, 255, 100)
_RED_STATIC = (255, 0, 0); _ORANGE_STATIC = (255, 120, 0); _YELLOW_STATIC = (255, 200, 0)
_GREEN_STATIC = (0, 255, 0); _BLUE_STATIC = (0, 0, 255); _VIOLET_STATIC = (148, 0, 211)
_LIGHT_BLUE_STATIC = (100, 180, 255)
_GREEN_ALERT = (0, 255, 0); _RED_ALERT = (255, 0, 0)

# --- Helper Functions ---
def wheel(pos):
    if not (0 <= pos <= 255): return (0,0,0)
    if pos < 85: return (int(pos * 3), int(255 - pos * 3), 0)
    elif pos < 170: pos -= 85; return (int(255 - pos * 3), 0, int(pos * 3))
    else: pos -= 170; return (0, int(pos * 3), int(255 - pos * 3))

def interpColor(color1, color2, factor):
    r = int(color1[0] * (1 - factor) + color2[0] * factor)
    g = int(color1[1] * (1 - factor) + color2[1] * factor)
    b = int(color1[2] * (1 - factor) + color2[2] * factor)
    return (r, g, b)

def exeFade(sourcePixel, targetPixel):
    for step in range(fadeSteps + 1):
        factor = step / fadeSteps
        for i in range(numPixels):
            pixels[i] = interpColor(sourcePixel[i], targetPixel[i], factor)
        pixels.show()
        time.sleep(fadeDelay)

# --- Mode Functions ---
def modeDefault():
    for i in range(numPixels):
        if i == 0: pixels[i] = _CUSTYL
        elif i == 4: pixels[i] = _CUSTRD
        else: pixels[i] = _WHITE_DEFAULT
    pixels.show()

def modeRainbow():
    global rainbowOffset
    for i in range(numPixels):
        pixelIndex = (i * 256 // numPixels) + rainbowOffset
        pixels[i] = wheel(pixelIndex & 255)
    pixels.show()
    rainbowOffset = (rainbowOffset + rainbowCycleSpeed) & 255

def modeAnyStatic(targetColor): pixels.fill(targetColor); pixels.show()

def modeBreathingWhite():
    global breathingIntensity, breathingDirection
    breathingIntensity += breathingStep * breathingDirection
    if breathingIntensity >= breathingMax:
        breathingIntensity = breathingMax; breathingDirection = -1
    elif breathingIntensity <= breathingMin:
        breathingIntensity = breathingMin; breathingDirection = 1
    r = int(_WHITE_DEFAULT[0] * breathingIntensity)
    g = int(_WHITE_DEFAULT[1] * breathingIntensity)
    b = int(_WHITE_DEFAULT[2] * breathingIntensity)
    pixels.fill((r,g,b)); pixels.show()

modes = [
    modeDefault,
    lambda: modeAnyStatic(_RED_STATIC), lambda: modeAnyStatic(_ORANGE_STATIC),
    lambda: modeAnyStatic(_YELLOW_STATIC), lambda: modeAnyStatic(_GREEN_STATIC),
    lambda: modeAnyStatic(_BLUE_STATIC), lambda: modeAnyStatic(_VIOLET_STATIC),
    lambda: modeAnyStatic(_LIGHT_BLUE_STATIC), modeBreathingWhite, modeRainbow
]

modeNames = None # Set to None if debugMode is False
if debugMode:
    modeNames = ["Default", "S.Red", "S.Orange", "S.Yellow", "S.Green", "S.Blue",
                 "S.Violet", "L.Blue", "BreathW", "Rainbow"]

def captureTarget(targetMode):
    """Renders a mode to the internal pixels buffer and returns a copy
       WITHOUT causing a visible flash on the physical LEDs."""
    original_brightness = pixels.brightness
    pixels.brightness = 0.0 # Make pixels temporarily invisible to prevent flash

    modes[targetMode]() # Mode function is called, its show() has no visible effect

    capturedData = list(pixels) # Capture the pixel data

    pixels.brightness = original_brightness # Restore original brightness
    return capturedData

def off():
    global pixelState
    pixels.fill(OFF_COLOR); pixels.show()
    pixelState = False

def photocellAlert(prevState):
    global currentModeIndex
    prevBrightness = pixels.brightness
    if prevBrightness < 1.0: pixels.brightness = 1.0
    
    blinkColor = _GREEN_ALERT if photocellEnabled else _RED_ALERT
    for _ in range(alertBlinks):
        pixels.fill(blinkColor); pixels.show(); time.sleep(alertBlinkDuration)
        pixels.fill(OFF_COLOR); pixels.show(); time.sleep(alertBlinkDuration)
    
    if prevBrightness < 1.0: pixels.brightness = prevBrightness

    if prevState: modes[currentModeIndex]()
    else: pixels.fill(OFF_COLOR); pixels.show()

# --- Main Loop ---
off()
gc.collect()

while True:
    currentTime = time.monotonic()

    mSwitchCurrentState = mSwitch.value
    lSwitchOn = not lSwitch.value
    photocellLevel = photocell.value

    # --- Momentary Switch Logic ---
    if mSwitchLastState and not mSwitchCurrentState: # Press
        if mSwitchClickTime != 0 and (currentTime - mSwitchClickTime < doubleClickWindow): # Double click
            photocellEnabled = not photocellEnabled
            photocellAlert(pixelState)
            mSwitchClickTime = 0 
        else: # First click
            mSwitchClickTime = currentTime

    if mSwitchClickTime != 0 and (currentTime - mSwitchClickTime >= doubleClickWindow): # Single click timeout
        if pixelState: # If lights are ON, perform fade-out then fade-in for mode change
            gc.collect() 
            modes[currentModeIndex]() # Ensure current frame for source
            prevMode = list(pixels)
            exeFade(prevMode, OFF_COLOR_LIST) # Fade out
            
            currentModeIndex = (currentModeIndex + 1) % len(modes)
            
            gc.collect()
            # Silently capture new mode's target state
            targetMode = captureTarget(currentModeIndex)
            # Strip is already visually off from the previous fade_out.
            exeFade(OFF_COLOR_LIST, targetMode) # Fade in
        else: # If lights are OFF, just update the mode index
            currentModeIndex = (currentModeIndex + 1) % len(modes)
        mSwitchClickTime = 0
    
    mSwitchLastState = mSwitchCurrentState

    # --- Light Control Logic ---
    expectedPixelState = False
    if lSwitchOn:
        expectedPixelState = True
    else: 
        if photocellEnabled:
            if pixelState: expectedPixelState = not (photocellLevel > photocellOffThreshold)
            else: expectedPixelState = photocellLevel < photocellOnThreshold
    
    # --- Apply Light State (with Fades) ---
    if expectedPixelState and not pixelState: # Request to Turn ON
        gc.collect()
        # Silently capture the target mode's first frame appearance
        targetPixel_on = captureTarget(currentModeIndex)
        
        # Ensure strip is visually off before starting fade-in
        pixels.fill(OFF_COLOR)
        pixels.show() 
        
        exeFade(OFF_COLOR_LIST, targetPixel_on)
        pixelState = True

    elif not expectedPixelState and pixelState: # Request to Turn OFF
        gc.collect()
        modes[currentModeIndex]() # Ensure current frame for source
        sourcePixel_off = list(pixels)
        
        exeFade(sourcePixel_off, OFF_COLOR_LIST)
        off()

    elif pixelState: # Lights are ON and expected to stay ON
        modes[currentModeIndex]()
    
    time.sleep(0.01)
