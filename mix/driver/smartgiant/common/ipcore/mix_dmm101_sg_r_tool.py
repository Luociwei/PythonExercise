# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps
from mix.driver.smartgiant.nightcrawler.module.mix_dmm101_sg_r import MIXDMM101SGR


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


class MIXDMM101SGRDebuger(cmd.Cmd):
    prompt = 'mixdmm101sgr>'
    intro = 'Xavier mixdmm101sgr debug tool'

    @handle_errors
    def do_enable(self, line):
        '''enable
        MIXDMM101SGR enable function '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.mixdmm101sgr.enable()
        print("Done.")

    @handle_errors
    def do_disable(self, line):
        '''disable
        MIXDMM101SGR disable function '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.mixdmm101sgr.disable()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate <sample_rate>
        <sample_rate>: int, [20000~10000000], unit SPS, ADC sample rate. '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.mixdmm101sgr.set_sampling_rate(*list(eval(line)))
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
        self.mixdmm101sgr.channel_select(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.mixdmm101sgr.read_volt()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_continuous_sampling_voltage(self, line):
        '''get_continuous_sampling_voltage <count>
        <count>: int, [1~2048], how many data to get. '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        result = self.mixdmm101sgr.get_continuous_sampling_voltage(*list(eval(line)))
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


def create_mixdmm101sgr_dbg(dev_name):
    mixdmm101sgr_dbg = MIXDMM101SGRDebuger()
    mixdmm101sgr_dbg.mixdmm101sgr = MIXDMM101SGR(axi4_bus=dev_name)
    return mixdmm101sgr_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/MIX_DMM101_SG_R')
    args = parser.parse_args()

    spi_return_dbg = create_mixdmm101sgr_dbg(args.device)

    spi_return_dbg.cmdloop()
