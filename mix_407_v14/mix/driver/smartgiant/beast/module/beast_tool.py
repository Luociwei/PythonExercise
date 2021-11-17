# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.beast.module.beast import Beast
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


class BeastDebuger(cmd.Cmd):
    prompt = 'beast>'
    intro = 'Xavier beast debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_select_range(self, line):
        '''select_range
        Beast select measure range
        signal_type: str('DC_VOLT', 'AC_VOLT')
        value:       int(2/20)
        eg: select_range 'AC_VOLT' 2 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.beast.select_range(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_enable_continuous_measure(self, line):
        '''enable_continuous_measure
        Beast enable upload function
        board data will be copyed to dma when this function called'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.beast.enable_continuous_measure()
        print("Done")

    @handle_errors
    def do_disable_continuous_measure(self, line):
        '''disable_continuous_measure
        Beast disable upload function'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.beast.disable_continuous_measure()
        print("Done")

    @handle_errors
    def do_frequency_measure(self, line):
        '''frequency_measure
        Beast measure input signal frequency function
        duration: int, Measure millisecond time
        eg: frequency_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.beast.frequency_measure(eval(line))
        print("Result:")
        print("Freq={}Hz, Duty={}%".format(result[0], result[1]))

    @handle_errors
    def do_vpp_measure(self, line):
        '''vpp_measure
        Beast measure input signal vpp function
        duration: int, Measure millisecond time
        eg: vpp_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.beast.vpp_measure(eval(line))
        print("Result:")
        print("vpp={:.6} mV, max={:.6} mV, min={:.6} mV".format(result[0], result[1], result[2]))

    @handle_errors
    def do_rms_measure(self, line):
        '''rms_measure
        Beast measure input signal rms value
        duration: int, Measure millisecond time
        eg: rms_measure 100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.beast.rms_measure(eval(line))
        print("Result:")
        print("rms={:.6} mV, average={:.6} mV".format(result[0], result[1]))

    @handle_errors
    def do_get_level(self, line):
        '''get_level
        Beast get current voltage level'''
        if '?' == line:
            print(get_function_doc(self))
        result = self.beast.get_level()
        print("Result:")
        print("level={}".format(result))

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Beast enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.beast.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Beast query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.beast.is_use_cal_data()
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


def create_beast_dbg(signal_meter, daqt2_bus_name, i2c_bus_name):
    beast_dbg = BeastDebuger()

    I2C_bus = AXI4LiteBus(i2c_bus_name, 256)
    i2c = MIXI2CSG(I2C_bus)

    axi4_bus = AXI4LiteBus(signal_meter, 256)
    signal_meter = MIXSignalMeterSG(axi4_bus)
    beast_dbg.beast = Beast(i2c, None, None, None, signal_meter)
    return beast_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-sg', '--signal_meter', help='signal_meter devcie name', default='/dev/MIX_Scope_001_001')
    parser.add_argument('-ipcore', '--daqt2', help='daqt2 devcie name', default='/dev/MIX_Scope_001_001')
    parser.add_argument('-i2c', '--i2c', help='eeprom i2c bus name', default='/dev/MIX_I2C_0')
    args = parser.parse_args()
    scope_dbg = create_beast_dbg(args.signal_meter, args.daqt2, args.i2c)

    scope_dbg.cmdloop()
