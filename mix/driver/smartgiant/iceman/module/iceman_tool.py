# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.iceman.module.iceman import Iceman
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_sgt1_sg_r import MIXSGT1SGR
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class IcemanDef:
    pass


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class IcemanDebugger(cmd.Cmd):
    prompt = 'iceman>'
    intro = 'Xavier iceman debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.iceman.module_init()
        print("Done")

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell: unit_index, gain, offset, threshold'''
        line = line.replace(' ', ',')
        params = list(eval(line))
        unit_index = int(params[0])
        gain = float(params[1])
        offset = float(params[2])
        threshold = float(params[3])
        self.iceman.write_calibration_cell(unit_index, gain, offset, threshold)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell; unit_index'''
        unit_index = int(line)
        ret = self.iceman.read_calibration_cell(unit_index)
        print("gain: %s" % (ret["gain"]))
        print("offset: %s" % (ret["offset"]))
        print("threshold: %s" % (ret["threshold"]))
        print("is_use: %s" % (ret["is_use"]))

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.iceman.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode <raw/cal>'''
        self.iceman.set_calibration_mode(line)
        print("Done")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.iceman.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_range(self, line):
        '''get_range'''
        result = self.iceman.get_range()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''Iceman board set dac sampling rate'''
        self.iceman.set_sampling_rate(eval(line))
        print("Done")

    @handle_errors
    def do_output_volt(self, line):
        '''output_volt volt [range]'''
        line = line.replace(' ', ',')
        line += ','
        self.iceman.output_volt(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_sine(self, line):
        '''sine freq rms offset [range]'''
        line = line.replace(' ', ',')
        self.iceman.output_sine(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_square(self, line):
        '''square freq vpp duty offset [range]'''
        line = line.replace(' ', ',')
        self.iceman.output_square(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_triangle(self, line):
        '''triangle freq vpp delay_ms offset [range]'''
        line = line.replace(' ', ',')
        self.iceman.output_triangle(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_sawtooth(self, line):
        '''sawtooth freq vpp trise delay_ms offset [range]'''
        line = line.replace(' ', ',')
        self.iceman.output_sawtooth(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_stop(self, line):
        '''stop'''
        self.iceman.output_stop()
        print("Done")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_write_calibration_cell.__doc__)
        print(self.do_read_calibration_cell.__doc__)
        print(self.do_erase_calibration_cell.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_module_init.__doc__)
        print(self.do_get_range.__doc__)
        print(self.do_output_volt.__doc__)
        print(self.do_sine.__doc__)
        print(self.do_square.__doc__)
        print(self.do_triangle.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_iceman_dbg(ip_name, signal_source_name, io_name, pin, i2c_name):
    iceman_dbg = None
    if utility.is_pl_device(i2c_name):
        axi4_bus = AXI4LiteBus(i2c_name, 256)
        i2c = MIXI2CSG(axi4_bus)
    else:
        i2c = I2C(i2c_name)

    if ip_name == '':
        axi4_bus = AXI4LiteBus(signal_source_name, 256)
        signal_source = MIXSignalSourceSG(axi4_bus)
        axi4_bus = AXI4LiteBus(io_name, 256)
        pl_gpio = MIXGPIOSG(axi4_bus)
        iceman_dbg = IcemanDebugger()
        iceman_dbg.iceman = Iceman(i2c, signal_source, Pin(pl_gpio, pin))
    else:
        axi4_bus = AXI4LiteBus(ip_name, 0x8000)
        mix_sgt1 = MIXSGT1SGR(axi4_bus)
        iceman_dbg = IcemanDebugger()
        iceman_dbg.iceman = Iceman(i2c, ipcore=mix_sgt1)
    return iceman_dbg


arguments = [
    ['-ipcore', '--ipcore', 'ipcore device name', ''],
    ['-ss', '--signal_source', 'signal source device name', ''],
    ['-io', '--io', 'pl gpio used to control range', ''],
    ['-pin', '--pin', 'gpio index', 0],
    ['-i2c', '--i2c_bus', 'i2c bus device name', ''],
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    iceman_dbg = create_iceman_dbg(args.ipcore, args.signal_source, args.io, args.pin, args.i2c_bus)
    iceman_dbg.cmdloop()
