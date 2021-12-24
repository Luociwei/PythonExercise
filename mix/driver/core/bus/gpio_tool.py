# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from gpio import GPIO


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


def get_function_doc(self=None):
    '''Get function.__doc__ '''
    func_name = inspect.stack()[1][3]
    if self is None:
        return eval('%s' % func_name).__doc__
    else:
        return getattr(self, func_name).__doc__


class GPIODebuger(cmd.Cmd):
    prompt = 'GPIO>'
    intro = 'Xavier GPIO debug tool'

    @handle_errors
    def do_set_level(self, line):
        '''set_level <level>
        <level>: 0 or 1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        level = int(line)
        self.mio.set_level(level)
        print('Done')

    @handle_errors
    def do_get_level(self, line):
        '''get_pin'''

        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.mio.get_level()
        print(result)

    @handle_errors
    def do_set_dir(self, line):
        '''set_dir <dir>
        <dir>: output or intput
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        direction = line
        self.mio.set_dir(direction)
        print('Done')

    @handle_errors
    def do_get_dir(self, line):
        '''get_dir'''

        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.mio.get_dir()
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_dbg(pin_id, direction, is_inversion):
    dbg = GPIODebuger()
    dbg.mio = GPIO(pin_id, direction, is_inversion)
    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pin_id', help='GPIO pin id range(0 ~ 1023)', default='0')
    parser.add_argument('-d', '--direction', help='gpio direction(intput output)', default='input')
    parser.add_argument('-i', '--inversion', help='is inversion, 1 is inversion', default='0')
    args = parser.parse_args()

    dbg = create_dbg(int(args.pin_id), args.direction, int(args.inversion))

    dbg.cmdloop()
