# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from pl_i2c_bus import *
from i2c import *
from ..utility import utility
from axi4_lite_bus import AXI4LiteBus


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class I2CBusDebugger(cmd.Cmd):
    prompt = 'i2c>'
    intro = 'Xavier i2c bus debug tool'
    i2c_bus = None

    def _write(self, line):
        line = line.replace(' ', ',')
        self.i2c_bus.write(*list(eval(line)))
        print('Done.')
        return

    def _read(self, line):
        line = line.replace(' ', ',')
        data = self.i2c_bus.read(*list(eval(line)))
        print('Result:')
        print(data)
        return

    def _write_and_read(self, line):
        line = line.replace(' ', ',')
        data = self.i2c_bus.write_and_read(*list(eval(line)))
        print('Write done.Return result:')
        print(data)
        return

    @handle_errors
    def do_write(self, line):
        '''write [device_address] [data]'''
        self._write(line)

    @handle_errors
    def do_read(self, line):
        '''read [device_address] [size]'''
        self._read(line)

    @handle_errors
    def do_write_and_read(self, line):
        '''write_and_read [device_address] [data] [read_length]'''
        self._write_and_read(line)

    @handle_errors
    def do_w(self, line):
        '''w [device_address] [data] #write command#'''
        self._write(line)

    @handle_errors
    def do_r(self, line):
        '''r [device_address] [size] #read command#'''
        self._read(line)

    @handle_errors
    def do_wr(self, line):
        '''wr [device_address] [data] [read_length] #write and read command#'''
        self._write_and_read(line)

    def do_quit(self, line):
        '''quit'''
        return True

    def do_scan(self, line):
        '''
        TODO: scan i2c device list
        '''
        pass

    def do_help(self, line):
        print('Usage:')
        print(self.do_write.__doc__)
        print(self.do_w.__doc__)
        print(self.do_read.__doc__)
        print(self.do_r.__doc__)
        print(self.do_write_and_read.__doc__)
        print(self.do_wr.__doc__)


def create_i2c_dbg(dev_name, reg_size):
    i2c_dbg = I2CBusDebugger()
    if dev_name == '':
        print("i2c device name error")
        exit()
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, reg_size)
            i2c_dbg.i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_dbg.i2c_bus = I2C(dev_name)
    return i2c_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default="")
    parser.add_argument('-s', '--size', help='device reserved memory size', default='256')
    args = parser.parse_args()

    i2c_dbg = create_i2c_dbg(args.device, int(args.size))

    i2c_dbg.cmdloop()
