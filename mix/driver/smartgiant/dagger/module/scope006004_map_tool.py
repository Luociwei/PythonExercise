# -*- coding: utf-8 -*-
import argparse
import os
import cmd
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.core.utility import utility
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.dagger.module.scope006004_map import Dagger
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR


__author__ = 'yuanle@SmartGiant'
__version__ = 'V0.0.5'


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


class DaggerDebugger(cmd.Cmd):
    prompt = 'dagger>'
    intro = 'Mix dagger debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.dagger.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s
        Dagger reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.dagger.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version
        Get Dagger driver version.
        eg.         get_driver_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.dagger.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = eval(line)
        result = self.dagger.get_sampling_rate(line)
        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_measure_enable(self, line):
        '''multi_points_measure_enable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = eval(line)
        self.dagger.multi_points_measure_enable(line)
        print("Done.")

    @handle_errors
    def do_multi_points_measure_disable(self, line):
        '''multi_points_measure_disable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = eval(line)
        self.dagger.multi_points_measure_disable(line)
        print("Done.")

    @handle_errors
    def do_multi_points_voltage_measure(self, line):
        '''multi_points_voltage_measure <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = eval(line)
        result = self.dagger.multi_points_voltage_measure(line)
        print("Result:")
        print(result)

    @handle_errors
    def do_voltage_measure(self, line):
        '''voltage_measure <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = eval(line)
        result = self.dagger.voltage_measure(line)
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
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


def create_dagger_dbg(ip_name, i2c_name, ad717x_name):
    dagger_dbg = None
    if utility.is_pl_device(i2c_name):
        axi4_bus = AXI4LiteBus(i2c_name, 256)
        i2c = MIXI2CSG(axi4_bus)
    else:
        i2c = I2C(i2c_name)

    if ip_name == '':
        axi4_bus = AXI4LiteBus(ad717x_name, 0x8000)
        ad717x = MIXAd7175SG(axi4_bus, 5000)
        dagger_dbg = DaggerDebugger(Dagger(i2c, ad717x))
    else:
        axi4_bus = AXI4LiteBus(ip_name, 256)
        mix_daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_mvref=5000, use_spi=False, use_gpio=False)
        dagger_dbg = DaggerDebugger(Dagger(i2c, ipcore=mix_daqt1))
    return dagger_dbg


arguments = [
    ['-ipcore', '--ipcore', 'ipcore device name', ''],
    ['-ad', '--ad717x', 'ad717x device name', ''],
    ['-i2c', '--i2c_bus', 'i2c bus device name', ''],
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    dagger_dbg = create_dagger_dbg(args.ipcore, args.i2c_bus, args.ad717x)
    dagger_dbg.cmdloop()
