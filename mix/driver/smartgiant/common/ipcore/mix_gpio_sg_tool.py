# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG

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


class MIXGPIOSGDebuger(cmd.Cmd):
    prompt = 'gpio>'
    intro = 'Xavier gpio debug tool'

    def _set_direction(self, line):
        line = line.replace(' ', ',')
        self.gpio.set_pin_dir(*list(eval(line)))

    def _get_direction(self, line):
        return self.gpio.get_pin_dir(eval(line))

    @handle_errors
    def do_set_dir(self, line):
        '''set_dir [pin_id] [dir]'''
        self._set_direction(line)
        print('Done.')

    @handle_errors
    def do_get_dir(self, line):
        '''get_dir [pin_id]'''
        result = self._get_direction(line)
        print("Result:")
        print(result)

    @handle_errors
    def do_set_pin(self, line):
        '''set_pin [pin_id] [level]'''
        line = line.replace(' ', ',')
        self.gpio.set_pin(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_pin(self, line):
        '''get_pin [pin_id]'''
        result = self.gpio.get_pin(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_set_dir.__doc__)
        print(self.do_get_dir.__doc__)
        print(self.do_set_pin.__doc__)
        print(self.do_get_pin.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_gpio_dbg(dev_name, reg_size):
    gpio_dbg = MIXGPIOSGDebuger()
    if dev_name == '':
        gpio_dbg.gpio = MIXGPIOSGEmulator(dev_name, reg_size)
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, reg_size)
        else:
            raise NotImplementedError('PS gpio not implement yet!')
        gpio_dbg.gpio = MIXGPIOSG(axi4_bus)
    return gpio_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-s', '--size', help='device reserved memory size', default='256')
    args = parser.parse_args()

    gpio_dbg = create_gpio_dbg(args.device, int(args.size))

    gpio_dbg.cmdloop()
