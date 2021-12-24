# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLSPIDef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AD5693Def:
    NOP_REGISTER = 0x00
    INPUT_REGISTER = 0x10
    LDAC_REGISTER = 0x20
    DAC_REGISTER = 0x30
    CONTROL_REGISTER = 0x40
    REG_REF_MASK = (1 << 12)
    REG_REF_INTERNEL = (0 << 12)
    REG_REF_EXTERNAL = (1 << 12)
    REG_GAIN_MASK = (1 << 11)
    REG_GAIN_VREF = (0 << 11)
    REG_GAIN_2VREF = (1 << 11)
    REG_RESET_SET = (1 << 15)

    REF_INTERNAL = 'internal'
    REF_EXTERNAL = 'external'
    # internel reference volt is 2500 mV
    INTERNAL_REF_MVOLT = 2500
    DAC_FULL_SCALE = pow(2, 16)


class AD5693Exception(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class AD5693(object):
    '''
    AD5693 function class

    ClassType = DAC

    Args:
        dev_addr: hexmial,             ad5693 device address.
        i2c_bus:  instance(I2C)/None,  i2c bus instance, if not using, will create emulator.
        mvref:    float, default 2500, reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ad5693 = AD5693(0x4C, i2c_bus, 2500)

    '''
    def __init__(self, dev_addr, i2c_bus=None, mvref=2500):
        assert (dev_addr & (~0x03)) == 0x4C
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('ad5693_emulator', PLSPIDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self.control_register = 0
        self.set_ref(AD5693Def.REF_INTERNAL)
        self.mvref = mvref
        self.dev_name = self.i2c_bus._dev_name

    def write_register(self, register, high_byte, low_byte):
        '''
        AD5693 write register

        Args:
            register:   hexmial, [0~0xff], specific register to write data.
            high_byte:  hexmial, [0~0xff], high byte data to write.
            low_byte:   hexmial, [0~0xff], low byte data to write.

        Examples:
            ad5693.write_register(0x00, 0x01, 0x02)

        '''
        self.i2c_bus.write(self.dev_addr, [register, high_byte, low_byte])

    def get_ref(self):
        '''
        AD5693 get reference mode

        Returns:
            string, ['internal', 'external']

        Examples:
            ref = ad5693.get_ref()
            print(ref)

        '''
        ref_value = self.control_register & AD5693Def.REG_REF_MASK
        return (AD5693Def.REF_INTERNAL if ref_value == AD5693Def.REG_REF_INTERNEL else AD5693Def.REF_EXTERNAL)

    def set_ref(self, ref):
        '''
        AD5693 set reference mode

        Args:
            ref: string, ['internal', 'external'], ad5693 reference mode.

        Examples:
            ad5693.set_ref('internal')

        '''
        assert ref in [AD5693Def.REF_INTERNAL, AD5693Def.REF_EXTERNAL]
        self.control_register &= ~AD5693Def.REG_REF_MASK
        self.control_register |= (AD5693Def.REG_REF_INTERNEL
                                  if ref == AD5693Def.REF_INTERNAL
                                  else AD5693Def.REG_REF_EXTERNAL)
        self.write_register(AD5693Def.CONTROL_REGISTER,
                            (self.control_register >> 8) & 0xFF,
                            self.control_register & 0xFF)

    def get_gain(self):
        '''
        AD5693 get gain value

        Returns:
            int, [1, 2].

        Examples:
            gain = ad5693.gain()
            print(gain)

        '''
        gain_value = self.control_register & AD5693Def.REG_GAIN_MASK
        return (1 if gain_value == AD5693Def.REG_GAIN_VREF else 2)

    def set_gain(self, gain):
        '''
        AD5693 set gain value

        Args:
            gain:    int, [1, 2], gain value.

        Examples:
            ad5693.set_gain()

        '''
        assert gain in [1, 2]
        self.control_register &= ~AD5693Def.REG_GAIN_MASK
        self.control_register |= (AD5693Def.REG_GAIN_VREF if gain == 1 else AD5693Def.REG_GAIN_2VREF)
        self.write_register(AD5693Def.CONTROL_REGISTER,
                            (self.control_register >> 8) & 0xFF,
                            self.control_register & 0xFF)

    def reset(self):
        '''
        AD5693 reset function

        Examples:
            ad5693.reset()

        '''
        self.write_register(AD5693Def.CONTROL_REGISTER,
                            (AD5693Def.REG_RESET_SET >> 8) & 0xFF,
                            AD5693Def.REG_RESET_SET & 0xFF)

    def output_volt_dc(self, channel, volt):
        '''
        AD5693 output dc voltage

        Args:
            channel: int, [0], channel must be 0.
            volt:    float, voltage vlaue to output.

        Examples:
            ad5693.output_volt_dc(0, 1000)

        '''
        assert volt >= 0
        mvref = (AD5693Def.INTERNAL_REF_MVOLT if self.get_ref() == AD5693Def.REF_INTERNAL else self.mvref)
        if volt > mvref * self.get_gain():
            msg = 'volt is too large, reference is %d mV' % (self.get_gain() * mvref)
            raise AD5693Exception(self.dev_name, msg)
        dac_value = int(volt * AD5693Def.DAC_FULL_SCALE / (self.get_gain() * mvref))
        self.write_register(AD5693Def.DAC_REGISTER, (dac_value >> 8) & 0xFF, dac_value & 0xFF)
