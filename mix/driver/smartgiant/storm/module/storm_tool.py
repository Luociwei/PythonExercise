# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.storm.module.storm import Storm

__author__ = 'weiping.mo@SmartGiant'
__version__ = '1.0'


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


class StormDebuger(cmd.Cmd):
    prompt = 'storm>'
    intro = 'Xavier storm debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_read_output_voltage(self, line):
        '''read_output_voltage
        Storm measure the output voltage via the ADS1112'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.read_output_voltage()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_source_current(self, line):
        '''read_source_current
        Storm measure the source current via the ADS1112'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.read_source_current()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_sink_current(self, line):
        '''read_sink_current
        Storm measure the sink current via the ADS1112'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.read_sink_current()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_local_temperature(self, line):
        '''get_local_temperature
        Storm get the local temperature'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.get_local_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_remote_temperature(self, line):
        '''get_remote_temperature
        Storm get the remote temperature'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.get_remote_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_output_voltage(self, line):
        '''set_output_voltage
        Storm set the output voltage via The AD5696
        volt:   int/float(7.2-12.8),unit is 'V'
        eg: set_output_voltage 7.2001'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.storm.set_output_voltage(eval(line))
        print('Done.')

    @handle_errors
    def do_ft4222_enable_measure(self, line):
        '''ft4222_enable_measure
        Storm Enable measure output voltage and output current'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.storm.ft4222_enable_measure()
        print('Done.')

    @handle_errors
    def do_ft4222_measure(self, line):
        '''ft4222_measure
        Storm Measure output voltage and output current'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.ft4222_measure()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Storm enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.storm.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Storm query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.is_use_cal_data()
        print('Result:')
        print(result)

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold
        MIXBoard calibration data write
        cal_item: string('a_volt','b_volt','a_sink_curr','b_sink_curr',
                  'a_src_curr','b_src_curr'),  calibration item
        cal_value:  int/float, calibration value
        eg: write_calibration_cell 'a_volt',0.1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.storm.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        cal_item: string('a_volt','b_volt','a_sink_curr','b_sink_curr',
                  'a_src_curr','b_src_curr'),  calibration item
        eg: read_calibration_cell 'a_volt' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.storm.legacy_read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell
        MIXBoard erase calibration unit
        cal_item: string('a_volt','b_volt','a_sink_curr','b_sink_curr',
                  'a_src_curr','b_src_curr'),  calibration item
        eg: erase_calibration_cell 'a_volt' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.storm.legacy_erase_calibration_cell(eval(line))
        print("Done.")

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


def create_storm_dbg(i2c_dev_name, ft4222_gpiow_file, ft4222_spimr_file):
    storm_dbg = StormDebuger()

    if i2c_dev_name is '':
        i2c = None
    else:
        i2c_bus = AXI4LiteBus(i2c_dev_name, 256)
        i2c = MIXI2CSG(i2c_bus)

    storm_dbg.storm = Storm(i2c, ft4222_gpiow_file, ft4222_spimr_file)

    return storm_dbg


if __name__ == '__main__':
    '''
    python storm_tool.py
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-i2c', '--i2c', help='i2c bus name for storm',
                        default='/dev/AXI4_I2C_1')
    parser.add_argument('-f1', '--gpiow', help='FT4222 gpiow firmware file',
                        default='/root/FT4222-arm/dist/gpiow')
    parser.add_argument('-f2', '--spimr', help='FT4222 spimr firmware file',
                        default='/root/FT4222-arm/dist/spimr')
    args = parser.parse_args()

    storm_dbg = create_storm_dbg(args.i2c, args.gpiow, args.spimr)
    storm_dbg.cmdloop()
