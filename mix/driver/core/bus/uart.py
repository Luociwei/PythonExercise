# -*- coding: utf-8 -*-
import os
import serial
from serial_emulator import SERIALEmulator


class UARTBusDef:
    PARITY = {
        'none': serial.PARITY_NONE,
        'even': serial.PARITY_EVEN,
        'odd': serial.PARITY_ODD,
        'mark': serial.PARITY_MARK,
        'space': serial.PARITY_SPACE
    }


class UARTException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class UART(object):
    '''
    Singleton wrapper of Xilinx UART driver using pyserial.

    ClassType = UART

    This is to ensure only 1 instance is created for the same char device
    in /dev/ttySx, even if instantiated multiple times.
    Please refer to _UART class docstring for parameters.

    Examples:
        uart_1 = UART('/dev/ttyS1')
        uart_2 = UART('/dev/ttyS1')
        assert uart_1 == uart_2          # True

    '''
    # class variable to host all i2c bus instances created.
    instances = {}

    def __new__(cls, dev_name=None, baudrate=115200, data_bits=8, parity='none', stop_bits=1):
        if dev_name in cls.instances:
            # use existing instance with using potentially new config
            cls.instances[dev_name].config(baudrate, data_bits, parity, stop_bits)
        else:
            # create a new one
            instance = _UART(dev_name, baudrate, data_bits, parity, stop_bits)
            cls.instances[dev_name] = instance
        return cls.instances[dev_name]


class _UART(object):
    '''
    UART class wrapped pyserial function

    Now UART class support Xilinx UART IP(16550 and uartlite) and PS UART.
    This class function can be called by rpc directly through uart instance.

    Args:
        port:        string, uart device name or None. The port will open on object creation,
                             when port given. The port will not be open when port not given.
                             Default port is None.
        baudrate:    int,    uart baud rate such as 9600 or 115200 etc. Default baudrate is 115200.
        data_bits:   int,    number of data bits. Possible values: 5,6,7,8. Default data_bits is
                                                8bit.
        parity:      string, enable parity checking. Possible values: ('none'/'odd'/'even'/
                             mark'/'space'). 'none' for no check 'odd' for odd check, 'even' for
                             even check. Default no check parity, 'mark' for parity bit is always 1,
                             'space' for parity bit is always 0.
        stop_bits:   float,  number of stop bits. Possible values: 1,1.5,2. Default stop_bits is 1.

    Raises:
        ValueError:          Will be raised when parameter are out of range, e.g. baud rate, data bits.
        SerialException:     In case the device can not be found or can not be configured.

    Examples:
        uart = UART('/dev/ttyPS0', 115200, 8, 'none', 1)
        uart.write('Hello world!')
        # wait data receive completed. Return all has been received datas,
        # if can not receive all 10 bytes data in 3 seconds.
        data = uart.read(10, 3)

    '''
    rpc_public_api = ['open', 'close', 'config', 'read_hex', 'write_hex']

    def __init__(self, dev_name=None, baudrate=115200, data_bits=8, parity='none', stop_bits=1):

        parity = UARTBusDef.PARITY[parity]

        if dev_name is not None and os.path.exists(dev_name):
            self._serial = serial.Serial(dev_name, baudrate, data_bits, parity, stop_bits)
            self._serial.flushInput()
            self._serial.flushOutput()
        elif dev_name is None:
            self._serial = SERIALEmulator(None, baudrate, data_bits, parity, stop_bits)
            self._serial.dev_name = dev_name
        else:
            raise UARTException(str(dev_name), "UART open fail!")

    def __del__(self):
        self.close()

    def open(self):
        '''
        Open uart port and reset input/output buffer.
        '''
        if not self._serial.isOpen():
            self._serial.open()

        return "done"

    def close(self):
        '''
        Uart close port immediately
        '''
        self._serial.close()
        return "done"

    def config(self, baudrate=115200, data_bits=8, parity='none', stop_bits=1):
        '''
        Uart configuration function, use to config the Uart.

        Args:
            baudrate:    int, default 115200, baud rate such as 9600 or 115200 etc. Default baudrate is 115200.
            data_bits:   int, default 8, number of data bits. Possible values: 5,6,7,8. Default data_bits is 8bit.
            parity:      string, ['none', 'odd', 'even'], default 'none', enable parity checking, checking parity.
            stop_bits:   float, default 1, number of stop bits. Possible values: 1,1.5,2.

        Examples:
            uart.config(115200, 8, 'none', 1)

        '''
        assert (baudrate > 0)
        assert data_bits in (serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS)
        assert parity in (param.lower() for param in serial.PARITY_NAMES.values())
        assert stop_bits in (serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)

        parity = parity[0].upper()

        self._serial.baudrate = baudrate
        self._serial.bytesize = data_bits
        self._serial.parity = parity
        self._serial.stopbits = stop_bits
        return "done"

    def read_hex(self, size, timeout_s=0):
        '''
        Uart read size bytes from the port. Note that data has been read is bytes.

        Args:
            size:        int, number of bytes to read. Default size is 1 byte.
            timeout_s:   float, default 0, set a read timeout value.

                            Posiible values for the parameter timeout_s which
                            controls the behavior of read():

                            - timeout_s = None: wait forever /utili
                                requested numbeer of bytes are received.
                            - timeout_s = 0: non-blocking mode, return
                                immediately in any case, returning zero
                                or more, up to the requested number of bytes
                            - timeout_s = x: set timeout to x seconds(float allowed)
                                return s immediately when
                                the requested number of bytes are available,
                                otherwise wait util the timeout_s expires and
                                return all bytes that were received util then.

        Returns:
            list, list read from the port.

        Examples:
            message = uart_bus.read(10, 3)
            print(message)

        '''
        assert (timeout_s >= 0) or (timeout_s is None)
        self._serial.timeout = timeout_s
        read_datas = self._serial.read(size)
        return [ord(x) for x in read_datas]

    def write_hex(self, data, timeout_s=None):
        '''
        Uart write the bytes data to the port.

        Args:
            data:          list,  the list data to be write.
            timeout_s:     float, set a write timeout value, default is blocking.

        Returns:
            int, value, number of bytes written.
        Raises:
            SerialTimeoutException:  In case a write timeout is configured for the port and the time
                                     is exceeded.

        Examples:
            uart_bus.write_hex([1, 2, 3, 4])

        '''
        assert isinstance(data, list) and len(data) > 0
        assert (timeout_s >= 0) or (timeout_s is None)
        self._serial.write_timeout = timeout_s
        self._serial.write(data)
        return 'done'

    def _read(self, size, timeout_s=0):
        '''
        Uart read size bytes from the port. Note that data has been read is bytes.

        Args:
            size:        int,   number of bytes to read. Default size is 1 byte.
            timeout_s:   float, default 0, set a read timeout value.

                            Posiible values for the parameter timeout_s which
                            controls the behavior of read():

                            - timeout_s = None: wait forever /utili
                                requested numbeer of bytes are received.
                            - timeout_s = 0: non-blocking mode, return
                                immediately in any case, returning zero
                                or more, up to the requested number of bytes
                            - timeout_s = x: set timeout to x seconds(float allowed)
                                return s immediately when
                                the requested number of bytes are available,
                                otherwise wait util the timeout_s expires and
                                return all bytes that were received util then.

        Returns:
            string, str, string read from the port.

        Examples:
            message = uart_bus.read(10, 3)
            print(message)

        '''
        assert (timeout_s >= 0) or (timeout_s is None)
        self._serial.timeout = timeout_s
        return self._serial.read(size)

    def _write(self, data, timeout_s=None):
        '''
        Uart write the bytes data to the port.

        Args:
            data:          string, the string data to be write.
            timeout_s:     float, set a write timeout value, default is blocking.

        Returns:
            string, "done", api execution successful.

        Raises:
            SerialTimeoutException:  In case a write timeout is configured for the port and the time
                                     is exceeded.

        Examples:
            count = uart_bus.write('Hello world!')
            print(count)

        '''
        assert len(data) > 0
        assert (timeout_s >= 0) or (timeout_s is None)
        self._serial.write_timeout = timeout_s
        self._serial.write(data)
        return 'done'

    def _get_baudrate(self):
        '''
        Uart get baud rate function, use it to get the baud rate

        Returns:
            int, value, return baud rate.

        Examples:
            baudrate = uart_bus.get_baudrate()
            print(baudrate)

        '''
        return self._serial.baudrate

    def _set_baudrate(self, baud_rate):
        '''
        Uart set baud rate function, use it to set the baud rate

        Args:
            baud_rate:    int(>0),     Baud rate of Uart bus

        Examples:
            uart_bus.set_baudrate(115200)

        '''
        assert (baud_rate > 0)
        self._serial.baudrate = baud_rate

    def _get_databits(self):
        '''
        Get databits to config Uart function

        Returns:
            int, value, return databit.

        Examples:
            databits = uart_bus.get_databits()
            print(databits)

        '''
        return self._serial.bytesize

    def _set_databits(self, data_bits):
        '''
        Use databit to config Uart function

        Args:
            data_bits:    int, [5, 6, 7, 8], databits of Uart bus.

        Examples:
            uart_bus.set_databits(8)

        '''
        assert data_bits in (serial.FIVEBITS, serial.SIXBITS, serial.SEVENBITS, serial.EIGHTBITS)

        self._serial.bytesize = data_bits

    def _get_parity(self):
        '''
        Uart get parity function, use it to get the parity value

        Returns:
            string, str, return parity flags.

        Examples:
            parity = uart_bus.get_parity()
            print(parity)

        '''
        return serial.PARITY_NAMES[self._serial.parity].lower()

    def _set_parity(self, parity):
        '''
        Uart set parity function, use it to set the parity to register

        Args:
            parity:  string, ['none', 'even', 'odd', 'mark', 'space'], parity bit of Uart bus.

        Examples:
            uart_bus.set_parity("none")

        '''
        assert parity in (param.lower() for param in serial.PARITY_NAMES.values())

        self._serial.parity = UARTBusDef.PARITY[parity]

    def _get_stopbits(self):
        '''
        Uart get stopbits function

        Returns:
            int, value, return stop_bits value

        Examples:
            stop_bits = uart_bus.get_stopbits()
            print(stop_bits)

        '''
        return self._serial.stopbits

    def _set_stopbits(self, stop_bits):
        '''
        Uart set stopbits function

        Args:
            stop_bits:    float, [1, 1.5, 2], stopbits of Uart bus.

        Examples:
            uart_bus.set_stopbits(1)

        '''
        assert stop_bits in (serial.STOPBITS_ONE, serial.STOPBITS_ONE_POINT_FIVE, serial.STOPBITS_TWO)

        self._serial.stopbits = stop_bits
