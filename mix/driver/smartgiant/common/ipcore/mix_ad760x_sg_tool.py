# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.mix_ad760x_sg import *

__author__ = 'weiping.mo@SmartGiant'
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


class MIXAd760xSGDebuger(cmd.Cmd):
    prompt = 'ad760x>'
    intro = 'Xavier ad760x debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_reset(self, line):
        '''reset
        AD760X internal function to reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad760x.reset()
        print('Done')
        return

    @handle_errors
    def do_single_sampling(self, line):
        '''single_sampling
        AD760X internal function to measure single voltage
        over_sampling: int(0-7), OS[2:0] oversample bit value
        adc_range: string('10V'/'5V'), adc reference voltage range
        eg: single_sampling 0,'5V' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.ad760x.single_sampling(*list(eval(line)))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling
        AD760X internal function to enable continuous measure
        over_sampling: int(0-7), OS[2:0] oversample bit value
        adc_range: string('10V'/'5V'), adc reference voltage range
        sampling_rate:  int(2000~200000), adc sampling rate
        eg: enable_continuous_sampling 0,'5V',2000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad760x.enable_continuous_sampling(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling
        AD760X internal function to disable continuous measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad760x.disable_continuous_sampling()
        print('Done')
        return

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


def create_ad760x_dbg(dev_name):
    ad760x_dbg = MIXAd760xSGDebuger()
    if dev_name == '':
        axi4_bus = None
    else:
        axi4_bus = AXI4LiteBus(dev_name, 8192)
    ad760x_dbg.ad760x = MIXAd760xSG(axi4_bus, 8)
    return ad760x_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name',
                        default='/dev/AXI4_AD760x_0')
    args = parser.parse_args()

    ad760x_dbg = create_ad760x_dbg(args.device)

    ad760x_dbg.cmdloop()
