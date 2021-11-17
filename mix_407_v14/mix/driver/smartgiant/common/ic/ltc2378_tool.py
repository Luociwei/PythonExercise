# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from ltc2378 import LTC2378
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.pl_spi_adc import PLSPIADC

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class LTC2378Debuger(cmd.Cmd):
    prompt = 'LTC2378>'
    intro = 'Xavier LTC2378 debug tool'

    @handle_errors
    def do_measure_rms_average_amplitude_max_min(self, line):
        '''measure_rms_average_amplitude_max_min sample_rate sample_time
           upload_adc_data(str) sample_interval upload_mode(str)
        '''
        line = line.replace(' ', ',')
        ret = self.ltc2378.measure_rms_average_amplitude_max_min(
            *list(eval(line)))
        print(ret)

    @handle_errors
    def do_measure_voltage(self, line):
        '''measure_voltage channel'''
        line = line.replace(' ', ',')
        ret = self.ltc2378.read_volt(eval(line))
        print(ret)

    @handle_errors
    def do_measure_thdn(self, line):
        '''measure_thdn bandwidth_hz sample_rate decimation_type(str)
        signal_source(str) upload(str) harmonic_count *measure_type
        '''
        line = line.replace(' ', ',')
        ret = self.ltc2378.measure_thdn(*list(eval(line)))
        print(ret)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_measure_rms_average_amplitude_max_min.__doc__)
        print(self.do_measure_voltage.__doc__)
        print(self.do_measure_thdn.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ltc2378_dbg(meter_dev, bus_dev, audio_dev, adc_volt_range):
    ltc2378_dbg = LTC2378Debuger()
    if meter_dev == '':
        meter_bus = None
    else:
        if utility.is_pl_device(meter_dev):
            axi4_bus = AXI4LiteBus(meter_dev, 1024)
            meter_bus = MIXSignalMeterSG(axi4_bus)
        else:
            meter_bus = MIXSignalMeterSG(meter_dev)
    if bus_dev == '':
        spi_adc_bus = None
    else:
        if utility.is_pl_device(bus_dev):
            adc_bus = AXI4LiteBus(bus_dev, 256)
            spi_adc_bus = PLSPIADC(adc_bus)
        else:
            spi_adc_bus = PLSPIADC(adc_bus)
    if audio_dev == '':
        audio_bus = None
    else:
        if utility.is_pl_device(audio_dev):
            axi4_bus = AXI4LiteBus(audio_dev, 65536)
            audio_bus = MIXFftAnalyzerSG(axi4_bus)
        else:
            audio_bus = MIXFftAnalyzerSG(axi4_bus)
    ltc2378_dbg.ltc2378 = LTC2378(
        meter_bus, spi_adc_bus, audio_bus, adc_volt_range)
    return ltc2378_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--meter_dev', help='meter device', default='')
    parser.add_argument('-b', '--bus_dev', help='bus device', default='')
    parser.add_argument('-s', '--audio_dev', help='audio device', default='')
    parser.add_argument('-r', '--adc_volt_range',
                        help='adc voltage range', default=[-4096, 4096])
    args = parser.parse_args()
    ltc2378_dbg = create_ltc2378_dbg(
        args.meter_dev, args.bus_dev, args.audio_dev, args.adc_volt_range)

    ltc2378_dbg.cmdloop()
