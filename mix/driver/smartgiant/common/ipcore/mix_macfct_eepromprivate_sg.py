# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_def import AXI4Def
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'Zhangsong Deng'
__version__ = '0.1'


class MIXMacFCTEepromPrivateSGDef:
    MODULE_EN_REGISTER = 0x10
    ADDR_REGISTER = 0x30
    CONFIG_REGISTER = 0x31
    FREQ_REGISTER = 0x32
    DIN_REGISTER = 0x34
    RAM_REGISTER = 0x38
    RAM_WR_REGISTER = 0x3A
    DOUT_REGISTER = 0x3C

    RESET_CMD = 0x00
    ENABLE_CMD = 0x01

    REG_SIZE = 256
    DEFAULT_RATE = 400000
    DEFAULT_MAX_RATE = 2000000
    SYS_CLK_INTERVAL_NS = 8

    SALVE_ADDR_MASK = 0x7F
    MIN_REG_BYTE = 1
    # desided by 0x38 register's length, length is 2 byte
    MAX_REG_BYTE = 2
    MIN_DATA_BYTE = 1
    # desided by RAM DIN/DOUT byte length, length is 4 byte
    MAX_DATA_BYTE = 4

    DEFAULT_REG_LEN = 1    # byte
    DEFAULT_DATA_LEN = 1    # byte
    DEFAULT_SLAVE_ADDR = 0x48
    MAX_REG_ADDR = 0xFFFF


class MIXMacFCTEepromPrivateSG(object):
    """
    MIXMacFCTEepromPrivateSG function

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string,   for i2c slave module config register
        slave_addr:  int,                config the i2c slave module's address

    Examples:
        axi4_bus = AXI4LiteBus("/dev/MIX_MacFCT_EepromPrivate_SG_0", 256)
        i2c_slave = MIXMacFCTEepromPrivateSG(axi4_bus, 0x48)
        i2c_slave.enable()
        i2c_slave.register_write(0x02, [0x89])
        reg_val = i2c_slave.register_read(0x02)
    """
    rpc_public_api = ['config']

    def __init__(self, axi4_bus, device_addr=MIXMacFCTEepromPrivateSGDef.DEFAULT_SLAVE_ADDR):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXMacFCTEepromPrivateSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.config(MIXMacFCTEepromPrivateSGDef.DEFAULT_RATE, device_addr, MIXMacFCTEepromPrivateSGDef.DEFAULT_REG_LEN,
                    MIXMacFCTEepromPrivateSGDef.DEFAULT_DATA_LEN)

    def _disable(self):
        """
        Disable MIXMacFCTEepromPrivateSG module

        Examples:
            i2c_slave._disable()
        """
        self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.MODULE_EN_REGISTER,
                                     [MIXMacFCTEepromPrivateSGDef.RESET_CMD])

    def _enable(self):
        """
        Enable MIXMacFCTEepromPrivateSG module. this function should be called before start to use this module

        Examples:
            i2c_slave._enable()
        """
        self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.MODULE_EN_REGISTER,
                                     [MIXMacFCTEepromPrivateSGDef.RESET_CMD])
        self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.MODULE_EN_REGISTER,
                                     [MIXMacFCTEepromPrivateSGDef.ENABLE_CMD])

    def config(self, speed_hz, device_addr, reg_len, data_len):
        """
        MIXMacFCTEepromPrivateSG module config function.

        Args:
            speed_hz:    int,[1~2000000]  unit Hz, config i2c slave's clk frequency
            device_addr: hex,[0x00~0x7F], config i2c slave address
            reg_len:     int,[1~15],      set i2c slave module device address
            data_len:    int,[1~4],       set the number of bytes in the register value

        Examples:
            i2c_slave.config(100000, 0x40, 1, 1)
        """
        assert isinstance(speed_hz, int)
        assert speed_hz > 0
        assert speed_hz <= MIXMacFCTEepromPrivateSGDef.DEFAULT_MAX_RATE
        assert isinstance(device_addr, int)
        assert device_addr >= 0
        assert device_addr <= MIXMacFCTEepromPrivateSGDef.SALVE_ADDR_MASK

        assert isinstance(reg_len, int)
        assert isinstance(data_len, int)
        assert reg_len >= MIXMacFCTEepromPrivateSGDef.MIN_REG_BYTE
        assert reg_len <= MIXMacFCTEepromPrivateSGDef.MAX_REG_BYTE
        assert data_len >= MIXMacFCTEepromPrivateSGDef.MIN_DATA_BYTE
        assert data_len <= MIXMacFCTEepromPrivateSGDef.MAX_DATA_BYTE

        self._data_width = data_len

        bit_clk_cnt = AXI4Def.AXI4_CLOCK / speed_hz
        # 8 ns ref by sys clk
        bit_clk_delay = bit_clk_cnt // MIXMacFCTEepromPrivateSGDef.SYS_CLK_INTERVAL_NS
        self._disable()
        self.axi4_bus.write_16bit_inc(MIXMacFCTEepromPrivateSGDef.FREQ_REGISTER, [bit_clk_delay])
        self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.ADDR_REGISTER, [device_addr])
        # config register combined with data length bit[3:0] & register length bit[7:4]
        self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.CONFIG_REGISTER, [(reg_len << 4) | data_len])
        self._enable()

    def get_slave_addr(self):
        """
        MIXMacFCTEepromPrivateSG module get address function

        Returns:
            int,    value of slave address which configed by user

        Examples:
            i2c_slave.get_slave_addr()
        """
        return self.axi4_bus.read_8bit_inc(MIXMacFCTEepromPrivateSGDef.ADDR_REGISTER, 1)[0]

    def get_speed(self):
        """
        MIXMacFCTEepromPrivateSG module get frequency configuration function

        Returns:
            int, value, unit Hz.    value which user configed, the value read back is not necessarily equal to
                                    the configured value due to the conversion

        Examples:
            i2c_slave.get_speed()
        """
        freq_reg_val = self.axi4_bus.read_16bit_inc(MIXMacFCTEepromPrivateSGDef.FREQ_REGISTER, 1)[0]
        return int(AXI4Def.AXI4_CLOCK / (freq_reg_val * MIXMacFCTEepromPrivateSGDef.SYS_CLK_INTERVAL_NS))

    def get_reg_len(self):
        """
        MIXMacFCTEepromPrivateSG module get register data byte length

        Returns:
            int,[1~2],   n byte(s) of data register length

        Examples:
            reg_len = i2c_slave.get_reg_len()
            print reg_len
        """
        con_reg_val = self.axi4_bus.read_8bit_inc(MIXMacFCTEepromPrivateSGDef.CONFIG_REGISTER, 1)[0]
        # register byte length config by register's bit[7:4]
        return (con_reg_val >> 4) & 0xF

    def get_date_len(self):
        """
        MIXMacFCTEepromPrivateSG module get data length

        Returns:
            int,[1~4],   n byte(s) of data length

        Examples:
            data_len = i2c_slave.get_date_len()
            print data_len
        """
        con_reg_val = self.axi4_bus.read_8bit_inc(MIXMacFCTEepromPrivateSGDef.CONFIG_REGISTER, 1)[0]
        # register byte length config by register's bit[3:0]
        return con_reg_val & 0xF

    def register_read(self, reg_addr, rd_len):
        """
        MIXMacFCTEepromPrivateSG module read register function

        Args:
            reg_addr:    hex,[0~0xFFFF], read register address
            rd_len:      int,            read data's length, begin from reg_addr

        Returns:
            list,   list of read data, data's length is related to data byte length's configure

        Examples:
            i2c_slave.enable()
            i2c_slave.register_read(0x00, 2)
        """
        assert reg_addr >= 0
        assert reg_addr <= MIXMacFCTEepromPrivateSGDef.MAX_REG_ADDR

        read_data_list = []
        for i in range(rd_len):
            self.axi4_bus.write_16bit_inc(MIXMacFCTEepromPrivateSGDef.RAM_REGISTER, [reg_addr])
            dout_val = self.axi4_bus.read_32bit_inc(MIXMacFCTEepromPrivateSGDef.DOUT_REGISTER, 1)[0]
            # calculate data by data byte length config with 8bits(1 byte)
            read_data_list.append(dout_val >> 8 * (MIXMacFCTEepromPrivateSGDef.MAX_DATA_BYTE - self._data_width))
            reg_addr += 1

        return read_data_list

    def register_write(self, reg_addr, data_list):
        """
        MIXMacFCTEepromPrivateSG module's set register value function

        Args:
            reg_addr:    hex,[0~0xFFFF], write register address
            data_list:   list,           write data list, unit size is 1 byte

        Examples:
            i2c_slave.enable()
            i2c_slave.register_write(0x02, [0x01, 0x02])
        """
        assert reg_addr >= 0
        assert reg_addr <= MIXMacFCTEepromPrivateSGDef.MAX_REG_ADDR

        for data in data_list:
            # calculate data by data byte length config with 8bits(1 byte)
            self.axi4_bus.write_32bit_inc(MIXMacFCTEepromPrivateSGDef.DIN_REGISTER,
                                          [data << 8 * (MIXMacFCTEepromPrivateSGDef.MAX_DATA_BYTE - self._data_width)])
            self.axi4_bus.write_16bit_inc(MIXMacFCTEepromPrivateSGDef.RAM_REGISTER, [reg_addr])
            self.axi4_bus.write_8bit_inc(MIXMacFCTEepromPrivateSGDef.RAM_WR_REGISTER,
                                         [MIXMacFCTEepromPrivateSGDef.ENABLE_CMD])
            reg_addr += 1
