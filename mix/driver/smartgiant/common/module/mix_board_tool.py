# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
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


class MIXBoardDebuger(cmd.Cmd):
    prompt = 'mix>'
    intro = ' MIXBoard debug tool'

    @handle_errors
    def do_read_temp(self, line):
        '''read_temp'''
        result = self._mix.get_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_eeprom(self, line):
        '''write_eeprom addr [data0,...,datan]'''
        line = line.replace(' ', ',')
        self._mix.write_eeprom(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_eeprom(self, line):
        '''read_eeprom addr nbytes'''
        line = line.replace(' ', ',')
        result = self._mix.read_eeprom(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_hw_ver(self, line):
        '''write_hw_ver "ver"'''
        self._mix.write_hardware_version(eval(line))
        print("Done.")

    @handle_errors
    def do_read_hw_ver(self, line):
        '''read_hw_ver'''
        result = self._mix.read_hardware_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_sn(self, line):
        '''write_sn key_n key_e "sn"'''
        line = line.replace(' ', ',')
        self._mix.write_serialnumber(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_sn(self, line):
        '''read_sn'''
        result = self._mix.read_serialnumber()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_cal_date(self, line):
        '''write_cal_date'''
        self._mix.write_calibration_date(eval(line))
        print("Done.")

    @handle_errors
    def do_read_cal_date(self, line):
        '''read_cal_date'''
        result = self._mix.read_calibration_date()
        print("Usage:")
        print(result)

    @handle_errors
    def do_write_cal(self, line):
        '''write_cal unit_id gain offset threshold'''
        line = line.replace(' ', ',')
        self._mix.write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_cal(self, line):
        '''read_cal unit_id'''
        result = self._mix.read_calibration_cell(eval(line))
        print("Usage:")
        print(result)

    @handle_errors
    def do_erase_cal(self, line):
        '''erase_cal unit_id'''
        self._mix.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_cal_pipe(self, line):
        '''cal_pipe {level: {'unit_id': type int,'limit':(value, unit)}} raw_data'''
        line = line.replace(' ', ',')
        result = self._mix.cal_pipe(*list(eval(line)))
        print("Usage:")
        print(result)

    @handle_errors
    def do_read_calibration(self, line):
        '''read_calibration range_name index'''
        line = line.replace(' ', ',')
        result = self._mix.read_calibration(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_calibration(self, line):
        '''write_calibration range_name index gain offset threshold'''
        line = line.replace(' ', ',')
        self._mix.write_calibration(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_erase_calibration(self, line):
        '''erase_calibration range_name index'''
        line = line.replace(' ', ',')
        self._mix.erase_calibration(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_load_calibration(self, line):
        '''load_calibration'''
        self._mix.load_calibration()
        print("Done")

    @handle_errors
    def do_config_calibration_range(self, line):
        '''config_calibration_range range_name addr count'''
        line = line.replace(' ', ',')
        self._mix.config_calibration_range(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_config_legacy_calibration_range(self, line):
        '''config_calibration_range range_name addr count'''
        line = line.replace(' ', ',')
        self._mix.config_legacy_calibration_range(*list(eval(line)))
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
    def do_write_vid(self, line):
        '''write_vid vid'''
        self._mix.write_vid(eval(line))
        print("Done")

    @handle_errors
    def do_read_vid(self, line):
        '''read_vid'''
        result = self._mix.read_vid()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_cal_start_addr(self, line):
        '''read_cal_start_addr'''
        result = self._mix.read_cal_start_addr()
        print("Result:")
        print("0x{:02x}".format(result))

    @handle_errors
    def do_write_cal_start_addr(self, line):
        '''write_cal_start_addr addr'''
        self._mix.write_cal_start_addr(eval(line))
        print("Done")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print("Usage:")
        print(self.do_read_temp.__doc__)
        print(self.do_write_eeprom.__doc__)
        print(self.do_read_eeprom.__doc__)
        print(self.do_write_hw_ver.__doc__)
        print(self.do_read_hw_ver.__doc__)
        print(self.do_write_sn.__doc__)
        print(self.do_read_sn.__doc__)
        print(self.do_write_cal_date.__doc__)
        print(self.do_read_cal_date.__doc__)
        print(self.do_write_cal.__doc__)
        print(self.do_read_cal.__doc__)
        print(self.do_erase_cal.__doc__)
        print(self.do_cal_pipe.__doc__)
        print(self.do_read_calibration.__doc__)
        print(self.do_write_calibration.__doc__)
        print(self.do_erase_calibration.__doc__)
        print(self.do_load_calibration.__doc__)
        print(self.do_write_vid.__doc__)
        print(self.do_read_vid.__doc__)
        print(self.do_write_cal_start_addr.__doc__)
        print(self.do_read_cal_start_addr.__doc__)
        print(self.do_calibrate.__doc__)
        print(self.do_config_calibration_range.__doc__)
        print(self.do_config_legacy_calibration_range.__doc__)
        print(self.do_config_calibration_checksum.__doc__)
        print(self.do_read_calibration_item.__doc__)
        print(self.do_write_calibration_item.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_mixboard_dbg(eeprom_addr, eeprom_bus_name, nct_addr, nct_bus_name, cal_table, range_table):
    mixboard_dbg = MIXBoardDebuger()
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

    mixboard_dbg._mix = MIXBoard(eeprom, nct, cal_table, range_table)
    return mixboard_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a1', '--address1', help='eeprom device address', default='0x00')
    parser.add_argument('-i2c1', '--i2c_bus1', help='eeprom i2c bus', default='')
    parser.add_argument('-a2', '--address2', help='nct75 device address', default='0x00')
    parser.add_argument('-i2c2', '--i2c_bus2', help='nct device bus', default='')
    parser.add_argument('-cal_table', '--cal_table', help='legacy calibration table', default='{}')
    parser.add_argument('-range_table', '--range_table', help='ICI calibration table', default='{}')

    args = parser.parse_args()

    mixboard_dbg = create_mixboard_dbg(int(args.address1, 16), args.i2c_bus1,
                                       int(args.address2, 16), args.i2c_bus2,
                                       eval(args.cal_table), eval(args.range_table))

    mixboard_dbg.cmdloop()
