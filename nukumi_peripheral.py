"""NUKUMI PERIPHERAL"""

import board
import time

from simpleio import map_range

from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import neopixel

#

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

#

touch = DigitalInOut(board.A1)

color_red = 0
color_blue = 255

light = neopixel.NeoPixel(board.NEOPIXEL, 10)
light.fill((color_red, 30, color_blue))
light.brightness = 0

#

here_light_touch = touch.value
here_light_brightness = light.brightness

#

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

#

while True:
    ble.start_advertising(advertisement)
    print("WAITING TO CONNECT...")
    while not ble.connected:
        pass
    print("CONNECTED!")

    while ble.connected:
        here_light_touch = touch.value

        now = time.monotonic()

        string_read = ''
        while uart.in_waiting:
            byte_read = uart.read(1).decode('utf-8')
            if byte_read != '\n':
                string_read += byte_read
            else:
                break
        else:
            byte_read = None

        string_read_list = string_read.split(",")

        print(string_read_list)
        print(here_light_brightness)

        #

        light.fill((color_red, 30, color_blue))

        if len(string_read_list) == 2 and string_read_list is not None and string_read_list[0] != "" and len(string_read_list[0]) == 1:
            if here_light_touch and int(string_read_list[0]) == 1:
                if here_light_brightness < .4:
                    here_light_brightness += .004

                if color_blue > 0:
                    color_blue -= 1

                if color_red < 255:
                    color_red += 1

            elif int(string_read_list[0]) == 1:
                if here_light_brightness < .4:
                    here_light_brightness += .004

                if color_blue < 255:
                    color_blue += 1

                if color_red > 0:
                    color_red -= 1

            elif here_light_touch:
                if here_light_brightness < .4:
                    here_light_brightness += .008

                if color_blue < 255:
                    color_blue += 1

                if color_red > 0:
                    color_red -= 1

            else:
                if here_light_brightness > 0:
                    here_light_brightness -= .004

                if color_blue < 255:
                    color_blue += 1

                if color_red > 0:
                    color_red -= 1

        #

        light.brightness = here_light_brightness

        #

        print(color_red)
        print(color_blue)

        time_now = time.monotonic()

        string_write = str(int(here_light_touch)) + ',' + str(here_light_brightness) + '\n'
        # uart.write(bytes(string_write, 'utf-8'))
        uart.write(string_write.encode("utf-8"))

        #

        time.sleep(.04)
