# -*- coding: utf-8 -*-
import argparse
import cmd
import traceback
import threading
import time
import os
from functools import wraps
from ..utility import utility
from pl_uart_bus import *
from axi4_lite_bus import *
from uart import UART
from uart_bus_emulator import UARTBusEmulator


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class UARTBusDebugger(cmd.Cmd):
    prompt = 'uart>'
    intro = 'Xavier uart bus debug tool'
    uart_bus = None
    receive_done = True
    lock = threading.Lock()

    def _set_uart_conf(self, line):
        '''set uart as 115200,8,N,1'''
        line = line.replace(',', ' ')
        config = line.split(' ')
        baudrate = int(config[0])
        databits = int(config[1])
        parity = 'none'
        if config[2] == 'N':
            parity = 'none'
        elif config[2] == 'O':
            parity = 'odd'
        elif config[2] == 'E':
            parity = 'even'
        stopbits = int(config[3])
        self.uart_bus.set_baudrate(baudrate)
        self.uart_bus.set_databits(databits)
        self.uart_bus.set_parity(parity)
        self.uart_bus.set_stopbits(stopbits)

    def _show_uart_conf(self, line):
        '''show uart conf as 115200,8,N,1'''
        show_str = ""
        show_str += str(self.uart_bus.get_baudrate())
        show_str += ","
        show_str += str(self.uart_bus.get_databits())
        show_str += ","
        if self.uart_bus.get_parity() == 'none':
            show_str += "N,"
        elif self.uart_bus.get_parity() == 'odd':
            show_str += "O,"
        elif self.uart_bus.get_parity() == 'even':
            show_str += "E"
        show_str += str(self.uart_bus.get_stopbits())
        print(show_str)

    def _timestamp_on_off(self, line):
        if line == "on":
            self.uart_bus.set_timestamp(True)
        elif line == "off":
            self.uart_bus.set_timestamp(False)

    def _write(self, line):
        line = line.replace(' ', ',')
        wr_data = eval(line)
        self.lock.acquire()
        self.uart_bus.write_hex([ord(c) for c in wr_data])
        self.lock.release()
        print('Done.')
        return

    def _read(self, line):
        line = line.replace(' ', ',')
        rd_param = eval(line)
        self.lock.acquire()
        if isinstance(rd_param, (int)):
            data = self.uart_bus.read_hex(rd_param)
        else:
            data = self.uart_bus.read_hex(*list(eval(line)))

        string = ''.join([chr(c) for c in data])
        self.lock.release()
        print('Result:')
        print(string)
        return

    def _receive_show_thread(self):
        while self.receive_done is not True:
            self.lock.acquire()
            data = self.uart_bus.read_hex(100, 0.01)
            self.lock.release()
            if len(data) > 0:
                string = ''.join([chr(c) for c in data])
                print(string)
            time.sleep(0.01)

    def do_startread(self, line):
        '''startread'''
        '''
        to start a thread for display data uart readed
        '''
        self.receive_done = False
        self._read_thread = threading.Thread(target=self._receive_show_thread)
        self._read_thread.start()

    def do_stopread(self, line):
        '''stopread'''
        '''
        stop uart data display thread
        '''
        self.receive_done = True
        self._read_thread.join()

    @handle_errors
    def do_show(self, line):
        '''show'''
        self._show_uart_conf(line)

    @handle_errors
    def do_config(self, line):
        '''config [baudrate] [databits] [parity] [stopbits]'''
        self._set_uart_conf(line)

    @handle_errors
    def do_write(self, line):
        '''write [data]'''
        self._write(line)

    @handle_errors
    def do_read(self, line):
        '''read [size]'''
        self._read(line)

    @handle_errors
    def do_w(self, line):
        '''w [data] #write command#'''
        self._write(line)

    @handle_errors
    def do_r(self, line):
        '''r [size] #read command#'''
        self._read(line)

    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        print('Usage:')
        print(self.do_show.__doc__)
        print(self.do_config.__doc__)
        print(self.do_write.__doc__)
        print(self.do_read.__doc__)
        print(self.do_w.__doc__)
        print(self.do_r.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_startread.__doc__)
        print(self.do_stopread.__doc__)

    do_s = do_startread
    do_e = do_stopread


def create_uart_dbg(dev_name, reg_size):
    uart_dbg = UARTBusDebugger()
    if dev_name == '':
        uart_dbg.uart_bus = UARTBusEmulator('uart_emulator', reg_size)
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, reg_size)
            uart_dbg.uart_bus = PLUARTBus(axi4_bus)
        else:
            uart_dbg.uart_bus = UART(dev_name)
    return uart_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default="")
    parser.add_argument('-s', '--size', help='device reserved memory size', default='256')
    args = parser.parse_args()

    uart_dbg = create_uart_dbg(args.device, int(args.size))

    uart_dbg.cmdloop()
