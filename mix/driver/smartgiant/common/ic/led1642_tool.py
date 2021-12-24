# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ic.led1642 import LED1642
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


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


class LED1642Debuger(cmd.Cmd):
    prompt = 'led1642>'
    intro = 'Xavier led1642 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_set_grayscale(self, line):
        ''' set_grayscale 12, 16'''
        line = line.replace(' ', ',')
        self.led1642.set_grayscale(eval(line))
        print("Result:")
        print('done')

    @handle_errors
    def do_set_channels_duty(self, line):
        '''set_channels_duty [(0,50),(1,50)...] '''
        line = line.replace(' ', ',')
        self.led1642.set_channels_dut(eval(line))
        print("Result:")
        print('done')

    @handle_errors
    def do_set_current_range(self, line):
        '''set_current_range 0,1 '''
        line = line.replace(' ', ',')
        self.led1642.set_current_range(eval(line))
        print("Result:")
        print('done')

    @handle_errors
    def do_set_current_gain(self, line):
        '''set_current_gain 0,30,50 '''
        line = line.replace(' ', ',')
        self.led1642.set_current_gain(eval(line))
        print("Result:")
        print('done')

    @handle_errors
    def do_quit(self, line):
        '''quit()'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_led1642_dbg(led1642, signal_out_pin):
    led1642_dbg = LED1642Debuger()

    led1642_bus = AXI4LiteBus(led1642, 256)
    signal_out_en = GPIO(int(signal_out_pin))
    led1642_dbg.led1642 = LED1642(led1642_bus, signal_out_en)
    return led1642_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-led', '--led1642', help='led1642 bus device name', default='/dev/MIX_AxiLiteToStream_0')
    parser.add_argument('-signal_out', '--signal_out_pin', help='led signal output', default=87)
    args = parser.parse_args()
    led1642_dbg = create_led1642_dbg(args.led1642, args.signal_out_pin)

    led1642_dbg.cmdloop()
