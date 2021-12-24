# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.usbc001.module.usbc001001 import USBC001001
from mix.driver.smartgiant.common.ic.tps6598x.tps6598x import TPS6598x


__author__ = 'jionghao@SmartGiant'
__version__ = '0.2'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class USBCBoardDebugger(cmd.Cmd):
    prompt = 'usbc>'
    intro = 'UABCBoard debug tool'

    @handle_errors
    def do_usbc_option(self, line):
        '''usbc_reset [chip_id] [option_name]'''
        self.usbc.usbc_reset(eval(line))
        print("Done.")

    @handle_errors
    def do_usbc_get_pin(self, line):
        '''usbc_get_pin [chip_id] [bit_number_list]'''
        line = line.replace(' ', ',')
        result = self.usbc.usbc_get_pin(*list(eval(line)))
        print("Usage:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print("Usage:")
        print(self.do_usbc_option.__doc__)
        print(self.do_usbc_get_pin.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bus(dev_name):
    axi4_bus = AXI4LiteBus(dev_name, 256)
    i2c_bus = MIXI2CSG(axi4_bus)
    return i2c_bus


def create_usbcboard_dbg(dev_name, device_address_0, device_address_1):
    usbcboard_dbg = USBCBoardDebugger()
    i2c_bus = create_bus(dev_name)
    tps6598x_0 = TPS6598x(device_address_0, i2c_bus)
    tps6598x_1 = TPS6598x(device_address_1, i2c_bus)
    usbcboard_dbg.usbc = USBC001001(tps6598x_0, tps6598x_1)
    return usbcboard_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-addr_0', '--device_address_0', help='usbc device address_0', default='0x38')
    parser.add_argument('-addr_1', '--device_address_1', help='usbc device address_1', default='0x39')
    args = parser.parse_args()

    usbcboard_dbg = create_usbcboard_dbg(args.device, int(args.device_address_0, 16), int(args.device_address_1, 16))

    usbcboard_dbg.cmdloop()
