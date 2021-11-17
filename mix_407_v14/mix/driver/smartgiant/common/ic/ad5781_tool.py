# -*- coding:utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from ad5781 import AD5781
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


__author__ = 'hongshen.wang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD5781Debuger(cmd.Cmd):
    prompt = 'ad5781>'
    intro = 'Xavier ad5781 debug tool'

    @handle_errors
    def do_write_control_register(self, line):
        '''write_control_register [data] '''
        line = line.replace(' ', ',')
        self.ad5781.write_control_register(eval(line))
        print('Done.')

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_voltage volt '''
        line = line.replace(' ', ',')
        self.ad5781.output_volt_dc(eval(line))
        print('Done.')

    @handle_errors
    def do_readback_output_voltage(self, line):
        '''readback_output_voltage '''
        line = line.replace(' ', ',')
        rd_data = self.ad5781.readback_output_voltage()
        print('Result:')
        print(rd_data)

    def do_read_register(self, line):
        '''read_register [data] eg: 0x01'''
        line = line.replace(' ', ',')
        rd_data = self.ad5781.read_register(eval(line))
        print('Result:')
        print(rd_data)

    def do_write_register(self, line):
        '''write_register [reg_addr] [reg_data] eg: 0x01 0xffff'''
        line = line.replace(' ', ',')
        self.ad5781.write_register(*eval(line))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_control_register.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_readback_output_voltage.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad5781_dbg(dev_name, mvref_p, mvref_n):
    ad5781_dbg = AD5781Debuger()
    if dev_name == '':
        spi_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            spi_bus = MIXQSPISG(axi4_bus)

    ad5781_dbg.ad5781 = AD5781(mvref_p, mvref_n, spi_bus)
    return ad5781_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-p', '--mvref_p', help='mvref_p', default='2048')
    parser.add_argument('-n', '--mvref_n', help='mvref_n', default='0')

    args = parser.parse_args()

    ad5781_dbg = create_ad5781_dbg(args.device, args.mvref_p, args.mvref_n)

    ad5781_dbg.cmdloop()
