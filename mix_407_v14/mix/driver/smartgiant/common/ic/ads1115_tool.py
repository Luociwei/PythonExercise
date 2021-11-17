# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ads1115 import ADS1115
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class ADS1115Debuger(cmd.Cmd):
    prompt = 'ads1115>'
    intro = 'Xavier ads1115 debug tool'

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel rate'''
        line = line.replace(' ', ',')
        self.ads1115.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.ads1115.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt channel'''
        line = line.replace(' ', ',')
        result = self.ads1115.read_volt(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_read_volt.__doc__)
        print(self.do_set_sampling_rate.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ads1115_dbg(dev_name, dev_addr):
    ads1115_dbg = ADS1115Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    ads1115_dbg.ads1115 = ADS1115(dev_addr, i2c_bus)
    return ads1115_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x48')
    args = parser.parse_args()
    ads1115_dbg = create_ads1115_dbg(args.device, int(args.address, 16))

    ads1115_dbg.cmdloop()
