# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.ic.ad56x3r import AD5663R, AD5643R, AD5623R

__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD56X3RDebuger(cmd.Cmd):
    prompt = 'ad56x3>'
    intro = 'Xavier ad56x3 debug tool'

    @handle_errors
    def do_reset(self, line):
        '''reset mode("DAC_AND_INPUT_SHIFT_REG","ALL_REG")'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.reset(eval(line))
        print('Done.')

    @handle_errors
    def do_select_work_mode(self, line):
        '''select_work_mode channel(0-2) mode("NORMAL","1KOHM_GND", "100KOHM_GND", "HIGH-Z")'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.select_work_mode(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_set_ldac_pin_enable(self, line):
        '''set_ldac_pin_enable channel(0-2)'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.set_ldac_pin_enable(eval(line))
        print('Done.')

    @handle_errors
    def do_set_ldac_pin_disable(self, line):
        '''set_ldac_pin_disable channel(0-2)'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.set_ldac_pin_disable(eval(line))
        print('Done.')

    @handle_errors
    def do_set_reference(self, line):
        '''set_reference ref_mode("INTERNAL,"EXTERN")'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.set_reference(eval(line))
        print('Done.')

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc channel(0-2) volt'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.output_volt_dc(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_write_operation(self, line):
        '''write_operation reg_addr data'''
        line = line.replace(' ', ',')
        line = eval(line)
        self.ad56x3.write_operation(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_reset.__doc__)
        print(self.do_select_work_mode.__doc__)
        print(self.do_set_ldac_pin_enable.__doc__)
        print(self.do_set_ldac_pin_disable.__doc__)
        print(self.do_set_reference.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_write_operation.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bus(dev_name):
    if dev_name == '':
        return None

    if utility.is_pl_device(dev_name):
        axi4_bus = AXI4LiteBus(dev_name, 256)
        bus = MIXQSPISG(axi4_bus)
        bus.mode = 'MODE2'
    else:
        raise NotImplementedError('PS SPI not implement yet!')
    return bus


def create_ad56x3(bus, vref, ref_mode, dac):
    if dac == 5663:
        ad56x3 = AD5663R(bus, vref, ref_mode)
    elif dac == 5643:
        ad56x3 = AD5643R(bus, vref, ref_mode)
    else:
        ad56x3 = AD5623R(bus, vref, ref_mode)
    return ad56x3


def create_ad56x3_dbg(dev_name, vref, ref_mode, dac):
    ad56x3_dbg = AD56X3RDebuger()
    bus = create_bus(dev_name)
    ad56x3_dbg.ad56x3 = create_ad56x3(bus, vref, ref_mode, dac)
    return ad56x3_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-v', '--vref', help='voltage reference', default='2500')
    parser.add_argument('-m', '--ref_mode', help='reference mode', default='EXTERN')
    parser.add_argument('-dac', '--dac', help='dac name', default='5663')

    args = parser.parse_args()

    ad56x3_dbg = create_ad56x3_dbg(args.device, int(args.vref), args.ref_mode, int(args.dac))

    ad56x3_dbg.cmdloop()
