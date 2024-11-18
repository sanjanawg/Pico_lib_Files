from machine import I2C, Pin
from utime import sleep_ms

class I2CBase:
    def writeto_mem(self, addr, memaddr, buf, *, addrsize=8):
        raise NotImplementedError('writeto_mem')

    def readfrom_mem(self, addr, memaddr, nbytes, *, addrsize=8):
        raise NotImplementedError('readfrom_mem')

    def write8(self, addr, buf, stop=True):
        raise NotImplementedError('write')

    def read16(self, addr, nbytes, stop=True):
        raise NotImplementedError('read')

    def __init__(self, bus=None, freq=None, sda=None, scl=None):
        raise NotImplementedError('__init__')

class VEML_I2C(I2CBase):
    def __init__(self, bus=None, freq=None, sda=None, scl=None):
        
        if bus is not None and sda is not None and scl is not None:
            print('Using supplied bus, sda, and scl to create machine.I2C() with freq: {} Hz'.format(freq))
            self.i2c = I2C(bus, freq=freq, sda=sda, scl=scl)
        else:
            raise Exception("Provide at least bus, sda, and scl")

        self.writeto_mem = self.i2c.writeto_mem
        self.readfrom_mem = self.i2c.readfrom_mem

    def write8(self, addr, reg, data):
        if reg is None:
            self.i2c.writeto(addr, data)
        else:
            self.i2c.writeto(addr, reg + data)
            
    def read16(self, addr, reg):
        self.i2c.writeto(addr, reg, False)
        return self.i2c.readfrom(addr, 2)
        
    def scan(self):
        print([hex(i) for i in self.i2c.scan()])
        
def create_veml_i2c(bus=None, freq=None, sda=None, scl=None, suppress_warnings=True):
    i2c = VEML_I2C(bus=bus, freq=freq, sda=sda, scl=scl)
    return i2c

# Registers
_veml6030Address = 0x48
_ALS_CONF = 0x00
_REG_ALS = 0x04

_DEFAULT_SETTINGS = b'\x00' # initialise gain:1x, integration 100ms, persistence 1, disable interrupt

class VEML6030(object):
    def __init__(self, i2c, addr=_veml6030Address):

        self.i2c = i2c
        self.addr = addr
        self.gain=1
        self.res = 0.0576 # [lx/bit]
        self.i2c.writeto_mem(self.addr, _ALS_CONF, _DEFAULT_SETTINGS)
        sleep_ms(4)
        
    def read(self):
        try:
            data = self.i2c.readfrom_mem(self.addr, _REG_ALS, 2)
        except:
            print(i2c_err_str.format(self.addr))
            return float('NaN')
        return int.from_bytes(data, 'little') * self.res
    
    def setGain(self,g):
        if g not in [0.125,0.25,1,2]:
            raise ValueError ('Invalid gain. Accepted values: 0.125, 0.25, 1, 2')
        self.gain=g
        if g == 0.125:
            conf = b'\x00\x10'
            self.res = 0.4608
        if g == 0.25:
            conf = b'\x00\x18'
            self.res = 0.2304
        if g == 1:
            conf = b'\x00\x00'
            self.res = 0.0576
        if g == 2:
            conf = b'\x00\x08'
            self.res = 0.0288
        self.setBits(_ALS_CONF, conf, 'b\x18\x00')
        sleep_ms(4)
        return
    
    def setBits(self, address, byte, mask):
        old = self.i2c.readfrom_mem(self.addr, address, 2)
        old_byte = int.from_bytes(self.i2c.readfrom_mem(self.addr, address, 2),'little')
        temp_byte = old_byte
        int_byte = int.from_bytes(byte,"little")
        int_mask = int.from_bytes(mask,"big")
        for n in range(16): # Cycle through each bit
            bit_mask = (int_mask >> n) & 1
            if bit_mask == 1:
                if ((int_byte >> n) & 1) == 1:
                    temp_byte = temp_byte | 1 << n
                else:
                    temp_byte = temp_byte & ~(1 << n)
        new_byte = temp_byte
        print(new_byte)
        self.i2c.writeto_mem(self.addr, address, new_byte.to_bytes(2,'little'))
          