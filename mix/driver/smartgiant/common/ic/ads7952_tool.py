# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.ic.ads7952 import ADS7952
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


__author__ = 'zhen@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class ADS7952Debuger(cmd.Cmd):
    prompt = 'ads7952>'
    intro = 'Xavier ads7952 debug tool'

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt [channel]'''
        line = line.replace(' ', ',')
        print(self.ads7952.read_volt(eval(line)))
        return

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_q(self, line):
        '''q'''
        return self.do_quit(line)

    @handle_errors
    def do_h(self, line):
        '''h'''
        self.do_help(line)
        return

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_read_volt.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_q.__doc__)
        print(self.do_help.__doc__)
        print(self.do_h.__doc__)
        return


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


def create_ads7952_dbg(dev_name, bus_type, vref):
    ads7952_dbg = ADS7952Debuger()
    if dev_name == '':
        bus = None
    else:
        bus = create_bus(dev_name, bus_type)

    ads7952_dbg.ads7952 = ADS7952(bus, vref)
    return ads7952_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    print(parser)
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-b', '--bus_type', help='bus type', default='spi')
    parser.add_argument('-v', '--verf', help='reference voltage', default='5000')
    args = parser.parse_args()
    ads7952_dbg = create_ads7952_dbg(args.device, args.bus_type, int(args.verf))
    ads7952_dbg.cmdloop()
