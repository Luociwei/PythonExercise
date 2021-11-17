# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_macfct_spireturn_sg import MIXMacFCTSpiReturnSG

__author__ = 'shunreng.he@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class SpiReturnDebuger(cmd.Cmd):
    prompt = 'spi_return>'
    intro = 'Xavier spin return debug tool'

    @handle_errors
    def do_set_mode(self, line):
        '''
        spi return set mode
        mode: int,[0, 1, 2, 3],    0:CPOL=0,CPHA=0;
                                   1:CPOL=1,CPHA=0;
                                   2:CPOL=0,CPHA=1;
                                   3:CPOL=1,CPHA=1.
        '''
        self.spi_return.set_mode(eval(line))

    @handle_errors
    def do_open(self, line):
        '''spi return open'''
        self.spi_return.open()

    @handle_errors
    def do_close(self, line):
        '''spi return close'''
        self.spi_return.close()

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        del self.spi_return
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_open.__doc__)
        print(self.do_close.__doc__)
        print(self.do_set_mode.__doc__)


def create_dma_dbg(dev_name):
    spi_return_dbg = SpiReturnDebuger()
    spi_return_dbg.spi_return = MIXMacFCTSpiReturnSG(dev_name)
    return spi_return_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/MIX_MacFCT_SpiReturn_SG_0')
    args = parser.parse_args()

    spi_return_dbg = create_dma_dbg(args.device)

    spi_return_dbg.cmdloop()
