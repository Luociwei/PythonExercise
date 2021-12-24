# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLUARTDef
from mix.driver.core.bus.axi4_lite_def import AXI4Def
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXUARTSG(object):
    '''
    Uart bus function class.

    ClassType = UART

    Args:
        axi4_bus:    instance(AXI4LiteBus)/None, If None, will create Emulator.
        baud_rate:   int, [0~1250000], default 115200, Baud rate of Uart bus, support normal baudrate:
                                                       9600, 115200 and up to 1.25M.
                                                       Baudrate higher than 1.25M is not verified.
        data_bits:   int, [5, 6, 7, 8], default 8, Data bits of Uart bus.
        parity:      string, ['none', 'odd', 'even'], default 'none', parity bit of Uart bus.
        stop_bits:   int, [1, 2], default 1, stop bit of Uart bus.
        timestamp:   boolean, [True, False], default False, whether uart output contains timestamp.
                                                            By default False to let read_hex() return
                                                            whatever come from uart bus.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_UART', 256)
        uart_bus = MIXUARTSG(axi4_bus)
        uart_bus.open()
        # do read and write:
        uart_bus.read_hex(0, 0.5)
        uart_bus.write_hex([0x20, 0xd])
        ...
        uart_bus.close()

    '''

    rpc_public_api = ['open', 'close', 'config', 'read_hex', 'write_hex']

    def __init__(self, axi4_bus=None, baud_rate=115200, data_bits=8,
                 parity='none', stop_bits=1, timestamp=False):

        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator("mix_uart_sg_emulator", PLUARTDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path; create axi4litebus instance here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, PLUARTDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.config(baud_rate, data_bits, parity, stop_bits, timestamp)

    def open(self):
        '''
        Uart open function; shall be called once before any uart read/write

        Returns:
            string, "done", api execution successful.

        Examples:
            uart_bus.open()

        '''
        self.axi4_bus.write_8bit_inc(PLUARTDef.CONFIG_REGISTER,
                                     [PLUARTDef.DISABLE_CMD])
        self.axi4_bus.write_8bit_inc(PLUARTDef.CONFIG_REGISTER,
                                     [PLUARTDef.ENABLE_CMD])

        self.axi4_bus.write_8bit_inc(PLUARTDef.CONFIG_ENABLE_REGISTER,
                                     [PLUARTDef.CONFIG_ENABLE_CMD])
        return 'done'

    def close(self):
        '''
        Uart close function; shall be called after uart operation is finished for dut

        Returns:
            string, "done", api execution successful.

        Examples:
            uart_bus.close()

        '''
        self.axi4_bus.write_8bit_inc(PLUARTDef.CONFIG_REGISTER,
                                     [PLUARTDef.DISABLE_CMD])
        return 'done'

    def config(self, baud_rate=115200, data_bits=8,
               parity='none', stop_bits=1, timestamp=False):
        '''
        Uart configuration function, use to config the Uart

        Args:
            baud_rate:    int, [0~2000000], default 115200, Baud rate of Uart bus, e.g.9600, 115200.
            data_bits:    int, [5, 6, 7, 8], default 8, Data bits of Uart bus.
            parity:       string, ['none', 'odd', 'even'], default 'none', parity bit of Uart bus.
            stop_bits:    int, [1, 2], default 1, stop bit of Uart bus
            timestamp:    boolean, [True, False], default False, timestamp of Uart bus.

        Returns:
            string, "done", api execution successful.

        Examples:
            uart_bus.config(115200, 8, 'none', 1, False)

        '''
        self._set_baudrate(baud_rate)
        self._set_databits(data_bits)
        self._set_stopbits(stop_bits)
        self._set_parity(parity)
        self._set_timestamp(timestamp)
        return 'done'

    def read_hex(self, rd_len=0, timeout_sec=0):
        '''
        Uart read specific rd_len data and return list of hex

        This api shall be used by station SW for uart read as it support any char

        Args:
            rd_len:         int, default 0, length of data to be read. if 0, all data cached will be read.
            timeout_sec:    float, default 0, block second time when can not get enough data.
                                              if timeout_sec==0, will block until get enough data
                                              Usually non-zero timeout_sec should be used to
                                              ensure the rpc will finish and not stuck in threadpool.
                                              This timeout_sec argument must be shorter than rpc timeout.

        Returns:
            list, [value],  each element takes one byte.

        Examples:
            # to read at most 18 bytes and wait no more than 0.5s:
            rd_data = uart_bus.read_hex(18, 0.5)
            rd_data == [58, 45, 41, 32]
            str_data = ''.join([chr(i) for i in rd_data])
            str_data == ':-) '

            # wait at most 1s ,return immediately if there is any data on uart:
            # this could be used at host side to reduce cpu utilization
            # when there is no data arrived on uart rx.
            rd_data = uart_bus.read(1, 1)
            # return value could be [] or list with 1 byte:
            #     [] means no uart data within 1s;
            #     1-byte list means there are bytes arrived on uart.

            # read all data from current uart buffer:
            rd_data = uart_bus.read(0)
            # this could return empty list when there is no data available;
            # this will return immediately.

        '''
        assert rd_len >= 0

        data_readed = 0
        result_data = []
        now = time.time()
        while True:
            rx_data = self.axi4_bus.read_16bit_inc(
                PLUARTDef.RXBUF_COUNT_REGISTER, 1)
            rx_buf_count = rx_data[0]
            if rd_len == 0:
                rd_len = rx_buf_count
            if rx_buf_count + data_readed > rd_len:
                rx_buf_count = rd_len - data_readed
            if rx_buf_count > 0:
                rd_data = self.axi4_bus.read_8bit_fix(
                    PLUARTDef.RX_BUF_REGISTER, rx_buf_count)
                result_data.extend(rd_data)
                data_readed += rx_buf_count

            if timeout_sec > 0:
                if time.time() > now + timeout_sec:
                    break

            if data_readed == rd_len:
                break

            time.sleep(AXI4Def.AXI4_DELAY)

        return result_data

    def write_hex(self, wr_data):
        '''
        Uart write hex data.

        This API shall be used by user software to handle DUT uart write.

        Args:
            data:    list, List data to be write.

        Returns:
            string, "done", api execution successful.

        Examples:
            string = 'abcd'
            wr_data = [ord(c) for c in string]
            uart_bus.write_hex(wr_data)

        '''
        assert isinstance(wr_data, list) and len(wr_data) > 0

        sent = 0
        while sent < len(wr_data):
            rd_data = self.axi4_bus.read_16bit_inc(
                PLUARTDef.TXBUF_COUNT_REGISTER, 1)
            tx_buf_count = rd_data[0]
            if len(wr_data) - sent > tx_buf_count:
                send_bytes = tx_buf_count
            else:
                send_bytes = len(wr_data) - sent

            self.axi4_bus.write_8bit_fix(PLUARTDef.TX_BUF_REGISTER,
                                         wr_data[sent:(sent + send_bytes)])
            sent += send_bytes
        return 'done'

    def _get_timestamp(self):
        '''
        Get uart time stamp config data

        Returns:
            boolean, [True, False], True for enable timestamp function,
                                    False for timestamp function.
        Examples:
                    timestamp_status = uart_bus.get_timestamp()
                    print(timestamp_status)

        '''
        config_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.TIMESTAMP_REGISTER, 1)[0]
        if config_data == PLUARTDef.TIMESTAMP_ENABLE_CMD:
            return True
        else:
            return False

    def _set_timestamp(self, state):
        '''
        Config Uart time stamp

        Args:
            state:  boolean, [True, False], timestamp state of Uart bus.

        Examples:
            Enable uart timestamp function.
            uart_bus.set_timestamp(True)

        '''
        assert state in [True, False]
        if state is True:
            self.axi4_bus.write_8bit_inc(PLUARTDef.TIMESTAMP_REGISTER,
                                         [PLUARTDef.TIMESTAMP_ENABLE_CMD])
        else:
            self.axi4_bus.write_8bit_inc(PLUARTDef.TIMESTAMP_REGISTER,
                                         [PLUARTDef.TIMESTAMP_DISABLE_CMD])

    def _get_baudrate(self):
        '''
        Uart set baud rate function, use it to set the baud rate

        Returns:
            int, value.

        Examples:
            baudrate = uart_bus.get_baudrate()
            print(baudrate)

        '''
        config_data = self.axi4_bus.read_32bit_inc(
            PLUARTDef.BADURATE_REGISTER, 1)[0]
        return int(config_data * AXI4Def.AXI4_CLOCK / pow(2, 32))

    def _set_baudrate(self, baud_rate):
        '''
        Uart set baud rate function, use it to set the baud rate to register

        Args:
            baud_rate:    int, [0~2000000], Baud rate of Uart bus.

        Examples:
            uart_bus.set_baudrate(115200)

        '''
        assert (baud_rate >= PLUARTDef.DEFAULT_MIN_BAUDRATE) and\
            (baud_rate <= PLUARTDef.DEFAULT_MAX_BAUDRATE)
        self.pl_baudrate = baud_rate
        rate_data = int(pow(2, 32) * baud_rate / AXI4Def.AXI4_CLOCK)
        self.axi4_bus.write_32bit_inc(PLUARTDef.BADURATE_REGISTER,
                                      [rate_data])

    def _get_databits(self):
        '''
        Get databits to config Uart function

        Returns:
            int, value.

        Examples:
            databits = uart_bus.get_databits
            print(databits)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        data_bits = rd_data & (PLUARTDef.DATABITS_MASK)
        data_bits = (data_bits >> 4) + 1
        return data_bits

    def _set_databits(self, data_bits):
        '''
        Use databit to config Uart function

        Args:
            data_bits:    int, [5, 6, 7, 8], databits of Uart bus.

        Examples:
            uart_bus.set_databits(8)

        '''
        assert data_bits in [5, 6, 7, 8]

        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        config = rd_data & (~PLUARTDef.DATABITS_MASK)
        config |= ((data_bits - 1) << 4)
        self.axi4_bus.write_8bit_inc(PLUARTDef.DATABIT_REGISTER, [config])

    def _get_parity(self):
        '''
        Uart set parity function, use it to set the parity to register

        Returns:
            int, value.

        Examples:
            parity = uart_bus.get_parity()
            print(parity)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        config = rd_data & (PLUARTDef.PARITY_MASK)
        return PLUARTDef.UART_PARITIES[config]

    def _set_parity(self, parity):
        '''
        Uart set parity function, use it to set the parity to register

        Args:
            parity:  string, ['none', 'even', 'odd'], parity bit of Uart bus.

        Examples:
            uart_bus.set_parity('none')

        '''
        assert parity in PLUARTDef.UART_PARITIES

        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        config = rd_data & (~PLUARTDef.PARITY_MASK)
        config |= PLUARTDef.UART_PARITIES.index(parity)

        self.axi4_bus.write_8bit_inc(PLUARTDef.DATABIT_REGISTER, [config])

    def _get_stopbits(self):
        '''
        Uart set stopbits function to register

        Returns:
            int, [1, 2].

        Examples:
            stopbits = uart_bus.get_stopbits()
            print(stopbits)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        config = ((rd_data & (PLUARTDef.STOPBITS_MASK)) >> 2) - 1
        return PLUARTDef.UART_STOPBITS[config]

    def _set_stopbits(self, stop_bits):
        '''
        Uart set stopbits function to config register

        Args:
            stop_bits:    int, [1, 2], stopbits of Uart bus.

        Examples:
            uart_bus.set_stopbits(1)

        '''
        assert stop_bits in PLUARTDef.UART_STOPBITS

        rd_data = self.axi4_bus.read_8bit_inc(
            PLUARTDef.DATABIT_REGISTER, 1)[0]
        config = rd_data & (~PLUARTDef.STOPBITS_MASK)
        config |= ((PLUARTDef.UART_STOPBITS.index(stop_bits) + 1) << 2)
        self.axi4_bus.write_8bit_inc(PLUARTDef.DATABIT_REGISTER, [config])
