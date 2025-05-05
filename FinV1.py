import board # type: ignore
import neopixel # type: ignore
import time # type: ignore
 
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
 
while True:
    for i in range(num_pixels):
        if i == 0:
            pixels[i] = CUSTRD
            pixels.show()
        elif i == 4:
            pixels[i] = CUSTYL
            pixels.show()
        else:
            pixels[i] = WHITE
            pixels.show()
