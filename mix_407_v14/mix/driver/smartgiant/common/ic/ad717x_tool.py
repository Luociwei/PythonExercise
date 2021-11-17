# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.smartgiant.common.bus.ft_ftspi import FTSPI
from mix.driver.smartgiant.common.ic.ad717x import AD7175, AD7177

__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD717XDebuger(cmd.Cmd):
    prompt = 'ad717x>'
    intro = 'Xavier ad717x debug tool'

    @handle_errors
    def do_channel_init(self, line):
        '''channel_init'''
        line = line.replace(' ', ',')
        self.ad717x.channel_init()
        print('Done')

    @handle_errors
    def do_reset(self, line):
        '''reset <register_state>
        <register_state>: dict/None, {0x10:0x8001, 0x11:0x9043}
        '''
        line = line.replace(' ', ',')
        self.ad717x.reset(eval(line))
        print('Done')

    @handle_errors
    def do_read_register(self, line):
        '''read_register <reg_addr>
        <reg_addr>: hex(0x00~0x3F)
        '''
        line = line.replace(' ', ',')
        result = self.ad717x.read_register(eval(line))
        print(result)

    @handle_errors
    def do_write_register(self, line):
        '''write_register <reg_addr>
        <reg_addr>: hex(0x00~0x3F)
        <reg_data>: int
        '''
        line = line.replace(' ', ',')
        self.ad717x.write_register(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_set_setup_register(self, line):
        '''set_setup_register <channel> <code_polar> <reference> <buffer_flag>
        <channel>: string("ch0"/"ch1"/"ch2"/"ch3")
        <code_polar>: string("unipolar"/"bipolar")
        <reference>: string("extern"/"internal"/"AVDD-AVSS")
        <buffer_flag>: string("enable"/"disable")
        '''
        line = line.replace(' ', ',')
        self.ad717x.set_setup_register(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate <channel> <rate>
        <channel>: str("ch0"~"ch3")/int(0-3)
        <rate>: int
        '''
        line = line.replace(' ', ',')
        self.ad717x.set_sampling_rate(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate <channel>
        <channel>: str("ch0"~"ch3")/int(0-3)
        '''
        line = line.replace(' ', ',')
        result = self.ad717x.get_sampling_rate(eval(line))
        print('result')

    @handle_errors
    def do_set_channel_state(self, line):
        '''set_channel_state <channel>  <state>
        <channel>: str("ch0"~"ch3")/int(0-3)
        <state>: str("enable", "disable")
        '''
        line = line.replace(' ', ',')
        self.ad717x.set_channel_state(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_select_single_channel(self, line):
        '''select_single_channel <channel>
        <channel>: str("ch0"~"ch3")/int(0-3)
        '''
        line = line.replace(' ', ',')
        self.ad717x.do_select_single_channel(eval(line))
        print('Done')

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt <channel> <timeout_sec>
        <channel>: str("ch0"~"ch3")/int(0-3)
        <timeout_sec>: int
        '''
        line = line.replace(' ', ',')
        result = self.ad717x.read_volt(*list(eval(line)))
        print(result)

    @handle_errors
    def do_is_communication_ok(self, line):
        '''is_communication_ok'''
        line = line.replace(' ', ',')
        result = self.ad717x.is_communication_ok()
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_channel_init.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_set_setup_register.__doc__)
        print(self.do_set_sampling_rate.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_set_channel_state.__doc__)
        print(self.do_select_single_channel.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_is_communication_ok.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad717x(ftspi, mvref, code_polar, reference, buffer_flag, clock, dac):
    if dac == 7175:
        ad717x = AD7175(ftspi, mvref, code_polar, reference, buffer_flag, clock, dac)
    else:
        ad717x = AD7177(ftspi, mvref, code_polar, reference, buffer_flag, clock, dac)

    return ad717x


def create_ad717x_dbg(locid, mvref, code_polar, reference, buffer_flag, clock, dac):
    ad717x_dbg = AD717XDebuger()
    ft4222 = FT4222(locid)
    ftspi = FTSPI(ft4222, 'SPI', 64, 'MODE3', 'SS0O')
    ad717x_dbg.ad717x = create_ad717x(ftspi, mvref, code_polar, reference, buffer_flag, clock, dac)
    return ad717x_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--locid', help='locid of FT4222 device', default='0')
    parser.add_argument('-v', '--mvref', help='voltage reference', default='5000')
    parser.add_argument('-cp', '--code_polar', help='adc polar mode', default='bipolar')
    parser.add_argument('-r', '--reference', help='Select voltage reference', default='extern')
    parser.add_argument('-b', '--buffer_flag', help='Enable or disable input buffer', default='enable')
    parser.add_argument('-cl', '--clock', help=' adc clock mode', default='crystal')
    parser.add_argument('-dac', '--dac', help='dac name', default='7175')

    args = parser.parse_args()

    ad717x_dbg = create_ad717x_dbg(args.locid, int(args.mvref), args.code_polar,
                                   args.reference, args.buffer_flag, args.clock, int(args.dac))

    ad717x_dbg.cmdloop()
