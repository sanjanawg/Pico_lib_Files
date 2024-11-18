from machine import I2C, Pin
import time

# MAX30102 I2C address and registers
MAX30102_ADDRESS = 0x57
FIFO_DATA_REGISTER = 0x07  # Adjusted to correct FIFO register
MODE_CONFIG = 0x09
SPO2_CONFIG = 0x0A
LED1_PA = 0x0C  # Red LED pulse amplitude
LED2_PA = 0x0D  # IR LED pulse amplitude

# Heart rate variables
RATE_SIZE = 4
rates = [0] * RATE_SIZE
rateSpot = 0
lastBeat = 0
beatsPerMinute = 0
beatAvg = 0

# Setup I2C on the Raspberry Pi Pico (using GP6 for SDA and GP7 for SCL)
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=400000)

# Initialize MAX30102
def initialize_max30102():
    try:
        # Put the device in heart rate mode and set configurations
        i2c.writeto_mem(MAX30102_ADDRESS, MODE_CONFIG, b'\x03')  # Heart rate mode
        i2c.writeto_mem(MAX30102_ADDRESS, SPO2_CONFIG, b'\x27')  # SPO2 config
        i2c.writeto_mem(MAX30102_ADDRESS, LED1_PA, b'\x24')  # Set LED1 (Red)
        i2c.writeto_mem(MAX30102_ADDRESS, LED2_PA, b'\x24')  # Set LED2 (IR)
        print("MAX30102 Initialized")
    except Exception as e:
        print(f"Initialization error: {e}")

# Read FIFO data from MAX30102
def read_max30102_fifo():
    try:
        data = i2c.readfrom_mem(MAX30102_ADDRESS, FIFO_DATA_REGISTER, 6)
        ir_value = (data[0] << 16) | (data[1] << 8) | data[2]
        red_value = (data[3] << 16) | (data[4] << 8) | data[5]
        return red_value, ir_value
    except Exception as e:
        print(f"Read error: {e}")
        return None, None

# Check for beat based on IR threshold
def checkForBeat(ir_value):
    threshold = 50000
    if ir_value > threshold:
        return True
    return False

# Calculate BPM and average BPM
def calculate_heart_rate(ir_value):
    global lastBeat, beatsPerMinute, rateSpot, beatAvg, rates
    currentTime = time.ticks_ms()
    
    if checkForBeat(ir_value):
        delta = time.ticks_diff(currentTime, lastBeat)
        lastBeat = currentTime

        if delta > 0:
            beatsPerMinute = 60 / (delta / 1000.0)
            if 20 < beatsPerMinute < 255:  # Filter invalid BPM
                rates[rateSpot] = int(beatsPerMinute)
                rateSpot = (rateSpot + 1) % RATE_SIZE
                beatAvg = sum(rates) / RATE_SIZE  # Average BPM readings
    
    return beatsPerMinute, beatAvg

# Main loop
initialize_max30102()

while True:
    red, ir = read_max30102_fifo()
    if ir is not None and red is not None:
        bpm, avg_bpm = calculate_heart_rate(ir)

        print(f"IR={ir}, Red={red}, BPM={bpm:.2f}, Avg BPM={avg_bpm:.2f}")

        if ir < 50000:
            print("No finger detected")
    else:
        print("Failed to read data from MAX30102")
    
    time.sleep(1)

