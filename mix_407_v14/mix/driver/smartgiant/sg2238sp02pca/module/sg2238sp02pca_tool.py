# -*- coding: UTF-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.sg2238sp02pca.module.sg2238sp02pca import SG2238SP02PCA
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus


__author__ = 'Hanyong.Huang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class Sg2238sp02pcaDebuger(cmd.Cmd):
    prompt = 'sg2238sp02pca>'
    intro = 'Xavier sg2238sp02pca debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''voltage offset'''

        self.sg223802.module_init()
        print("Done.")

    @handle_errors
    def do_set_offset(self, line):
        '''voltage offset'''
        # self.sg223802.set_offset(*list(eval(line)))
        line = line.replace(' ', ',').split(',')
        self.sg223802.set_offset(line[0], int(line[1]))
        print("Done.")

    @handle_errors
    def do_fan_on(self, line):
        '''open fan'''
        self.sg223802.fan_on()
        print("Done.")

    @handle_errors
    def do_fan_off(self, line):
        '''close fan'''
        self.sg223802.fan_off()
        print("Done.")

    @handle_errors
    def do_select_voltage_gain(self, line):
        '''Voltage amplification factor'''
        self.sg223802.select_voltage_gain(line)
        print("Done.")

    @handle_errors
    def do_current_output(self, line):
        '''select output current'''
        self.sg223802.current_output(line)
        print("Done.")

    @handle_errors
    def do_select_signal_type(self, line):
        '''select signal type'''
        self.sg223802.select_signal_type(line)
        print("Done.")

    @handle_errors
    def do_select_impedance(self, line):
        '''select impedance'''
        self.sg223802.select_impedance(line)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read calibration from eeprom'''
        line = line.replace(' ', ',').split(',')
        print self.sg223802.legacy_read_calibration_cell(int(line[0]))
        # print("Done.")

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write calibration to eeprom'''
        line = line.replace(' ', ',')
        self.sg223802.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_temperature(self, line):
        '''get board temperature'''
        print self.sg223802.get_temperature()

    @handle_errors
    def do_calibration_pipe(self, line):
        '''get calibration result'''
        line = line.replace(' ', ',').split(',')
        range = line[0]
        raw_data = float(line[1])
        print self.sg223802.calibration_pipe(range, raw_data)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_fan_on.__name__, self.do_fan_on.__doc__)
        print(self.do_fan_off.__name__, self.do_fan_off.__doc__)
        print(self.do_module_init.__name__, self.do_module_init.__doc__)
        print(self.do_select_signal_type.__name__, self.do_select_signal_type.__doc__)
        print(self.do_select_impedance.__name__, self.do_select_impedance.__doc__)
        print(self.do_set_offset.__name__, self.do_set_offset.__doc__)
        print(self.do_current_output.__name__, self.do_current_output.__doc__)
        print(self.do_read_calibration_cell.__name__, self.do_read_calibration_cell.__doc__)
        print(self.do_write_calibration_cell.__name__, self.do_write_calibration_cell.__doc__)
        print(self.do_calibration_pipe.__name__, self.do_calibration_pipe.__doc__)


def create_sg2238_dbg(i2c1):
    sg2238_dbg = Sg2238sp02pcaDebuger()
    if i2c1 == '':
        i2c1 = None
    else:
        if utility.is_pl_device(i2c1):
            axi4_bus = AXI4LiteBus(i2c1, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c1)
    sg2238_dbg.sg223802 = SG2238SP02PCA(i2c_bus)

    return sg2238_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    i2c_dev = '/dev/i2c-0'
    parser.add_argument('-i2c1', '--i2c1', help='i2c bus name', default=i2c_dev)
    args = parser.parse_args()
    sg2238_dbg = create_sg2238_dbg(args.i2c1)
    sg2238_dbg.cmdloop()
