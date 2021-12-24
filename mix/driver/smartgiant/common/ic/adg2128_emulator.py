# -*- coding:utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class ADG2128Def:

    XLINE_READBACK_ADDR = [
        0x34, 0x3c, 0x74, 0x7c, 0x35, 0x3d,
        0x75, 0x7d, 0x36, 0x3e, 0x76, 0x7e
    ]

    X_LINE_WRITE_ADDRESS = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D]
    Y_LINE_WRITE_ADDRESS = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07]

    TRANSPARENT_MODE = 1
    LATCHED_MODE = 0


class ADG2128Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class ADG2128Emulator(object):
    '''
    ADG2128 Emulator class
    '''

    def __init__(self, dev_name):
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def write_register(self, reg_addr, reg_data):
        '''
        ADG2128 write data to address

        Args:
            reg_addr:    hexmial, [0~0FF], Write data to this address.
            reg_data:    list, [0x0], Write register data.

        Examples:
            adg2128.write(0x12, [0x00])

        '''

        assert reg_addr >= 0 and reg_data <= 0x01

        write_data = [reg_addr, reg_data]
        self._recorder.record("%s write %s to 0x%02x" % (self.dev_name, hex(write_data[1]), write_data[0]))

    def read_register(self, reg_addr, length):
        '''
        ADG2128 read specific length data from address

        Args:
            reg_addr:   hexmial, [0~0FF], Read data from this address.
            length:     int, [0~2], Length to read.

        Returns:
            list, [value].

        Examples:
            rd_data = adg2128.read_register(0x00, 1)
            print(rd_data)

        '''
        assert reg_addr in ADG2128Def.XLINE_READBACK_ADDR
        assert 0 <= length <= 2

        cmd_list = [reg_addr, 0x00]
        rd_data = cmd_list
        self._recorder.record("%s read 0x%02x with %d bytes" % (self.dev_name, reg_addr, length))
        return rd_data

    def connect(self, x, y):
        '''
        ADG2128 close/on x-y channel

        Args:
            x:   int, [0~11].
            y:   int, [0~7].

        Examples:
            adg2128.connect(0, 3)

        '''
        assert isinstance(x, int) and isinstance(y, int)
        assert 0 <= x <= 11 and 0 <= y <= 7
        switch = 1 << 7 | ADG2128Def.X_LINE_WRITE_ADDRESS[x] << 3 | ADG2128Def.Y_LINE_WRITE_ADDRESS[y]
        self.write_register(switch, ADG2128Def.TRANSPARENT_MODE)
        self._recorder.record("%s connect %d-%d channel" % (self.dev_name, x, y))

    def disconnect(self, x, y):
        '''
        ADG2128 open/off x-y channel

        Args:
            x:   int, [0~11].
            y:   int, [0~7].

        Examples:
            adg2128.disconnect(0, 3)

        '''
        assert isinstance(x, int) and isinstance(y, int)
        assert 0 <= x <= 11 and 0 <= y <= 7
        switch = ADG2128Def.X_LINE_WRITE_ADDRESS[x] << 3 | ADG2128Def.Y_LINE_WRITE_ADDRESS[y]
        self.write_register(switch, ADG2128Def.TRANSPARENT_MODE)
        self._recorder.record("%s disconnect %d-%d channel" % (self.dev_name, x, y))

    def is_connect(self, x, y):
        '''
        ADG2128 read x-y channel state

        Args:
            x:   int, [0~11].
            y:   int, [0~7].

        Returns:
            int, [0, 1], 0 means open/off, 1 means close/on.

        Examples:
            adg2128.connect(0, 3)

        '''
        assert isinstance(x, int) and isinstance(y, int)
        assert 0 <= x <= 11 and 0 <= y <= 7
        readback_addr = ADG2128Def.XLINE_READBACK_ADDR[x]
        ra_data = self.read_register(readback_addr, 2)
        self._recorder.record("%s is_connect %d-%d channel" % (self.dev_name, x, y))
        return ra_data[1] & (1 << y)

    def set_xy_state(self, switch_val):
        '''
        ADG2128 set the xy state

        Args:
            switch_val:  list, eg: [[1,2,0], [3,4,1] means X1Y2=0 ,X3Y4=1.

        Raises:
            ADG2128Exception:An error occurred when set switch XiYj state for ADG2128 fail.

        Examples:
            adg2128.set_xy_state([[1,2,0], [3,4,1]])

        '''
        if not switch_val or not (isinstance(switch_val, list) and
                                  isinstance(switch_val[0], list)):
            raise ADG2128Exception(
                "An error occurred when set switch XiYj state\
                for ADG2128 fail.")
        else:
            for val in switch_val:
                if val[2]:
                    self.connect(val[0], val[1])
                else:
                    self.disconnect(val[0], val[1])
        self._recorder.record("%s set the xy state" % (self.dev_name))

    def get_xy_state(self, switch_val):
        '''
        ADG2128 get the xy state

        Args:
            switch_val:      list, eg: [[1,2], [3,4]] means witch X1Y2 and switch X3Y4.

        Returns:
            list, [[value, value, value],[value, value, value]], eg: [[1,2,1], [3,4,0]] means X1Y2=1, X3Y4=0.

        Raises:
            ADG2128Exception:An error occurred when set switch XiYj state for ADG2128 fail.

        Examples:
            rd_data = adg2128.get_xy_state([[1,2], [3,4]])
            print(switch_val)

        '''
        if not switch_val or not (isinstance(switch_val, list) and isinstance(switch_val[0], list)):
            raise ADG2128Exception(
                "An error occurred when set switch XiYj state\
                for adg2128 fail.")
        else:
            for val in switch_val:
                state = self.is_connect(val[0], val[1])
                val.append(state)

        self._recorder.record("%s get the xy state" % (self.dev_name))
        return switch_val
