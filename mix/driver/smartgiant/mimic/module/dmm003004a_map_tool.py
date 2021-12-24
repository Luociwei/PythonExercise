# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.mimic.module.dmm003004a_map import DMM003004A


__author__ = 'tufeng.mao@SmartGiant'
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


class DMM003004ADebuger(cmd.Cmd):
    prompt = 'dmm003004A>'
    intro = 'Xavier dmm003004A debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.dmm003004A.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s
        Mimic reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.dmm003004A.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version
        Get Mimic driver version.
        eg.         get_driver_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.dmm003004A.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel rate'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.dmm003004A.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.dmm003004A.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path channel range'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.dmm003004A.set_measure_path(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.get_measure_path()
        print(result)

    @handle_errors
    def do_dc_voltage_measure(self, line):
        '''dc_voltage_measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.dc_voltage_measure(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_ac_voltage_measure(self, line):
        '''ac_voltage_measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.ac_voltage_measure(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_continuous_measure(self, line):
        '''continuous_measure count'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.continuous_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_resistor_measure(self, line):
        '''resistor_measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.resistor_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_diode_measure(self, line):
        '''diode_measure'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.dmm003004A.diode_voltage_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.dmm003004A.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr data'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.dmm003004A.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.dmm003004A.get_temperature()
        print("%f" % result)

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


def create_dmm003004A_dbg(ipcore_name, vref, i2c_bus_name):
    dmm003004A_dbg = DMM003004ADebuger()
    daqt1 = None
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_chip='AD7175', ad717x_mvref=vref, use_spi=False, use_gpio=False)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    dmm003004A_dbg.dmm003004A = DMM003004A(i2c_bus, daqt1)
    dmm003004A_dbg.dmm003004A.post_power_on_init()
    return dmm003004A_dbg


if __name__ == '__main__':
    '''
    ***measure single voltage/current step:
        1.set_measure_path
        2.measure single voltage/current
    ***measure continue voltage/current step:
        1.set_measure_path
        2.enable_continuous_measure
        3.measure continue voltage/current
    ***when from continue mode to single mode,you have to stop_continuous_measure first.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ipcore', help='ipcore devcie name',
                        default='')
    parser.add_argument('-v', '--vref', help='ad7175 reference',
                        default='2500')
    parser.add_argument('-i2c', '--i2c', help='cat9555 i2c bus name',
                        default='')

    args = parser.parse_args()
    dmm003004A_dbg = create_dmm003004A_dbg(args.ipcore, args.vref, args.i2c)

    dmm003004A_dbg.cmdloop()
