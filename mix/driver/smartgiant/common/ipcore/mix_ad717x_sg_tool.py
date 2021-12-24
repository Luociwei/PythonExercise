# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import *
from mix.driver.smartgiant.common.utility import utility

__author__ = 'jiasheng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MIXAD717XSGDebuger(cmd.Cmd):
    prompt = 'ad717x>'
    intro = 'Xavier ad717x debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register reg_addr '''
        line = line.replace(' ', ',')
        data = self.ad717x.read_register(eval(line))
        print('Result:')
        print(data)
        return

    @handle_errors
    def do_write_register(self, line):
        '''write_register register_address data'''
        line = line.replace(' ', ',')
        self.ad717x.write_register(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_set_sinc(self, line):
        '''set_sinc channel sinc '''
        line = line.replace(' ', ',')
        self.ad717x.set_sinc(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel sampling_rate '''
        line = line.replace(' ', ',')
        self.ad717x.set_sampling_rate(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.ad717x.get_sampling_rate(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt channel'''
        result = self.ad717x.read_volt(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_is_communication_ok(self, line):
        '''is_communication_ok'''
        self.ad717x.is_communication_ok()
        print('Done')
        return

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling channel sampling_rate '''
        line = line.replace(' ', ',')
        self.ad717x.enable_continuous_sampling(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling'''
        self.ad717x.disable_continuous_sampling()
        print('Done')
        return

    @handle_errors
    def do_get_continuous_sampling_voltage(self, line):
        '''get_continuous_sampling_voltage channel count'''
        line = line.replace(' ', ',')
        result = self.ad717x.get_continuous_sampling_voltage(*list(eval(line)))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print("Usage:")
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_set_sinc.__doc__)
        print(self.do_set_sampling_rate.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_is_communication_ok.__doc__)
        print(self.do_enable_continuous_sampling.__doc__)
        print(self.do_disable_continuous_sampling.__doc__)
        print(self.do_get_continuous_sampling_voltage.__doc__)
        print(self.do_quit.__doc__)


def create_ad717x_dbg(chip_type, dev_name, vref):
    vref = int(vref)
    ad717x_dbg = MIXAd717xSGDebuger()
    if dev_name == '':
        axi4_bus = None
    else:
        if utility.is_pl_device(dev_name):
            # print("this is ok")
            axi4_bus = AXI4LiteBus(dev_name, 9548)
    chip_class = eval("MIX{}SG".format(chip_type))
    ad717x_dbg.ad717x = chip_class(axi4_bus, vref)
    return ad717x_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--type', help='chip type', default='Ad7175')
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-v', '--vref', help='device reference voltage', default=2500)
    args = parser.parse_args()

    ad717x_dbg = create_ad717x_dbg(args.type, args.device, args.vref)

    ad717x_dbg.cmdloop()
