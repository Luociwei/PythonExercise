# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.beast.module.scope001002 import Scope001002
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG

__author__ = 'Chujie.Lan@SmartGiant'
__version__ = '1.2'


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


class Scope001002Debuger(cmd.Cmd):
    prompt = 'scope001002>'
    intro = 'Xavier scope001002 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_select_range(self, line):
        '''select_range
        Scope001002 select measure range
        signal_type: str('DC_VOLT', 'AC_VOLT')
        value:       int(2/20)
        eg: select_range 'AC_VOLT' 2 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.scope001002.select_range(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_enable_continuous_measure(self, line):
        '''enable_continuous_measure
        Scope001002 enable upload function
        board data will be copyed to dma when this function called'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope001002.enable_continuous_measure()
        print("Done")

    @handle_errors
    def do_disable_continuous_measure(self, line):
        '''disable_continuous_measure
        Scope001002 disable upload function'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope001002.disable_continuous_measure()
        print("Done")

    @handle_errors
    def do_frequency_measure(self, line):
        '''frequency_measure
        Scope001002 measure input signal frequency function
        duration: int, Measure millisecond time
        eg: frequency_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope001002.frequency_measure(eval(line))
        print("Result:")
        print("Freq={}Hz, Duty={}%".format(result[0], result[1]))

    @handle_errors
    def do_vpp_measure(self, line):
        '''vpp_measure
        Scope001002 measure input signal vpp function
        duration: int, Measure millisecond time
        eg: vpp_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope001002.vpp_measure(eval(line))
        print("Result:")
        print("vpp={:.6} mV, max={:.6} mV, min={:.6} mV".format(result[0], result[1], result[2]))

    @handle_errors
    def do_rms_measure(self, line):
        '''rms_measure
        Scope001002 measure input signal rms value
        duration: int, Measure millisecond time
        eg: rms_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope001002.rms_measure(eval(line))
        print("Result:")
        print("rms={:.6} mV, average={:.6} mV".format(result[0], result[1]))

    @handle_errors
    def do_get_level(self, line):
        '''get_level
        Scope001002 get current voltage level'''
        if '?' == line:
            print(get_function_doc(self))
        result = self.scope001002.get_level()
        print("Result:")
        print("level={}".format(result))

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Scope001002 enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.scope001002.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Scope001002 query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.scope001002.is_use_cal_data()
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
        print(self.do_enable_continuous_measure.__doc__)
        print(self.do_disable_continuous_measure.__doc__)
        print(self.do_select_range.__doc__)
        print(self.do_frequency_measure.__doc__)
        print(self.do_vpp_measure.__doc__)
        print(self.do_rms_measure.__doc__)
        print(self.do_get_level.__doc__)
        print(self.do_set_calibration_mode.__doc__)
        print(self.do_is_use_cal_data.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_scope001002_dbg(signal_meter, daqt2_bus_name, i2c_bus_name):
    scope001002_dbg = Scope001002Debuger()

    I2C_bus = AXI4LiteBus(i2c_bus_name, 256)
    i2c = MIXI2CSG(I2C_bus)

    axi4_bus = AXI4LiteBus(signal_meter, 256)
    signal_meter = MIXSignalMeterSG(axi4_bus)
    scope001002_dbg.scope001002 = Scope001002(i2c, None, None, None, signal_meter)
    return scope001002_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-sg', '--signal_meter', help='signal_meter devcie name', default='/dev/MIX_Scope_001_001')
    parser.add_argument('-ipcore', '--daqt2', help='daqt2 devcie name', default='/dev/MIX_Scope_001_001')
    parser.add_argument('-i2c', '--i2c', help='eeprom i2c bus name', default='/dev/MIX_I2C_0')
    args = parser.parse_args()
    scope_dbg = create_scope001002_dbg(args.signal_meter, args.daqt2, args.i2c)

    scope_dbg.cmdloop()
