# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from ads1112 import ADS1112
from ..bus.i2c import I2C


__author__ = 'jihua.jiang@SmartGiant'
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


class ADS1112Debuger(cmd.Cmd):
    prompt = 'ads1112>'
    intro = 'Xavier ads1112 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_reset(self, line):
        '''reset

        eg: reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ads1112.reset()
        print('done')

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling

        eg: disable_continuous_sampling'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ads1112.disable_continuous_sampling()
        print('done')

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling channel

        channel: int(0/1/2/3)
        eg: enable_continuous_sampling 0'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ads1112.enable_continuous_sampling(eval(line))
        print('done')

    @handle_errors
    def do_set_sample_rate(self, line):
        '''set_sample_rate rate

        rate: int(15/30/60/240)
        eg: set_sample_rate 15'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ads1112.set_sample_rate(eval(line))
        print('done')

    @handle_errors
    def do_get_sample_rate(self, line):
        '''get_sample_rate

        eg: get_sampling_rate'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.ads1112.get_sample_rate()
        print(result)

    @handle_errors
    def do_set_pga_gain(self, line):
        '''set_pga_gain gain

        gain: int(1/2/4/8)
        eg: set_pga_gain 1'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ads1112.set_pga_gain(eval(line))
        print('done')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt channel

        channel:    int(0/1/2/3)
        eg:         read_volt 0 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ads1112.disable_continuous_sampling()
        result = self.ads1112.read_volt(eval(line))
        print(result)

    @handle_errors
    def do_get_continuos_volt(self, line):
        '''get_continuos_volt
        ADS1112 read the voltage of specific channel.
        channel:    int(0/1/2/3)
        eg:         get_continuos_volt 10 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ads1112.get_continuous_sampling_voltage(10)
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_ads1112_dbg(dev_name, dev_addr):
    ads1112_dbg = ADS1112Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        i2c_bus = I2C(dev_name)
    ads1112_dbg.ads1112 = ADS1112(dev_addr, i2c_bus)
    return ads1112_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x48')
    args = parser.parse_args()
    ads1112_dbg = create_ads1112_dbg(args.device, int(args.address, 16))

    ads1112_dbg.cmdloop()
