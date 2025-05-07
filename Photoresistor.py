import time
import analogio
import neopixel
import board

photocell_pin = board.A2  #pin 0 is Analog input 2 
photocell = analogio.AnalogIn(photocell_pin)
pixel_pin = board.D2
num_pixels = 16
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)

WHITE = (255, 255, 255)
OFF = (0, 0, 0)

while True:  
    time.sleep(0.1)
    print(">value:" + str(photocell.value) + "\r\n")
    if (photocell.value <= 10000):
        pixels.fill(WHITE)
        pixels.show()
    else:
        pixels.fill(OFF)
        pixels.show()
