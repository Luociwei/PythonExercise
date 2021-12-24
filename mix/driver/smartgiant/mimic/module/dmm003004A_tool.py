# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.mimic.module.dmm003004A import DMM003004A


__author__ = 'tufeng.mao@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class DMM003004ADebuger(cmd.Cmd):
    prompt = 'dmm003004A>'
    intro = 'Xavier dmm003004A debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.dmm003004A.module_init()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel rate'''
        line = line.replace(' ', ',')
        self.dmm003004A.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.dmm003004A.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path channel range'''
        line = line.replace(' ', ',')
        self.dmm003004A.set_measure_path(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        line = line.replace(' ', ',')
        result = self.dmm003004A.get_measure_path()
        print(result)

    @handle_errors
    def do_dc_voltage_measure(self, line):
        '''dc_voltage_measure'''
        result = self.dmm003004A.dc_voltage_measure()

        print("Result:")
        print(result)

    @handle_errors
    def do_ac_voltage_measure(self, line):
        '''ac_voltage_measure'''
        result = self.dmm003004A.ac_voltage_measure()

        print("Result:")
        print(result)

    @handle_errors
    def do_continuous_measure(self, line):
        '''continuous_measure count'''
        result = self.dmm003004A.continuous_measure(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure'''
        result = self.dmm003004A.current_measure()
        print("Result:")
        print(result)

    @handle_errors
    def do_resistor_measure(self, line):
        '''resistor_measure'''
        result = self.dmm003004A.resistor_measure()
        print("Result:")
        print(result)

    @handle_errors
    def do_diode_measure(self, line):
        '''diode_measure'''
        result = self.dmm003004A.diode_voltage_measure()
        print("Result:")
        print(result)

    def do_read_register(self, line):
        '''read_register addr'''
        result = self.dmm003004A.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    def do_write_register(self, line):
        '''write_register addr data'''
        self.dmm003004A.ad7175.write_register(*list(eval(line)))
        print("Done.")

    def do_temperature(self, line):
        '''temperature'''
        result = self.dmm003004A.get_temperature()
        print("%f" % result)

    def do_write_calibration_date(self, line):
        '''write_calibration_date '2018929' '''
        self.dmm003004A.legacy_write_calibration_date(eval(line))
        print("Done.")

    def do_read_calibration_date(self, line):
        '''read_calibration_date'''
        result = self.dmm003004A.legacy_read_calibration_date()
        print(result)

    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold'''
        line = line.replace(' ', ',')
        self.dmm003004A.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    def do_read_calibration_cell(self, line):
        '''read_calibration_cell unit_index'''
        result = self.dmm003004A.legacy_read_calibration_cell(eval(line))
        print(result)

    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.dmm003004A.legacy_erase_calibration_cell(eval(line))
        print("Done.")

    def do_write_cal_mode(self, line):
        '''write_cal_mode 'raw'or'cal' '''
        self.dmm003004A.mode = eval(line)
        print("Done.")

    def do_read_cal_mode(self, line):
        '''read_cal_mode'''
        result = self.dmm003004A.mode
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_module_init.__doc__)
        print(self.do_set_sampling_rate.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_set_measure_path.__doc__)
        print(self.do_get_measure_path.__doc__)
        print(self.do_dc_voltage_measure.__doc__)
        print(self.do_ac_voltage_measure.__doc__)
        print(self.do_continuous_measure.__doc__)
        print(self.do_current_measure.__doc__)
        print(self.do_resistor_measure.__doc__)
        print(self.do_diode_measure.__doc__)
        print(self.do_temperature.__doc__)
        print(self.do_write_calibration_date.__doc__)
        print(self.do_read_calibration_date.__doc__)
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_erase_calibration_cell.__doc__)
        print(self.do_write_cal_mode.__doc__)
        print(self.do_read_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_dmm003004A_dbg(ipcore_name, vref, i2c_bus_name):
    dmm003004A_dbg = DMM003004ADebuger()
    daqt1 = None
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_chip='AD7175', ad717x_mvref=vref, use_spi=False, use_gpio=False)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    dmm003004A_dbg.dmm003004A = DMM003004A(i2c_bus, daqt1)
    dmm003004A_dbg.dmm003004A.module_init()
    return dmm003004A_dbg


if __name__ == '__main__':
    '''
    ***measure single voltage/current step:
        1.set_measure_path
        2.measure single voltage/current
    ***measure continue voltage/current step:
        1.set_measure_path
        2.enable_continuous_measure
        3.measure continue voltage/current
    ***when from continue mode to single mode,you have to stop_continuous_measure first.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ipcore', help='ipcore devcie name',
                        default='')
    parser.add_argument('-v', '--vref', help='ad7175 reference',
                        default='2500')
    parser.add_argument('-i2c', '--i2c', help='cat9555 i2c bus name',
                        default='')

    args = parser.parse_args()
    dmm003004A_dbg = create_dmm003004A_dbg(args.ipcore, args.vref, args.i2c)

    dmm003004A_dbg.cmdloop()
