# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


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


class EepromDebuger(cmd.Cmd):
    prompt = 'eeprom>'
    intro = 'Xavier eeprom debug tool'

    @handle_errors
    def do_write(self, line):
        '''write [addr] [data]'''
        line = line.replace(' ', ',')
        self.eeprom.write(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_read(self, line):
        '''read addr [rd_len]'''
        line = line.replace(' ', ',')
        rd_data = self.eeprom.read(*list(eval(line)))
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


def create_eeprom(bus, bus_type, chip_type, dev_addr):
    eeprom_module = __import__(chip_type.lower(), fromlist={chip_type.lower()}, level=-1)
    eeprom = None
    for item in dir(eeprom_module):
        if item.lower() == chip_type.lower():
            if bus_type is 'i2c':
                eeprom = getattr(eeprom_module, item)(dev_addr, bus)
            else:
                eeprom = getattr(eeprom_module, item)(bus)
            break
    if eeprom is None:
        raise Exception('Chip ' + chip_type + ' not found.')
    return eeprom


def create_eeprom_dbg(dev_name, dev_addr, chip_type, bus_type):
    eeprom_dbg = EepromDebuger()
    bus = create_bus(dev_name, bus_type)
    eeprom_dbg.eeprom = create_eeprom(bus, bus_type, chip_type, dev_addr)
    return eeprom_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x50')
    parser.add_argument('-t', '--chip_type', help='chip type', default='at24c08')
    parser.add_argument('-b', '--bus_type', help='bus type', default='i2c')

    args = parser.parse_args()

    eeprom_dbg = create_eeprom_dbg(args.device, int(args.address, 16), args.chip_type, args.bus_type)

    eeprom_dbg.cmdloop()
