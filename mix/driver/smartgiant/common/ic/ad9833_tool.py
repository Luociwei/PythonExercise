# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ad9833 import AD9833
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD9833Debuger(cmd.Cmd):
    prompt = 'ad9833>'
    intro = 'Xavier ad9833 debug tool'

    @handle_errors
    def do_output(self, line):
        '''output freq_chann freq phase_chann phase mode'''
        line = line.replace(' ', ',')
        self.ad9833.output(*list(eval(line)))

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_output.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad9833_dbg(dev_name):
    ad9833_dbg = AD9833Debuger()
    if dev_name == '':
        spi_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            spi_bus = MIXQSPISG(axi4_bus)
            spi_bus.set_mode('MODE1')
        else:
            raise NotImplementedError('ps spi bus not support')
    ad9833_dbg.ad9833 = AD9833(spi_bus)
    return ad9833_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    args = parser.parse_args()

    ad9833_dbg = create_ad9833_dbg(args.device)

    ad9833_dbg.cmdloop()
