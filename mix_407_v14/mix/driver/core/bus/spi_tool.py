# -*- coding: utf-8 -*-
import argparse
import cmd
import os
from functools import wraps
import traceback
from ..utility import utility
from axi4_lite_bus import AXI4LiteBus
from spi import SPI
from pl_spi_bus.py import PLSPIBus
from spi_bus_emulator import SPIBusEmulator


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class SPIBusDebugger(cmd.Cmd):
    prompt = 'spi>'
    intro = 'Xavier spi bus debug tool'
    spi_bus = None

    def _show(self, line):
        print('Mode = ' + self.spi_bus.get_mode())
        print('Speed = ' + str(self.spi_bus.get_speed()))

    def _set_mode(self, line):
        self.spi_bus.set_mode(line)

    def _set_speed(self, line):
        self.spi_bus.set_speed(int(line, 10))

    def _write(self, line):
        line = line.replace(' ', ',')
        self.spi_bus.write(list(eval(line)))
        print('Done.')
        return

    def _read(self, line):
        data = self.spi_bus.read(eval(line))
        print('Result:')
        print(data)
        return

    def _transfer(self, line):
        print(line)
        line = line.replace(' ', ',')
        data = self.spi_bus.transfer(*list(eval(line)))
        print('Write done.Return result:')
        print(data)
        return

    @handle_errors
    def do_show(self, line):
        '''show'''
        self._show(line)

    @handle_errors
    def do_setmode(self, line):
        '''setmode ['MODE0'|'MODE1'|'MODE2'|'MODE3']'''
        self._set_mode(line)

    @handle_errors
    def do_setspeed(self, line):
        '''setspeed [speed]'''
        self._set_speed(line)

    @handle_errors
    def do_write(self, line):
        '''write [data]'''
        self._write(line)

    @handle_errors
    def do_read(self, line):
        '''read [size]'''
        self._read(line)

    @handle_errors
    def do_transfer(self, line):
        '''transfer [data] [read_length]'''
        self._transfer(line)

    @handle_errors
    def do_w(self, line):
        '''w [data] #write command#'''
        self._write(line)

    @handle_errors
    def do_r(self, line):
        '''r [size] #read command#'''
        self._read(line)

    @handle_errors
    def do_tr(self, line):
        '''tr [data] [read_length] #write and read command#'''
        self._transfer(line)

    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        print('Usage:')
        print(self.do_show.__doc__)
        print(self.do_setmode.__doc__)
        print(self.do_setspeed.__doc__)
        print(self.do_read.__doc__)
        print(self.do_r.__doc__)
        print(self.do_write.__doc__)
        print(self.do_w.__doc__)
        print(self.do_transfer.__doc__)
        print(self.do_tr.__doc__)
        print(self.do_quit.__doc__)


def create_spi_dbg(dev_name, reg_size):
    spi_dbg = SPIBusDebugger()
    if dev_name == '':
        spi_dbg.spi_bus = SPIBusEmulator('spi_emulator', reg_size)
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, reg_size)
            spi_dbg.spi_bus = PLSPIBus(axi4_bus)
        else:
            spi_dbg.spi_bus = SPI(dev_name)
    return spi_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default="")
    parser.add_argument('-s', '--size', help='device reserved memory size', default='8192')
    args = parser.parse_args()

    spi_dbg = create_spi_dbg(args.device, int(args.size))

    spi_dbg.cmdloop()
