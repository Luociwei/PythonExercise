# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ic.ad5592r import AD5592R


__author__ = 'yongjiu@SmartGiant'
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


class AD5592RDebuger(cmd.Cmd):
    prompt = 'AD5592R>'
    intro = 'Xavier ad5592r debug tool'

    @handle_errors
    def do_reset(self, line):
        '''reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad5592r.reset()
        print('Done')

    @handle_errors
    def do_spi_write(self, line):
        '''spi_write <value>
        <value>:0~0xFFFF
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad5592r.spi_write(eval(line))
        print('Done')

    @handle_errors
    def do_spi_read(self, line):
        '''spi_read'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad5592r.spi_read()
        print('{}'.format(result))

    @handle_errors
    def do_register_write(self, line):
        '''register_write <register> <value>
        <register>:0~15
        <value>:0~0x7FF
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.register_write(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_register_read(self, line):
        '''register_read <register>
        <register>:0~15
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad5592r.register_read(eval(line))
        print('{}'.format(result))

    @handle_errors
    def do_reference_get(self, line):
        '''reference_get'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad5592r.reference
        print('{}'.format(result))

    @handle_errors
    def do_reference_set(self, line):
        '''reference_set <mode>
        <mode>:"internal", "external"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad5592r.reference = line
        print('Done')

    @handle_errors
    def do_gain_set(self, line):
        '''gain_set <adc_gain> <dac_gain>
        <adc_gain>:0 or 1
        <dac_gain>:0 or 1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.gain_set(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_channel_config(self, line):
        '''channel_config <channel> <mode>
        <channel>:0~7
        <mode>:"DAC", "ADC", "INPUT", "OUTPUT
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.channel_config(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc <channel> <volt>
        <channel>:0~7
        <volt>:0~5000
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.output_volt_dc(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt <channel>
        <channel>:0~7
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad5592r.read_volt(eval(line))
        print('{}'.format(result))

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_bus(dev_name, bus_type):
    if dev_name == '':
        return None

    if bus_type == 'i2c':
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            bus = MIXI2CSG(axi4_bus)
        else:
            bus = I2C(dev_name)
    elif bus_type == 'spi':
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            bus = MIXQSPISG(axi4_bus)
        else:
            raise NotImplementedError('PS SPI not implement yet!')
    return bus


def create_dbg(dev_name):
    dbg = AD5592RDebuger()

    bus = create_bus(dev_name, 'spi')

    mvref = 2500
    ref_mode = 'internal'
    adc_gain = 2
    dac_gain = 2

    dbg.ad5592r = AD5592R(bus, mvref, ref_mode, adc_gain, dac_gain)
    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/MIX_QSPI_1')
    args = parser.parse_args()

    dbg = create_dbg(args.device)

    dbg.cmdloop()
