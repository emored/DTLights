import board
import neopixel
import time
 
pixel_pin = board.D2   #the ring data is connected to this pin
num_pixels = 4        #number of leds pixels on the ring
 
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

CUSTYL = (255, 150, 25)
OFF = (0, 0, 0)
 
while True:
    pixels.fill(CUSTYL)
    pixels.show()
    time.sleep(0.5)
