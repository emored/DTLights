import board # type: ignore
import neopixel # type: ignore
import time # type: ignore
import analogio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore

switch = DigitalInOut(board.D3)
switch.direction = Direction.INPUT
switch.pull = Pull.UP
lastState = True
override = False
clickTime = 0
clickInterval = 0.5

photocell_pin = board.A2  #pin 0 is Analog input 2 
photocell = analogio.AnalogIn(photocell_pin)
photocellEnabled = True

pixel_pin = board.D2
num_pixels = 8        #number of leds pixels on the ring
 
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)
pixelState = False

RED = (255, 0, 0) # RGB
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
OFF = (0, 0, 0)
CUSTYL = (255, 150, 20)
CUSTRD = (255, 30, 30)
WHITE = (255, 255, 100)
 
def defMode():
    for j in range(250):
        R1 = int(CUSTRD[0]) * j / 250
        R2 = int(CUSTRD[1]) * j / 250
        R3 = int(CUSTRD[2]) * j / 250
        Y1 = int(CUSTYL[0]) * j / 250
        Y2 = int(CUSTYL[1]) * j / 250
        Y3 = int(CUSTYL[2]) * j / 250
        W1 = int(WHITE[0]) * j / 250
        W2 = int(WHITE[1]) * j / 250
        W3 = int(WHITE[2]) * j / 250
        pixels[0] = (int(R1), int(R2), int(R3))
        pixels[4] = (int(Y1), int(Y2), int(Y3))
        pixels[1] = (int(W1), int(W2), int(W3))
        pixels[2] = (int(W1), int(W2), int(W3))
        pixels[3] = (int(W1), int(W2), int(W3))
        pixels[5] = (int(W1), int(W2), int(W3))
        pixels[6] = (int(W1), int(W2), int(W3))
        pixels[7] = (int(W1), int(W2), int(W3))
        pixels.show()

def off():
    pixels.fill(OFF)
    pixels.show()

def photoAlert():
    if photocellEnabled:
        for i in range(2):
            pixels.fill(WHITE)
            pixels.show()
            time.sleep(0.25)
            pixels.fill(OFF)
            pixels.show()
            time.sleep(0.1)
    elif not photocellEnabled:
        for i in range(2):
            pixels.fill(CYAN)
            pixels.show()
            time.sleep(0.25)
            pixels.fill(OFF)
            pixels.show()
            time.sleep(0.1)

while True:
    currentState = switch.value

    # Print states
    print("Last: " + str(lastState) + " Current: "+ str(currentState) + " Button: " + str(override))
    print(">value:" + str(photocell.value) + "\r\n")

    if lastState and not currentState:  # Button press detected
        timeNow = time.monotonic()
        if timeNow - clickTime < clickInterval:  # Double-click detected
            photocellEnabled = not photocellEnabled
            print("Photocell toggled: " + str(photocellEnabled))
            photoAlert()
            clickTime = 0  # Reset clickTime to avoid triggering override
        else:
            clickTime = timeNow

    if clickTime and (time.monotonic() - clickTime >= clickInterval):  
        # Single click timeout, toggle override
        override = not override
        clickTime = 0  # Reset clickTime after processing single click

    # Only update lights if not in the middle of a double-click
    if not clickTime:
        if override:
            defMode()
        elif photocell.value < 35000 and photocellEnabled:
            defMode()
        else:
            off()

    lastState = currentState
    time.sleep(0.12)
