# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus


__author__ = 'yuanle@SmartGiant & wangguang@SmartGiant & gaocong@SmartGiant'
__version__ = '0.1'


class MIXI2SSGDef:

    TX_CACHE_DEPTH_REG = 0x0C
    RX_CACHE_DEPTH_REG = 0x0E
    MODULE_EN_REG = 0x10
    TRANSMIT_EN_REG = 0x11
    TX_FIFO_RESET_REG = 0x12
    RX_FIFO_RESET_REG = 0x13

    BCLK_DIVIDE_REG = 0X14
    LRCK_DIVIDE_REG = 0X15
    DATA_WIDTH_REG = 0X16
    I2S_CONFIG_REG = 0X17
    REG_SIZE = 8192

    MODULE_ENABLE = (1 << 0)
    TRANS_TX_ENABLE = (1 << 0)
    TRANS_RX_ENABLE = (1 << 1)

    TX_FIFO_RESET = 1
    RX_FIFO_RESET = 1
    TX_FIFO_DERESET = 0
    RX_FIFO_DERESET = 0

    MCLK = 98304000
    LRCK_DIVIDE = 32

    SAMPLING_EDGE_OFFSET = 4
    MODE_OFFSET = 5
    SUPPORT_SAMPLE_RATE = [48, 96, 192]
    MODE = ['master', 'slave']
    I2S_FORMAT_STANDARD = 1


class MIXI2SSGException(Exception):
    pass


class MIXI2SSG(object):

    '''
    MIX I2S SG IP driver

    This class provides function to config MIX_I2S_SG IP. This IP just support standard
    data format. sampling data in falling edge for tx mode, rising edge for rx mode.
    Before enable tx/rx mode, you must config I2S IP first.

    Args:
        axi4_bus: instance,     AXI4 lite bus instance or device path

    Examples:
        i2s = MIXI2SSG('/dev/MIX_I2S_SG_0')
        i2s.reset()
        # config I2S in TX mode with 48 kHz sampling rate, 24 bits data
        i2s.tx_enable(48, 24)
        # I2S data will be processed after tx enable
        # disable TX
        i2s.tx_disable()

        # config I2S in RX mode with 48 kHz sampling rate, 24 bits data and master mode
        i2s.rx_enable(48, 24)
        # I2S data will be processed after rx enable
        # disable RX
        i2s.rx_disable()
    '''

    rpc_public_api = ['rx_enable', 'tx_enable', 'config',
                      'rx_disable', 'tx_disable', 'reset']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # device path passed in; create axi4litebus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXI2SSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self._open()

    def __del__(self):
        self._close()

    def _open(self):
        '''
        Enable MIX I2S SG IP and FIFO. This is a private function.
        '''
        # enable IP
        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.MODULE_EN_REG, 1)[0]
        reg_value |= MIXI2SSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.MODULE_EN_REG, [reg_value])
        return "done"

    def _close(self):
        '''
        Disable MIX I2S SG IP and FIFO. This is a private function.
        '''
        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.MODULE_EN_REG, 1)[0]
        reg_value &= ~MIXI2SSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.MODULE_EN_REG, [reg_value])

        return "done"

    def reset(self):
        '''
        Reset MIX_I2S_SG IP core.
        '''
        self._close()
        self._open()
        return "done"

    def tx_enable(self):
        '''
        Enable TX transmition function.

        Returns:
            string, "done", if execute success, return "done"
        '''
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TX_FIFO_RESET_REG,
                                     [MIXI2SSGDef.TX_FIFO_DERESET])

        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, 1)[0]
        reg_value |= MIXI2SSGDef.TRANS_TX_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, [reg_value])

        return "done"

    def tx_disable(self):
        '''
        Disable TX transmition function.

        Returns:
            string, "done", if execute success, return "done"
        '''
        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, 1)[0]
        reg_value &= ~MIXI2SSGDef.TRANS_TX_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, [reg_value])

        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TX_FIFO_RESET_REG,
                                     [MIXI2SSGDef.TX_FIFO_RESET])
        return "done"

    def rx_enable(self):
        '''
        Enable RX transmition function.

        Returns:
            string, "done", if execute success, return "done"
        '''
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.RX_FIFO_RESET_REG,
                                     [MIXI2SSGDef.RX_FIFO_DERESET])

        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, 1)[0]
        reg_value |= MIXI2SSGDef.TRANS_RX_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, [reg_value])
        return "done"

    def rx_disable(self):
        '''
        Disable RX transmition function

        Returns:
            string, "done", if execute success, return "done"
        '''
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.RX_FIFO_RESET_REG,
                                     [MIXI2SSGDef.RX_FIFO_RESET])

        reg_value = self.axi4_bus.read_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, 1)[0]
        reg_value &= ~MIXI2SSGDef.TRANS_RX_ENABLE
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.TRANSMIT_EN_REG, [reg_value])
        return "done"

    def config(self, sampling_rate, data_width, mode):
        '''
        Config MIX I2S SG IP

        Args:
            sampling_rate:       int, [48, 96, 192], sampling rate in kHz
            data_width:          int, [1~24], data width
            mode:                string, ['master', 'slave'], master/slave mode.
        Returns:
            string, "done", if execute successfully, return "done".
        '''
        assert sampling_rate in MIXI2SSGDef.SUPPORT_SAMPLE_RATE
        assert data_width in [i + 1 for i in range(24)]
        assert mode in ['master', 'slave']

        bclk = sampling_rate * 1000 * 2 * MIXI2SSGDef.LRCK_DIVIDE
        bclk_div = int(MIXI2SSGDef.MCLK / bclk / 2)
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.BCLK_DIVIDE_REG, [bclk_div & 0xFF])
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.DATA_WIDTH_REG, [data_width])
        reg_value = MIXI2SSGDef.I2S_FORMAT_STANDARD
        reg_value |= (MIXI2SSGDef.MODE.index(mode) << MIXI2SSGDef.MODE_OFFSET)
        self.axi4_bus.write_8bit_inc(MIXI2SSGDef.I2S_CONFIG_REG, [reg_value])
        return "done"
