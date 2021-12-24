# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.bus.pin import Pin
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.smartgiant.darkbeast.module.oab3001002_map import DarkBeast
from mix.driver.core.utility import utility

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1.2'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


def get_function_doc(self=None):
    '''Get function.__doc__ '''
    func_name = inspect.stack()[1][3]
    if self is None:
        return eval('%s' % func_name).__doc__
    else:
        return getattr(self, func_name).__doc__


class DarkBeastDebuger(cmd.Cmd):
    prompt = 'darkbeast>'
    intro = 'Xavier DarkBeast debug tool'

    @handle_errors
    def do_call(self, line):
        '''call function()
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = eval("self.darkbeast.{}".format(line))
        print(result)

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout'''
        self.darkbeast.post_power_on_init(eval(line))

    @handle_errors
    def do_reset(self, line):
        '''reset timeout'''
        self.darkbeast.reset(eval(line))

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout'''
        self.darkbeast.pre_power_down(eval(line))

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version'''
        print self.darkbeast.get_driver_version()

    @handle_errors
    def do_close(self, line):
        '''close'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.darkbeast.close()
        print('Done')

    @handle_errors
    def do_open(self, line):
        '''open'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.darkbeast.open()
        print(result)

    @handle_errors
    def do_communicate(self, line):
        '''communicate <cmd_string>
        <cmd_string>: 12345tfddd
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.darkbeast.communicate(line)
        print(result)

    @handle_errors
    def do_aid_connect_set(self, line):
        '''aid_connect_set <status>
        <status>: 'enable', 'disable'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.darkbeast.aid_connect_set(int(line))
        print('Done')

    @handle_errors
    def do_gpio_set(self, line):
        '''gpio_set <gpio_name> <level>
        <gpio_name>: "PULL_UP", "PULL_DOWN", "TX_EN",
                     "CONNECT_DETECTION", "REMOVAL_DETECTION"
        <level>: 0/1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.darkbeast.gpio_set(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_pin_set(self, line):
        '''pin_set <pin_name> <level>
        <pin_name>: "A0", "A1", "A2", "ELAOD_EN"
        <level>: 0/1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.darkbeast.pin_set(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_dbg(file, uart, i2c_bus_name, plgpio, pull_up_pin_num, pull_down_pin_num, tx_en_pin_num,
               removal_det_pin_num, connect_det_pin_num, a0_pin_id, a1_pin_id, a2_pin_id, elaod_en_pin_id):
    dbg = DarkBeastDebuger()

    firmware_path = file
    pl_uart_drv_ko_file = uart

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    if plgpio == '':
        gpio = None
    else:
        axi4_bus = AXI4LiteBus(plgpio, 256)
        gpio = MIXGPIOSG(axi4_bus)

    pull_up_pin = GPIO(int(pull_up_pin_num))
    pull_down_pin = GPIO(int(pull_down_pin_num))
    tx_en_pin = GPIO(int(tx_en_pin_num))
    removal_det_pin = GPIO(int(removal_det_pin_num))
    connect_det_pin = GPIO(int(connect_det_pin_num))

    cat9555 = CAT9555(0x20, i2c_bus)
    a0_pin = Pin(cat9555, a0_pin_id)
    a1_pin = Pin(cat9555, a1_pin_id)
    a2_pin = Pin(cat9555, a2_pin_id)
    elaod_en_pin = Pin(cat9555, elaod_en_pin_id)
    dbg.darkbeast = DarkBeast(firmware_path, pl_uart_drv_ko_file, i2c_bus, gpio, pull_up_pin,
                              pull_down_pin, tx_en_pin, removal_det_pin, connect_det_pin, a0_pin,
                              a1_pin, a2_pin, elaod_en_pin)
    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', help='ELF file', default='/root/HSAID_FCT.elf')
    parser.add_argument('-ko', '--uart', help='KO file', default='/root/pl_uart_drv.ko')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name', default='')
    parser.add_argument('-plgpio', '--plgpio', help='plgpio driver name', default='')
    parser.add_argument('-num1', '--pull_up_pin', help='gpio number', default='54')
    parser.add_argument('-num2', '--pull_down_pin', help='gpio number', default='55')
    parser.add_argument('-num3', '--tx_en_pin', help='gpio number', default='56')
    parser.add_argument('-num4', '--removal_det_pin', help='gpio number', default='57')
    parser.add_argument('-num5', '--connect_det_pin', help='gpio number', default='58')
    parser.add_argument('-pin0', '--a0_pin', help='pin id', default='0')
    parser.add_argument('-pin1', '--a1_pin', help='pin id', default='1')
    parser.add_argument('-pin2', '--a2_pin', help='pin id', default='2')
    parser.add_argument('-pin3', '--elaod_en_pin', help='pin id', default='6')
    args = parser.parse_args()

    dbg = create_dbg(args.file, args.uart, args.i2c, args.plgpio, args.pull_up_pin, args.pull_down_pin,
                     args.tx_en_pin, args.removal_det_pin, args.connect_det_pin,
                     args.a0_pin, args.a1_pin, args.a2_pin, args.elaod_en_pin,)

    dbg.cmdloop()
