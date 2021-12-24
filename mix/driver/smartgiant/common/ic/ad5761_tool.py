# -*- coding:utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ad57x1r import AD5761
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


__author__ = 'zijian.xu@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD5761Debuger(cmd.Cmd):
    prompt = 'ad5761>'
    intro = 'Xavier ad5761 debug tool'

    @handle_errors
    def do_write_control_register(self, line):
        '''write_control_register [data] '''
        line = line.replace(' ', ',')
        self.ad5761.write_control_register(eval(line))
        print('Done.')

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_voltage None volt '''
        line = line.replace(' ', ',')
        self.ad5761.output_volt_dc(eval(line))
        print('Done.')

    @handle_errors
    def do_readback_output_voltage(self, line):
        '''readback_output_voltage '''
        line = line.replace(' ', ',')
        rd_data = self.ad5761.readback_output_voltage()
        print('Result:')
        print(rd_data)

    def do_read_register(self, line):
        '''read_register [data] eg: 0x01'''
        line = line.replace(' ', ',')
        rd_data = self.ad5761.read_register(eval(line))
        print('Result:')
        print(rd_data)

    def do_write_register(self, line):
        '''write_register [reg_addr] [reg_data] eg: 0x01 0xffff'''
        line = line.replace(' ', ',')
        self.ad5761.write_register(*eval(line))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_control_register.__doc__)
        print(self.do_output_voltage.__doc__)
        print(self.do_readback_output_voltage.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad5761_dbg(dev_name, vref):
    ad5761_dbg = AD5761Debuger()
    if dev_name == '':
        spi_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            spi_bus = MIXQSPISG(axi4_bus)

    ad5761_dbg.ad5761 = AD5761(vref, spi_bus)
    return ad5761_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-v', '--vref', help='vref', default='2500')
    args = parser.parse_args()

    ad5761_dbg = create_ad5761_dbg(args.device, args.vref)

    ad5761_dbg.cmdloop()
