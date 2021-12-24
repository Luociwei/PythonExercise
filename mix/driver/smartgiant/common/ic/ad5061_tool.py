# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.ad506x import AD5061
from mix.driver.core.ic.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD5061Debuger(cmd.Cmd):
    prompt = 'ad5061>'
    intro = 'Xavier ad5061 debug tool'

    @handle_errors
    def do_sine(self, line):
        '''sine [vpp] [offset] [frequency] [output_time]'''
        line = line.replace(' ', ',')
        self.ad5061.sine(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc [channel] [volt]'''
        line = line.replace(' ', ',')
        self.ad5061.output_volt_dc(*eval(line))
        print('Done.')

    @handle_errors
    def do_triangle(self, line):
        '''triangle [v1] [v2] [triangle_width] [period] [output_time]'''
        line = line.replace(' ', ',')
        self.ad5061.triangle(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_pulse(self, line):
        '''pulse [v1] [v2] [edge_width] [pulse_width] [period] [output_time]'''
        line = line.replace(' ', ',')
        self.ad5061.pulse(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_disable_output(self, line):
        '''disable_output'''
        self.ad5061.disable_output()
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print(self.do_sine.__doc__)
        print(self.do_output_volt_dc.__doc__)
        print(self.do_triangle.__doc__)
        print(self.do_pulse.__doc__)
        print(self.do_disable_output.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad5061_dbg(dac_volt_min, dac_volt_max, sample_rate,
                      sck_speed, signal_source_dev, spi_dac_dev):
    ad5061_dbg = AD5061Debuger()

    if signal_source_dev == '':
        waveform_bus = None
    else:
        if utility.is_pl_device(signal_source_dev):
            axi4_bus = AXI4LiteBus(
                signal_source_dev, 256)
            waveform_bus = MIXSignalSourceSG(axi4_bus)
        else:
            raise NotImplementedError('signal_source_dev not support')

    if spi_dac_dev == '':
        spi_dac_bus = None
    else:
        if utility.is_pl_device(spi_dac_dev):
            axi4_bus = AXI4LiteBus(spi_dac_dev, 256)
            spi_dac_bus = PLSPIDAC(axi4_bus)
        else:
            raise NotImplementedError('spi_dac_dev not support')

    ad5061_dbg.ad5061 = AD5061(
        dac_volt_min, dac_volt_max, sample_rate, sck_speed,
        waveform_bus, spi_dac_bus)
    return ad5061_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--dac_volt_min',
                        help='dac_volt_min', default='0')
    parser.add_argument('-x', '--dac_volt_max',
                        help='dac_volt_max', default='2048')
    parser.add_argument('-r', '--sample_rate',
                        help='sample_rate', default='200000')
    parser.add_argument('-c', '--sck_speed',
                        help='sck_speed', default='10000000')
    parser.add_argument('-s', '--signal_source_dev',
                        help='signal_source_dev file name', default='')
    parser.add_argument('-d', '--spi_dac_dev',
                        help='spi_dac_dev file name', default='')

    args = parser.parse_args()
    ad506x_dbg = create_ad5061_dbg(int(args.dac_volt_min),
                                   int(args.dac_volt_max),
                                   int(args.sample_rate), int(args.sck_speed),
                                   args.signal_source_dev,
                                   args.spi_dac_dev)

    ad506x_dbg.cmdloop()
