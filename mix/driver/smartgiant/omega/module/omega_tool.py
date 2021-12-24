# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps

from mix.driver.smartgiant.omega.module.omega import Omega
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.pl_spi_bus import PLSPIBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r_emulator import MIXDAQT1SGREmulator
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG


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


class OmegaDebuger(cmd.Cmd):
    prompt = 'omega>'
    intro = 'Xavier Omega debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_module_init(self, line):
        '''module_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.module_init()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate
        Omega set ad7175 sampling rate
        rate:    float    ad7175 sampling rate, value is from 1 to 250000.
        eg: set_sampling_rate 100000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.set_sampling_rate(eval(line))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate
        Omega set ad7175 sampling rate.'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.get_sampling_rate()
        print("Result:")
        print(result)

    @handle_errors
    def do_select_range(self, line):
        '''select_range
        Omega select capacitance range
        range: string 'vref_test',100pF',1000pF','10nF',
                      '100nF','1000nF','10uF','50uF','500uF','close'
        eg: select_range '500uF' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.select_range(eval(line))
        print("Done.")

    @handle_errors
    def do_get_range(self, line):
        '''get_range
        Omega get current capacitance range'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.get_range()
        print("Result:")
        print(result)

    @handle_errors
    def do_measure_dds_voltage(self, line):
        '''measure_dds_voltage
        Omega measure standard dds voltage value, used when board initializes'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.measure_dds_voltage()
        print('Done')

    @handle_errors
    def do_measure_capacitance(self, line):
        '''measure_capacitance
        Omega measure capacitance using capacitance range
        cap_range: '100pF',1000pF','10nF',
                   '100nF','1000nF','10uF','50uF','500uF'
        adc_samples: int, default is 2
        eg: measure_capacitance '500uF', 5,2 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.omega.measure_capacitance(*list(eval(line)))
        print("Result:")
        print(round(result[0], 4), result[1])

    @handle_errors
    def do_measure_cap(self, line):
        '''measure_cap
        Omega measure capacitance using capacitance range
        cap_range: '100pF',1000pF','10nF',
                   '100nF','1000nF','10uF','50uF','500uF'
        eg: measure_cap '500uF' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.measure_capacitance(eval(line))
        print("Result:")
        print(round(result[0], 4), result[1])

    def do_temperature(self, line):
        '''temperature
        Omega read temperature from sensor
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.get_temperature()
        print("Result:")
        print(result)

    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold
        MIXBoard calibration data write
        unit_index:   int,    calibration unit index
        gain:         float,  calibration gain
        offset:       float,  calibration offset
        threshold:    float,  if value < threshold,
                            use this calibration unit data
        eg: write_calibration_cell 0,1.1,0.1,100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.omega.write_calibration_cell(*list(eval(line)))
        print("Done.")

    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        unit_index: int, calibration unit index
        eg: read_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell
        MIXBoard erase calibration unit
        unit_index: int, calibration unit index
        eg: erase_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.erase_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Omega enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.omega.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Omega query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.omega.is_use_cal_data()
        print('Result:')
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


def create_omega_dbg(axi4_bus_name, spi_axi4_bus_name, i2c_bus_name):
    omega = OmegaDebuger()

    if axi4_bus_name == '':
        daqt1 = MIXDAQT1SGREmulator(axi4_bus=None, ad717x_chip='AD7175', ad717x_mvref=5000,
                                    use_spi=True, use_gpio=False)
        ad7175 = None
        spi_bus = None
    elif 'DAQT1' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8000)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=True, use_gpio=False)
        ad7175 = None
        spi_bus = None
    else:
        daqt1 = None
        ad717x_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8192)
        ad7175 = MIXAd7175SG(ad717x_axi4_bus, 5000)

        if spi_axi4_bus_name == '':
            spi_bus = None
        else:
            spi_axi4_bus = AXI4LiteBus(spi_axi4_bus_name, 0x8192)
            spi_bus = PLSPIBus(spi_axi4_bus)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
        i2c_bus = MIXI2CSG(axi4_bus)

    omega.omega = Omega(i2c=i2c_bus,
                        ip=daqt1,
                        ad7175=ad7175,
                        spi=spi_bus)
    return omega


if __name__ == '__main__':
    '''
    python omega_tool.py
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ip', help='ipcore device file name',
                        default='/dev/MIX_DAQT1_0')
    parser.add_argument('-spi', '--spi', help='spi device file name',
                        default='')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name',
                        default='/dev/MIX_I2C_0')

    args = parser.parse_args()
    omega_dbg = create_omega_dbg(args.ip, args.spi, args.i2c)

    omega_dbg.cmdloop()
