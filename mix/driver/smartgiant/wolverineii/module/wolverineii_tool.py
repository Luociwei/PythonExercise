# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.wolverineii.module.wolverineii import WolverineII
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.commom.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.utility import utility

__author__ = 'zicheng.huang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class WolverineiiDebuger(cmd.Cmd):
    prompt = 'wolverineii>'
    intro = 'Xavier wolverineii debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.wolverineii.module_init()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel sampling_rate'''
        line = line.replace(' ', ',')
        self.wolverineii.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.wolverineii.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path sel_range delay_time'''
        line = line.replace(' ', ',')
        self.wolverineii.set_measure_path(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        line = line.replace(' ', ',')
        result = self.wolverineii.get_measure_path()
        print(result)

    @handle_errors
    def do_voltage_measure(self, line):
        '''voltage_measure volt_range sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.voltage_measure(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_continuous_sample(self, line):
        '''continuous_sample count sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.continuous_sample(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure curr_range sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    def do_read_register(self, line):
        '''read_register addr'''
        result = self.wolverineii.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    def do_write_register(self, line):
        '''write_register addr data'''
        self.wolverineii.ad7175.write_register(*list(eval(line)))
        print("Done.")

    def do_temperature(self, line):
        '''temperature'''
        result = self.wolverineii.get_temperature()
        print("%f" % result)

    def do_multi_points_measure(self, line):
        '''multi_points_measure count sel_range sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.multi_points_measure(*list(eval(line)))
        print("Result:")
        print(result)

    def do_multi_points_voltage_measure(self, line):
        '''multi_points_voltage_measure count volt_range sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.multi_points_voltage_measure(*list(eval(line)))
        print("Result:")
        print(result)

    def do_multi_points_current_measure(self, line):
        '''multi_points_current_measure count curr_range sampling_rate'''
        line = line.replace(' ', ',')
        result = self.wolverineii.multi_points_current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold'''
        line = line.replace(' ', ',')
        self.wolverineii.write_calibration_cell(*list(eval(line)))
        print("Done.")

    def do_read_calibration_cell(self, line):
        '''read_calibration_cell unit_index'''
        result = self.wolverineii.read_calibration_cell(eval(line))
        print(result)

    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.wolverineii.erase_calibration_cell(eval(line))
        print("Done.")

    def do_write_cal_mode(self, line):
        '''write_cal_mode 'raw'or'cal' '''
        self.wolverineii.mode = eval(line)
        print("Done.")

    def do_read_cal_mode(self, line):
        '''read_cal_mode'''
        result = self.wolverineii.mode
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
        print(self.do_voltage_measure.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_continuous_sample.__doc__)
        print(self.do_multi_points_measure.__doc__)
        print(self.do_current_measure.__doc__)
        print(self.do_temperature.__doc__)
        print(self.do_multi_points_voltage_measure.__doc__)
        print(self.do_multi_points_current_measure.__doc__)
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_erase_calibration_cell.__doc__)
        print(self.do_write_cal_mode.__doc__)
        print(self.do_read_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_wolverineii_dbg(ipcore_name, i2c_bus_name):
    wolverineii_dbg = WolverineiiDebuger()
    daqt1 = None
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, 'AD7175', use_spi=True, use_gpio=False)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    wolverineii_dbg.wolverineii = WolverineII(i2c_bus, daqt1)
    wolverineii_dbg.wolverineii.module_init()
    return wolverineii_dbg


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
    parser.add_argument('-i2c', '--i2c', help='cat9555 i2c bus name',
                        default='')

    args = parser.parse_args()
    wolverineii_dbg = create_wolverineii_dbg(args.ipcore, args.i2c)

    wolverineii_dbg.cmdloop()
