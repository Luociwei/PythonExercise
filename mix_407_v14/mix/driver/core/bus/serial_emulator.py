# -*- coding: utf-8 -*-
"""
This is a class of the implemention of UART for usual emulator
"""
import serial
from ..tracer.recorder import *


class SERIALException(Exception):
    pass


class SERIALEmulator(object):

    def __init__(self, port=None, baudrate=115200, bytesize=8, parity='none', stopbits=1):
        self._baudrate = baudrate
        self._bytesize = bytesize
        self._parity = parity
        self._stopbits = stopbits
        self._recorder = Recorder()
        self._timeout = 0
        self._write_timeout = 0
        add_recorder(self._recorder)

    def open(self):
        self._recorder.record("serial open")

    def close(self):
        self._recorder.record("serial close")

    def read(self, size=1, timeout=0):
        '''
        Uart read size bytes from the port. Note that data has been read is bytes.

        :param size:        int,        number of bytes to read. Default size is 1 byte.
        :param timeout:     float,      set a read timeout value. Default timeout = 0.

                                        Posiible values for the parameter timeout which
                                        controls the behavior of read():

                                        - timeout = None: wait forever /utili
                                            requested numbeer of bytes are received.
                                        - timeout = 0: non-blocking mode, return
                                            immediately in any case, returning zero
                                            or more, up to the requested number of bytes
                                        - tiemout = x: set timeout to x seconds(float allowed)
                                            return s immediately when
                                            the requested number of bytes are available,
                                            otherwise wait util the tiemout expires and
                                            return all bytes that were received util then.

        :returns:           bytes       Bbytes read from the port.
        '''
        self._recorder.record("read %d bytes from serial bus" % (size))
        return bytes(bytearray([x for x in range(size)]))

    def write(self, data, timeout=0):
        '''
        Uart write the bytes data to the port.

        :param data:                        string,         the string data to be write.
        :param timeout:                     float,          set a write timeout value, default is blocking.
        :return:                            int,            number of bytes written.
        :raises SerialTimeoutException:     In case a write timeout is configured for the port and the time is exceeded.
        '''
        self._recorder.record("write %s to serial bus" % (str(data)))

    @property
    def write_timeout(self):
        '''
        Uart write timeout function, use it to get the write time out limit

        :returns:   int
        :example:
                    write_timeout = serial.write_timeout
                    print(write_timeout)
        '''
        self._recorder.record("get write_timeout: %d" % (self._write_timeout))
        return self._write_timeout

    @write_timeout.setter
    def write_timeout(self, timeout):
        '''
        Uart write timeout function, use it to set the write time out limit

        :returns:   int
        :example:
                    serial.write_timeout = 10
        '''
        self._write_timeout = timeout
        self._recorder.record("set write_timeout: %d" % (self._write_timeout))

    @property
    def timeout(self):
        '''
        Uart timeout function, use it to get the time out limit

        :returns:   int
        :example:
                    timeout = serial.timeout
                    print(timeout)
        '''
        self._recorder.record("get timeout: %d" % (self._timeout))
        return self._timeout

    @timeout.setter
    def timeout(self, timeout):
        '''
        Uart timeout function, use it to set the time out limit

        :returns:   int
        :example:
                    serial.timeout = 10
        '''
        self._timeout = timeout
        self._recorder.record("set timeout: %d" % (self._timeout))

    @property
    def baudrate(self):
        '''
        Uart set baud rate function, use it to set the baud rate

        :returns:   int
        :example:
                    baudrate = serial.baudrate
                    print(baudrate)
        '''
        self._recorder.record("get baudrate: %d" % (self._baudrate))
        return self._baudrate

    @baudrate.setter
    def baudrate(self, baud_rate):
        '''
        Uart set baud rate function, use it to set the baud rate to register

        :param     baud_rate:    int(0-4000000),     Baud rate of Uart bus
        :example:
                    serial.baudrate = 115200
        '''
        assert (baud_rate > 0) and (baud_rate <= 4000000)
        self._baudrate = baud_rate
        self._recorder.record("set baudrate: %d" % (self._baudrate))

    @property
    def bytesize(self):
        '''
        Get bytesize to config Uart function

        :returns:   int
        :example:
                    bytesize = serial.bytesize
                    print(bytesize)
        '''
        self._recorder.record("get bytesize: %d" % (self._bytesize))
        return self._bytesize

    @bytesize.setter
    def bytesize(self, bytesize):
        '''
        Use databit to config Uart function

        :param     bytesize:        int(5/6/7/8),        bytesize of Uart bus
        :example:
                    serial.bytesize = 8
        '''
        assert bytesize in (5, 6, 7, 8)
        self._bytesize = bytesize
        self._recorder.record("set bytesize: %d" % (self._bytesize))

    @property
    def parity(self):
        '''
        Uart set parity function, use it to set the parity to register

        :example:
        :returns:   int
                    parity = serial.parity
                    print(parity)
        '''
        self._recorder.record("get parity: %s" % (self._parity))
        return self._parity

    @parity.setter
    def parity(self, parity):
        '''
        Uart set parity function, use it to set the parity to register

        :param     parity:  string('N', 'E', 'O', 'M', 'S'),        parity bit of Uart bus
        :example:
                    serial.parity = "none"
        '''
        assert parity in ('N', 'E', 'O', 'M', 'S')
        self._parity = parity
        self._recorder.record("set parity: %s" % (self._parity))

    @property
    def stopbits(self):
        '''
        Uart set stopbits function to register

        :returns:   int
        :example:
                    stopbits = serial.stopbits
                    print(stopbits)
        '''
        self._recorder.record("get stopbits: %0.1f" % (self._stopbits))
        return self._stopbits

    @stopbits.setter
    def stopbits(self, stop_bits):
        '''
        Uart set stopbits function to config register

        :param     stop_bits:        float(1, 1.5, 2),        stopbits of Uart bus
        :example:
                    serial.stopbits = 1
        '''
        assert stop_bits in (1, 1.5, 2)
        self._stopbits = stop_bits
        record_str = "set stopbits: %0.1f" % (self._stopbits)
        self._recorder.record(record_str)

