# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.utility.utility import utility
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.elektra.module.el004002a_map import EL004002A
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG


__author__ = 'dongdongzhang@SmartGiant'
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


class ElektraDebuger(cmd.Cmd):
    prompt = 'elektra>'
    intro = 'Xavier elektra debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s
        Elektra reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout_s
        Elektra reset the instrument module to a know hardware state.
        eg:           do_pre_power_down
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.pre_power_down(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version
        Get Elektra driver version.
        eg.         get_driver_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.elektra.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_voltage(self, line):
        '''read_voltage <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.elektra.read_voltage(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_current(self, line):
        '''read_current <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.elektra.read_current(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_cc(self, line):
        '''set_cc <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cc(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_cv(self, line):
        '''set_cv <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cv(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_cr(self, line):
        '''set_cr <channel> <value>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.elektra.set_cr(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_channel_enable(self, line):
        '''channel_enable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.channel_enable(eval(line))
        print("Done.")

    @handle_errors
    def do_channel_disable(self, line):
        '''channel_disable <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.channel_disable(eval(line))
        print("Done.")

    @handle_errors
    def do_reset_board(self, line):
        '''reset_board <channel>'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.elektra.reset_board(eval(line))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_elektra_dbg(i2c_name, spi_name, ad717x_name, gpio_id, ipcore_name):
    scope_dbg = ElektraDebuger()
    if i2c_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_name):
            axi4_bus = AXI4LiteBus(i2c_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_name)

    if spi_name == '':
        spi_bus = None
    else:
        axi4_bus = AXI4LiteBus(spi_name, 8192)
        spi_bus = MIXQSPISG(axi4_bus)

    ipcore = None
    ad7175 = None
    vref = 5000
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        ipcore = MIXDAQT1SGR(axi4_bus, ad717x_mvref=vref, use_spi=True, use_gpio=False)
    elif ad717x_name != '':
        axi4_bus = AXI4LiteBus(ad717x_name, 256)
        ad7175 = MIXAd7175SG(axi4_bus, vref)

    if gpio_id == '':
        gpio_bus = None
    else:
        io = GPIO(gpio_id, "output")
        gpio_bus = Pin(io, gpio_id, "output")

    scope_dbg.elektra = EL004002A(i2c=i2c_bus, spi=spi_bus, ad7175=ad7175, gpio=gpio_bus, ipcore=ipcore)
    return scope_dbg


arguments = [
    ['-i2c', '--i2c_bus', 'i2c bus device name', ''],
    ['-spi', '--spi_bus', 'spi bus device name', ''],
    ['-ad7175', '--ad717x', 'ad717x device name', ''],
    ['-gpio', '--gpio', 'gpio id', ''],
    ['-ipcore', '--MIX_DAQT1_0', 'MIX_DAQT1_0 device name', '']
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    elektra_dbg = create_elektra_dbg(args.i2c_bus, args.spi_bus, args.ad717x,
                                     args.gpio, args.MIX_DAQT1_0)
    elektra_dbg.cmdloop()
