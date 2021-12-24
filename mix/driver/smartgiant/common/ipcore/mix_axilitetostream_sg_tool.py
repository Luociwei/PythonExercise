# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_axilitetostream_sg import MIXAxiLiteToStreamSG
from mix.driver.smartgiant.common.bus.axi4_lite_bus import AXI4LiteBus


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MIXAxiLiteToStreamSGDebuger(cmd.Cmd):
    prompt = 'axilitetostream>'
    intro = 'Xavier axilitetostream debug tool'

    @handle_errors
    def do_read(self, line):
        '''read'''
        self.axilitetostream.read()
        print('Done.')

    @handle_errors
    def do_write(self, line):
        '''write [data]'''
        self.axilitetostream.write(line)
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write.__doc__)
        print(self.do_read.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_axilitetostream_dbg(dev_name):
    axilitetostream_dbg = MIXAxiLiteToStreamSGDebuger()
    if dev_name == '':
        axi4_bus = None
    else:
        axi4_bus = AXI4LiteBus(dev_name, 256)
    axilitetostream_dbg.axilitetostream = MIXAxiLiteToStreamSG(axi4_bus)
    return axilitetostream_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')

    args = parser.parse_args()

    axilitetostream_dbg = create_axilitetostream_dbg(args.device)

    axilitetostream_dbg.cmdloop()
