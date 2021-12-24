# -*- coding: utf-8 -*-
import ctypes
import struct
from spi_emulator import SpiEmuLib


class SPIDef:
    SPI_MODES = {
        # CPOL=0, CPHA=0
        "MODE0": 0x00,
        # CPOL=0, CPHA=1
        "MODE1": 0x01,
        # CPOL=1, CPHA=0
        "MODE2": 0x02,
        # CPOL=1, CPHA=1
        "MODE3": 0x03,
    }
    SPI_PROTOCOL = {
        "SPI": 0,
        "QPI": 0xA00,
        "DPI": 0x500,
        "QSPI": 0xA00,
    }

    MODE_MASK = 0x03
    PROTOCOL_MASK = 0xF00


class SPIException(Exception):
    def __init__(self, dev_name, err_code):
        reason = (128 * ctypes.c_char)()
        base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        base_lib.get_error_reason(err_code, reason, len(reason))
        self._err_reason = '[%s]: %s.' % (dev_name, ctypes.string_at(reason, -1).decode("utf-8"))

    def __str__(self):
        return self._err_reason


class SPI(object):
    '''
    SPIBus function class

    ClassType = QSPI

    This driver can be used to drive xilinx spi ipcore.

    Args:
        dev_name:   string, SPIBus device name.

    Examples:
        spi = SPIBus('/dev/spidev32766.0')

    '''
    rpc_public_api = [
        'close', 'get_wait_us', 'set_wait_us', 'get_mode', 'set_mode',
        'get_speed', 'set_speed', 'config_protocol', 'write', 'read', 'transfer'
    ]

    def __init__(self, dev_name):
        self._dev_name = dev_name
        if not dev_name:
            self.base_lib = SpiEmuLib()
        else:
            self.base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        '''
        SPIBus open device, has been called once when init

        Examples:
            spi.open()

        '''
        self._spi = self.base_lib.spi_open(self._dev_name)
        if self._spi == 0:
            raise RuntimeError('Open SPI device %s failure.' % (self._dev_name))

    def close(self):
        '''
        SPIBus close device

        Examples:
            i2c.close()

        '''
        self.base_lib.spi_close(self._spi)

    def get_wait_us(self):
        '''
        SPIBus get wait time before next transmition

        Examples:
            wait_us = spi.get_wait_us()
            print(wait_us)

        '''
        usecs = ctypes.c_ushort()
        result = self.base_lib.spi_get_wait_us(self._spi, ctypes.byref(usecs))
        if result != 0:
            raise SPIException(self._dev_name, result)
        return struct.unpack('H', usecs)[0]

    def set_wait_us(self, us):
        '''
        SPIBus set wait us

        Args:
            us:    int, Wait time before next transmition.

        Examples:
            spi.set_wait_us(us)

        '''
        self.base_lib.spi_set_wait_us(self._spi, us)

    def get_mode(self):
        '''
        SPIBus get CPOL and CPHA mode

        Examples:
            mode = spi.get_mode()
            print(mode)

        '''
        cmode = ctypes.c_uint()
        self.base_lib.spi_get_mode(self._spi, ctypes.byref(cmode))

        mode = struct.unpack('I', cmode)[0] & SPIDef.MODE_MASK
        for key in SPIDef.SPI_MODES.keys():
            if SPIDef.SPI_MODES[key] == mode:
                return key
        return "none"

    def set_mode(self, mode):
        '''
        PLSPIBus set CPOL and CPHA mode

        Args:
            mode:   string, ['MODE0', 'MODE1', 'MODE2', 'MODE3'], CPOL and CPHA mode.

        Examples:
            spi.set_mode(mode)

        '''
        # read mode
        cmode = ctypes.c_uint()
        result = self.base_lib.spi_get_mode(self._spi, ctypes.byref(cmode))
        if result != 0:
            raise SPIException(self._dev_name, result)

        mode_data = struct.unpack('I', cmode)[0] & SPIDef.PROTOCOL_MASK

        # set mode
        mode_data |= SPIDef.SPI_MODES[mode]
        result = self.base_lib.spi_set_mode(self._spi, mode_data)
        if result != 0:
            raise SPIException(self._dev_name, result)

    def get_speed(self):
        '''
        SPIBus get transmition speed

        Examples:
            speed = spi.get_speed()
            print(speed)

        '''
        rate = ctypes.c_uint()
        result = self.base_lib.spi_get_frequency(self._spi, ctypes.byref(rate))
        if result != 0:
            raise SPIException(self._dev_name, result)

        return struct.unpack('I', rate)[0]

    def set_speed(self, speed):
        '''
        SPIBus set transmit speed

        Args:
            speed:  int, Spi transmition speed.

        Examples:
            spi.set_speed(speed)

        '''
        result = self.base_lib.spi_set_frequency(self._spi, speed)
        if result != 0:
            raise SPIException(self._dev_name, result)

    def config_protocol(self, mode):
        '''
        Config spi protocol mode. Now spi bus driver support SPI/QPI mode.

        Args:
            mode:    string, ['SPI', QPI', 'QSPI'), spi bus work mode. 'SPI' mode is standard mode.
                                                    'QPI', 'QSPI' mode has 4 data lines.

        Raises:
            SPIException:    Raise exception when config spi bus mode failed.

        Examples:
            spi_bus = SPIBus('/dev/MIX_SPI_0')
            spi_bus.config_protocol('SPI')

        '''
        # read
        cmode = ctypes.c_uint()
        result = self.base_lib.spi_get_mode(self._spi, ctypes.byref(cmode))
        if result != 0:
            raise SPIException(self._dev_name, result)

        mode_data = struct.unpack('I', cmode)[0] & SPIDef.MODE_MASK
        if mode != 'SPI':
            mode_data |= SPIDef.SPI_PROTOCOL[mode]

        # write
        result = self.base_lib.spi_set_mode(self._spi, mode_data)
        if result != 0:
            raise SPIException(self._dev_name, result)

    def write(self, wr_data):
        '''
        SPIBus write data function

        Args:
            wr_data:    list,       Datas to be write

        Examples:
            spi.write([1, 2, 3])

        '''
        data = (ctypes.c_ubyte * len(wr_data))(*wr_data)
        result = self.base_lib.spi_write(self._spi, data, len(wr_data))
        if result != 0:
            raise SPIException(self._dev_name, result)

    def read(self, rd_len):
        '''
        SPIBus read data function

        Args:
            rd_len:     int,        Length of datas to be read.

        Examples:
            datas = spi.read(3)
            print(datas)

        '''
        rd_len = int(rd_len)
        assert rd_len > 0
        rd_data = (ctypes.c_ubyte * rd_len)()
        result = self.base_lib.spi_read(self._spi, rd_data, rd_len)
        if result != 0:
            raise SPIException(self._dev_name, result)

        return list(struct.unpack('%dB' % rd_len, rd_data))

    def transfer(self, wr_data, rd_len=0, sync=True):
        '''
        SPIBus transfer data function

        Args:
            wr_data:    list,       Datas to be send.
            rd_len:     int,        Length of datas to be read.
            sync:       boolean,    True for write and read synchronizily,
                                    False for write then read from spi bus.

        Examples:
            data = spi.transfer([1, 2, 3], 4, False)
            print(data)

        '''
        rd_len = int(rd_len)

        if sync:
            crd_data = (ctypes.c_ubyte * len(wr_data))()
            cwr_data = (ctypes.c_ubyte * len(wr_data))(*wr_data)

            result = self.base_lib.spi_sync_transfer(self._spi, cwr_data, crd_data, len(wr_data))
            if result != 0:
                raise SPIException(self._dev_name, result)

            return list(struct.unpack('%dB' % (len(wr_data)), crd_data))
        else:
            crd_data = (ctypes.c_ubyte * rd_len)()
            cwr_data = (ctypes.c_ubyte * len(wr_data))(*wr_data)

            result = self.base_lib.spi_async_transfer(self._spi, cwr_data, len(wr_data), crd_data, rd_len)
            if result != 0:
                raise SPIException(self._dev_name, result)

            return list(struct.unpack('%dB' % (rd_len), crd_data))
