# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.ic.mcp23008 import MCP23008
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MCP23008Debuger(cmd.Cmd):
    prompt = 'mcp23008>'
    intro = 'Xavier mcp23008 debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register device_address rd_len'''
        line = line.replace(' ', ',')
        data = self.mcp23008.read_register(*list(eval(line)))
        print('Result:')
        print(data)
        return

    @handle_errors
    def do_write_register(self, line):
        '''write_register register_address [data]'''
        line = line.replace(' ', ',')
        self.mcp23008.write_register(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_set_pin_dir(self, line):
        '''set_pin_dir pin_id dir'''
        line = line.replace(' ', ',')
        self.mcp23008.set_pin_dir(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin_dir(self, line):
        '''get_pin_dir pin_id'''
        result = self.mcp23008.get_pin_dir(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pin(self, line):
        '''set_pin pin_id level'''
        line = line.replace(' ', ',')
        self.mcp23008.set_pin(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin(self, line):
        '''get_pin pin_id'''
        result = self.mcp23008.get_pin(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_get_pin_state(self, line):
        '''get_pin_state pin_id'''
        result = self.mcp23008.get_pin_state(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pin_inversion(self, line):
        '''set_pin_inversion pin_id inversion'''
        line = line.replace(' ', ',')
        self.mcp23008.set_pin_inversion(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin_inversion(self, line):
        '''get_pin_inversion pin_id'''
        result = self.mcp23008.get_pin_inversion(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pins_dir(self, line):
        '''set_pins_dir [data]'''
        line = line.replace(' ', ',')
        self.mcp23008.set_pins_dir(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_pins_dir(self, line):
        '''get_pins_dir'''
        result = self.mcp23008.get_pins_dir()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_ports(self, line):
        '''set_ports [data]'''
        line = line.replace(' ', ',')
        self.mcp23008.set_ports(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_ports(self, line):
        '''get_ports'''
        result = self.mcp23008.get_ports()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_get_ports_state(self, line):
        '''get_ports_state'''
        result = self.mcp23008.get_ports_state()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_ports_inversion(self, line):
        '''set_ports_inversion [data]'''
        line = line.replace(' ', ',')
        self.mcp23008.set_ports_inversion(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_ports_inversion(self, line):
        '''get_ports_inversion'''
        result = self.mcp23008.get_ports_inversion()
        print('Result:')
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print("Usage:")
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_set_pin_dir.__doc__)
        print(self.do_get_pin_dir.__doc__)
        print(self.do_set_pin.__doc__)
        print(self.do_get_pin.__doc__)
        print(self.do_get_pin_state.__doc__)
        print(self.do_set_pin_inversion.__doc__)
        print(self.do_get_pin_inversion.__doc__)
        print(self.do_set_pins_dir.__doc__)
        print(self.do_get_pins_dir.__doc__)
        print(self.do_get_ports.__doc__)
        print(self.do_set_ports.__doc__)
        print(self.do_get_ports_state.__doc__)
        print(self.do_set_ports_inversion.__doc__)
        print(self.do_get_ports_inversion.__doc__)
        print(self.do_quit.__doc__)


def create_mcp23008_dbg(dev_name, device_address):
    mcp23008_dbg = MCP23008Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    mcp23008_dbg.mcp23008 = MCP23008(device_address, i2c_bus)
    return mcp23008_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x20')
    args = parser.parse_args()

    mcp23008_dbg = create_mcp23008_dbg(args.device, int(args.address, 16))

    mcp23008_dbg.cmdloop()
