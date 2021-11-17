# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_def import AXI4Def
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXEepromEmulateSGDef:
    REG_SIZE = 256
    MODULE_EN_REG = 0x10
    I2C_S_ADDR_REG = 0x30
    I2C_S_CONFIG_REG = 0x31
    I2C_S_BIT_RATE_CONFIG_REG = 0x32
    I2C_S_RAM_DIN_REG = 0x34
    I2C_S_RAM_ADDR_REG = 0x38
    I2C_S_RAM_WR_REG = 0x3A
    I2C_S_RAM_DOUT_REG = 0x3C

    MODULE_ENABLE = 0x01
    MODULE_DISABLE = 0x00
    DEFAULT_SPEED_HZ = 400000
    MAX_SPEED_HZ = 2000000
    SYS_CLK_INTERVAL_NS = 8

    MAX_DEV_ADDR = 0x7F
    MIN_REG_ADDR_LEN = 1
    MAX_REG_ADDR_LEN = 2
    MIN_DATA_WIDTH = 1
    MAX_DATA_WIDTH = 4
    MAX_REG_ADDR = 0xFFFF
    WRITE_ENABLE = 1


class MIXEepromEmulateSG(object):
    '''
    MIX_Eeprom_Emulate_SG IP driver which is used to emulate an eeprom.

    Args:
        axi4_bus: string/instance, this parameter can be instance of AXI4LiteBus or
                  device name in '/dev/' folder with full path.

    Examples:
        emu = MIXEepromEmulateSG('/dev/MIX_Eeprom_Emulate_0')
        # config emulator: device addr 0x50, speed 400000 Hz,
        # reg addr length 1 byte, data width 1 byte
        emu.config(400000, 0x50, 1, 1)
        # read 2 bytes data from address 0x01 of emulator,
        # dut must write data to emulator first through I2C bus.
        data = emu.register_read(0x01, 2)
        print(data)
        # write data to address 0x01 of emulator,
        # then dut can read data from emulator through I2C bus.
        emu.register_write(0x01, [1,2,3])
    '''

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXEepromEmulateSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

    def _disable(self):
        '''
        Disable IP module function, this is a private function.
        '''
        self.axi4_bus.write_8bit_inc(MIXEepromEmulateSGDef.MODULE_EN_REG,
                                     [MIXEepromEmulateSGDef.MODULE_DISABLE])

    def _enable(self):
        '''
        Enable IP module function, this is a private function.
        '''
        self.axi4_bus.write_8bit_inc(MIXEepromEmulateSGDef.MODULE_EN_REG,
                                     [MIXEepromEmulateSGDef.MODULE_ENABLE])

    def config(self, speed_hz, dev_addr, reg_len, data_width):
        '''
        Config emulator speed, device address, register address length and data width.

        Args:
            speed_hz:   int, [0~2000000], I2C bus speed in Hz.
            dev_addr:   int, [0~0x7F], device address.
            reg_len:    int, [1,2], register address length.
            data_width: int, [1,2,3,4], one data width in byte.

        Retruns:
            string, "done", return "done" if execute successfully.
        '''
        assert isinstance(speed_hz, int)
        assert speed_hz > 0
        assert speed_hz <= MIXEepromEmulateSGDef.MAX_SPEED_HZ
        assert isinstance(dev_addr, int)
        assert 0 <= dev_addr <= MIXEepromEmulateSGDef.MAX_DEV_ADDR
        assert isinstance(reg_len, int)
        assert reg_len >= MIXEepromEmulateSGDef.MIN_REG_ADDR_LEN
        assert reg_len <= MIXEepromEmulateSGDef.MAX_REG_ADDR_LEN
        assert isinstance(data_width, int)
        assert data_width >= MIXEepromEmulateSGDef.MIN_DATA_WIDTH
        assert data_width <= MIXEepromEmulateSGDef.MAX_DATA_WIDTH

        self.data_width = data_width
        bit_clk_cnt = AXI4Def.AXI4_CLOCK / speed_hz
        bit_clk_delay = int(bit_clk_cnt / MIXEepromEmulateSGDef.SYS_CLK_INTERVAL_NS)

        self._disable()
        self.axi4_bus.write_16bit_inc(MIXEepromEmulateSGDef.I2C_S_BIT_RATE_CONFIG_REG, [bit_clk_delay])
        self.axi4_bus.write_8bit_inc(MIXEepromEmulateSGDef.I2C_S_ADDR_REG, [dev_addr])
        # I2C_S_CONFIG_REG combined with data width bit[3:0] & register length bit[7:4]
        self.axi4_bus.write_8bit_inc(MIXEepromEmulateSGDef.I2C_S_CONFIG_REG, [(reg_len << 4) | data_width])
        self._enable()
        return "done"

    def get_dev_addr(self):
        '''
        Get current device address.

        Returns:
            int, [0~0x7F], current device address.
        '''
        return self.axi4_bus.read_8bit_inc(MIXEepromEmulateSGDef.I2C_S_ADDR_REG, 1)[0]

    def get_speed(self):
        '''
        Get current I2C speed in Hz.

        Returns:
            int, current I2C speed in Hz.
        '''
        freq_reg_val = self.axi4_bus.read_16bit_inc(MIXEepromEmulateSGDef.I2C_S_BIT_RATE_CONFIG_REG, 1)[0]
        return int(AXI4Def.AXI4_CLOCK / (freq_reg_val * MIXEepromEmulateSGDef.SYS_CLK_INTERVAL_NS))

    def get_reg_len(self):
        '''
        Get current register address length in byte.

        Returns:
            int, [1,2], current register address length.
        '''
        reg_val = self.axi4_bus.read_8bit_inc(MIXEepromEmulateSGDef.I2C_S_CONFIG_REG, 1)[0]
        return (reg_val >> 4) & 0xF

    def get_data_width(self):
        '''
        Get current data width in byte.

        Returns:
            int, [1,2,3,4], current data width.
        '''
        reg_val = self.axi4_bus.read_8bit_inc(MIXEepromEmulateSGDef.I2C_S_CONFIG_REG, 1)[0]
        return reg_val & 0xF

    def register_read(self, reg_addr, rd_len):
        '''
        Read data from eeprom emulator.

        Args:
            reg_addr:   int, register address
            rd_len:     int, length of data to be read.

        Returns:
            list, [value], data has been read. One data width is decided by config function.
        '''
        assert reg_addr >= 0
        assert reg_addr <= MIXEepromEmulateSGDef.MAX_REG_ADDR

        result = []
        for i in range(rd_len):
            self.axi4_bus.write_16bit_inc(MIXEepromEmulateSGDef.I2C_S_RAM_ADDR_REG, [reg_addr])
            reg_val = self.axi4_bus.read_32bit_inc(MIXEepromEmulateSGDef.I2C_S_RAM_DOUT_REG, 1)[0]
            result.append(reg_val >> 8 * (MIXEepromEmulateSGDef.MAX_DATA_WIDTH - self.data_width))
            reg_addr += 1
        return result

    def register_write(self, reg_addr, wr_data):
        '''
        Write data to eeprom emulator.

        Args:
            reg_addr:   int, register address.
            wr_data:    list, data to be write. One data width is decided by config function.
        '''
        assert reg_addr >= 0
        assert reg_addr <= MIXEepromEmulateSGDef.MAX_REG_ADDR

        for data in wr_data:
            self.axi4_bus.write_32bit_inc(MIXEepromEmulateSGDef.I2C_S_RAM_DIN_REG,
                                          [data << 8 * (MIXEepromEmulateSGDef.MAX_DATA_WIDTH - self.data_width)])
            self.axi4_bus.write_16bit_inc(MIXEepromEmulateSGDef.I2C_S_RAM_ADDR_REG, [reg_addr])
            self.axi4_bus.write_8bit_inc(MIXEepromEmulateSGDef.I2C_S_RAM_WR_REG, [MIXEepromEmulateSGDef.WRITE_ENABLE])
            reg_addr += 1
