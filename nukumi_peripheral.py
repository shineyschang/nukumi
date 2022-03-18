"""NUKUMI PERIPHERAL"""

import board
import time

from simpleio import map_range

from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull

import neopixel

# BLUETOOTH IMPORTS

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

# CAPACITIVE TOUCH

import touchio

# LIGHTING FLOURISH

import random

# VARIED + BOUNCING GREEN VALUES GIVE LIGHT MOVING QUALITY

# touch = DigitalInOut(board.A1)
touch = touchio.TouchIn(board.A1)

color_red = 0
color_blue = 255

color_green = [None] * 10
color_green_bounce = [None] * 10

for i in range(10):
    color_green[i] = random.randint(10, 60)
    color_green_bounce[i] = random.uniform(0, 4)

light = neopixel.NeoPixel(board.NEOPIXEL, 10)
light.fill((color_red, 60, color_blue))
light.brightness = 0

#

here_light_touch = touch.value
here_light_brightness = light.brightness

# BLUETOOTH PERIPHERAL SETUP

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

#

while True:

    # CONNECTING (PERIPHERAL)

    ble.start_advertising(advertisement)
    print("WAITING TO CONNECT...")
    while not ble.connected:
        pass
    print("CONNECTED!")

    while ble.connected:
        here_light_touch = touch.value

        now = time.monotonic()

        # READING INCOMING STRING

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

        # ASSIGNING RGB VALUES TO NEOPIXELS

        for i in range(10):
            light[i] = (color_red, color_green[i], color_blue)

        # IF BOTH ARE TOUCHED, IF ONLY ONE IS TOUCHED (X2), IF NEITHER IS BEING TOUCHED

        if len(string_read_list) == 2 and string_read_list is not None and string_read_list[0] != "" and len(string_read_list[0]) == 1:
            if here_light_touch and int(string_read_list[0]) == 1:
                if here_light_brightness < .4:
                    here_light_brightness += .004

                if color_blue > 10:
                    color_blue -= 2

                if color_red < 250:
                    color_red += 2

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

        # BOUNCING GREEN VALUES

        for i in range(10):

            color_green[i] += color_green_bounce[i]

            if color_green[i] < 10 or color_green[i] > 60:
                color_green_bounce[i] = -color_green_bounce[i]

        #

        light.brightness = here_light_brightness

        #

        print(color_red)
        print(color_blue)
        # print(color_green)

        time_now = time.monotonic()

        # WRITING STRING

        string_write = str(int(here_light_touch)) + ',' + str(here_light_brightness) + '\n'
        # uart.write(bytes(string_write, 'utf-8'))
        uart.write(string_write.encode("utf-8"))

        #

        time.sleep(.04)
