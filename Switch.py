import board # type: ignore
import neopixel # type: ignore
import time # type: ignore
 
pixel_pin = board.D2
num_pixels = 8        #number of leds pixels on the ring
 
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.7, auto_write=False)
 
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

myCOLORS = [RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, CUSTYL, CUSTRD, WHITE]
 
while True:
    for i in range(0,7,2):
        pixels[i] = WHITE
    for i in range(1,8,2):
        pixels[i] = YELLOW
    pixels.show()
    time.sleep(0.5)
    for i in range(0,7,2):
        pixels[i] = YELLOW
    for i in range(1,8,2):
        pixels[i] = WHITE
    pixels.show()
    time.sleep(0.5)
