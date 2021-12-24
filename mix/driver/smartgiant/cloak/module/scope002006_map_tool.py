# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.cloak.module.scope002006_map import Scope002006

__author__ = 'jiebin.zheng@SmartGiant'
__version__ = '0.1.3'


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


class Scope002006Debuger(cmd.Cmd):
    prompt = 'scope002006>'
    intro = 'Xavier scope002006 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout_s'''
        self.scope002006.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s'''
        self.scope002006.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version'''
        result = self.scope002006.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate
        Scope002006 get sampling rate of adc.
        eg: get_sampling_rate'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.get_sampling_rate()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_module_calibration(self, line):
        '''write_module_calibration calibration_vectors'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.write_module_calibration(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_sinc(self, line):
        '''set_sinc sinc'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.set_sinc(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_measure_value(self, line):
        '''read_measure_value sample_rate count
        Scope002006 measure current
        sample_rate: float, [5~250000], adc measure sampling rate, which is not continuous, default 1000.
        count: int, samples count taken for averaging. Default 1.
        eg: read_measure_value 1000 5'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.read_measure_value(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_measure_list(self, line):
        '''read_measure_list sample_rate count
        Scope002006 measure currents
        sample_rate: float, [5~250000], adc measure sampling rate, which is not continuous, default 1000.
        count: int, samples count taken for averaging. Default 1.
        eg: read_measure_list 1000 5'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.read_measure_list(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling sample_rate down_sample selection
        Scope002006 enables continuous sampling and data throughput upload to upper stream
        sample_rate: float, [5~250000], adc measure sampling rate, which is not continuous, default 1000.
        down_sample: int, down sample rate for decimation. Default 1.
        selection: string, 'max'|'min",This parameter takes effect as long as down_sample
                            is higher than 1. Default ‘max’.
        eg: enable_continuous_sampling 1000 1 'max' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.enable_continuous_sampling(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling
        Scope002006 stop continuous measure
        eg: disable_continuous_sampling '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.disable_continuous_sampling()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_continuous_sampling_statistics(self, line):
        '''read_continuous_sampling_statistics
        Scope002006 measure current in continuous mode
        count: int, [1~512], sampling numbers.
        eg: read_continuous_sampling_statistics 512 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.read_continuous_sampling_statistics(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_datalogger_start(self, line):
        '''datalogger_start
        Scope002006 set tag value for upload data
        tag: int, the value is upper 4 bits are valid, from 0x0 to 0xf.
        eg: datalogger_start 0xf '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.datalogger_start(eval(line))
        print("Done.")

    @handle_errors
    def do_datalogger_end(self, line):
        '''datalogger_end
        Scope002006 clear tag value for upload data
        eg: datalogger_end'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.datalogger_end()
        print("Done.")

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Scope002006 enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Scope002006 query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.is_use_cal_data()
        print('Result:')
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


def create_scope_dbg(axi4_bus_name, i2c_bus_name):
    scope_dbg = Scope002006Debuger()

    if 'Scope' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8000)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=2500,
                            use_spi=False, use_gpio=True)
        ad7175 = None
    else:
        daqt1 = None
        ad717x_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8192)
        ad7175 = MIXAd7175SG(ad717x_axi4_bus, 2500)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        i2c_bus = I2C(i2c_bus_name)

    scope_dbg.scope002006 = Scope002006(i2c=i2c_bus, ad7175=ad7175, ipcore=daqt1)
    return scope_dbg


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ip', help='ipcore device file name',
                        default='/dev/Scope_002_0')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name',
                        default='/dev/i2c-0')

    args = parser.parse_args()
    scope_dbg = create_scope_dbg(args.ip, args.i2c)
    scope_dbg.cmdloop()
