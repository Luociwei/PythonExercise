# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667


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


class AD56X7RDebuger(cmd.Cmd):
    prompt = 'ad56x7r>'
    intro = 'Xavier ad56x7r debug tool'

    @handle_errors
    def do_write(self, line):
        '''write addr [data]'''
        line = line.replace(' ', ',')
        self.ad56x7r.write_operation(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_read(self, line):
        '''read'''
        rd_data = self.ad56x7r.read_operation()
        print('Result:')
        print(rd_data)

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc [channel] [volt]'''
        line = line.replace(' ', ',')
        self.ad56x7r.output_volt_dc(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_select_work_mode(self, line):
        '''select_work_mode [channel] [mode]'''
        line = line.replace(' ', ',')
        self.ad56x7r.select_work_mode(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_set_ldac_pin_enable(self, line):
        '''set_ldac_pin_enable [channel]'''
        self.ad56x7r.set_ldac_pin_enable(eval(line))
        print('Done.')

    @handle_errors
    def do_set_reference(self, line):
        '''set_reference [ref_mode]'''
        self.ad56x7r.set_reference(eval(line))
        print('Done.')

    @handle_errors
    def do_reset(self, line):
        '''reset [mode]'''
        line = line.replace(' ', ',')
        self.ad56x7r.reset(eval(line))
        print('Done.')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt [channel]'''
        line = line.replace(' ', ',')
        rd_data = self.ad56x7r.read_volt(eval(line))
        print('Result:')
        print(rd_data)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_write.__doc__)
        print(self.do_read.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_select_work_mode.__doc__)
        print(self.do_set_ldac_pin_enable.__doc__)
        print(self.do_set_reference.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bus(dev_name, bus_type):
    if dev_name == '':
        return None

    if bus_type == 'i2c':
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            bus = MIXI2CSG(axi4_bus)
        else:
            bus = I2C(dev_name)
    elif bus_type == 'spi':
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            bus = MIXQSPISG(axi4_bus)
        else:
            raise NotImplementedError('PS SPI not implement yet!')
    return bus


def create_ad56x7r_dbg(dev_name, dev_addr, bus_type):
    ad56x7r_dbg = AD56X7RDebuger()
    bus = create_bus(dev_name, bus_type)
    ad56x7r_dbg.ad56x7r = AD5667(dev_addr, bus)
    return ad56x7r_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x0c')
    parser.add_argument('-b', '--bus_type', help='bus type', default='i2c')

    args = parser.parse_args()

    ad56x7r_dbg = create_ad56x7r_dbg(args.device, int(args.address, 16), args.bus_type)

    ad56x7r_dbg.cmdloop()
