# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ad527x import AD5272
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.bus.axi4_lite_def import PLI2CDef

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD5272Debuger(cmd.Cmd):
    prompt = 'AD5272>'
    intro = 'Xavier AD5272 debug tool'

    @handle_errors
    def do_write_command(self, line):
        '''write_command command data'''
        line = line.replace(' ', ',')
        self.ad5272.write_command(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_read_command(self, line):
        '''read_command command'''
        line = line.replace(' ', ',')
        ret = self.ad5272.read_command(eval(line))
        print(ret)

    @handle_errors
    def do_get_resistor(self, line):
        '''get_resistor'''
        ret = self.ad5272.get_resistor()
        print(ret)

    @handle_errors
    def do_set_resistor(self, line):
        '''set_resistor resistor(float)'''
        line = line.replace(' ', ',')
        self.ad5272.set_resistor(eval(line))
        print('Done')

    @handle_errors
    def do_set_work_mode(self, line):
        '''set_work_mode work_mode('shutdown'|'normal')'''
        line = line.replace(' ', ',')
        self.ad5272.set_work_mode(eval(line))
        print('Done')

    @handle_errors
    def do_set_control_register(self, line):
        '''set_control_register reg_data'''
        line = line.replace(' ', ',')
        self.ad5272.set_control_register(eval(line))
        print('Done')

    @handle_errors
    def do_get_control_register(self, line):
        '''get_control_register'''
        ret = self.ad5272.get_control_register()
        print(ret)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_command.__doc__)
        print(self.do_read_command.__doc__)
        print(self.do_get_resistor.__doc__)
        print(self.do_set_resistor.__doc__)
        print(self.do_set_work_mode.__doc__)
        print(self.do_set_control_register.__doc__)
        print(self.do_get_control_register.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad5272_dbg(dev_name, dev_addr):
    ad5272_dbg = AD5272Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    ad5272_dbg.ad5272 = AD5272(dev_addr, i2c_bus)
    return ad5272_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x2C')
    args = parser.parse_args()
    ad5272_dbg = create_ad5272_dbg(args.device, int(args.address, 16))

    ad5272_dbg.cmdloop()
