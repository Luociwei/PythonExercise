# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

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


class FT4222Debugger(cmd.Cmd):
    prompt = 'ft4222>'
    intro = 'Xavier ft4222 bus debug tool'

    @handle_errors
    def do_open(self, line):
        '''open'''
        self.ft4222.open()
        print('Done')

    @handle_errors
    def do_close(self, line):
        '''close'''
        self.ft4222.close()
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print('Usage:')
        print(self.do_open.__doc__)
        print(self.do_close.__doc__)
        print(self.do_quit.__doc__)


def create_ft4222_dbg(locid):
    ft4222_dbg = FT4222Debugger()
    ft4222_dbg.ft4222 = FT4222(locid)

    return ft4222_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--locid', help='locid of FT4222 device', default='0')
    args = parser.parse_args()

    ft4222_dbg = create_ft4222_dbg(args.locid)

    ft4222_dbg.cmdloop()
