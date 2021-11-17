# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.utility.utility import utility
from mix.driver.core.bus.i2c import I2C as PSI2CBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.starlordii.module.audio005002_map import Audio005002
from mix.driver.core.bus.i2c_ds_bus import I2CDownstreamBus
from mix.driver.core.ic.tca9548 import TCA9548
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_audio005_sg_r import MIXAudio005SGR

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.0.1'


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


class MIX_Audio005002_Debuger(cmd.Cmd):
    prompt = 'audio005002>'
    intro = 'Xavier audio005002 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell: unit_index, gain, offset, threshold'''
        line = line.replace(' ', ',')
        params = list(eval(line))
        unit_index = int(params[0])
        gain = float(params[1])
        offset = float(params[2])
        threshold = float(params[3])
        self.audio005002.write_calibration_cell(unit_index, gain, offset, threshold)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell; unit_index'''
        unit_index = int(line)
        ret = self.audio005002.read_calibration_cell(unit_index)
        print("gain: %s" % (ret["gain"]))
        print("offset: %s" % (ret["offset"]))
        print("threshold: %s" % (ret["threshold"]))
        print("is_use: %s" % (ret["is_use"]))

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.audio005002.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode <raw/cal>'''
        self.audio005002.set_calibration_mode(eval(line))
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.audio005002.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout'''
        self.audio005002.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout'''
        self.audio005002.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout'''
        self.audio005002.pre_power_down(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version'''
        result = self.audio005002.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_upload(self, line):
        '''enable_upload'''
        self.audio005002.enable_upload()
        print("Done.")

    @handle_errors
    def do_disable_upload(self, line):
        '''disable_upload'''
        self.audio005002.disable_upload()
        print("Done.")

    @handle_errors
    def do_measure(self, line):
        '''measure channel scope bandwidth_hz harmonic_count decimation_type sampling_rate'''
        line = line.replace(' ', ',')
        info = self.audio005002.measure(*list(eval(line)))
        print("Result:")
        print("freq: %f HZ" % info['freq'])
        print("vpp: %f mV" % info['vpp'])
        print("thd: %f DB" % info['thd'])
        print("thdn:%f DB" % info['thdn'])
        print("rms: %f" % info['rms'])
        print("noisefloor: %f mV" % info['noisefloor'])

    @handle_errors
    def do_enable_output(self, line):
        '''enable_output frequency vpp'''
        line = line.replace(' ', ',')
        self.audio005002.enable_output(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_disable_output(self, line):
        '''disable_output'''
        self.audio005002.disable_output()
        print("Done.")

    @handle_errors
    def do_configure_input_channel(self, line):
        '''configure_input_channel channel enable enable_lna sample_rate'''
        line = line.replace(' ', ',')
        result = self.audio005002.configure_input_channel(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_input_channel_configuration(self, line):
        '''get_input_channel_configuration channel'''
        line = line.replace(' ', ',')
        result = self.audio005002.get_input_channel_configuration(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_configure_output_channel(self, line):
        '''configure_output_channel channel enable sample_rate'''
        line = line.replace(' ', ',')
        result = self.audio005002.configure_output_channel(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_output_channel_configuration(self, line):
        '''get_output_channel_configuration channel'''
        line = line.replace(' ', ',')
        result = self.audio005002.get_output_channel_configuration(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_read(self, line):
        '''read channels samples_per_channel timeout'''
        line = line.replace(' ', ',')
        result = self.audio005002.read(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_write(self, line):
        '''write channel data repeat'''
        line = line.replace(' ', ',')
        self.audio005002.write(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_temperature(self, line):
        '''read_temperature'''
        result = self.audio005002.get_temperature()
        print("Result:")
        print(result)

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
        print(self.do_configure_input_channel.__doc__)
        print(self.do_get_input_channel_configuration.__doc__)
        print(self.do_configure_output_channel.__doc__)
        print(self.do_get_output_channel_configuration.__doc__)
        print(self.do_read.__doc__)
        print(self.do_write.__doc__)
        print(self.do_read_temperature.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_beast_dbg(ip_name, i2c_bus_name):
    audio005002_dbg = MIX_Audio005002_Debuger()

    if utility.is_pl_device(i2c_bus_name):
        axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
        i2c_bus = MIXI2CSG(axi4_bus)
    else:
        i2c_bus = PSI2CBus(i2c_bus_name)

    mux = TCA9548(0x77, i2c_bus)
    i2c_bus_1 = I2CDownstreamBus(mux, 5)
    axi4_bus = AXI4LiteBus(ip_name, 65535)
    mix_aut5_r = MIXAudio005SGR(axi4_bus, fft_data_cnt=1234)
    audio005002_dbg.audio005002 = Audio005002(i2c=i2c_bus_1, ipcore=mix_aut5_r)
    return audio005002_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-ip', '--mix_audio005_r', help='audio005 devcie name', default='/dev/AXI4_Audio005_SG_R')
    parser.add_argument('-i2c', '--i2c', help='eeprom i2c bus name', default='/dev/AXI4_I2C')
    args = parser.parse_args()
    scope_dbg = create_beast_dbg(args.mix_audio005_r, args.i2c)

    scope_dbg.cmdloop()
