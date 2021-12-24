# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from ..ipcore.iioxadc import IIOXADC


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


class IIOXADCDebuger(cmd.Cmd):
    prompt = 'iioxadc>'
    intro = 'Xavier iioxadc debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_read_temperature(self, line):
        '''read_temperature
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.iioxadc.read_temperature()
        print("Result:")
        print("temperature:{}".format(result))

    @handle_errors
    def do_read_voltage(self, line):
        '''read_volt
        read voltage at single conversion mode
        :param channel:    str('vpvn','vaux0'~'vaux15')
        :param count:      int,            number of voltage to read, deafult is 1
        :returns:          float,          unit is mV
        eg: read_volt "vpvn" 2 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.iioxadc.read_voltage(*list(eval(line)))
        print("Result:")
        print("voltage:{}mV".format(result))

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
        print(self.do_read_temperature.__doc__)
        print(self.do_read_voltage.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_iioxadc_dbg(devcie):
    iioxadc_dbg = IIOXADCDebuger()

    iioxadc_dbg.iioxadc = IIOXADC(devcie)
    return iioxadc_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-dev', '--devive_name', help='xadc device name', default='iio:device0')
    args = parser.parse_args()
    xadc_dbg = create_iioxadc_dbg(args.devive_name)

    xadc_dbg.cmdloop()
