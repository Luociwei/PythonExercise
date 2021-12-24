# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.magik.module.scope005004_map import Magik


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = 'V0.1.1'


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


class MagikDebuger(cmd.Cmd):
    prompt = 'MagikDebuger>'
    intro = 'Xavier Magik debug tool'

    magik = None

    @handle_errors
    def do_call(self, line):
        '''call function()
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = eval("self.magik.{}".format(line))
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_dbg(ipcore_name, signal_meter_0, signal_meter_1, spi_bus_name, i2c_bus_name):
    dbg = MagikDebuger()
    ipcore = None
    signal_meter0 = None
    signal_meter1 = None
    if ipcore_name != '':
        ipcore = ipcore_name
    elif signal_meter_0 and signal_meter_1:
        axi4_bus = AXI4LiteBus(signal_meter_0, 256)
        signal_meter0 = MIXSignalMeterSG(axi4_bus)
        axi4_bus = AXI4LiteBus(signal_meter_1, 256)
        signal_meter1 = MIXSignalMeterSG(axi4_bus)

    spi = MIXQSPISG(AXI4LiteBus(spi_bus_name, 8192))
    i2c = I2C(i2c_bus_name)

    dbg.magik = Magik(ipcore, signal_meter0, signal_meter1, spi, i2c)

    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--ipcore', help='Aggregated ipcore name', default='/dev/MIX_DAQT2_0')
    parser.add_argument('-sm0', '--signal_meter_0', help='signal_meter_0', default='')
    parser.add_argument('-sm1', '--signal_meter_1', help='signal_meter_1', default='')
    parser.add_argument('-spi', '--spi', help='spi bus name', default='')
    parser.add_argument('-i2c', '--i2c', help='i2c bus name', default='/dev/i2c-1')
    args = parser.parse_args()

    dbg = create_dbg(args.ipcore, args.signal_meter_0, args.signal_meter_1, args.spi, args.i2c)

    dbg.cmdloop()
