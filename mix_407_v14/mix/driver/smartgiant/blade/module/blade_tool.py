# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.gpio import GPIO
from mix.driver.smartgiant.common.ipcore.mix_ad760x_sg import MIXAd7608SG
from mix.driver.smartgiant.common.ipcore.mix_xadc_sg import MIXXADCSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_qi_asklink_encode_sg import MIXQIASKLinkEncodeSG
from mix.driver.smartgiant.common.ipcore.mix_qi_fsklink_decode_sg import MIXQIFSKLinkDecodeSG
from mix.driver.smartgiant.blade.module.blade import Blade

__author__ = 'weiping.mo@SmartGiant'
__version__ = '1.0'


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


class BladeDebuger(cmd.Cmd):
    prompt = 'blade>'
    intro = 'Xavier blade debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_module_init(self, line):
        '''module_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.blade.module_init()
        print("Done")

    @handle_errors
    def do_dac_output(self, line):
        '''dac_output
        Blade adc output voltage, 0-5500mV.
        dac_channel:    string('ch0'-'ch5')
        voltage:        float/int(0~5500), unit is mV
        eg:             dac_output 'ch0',1000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.blade.dac_output(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_ac_signal_measure(self, line):
        '''ac_signal_measure
        Blade AC signal measurement
        option:        string('f','d','v','w')
        amplitude:     int(0~5000), unit is mV
        time_ms:       int(0-2000), unit is ms
        eg:            ac_signal_measure 'f',2500,1000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.blade.ac_signal_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_adc_voltage_measure(self, line):
        '''adc_voltage_measure
        Blade ADC read voltage
        option:        string('AVG','AVG')
        adc_channel:   string('ch0'-'ch7')
        adc_range:     string('10V'/'5V'), adc reference voltage range
        sampling_rate: int(2000-200000), adc sampling_rate 2000~200000Hz
        sampling_count: int
        time_ms:       int(0-2000), unit is ms
        eg:            adc_voltage_measure 'avg','ch0','5V',20000,10,100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.blade.adc_voltage_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_ask_write_encode_data(self, line):
        '''ask_write_encode_data
        Blade send ASK signal (square wave)
        data:  list, Data to write, the list element is an integer
        freq:  int, 100-100000
        eg:             ask_write_encode_data [1,2,3,4,5],2000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.blade.ask_write_encode_data(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_fsk_frequency_measure(self, line):
        '''fsk_frequency_measure
        Blade measure FSK signal frequency
        time_ms: int(0-2000), unit is ms
        eg: fsk_frequency_measure 2000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.blade.fsk_frequency_measure(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_fsk_decode_state(self, line):
        '''fsk_decode_state
        Blade Get Fsk Decode state'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.blade.fsk_decode_state()
        print('Result:')
        print(result)

    @handle_errors
    def do_fsk_read_decode_data(self, line):
        '''fsk_read_decode_data
        Blade receive FSK signal'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.blade.fsk_read_decode_data()
        print('Result:')
        print(result)

    @handle_errors
    def do_adc_measure_upload_enable(self, line):
        '''adc_measure_upload_enable
        Blade adc measure data upoad mode open.
        adc_range:     string('10V'/'5V'), adc reference voltage range
        sampling_rate: int(2000-200000), adc sampling_rate 2000~200000Hz
        eg:             adc_measure_upload_enable '5V',2000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.blade.adc_measure_upload_enable(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_adc_measure_upload_disable(self, line):
        '''adc_measure_upload_disable
        Blade upoad mode close'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.blade.adc_measure_upload_disable()
        print("Done")

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Beast enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.blade.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Beast query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.blade.is_use_cal_data()
        print('Result:')
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
        self.blade.write_calibration_cell(*list(eval(line)))
        print("Done.")

    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        unit_index: int, calibration unit index
        eg: read_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.blade.read_calibration_cell(eval(line))
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
        self.blade.erase_calibration_cell(*list(eval(line)))
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


def create_blade_dbg(i2c_dev_name,
                     adc_dev_name,
                     xadc_dev_name,
                     adc_signal_meter_dev_name,
                     ac_signal_meter_dev_name,
                     fsk_signal_meter_dev_name,
                     ask_code_dev_name,
                     fsk_decode_dev_name):
    blade_dbg = BladeDebuger()

    if i2c_dev_name is '':
        i2c = None
    else:
        i2c = I2C(i2c_dev_name)

    if adc_dev_name is '':
        ad7608 = None
    else:
        axi4_bus = AXI4LiteBus(adc_dev_name, 8192)
        ad7608 = MIXAd7608SG(axi4_bus)

    if xadc_dev_name is '':
        xadc = None
    else:
        axi4_bus = AXI4LiteBus(xadc_dev_name, 2048)
        xadc = MIXXADCSG(axi4_bus)

    if adc_signal_meter_dev_name is '':
        adc_signal_meter = None
    else:
        axi4_bus = AXI4LiteBus(adc_signal_meter_dev_name, 1024)
        adc_signal_meter = MIXSignalMeterSG(axi4_bus)

    if ac_signal_meter_dev_name is '':
        ac_signal_meter = None
    else:
        axi4_bus = AXI4LiteBus(ac_signal_meter_dev_name, 1024)
        ac_signal_meter = MIXSignalMeterSG(axi4_bus)

    if fsk_signal_meter_dev_name is '':
        fsk_signal_meter = None
    else:
        axi4_bus = AXI4LiteBus(fsk_signal_meter_dev_name, 1024)
        fsk_signal_meter = MIXSignalMeterSG(axi4_bus)

    if ask_code_dev_name is '':
        ask_code = None
    else:
        axi4_bus = AXI4LiteBus(ask_code_dev_name, 8192)
        ask_code = MIXQIASKLinkEncodeSG(axi4_bus)

    if fsk_decode_dev_name is '':
        fsk_decode = None
    else:
        axi4_bus = AXI4LiteBus(fsk_decode_dev_name, 8192)
        fsk_decode = MIXQIFSKLinkDecodeSG(axi4_bus)

    adc_ctrl_pin = GPIO(92)
    fsk_ctrl_pin = GPIO(94)
    fsk_cic_ctrl_pin = GPIO(93)
    adc_filter_pin_0 = GPIO(86)
    adc_filter_pin_1 = GPIO(87)
    adc_filter_pin_2 = GPIO(88)

    blade_dbg.blade = Blade(i2c=i2c,
                            adc=ad7608,
                            xadc=xadc,
                            adc_signal_meter=adc_signal_meter,
                            ac_signal_meter=ac_signal_meter,
                            fsk_signal_meter=fsk_signal_meter,
                            ask_code=ask_code,
                            fsk_decode=fsk_decode,
                            adc_ctrl_pin=adc_ctrl_pin,
                            fsk_ctrl_pin=fsk_ctrl_pin,
                            fsk_cic_ctrl_pin=fsk_cic_ctrl_pin,
                            adc_filter_pin_0=adc_filter_pin_0,
                            adc_filter_pin_1=adc_filter_pin_1,
                            adc_filter_pin_2=adc_filter_pin_2)
    return blade_dbg


if __name__ == '__main__':
    '''
    python blade_tool.py
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-i2c', '--i2c', help='i2c bus name for blade',
                        default='/dev/i2c-2')
    parser.add_argument('-adc', '--adc', help='MIXAd7608SG devcie name',
                        default='/dev/MIX_AD760x_v1_0')
    parser.add_argument('-xadc', '--xadc', help='XADC devcie name',
                        default='/dev/MIX_XADC_0')
    parser.add_argument(
        '-sg0', '--sg_adc', help='signal_meter adc devcie name',
        default='/dev/MIX_SignalMeter_1')
    parser.add_argument(
        '-sg1', '--sg_freq', help='signal_meter frequency devcie name',
        default='/dev/MIX_SignalMeter_0')
    parser.add_argument(
        '-sg2', '--sg_fsk', help='signal_meter fsk devcie name',
        default='/dev/MIX_SignalMeter_2')
    parser.add_argument(
        '-ask', '--ask_code', help='ASK encode devcie name',
        default='/dev/MIX_QI_ASKLink_Encode_0')
    parser.add_argument(
        '-fsk', '--fsk_decode', help='FSK decode devcie name',
        default='/dev/MIX_QI_FSKLink_Decode_0')
    args = parser.parse_args()

    blade_dbg = create_blade_dbg(args.i2c, args.adc,
                                 args.xadc, args.sg_adc, args.sg_freq,
                                 args.sg_fsk, args.ask_code, args.fsk_decode)
    blade_dbg.cmdloop()
