# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_macfct_eepromprivate_sg import MIXMacFCTEepromPrivateSG

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


class EepromPrivateDebuger(cmd.Cmd):
    prompt = 'eeprom_private>'
    intro = 'Xavier eeprom private debug tool'

    @handle_errors
    def do_config(self, line):
        '''
        i2c slave config [speed_hz] [device_addr] [reg_len] [data_len]
        '''
        line = line.replace(' ', ',')
        self.eeprom_private.config(*list(eval(line)))

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        del self.eeprom_private
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_config.__doc__)


def create_dma_dbg(dev_name):
    eeprom_private_dbg = EepromPrivateDebuger()
    eeprom_private_dbg.eeprom_private = MIXMacFCTEepromPrivateSG(dev_name)
    return eeprom_private_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/MIX_MacFCT_EepromPrivate_SG_0')
    args = parser.parse_args()

    eeprom_private_dbg = create_dma_dbg(args.device)

    eeprom_private_dbg.cmdloop()
