# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.adcxx1c0xx import ADC121C021
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class ADC121C021Debuger(cmd.Cmd):
    prompt = 'adc121c021>'
    intro = 'xavier adc121c021 debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register [address] [length] eg:0x01 2'''
        line = line.replace(' ', ',')
        rd_data = self.adc121c021.read_register(*eval(line))
        print(rd_data)

    @handle_errors
    def do_write_register(self, line):
        '''write_register [address] [data_list]eg: 0x02 [0x12,0x23]'''
        line = line.replace(' ', ',')
        self.adc121c021.write_register(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt [channel]'''
        result = self.adc121c021.read_volt(eval(line))
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_adc121c021_dbg(dev_name, vref, dev_addr):
    adc121c021_dbg = ADC121C021Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    adc121c021_dbg.adc121c021 = ADC121C021(dev_addr, vref, i2c_bus)
    return adc121c021_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-v', '--vref', help='vref', default='3300')
    parser.add_argument('-a', '--address', help='device address',
                        default='0x54')

    args = parser.parse_args()
    adc121c021_dbg = create_adc121c021_dbg(args.device, args.vref,
                                           int(args.address, 16))

    adc121c021_dbg.cmdloop()
