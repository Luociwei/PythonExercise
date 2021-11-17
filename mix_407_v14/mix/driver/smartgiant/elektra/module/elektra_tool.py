# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_ad760x_sg import MIXAd7608SG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.elektra.module.elektra import Elektra


__author__ = 'dongdongzhang@SmartGiant'
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


class ElektraDebuger(cmd.Cmd):
    prompt = 'elektra>'
    intro = 'Xavier elektra debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.module_init()
        print("Done")

    @handle_errors
    def do_read_voltage(self, line):
        '''read_voltage <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.elektra.read_voltage(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_current(self, line):
        '''read_current <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.elektra.read_current(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_cc(self, line):
        '''set_cc <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cc(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_cv(self, line):
        '''set_cv <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cv(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_cr(self, line):
        '''set_cr <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cr(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_channel_enable(self, line):
        '''channel_enable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.channel_enable(eval(line))
        print("Done.")

    @handle_errors
    def do_channel_disable(self, line):
        '''channel_disable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.channel_disable(eval(line))
        print("Done.")

    @handle_errors
    def do_reset_board(self, line):
        '''reset_board <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.reset_board(eval(line))
        print("Done.")

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell <cal_name> <unit_index> <gain> <offset> <threshold>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell <cal_name> <unit_index>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.read_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_cal_pipe(self, line):
        '''cal_pipe <cal_name> <fun_cal_info> <raw_data>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.cal_pipe(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_module_init.__doc__)
        print(self.do_read_voltage.__doc__)
        print(self.do_read_current.__doc__)
        print(self.do_set_cc.__doc__)
        print(self.do_set_cv.__doc__)
        print(self.do_set_cr.__doc__)
        print(self.do_channel_enable.__doc__)
        print(self.do_channel_disable.__doc__)
        print(self.do_reset_board.__doc__)
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_cal_pipe.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_elektra_dbg(i2c_name, spi_name, ad760x_name, gpio_name, volt_ch_1, volt_ch_2, curr_ch_1, curr_ch_2):
    scope_dbg = ElektraDebuger()
    if i2c_name == '':
        i2c_bus = None
    else:
        axi4_bus = AXI4LiteBus(i2c_name, 256)
        i2c_bus = MIXI2CSG(axi4_bus)

    if spi_name == '':
        spi_bus = None
    else:
        axi4_bus = AXI4LiteBus(spi_name, 8192)
        spi_bus = MIXQSPISG(axi4_bus)

    if ad760x_name == '':
        ad7608_ip = None
    else:
        axi4 = AXI4LiteBus(ad760x_name, 8192)
        ad7608_ip = MIXAd7608SG(axi4)

    if gpio_name == '':
        gpio_bus = None
    else:
        axi4 = AXI4LiteBus(gpio_name, 256)
        gpio_bus = MIXGPIOSG(axi4)

    volt_1 = int(volt_ch_1)
    volt_2 = int(volt_ch_2)
    curr_1 = int(curr_ch_1)
    curr_2 = int(curr_ch_2)
    scope_dbg.elektra = Elektra(i2c=i2c_bus, spi=spi_bus, ad7608=ad7608_ip, gpio=gpio_bus,
                                volt_ch1=volt_1, volt_ch2=volt_2, curr_ch1=curr_1, curr_ch2=curr_2)
    return scope_dbg


arguments = [
    ['-i2c', '--i2c_bus', 'i2c bus device name', ''],
    ['-spi', '--spi_bus', 'spi bus device name', ''],
    ['-ip', '--ad760x', 'ad760x device name', ''],
    ['-gpio', '--gpio', 'gpio device name', ''],
    ['-volt_ch1', '--volt_1', 'adc channel id', ''],
    ['-volt_ch2', '--volt_2', 'adc channel id', ''],
    ['-curr_ch1', '--curr_1', 'adc channel id', ''],
    ['-curr_ch2', '--curr_2', 'adc channel id', ''],
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    elektra_dbg = create_elektra_dbg(args.i2c_bus, args.spi_bus, args.ad760x, args.gpio,
                                     args.volt_1, args.volt_2, args.curr_1, args.curr_2)
    elektra_dbg.cmdloop()
