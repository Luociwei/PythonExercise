# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_aut1_sg_r import MIXAUT1SGR
from mix.driver.smartgiant.dazzler.module.audio001004_map import Audio001004

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class DazzlerDebuger(cmd.Cmd):
    prompt = 'audio001004>'
    intro = 'Mix audio001004 debug tool'

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
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout'''
        self.audio.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout'''
        self.audio.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout'''
        self.audio.pre_power_down(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version'''
        result = self.audio.get_driver_version()
        print("Result:")
        print(result)

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
        result = self.audio.get_temperature()
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
        print(self.do_post_power_on_init.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_pre_power_down.__doc__)
        print(self.do_get_driver_version.__doc__)
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


def create_dazzler_dbg(i2s_rx_en_pin, adc_rst_pin, gpio_dev,
                       i2s_tx_en_pin, dac_rst_pin,
                       i2c_dev, mix_aut1_dev):

    dazzler_dbg = DazzlerDebuger()

    if utility.is_pl_device(i2c_dev):
        axi4_bus = AXI4LiteBus(i2c_dev, 256)
        i2c_bus = MIXI2CSG(axi4_bus)
    else:
        i2c_bus = I2C(i2c_dev)

    axi4 = AXI4LiteBus(mix_aut1_dev, 0x8000)
    mix_aut1 = MIXAUT1SGR(axi4)

    if gpio_dev != "":
        axi4 = AXI4LiteBus(gpio_dev, 256)
        gpio = MIXGPIOSG(axi4)
        analyzer_rst = Pin(gpio, adc_rst_pin)
        analyzer_en = Pin(gpio, i2s_rx_en_pin)
        signal_source_rst = Pin(gpio, dac_rst_pin)
        signal_source_en = Pin(gpio, i2s_tx_en_pin)
        dazzler_dbg.audio = Audio001004(i2c=i2c_bus, adc_rst_pin=analyzer_rst,
                                        i2s_rx_en_pin=analyzer_en,
                                        dac_rst_pin=signal_source_rst,
                                        i2s_tx_en_pin=signal_source_en,
                                        ipcore=mix_aut1)
    else:
        dazzler_dbg.audio = Audio001004(i2c=i2c_bus, ipcore=mix_aut1)

    return dazzler_dbg


arguments = [
    ['-i2s_rx_en', '--i2s_rx_en_pin', 'i2s rx enable pin', 1],
    ['-adc_rst', '--adc_reset_pin', 'adc reset pin', 0],
    ['-i2s_tx_en', '--i2s_tx_en_pin', 'i2s tx enable pin', 9],
    ['-dac_rst', '--dac_reset_pin', 'dac reset pin', 8],
    ['-io', '--gpio', 'gpio device name', ''],
    ['-i2c', '--i2c_device', 'i2c device name', ''],
    ['-ip', '--mix_aut1', 'MIXAUT1SGR device name', '']
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()

    dazzler_dbg = create_dazzler_dbg(args.i2s_rx_en_pin, args.adc_reset_pin, args.gpio,
                                     args.i2s_tx_en_pin, args.dac_reset_pin,
                                     args.i2c_device, args.mix_aut1)
    dazzler_dbg.cmdloop()
