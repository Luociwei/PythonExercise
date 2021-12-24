# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ic.ad569x import AD569X
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


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


class AD569XDebuger(cmd.Cmd):
    prompt = 'ad569x>'
    intro = 'Xavier ad569x debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_power_mode(self, line):
        '''power_mode
        Puts the device in a specific power mode
        channel:   int(0/1/2/3), DAC Channel
        mode:       string('NORMAL','1K','100K','3_STATE')
        eg:         power_mode 0,'NORMAL' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad569x.power_mode(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_select_vref_mode(self, line):
        '''select_vref_mode
        Select internal or external voltage reference
        vref_mode:  string('INT_REF_ON','INT_REF_OFF')
        eg: select_vref_mode 'INT_REF_ON' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad569x.select_vref_mode(eval(line))
        print("Done")

    @handle_errors
    def do_soft_reset(self, line):
        '''soft_reset
        Resets the device(clears the outputs to either zero scale or midscale)'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad569x.soft_reset()
        print("Done")

    @handle_errors
    def do_output_volt(self, line):
        '''output_volt
        Set the output voltage of the selected channel
        channel:   int(0/1/2/3), DAC Channel
        volt: 	    int/float, the voltage
        eg: 		output_volt 0,2.49 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.ad569x.output_volt(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_readback_volt(self, line):
        '''readback_volt
        Reads back the voltage value written to one of the channels
        channel:   int(0/1/2/3), DAC Channel
        eg:         readback_volt 0'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad569x.readback_volt(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
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


def create_ad569x_dbg(dev_name, dev_addr):
    ad569x_dbg = AD569XDebuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    ad569x_dbg.ad569x = AD569X(dev_addr, i2c_bus)
    return ad569x_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x0D')
    args = parser.parse_args()
    ad569x_dbg = create_ad569x_dbg(args.device, int(args.address, 16))

    ad569x_dbg.cmdloop()
