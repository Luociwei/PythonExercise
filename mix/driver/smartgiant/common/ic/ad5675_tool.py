# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.ic.ad5675 import AD5675

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


class AD5675Debuger(cmd.Cmd):
    prompt = 'ad5675>'
    intro = 'Xavier ad5675 debug tool'

    @handle_errors
    def do_set_mode(self, line):
        '''set_mode channel(0-7) mode('normal','ground','tristate')'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad5675.set_mode(line[0], line[1])
        print('Done.')

    @handle_errors
    def do_set_gain(self, line):
        '''set_gain gain(1-2)'''
        self.ad5675.set_gain(eval(line))
        print('Done.')

    @handle_errors
    def do_get_gain(self, line):
        '''get_gain'''
        gain_value = self.ad5675.get_gain()
        print('Gain: ' + str(gain_value))

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc channel(0-7) volt'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad5675.output_volt_dc(line[0], line[1])
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_set_mode.__doc__)
        print(self.do_set_gain.__doc__)
        print(self.do_get_gain.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bus(dev_name):
    if dev_name == '':
        return None

    if utility.is_pl_device(dev_name):
        axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
        i2c_bus = MIXI2CSG(axi4_bus)
    else:
        i2c_bus = I2C(dev_name)
    return i2c_bus


def create_ad5675(bus, vref):
    ad5675 = AD5675(bus, vref)
    return ad5675


def create_ad5675_dbg(dev_name, dev_addr, vref):
    ad5675_dbg = AD5675Debuger()
    i2c_bus = create_bus(dev_name)
    ad5675_dbg.ad5675 = AD5675(dev_addr, i2c_bus, vref)
    return ad5675_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x0C')
    parser.add_argument('-v', '--vref', help='voltage reference', default='2500')
    args = parser.parse_args()
    ad5675_dbg = create_ad5675_dbg(args.device, int(args.address, 16), int(args.vref))
    ad5675_dbg.cmdloop()
