# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.smartgiant.common.bus.ft_gpio import FTGPIO
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


class FTGPIODebuger(cmd.Cmd):
    prompt = 'FTGPIO>'
    intro = 'Xavier FTGPIO debug tool'

    @handle_errors
    def do_set_pin_dir(self, line):
        '''set_pin_dir <pin_id> <dir>
        <pin_id>: 0-3
        <dir>:'input'/'output'
        '''
        line = line.replace(' ', ',')
        self.ftgpio.set_pin_dir(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_get_pin_dir(self, line):
        '''get_pin_dir <pin_id>
        <pin_id>: 0-3
        '''
        result = self.ftgpio.get_pin_dir(eval(line))
        print(result)

    @handle_errors
    def do_set_pin(self, line):
        '''set_pin <pin_id> <level>
        <pin_id>: 0-3
        <level>: 0/1
        '''
        line = line.replace(' ', ',')
        self.ftgpio.set_pin(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_get_pin(self, line):
        '''get_pin <pin_id>
        <pin_id>: 0-3
        '''
        result = self.ftgpio.get_pin(eval(line))
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print('Usage:')
        print(self.do_set_pin_dir.__doc__)
        print(self.do_get_pin_dir.__doc__)
        print(self.do_set_pin.__doc__)
        print(self.do_get_pin.__doc__)
        print(self.do_quit.__doc__)


def create_dbg(locid, delay):
    dbg = FTGPIODebuger()
    ft4222 = FT4222(locid)
    dbg.ftgpio = FTGPIO(ft4222, delay)

    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--locid', help='locid of FT4222 device', default='1')
    parser.add_argument('-d', '--delay', help='delay between Init and Write', default='0')
    args = parser.parse_args()

    dbg = create_dbg(args.locid, int(args.delay))

    dbg.cmdloop()
