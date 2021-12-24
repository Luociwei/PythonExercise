# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLI2CDef

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MAX6642Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MAX6642Def:
    # Command-Byte Assignments
    CMD_REGS = {
        'local': {
            'temperature': 0x00,
            'extended': 0x11,
            'rd_high_limit': 0x05,
            'wr_high_limit': 0x0B,
        },
        'remote': {
            'temperature': 0x01,
            'extended': 0x10,
            'rd_high_limit': 0x07,
            'wr_high_limit': 0x0D,
        },
        'state': 0x02,
        'rd_config': 0x03,
        'wr_config': 0x09,
        'single_shot': 0x0F,
        'manufacturer_id': 0xFE
    }

    # Configuration-Byte Bit Assignments
    CONFIG_BIT = {
        'mask_alert': 7,
        'stop': 6,
        'external_only': 5,
        'fault_queue': 4,
    }

    # Manufacturer ID(4Dh)
    ID = 0x4D


class MAX6642(object):
    '''
    MAX6642 Driver:
        The MAX6642 precise, two-channel digital temperature sensor accurately
        measures the temperature of its own die and a remote PN junction and
        reports the temperature data over a 2-wire serial interface.

    ClassType = ADC

    Args:
        dev_addr:   hexmial,             I2C device address of TEMPERATURE SENSOR.
        i2c_bus:    instance(I2C)/None,  i2c bus instance, If not using this parameter,
                                         it will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        axi4_i2c = MIXI2CSG(axi)
        max6642 = MAX6642(0x48, axi4_i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        # Slave address is 0x48~0x4F, Table 6 of MAX6642 Datasheet
        assert dev_addr & ~0x07 == 0x48
        self.dev_addr = dev_addr

        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("i2c_emulator",
                                          PLI2CDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus

    def _register_read(self, reg_addr, reg_size):
        '''
        MAX6642 read register

        Args:
            reg_addr:   hexmial,  register address.
            reg_size:   int,      read length.

        Returns:
            list, [value], each element takes one byte.

        '''

        return self.i2c_bus.write_and_read(self.dev_addr,
                                           [reg_addr], reg_size)

    def _register_write(self, reg_addr, reg_data):
        '''
        MAX6642 write register

        Args:
            reg_addr:    hexmial,   register address.
            reg_data:    int,       register data.

        '''
        self.i2c_bus.write(self.dev_addr, [reg_addr, reg_data])

    def get_temperature(self, channel, extended=False):
        '''
        MAX6642 read local or remote temperature, chose to read extended resolution.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            extended:   boolean, [True, False], enable or disable extended resolution.

        Returns:
            int/float, value, unit °C.

        '''
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS
        assert isinstance(extended, bool)

        # The temperature data format for these registers is
        # 8 bits for each channel, with the LSB representing +1°C
        ret = self._register_read(MAX6642Def.CMD_REGS[channel]['temperature'], 1)
        temp_val = ret[0]

        if extended:
            # extended 2 bits, the resolution to +0.25°C per LSB
            ret = self._register_read(MAX6642Def.CMD_REGS[channel]['extended'], 1)
            ext_val = (ret[0] >> 6) & 0x3
            temp_val += (ext_val * 0.25)

        return temp_val

    def read_high_limit(self, channel):
        '''
        MAX6642 read local or remote high limit.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.

        '''
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS

        return self._register_read(MAX6642Def.CMD_REGS[channel]['rd_high_limit'], 1)[0]

    def write_high_limit(self, channel, limit):
        '''
        MAX6642 write local or remote high limit.
        The intended measuring range for the MAX6642 is 0 to +150 (Celsius).
        However, the limit is an 8 bit unsigned number and can be set between 0 and +255.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            limit:      int, [0~255], temperature limit.

        '''
        channel = channel.lower()
        assert channel in MAX6642Def.CMD_REGS
        assert isinstance(limit, int) and 0 <= limit <= 0xff

        self._register_write(MAX6642Def.CMD_REGS[channel]['wr_high_limit'], limit)

    def manufacturer_id(self):
        '''
        MAX6642 read manufacturer ID(4Dh).
        '''
        return self._register_read(MAX6642Def.CMD_REGS['manufacturer_id'], 1)[0]

    def single_shot(self):
        '''
        MAX6642 single-shot command, if the single-shot command is received
        while the MAX6642 is in standby mode (RUN bit = 1).
        '''
        self._register_write(MAX6642Def.CMD_REGS['single_shot'], 0x01)

    def read_state(self):
        '''
        MAX6642 read status byte.
        '''
        return self._register_read(MAX6642Def.CMD_REGS['state'], 1)[0]

    def read_config(self):
        '''
        MAX6642 read configuration_byte.
        '''
        return self._register_read(MAX6642Def.CMD_REGS['rd_config'], 1)[0]

    def write_config(self, config_bit, bit_val):
        '''
        MAX6642 write configuration_byte bit.

        Args:
            config_bit:    string, ['mask_alert', 'stop', 'external_only', 'fault_queue'].
            bit_val:       int, [0, 1], bit value.

        '''
        assert config_bit in MAX6642Def.CONFIG_BIT
        assert isinstance(bit_val, int) and 0 <= bit_val <= 1

        config_val = self.read_config()

        if bit_val:
            config_val |= (0x1 << MAX6642Def.CONFIG_BIT[config_bit])
        else:
            config_val &= ~(0x1 << MAX6642Def.CONFIG_BIT[config_bit])

        self._register_write(MAX6642Def.CMD_REGS['wr_config'], config_val)
