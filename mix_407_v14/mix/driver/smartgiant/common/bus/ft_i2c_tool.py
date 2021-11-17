# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.smartgiant.common.bus.ft_i2c import FTI2C
from mix.driver.smartgiant.common.bus.ft4222 import FT4222

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class FTI2CDebugger(cmd.Cmd):
    prompt = 'FTI2C>'
    intro = 'Xavier FTI2C bus debug tool'

    @handle_errors
    def do_read(self, line):
        '''read  <addr> <data_len>
        <addr>: 0-0xFF
        <data_len>: 0-1024
        '''
        line = line.replace(' ', ',')
        result = self.fti2c.read(*list(eval(line)))
        print(result)

    @handle_errors
    def do_write(self, line):
        '''write  <addr> <data>
        <addr>: 0-0xFF
        <data>: list
        '''
        line = line.replace(' ', ',')
        self.fti2c.write(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_write_and_read(self, line):
        '''write_and_read  <addr> <wr_data> <rd_len>
        <addr>: 0-0xFF
        <wr_data>: list
        <rd_len>: 0-1024
        '''
        line = line.replace(' ', ',')
        result = self.fti2c.write_and_read(*list(eval(line)))
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print('Usage:')
        print(self.do_read.__doc__)
        print(self.do_write.__doc__)
        print(self.do_write_and_read.__doc__)
        print(self.do_quit.__doc__)


def create_i2c_dbg(locid, bps):
    i2c_dbg = FTI2CDebugger()
    ft4222 = FT4222(locid)
    i2c_dbg.fti2c = FTI2C(ft4222, bps)

    return i2c_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--locid', help='locid of FT4222 device', default='0')
    parser.add_argument('-c', '--bps', help='FTI2C bus clock speed', default='400000')
    args = parser.parse_args()

    i2c_dbg = create_i2c_dbg(args.locid, int(args.bps))

    i2c_dbg.cmdloop()
