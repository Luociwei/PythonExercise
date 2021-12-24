# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.negasonic.module.negasonic import Negasonic
from mix.driver.core.utility.utility import utility
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_aut1 import MIXAUT1
from mix.driver.core.bus.pin import Pin

__author__ = 'Zhangsong Deng'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class NegasonicDebuger(cmd.Cmd):
    prompt = 'negasonic>'
    intro = 'Mix negasonic debug tool'

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell: unit_index, gain, offset, threshold'''
        line = line.replace(' ', ',')
        params = list(eval(line))
        unit_index = int(params[0])
        gain = float(params[1])
        offset = float(params[2])
        threshold = float(params[3])
        self.audio.write_calibration_cell(unit_index, gain, offset, threshold)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell; unit_index'''
        unit_index = int(line)
        ret = self.audio.read_calibration_cell(unit_index)
        print("gain: %s" % (ret["gain"]))
        print("offset: %s" % (ret["offset"]))
        print("threshold: %s" % (ret["threshold"]))
        print("is_use: %s" % (ret["is_use"]))

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.audio.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode <raw/cal>'''
        self.audio.set_calibration_mode(line)
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.audio.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.audio.module_init()
        print("Done.")

    @handle_errors
    def do_enable_upload(self, line):
        '''enable_upload'''
        self.audio.enable_upload()
        print("Done.")

    @handle_errors
    def do_disable_upload(self, line):
        '''disable_upload'''
        self.audio.disable_upload()
        print("Done.")

    @handle_errors
    def do_measure(self, line):
        '''measure bandwidth harmonic_num decimation'''
        line = line.replace(' ', ',')
        info = self.audio.measure(*list(eval(line)))
        print("Result:")
        print("freq: %f HZ" % info['freq'])
        print("vpp: %f mV" % info['vpp'])
        print("thd: %f DB" % info['thd'])
        print("thdn:%f DB" % info['thdn'])
        print("rms: %f" % info['rms'])

    @handle_errors
    def do_enable_output(self, line):
        '''enable_output frequency rms'''
        line = line.replace(' ', ',')
        self.audio.enable_output(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_disable_output(self, line):
        '''disable_output'''
        self.audio.disable_output()
        print("Done.")

    @handle_errors
    def do_read_temperature(self, line):
        '''read_temperature'''
        result = self.audio.temperature
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_cal(self, line):
        '''erase_cal unit_id'''
        self.audio.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_erase_calibration_cell.__doc__)
        print(self.do_module_init.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_enable_upload.__doc__)
        print(self.do_disable_upload.__doc__)
        print(self.do_measure.__doc__)
        print(self.do_enable_output.__doc__)
        print(self.do_disable_output.__doc__)
        print(self.do_read_temperature.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_negasonic_dbg(fftrt_dev, i2s_rx_en_pin, adc_rst_pin, gpio_dev,
                         signal_source_dev, i2s_tx_en_pin, dac_rst_pin,
                         i2c_dev, mix_aut1_dev):

    negasonic_dbg = NegasonicDebuger()

    if i2c_dev != '':
        if utility.is_pl_device(i2c_dev):
            axi4_bus = AXI4LiteBus(i2c_dev, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_dev)
    else:
        i2c_bus = None

    if mix_aut1_dev != '':
        axi4 = AXI4LiteBus(mix_aut1_dev, 0x8000)
        mix_aut1 = MIXAUT1(axi4)
        negasonic_dbg.audio = Negasonic(i2c_bus, ip=mix_aut1)
    else:
        axi4 = AXI4LiteBus(fftrt_dev, 256)
        analyzer = MIXFftAnalyzerSG(axi4)

        axi4 = AXI4LiteBus(signal_source_dev, 256)
        signal_source = MIXSignalSourceSG(axi4)

        axi4 = AXI4LiteBus(gpio_dev, 256)
        gpio = MIXGPIOSG(axi4)
        analyzer_rst = Pin(gpio, adc_rst_pin)
        analyzer_en = Pin(gpio, i2s_rx_en_pin)
        signal_source_rst = Pin(gpio, dac_rst_pin)
        signal_source_en = Pin(gpio, i2s_tx_en_pin)
        negasonic_dbg.audio = Negasonic(i2c_bus, analyzer=analyzer, signal_sourc=signal_source,
                                        analyzer_rst=analyzer_rst, analyzer_en=analyzer_en,
                                        signal_source_rst=signal_source_rst,
                                        signal_source_en=signal_source_en,
                                        ip=mix_aut1)

    return negasonic_dbg


arguments = [
    ['-fd', '--fftrt_device', 'fft_analyzer device name', ''],
    ['-i2s_rx_en', '--i2s_rx_en_pin', 'i2s rx enable pin', 1],
    ['-adc_rst', '--adc_reset_pin', 'adc reset pin', 0],
    ['-sd', '--signal_source_device', 'signal_source device name', ''],
    ['-i2s_tx_en', '--i2s_tx_en_pin', 'i2s tx enable pin', 9],
    ['-dac_rst', '--dac_reset_pin', 'dac reset pin', 8],
    ['-io', '--gpio', 'gpio device name', ''],
    ['-i2c', '--i2c_device', 'i2c device name', ''],
    ['-ip', '--mix_aut1', 'MIXAUT1 device name', '']
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()

    negasonic_dbg = create_negasonic_dbg(args.fftrt_device, args.i2s_rx_en_pin, args.adc_reset_pin, args.gpio,
                                         args.signal_source_device, args.i2s_tx_en_pin,
                                         args.dac_reset_pin, args.i2c_device, args.mix_aut1)
    negasonic_dbg.cmdloop()
