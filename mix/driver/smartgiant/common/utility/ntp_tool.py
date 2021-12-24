# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.utility.ntp import NTP, AXI4UTC

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class NTPDebuger(cmd.Cmd):
    prompt = 'NTP server>'
    intro = 'Xavier NTP server debug tool'

    ntp = None
    utc = None

    @handle_errors
    def do_set_rtc(self, line):
        ''' set_rtc <timestamp>, timestamp: 1538296130  #2018-09-30 16:28:50 CST '''
        timestamp = line
        self.ntp.set_rtc(timestamp)
        print('Done')
        return

    @handle_errors
    def do_get_rtc(self, line):
        ''' get_rtc , return timestamp '''

        timestamp = self.ntp.get_rtc()
        print('Result: %s' % timestamp)
        return

    @handle_errors
    def do_set_ntp_server(self, line):
        ''' set_ntp_server <IP>, IP:169.254.1.10 '''
        self.ntp.set_ntp_server(line)
        print('Done')
        return

    @handle_errors
    def do_set_fpga_rtc(self, line):
        ''' set_fpga_rtc <second> <millisecond>, eg:set_fpga_rtc 1538296130 0'''
        line = line.replace(' ', ',')
        self.utc.set_rtc(*list(eval(line)))
        print('Done')
        return

    @handle_errors
    def do_get_fpga_rtc(self, line):
        ''' get_fpga_rtc ,   return timestamp'''
        second, millisecond = self.utc.get_rtc()
        timestamp = second + millisecond
        print('Result: %s' % timestamp)
        return

    @handle_errors
    def do_quit(self, line):
        ''' quit    quit the debug'''
        return True

    @handle_errors
    def do_help(self, line):
        ''' help    print help info'''
        print("Usage:")
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)
        print(self.do_set_rtc.__doc__)
        print(self.do_get_rtc.__doc__)
        print(self.do_set_ntp_server.__doc__)
        print(self.do_set_fpga_rtc.__doc__)
        print(self.do_get_fpga_rtc.__doc__)


def create_ntp_dbg():
    ntp_dbg = NTPDebuger()
    ntp_dbg.ntp = NTP()
    ntp_dbg.utc = AXI4UTC()
    return ntp_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    ntp_dbg = create_ntp_dbg()
    ntp_dbg.cmdloop()
