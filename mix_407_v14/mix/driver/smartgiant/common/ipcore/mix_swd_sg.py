# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.utility.data_operate import DataOperate
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator

__author__ = 'jihua.jiang@SmartGiant'
__version__ = '0.1'


class MIXSWDSGDef:
    REG_SIZE = 8192
    VERSION_REG = 0x00
    BASE_CLK_FREQ_REG = 0x01
    SWD_CLK_DIV_REG = 0x04
    MODULE_EN_REG = 0x10
    SWD_START_REG = 0x11
    SWD_CTRL_REG = 0x12
    SWD_STATE_REG = 0x14
    SWD_REQ_DATA = 0x23
    SWD_WDATA_REG = 0x24
    SWD_RDATA_REG = 0x28
    SWD_ACK_DATA_REG = 0x2c
    SWITCH_FIFO_REG = 0x30
    REQ_START_OFFSET = 0
    REQ_APNDP_OFFSET = 1
    REQ_RNW_OFFSET = 2
    REQ_ADDR_OFFSET = 3
    REQ_PARITY_OFFSET = 5

    REQ_APNDP = ['DP', 'AP']
    REQ_RNW_READ = 0x01
    # swd clock range
    SPEED_MIN = 2000
    SPEED_MAX = 12500000
    # swd communicate timeout
    TIMEOUT_S = 1.0
    BUSY = 0x00
    DELAY_S = 0.001
    # swd ACK data
    ACK_VALID_DATA = 0x07
    # swd ACK value
    ACK_OK = 0x01
    ACK_WAIT = 0x02
    ACK_ERROR = 0x04
    START_TRANSMIT = 0x01
    DEVICE_ENABLE = 0X01
    DEVICE_DISABLE = 0xFE
    RST_ENABLE = 0x7F
    RST_DISABLE = 0x80
    TRANSMIT_ENABLE = 0x01
    SWITCH_SEQUENCE = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x9E,
                       0xE7, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
                       0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00]


class MIXSWDSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = "MIXSWDSG {}".format(err_str)

    def __str__(self):
        return self.err_reason


class MIXSWDSG(object):
    '''
    MIXSWDSG function class

    which provide bus clock setting, rst pin control,
    switch swquence setting, and register read or write function.

    ClassType = SWD

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or device path of AXI4LiteBus.

    Examples:
        swd = MIXSWDSG('/dev/MIX_SWD_0')

    '''

    rpc_public_api = ['set_speed', 'set_rst_high', 'set_rst_low', 'reset',
                      'switch_sequence', 'write', 'read', 'dp_write',
                      'dp_read', 'ap_write', 'ap_read']

    def __init__(self, axi4_bus=None):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator('axi4_bus_emulator', MIXSWDSGDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXSWDSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
        enable swd device, device must be enable and that can communicate.

        Examples:
            swd._enable()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.MODULE_EN_REG, 1)
        # set the bit1 to enable the device.
        rd_data[0] = rd_data[0] | MIXSWDSGDef.DEVICE_ENABLE

        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.MODULE_EN_REG, rd_data)

    def _disable(self):
        '''
        disable swd device.

        Examples:
            swd._disable()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.MODULE_EN_REG, 1)
        # reset the bit1 to disable the device.
        rd_data[0] = rd_data[0] & MIXSWDSGDef.DEVICE_DISABLE

        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.MODULE_EN_REG, rd_data)

    def set_speed(self, speed):
        '''
        set the clock speed.

        Args:
            speed:    int, [2000~12500000], unit Hz, swd transmit speed.

        Examples:
            # set swd clock speed as 500KHz
            swd.set_speed(500000)

        '''
        assert MIXSWDSGDef.SPEED_MIN <= speed
        assert speed <= MIXSWDSGDef.SPEED_MAX

        # the BASE_CLK_FREQ register is 24 bit width.
        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.BASE_CLK_FREQ_REG, 3)
        # KHz to Hz.
        base_clk_freq = DataOperate.list_2_int(rd_data) * 1000
        # calculate the frequency division
        swd_freq_div = int(((base_clk_freq) / (speed * 2)) - 2)

        if swd_freq_div < 0:
            swd_freq_div = 0

        self.axi4_bus.write_16bit_fix(MIXSWDSGDef.SWD_CLK_DIV_REG, [swd_freq_div])
        return "done"

    def set_rst_high(self):
        '''
        set the reset pin as high level.

        Examples:
            # set reset pin as high level
            swd.set_rst_high()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, 1)
        # set the bit8 as 0 to enable the rst pin as high level.
        rd_data[0] = rd_data[0] & MIXSWDSGDef.RST_ENABLE

        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, rd_data)
        return "done"

    def set_rst_low(self):
        '''
        set the reset pin as low level.

        Examples:
            # set reset pin as low level
            swd.reset_rst()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, 1)
        # set the bit8 as 1 to enable the rst pin as low level.
        rd_data[0] = rd_data[0] | MIXSWDSGDef.RST_DISABLE

        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, rd_data)
        return "done"

    def reset(self, delay_s):
        '''
        reset swd slave device.

        This function will set rst pin to low and then set rst pin to high.

        Args:
            delay_s:   float, delay seconds between rst pin low
                                       level to high level.
        '''
        self.set_rst_low()
        time.sleep(delay_s)
        self.set_rst_high()
        return "done"

    def switch_sequence(self, timing_data=MIXSWDSGDef.SWITCH_SEQUENCE):
        '''
        set the swd switch sequence for enter the swd debug mode.

        Args:
            timing_data:    list, 8 bit hex element, swd switch sequence data,
                            default timing_data is base on STM's series chips.

        Raises:
            MIXSWDSGException: transmit time out.

        Examples:
            # switch sequence enter swd debug mode.
            swd.switch_sequence()

        '''
        self.axi4_bus.write_8bit_fix(MIXSWDSGDef.SWITCH_FIFO_REG, timing_data)

        rd_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, 1)
        # set the bit1 enable swd communicate
        rd_data[0] = rd_data[0] | MIXSWDSGDef.TRANSMIT_ENABLE

        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_CTRL_REG, rd_data)

        self._wait_busy()
        return "done"

    def write(self, req_data, data):
        '''
        write data to communicate with chip.

        Args:
            req_data:   int, the request data.
            data:       int, 32 bit hex data, the data to write.

        Raises:
            MIXSWDSGException: transmit time out.

        Examples:
            # write data.
            swd.write(0x21,0x12345678)
        '''
        assert isinstance(data, int)

        # write request data
        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_REQ_DATA, [req_data])
        # write data
        self.axi4_bus.write_32bit_fix(MIXSWDSGDef.SWD_WDATA_REG, [data])
        # start transmit
        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_START_REG, [MIXSWDSGDef.START_TRANSMIT])

        self._wait_busy()

        # check the ACK data
        self._check_ack(self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_ACK_DATA_REG, 1)[0])
        return "done"

    def read(self, req_data):
        '''
        read data to communicate with chip.

        Args:
            req_data:   int, the request data.

        Raises:
            MIXSWDSGException: transmit time out.

        Returns:
            int, value, 32 bit hex data of read.

        Examples:
            # read data.
            swd.read(0x21)

        '''
        # write request data
        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_REQ_DATA, [req_data])
        # start transmit
        self.axi4_bus.write_8bit_inc(MIXSWDSGDef.SWD_START_REG, [MIXSWDSGDef.START_TRANSMIT])

        self._wait_busy()

        rd_data = self.axi4_bus.read_32bit_fix(MIXSWDSGDef.SWD_RDATA_REG, 1)[0]

        ack_data = self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_ACK_DATA_REG, 1)[0]

        self._check_ack(ack_data)

        return rd_data

    def _check_ack(self, ack):
        '''
        SWD check ack value. If some error occurs, MIXSWDSGException will be raised.

        Args:
            ack:   int,        ACK value.

        '''
        ack_data = ack & MIXSWDSGDef.ACK_VALID_DATA
        if ack_data == MIXSWDSGDef.ACK_OK:
            return
        elif ack_data == MIXSWDSGDef.ACK_WAIT:
            raise MIXSWDSGException("ack wait")
        elif ack_data == MIXSWDSGDef.ACK_ERROR:
            raise MIXSWDSGException("ack error")
        else:
            raise MIXSWDSGException("no ack")

    def _wait_busy(self):
        '''
        Wait swd comminucattion ready.
        '''
        start = time.time()

        while (time.time() < (start + MIXSWDSGDef.TIMEOUT_S)):
            if MIXSWDSGDef.BUSY != self.axi4_bus.read_8bit_inc(MIXSWDSGDef.SWD_STATE_REG, 1)[0]:
                return
            time.sleep(MIXSWDSGDef.DELAY_S)

        raise MIXSWDSGException("communicate timeout")

    def _calculate_req_parity(self, data):
        assert data >= 0 and data <= 0xFF
        data ^= (data >> 4)
        data ^= (data >> 2)
        data ^= (data >> 1)
        data &= 0x01
        return data

    def _dap_write(self, port, addr, data):
        '''
        Write data to DP/AP port

        Args:
            port:            string, ['DP', 'AP'],   indicate the data write to 'DP' or 'AP' register.
            addr:            int, [0~3],             regsiter address.
            data:            int,                    data to be write.

        '''
        assert addr >= 0 and addr <= 0x03
        assert port in MIXSWDSGDef.REQ_APNDP
        assert data >= 0 and data <= 0xFFFFFFFF
        request_data = (addr & 0x03) << MIXSWDSGDef.REQ_ADDR_OFFSET
        request_data |= MIXSWDSGDef.REQ_APNDP.index(port) << MIXSWDSGDef.REQ_APNDP_OFFSET
        # just calculate bit1~bit4 parity
        parity = self._calculate_req_parity(request_data)
        request_data |= parity << MIXSWDSGDef.REQ_PARITY_OFFSET
        # bit0: start, must be 1
        # bit7: park, must be 1
        request_data |= 0x81
        self.write(request_data, data)

    def _dap_read(self, port, addr):
        '''
        Read data from DP/AP register

        Args:
            port:            string, ['DP', 'AP'],   indicate the data write to 'DP' or 'AP' register.
            addr:            int, [0~3],             regsiter address

        Returns:
            int, value, data has been read.

        '''
        assert addr >= 0 and addr <= 0x03
        assert port in MIXSWDSGDef.REQ_APNDP
        request_data = (addr & 0x03) << MIXSWDSGDef.REQ_ADDR_OFFSET
        request_data |= MIXSWDSGDef.REQ_APNDP.index(port) << MIXSWDSGDef.REQ_APNDP_OFFSET
        request_data |= MIXSWDSGDef.REQ_RNW_READ << MIXSWDSGDef.REQ_RNW_OFFSET
        # just calculate bt1-bit4 parity
        parity = self._calculate_req_parity(request_data)
        request_data |= parity << MIXSWDSGDef.REQ_PARITY_OFFSET
        # bit0: start, must be 1
        # bit7: park, must be 1
        request_data |= 0x81
        return self.read(request_data)

    def dp_write(self, addr, data):
        '''
        Write data to DP register

        Args:
            addr:     int, [0~3],           DP register address.
            data:     int, [0~0xFFFFFFFF],  Data to be write to DP register.

        '''
        self._dap_write('DP', addr, data)
        return "done"

    def dp_read(self, addr):
        '''
        Read data from DP register

        Args:
            addr:    int, [0~3],           DP register address.

        Returns:
            int, value, data has been read.

        '''
        return self._dap_read('DP', addr)

    def ap_write(self, addr, data):
        '''
        Write data to AP register

        Args:
            addr:     int, [0~3],            AP register address.
            data:     int, [0~0xFFFFFFFF],   Data to be write to AP register.

        '''
        self._dap_write('AP', addr, data)
        return "done"

    def ap_read(self, addr):
        '''
        Read data from AP register

        Args:
            addr:     int, [0~3],     AP register address.

        Returns:
            int, value, data has been read.

        '''
        return self._dap_read('AP', addr)
