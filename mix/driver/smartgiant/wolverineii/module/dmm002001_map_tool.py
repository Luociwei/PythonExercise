# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.wolverineii.module.dmm002001_map import WolverineII
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.commom.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.utility import utility

__author__ = 'zicheng.huang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())

    return wrapper_func


class WolverineiiDebuger(cmd.Cmd):
    prompt = 'wolverineii>'
    intro = 'Xavier wolverineii debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout_s'''
        self.wolverineii.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout_s'''
        self.wolverineii.pre_power_down(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s'''
        self.wolverineii.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_set_sinc(self, line):
        '''set_sinc channel sinc'''
        line = line.replace(' ', ',')
        self.wolverineii.set_sinc(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate channel'''
        result = self.wolverineii.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path sel_range'''
        self.wolverineii.set_measure_path(eval(line))
        print("Done.")

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path'''
        line = line.replace(' ', ',')
        result = self.wolverineii.get_measure_path()
        print(result)

    @handle_errors
    def do_read_measure_value(self, line):
        '''read_measure_value sample_rate count'''
        line = line.replace(' ', ',')
        result = self.wolverineii.read_measure_value(*list(eval(line)))

        print("Result:")
        print(result)

    @handle_errors
    def do_read_measure_list(self, line):
        '''read_measure_list sample_rate count'''
        line = line.replace(' ', ',')
        result = self.wolverineii.read_measure_list(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_continuous_sampling(self, line):
        '''enable_continuous_sampling channel sample_rate down_sample selection'''
        line = line.replace(' ', ',')
        self.wolverineii.enable_continuous_sampling(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_disable_continuous_sampling(self, line):
        '''disable_continuous_sampling'''
        self.wolverineii.disable_continuous_sampling()
        print("Done.")

    @handle_errors
    def do_read_continuous_sampling_statistics(self, line):
        '''read_continuous_sampling_statistics count'''
        result = self.wolverineii.read_continuous_sampling_statistics(
            eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_datalogger_start(self, line):
        '''datalogger_start tag'''
        self.wolverineii.datalogger_start(eval(line))
        print("Done.")

    @handle_errors
    def do_datalogger_end(self, line):
        '''datalogger_end'''
        self.wolverineii.datalogger_end()
        print("Done.")

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr'''
        result = self.wolverineii.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr data'''
        self.wolverineii.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature'''
        result = self.wolverineii.get_temperature()
        print("%f" % result)

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode raw|cal'''
        self.wolverineii.set_calibration_mode(line)
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.wolverineii.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_pre_power_down.__doc__)
        print(self.do_post_power_on_init.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_set_sinc.__doc__)
        print(self.do_get_sampling_rate.__doc__)
        print(self.do_set_measure_path.__doc__)
        print(self.do_get_measure_path.__doc__)
        print(self.do_read_measure_value.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_read_measure_list.__doc__)
        print(self.do_enable_continuous_sampling.__doc__)
        print(self.do_disable_continuous_sampling.__doc__)
        print(self.do_read_continuous_sampling_statistics.__doc__)
        print(self.do_datalogger_start.__doc__)
        print(self.do_datalogger_end.__doc__)
        print(self.do_temperature.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_wolverineii_dbg(ipcore_name, i2c_bus_name):
    wolverineii_dbg = WolverineiiDebuger()
    daqt1 = None
    if ipcore_name != '':
        axi4_bus = AXI4LiteBus(ipcore_name, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, 'AD7175', use_spi=True, use_gpio=False)

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    wolverineii_dbg.wolverineii = WolverineII(i2c_bus, daqt1)
    wolverineii_dbg.wolverineii.post_power_on_init(1)
    return wolverineii_dbg


if __name__ == '__main__':
    '''
    ***measure single voltage/current step:
        1.set_measure_path
        2.measure single voltage/current
    ***measure continue voltage/current step:
        1.set_measure_path
        2.enable_continuous_measure
        3.measure continue voltage/current
    ***when from continue mode to single mode,you have to stop_continuous_measure first.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip',
                        '--ipcore',
                        help='ipcore devcie name',
                        default='')
    parser.add_argument('-i2c',
                        '--i2c',
                        help='cat9555 i2c bus name',
                        default='')

    args = parser.parse_args()
    wolverineii_dbg = create_wolverineii_dbg(args.ipcore, args.i2c)

    wolverineii_dbg.cmdloop()
