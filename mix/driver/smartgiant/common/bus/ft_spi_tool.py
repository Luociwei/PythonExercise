# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.smartgiant.common.bus.ft_ftspi import FTSPI
from mix.driver.smartgiant.common.bus.ft4222 import FT4222

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


class FTSPIDebugger(cmd.Cmd):
    prompt = 'ftspi>'
    intro = 'Xavier ftspi bus debug tool'

    @handle_errors
    def do_get_mode(self, line):
        '''get_mode'''
        result = self.ftspi.get_mode()
        print(result)

    @handle_errors
    def do_set_mode(self, line):
        '''set_mode <mode>
        <mode>: 'MODE0'/'MODE1'/'MODE2'/'MODE3'
        '''
        self.ftspi.set_mode(eval(line))
        print('Done')

    @handle_errors
    def do_get_speed(self, line):
        '''get_speed'''
        result = self.ftspi.get_speed()
        print(result)

    @handle_errors
    def do_set_speed(self, line):
        '''set_speed <speed>
        <speed>: 2/4/8/16/32/64/128/512
        '''
        self.ftspi.set_speed(eval(line))
        print('Done')

    @handle_errors
    def do_config_protocol(self, line):
        '''config_protocol <mode>
        <mode>: 'SPI','DSPI','QSPI'
        '''
        self.ftspi.config_protocol(eval(line))
        print('Done')

    @handle_errors
    def do_write(self, line):
        '''write <wr_data>
        <wr_data>: list
        '''
        self.ftspi.write(eval(line))
        print('Done')

    @handle_errors
    def do_read(self, line):
        '''read <rd_len>
        <rd_len>: int
        '''
        result = self.ftspi.read(eval(line))
        print(result)

    @handle_errors
    def do_sync_transfer(self, line):
        '''sync_transfer <wr_data>
        <wr_data>: list
        '''
        result = self.ftspi.sync_transfer(eval(line))
        print(result)

    @handle_errors
    def do_async_transfer(self, line):
        '''async_transfer <wr_data> <rd_len>
        <wr_data>: list
        <rd_len>: int
        '''
        line = line.replace(' ', ',')
        result = self.ftspi.async_transfer(*list(eval(line)))
        print(result)

    @handle_errors
    def do_transfer(self, line):
        '''transfer <wr_data> <rd_len> <sync>
        <wr_data>: list
        <rd_len>: int
        <sync>: bool
        '''
        result = self.ftspi.transfer(*list(eval(line)))
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print('Usage:')
        print(self.do_get_mode.__doc__)
        print(self.do_set_mode.__doc__)
        print(self.do_get_speed.__doc__)
        print(self.do_set_speed.__doc__)
        print(self.do_config_protocol.__doc__)
        print(self.do_read.__doc__)
        print(self.do_write.__doc__)
        print(self.do_read.__doc__)
        print(self.do_sync_transfer.__doc__)
        print(self.do_async_transfer.__doc__)
        print(self.do_transfer.__doc__)
        print(self.do_quit.__doc__)


def create_ftspi_dbg(locid, ioline, speed, mode, ssomap):
    ftspi_dbg = FTSPIDebugger()
    ft4222 = FT4222(locid)
    ftspi_dbg.ftspi = FTSPI(ft4222, ioline, speed, mode, ssomap)
    return ftspi_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--locid', help='locid of FT4222 device', default='0')
    parser.add_argument('-io', '--ioline', help='SPI/DSPI/QSPI', default='SPI')
    parser.add_argument('-c', '--speed', help='FTSPI clock speed', default='64')
    parser.add_argument('-m', '--mode', help='FTSPI clock Polarity and clock Phase', default='MODE3')
    parser.add_argument('-ss', '--ssomap', help='FTSPI slave selection output pins bitmap', default='SS0O')
    args = parser.parse_args()

    ftspi_dbg = create_ftspi_dbg(args.locid, args.ioline, int(args.speed), args.mode, args.ssomap)

    ftspi_dbg.cmdloop()
