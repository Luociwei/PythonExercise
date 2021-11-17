# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_def import AXI4Def
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate


__author__ = 'huanghanyong@SmartGiant'
__version__ = '1.0'


class MIXQSPISGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXQSPISG(object):
    '''
    Singleton wrapper of MIXQSPISG

    This is to ensure only 1 instance will be created for the same
    char device in /dev, even when instantiated multiple times.
    It is to solve problem when profile define multiple instance
    for the same /dev/MIX_QSPI_x.

    Args:
        axi4_bus:   instance(AXI4LiteBus),      class instance of axi4 bus

    Examples:
        spi = MIXQSPISG('/dev/MIX_QSPI_0')

    '''
    instances = {}

    def __new__(cls, axi4_bus):
        if axi4_bus in cls.instances:
            return cls.instances[axi4_bus]
        else:
            instance = _MIXQSPISG(axi4_bus)
            cls.instances[axi4_bus] = instance
        return instance


class _MIXQSPISG(object):
    '''
    The MIXQSPISG class provides an interface to the MIX QSPI IPcore. This class supports SPI and QPI mode.

    ClassType = SPI

    Args:
        axi4_bus:   instance(AXI4LiteBus)/None, Class instance of axi4 bus, if not using this parameter,
                                                will create emulator

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
        spi = MIXQSPISG(axi4_bus)

    '''
    rpc_public_api = ['set_timeout', 'set_work_mode', 'get_work_mode', 'set_mode',
                      'get_mode', 'set_speed', 'get_speed', 'read', 'write', 'sync_transfer',
                      'async_transfer', 'transfer']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self._axi4_bus = AXI4LiteBus(axi4_bus, PLSPIDef.REG_SIZE)
        else:
            self._axi4_bus = axi4_bus
        self._dev_name = self._axi4_bus._dev_name
        self.__data_deal = DataOperate()
        self._timeout = AXI4Def.AXI4_TIMEOUT
        self._spi_speed = PLSPIDef.DEFAULT_SPEED
        self._spi_work_mode = PLSPIDef.SPI_MODE
        self.open()

    def __del__(self):
        self.close()

    def _wait_for_ready(self):
        '''
        Waiting for ipcore status to be ready or timeout

        Returns:
            boolean, [True, False], True is ready,Fasle is timeout.

        '''
        ret = 0
        start = time.time()
        while (time.time() < (start + self._timeout)):
            ret = self._axi4_bus.read_8bit_inc(PLSPIDef.STATE_REGISTER, PLSPIDef.STATE_READY)[0]
            if ret == PLSPIDef.SPI_READY:
                return True
            time.sleep(PLSPIDef.DELAY_TIME)
        return False

    def _clear_fifo(self):
        '''
        Clear fifo data.
        '''
        self._axi4_bus.write_8bit_inc(PLSPIDef.FIFO_CLR_REGISTER, [PLSPIDef.CLEAR_FIFO])

    def _assembly_data(self, wr_data):
        '''
        4-byte alignment operation, combining a 1-byte list of each element into a 4-byte list for each element

        Args:
            wr_data:    list, 1-byte list of each element.

        Returns:
            list, [value], 4-byte list of each element.

        '''
        assert isinstance(wr_data, list)

        data = []
        offset = 0
        wr_len = len(wr_data)

        if 0 <= wr_len < 4:
            data.append(self.__data_deal.list_2_int(wr_data[offset:]))
            return data

        for i in range(0, (wr_len / PLSPIDef.BYTE_ALIGNMENT_LENGTH + 1)):
            if wr_len - offset >= PLSPIDef.BYTE_ALIGNMENT_LENGTH:
                data.append(self.__data_deal.list_2_int(wr_data[offset:offset + PLSPIDef.BYTE_ALIGNMENT_LENGTH]))
                offset += PLSPIDef.BYTE_ALIGNMENT_LENGTH
            elif wr_len - offset > 0:
                data.append(self.__data_deal.list_2_int(wr_data[offset:]))
        return data

    def _read_fifo(self, rd_len):
        '''
        Read data from receiving fifo

        Args:
            rd_len:    int, Length of read data.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        '''
        assert isinstance(rd_len, int)
        assert (rd_len > 0)

        rd_cnt = rd_len / PLSPIDef.BYTE_ALIGNMENT_LENGTH
        rd_remain = rd_len % PLSPIDef.BYTE_ALIGNMENT_LENGTH

        rd_data = []
        if rd_cnt:
            datas = self._axi4_bus.read_32bit_fix(PLSPIDef.WDATA_REGISTER, rd_cnt)
            for _data in datas:
                rd_data += DataOperate.int_2_list(_data, PLSPIDef.INT_TO_LIST_LEN_4)

        if rd_remain:
            rd_data += self._axi4_bus.read_8bit_inc(PLSPIDef.WDATA_REGISTER, rd_remain)

        return rd_data

    def _write_fifo(self, wr_data):
        '''
        Write data to transfer fifo

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.

        '''
        wr_len = len(wr_data)
        wr_data = self._assembly_data(wr_data)
        # 'wr_len - 1': SPI operation byte length. SPI_BYTE_LEN = Actual byte length - 1
        data = self.__data_deal.int_2_list(wr_len - 1, PLSPIDef.INT_TO_LIST_LEN_2)
        self._axi4_bus.write_8bit_inc(PLSPIDef.BYTE_LEN_REGISTER, data)
        self._axi4_bus.write_8bit_inc(PLSPIDef.TRANSMIT_START_REGISTER, [PLSPIDef.TRANSMIT_ENABLE])
        self._axi4_bus.write_32bit_fix(PLSPIDef.WDATA_REGISTER, wr_data)
        if not self._wait_for_ready():
            raise MIXQSPISGException(self._axi4_bus._dev_name, "timeout")

    def _only_read(self, rd_len):
        '''
        Read rd_len bytes data from the spi bus

        Args:
            rd_len:    int, Length of read data.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        '''
        assert isinstance(rd_len, int)
        assert rd_len > 0

        data = []
        reg_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONTROL_REGISTER, PLSPIDef.CONTROL_REGISTER_LEN)[0]
        reg_data &= ~PLSPIDef.WRITE_ENABLE
        reg_data |= PLSPIDef.READ_ENABLE
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONTROL_REGISTER, [reg_data])

        while(rd_len > 0):
            if PLSPIDef.MAX_FIFO_LEN <= rd_len:
                byte_len = PLSPIDef.MAX_FIFO_LEN
                rd_len -= PLSPIDef.MAX_FIFO_LEN
            else:
                byte_len = rd_len
                rd_len = 0

            self._axi4_bus.write_16bit_inc(PLSPIDef.BYTE_LEN_REGISTER, [byte_len - 1])
            self._axi4_bus.write_8bit_inc(PLSPIDef.TRANSMIT_START_REGISTER, [PLSPIDef.TRANSMIT_ENABLE])
            if not self._wait_for_ready():
                raise MIXQSPISGException(self._axi4_bus._dev_name, "timeout")
            data += self._read_fifo(byte_len)
            self._clear_fifo()
        return data

    def _only_write(self, wr_data):
        '''
        Write data to spi bus

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.

        '''
        assert isinstance(wr_data, list)

        offset = 0
        data_len = len(wr_data)
        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONTROL_REGISTER, PLSPIDef.CONTROL_REGISTER_LEN)[0]
        rd_data |= PLSPIDef.WRITE_ENABLE
        rd_data &= ~PLSPIDef.READ_ENABLE
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONTROL_REGISTER, [rd_data])

        while(data_len > 0):
            if data_len >= PLSPIDef.MAX_FIFO_LEN:
                data_len -= PLSPIDef.MAX_FIFO_LEN
            else:
                data_len = 0
            data = wr_data[offset:(offset + PLSPIDef.MAX_FIFO_LEN)]
            self._write_fifo(data)
            self._clear_fifo()
            offset += PLSPIDef.MAX_FIFO_LEN

    def open(self):
        '''
        Open the spi device, initialize the clock rate and the working mode

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.open()

        '''
        rd_conf_val = self._axi4_bus.read_8bit_inc(PLSPIDef.CONFIG_REGISTER, PLSPIDef.CONFIG_REGISTER_LEN)[0]
        config_data = rd_conf_val | PLSPIDef.MODULE_ENABLE
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONFIG_REGISTER, [config_data])

        self.set_speed(self._spi_speed)
        self.set_work_mode(self._spi_work_mode)

    def close(self):
        '''
        Close the spi device

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.close()

        '''
        if not hasattr(self, '_axi4_bus'):
            return
        rd_conf_val = self._axi4_bus.read_8bit_inc(PLSPIDef.CONFIG_REGISTER, PLSPIDef.CONFIG_REGISTER_LEN)[0]
        config_data = rd_conf_val & ~PLSPIDef.MODULE_ENABLE
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONFIG_REGISTER, [config_data])

    def set_timeout(self, timeout):
        '''
        Set the timeout for waiting for the ipcore state to be ready

        Args:
            timeout:    float, unit s.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            # set 0.1s timeout for polling the ipcore status register
            spi.set_timeout(0.1)

        '''
        assert isinstance(timeout, float)
        assert timeout >= 0

        self._timeout = timeout

    def set_work_mode(self, quad_mode):
        '''
        Set the spi working mode. The MIX QSPI_SG IPcore supports SPI / QPI mode

        Args:
            quad_mode:    int, [0, 1], 0: SPI mode, 1: QPI mode.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            # set the spi working mode to SPI mode.
            spi.set_work_mode(PLSPIDef.SPI_MODE)

        '''
        assert quad_mode in [PLSPIDef.SPI_MODE, PLSPIDef.QPI_MODE]

        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONTROL_REGISTER, PLSPIDef.CONTROL_REGISTER_LEN)[0]
        rd_data &= PLSPIDef.SPI_MODE_CLEAR
        rd_data |= quad_mode
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONTROL_REGISTER, [rd_data])
        self._spi_work_mode = quad_mode

    def get_work_mode(self):
        '''
        Get spi working mode

        Returns:
            int, [0, 1], 0: SPI mode, 1: QPI mode.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            ret = spi.set_work_mode()   # ret == 0

        '''
        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONTROL_REGISTER, PLSPIDef.CONTROL_REGISTER_LEN)[0]
        return rd_data & PLSPIDef.SPI_MODE_BIT

    def set_mode(self, mode):
        '''
        Set the spi bus clock polarity and phase mode

        Args:
            mode:   string, ['MODE0', 'MODE1', 'MODE2', 'MODE3'], set mode.
            +---------+---------+----------+
            | Mode    |   CPOL  |   CPHA   |
            +=========+=========+==========+
            |    0    |    0    |     0    |
            +---------+---------+----------+
            |    1    |    0    |     1    |
            +---------+---------+----------+
            |    2    |    1    |     0    |
            +---------+---------+----------+
            |    3    |    1    |     1    |
            +---------+---------+----------+

        Examples:
            # set polarity to 0, phase to 0.
            spi.set_mode("MODE0")

        '''
        assert mode in PLSPIDef.SPI_MODES
        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONFIG_REGISTER, PLSPIDef.CONFIG_REGISTER_LEN)[0]

        # 'rd_data & PLSPIDef.SPI_MODE_MASK' is to clear bit4 and bit5,
        # '(mode & 0x03) << 4' is write bit4 and bit 5
        rd_data = (rd_data & PLSPIDef.SPI_MODE_MASK) | ((PLSPIDef.SPI_MODES[mode] & 0x03) << 4)
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONFIG_REGISTER, [rd_data])

    def get_mode(self):
        '''
        Get the spi bus clock polarity and phase mode

        Returns:
            string, ['MODE0', 'MODE1', 'MODE2', 'MODE3'], 'MODE0': CPOL=0, CPHA=0
                                                          'MODE1': CPOL=0, CPHA=1
                                                          'MODE2': CPOL=1, CPHA=0
                                                          'MODE3': CPOL=1, CPHA=1

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            ret = spi.get_mode()  # ret == "MODE0"

        '''
        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONFIG_REGISTER, PLSPIDef.CONFIG_REGISTER_LEN)[0]

        # get bit4 and bit 5
        config_data = (rd_data & ~PLSPIDef.SPI_MODE_MASK) >> 4
        for (key, value) in PLSPIDef.SPI_MODES.viewitems():
            if value == config_data:
                return key

    def get_base_clock(self):
        '''
        Get the ipcore base clock frequency

        Returns:
            int, value, unit kHz.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            ret = spi.get_base_clock()  # ret == 125000

        '''
        base_clk = self._axi4_bus.read_8bit_inc(PLSPIDef.BASE_CLOCK_FREQ_REGISTER, PLSPIDef.CLK_REGISTER_LEN)
        return self.__data_deal.list_2_int(base_clk)

    def set_speed(self, speed):
        '''
        Set the spi bus clock speed

        Args:
            speed:  int, [2~20000000], unit Hz, 1000000 means 1000000Hz.

        Examples:
            # set clock speed to 10MHz
            spi.set_speed(10000000)

        '''
        assert (speed >= PLSPIDef.MIN_SPEED)
        assert (speed <= PLSPIDef.MAX_SPEED)

        # get bace clocek frequency
        base_clk_freq = self.get_base_clock()

        # SPI_CLK_DIV = BASE_CLK_FREQ / (SPI_CLK_FREQ * 2) - 2
        freq_div = int(((base_clk_freq * PLSPIDef.KHZ) / (speed * 2)) - 2)
        if freq_div < 0:
            freq_div = 0
        wr_data = self.__data_deal.int_2_list(freq_div, PLSPIDef.INT_TO_LIST_LEN_2)
        self._axi4_bus.write_8bit_inc(PLSPIDef.FREQ_REGISTER, wr_data)
        self._spi_speed = speed

    def get_speed(self):
        '''
        Get the spi bus clock speed

        Returns:
            int, value, unit Hz.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            ret = spi.get_speed()   # ret == 10000000

        '''
        speed = self._axi4_bus.read_16bit_inc(PLSPIDef.FREQ_REGISTER, PLSPIDef.FREQ_REGISTER_LEN)[0]
        # get bace clocek frequency
        base_clk_freq = self.get_base_clock()

        # SPI_CLK_FREQ = BASE_CLK_FREQ / (SPEED + 2) * 2
        return (base_clk_freq * PLSPIDef.KHZ) / ((speed + 2) * 2)

    def set_cs(self, cs_mode):
        '''
        Set the chip select signal level

        Args:
            cs_mode:    int, [0, 1], 0: CS_LOW, 1: CS_HIGH.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            # set the chip select signal to low level.
            spi.set_cs(PLSPIDef.CS_LOW)

        '''
        assert cs_mode in [PLSPIDef.CS_LOW, PLSPIDef.CS_HIGH]

        self._axi4_bus.write_8bit_inc(PLSPIDef.CS_REGISTER, [cs_mode])

    def read(self, rd_len):
        '''
        Read data from spi bus. This function will control the chip select signal

        Args:
            rd_len:    int, (>0), Length of read data.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.read(100)

        '''
        assert isinstance(rd_len, int)
        assert rd_len > 0

        self.set_cs(PLSPIDef.CS_LOW)
        rd_data = self._only_read(rd_len)
        self.set_cs(PLSPIDef.CS_HIGH)
        return rd_data

    def write(self, wr_data):
        '''
        Write data to spi bus. This function will control the chip select signal

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.set_mode("MODE0")
            spi.write([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])

        '''
        assert isinstance(wr_data, list)

        self.set_cs(PLSPIDef.CS_LOW)
        self._only_write(wr_data)
        self.set_cs(PLSPIDef.CS_HIGH)

    def sync_transfer(self, wr_data):
        '''
        This function only supports standard spi mode

        Write data to the spi bus. At the same time, the same length of data is read

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.set_mode("MODE0")
            spi.set_work_mode("SPI")
            to_send = [0x01, 0x03, 0x04, 0x06]
            ret = spi.sync_transfer(to_send) # len(ret) == len(to_send)

        '''
        assert isinstance(wr_data, list)

        offset = 0
        read_data = []
        rd_len = len(wr_data)
        self.set_cs(PLSPIDef.CS_LOW)
        rd_data = self._axi4_bus.read_8bit_inc(PLSPIDef.CONTROL_REGISTER, PLSPIDef.CONTROL_REGISTER_LEN)[0]
        rd_data |= PLSPIDef.READ_WRITE_ENABLE
        self._axi4_bus.write_8bit_inc(PLSPIDef.CONTROL_REGISTER, [rd_data])

        while(rd_len > 0):
            if rd_len >= PLSPIDef.MAX_FIFO_LEN:
                byte_len = PLSPIDef.MAX_FIFO_LEN
                rd_len -= PLSPIDef.MAX_FIFO_LEN
            else:
                byte_len = rd_len
                rd_len = 0

            data = wr_data[offset:(offset + PLSPIDef.MAX_FIFO_LEN)]
            self._write_fifo(data)
            read_data += self._read_fifo(byte_len)
            offset += byte_len
            self._clear_fifo()
        self.set_cs(PLSPIDef.CS_HIGH)
        return read_data

    def async_transfer(self, wr_data, rd_len):
        '''
        This function supports SPI and QPI mode

        First write data to the spi bus, then read data from the spi bus

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.
            rd_len:     int, Length of read data.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.set_mode("MODE0")
            spi.set_work_mode("QPI")
            ret = spi.async_transfer([0x01,0x02,0x03,0x04], 3)   # len(ret) == 3

        '''
        assert isinstance(wr_data, list)
        assert rd_len > 0

        self.set_cs(PLSPIDef.CS_LOW)

        # write operation
        self._only_write(wr_data)

        # read operation
        read_data = self._only_read(rd_len)

        self.set_cs(PLSPIDef.CS_HIGH)
        return read_data

    def transfer(self, wr_data, rd_len, sync=True):
        '''
        This is the same as sync_transfer when sync is True, and the same as async_transfer when sync is False

        Args:
            wr_data:    list, Data to write, the list element is an integer, bit width: 8 bits.
            rd_len:     int, Length of read data.
            sync:       boolean, [True, False], True for write and read synchronizily,
                                                False for write then read from spi bus.

        Returns:
            list, [value], Data to be read, the list element is an integer, bit width: 8 bits.

        Examples:
            axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
            spi = PLSPIBus(axi4_bus)
            spi.set_mode("MODE0")
            spi.set_work_mode("QPI")
            # write [0x01,0x02,0x03] data to spi bus,then read 4 bytes from spi bus.
            ret = spi.transfer([0x01,0x02,0x03], 4, False)   # len(ret) == 4

        '''
        assert isinstance(wr_data, list)
        assert rd_len > 0
        assert sync in [True, False]

        if sync is True:
            return self.sync_transfer(wr_data)
        else:
            return self.async_transfer(wr_data, rd_len)
