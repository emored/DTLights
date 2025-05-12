import board # type: ignore
import neopixel # type: ignore
import time # type: ignore
import analogio # type: ignore
from digitalio import DigitalInOut, Direction, Pull # type: ignore

switch = DigitalInOut(board.D3)
switch.direction = Direction.INPUT
switch.pull = Pull.UP
switchPower = False
 
photocell_pin = board.A2  #pin 0 is Analog input 2 
photocell = analogio.AnalogIn(photocell_pin)
phPower = False

pixel_pin = board.D2
num_pixels = 8        #number of leds pixels on the ring
 
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)
 
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

while True:
    # Print states
    print(str(switch.value) + str(switchPower) + str(phPower))
    print(">value:" + str(photocell.value) + "\r\n")

    if (photocell.value <= 10000):
        phPower = True
    else:
        phPower = False

    #Manual On Off
    if switch.value == False and switchPower == False:
        switchPower = True
    elif switch.value == False and switchPower == True:
        switchPower = False

    if switchPower == False or phPower == False:
        pixels.fill(OFF)
        pixels.show()
    elif switchPower == True or phPower == True:
        defMode()
    time.sleep(0.5)
