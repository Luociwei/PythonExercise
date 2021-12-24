# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.moonstar.module.dmm007001_map import DMM007001

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = 'V0.0.1'


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


class MoonstarDebuger(cmd.Cmd):
    prompt = 'moonstar>'
    intro = 'Mix moonstar debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        if line:
            timeout = eval(line)
        else:
            timeout = 0
        print(self.moonstar.post_power_on_init(timeout))

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s
        Mimic reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        if line:
            timeout = eval(line)
        else:
            timeout = 0
        print(self.moonstar.reset(timeout))

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version
        Get Mimic driver version.
        eg.         get_driver_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate rate'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.moonstar.set_sampling_rate(eval(line)))

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.get_sampling_rate()
        print("Result:")
        print(result)

    @handle_errors
    def do_configure_channel(self, line):
        '''configure_channel channel type max_expected_value'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.moonstar.configure_channel(*list(eval(line))))

    @handle_errors
    def do_get_channel_configuration(self, line):
        '''get_channel_configuration channel'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.get_channel_configuration(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read(self, line):
        '''read channels samples_per_channel timeout'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        line = eval(line)
        if not isinstance(line, tuple):
            line = (line,)
        result = self.moonstar.read(*list(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling channels sample_rate down_sample selection'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        line = eval(line)
        if not isinstance(line, tuple):
            line = (line,)
        result = self.moonstar.enable_continuous_sampling(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.disable_continuous_sampling(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_disable_calibration(self, line):
        '''disable_calibration'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.moonstar.disable_calibration())

    @handle_errors
    def do_enable_calibration(self, line):
        '''enable_calibration calibration_cell_index'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.moonstar.enable_calibration(eval(line)))

    @handle_errors
    def do_get_active_calibration_index(self, line):
        '''get_active_calibration_index'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.get_active_calibration_index()
        print("Results:")
        print(result)

    @handle_errors
    def do_temperature(self, line):
        '''temperature'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.moonstar.get_temperature()
        print("Results:")
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


def create_moonstar_dbg(ipcore_name, i2c_bus_name):
    moonstar_dbg = MoonstarDebuger()

    axi4_bus = AXI4LiteBus(ipcore_name, 9548)
    daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_chip='AD7175', use_spi=False, use_gpio=False)

    if utility.is_pl_device(i2c_bus_name):
        axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
        i2c_bus = MIXI2CSG(axi4_bus)
    else:
        i2c_bus = I2C(i2c_bus_name)

    moonstar_dbg.moonstar = DMM007001(i2c_bus, daqt1)
    moonstar_dbg.moonstar.post_power_on_init()
    return moonstar_dbg


if __name__ == '__main__':
    '''
    ***measure single voltage/current step:
        1.set_measure_path
        2.measure single voltage/current
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ipcore', help='ipcore devcie name', default='')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name', default='')

    args = parser.parse_args()
    moonstar_dbg = create_moonstar_dbg(args.ipcore, args.i2c)

    moonstar_dbg.cmdloop()
