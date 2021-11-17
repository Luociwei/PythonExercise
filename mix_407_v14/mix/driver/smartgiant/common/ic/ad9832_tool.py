# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from mix.driver.smartgiant.common.ic.ad9832 import AD9832
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.bus.axi4_lite_def import PLSPIDef
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR

__author__ = 'yongjiu@SmartGiant' + 'weiping.mo@SmartGiant'
__version__ = '0.2'


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


class AD9832Debuger(cmd.Cmd):
    prompt = 'AD9832>'
    intro = 'Xavier ad9832 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_output(self, line):
        '''output
        AD9832 generate waveform output, just support sine waveform
        freq_ch:  str('FREQ0', 'FREQ1')
        freq:     float/int, (0 ~ 25000000) Hz
        phase_ch: str('PHASE0' ~ 'PHASE3')
        phase:    float/int, (0 ~ 2*pi)
        eg: output 'FREQ0',1000,'PHASE0',0 '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9832.output(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_enable_output(self, line):
        '''enable_output
        AD9832 enable waveform output'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ad9832.enable_output()
        print('Done')

    @handle_errors
    def do_stop_output(self, line):
        '''stop_output
        AD9832 stop waveform output'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.ad9832.stop_output()
        print('Done')

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
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_ad9832_dbg(dev_name):
    ad9832_dbg = AD9832Debuger()
    if dev_name == '':
        spi_bus = None
    elif 'DAQT1' in dev_name:
        axi4_bus = AXI4LiteBus(dev_name, 0x8000)
        daqt1 = MIXDAQT1SGR(axi4_bus=axi4_bus, ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=True, use_gpio=False)
        spi_bus = daqt1.spi
    else:
        axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
        spi_bus = MIXQSPISG(axi4_bus)

    spi_bus.set_speed(400000)
    spi_bus.mode = 'MODE1'
    ad9832_dbg.ad9832 = AD9832(spi_bus)
    return ad9832_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name',
                        default='/dev/mix_daqt1_sg_r_0')
    args = parser.parse_args()

    ad9832_dbg = create_ad9832_dbg(args.device)

    ad9832_dbg.cmdloop()
