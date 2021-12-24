# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_emulator_plugin import I2CEmulatorPlugin

__author__ = 'yuanle@SmartGiant'
__version__ = '0.2'


class AD56X9REmulatorPlugin(I2CEmulatorPlugin):

    def __init__(self):
        I2CEmulatorPlugin.__init__(self)
