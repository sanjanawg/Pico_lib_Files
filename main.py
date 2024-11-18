from machine import I2C, Pin, UART, ADC
import time
from VEML6030 import VEML6030  # Make sure VEML6030 library is installed

# Setup I2C on the Raspberry Pi Pico (using GP6 for SDA and GP7 for SCL)
i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100000)

# UART for communication (to send data)
uart = UART(0, baudrate=115200)  # Initialize UART0 with a baud rate of 115200

# Initialize VEML6030 Light Sensor
veml6030_sensor = VEML6030(i2c)

# Setup ADC for AD8232 on GP26 (ADC0)
ad8232_adc = ADC(Pin(26))

# Sensor I2C addresses
SHT40_ADDRESS = 0x44  # SHT40 (Temperature and Humidity sensor)
MAX30102_ADDRESS = 0x57  # MAX30102 (Pulse Oximeter sensor)
GY906_ADDRESS = 0x5A     # GY-906 (MLX90614 Infrared temperature sensor)
TEMP_REGISTER = 0x07

# Function to read data from I2C sensor
def read_sensor_data(address, nbytes):
    try:
        return i2c.readfrom(address, nbytes)
    except OSError as e:
        print(f"Error reading from I2C address {hex(address)}: {e}")
        return None

# SHT40 sensor data reading
def read_sht40():
    try:
        i2c.writeto(SHT40_ADDRESS, b'\xFD')
        time.sleep(0.05)
        data = read_sensor_data(SHT40_ADDRESS, 6)
        if data:
            temperature_raw = (data[0] << 8 | data[1])
            humidity_raw = (data[3] << 8 | data[4])
            temperature = -45 + (175 * (temperature_raw / 65535.0))
            humidity = 100 * (humidity_raw / 65535.0)
            return temperature, humidity
        return None, None
    except Exception as e:
        print(f"Error reading SHT40: {e}")
        return None, None

# MAX30102 sensor data reading
def read_max30102():
    try:
        data = read_sensor_data(MAX30102_ADDRESS, 6)
        return list(data) if data else None
    except Exception as e:
        print(f"Error reading MAX30102: {e}")
        return None

# GY-906 sensor data reading
def read_gy906_temp():
    try:
        data = i2c.readfrom_mem(GY906_ADDRESS, TEMP_REGISTER, 2)
        object_temp_raw = int.from_bytes(data, "little")
        return (object_temp_raw * 0.02) - 273.15
    except Exception as e:
        print(f"Error reading GY-906: {e}")
        return None

# AD8232 heart rate data reading
def read_ad8232():
    try:
        ad8232_value = ad8232_adc.read_u16()  # Reads the ADC value (0-65535)
        return ad8232_value * (3.3 / 65535)   # Convert to voltage (assuming 3.3V)
    except Exception as e:
        print(f"Error reading AD8232: {e}")
        return None

# Format data for InfluxDB (line protocol)
def format_influxdb_data(data):
    # Prepare InfluxDB line protocol string
    influx_data = [
        f"environment temperature={data['temperature']},humidity={data['humidity']}",
        f"light light_level={data['light_level']}",
        f"health heart_rate_voltage={data['heart_rate_voltage']},object_temp={data['object_temp']}"
    ]
    return '\n'.join(influx_data)

# Main loop to read all sensors and send data via UART
while True:
    # Read from SHT40
    temperature, humidity = read_sht40()
    
    # Read from VEML6030
    light_level = veml6030_sensor.read()
    
    # Read from MAX30102
    max30102_data = read_max30102()
    
    # Read from GY-906
    object_temp = read_gy906_temp()
    
    # Read from AD8232
    heart_rate_voltage = read_ad8232()

    # Prepare data for display and UART
    data_to_send = {
        'temperature': temperature,
        'humidity': humidity,
        'light_level': light_level,
        'heart_rate_data': max30102_data,
        'object_temp': object_temp,
        'heart_rate_voltage': heart_rate_voltage
    }

    # Format data for InfluxDB
    influxdb_payload = format_influxdb_data(data_to_send)

    # Print the sensor data (for debugging)
    print("InfluxDB Payload:\n", influxdb_payload)
    
    # Send the data over UART to Raspberry Pi 5
    uart.write(influxdb_payload + '\n')
    
    # Delay before next read
    time.sleep(1)
