# -*- coding: utf-8 -*-
import argparse
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.module.sg_module_driver_tool import SGModuleDriverDebuger
from mix.driver.smartgiant.wolverine.module.dmm001003_map import Wolverine
from mix.driver.smartgiant.wolverine.module.dmm001003_map import WolverineDef

__author__ = 'jihuajiang@SmartGiant' + 'wenqiang.gao@gzseeing.com'
__version__ = '0.1.2'


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


class WolverineDebugger(SGModuleDriverDebuger):
    prompt = 'wolverine>'
    intro = 'Xavier wolverine debug tool'

    def __init__(self, wolverine):
        self.wolverine = wolverine
        SGModuleDriverDebuger.__init__(self)
        self._mix = super(Wolverine, self.wolverine)

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout_s'''
        self.wolverine.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_sinc(self, line):
        '''set_sinc
        channel: tring('100uA', '2mA', '5V')
        sinc: string("sinc5_sinc1", "sinc3")
        eg. set_sinc "100uA","sinc3"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.wolverine.set_sinc(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_write_module_calibration(self, line):
        '''write_module_calibration
        channel: tring('100uA', '2mA', '5V')
        scalibration_vectors: list, [[module_raw1,benchmark1],
            [module_raw1,benchmark2]]
        eg. write_module_calibration "100uA",[[2000, 2001], [3000, 3001]]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.wolverine.write_module_calibration(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate
        Wolverine get sampling rate of adc
        channel:  string('5V'/'2mA'/'100uA')
        eg: get_sampling_rate '5V' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path
        Wolverine get measure path
        eg: get_measure_path'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_measure_path()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path
        Wolverine set measure path
        channel:  string('5V'/'2mA'/'100uA')
        eg. set_measure_path '5V' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.set_measure_path(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_measure_value(self, line):
        '''read_measure_value
        Wolverine measure voltage or current
        sample_rate:  int(5-250000)
        count: samples count,default 1
        eg: read_measure_value 1000, 1'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.read_measure_value(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_measure_list(self, line):
        '''read_measure_list
        Wolverine measure current or voltage
        sample_rate:  int(5-250000)
        count: samples count,default 1
        eg: read_measure_list 1000, 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.wolverine.read_measure_list(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling
        Wolverine disables continuous mode
        disable_continuous_sampling '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.disable_continuous_sampling()
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling
        Wolverine measure voltage/current in continuous mode
        channel:          string('5V', 2mA','100uA')
        sampling_rate:  int(5-250000), default 1000
        down_sample:  int(5-250000), default 5
        selection:  string('max', 'min'), Default 'max'
        eg: enable_continuous_sampling '2mA',1000,5,'max' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.wolverine.enable_continuous_sampling(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_continuous_sampling_statistics(self, line):
        '''read_continuous_sampling_statistics
        Wolverine measure voltage/current in continuous mode
        count:          int, default 1
        eg: read_continuous_sampling_statistics 2'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.read_continuous_sampling_statistics(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_datalogger_start(self, line):
        '''datalogger_start
        tag: int the value is low 4 bits are valid, from 0x00 to 0x0f'''
        self.wolverine.datalogger_start(eval(line))
        print("Done.")

    @handle_errors
    def do_datalogger_end(self, line):
        '''datalogger_end '''
        self.wolverine.datalogger_end()
        print("Done.")

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr data'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.wolverine.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature
        Wolverine read temperature from sensor
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.read_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        MIXBoard enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        MIXBoard query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.is_use_cal_data()
        print('Result:')
        print(result)

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode raw|cal'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.set_calibration_mode(line)
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.wolverine.get_calibration_mode()
        print("Result:")
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


def create_wolverine_dbg(i2c_dev_name, ad7175,
                         range_ctrl_pin, meter_ctrl_pin, ipcore):
    '''
    cmd: python dmm001003_map_tool.py  -i2c /dev/i2c-0 -rp 86 -mp 87 -ip /dev/MIX_DAQT1_0
    '''
    if utility.is_pl_device(i2c_dev_name):
        axi4_bus = AXI4LiteBus(i2c_dev_name, 256)
        i2c_bus = MIXI2CSG(axi4_bus)
    else:
        i2c_bus = I2C(i2c_dev_name)

    if range_ctrl_pin and meter_ctrl_pin:
        range_ctrl_pin = GPIO(pin_id=int(range_ctrl_pin), default_dir='output')
        meter_ctrl_pin = GPIO(pin_id=int(meter_ctrl_pin), default_dir='output')
    else:
        print "Invalid parameter, please check"

    wolverine_dbg = WolverineDebugger(Wolverine(i2c_bus, ad7175, range_ctrl_pin,
                                      meter_ctrl_pin, ipcore))
    return wolverine_dbg


if __name__ == '__main__':
    '''
    ***measure voltage/current step:
        1.disable_continuous_sampling
        2.set_measure_path
        3.read_measure_value or read_measure_list
    ***measure continue voltage/current step:
        1.enable_continuous_sampling
        2.read_continuous_sampling_statistics
    ***when from continue mode to single mode,you have to disable_continuous_sampling first.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-i2c', '--i2c',
                        help='i2c device name, which is used to control eeprom and nct75', default='')
    parser.add_argument('-ad', '--ad7175', help='ad7175 devcie name',
                        default='')
    parser.add_argument('-rp', '--range_ctrl_pin', help='range select bit', default='')
    parser.add_argument('-mp', '--meter_ctrl_pin', help='meter select bit', default='')
    parser.add_argument('-ip', '--ipcore', help='MIX DAQT1 ipcore device name', default='')
    args = parser.parse_args()
    wolverine_dbg = create_wolverine_dbg(args.i2c, args.ad7175,
                                         args.range_ctrl_pin, args.meter_ctrl_pin, args.ipcore)

    wolverine_dbg.cmdloop()
