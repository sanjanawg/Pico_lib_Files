from machine import I2C, Pin
import time

# Setup I2C on the Raspberry Pi Pico (I2C1 on GP6 (SDA) and GP7 (SCL))
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)  # Reduced frequency for stability

# Scan for all connected I2C devices
devices = i2c.scan()

# Print I2C device addresses in hexadecimal
if devices:
    print("I2C devices found:", [hex(device) for device in devices])
else:
    print("No I2C devices found.")
