from VEML6030 import VEML6030
from time import sleep
from machine import I2C, Pin

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)

sensor = VEML6030(i2c)

while True:
    print(str(sensor.read()) + " lux")
    sleep(0.1)