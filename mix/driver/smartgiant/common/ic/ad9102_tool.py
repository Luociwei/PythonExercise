# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from ad9102 import AD9102
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.core.bus.pin import Pin


__author__ = "huangjianxuan@SmartGiant, xuboyan@SmartGiant"
__version__ = "1.0"


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


class AD9102Debuger(cmd.Cmd):
    prompt = 'ad9102>'
    intro = 'Xavier ad9102 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_write_register(self, line):
        '''write_register'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.write_register(*list(eval(line)))

    @handle_errors
    def do_read_register(self, line):
        '''read_register'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.read_register(*list(eval(line)))

    @handle_errors
    def do_reset(self, line):
        '''reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.reset(*list(eval(line)))

    @handle_errors
    def do_set_ref_voltage(self, line):
        '''set_ref_voltage'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_ref_voltage(*list(eval(line)))

    @handle_errors
    def do_set_dac_rset(self, line):
        '''set_dac_rset'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dac_rset(*list(eval(line)))

    @handle_errors
    def do_set_ram_update(self, line):
        '''set_ram_update'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_ram_update(*list(eval(line)))

    @handle_errors
    def do_set_pat_status(self, line):
        '''set_pat_status'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_pat_status(*list(eval(line)))

    @handle_errors
    def do_set_pat_type(self, line):
        '''set_pat_type'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_pat_type(*list(eval(line)))

    @handle_errors
    def do_waveform_config(self, line):
        '''write_register'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.waveform_config(*list(eval(line)))

    @handle_errors
    def do_set_pat_timebase(self, line):
        '''set_pat_timebase'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_pat_timebase(*list(eval(line)))

    @handle_errors
    def do_set_pat_period(self, line):
        '''set_pat_period'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_pat_period(*list(eval(line)))

    @handle_errors
    def do__real_value_to_reg_value(self, line):
        '''_real_value_to_reg_value'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102._real_value_to_reg_value(*list(eval(line)))

    @handle_errors
    def do_set_dac_doffset(self, line):
        '''set_dac_doffset'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dac_doffset(*list(eval(line)))

    @handle_errors
    def do_set_dac_cst(self, line):
        '''set_dac_cst'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dac_cst(*list(eval(line)))

    @handle_errors
    def do_set_dac_dgain(self, line):
        '''set_dac_dgain'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dac_dgain(*list(eval(line)))

    @handle_errors
    def do_sawtooth_config(self, line):
        '''sawtooth_config'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.sawtooth_config(*list(eval(line)))

    @handle_errors
    def do_set_frequency(self, line):
        '''set_frequency'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_frequency(*list(eval(line)))

    @handle_errors
    def do_set_phase(self, line):
        '''set_phase'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_phase(*list(eval(line)))

    @handle_errors
    def do_set_start_delay(self, line):
        '''set_start_delay'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_start_delay(*list(eval(line)))

    @handle_errors
    def do_set_sram_addr(self, line):
        '''set_sram_addr'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_sram_addr(*list(eval(line)))

    @handle_errors
    def do_set_dds_cycles(self, line):
        '''set_dds_cycles'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dds_cycles(*list(eval(line)))

    @handle_errors
    def do_set_dc_output(self, line):
        '''set_dc_output'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.set_dc_output(*list(eval(line)))

    @handle_errors
    def do_sine_output(self, line):
        '''sine_output'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.sine_output(*list(eval(line)))

    @handle_errors
    def do_sawtooth_output(self, line):
        '''sawtooth_output'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.sawtooth_output(*list(eval(line)))

    @handle_errors
    def do_write_pattern(self, line):
        '''write_pattern'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.write_pattern(*list(eval(line)))

    @handle_errors
    def do_play_pattern(self, line):
        '''play_pattern'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.ad9102.play_pattern(*list(eval(line)))

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
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_ad9102_dbg(spi_bus_name, cs_ctrl=None, cs_chip=None, cs_addr=None, cs_i2c=None):
    ad9102_dbg = AD9102Debuger()
    if spi_bus_name == '':
        spi_bus = None
    else:
        axi4_bus = AXI4LiteBus(spi_bus_name, PLSPIDef.REG_SIZE)
        spi_bus = MIXQSPISG(axi4_bus)
        spi_bus.set_mode('MODE3')
        spi_bus.set_speed(800000)

    if cs_ctrl is not None:
        cs_chip = str(cs_chip)
        if '0x' in cs_addr:
            cs_addr = int(cs_addr, 16)
        else:
            cs_addr = int(cs_addr)
        cs_i2c = str(cs_i2c)
        cs_i2c = I2C(cs_i2c)
        exec('from ..ic.{} import {}'.format(cs_chip.lower(), cs_chip.upper()))
        cs_chip = eval(cs_chip.upper())(cs_addr, cs_i2c)
        cs = Pin(cs_chip, int(cs_ctrl))
    else:
        cs = None
    ad9102_dbg.ad9102 = AD9102(spi_bus, cs=cs)
    return ad9102_dbg


arguments = [
    ['-spi', '--spi', 'spi bus name', '/dev/MIX_QSPI_SG'],
    ['-cs', '--cs_ctrl', 'cs pin ctrl', None],
    ['-cs_chip', '--cs_chip', 'chip of cs pin', None],
    ['-cs_addr', '--cs_addr', 'chip of cs pin', None],
    ['-cs_i2c', '--cs_i2c', 'chip i2c name of cs pin', None],
]


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    ad9102_dbg = create_ad9102_dbg(args.spi, args.cs_ctrl, args.cs_chip, args.cs_addr, args.cs_i2c)
    ad9102_dbg.cmdloop()
