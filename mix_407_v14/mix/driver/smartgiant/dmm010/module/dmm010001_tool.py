# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.dmm010.module.dmm010001 import DMM010001
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.utility.utility import utility
from mix.driver.core.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.ipcore.mix_daqt1_sg_r_emulator import MIXDAQT1SGREmulator


__author__ = 'haite.zhuang@SmartGiant'
__version__ = '0.2'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class DMM010001Debuger(cmd.Cmd):
    prompt = 'dmm>'
    intro = 'Xavier dmm010001 debug tool'

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate channel rate'''
        line = line.replace(' ', ',')
        self.dmm.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.dmm.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path range('6V'/'1A'/'1ohm'/'20ohm')'''
        line = line.replace(' ', ',')
        self.dmm.set_measure_path(eval(line))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        line = line.replace(' ', ',')
        result = self.dmm.get_measure_path()
        print(result)

    @handle_errors
    def do_voltage_measure(self, line):
        '''voltage_measure'''
        result = self.dmm.voltage_measure()

        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_measure(self, line):
        '''multi_points_measure sel_range count'''
        line = line.replace(' ', ',')
        result = self.dmm.multi_points_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure'''
        result = self.dmm.current_measure()
        print("Result:")
        print(result)

    @handle_errors
    def do_resistor_measure(self, line):
        '''resistor_measure sel_range '''
        result = self.dmm.resistor_measure(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_measure_enable(self, line):
        '''multi_points_measure_enable channel,sampling_rate '''
        line = line.replace(' ', ',')
        self.dmm.multi_points_measure_enable(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_multi_points_measure_disable(self, line):
        '''multi_points_measure_disable channel'''
        self.dmm.multi_points_measure_disable(eval(line))
        print("Done.")

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr'''
        result = self.dmm.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr data'''
        self.dmm.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_adc_volt(self, line):
        '''read_adc_volt channels'''
        result = self.dmm.ad7175.read_volt(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_io(self, line):
        '''set_io pin level'''
        self.dmm.tca9538.set_pin(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature'''
        result = self.dmm.get_temperature()
        print(result)

    @handle_errors
    def do_write_calibration_date(self, line):
        '''write_calibration_date '2018929' '''
        self.dmm.write_calibration_date(eval(line))
        print("Done.")

    @handle_errors
    def do_read_calibration_date(self, line):
        '''read_calibration_date'''
        result = self.dmm.read_calibration_date()
        print(result)

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset'''
        line = line.replace(' ', ',')
        self.dmm.write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell unit_index'''
        result = self.dmm.read_calibration_cell(eval(line))
        print(result)

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.dmm.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_write_cal_mode(self, line):
        '''write_cal_mode mode('raw'/'cal') '''
        self.dmm.set_calibration_mode(eval(line))
        print("Done.")

    @handle_errors
    def do_read_cal_mode(self, line):
        '''read_cal_mode'''
        result = self.dmm.get_calibration_mode()
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_set_sampling_rate.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_set_measure_path.__doc__)
        print(self.do_get_measure_path.__doc__)
        print(self.do_voltage_measure.__doc__)
        print(self.do_current_measure.__doc__)
        print(self.do_resistor_measure.__doc__)
        print(self.do_multi_points_measure_enable.__doc__)
        print(self.do_multi_points_measure_disable.__doc__)
        print(self.do_multi_points_measure.__doc__)
        print(self.do_temperature.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_read_adc_volt.__doc__)
        print(self.do_set_io.__doc__)
        print(self.do_write_calibration_date.__doc__)
        print(self.do_read_calibration_date.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_erase_calibration_cell.__doc__)
        print(self.do_read_cal_mode.__doc__)
        print(self.do_write_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_dmm_dbg(ad7175_bus_name, i2c_bus_name, axi4_bus_name):
    dmm_dbg = DMM010001Debuger()

    if axi4_bus_name == '':
        daqt1 = MIXDAQT1SGREmulator(axi4_bus=None, ad717x_chip='AD7175', ad717x_mvref=5000,
                                    use_spi=False, use_gpio=False)
        ad7175 = None
    elif 'MIX_DAQT' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 65535)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=False, use_gpio=False)
        ad7175 = None
    else:
        daqt1 = None
        ad717x_axi4_bus = AXI4LiteBus(ad7175_bus_name, 8192)
        ad7175 = MIXAd7175SG(ad717x_axi4_bus, 5000)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    dmm_dbg.dmm = DMM010001(ad7175, i2c_bus, daqt1)
    dmm_dbg.dmm.module_init()
    return dmm_dbg


if __name__ == '__main__':
    '''
    ***measure single voltage/current step:
        1.set_measure_path
        2.measure single voltage/current
    ***measure continue voltage/current step:
        1.set_measure_path
        2.multi_points_measure_enable
        3.measure continue voltage/current
    ***when from continue mode to single mode,you have to stop_continuous_measure first.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ad', '--ad7175', help='ad7175 devcie name',
                        default='/dev/MIX_AD717X_0')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name',
                        default='/dev/i2c-1')
    parser.add_argument('-ip', '--ipcore', help='ipcore device name',
                        default='/dev/MIX_DAQT1_0')
    args = parser.parse_args()
    dmm_dbg = create_dmm_dbg(args.ad7175, args.i2c, args.ipcore)

    dmm_dbg.cmdloop()
