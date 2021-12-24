# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r_emulator import MIXDAQT1SGREmulator
from mix.driver.smartgiant.cloak.module.scope002006 import Scope002006

__author__ = 'shunreng.he@SmartGiant'
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


class Scope002006Debuger(cmd.Cmd):
    prompt = 'Scope002006>'
    intro = 'Xavier Scope002006 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_module_init(self, line):
        '''module_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.module_init()
        print("Done")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate
        Scope002006 set ad7175 sampling rate
        sampling_rate:  int,ad7175 sampling rate, value is 5 SPS to 10 kSPS.
        eg: set_sampling_rate 10000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.set_sampling_rate('CURR', eval(line))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel
        Scope002006 get sampling rate of adc.
        eg: get_sampling_rate '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.get_sampling_rate('CURR')
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure
        Scope002006 measure current once'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.current_measure()
        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_current_measure(self, line):
        '''multi_points_current_measure
        Scope002006 measure current in continuous mode
        count: int,    number current value to be get
        eg: multi_points_current_measure 10 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.multi_points_current_measure(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_measure_enable(self, line):
        '''multi_points_measure_enable
        Scope002006 start continuous measure
        sampling_rate:  int,ad7175 sampling rate, value is 5 SPS to 10 kSPS.
        eg: multi_points_measure_enable '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.multi_points_measure_enable('CURR')
        print("Done.")

    @handle_errors
    def do_multi_points_measure_disable(self, line):
        '''multi_points_measure_disable
        Scope002006 stop continuous measure
        eg: multi_points_measure_disable '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.multi_points_measure_disable('CURR')
        print("Done.")

    @handle_errors
    def do_mode(self, line):
        '''mode mode
        Scope002006 set continue_sample_mode
        mode:  True/False
        eg: mode False '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.mode = eval(line)
        print("Done.")

    def do_read_register(self, line):
        '''read_register
        MIXAD717X read the register value
        reg_addr: hex(0x00~0x3F)      register address
        eg: read_register 0x00 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    def do_write_register(self, line):
        '''write_register
        MIXAD717X write the register value
        reg_addr:  hex(0x00~0x3F)      Register address.
        reg_value: int                 Register value to be write.
        eg: write_register 0x10 30 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.omega.scope002006.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature
        Scope002006 read temperature from sensor
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.get_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Scope002006 enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Scope002006 query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.is_use_cal_data()
        print('Result:')
        print(result)

    @handle_errors
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
        self.scope002006.write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        unit_index: int, calibration unit index
        eg: read_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope002006.read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell
        MIXBoard erase calibration unit
        unit_index: int, calibration unit index
        eg: erase_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope002006.erase_calibration_cell(*list(eval(line)))
        print("Done.")

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


def create_scope_dbg(axi4_bus_name, i2c_bus_name):
    scope_dbg = Scope002006Debuger()

    if axi4_bus_name == '':
        daqt1 = MIXDAQT1SGREmulator(axi4_bus=None, ad717x_chip='AD7175', ad717x_mvref=2500,
                                    use_spi=False, use_gpio=False)
        ad7175 = None
    elif 'MIX_Scope' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8000)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=2500,
                            use_spi=False, use_gpio=False)
        ad7175 = None
    elif 'MIX_DAQT' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8000)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=2500,
                            use_spi=False, use_gpio=False)
        ad7175 = None
    else:
        daqt1 = None
        ad717x_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x8192)
        ad7175 = MIXAd7175SG(ad717x_axi4_bus, 2500)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        i2c_bus = I2C(i2c_bus_name)

    scope_dbg.scope002006 = Scope002006(i2c=i2c_bus, ad7175=ad7175, ipcore=daqt1)
    return scope_dbg


if __name__ == '__main__':
    '''
    ***setup:
        module_init
    ***measure single current step:
        1.disable_continuous_measure
        2.measure single current
    ***measure continue current step:
        1.enable_continuous_measure
        2.measure continue current
    ***when from continue mode to single mode,you have to stop_continuous_measure first.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ip', help='ipcore device file name',
                        default='/dev/MIX_Scope_002_006')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name',
                        default='/dev/MIX_I2C_0')

    args = parser.parse_args()
    scope_dbg = create_scope_dbg(args.ip, args.i2c)
    scope_dbg.cmdloop()
