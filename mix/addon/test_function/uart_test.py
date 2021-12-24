import os
import re
import time
import select
import socket
import threading
import multiprocessing
import signal
# from threading import Thread


PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class UART_TEST(object):

    rpc_public_api = ['read','write','config','open','close','write_read']
    def __init__(self, xobjects):
        self._connect_socket = None
        self._uart_device = xobjects['uart']
        self._uart_device_net = xobjects['uart']
        self._inputs = []
        self._uart_stop = False
        
    def read(self, size = 1024, timeout_s=0):
        '''
        uart read data
        Args:
            size:      int,     default 1024
            timeout_s  int,      default 0
        Example:
            uart_read()
        '''
        result = self._uart_device.read_hex(size, timeout_s)
        new_string = []
        for c in result:
            if c !=255:
                new_string.append(str(chr(c)))
        if new_string:
            s=''.join(new_string)
            return s
        else:
            return ''

    def read_hex(self, size = 1024, timeout_s=0):
        '''
        uart read data hex
        Args:
            size:      int,     default 1024
            timeout_s  int,      default 0
        Example:
            read_hex()
        '''
        return self._uart_device.read_hex(size, timeout_s)

    def write(self, datastring, timeout_s=None):
        '''
        uart write string
        Args:
            datastring:      string,   any words
            timeout_s:       int,      none
        Example:
            uart_write(datastring)
            uart_write("hello world")
        '''
        data_list = []
        for c in datastring:
            data_list.append(int(str(ord(c))))
        return self._uart_device.write_hex(data_list)
    def write_hex(self, data, timeout_s=None):
        '''
        uart write hex
        Args:
            data:            int,   hex data
            timeout_s:       int,      none
        Example:
          uart_write_hex(0x13)
        '''
        return self._uart_device.write_hex(data)

    def write_read(self, datastring, timeout_s=None):
        '''
        uart write string
        Args:
            datastring:      string,   any words
            timeout_s:       int,      none
        Example:
            uart_write_read(datastring)
            uart_write_read("hello world")
        '''
        self.write(datastring)
        time.sleep(0.01)
        return self.read(1024,1)

    def config(self):
        '''
        uart config
        Args:
            name:   string,       uart device name or None. The port will open on object creation,
                                                when port given. The port will not be open when port not given.
                                                Default port is None.
            baudrate:              int,          uart baud rate such as 9600 or 115200 etc. Default baudrate is 115200.
            data_bits:              int,          number of data bits. Possible values: 5,6,7,8. Default data_bits is
                                                8bit.
            stop_bits:              float,        number of stop bits. Possible values: 1,1.5,2. Default stop_bits is 1.                                 
            parity:                string,       enable parity checking. Possible values: ('none'/'odd'/'even'/
                                                mark'/'space'). 'none' for no check 'odd' for odd check, 'even' for
                                                even check. Default no check parity, 'mark' for parity bit is always 1,
                                                'space' for parity bit is always 0.
            timestamp:              string,     reserve
 
        Example:
        uart_config(UUT,1000000,8,1,none,OFF)

        '''
        baudrate=115200
        data_bits=8
        stop_bits=1
        parity='none'
        self._uart_device.config(int(baudrate),int(data_bits),parity,int(stop_bits))
        return PASS_MASK

    def open(self):
        '''
        Open uart port and reset input/output buffer.
        Args:
            none
        Example:
            uart_open()
        '''
        return self._uart_device.open()
        
    def close(self):
        '''
        Uart close port immediately
        Args:
            none
        Example:
            uart_close()

        '''
        return self._uart_device.close()
