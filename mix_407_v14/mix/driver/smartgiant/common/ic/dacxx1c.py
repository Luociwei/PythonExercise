# -*- coding: utf-8 -*-

__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.1'


class DACXX1CDef:
    # 8/10/12-bit
    DAC081C_RESOLUTION = 8
    DAC101C_RESOLUTION = 10
    DAC121C_RESOLUTION = 12

    # Power-Down Modes
    POWER_MODE = {
        'NORMAL': 0,    # Normal operation
        '2.5K': 1,      # 2.5 kOhm to GND
        '100K': 2,      # 100 kOhm to GND
        'Hi_Z': 3       # High Impedance
    }


class DACXX1C(object):
    '''
    DACXX1C Driver:

        The DACXX1C is a 8/10/12-bit, single channel, voltage output digital-to-analog
        converter (DAC) that operates from a +2.7V to 5.5V supply.
        The output amplifier allows rail-to-rail output swing and has an 6µsec settling time.
        The DACXX1C uses the supply voltage as the reference to provide the widest dynamic
        output range and typically consumes 132µA while operating at 5.0V.
        It is available in 6-lead SOT and WSON packages and provides three address options (pin selectable).

        DAC081C: 8-bit DAC.
        DAC101C: 10-bit DAC.
        DAC121C: 12-bit DAC.

    ClassType = DAC

    Args:
        dev_addr:   hexmial,              DACXX1C i2c bus device address.
        i2c_bus:    instance(I2C)/None,   i2c bus class instance.
        mvref:      int/float, unit mV,   default 3300, DACXX1C reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        dacxx1c = DACXX1C(0x09, i2c_bus, 3300)
        dacxx1c.output_volt(1000)
    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=3300):
        assert isinstance(dev_addr, int)
        assert isinstance(mvref, (float, int)) and mvref > 0.0

        self._dev_addr = dev_addr
        self.i2c_bus = i2c_bus
        self.mvref = mvref
        self.resolution = DACXX1CDef.DAC101C_RESOLUTION

    def output_volt(self, volt, mode='NORMAL'):
        '''
        Set the output voltage.

        Args:
            volt:      int/float, [0 ~ mvref], unit mV, Output voltage value.
            mode:      string, ['NORMAL', '2.5K', '100K', 'Hi_Z'], Power-Down Modes.
        '''
        assert isinstance(volt, (int, float)) and 0.0 <= volt <= self.mvref
        assert mode in DACXX1CDef.POWER_MODE

        # Calculate DAC code value to setup
        dac_value = int(float(volt) / self.mvref * ((0x1 << self.resolution) - 1))
        code = (((DACXX1CDef.POWER_MODE[mode] << 12) & 0x3000) |
                (dac_value << (12 - self.resolution))) & 0xffff

        high_byte = (code >> 8) & 0xFF
        low_byte = code & 0xFF
        self.i2c_bus.write(self._dev_addr, [high_byte, low_byte])

    def readback_volt(self):
        '''
        Reads back the binary value and calculate the voltage.

        Returns:
            float, value, unit mV, the current voltage.
        '''
        # Reads back the binary value
        raw_data = self.i2c_bus.read(self._dev_addr, 2)
        raw_value = (raw_data[0] << 8) | raw_data[1]
        volt_code = (raw_value >> (12 - self.resolution)) & ((0x1 << self.resolution) - 1)

        # Calculate the voltage
        volt = float(self.mvref * volt_code) / ((0x1 << self.resolution) - 1)

        return volt


class DAC081C(DACXX1C):
    '''
    DAC081C: 8-bit DAC.

    Args:
        dev_addr:   hexmial,              DAC081C i2c bus device address.
        i2c_bus:    instance(I2C)/None,   i2c bus class instance.
        mvref:      int/float, unit mV,   default 3300, DAC081C reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        dac = DAC081C(0x09, i2c_bus, 3300)
        dac.output_volt(1000)
    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=3300):
        super(DAC081C, self).__init__(dev_addr, i2c_bus, mvref)
        self.resolution = DACXX1CDef.DAC081C_RESOLUTION


class DAC101C(DACXX1C):
    '''
    DAC101C: 10-bit DAC.

    Args:
        dev_addr:   hexmial,              DAC101C i2c bus device address.
        i2c_bus:    instance(I2C)/None,   i2c bus class instance.
        mvref:      int/float, unit mV,   default 3300, DAC101C reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        dac = DAC101C(0x09, i2c_bus, 3300)
        dac.output_volt(1000)
    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=3300):
        super(DAC101C, self).__init__(dev_addr, i2c_bus, mvref)
        self.resolution = DACXX1CDef.DAC101C_RESOLUTION


class DAC121C(DACXX1C):
    '''
    DAC121C: 12-bit DAC.

    Args:
        dev_addr:   hexmial,              DAC121C i2c bus device address.
        i2c_bus:    instance(I2C)/None,   i2c bus class instance.
        mvref:      int/float, unit mV,   default 3300, DAC121C reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        dac = DAC121C(0x09, i2c_bus, 3300)
        dac.output_volt(1000)
    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=3300):
        super(DAC121C, self).__init__(dev_addr, i2c_bus, mvref)
        self.resolution = DACXX1CDef.DAC121C_RESOLUTION
