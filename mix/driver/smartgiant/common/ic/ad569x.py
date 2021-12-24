# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class AD569XException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class AD569XDef:
    # Refering to AD569X datasheet
    SLAVE_ADDR_5MSB = 0x0C
    VREF = 2500  # mV
    # GAIN pin tied to GND (output range: 0V to VREF)
    GAIN_1 = 1
    # GAIN pin tied to VDD (output range: 0V to 2*VREF)
    GAIN_2 = 2
    # 12/14/16-bit
    AD5694_RESOLUTION = 12
    AD5696_RESOLUTION = 16
    AD5694R_RESOLUTION = 12
    AD5695R_RESOLUTION = 14
    AD5696R_RESOLUTION = 16

    # Command Definitions
    COMMAND = {
        'NOP': (0 << 4),
        'WR_INPUT_N': (1 << 4),
        'UPDATE_DAC_N': (2 << 4),
        'WR_UPDT_DAC_N': (3 << 4),
        'POWE_RMODE': (4 << 4),
        'LDAC_MASK': (5 << 4),
        'SOFT_RESET': (6 << 4),
        'INT_REF_SETUP': (7 << 4)
    }

    # Address Bits and Selected DACs
    ADDR_DAC = {
        'DAC_A': 1,
        'DAC_B': 2,
        'DAC_C': 4,
        'DAC_D': 8,
    }

    # Power-Down/Power-Up Operation
    POWER_MODE = {
        'NORMAL': 0,  # Normal operation
        '1K': 1,  # 1 kOhm to GND
        '100K': 2,  # 100 kOhm to GND
        '3_STATE': 3  # Three-state
    }

    # Power-Down/Power-Up Operation
    POWER_PDX = {
        'PDA': {
            'OFFSET': 0,
            'MASK': (0x3 << 0),
        },
        'PDB': {
            'OFFSET': 2,
            'MASK': (0x3 << 2),
        },
        'PDC': {
            'OFFSET': 4,
            'MASK': (0x3 << 4),
        },
        'PDD': {
            'OFFSET': 0,
            'MASK': (0x3 << 6),
        },
    }

    # Reference Setup Register
    VREF_MODE = {
        'INT_REF_ON': 0,
        'INT_REF_OFF': 1
    }

    CHANNEL_LIST = ['DAC_A', 'DAC_B', 'DAC_C', 'DAC_D']


class AD569X(object):
    '''
    AD569X Driver:
        The AD5694/AD5696, members of the nanoDAC+™ family are low power, quad,
        12/16-bit buffered voltage output DACs. The devices include a gain select
        pin giving a full-scale output of 0V to VREF (gain = 1) or 0V to 2VREF (gain = 2).

        The AD5694R/AD5695R/AD5696R nanoDAC+TM are quad, 12/14/16-bit, rail-to-rail,
        voltage output DACs. The devices include a 2.5V, 2ppm/˚C internal reference
        (enabled by default) and a gain select pin giving a full-scale output of
        2.5V (gain=1) or 5V (gain=2).

        AD5694: 12-bit DAC, no internal voltage reference.
        AD5696: 16-bit DAC, no internal voltage reference.
        AD5694R: 12-bit DAC, with internal voltage reference.
        AD5695R: 14-bit DAC, with internal voltage reference.
        AD5696R: 16-bit DAC, with internal voltage reference.

    ClassType = DAC

    Args:
        dev_addr: hexmial,                 AD569X i2c bus device address.
        i2c_bus:  instance(I2C)/None,      i2c bus class instance, if not using, will create emulator.
        mvref:    int/float, unit mV, default 2500, AD569X reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ad569x = AD569X(0x0D, i2c_bus, 2500)
        ad569x.output_volt(0, 1000)

    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        assert isinstance(dev_addr, int) and (dev_addr & (~0x03)) == AD569XDef.SLAVE_ADDR_5MSB
        assert isinstance(vref, (float, int)) and vref > 0.0

        self._dev_addr = dev_addr
        self.vref = vref
        self.resolution = AD569XDef.AD5696_RESOLUTION
        self.gain = AD569XDef.GAIN_1

        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('ad569x_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

    def _write_register(self, command, data):
        '''
        Write data to Input Shift Register (24-bit wide) of AD569X.

        Args:
            command:   hexmial, [0~0xff], command byte.
            data:      hexmial, [0~0xffff], high_byte and low_byte.

        '''
        assert isinstance(command, int) and 0x00 <= command <= 0xFF
        assert isinstance(data, int) and 0x0000 <= data <= 0xFFFF

        high_byte = (data >> 8) & 0xFF
        low_byte = data & 0xFF

        self.i2c_bus.write(self._dev_addr, [command, high_byte, low_byte])

    def power_mode(self, channel, mode='NORMAL'):
        '''
        Puts the device in a specific power mode.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.
            mode:      string, ['NORMAL', '1K', '100K', '3_STATE'], Power mode of the device.

        '''
        mode = mode.upper()
        assert channel in [0, 1, 2, 3]
        assert mode in AD569XDef.POWER_MODE

        wr_data = 0
        channel_name = AD569XDef.CHANNEL_LIST[channel]
        pdx = 'PD' + channel_name[-1:]
        wr_data &= ~(AD569XDef.POWER_PDX[pdx]['MASK'])
        wr_data |= (AD569XDef.POWER_MODE[mode] << AD569XDef.POWER_PDX[pdx]['OFFSET'])

        self._write_register(AD569XDef.COMMAND['POWE_RMODE'], wr_data)

    def soft_reset(self):
        '''
        Resets the device(clears the outputs to either zero scale or midscale).
        '''
        self._write_register(AD569XDef.COMMAND['SOFT_RESET'], 0)

    def select_vref_mode(self, vref_mode):
        '''
        Select internal or external voltage reference.

        Args:
            vref_mode:   string, ['INT_REF_ON', 'INT_REF_OFF'], Internal Reference On/Off.

        '''
        vref_mode = vref_mode.upper()
        assert vref_mode in AD569XDef.VREF_MODE

        self._write_register(AD569XDef.COMMAND['INT_REF_SETUP'], AD569XDef.VREF_MODE[vref_mode])

    def output_volt(self, channel, volt):
        '''
        Set the output voltage of the selected channel.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.
            volt:      int/float, [0~2500], Output voltage value.

        Returns:
            float, value, unit mV, the current voltage of specific channel.

        '''
        assert channel in [0, 1, 2, 3]
        assert isinstance(volt, (int, float)) and 0.0 <= volt <= (self.vref * self.gain)

        channel_name = AD569XDef.CHANNEL_LIST[channel]
        command = AD569XDef.COMMAND['WR_UPDT_DAC_N'] + AD569XDef.ADDR_DAC[channel_name]
        # Calculate DAC code value to setup
        dac_value = int(volt * (0x1 << self.resolution) / (self.vref * self.gain))
        code = (dac_value << (16 - self.resolution)) & 0xffff
        self._write_register(command, code)

        # Calculate the voltage
        channel_volt = float(self.vref * self.gain * code) / (0x1 << self.resolution)
        return channel_volt

    def readback_volt(self, channel):
        '''
        Reads back the binary value written to one of the channels, and calculate the voltage.

        Args:
            channel:   int, [0, 1, 2, 3), DAC Channel.

        Returns:
            float, value, unit mV, the current voltage of specific channel.

        '''

        assert channel in [0, 1, 2, 3]

        channel_name = AD569XDef.CHANNEL_LIST[channel]
        self.i2c_bus.write(self._dev_addr, [AD569XDef.ADDR_DAC[channel_name]])
        # Reads back the binary value
        rd_data = self.i2c_bus.read(self._dev_addr, 2)
        channel_value = (rd_data[0] << 8) | rd_data[1]
        channel_value >>= (16 - self.resolution)
        # Calculate the voltage
        channel_volt = float(self.vref * self.gain * channel_value - 1) / (0x1 << self.resolution)

        return channel_volt


class AD5694(AD569X):
    '''
    AD5694 Driver:
        The AD5694, members of the nanoDAC+™ family are low power, quad,
        12-bit buffered voltage output DACs. The devices include a gain select
        pin giving a full-scale output of 0V to VREF (gain = 1) or 0V to 2VREF (gain = 2).

        AD5694: 12-bit DAC, no internal voltage reference.

    :param     dev_addr: hexmial,        AD569X i2c bus device address
    :param     i2c_bus:  Instance/None,  i2c bus class instance, if not using, will create emulator

    :example:
                axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
                i2c_bus = MIXI2CSG(axi4_bus)
                ad5694 = AD5694(0x0D, i2c_bus)
    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        super(AD5694, self).__init__(dev_addr, i2c_bus, vref)
        self.resolution = AD569XDef.AD5694_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5696(AD569X):
    '''
    AD5696 Driver:
        The AD5696, members of the nanoDAC+™ family are low power, quad,
        16-bit buffered voltage output DACs. The devices include a gain select
        pin giving a full-scale output of 0V to VREF (gain = 1) or 0V to 2VREF (gain = 2).

        AD5696: 16-bit DAC, no internal voltage reference.

    :param     dev_addr: hexmial,        AD569X i2c bus device address
    :param     i2c_bus:  Instance/None,  i2c bus class instance, if not using, will create emulator

    :example:
                axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
                i2c_bus = MIXI2CSG(axi4_bus)
                ad5696 = AD5696(0x0D, i2c_bus)
    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        super(AD5696, self).__init__(dev_addr, i2c_bus, vref)
        self.resolution = AD569XDef.AD5696_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5694R(AD569X):
    '''
    AD5694R Driver:
        The AD5694R nanoDAC+TM are quad, 12-bit, rail-to-rail,
        voltage output DACs. The devices include a 2.5V, 2ppm/˚C internal reference
        (enabled by default) and a gain select pin giving a full-scale output of
        2.5V (gain=1) or 5V (gain=2).

        AD5694R: 12-bit DAC, with internal voltage reference.

    ClassType = DAC

    Args:
        dev_addr: hexmial,                 AD569X i2c bus device address.
        i2c_bus:  instance(I2C)/None,      i2c bus class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ad5694r = AD5694R(0x0D, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        super(AD5694R, self).__init__(dev_addr, i2c_bus, vref)
        self.resolution = AD569XDef.AD5694R_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5695R(AD569X):
    '''
    AD5695R Driver:
        The AD5695R nanoDAC+TM are quad, 14-bit, rail-to-rail,
        voltage output DACs. The devices include a 2.5V, 2ppm/˚C internal reference
        (enabled by default) and a gain select pin giving a full-scale output of
        2.5V (gain=1) or 5V (gain=2).

        AD5695R: 14-bit DAC, with internal voltage reference.

    ClassType = DAC

    Args:
        dev_addr: hexmial,                 AD569X i2c bus device address.
        i2c_bus:  instance(I2C)/None,      i2c bus class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ad5695r = AD5695R(0x0D, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        super(AD5695R, self).__init__(dev_addr, i2c_bus, vref)
        self.resolution = AD569XDef.AD5695R_RESOLUTION
        self.gain = AD569XDef.GAIN_1


class AD5696R(AD569X):
    '''
    AD5696R Driver:
        The AD5696R nanoDAC+TM are quad, 16-bit, rail-to-rail,
        voltage output DACs. The devices include a 2.5V, 2ppm/˚C internal reference
        (enabled by default) and a gain select pin giving a full-scale output of
        2.5V (gain=1) or 5V (gain=2).

        AD5696R: 16-bit DAC, with internal voltage reference.

    ClassType = DAC

    Args:
        dev_addr: hexmial,                 AD569X i2c bus device address.
        i2c_bus:  instance(I2C)/None,      i2c bus class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ad5696r = AD5696R(0x0D, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None, vref=2500):
        super(AD5696R, self).__init__(dev_addr, i2c_bus, vref)
        self.resolution = AD569XDef.AD5696R_RESOLUTION
        self.gain = AD569XDef.GAIN_1
