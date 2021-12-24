# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.pl_i2c_bus import PLI2CBus
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.sg2251pw01pca.module.sg2251pw01pca import SG2251PW01PCA


__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.1'


class SG2251PW01PCADef:
    pass


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class SG2251PW01PCADebugger(cmd.Cmd):
    prompt = 'sg2251pw01pca>'
    intro = 'Xavier sg2251pw01pca debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.sg2251pw01pca.module_init()
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
        self.sg2251pw01pca.write_calibration_cell(unit_index, gain, offset, threshold)
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell; unit_index'''
        unit_index = int(line)
        ret = self.sg2251pw01pca.read_calibration_cell(unit_index)
        print("gain: %s" % (ret["gain"]))
        print("offset: %s" % (ret["offset"]))
        print("threshold: %s" % (ret["threshold"]))
        print("is_use: %s" % (ret["is_use"]))

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell unit_index'''
        self.sg2251pw01pca.erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode <raw/cal>'''
        self.sg2251pw01pca.set_calibration_mode(line)
        print("Done")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.sg2251pw01pca.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_power_output(self, line):
        '''power_output volt'''
        line = line.replace(' ', ',')
        line += ','
        self.sg2251pw01pca.power_output(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_set_current_limit(self, line):
        '''current_limit current'''
        line = line.replace(' ', ',')
        line += ','
        self.sg2251pw01pca.set_current_limit(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_power_readback_voltage_calc(self, line):
        '''power_readback_voltage volt'''
        line = line.replace(' ', ',')
        line += ','
        self.sg2251pw01pca.power_readback_voltage_calc(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_power_readback_current_calc(self, line):
        '''power_readback_current current'''
        line = line.replace(' ', ',')
        line += ','
        self.sg2251pw01pca.power_readback_current_calc(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_power_control(self, line):
        '''power_control <on/off>'''
        line = line.replace(' ', ',')
        line += ','
        self.sg2251pw01pca.power_control(*list(eval(line)))
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
        print(self.do_power_output.__doc__)
        print(self.do_set_current_limit.__doc__)
        print(self.do_power_readback_voltage_calc.__doc__)
        print(self.do_power_readback_current_calc.__doc__)
        print(self.do_power_control.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_sg2251pw01pca_dbg(ip_name, signal_source_name, io_name, pin, i2c_name):
    sg2251pw01pca_dbg = None
    if utility.is_pl_device(i2c_name):
        axi4_bus = AXI4LiteBus(i2c_name, 256)
        i2c = PLI2CBus(axi4_bus)
    else:
        i2c = I2C(i2c_name)
    sg2251pw01pca_dbg.sg2251pw01pca = SG2251PW01PCA(i2c)

    return sg2251pw01pca_dbg


arguments = [
    ['-i2c', '--i2c_bus', 'i2c bus device name', ''],
]

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    sg2251pw01pca_dbg = create_sg2251pw01pca_dbg(args.i2c_bus)
    sg2251pw01pca_dbg.cmdloop()
