# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.magik.module.magik import Magik


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


def create_dbg():
    dbg = MagikDebuger()
    signal_meter_0 = MIXSignalMeterSG(AXI4LiteBus('/dev/MIX_SignalMeter_0', 8192))
    signal_meter_1 = MIXSignalMeterSG(AXI4LiteBus('/dev/MIX_SignalMeter_0', 8192))
    spi = MIXQSPISG(AXI4LiteBus('/dev/MIX_QSPI_1', 8192))
    i2c = MIXI2CSG(AXI4LiteBus('/dev/MIX_I2C_1', 8192))

    dbg.magik = Magik(None, signal_meter_0, signal_meter_1, spi, i2c)

    return dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    dbg = create_dbg()

    dbg.cmdloop()
