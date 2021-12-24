# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.smartgiant.common.ic.ad5676 import AD5676

__author__ = 'TangentLin@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class Ad5676Debuger(cmd.Cmd):
    prompt = 'ad5676>'
    intro = 'Xavier ad5676 debug tool'

    @handle_errors
    def do_set_mode(self, line):
        '''set_mode channel(0-7) mode('normal','ground','tristate')'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad5676.set_mode(line[0], line[1])
        print('Done.')

    @handle_errors
    def do_set_gain(self, line):
        '''set_gain gain(1-2)'''
        self.ad5676.set_gain(eval(line))
        print('Done.')

    @handle_errors
    def do_read_gain(self, line):
        '''read_gain'''
        gain_value = self.ad5676.get_gain()
        print('Gain: ' + str(gain_value))

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc channel(0-7) volt'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad5676.output_volt_dc(line[0], line[1])
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
        print(self.do_read_gain.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bus(dev_name):
    if dev_name == '':
        return None

    if utility.is_pl_device(dev_name):
        axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
        bus = MIXQSPISG(axi4_bus)
        bus.mode = 'MODE2'
    else:
        raise NotImplementedError('PS SPI not implement yet!')
    return bus


def create_ad5676(bus, vref):
    ad5676 = AD5676(bus, vref)
    return ad5676


def create_ad5676_dbg(dev_name, vref):
    ad5676_dbg = Ad5676Debuger()
    bus = create_bus(dev_name)
    ad5676_dbg.ad5676 = create_ad5676(bus, vref)
    return ad5676_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-v', '--vref', help='voltage reference', default='2500')

    args = parser.parse_args()

    ad5676_dbg = create_ad5676_dbg(args.device, int(args.vref))

    ad5676_dbg.cmdloop()
