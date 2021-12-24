# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.pl_gpio import PLGPIO
from mix.driver.core.bus.gpio import GPIO
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import *
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.hppsu001.module.hppsu001002 import HPPSU001002

__author__ = 'xuboyan@SmartGiant'
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


class HPPSU001002Debugger(cmd.Cmd):
    prompt = 'hppsu001002>'
    intro = 'Xavier hppsu001002 debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.hppsu.module_init()
        print("Done.")

    @handle_errors
    def do_io_function_ctrl(self, line):
        '''io_function_ctrl <function> <mode>
        <function>: string, ["power_ctrl", "discharge_ctrl", "protect_reset"]
        <mode>: string, ["on", "off"]
        eg: io_function_ctrl ["power_ctrl","on"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.io_function_ctrl(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_fault_state(self, line):
        '''read_fault_state
        return: string, ["OCP", "OVP", "RSFP", "OTP"]
        eg: read_fault_state '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.read_fault_state()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_fault_pin_level(self, line):
        '''get_fault_pin_level
        return: int, 0 for nomal state, 1 for fault state
        eg: get_fault_pin_level '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.get_fault_pin_level()
        print("Result:")
        print(result)

    @handle_errors
    def do_ovp_to_output_ratio_set(self, line):
        '''ovp_to_output_ratio_set <value> <ratio_range>
        <ratio_range>: string, ["10V", "30V"], "10V" is [0~10]V, "30V" is [10~30]V
        <value>: float, [0~2]
        eg: ovp_to_output_ratio_set ["30V",1.05] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.ovp_to_output_ratio_set(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_ovp_to_output_ratio_get(self, line):
        '''ovp_to_output_ratio_get <ratio_range>
        <ratio_range>: string, ["10V", "30V"], "10V" is [0~10]V, "30V" is [10~30]V
        return: float, [0~2]
        eg: ovp_to_output_ratio_get ["30V"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        result = self.hppsu.ovp_to_output_ratio_get(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_output_value(self, line):
        '''set_output_value <channel> <value>
        <channel>: string, ["OCP", "OVP"]
        <value>:
            OCP:            float, [0~30000], unit is mA
            OVP:            float, [0~31500], unit is mV
        eg: set_output_value ["OCP",5000]  '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.set_output_value(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_power_output_voltage(self, line):
        '''power_output_voltage <output> <mode>
        <output>: float, [0~30000]
        <mode>: string, ["debug", "normal"]
        eg: power_output_voltage [5000] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.power_output_voltage(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_adc_register_read(self, line):
        '''adc_register_read <register>
        <register>: hex, [0x00~0x3f]
        eg: adc_register_read [0x07] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.adc_register_read(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_adc_register_write(self, line):
        '''adc_register_write <register> <value>
        <register>: hex, [0x00~0x3f]
        <value>: hex, [0x00~0xffffffff]
        eg: adc_register_write [0x10,30] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.adc_register_write(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate <channel> <sampling_rate>
        <channel>: string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"]
        <sampling_rate>:  float, [5~250000]
        eg: set_sampling_rate ["VOLTAGE_MEASURE",10000] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.set_sampling_rate(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel <channel>
        <channel>: string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"]
        eg: get_sampling_rate ["VOLTAGE_MEASURE"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.get_sampling_rate(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_measure(self, line):
        '''measure <channel>
        <channel>: string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"]
        eg: measure ["VOLTAGE_MEASURE"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_temperature(self, line):
        '''read_temperature
        return: tuple, [ret,unit], unit is C
        eg: read_temperature '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.read_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_eeprom(self, line):
        '''write_eeprom addr <address> <data_list>
        <address>: hex, [0~0xFFFF], eeprom memeroy address.
        <data_list>: int, element for byte data, which you want to write into eeprom.
        eg: write_eeprom [0x50,[0x01,0x20,0x05]] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.write_eeprom(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_eeprom(self, line):
        '''read_eeprom <address> <count>
        <address>: hex, [0~0xFFFF], eeprom memory address.
        <count>: int, [0~1024], Count of datas to be read.
        eg: read_eeprom [0x50,5] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        result = self.hppsu.read_eeprom(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode mode <mode>
        <mode>: string, ["cal", "raw"], "cal": enable calibration, "raw": disable calibration.
        eg: set_cal_mode ["cal"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.hppsu.set_calibration_mode(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode
        return: string, ["cal", "raw"], "cal": enable calibration, "raw": disable calibration.
        eg: get_cal_mode '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.hppsu.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_calibration_item(self, line):
        '''write_calibration_item <cal_index> <range_name> <index> <gain> <offset> <threshold>
        <cal_index>:    int, (>=0), the index in the range to calibration item
        <range_name>:   string, ["VOLTAGE_OUTPUT", "VOLTAGE_MEASURE", "CURRENT_MEASURE", "OCP", "OVP"]
        <index>:        int,    calibration index
        <gain>:         float,  calibration gain
        <offset>:       float,  calibration offset
        <threshold>:    float,  if raw data >= threshold,
                                the cell data will be used to calibrate.
        eg: write_calibration_item [0,"VOLTAGE_MEASURE",0,1.1,0.1,100] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.hppsu.write_calibration_item(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_item(self, line):
        '''read_calibration_item <cal_index> <range_name> <index>
        <cal_index>:    int, (>=0), the index in the range to calibration item
        <range_name>:   string, ["VOLTAGE_OUTPUT", "VOLTAGE_MEASURE", "CURRENT_MEASURE", "OCP", "OVP"]
        <index>:   int, calibration index
        eg: read_calibration_item [0,"VOLTAGE_MEASURE",0] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.hppsu.read_calibration_item(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration_item(self, line):
        '''erase_calibration_item <cal_index> <range_name> <index>
        <cal_index>:    int, (>=0), the index in the range to calibration item
        <range_name>:   string, ["VOLTAGE_OUTPUT", "VOLTAGE_MEASURE", "CURRENT_MEASURE", "OCP", "OVP"]
        <index>:   int, calibration index
        eg: erase_calibration_item [0,"VOLTAGE_MEASURE",0] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.hppsu.erase_calibration_item(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_hppsu001002_dbg(i2c_bus_name, axi4_bus_name, gpio_device_name, fault_pin_id):
    hppsu001002_dbg = HPPSU001002Debugger()
    if i2c_bus_name == '':
        i2c_bus = None
    else:
        i2c_bus = I2C(i2c_bus_name)

    if gpio_device_name == '':
        fault_pin = GPIO(int(fault_pin_id))
    else:
        axi4_bus = AXI4LiteBus(gpio_device_name, 256)
        gpio = PLGPIO(axi4_bus)
        fault_pin = Pin(gpio, int(fault_pin_id))

    if axi4_bus_name == '':
        daqt1 = MIXDAQT1Emulator(axi4_bus=None, ad717x_chip='AD7175', ad717x_mvref=5000,
                                 use_spi=False, use_gpio=False)
        ad7175 = None
    elif 'MIX_DAQT' in axi4_bus_name or 'MIX_AD717X_SG' in axi4_bus_name:
        daqt1_axi4_bus = AXI4LiteBus(axi4_bus_name, 65535)
        daqt1 = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=False, use_gpio=False)
        ad7175 = None
    else:
        daqt1 = None
        ad717x_axi4_bus = AXI4LiteBus(axi4_bus_name, 0x4000)
        ad7175 = MIXAd7175SG(ad717x_axi4_bus, 5000)

    hppsu001002_dbg.hppsu = HPPSU001002(i2c=i2c_bus, ad7175=ad7175, fault_pin=fault_pin, ipcore=daqt1)
    hppsu001002_dbg.hppsu.module_init()
    return hppsu001002_dbg


arguments = [
    ['-i2c', '--i2c', 'i2c bus name', '/dev/i2c-1'],
    ['-ip', '--ipcore', 'ipcore device file name', '/dev/MIX_DAQT1_0'],
    ['-gd', '--gpio_device_name', 'gpio device name', ''],
    ['-fault', '--fault_pin_id', 'fault pin id', 86],
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    hppsu001002_dbg = create_hppsu001002_dbg(args.i2c, args.ipcore, args.gpio_device_name, int(args.fault_pin_id))
    hppsu001002_dbg.cmdloop()
