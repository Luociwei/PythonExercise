# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_ltc2386_sg import MIXLTC2386SG


__author__ = 'xuboyan@SmartGiant'
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


class MIXLTC2386SGDebuger(cmd.Cmd):
    prompt = 'mixltc2386sg>'
    intro = 'Xavier mixltc2386sg debug tool'

    @handle_errors
    def do_enable(self, line):
        '''enable
        MIXLTC2386SG enable function '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.mixltc2386sg.enable()
        print("Done.")

    @handle_errors
    def do_disable(self, line):
        '''disable
        MIXLTC2386SG disable function '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.mixltc2386sg.disable()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate <sample_rate>
        <sample_rate>: int, [20000~10000000], unit SPS, ADC sample rate. '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.mixltc2386sg.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_channel_select(self, line):
        '''channel_select <channel> <adc_resolution>
        <channel>: string, ['CHA', 'CHAB'].
        <adc_resolution>: string, ['16bit', '18bit']. '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.mixltc2386sg.channel_select(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.mixltc2386sg.read_volt()
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        return True

    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_mixltc2386sg_dbg(dev_name):
    mixltc2386sg_dbg = MIXLTC2386SGDebuger()
    mixltc2386sg_dbg.mixltc2386sg = MIXLTC2386SG(axi4_bus=dev_name)
    return mixltc2386sg_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/MIX_LTC2386_SG')
    args = parser.parse_args()

    spi_return_dbg = create_mixltc2386sg_dbg(args.device)

    spi_return_dbg.cmdloop()
