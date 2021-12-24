# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from ..bus.pl_i2c_bus import PLI2CBus
from ..bus.i2c import I2C
from ..bus.axi4_lite_def import PLI2CDef
from pca9554 import PCA9554
from ..utility import utility
from ..bus.axi4_lite_bus import AXI4LiteBus


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class PCA9554Debuger(cmd.Cmd):
    prompt = 'pca9554>'
    intro = 'Xavier pca9554 debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register device_address rd_len'''
        line = line.replace(' ', ',')
        data = self.pca9554.read_register(*list(eval(line)))
        print('Result:')
        print(data)
        return

    @handle_errors
    def do_write_register(self, line):
        '''write_register register_address [data]'''
        line = line.replace(' ', ',')
        self.pca9554.write_register(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_set_pin_dir(self, line):
        '''set_pin_dir pin_id dir'''
        line = line.replace(' ', ',')
        self.pca9554.set_pin_dir(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin_dir(self, line):
        '''get_pin_dir pin_id'''
        result = self.pca9554.get_pin_dir(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pin(self, line):
        '''set_pin pin_id level'''
        line = line.replace(' ', ',')
        self.pca9554.set_pin(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin(self, line):
        '''get_pin pin_id'''
        result = self.pca9554.get_pin(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_get_pin_state(self, line):
        '''get_pin_state pin_id'''
        result = self.pca9554.get_pin_state(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pin_inversion(self, line):
        '''set_pin_inversion pin_id inversion'''
        line = line.replace(' ', ',')
        self.pca9554.set_pin_inversion(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_pin_inversion(self, line):
        '''get_pin_inversion pin_id'''
        result = self.pca9554.get_pin_inversion(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pins_dir(self, line):
        '''set_pins_dir [data]'''
        line = line.replace(' ', ',')
        self.pca9554.set_pins_dir(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_pins_dir(self, line):
        '''get_pins_dir'''
        result = self.pca9554.get_pins_dir()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_ports(self, line):
        '''set_ports [data]'''
        line = line.replace(' ', ',')
        self.pca9554.set_ports(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_ports(self, line):
        '''get_ports'''
        result = self.pca9554.get_ports()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_get_ports_state(self, line):
        '''get_ports_state'''
        result = self.pca9554.get_ports_state()
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_ports_inversion(self, line):
        '''set_ports_inversion [data]'''
        line = line.replace(' ', ',')
        self.pca9554.set_ports_inversion(eval(line))
        print('Done')
        return

    @handle_errors
    def do_get_ports_inversion(self, line):
        '''get_ports_inversion'''
        result = self.pca9554.get_ports_inversion()
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


def create_pca9554_dbg(dev_name, device_address):
    pca9554_dbg = PCA9554Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    pca9554_dbg.pca9554 = PCA9554(device_address, i2c_bus)
    return pca9554_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x3c')
    args = parser.parse_args()

    pca9554_dbg = create_pca9554_dbg(args.device, int(args.address, 16))

    pca9554_dbg.cmdloop()
