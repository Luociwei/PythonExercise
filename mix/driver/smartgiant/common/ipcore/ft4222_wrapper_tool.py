# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps

from ft4222_wrapper import FT4222Wrapper

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class FT4222WrapperDebuger(cmd.Cmd):
    prompt = 'ft4222Wrapper>'
    intro = 'Xavier ft4222Wrapper debug tool'

    @handle_errors
    def do_open(self, line):
        '''open use_gpio '''
        line = line.replace(' ', ',')
        self.ft4222Wrapper.open(eval(line))
        print('Done')

    @handle_errors
    def do_close(self, line):
        '''close'''
        line = line.replace(' ', ',')
        self.ft4222Wrapper.close()
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print("Usage:")
        print(self.do_open.__doc__)
        print(self.do_close.__doc__)
        print(self.do_quit.__doc__)


def create_FT4222Wrapper_dbg(locid_a, locid_b, ad717x_chip, mvref, code_polar, reference,
                             buffer_flag, clock, ioline, speed, mode, ssomap, use_gpio, delay):

    FT4222Wrapper_dbg = FT4222WrapperDebuger()
    FT4222Wrapper_dbg.ft4222Wrapper = FT4222Wrapper(locid_a, locid_b, ad717x_chip, mvref, code_polar, reference,
                                                    buffer_flag, clock, ioline, speed, mode, ssomap, use_gpio, delay)
    return FT4222Wrapper_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id_a', '--locid_a', help='locid of FT4222 device for spi', default='0')
    parser.add_argument('-id_b', '--locid_b', help='locid of FT4222 device for gpio', default='1')
    parser.add_argument('-chip', '--ad717x_chip', help='ADC chip type(AD7175/AD7177)', default='AD7175')
    parser.add_argument('-v', '--mvref', help='voltage reference', default='5000')
    parser.add_argument('-cp', '--code_polar', help='adc polar mode', default='bipolar')
    parser.add_argument('-r', '--reference', help='Select voltage reference', default='extern')
    parser.add_argument('-b', '--buffer_flag', help='Enable or disable input buffer', default='enable')
    parser.add_argument('-cl', '--clock', help=' adc clock mode', default='crystal')
    parser.add_argument('-io', '--ioline', help='SPI/DSPI/QSPI', default='SPI')
    parser.add_argument('-s', '--speed', help='FTSPI clock speed', default='64')
    parser.add_argument('-m', '--mode', help='FTSPI clock Polarity and clock Phase', default='MODE3')
    parser.add_argument('-ss', '--ssomap', help='FTSPI slave selection output pins bitmap', default='SS0O')
    parser.add_argument('-u', '--use_gpio', help='gpio use flag', default='False')
    parser.add_argument('-d', '--delay', help='delay between Init and Write', default='0')
    args = parser.parse_args()

    FT4222Wrapper_dbg = create_FT4222Wrapper_dbg(args.locid_a, args.locid_b, args.ad717x_chip
                                                 int(args.mvref), args.code_polar, args.reference,
                                                 args.buffer_flag, args.clock, args.ioline, int(args.speed),
                                                 args.mode, args.ssomap, args.use_gpio, int(args.delay))

    FT4222Wrapper_dbg.cmdloop()
