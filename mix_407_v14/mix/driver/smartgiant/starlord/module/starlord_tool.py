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
from mix.driver.smartgiant.starlord.module.starlord import StarLord
from mix.driver.core.bus.i2c_ds_bus import I2CDownstreamBus
from mix.driver.core.ic.tca9548 import TCA9548
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_aut5_sg_r import MIXAUT5SGR

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


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


class MIX_StarLord_SGDebuger(cmd.Cmd):
    prompt = 'starlord>'
    intro = 'Xavier starlord debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell: unit_index, gain, offset, threshold'''
        line = line.replace(' ', ',')
        params = list(eval(line))
        unit_index = int(params[0])
        gain = float(params[1])
        offset = float(params[2])
        threshold = float(params[3])
        self.starlord.write_calibration_cell(unit_index, gain, offset, threshold)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell; unit_index'''
        unit_index = int(line)
        ret = self.starlord.read_calibration_cell(unit_index)
        print("gain: %s" % (ret["gain"]))
        print("offset: %s" % (ret["offset"]))
        print("threshold: %s" % (ret["threshold"]))
        print("is_use: %s" % (ret["is_use"]))

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.starlord.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode <raw/cal>'''
        self.starlord.set_calibration_mode(eval(line))
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.starlord.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.starlord.module_init()
        print("Done.")

    @handle_errors
    def do_enable_upload(self, line):
        '''enable_upload'''
        self.starlord.enable_upload(eval(line))
        print("Done.")

    @handle_errors
    def do_disable_upload(self, line):
        '''disable_upload'''
        self.starlord.disable_upload(eval(line))
        print("Done.")

    @handle_errors
    def do_measure(self, line):
        '''measure channel bandwidth harmonic_num decimation sampling_rate'''
        line = line.replace(' ', ',')
        info = self.starlord.measure(*list(eval(line)))
        print("Result:")
        print("freq: %f HZ" % info['freq'])
        print("vpp: %f mV" % info['vpp'])
        print("thd: %f DB" % info['thd'])
        print("thdn:%f DB" % info['thdn'])
        print("rms: %f" % info['rms'])
        print("noisefloor: %f mV" % info['noisefloor'])

    @handle_errors
    def do_config_lna_scope(self, line):
        '''config_lna_scope channel scope adc_upload_ch'''
        line = line.replace(' ', ',')
        self.starlord.config_lna_scope(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_enable_lna_upload(self, line):
        '''enable_lna_upload channel sampling_rate'''
        line = line.replace(' ', ',')
        self.starlord.enable_lna_upload(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_disable_lna_upload(self, line):
        '''disable_lna_upload channel'''
        self.starlord.disable_lna_upload(eval(line))
        print("Done.")

    @handle_errors
    def do_measure_lna(self, line):
        '''measure bandwidth harmonic_num decimation sampling_rate'''
        line = line.replace(' ', ',')
        info = self.starlord.measure_lna(*list(eval(line)))
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
        self.starlord.enable_output(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_disable_output(self, line):
        '''disable_output'''
        self.starlord.disable_output()
        print("Done.")

    @handle_errors
    def do_read_temperature(self, line):
        '''read_temperature'''
        result = self.starlord.get_temperature()
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
        print(self.do_module_init.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_enable_upload.__doc__)
        print(self.do_disable_upload.__doc__)
        print(self.do_measure.__doc__)
        print(self.do_config_lna_scope.__doc__)
        print(self.do_enable_lna_upload.__doc__)
        print(self.do_disable_lna_upload.__doc__)
        print(self.do_measure_lna.__doc__)
        print(self.do_enable_output.__doc__)
        print(self.do_disable_output.__doc__)
        print(self.do_read_temperature.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_beast_dbg(ip_name, i2c_bus_name):
    starlord_dbg = MIX_StarLord_SGDebuger()

    if i2c_bus_name == '':
        i2c_bus_name = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = PSI2CBus(i2c_bus_name)
    mux = TCA9548(0x77, i2c_bus)
    i2c_bus_1 = I2CDownstreamBus(mux, 5)
    axi4_bus = AXI4LiteBus(ip_name, 65535)
    mix_aut5_r = MIXAUT5SGR(axi4_bus, fft_data_cnt=1234, ad717x_mvref=2500)
    starlord_dbg.starlord = StarLord(i2c=i2c_bus_1, ipcore=mix_aut5_r)
    return starlord_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-ip', '--mix_aut5_r', help='aut5 devcie name', default='/dev/MIX_AUT5_0')
    parser.add_argument('-i2c', '--i2c', help='eeprom i2c bus name', default='/dev/i2c-2')
    args = parser.parse_args()
    scope_dbg = create_beast_dbg(args.mix_aut5_r, args.i2c)

    scope_dbg.cmdloop()
