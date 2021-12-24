# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.bus.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.ic.ad5592r import AD5592R
from mix.driver.smartgiant.darkbeastf.module.darkbeastf import DarkBeastF

__author__ = 'dongdong.zhang@SmartGiant'
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


class DarkBeastFDebuger(cmd.Cmd):
    prompt = 'darkbeastf>'
    intro = 'Xavier DarkBeastF debug tool'

    @handle_errors
    def do_call(self, line):
        '''call function()
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = eval("self.darkbeastf.{}".format(line))
        print(result)

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.darkbeastf.module_init()
        print('Done')

    @handle_errors
    def do_close(self, line):
        '''close'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.darkbeastf.close()
        print('Done')

    @handle_errors
    def do_open(self, line):
        '''open'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.darkbeastf.open()
        print('Done')

    @handle_errors
    def do_communicate(self, line):
        '''communicate <cmd_string>
        <cmd_string>: 12345tfddd
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.darkbeastf.communicate(line)
        print(result)

    @handle_errors
    def do_aid_connect_set(self, line):
        '''aid_connect_set <status>
        <status>: 'enable', 'disable'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.darkbeastf.aid_connect_set(int(line))
        print('Done')

    @handle_errors
    def do_set_orion_volt(self, line):
        '''set_orion_volt <volt>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.darkbeastf.set_orion_volt(eval(line))
        print('Done')

    @handle_errors
    def do_set_eload_current(self, line):
        '''set_eload_current <current>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.darkbeastf.set_eload_current(eval(line))
        print('Done')

    @handle_errors
    def do_read_eload_current(self, line):
        '''read_eload_current'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.darkbeastf.read_eload_current()
        print(result)

    @handle_errors
    def do_read_orion_volt(self, line):
        '''read_orion_volt'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.darkbeastf.read_orion_volt()
        print(result)

    @handle_errors
    def do_read_orion_current(self, line):
        '''read_orion_current'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.darkbeastf.read_orion_current()
        print(result)

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell <cal_name> <unit_index>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.darkbeastf.read_calibration_cell(*list(eval(line)))
        print(result)

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell <cal_name> <unit_index> <gain> <offset> <threshold>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.darkbeastf.write_calibration_cell(*list(eval(line)))
        print('Done')

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


def create_dbg(file, gpio_number, spi_bus_name, adc_channel,
               i2c_bus_name, uart_drv, ad5667r_drv):
    dbg = DarkBeastFDebuger()

    firmware_path = file
    aid_connect = GPIO(int(gpio_number))

    if spi_bus_name == '':
        ad5592r = None
    else:
        axi4_bus = AXI4LiteBus(spi_bus_name, 256)
        spi_bus = MIXQSPISG(axi4_bus)
        ad5592r = AD5592R(spi_bus, 2500, 'internal', 1, 2)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    pl_uart_drv_ko_file = uart_drv
    ad5667r_drv_ko_file = ad5667r_drv
    dbg.darkbeastf = DarkBeastF(firmware_path, aid_connect, ad5592r, adc_channel,
                                i2c_bus, pl_uart_drv_ko_file, ad5667r_drv_ko_file)
    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='ELF file', default='/root/AID_OAB3_FATP_v1_0_12_DOE8.elf')
    parser.add_argument('-n0', '--gpio_number', help='GPIO number', default='59')
    parser.add_argument('-spi', '--spi', help='spi bus name', default='')
    parser.add_argument('-ch', '--adc_channel', help='ad5592r channel', default='7')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name', default='')
    parser.add_argument('-uart', '--uart_drv', help='uart drive .ko file',
                        default='/mix/driver/module/pl_uart_drv.ko')
    parser.add_argument('-dac', '--ad5667r_drv', help='ad5667r drive .ko file',
                        default='/mix/driver/module/ad5064.ko')
    args = parser.parse_args()

    dbg = create_dbg(args.file, args.gpio_number, args.spi, args.adc_channel,
                     args.i2c, args.uart_drv, args.ad5667r_drv)

    dbg.cmdloop()
