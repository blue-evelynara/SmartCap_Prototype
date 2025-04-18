# bh1750.py

import time
from machine import I2C

PWR_DOWN = 0x00
PWR_ON = 0x01
RESET = 0x07
CONT_HIRES_1 = 0x10
CONT_HIRES_2 = 0x11
CONT_LORES = 0x13
ONCE_HIRES_1 = 0x20
ONCE_HIRES_2 = 0x21
ONCE_LORES = 0x23

class BH1750:
    def __init__(self, i2c, address=0x23, mode=CONT_HIRES_1):
        self.i2c = i2c
        self.addr = address
        self.mode = mode
        self.on()
        self.reset()

    def on(self):
        self.i2c.writeto(self.addr, bytes([PWR_ON]))

    def off(self):
        self.i2c.writeto(self.addr, bytes([PWR_DOWN]))

    def reset(self):
        self.i2c.writeto(self.addr, bytes([RESET]))

    def luminance(self, mode=None):
        if mode is None:
            mode = self.mode
        self.i2c.writeto(self.addr, bytes([mode]))
        time.sleep_ms(180)
        raw = self.i2c.readfrom(self.addr, 2)
        result = (raw[0] << 8) | raw[1]
        return result / 1.2

