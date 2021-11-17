# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_xadc_sg import MIXXADCSG

__author__ = 'zhuanghaite@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MIXXADCSGDebuger(cmd.Cmd):
    prompt = 'xadc>'
    intro = 'Xavier xadc debug tool'

    @handle_errors
    def do_config(self, line):
        '''config [sample_rate] [polar]'''
        line = line.replace(' ', ',')
        self.xadc.config(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_set_multiplex_channel(self, line):
        '''set_multiplex_channel [multiplex]'''
        line = line.replace(' ', '')
        if line.upper() == '0XFF':
            multiplex = 0xff
        else:
            multiplex = int(line, 10)
        self.xadc.set_multiplex_channel(multiplex)
        print('Done.')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt'''
        result = self.xadc.read_volt()
        print("Result:")
        print("%smV" % (result))

    @handle_errors
    def do_get_temperature(self, line):
        '''get_temperature'''
        result = self.xadc.get_temperature()
        print("Result:")
        print("%sC" % (result))

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling'''
        self.xadc.enable_continuous_sampling(eval(line))
        print('Done.')

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling'''
        self.xadc.disable_continuous_sampling()
        print('Done.')

    @handle_errors
    def do_get_continuous_sampling_voltage(self, line):
        '''get_continuous_sampling_voltage [count]'''
        line = line.replace(' ', ',')
        result = self.xadc.get_continuous_sampling_voltage(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_config.__doc__)
        print(self.do_set_multiplex_channel.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_get_temperature.__doc__)
        print(self.do_enable_continuous_sampling.__doc__)
        print(self.do_disable_continuous_sampling.__doc__)
        print(self.do_get_continuous_sampling_voltage.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_xadc_dbg(dev_name, reg_size):
    xadc_dbg = MIXXADCSGDebuger()
    axi4_bus = AXI4LiteBus(dev_name, reg_size)
    xadc_dbg.xadc = MIXXADCSG(axi4_bus)
    return xadc_dbg


arguments = [
    ['-d', '--device', 'device file name', ''],
    ['-s', '--size', 'device reserved memory size', '2048']
]


def create_dbg(args):
    return create_xadc_dbg(args.device, int(args.size))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()
    xadc_dbg = create_dbg(args)

    xadc_dbg.cmdloop()
