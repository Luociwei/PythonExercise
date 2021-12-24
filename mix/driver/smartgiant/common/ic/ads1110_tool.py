# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ads1110 import ADS1110
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


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


class ADS1110Debuger(cmd.Cmd):
    prompt = 'ads1110>'
    intro = 'Xavier ads1110 debug tool'

    @handle_errors
    def do_initial(self, line):
        '''initial data_rate gain_set'''
        line = line.replace(' ', ',')
        self.ads1110.initial(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt'''
        result = self.ads1110.read_volt()
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_initial.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ads1110_dbg(dev_name, dev_addr):
    ads1110_dbg = ADS1110Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    ads1110_dbg.ads1110 = ADS1110(dev_addr, i2c_bus)
    return ads1110_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x48')
    args = parser.parse_args()
    ads1110_dbg = create_ads1110_dbg(args.device, int(args.address, 16))

    ads1110_dbg.cmdloop()
