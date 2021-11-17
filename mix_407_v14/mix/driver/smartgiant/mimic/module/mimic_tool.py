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
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.mimic.module.mimic import Mimic

__author__ = 'jinkun.lin@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MimicDebuger(cmd.Cmd):
    prompt = 'mimic>'
    intro = 'Xavier mimic003003 debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.mimic.module_init()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel rate'''
        line = line.replace(' ', ',')
        self.mimic.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.mimic.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path channel range'''
        line = line.replace(' ', ',')
        self.mimic.set_measure_path(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        line = line.replace(' ', ',')
        result = self.mimic.get_measure_path()
        print(result)

    @handle_errors
    def do_dc_voltage_measure(self, line):
        '''dc_voltage_measure'''
        line = line.replace(' ', ',')
        result = self.mimic.dc_voltage_measure(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_ac_voltage_measure(self, line):
        '''ac_voltage_measure'''
        line = line.replace(' ', ',')
        result = self.mimic.ac_voltage_measure(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_continuous_measure(self, line):
        '''continuous_measure count'''
        line = line.replace(' ', ',')
        result = self.mimic.continuous_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure'''
        line = line.replace(' ', ',')
        result = self.mimic.current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_resistor_measure(self, line):
        '''resistor_measure'''
        line = line.replace(' ', ',')
        result = self.mimic.resistor_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_diode_measure(self, line):
        '''diode_measure'''
        line = line.replace(' ', ',')
        result = self.mimic.diode_voltage_measure(*list(eval(line)))
        print("Result:")
        print(result)

    def do_read_register(self, line):
        '''read_register addr'''
        result = self.mimic.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    def do_write_register(self, line):
        '''write_register addr data'''
        self.mimic.ad7175.write_register(*list(eval(line)))
        print("Done.")

    def do_temperature(self, line):
        '''temperature'''
        result = self.mimic.get_temperature()
        print("%f" % result)

    def do_write_calibration_date(self, line):
        '''write_calibration_date '2018929' '''
        self.mimic.legacy_write_calibration_date(eval(line))
        print("Done.")

    def do_read_calibration_date(self, line):
        '''read_calibration_date'''
        result = self.mimic.legacy_read_calibration_date()
        print(result)

    def do_legacy_write_calibration_cell(self, line):
        '''legacy_write_calibration_cell unit_index gain offset threshold'''
        line = line.replace(' ', ',')
        self.mimic.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    def do_legacy_read_calibration_cell(self, line):
        '''read_calibration_cell unit_index'''
        result = self.mimic.legacy_read_calibration_cell(eval(line))
        print(result)

    def do_legacy_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.mimic.legacy_erase_calibration_cell(eval(line))
        print("Done.")

    def do_write_cal_mode(self, line):
        '''write_cal_mode 'raw'or'cal' '''
        self.mimic.mode = eval(line)
        print("Done.")

    def do_read_cal_mode(self, line):
        '''read_cal_mode'''
        result = self.mimic.mode
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
        print(self.do_legacy_write_calibration_cell.__doc__)
        print(self.do_legacy_read_calibration_cell.__doc__)
        print(self.do_legacy_erase_calibration_cell.__doc__)
        print(self.do_write_cal_mode.__doc__)
        print(self.do_read_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_mimic_dbg(ipcore_name, ad7175_bus_name, vref, i2c_bus_name):
    mimic_dbg = MimicDebuger()
    daqt1 = None
    ad7175 = None
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_mvref=vref, use_spi=False, use_gpio=False)
    elif ad7175_bus_name != '':
        axi4_bus = AXI4LiteBus(ad7175_bus_name, 256)
        ad7175 = MIXAd7175SG(axi4_bus, vref)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    mimic_dbg.mimic = Mimic(i2c_bus, daqt1, ad7175)
    mimic_dbg.mimic.module_init()
    return mimic_dbg


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
    parser.add_argument('-ad', '--ad7175', help='ad7175 devcie name',
                        default='')
    parser.add_argument('-v', '--vref', help='ad7175 reference',
                        default='2500')
    parser.add_argument('-i2c', '--i2c', help='cat9555 i2c bus name',
                        default='')

    args = parser.parse_args()
    mimic_dbg = create_mimic_dbg(args.ipcore, args.ad7175,
                                 args.vref, args.i2c)

    mimic_dbg.cmdloop()
