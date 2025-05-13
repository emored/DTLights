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
 
photocell_pin = board.A2  #pin 0 is Analog input 2 
photocell = analogio.AnalogIn(photocell_pin)

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
    for i in range(num_pixels):
        if i == 0:
            pixels[i] = CUSTRD
        elif i == 4:
            pixels[i] = CUSTYL
        else:
            pixels[i] = WHITE
    pixels.show()

def off():
    pixels.fill(OFF)
    pixels.show()

while True:
    currentState = switch.value

    # Print states
    print("Last: " + str(lastState) + " Current: "+ str(currentState) + " Button: " + str(override))
    print(">value:" + str(photocell.value) + "\r\n")

    if lastState and not currentState:
        override = not override
    
    if override:
        defMode()
    elif photocell.value < 10000:
        defMode()
    else:
        off()

    lastState = currentState
    time.sleep(0.12)
