# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.bus.i2c import I2C
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.ic.at24c08 import AT24C08
from mix.driver.smartgiant.common.ic.nct75 import NCT75


__author__ = 'jingyong.xiao@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class SGModuleDriverDebuger(cmd.Cmd):
    prompt = 'mix>'
    intro = ' SGModuleDriver debug tool'

    @handle_errors
    def do_read_temp(self, line):
        '''read_temp'''
        result = self._mix.read_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_nvmem(self, line):
        '''write_nvmem addr bytearray([data0,...,datan])'''
        line = line.replace(' ', ',')
        self._mix.write_nvmem(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_nvmem(self, line):
        '''read_nvmem addr count'''
        line = line.replace(' ', ',')
        result = self._mix.read_nvmem(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_calibration_mode(self, line):
        '''get_calibration_mode'''
        line = line.replace(' ', ',')
        self._mix.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode mode'''
        line = line.replace(' ', ',')
        self._mix.set_calibration_mode(eval(line))
        print("Done")

    @handle_errors
    def do_erase_calibration_item(self, line):
        '''erase_calibration_item cal_index range_name index'''
        line = line.replace(' ', ',')
        self._mix.erase_calibration_item(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_load_calibration(self, line):
        '''load_calibration'''
        self._mix.load_calibration()
        print("Done")

    @handle_errors
    def do_config_calibration_range(self, line):
        '''config_calibration_range cal_index range_name addr count'''
        line = line.replace(' ', ',')
        self._mix.config_calibration_range(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_config_calibration_checksum(self, line):
        '''config_calibration_checksum cal_index'''
        self._mix.config_calibration_checksum(eval(line))
        print("Done")

    @handle_errors
    def do_read_calibration_item(self, line):
        '''read_calibration_item cal_index range_name index'''
        line = line.replace(' ', ',')
        self._mix.read_calibration_item(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_write_calibration_item(self, line):
        '''write_calibration_item cal_index range_name index gain offset threshold'''
        line = line.replace(' ', ',')
        self._mix.write_calibration_item(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_calibrate(self, line):
        '''calibrate range_name raw_data'''
        line = line.replace(' ', ',')
        result = self._mix.calibrate(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_eeprom_read_string(self, line):
        '''eeprom_read_string addr rd_len'''
        line = line.replace(' ', ',')
        result = self._mix.eeprom_read_string(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_eeprom_write_string(self, line):
        '''eeprom_write_string addr data'''
        line = line.replace(' ', ',')
        result = self._mix.eeprom_write_string(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print("Usage:")
        print(self.do_read_temp.__doc__)
        print(self.do_write_nvmem.__doc__)
        print(self.do_read_nvmem.__doc__)
        print(self.do_get_calibration_mode.__doc__)
        print(self.do_set_calibration_mode.__doc__)
        print(self.do_erase_calibration_item.__doc__)
        print(self.do_load_calibration.__doc__)
        print(self.do_calibrate.__doc__)
        print(self.do_eeprom_read_string.__doc__)
        print(self.do_eeprom_write_string.__doc__)
        print(self.do_config_calibration_range.__doc__)
        print(self.do_config_calibration_checksum.__doc__)
        print(self.do_read_calibration_item.__doc__)
        print(self.do_write_calibration_item.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_sgmoduledriver_dbg(eeprom_addr, eeprom_bus_name, nct_addr, nct_bus_name, range_table):
    sgmoduledriver_dbg = SGModuleDriverDebuger()
    if eeprom_bus_name == "":
        eeprom = None
    else:
        if utility.is_pl_device(eeprom_bus_name):
            axi4_bus = AXI4LiteBus(eeprom_bus_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(eeprom_bus_name)
        eeprom = AT24C08(eeprom_addr, i2c_bus)

    if nct_bus_name == "":
        nct = None
    else:
        if utility.is_pl_device(nct_bus_name):
            axi4_bus = AXI4LiteBus(nct_bus_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(nct_bus_name)
        nct = NCT75(nct_addr, nct_bus_name)

    sgmoduledriver_dbg._mix = SGModuleDriver(eeprom, nct, range_table)
    return sgmoduledriver_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a1', '--address1', help='eeprom device address', default='0x00')
    parser.add_argument('-i2c1', '--i2c_bus1', help='eeprom i2c bus', default='')
    parser.add_argument('-a2', '--address2', help='nct75 device address', default='0x00')
    parser.add_argument('-i2c2', '--i2c_bus2', help='nct device bus', default='')
    parser.add_argument('-range_table', '--range_table', help='ICI calibration table', default='{}')

    args = parser.parse_args()

    sgmoduledriver_dbg = create_sgmoduledriver_dbg(int(args.address1, 16), args.i2c_bus1,
                                                   int(args.address2, 16), args.i2c_bus2,
                                                   eval(args.range_table))

    sgmoduledriver_dbg.cmdloop()
