# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.axi4_lite_def import MIXAidSlaveSGDef
from mix.driver.smartgiant.common.ipcore.mix_aidslave_sg import MIXAidSlaveSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MIXAidSlaveSGDebuger(cmd.Cmd):
    prompt = 'aid>'
    intro = 'Xavier aid slave debug tool'

    @handle_errors
    def do_open(self, line):
        '''open'''
        self.aid.open()
        print('Done.')

    @handle_errors
    def do_close(self, line):
        '''close'''
        self.aid.close()
        print('Done.')

    @handle_errors
    def do_config_command(self, line):
        '''config_command [index] [req_data] [req_mask] [rep_data]'''
        line = line.replace(' ', ',')
        self.aid.config_command(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_open.__doc__)
        print(self.do_close.__doc__)
        print(self.do_config_command.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_aid_dbg(dev_name):
    aid_dbg = MIXAidSlaveSGDebuger()
    if dev_name == '':
        axi4_bus = None
    else:
        axi4_bus = AXI4LiteBus(dev_name, MIXAidSlaveSGDef.REG_SIZE)
    aid_dbg.aid = MIXAidSlaveSG(axi4_bus)
    return aid_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')

    args = parser.parse_args()

    aid_dbg = create_aid_dbg(args.device)

    aid_dbg.cmdloop()
