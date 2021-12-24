# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.ic.tca9548 import TCA9548
from mix.driver.core.bus.i2c_ds_bus import I2CDownstreamBus
from mix.driver.smartgiant.odin.module.psu001011_map import Odin
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR


__author__ = 'jihua.jiang@SmartGiant'
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


class OdinDebuger(cmd.Cmd):
    prompt = 'odin>'
    intro = 'odin debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.post_power_on_init(eval(line)))

    @handle_errors
    def do_reset(self, line):
        '''reset timeout'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.reset(eval(line)))

    @handle_errors
    def do_enable_battery_output(self, line):
        '''enable_battery_output voltage
        eg.enable_battery_output [1000]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.enable_battery_output(*list(eval(line))))

    @handle_errors
    def do_disable_battery_output(self, line):
        '''disable_battery_output'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.disable_battery_output())

    @handle_errors
    def do_enable_continuous_measure(self, line):
        '''enable_continuous_measure ch_type, measure_type, sampling_rate
           eg.enable_continuous_measure ['battery','voltage',1000]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.enable_continuous_measure(*list(eval(line))))

    @handle_errors
    def do_disable_continuous_measure(self, line):
        '''disable_continuous_measure ch_type
           eg.disable_continuous_measure ['battery'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.disable_continuous_measure(*list(eval(line))))

    @handle_errors
    def do_voltage_sample(self, line):
        '''voltage_sample ch_type, points, mux_delay, raw
           eg.voltage_sample ['battery',10,0,True]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.voltage_sample(*list(eval(line))))

    @handle_errors
    def do_current_sample(self, line):
        '''current_sample ch_type, points, mux_delay, raw
           eg.current_sample ['battery',10,0,True]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.current_sample(*list(eval(line))))

    @handle_errors
    def do_set_current_limit(self, line):
        '''set_current_limit threshold
           eg.set_current_limit [1000]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.set_current_limit(eval(line)))

    @handle_errors
    def do_set_measure_path(self, line):
        '''set_measure_path ch_type, scope
           eg.set_measure_path ['battery','1mA'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.set_measure_path(*list(eval(line))))

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path ch_type
           eg.get_measure_path ['battery'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.get_measure_path(eval(line)))

    @handle_errors
    def do_voltage_measure(self, line):
        '''voltage_measure ch_type, mux_delay
           eg.voltage_measure ['battery',0]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.voltage_measure(*list(eval(line))))

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure ch_type, mux_delay
           eg.current_measure ['battery',0]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.current_measure(*list(eval(line))))

    @handle_errors
    def do_enable_charge_output(self, line):
        '''enable_charge_output voltage
           eg.enable_charge_output [1000]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.enable_charge_output(*list(eval(line))))

    @handle_errors
    def do_disable_charge_output(self, line):
        '''disable_charge_output'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.disable_charge_output())

    @handle_errors
    def do_set_sample_rate(self, line):
        '''set_sample_rate ch_type, sampling_rate
           eg.set_sample_rate ['charge',15]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.set_sample_rate(*list(eval(line))))

    @handle_errors
    def do_get_sample_rate(self, line):
        '''get_sample_rate ch_type
           eg.get_sample_rate ['charge'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.get_sample_rate(*list(eval(line))))

    @handle_errors
    def do_datalogger_start(self, line):
        '''datalogger_start ch_type, measure_type
           eg.datalogger_start ['battery','current'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.datalogger_start(*list(eval(line))))

    @handle_errors
    def do_datalogger_stop(self, line):
        '''datalogger_stop ch_type, measure_type
           eg.datalogger_stop ['charge','current'] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.datalogger_stop(*list(eval(line))))

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode mode
           eg.set_calibration_mode ['raw/cal]' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        print(self.psu.set_calibration_mode(*list(eval(line))))

    @handle_errors
    def do_get_calibration_mode(self, line):
        '''get_calibration_mode'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        print(self.psu.get_calibration_mode())

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_psu_dbg(i2c_ext, i2c_power, ad7175_bus_name, ipcore, i2c_ext_use_tca9548_ch,
                   i2c_power_use_tca9548_ch, tca9548_addr):
    psu_dbg = OdinDebuger()
    daqt1 = None
    ad7175 = None
    if ipcore != '':
        axi4_bus = AXI4LiteBus(ipcore, 9548)
        daqt1 = MIXDAQT1SGR(axi4_bus, ad717x_mvref=2500, use_spi=False, use_gpio=False)
    elif ad7175_bus_name != '':
        axi4_bus = AXI4LiteBus(ad7175_bus_name, 256)
        ad7175 = MIXAd7175SG(axi4_bus, 2500)

    if i2c_ext != '':
        if 'AXI4' in i2c_ext or 'MIX' in i2c_ext:
            axi4_bus = AXI4LiteBus(i2c_ext, 256)
            i2c_bus_ext = MIXI2CSG(axi4_bus)
        else:
            i2c_bus_ext = I2C(i2c_ext)

    if i2c_power != '':
        if 'AXI4' in i2c_power or 'MIX' in i2c_power:
            axi4_bus = AXI4LiteBus(i2c_power, 256)
            i2c_bus_power = MIXI2CSG(axi4_bus)
        else:
            i2c_bus_power = I2C(i2c_power)

    if i2c_ext_use_tca9548_ch != '' or i2c_power_use_tca9548_ch != '':
        tca9548_i2c = TCA9548(int(tca9548_addr), i2c_bus_ext)
        if i2c_ext_use_tca9548_ch != '':
            i2c_bus_ext = I2CDownstreamBus(tca9548_i2c, int(i2c_ext_use_tca9548_ch))
        if i2c_power_use_tca9548_ch != '':
            i2c_bus_power = I2CDownstreamBus(tca9548_i2c, int(i2c_power_use_tca9548_ch))

    psu_dbg.psu = Odin(i2c_bus_ext, i2c_bus_power, ad7175, daqt1)
    psu_dbg.psu.post_power_on_init()
    return psu_dbg


if __name__ == '__main__':
    '''
    python -m odin_tool -ad '/dev/MIX_PSU001_0' -iic_1 '/dev/i2c-2' -iic_2 '/dev/i2c-3' -iic_ext_ch '5'

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
    parser.add_argument('-ip', '--ipcore', help='ipcore devcie name',
                        default='')
    parser.add_argument('-ad', '--ad7175', help='ad7175 devcie name',
                        default='')
    parser.add_argument('-iic_1', '--iic_ext', help='pca9536,cat32,nct75 i2c bus name',
                        default='')
    parser.add_argument('-iic_2', '--iic_power', help='ad5667,ads1112 i2c bus name',
                        default='')
    parser.add_argument('-iic_ext_ch', '--iic_ext_ch', help='i2c_ext use tca9548 extend channel',
                        default='')
    parser.add_argument('-iic_power_ch', '--iic_power_ch', help='i2c_power use tca9548 extend channel',
                        default='')
    parser.add_argument('-tca9548_addr', '--tca9548_addr', help='tca9548 i2c extend addr',
                        default='119')
    args = parser.parse_args()
    psu_dbg = create_psu_dbg(args.iic_ext, args.iic_power, args.ad7175, args.ipcore,
                             args.iic_ext_ch, args.iic_power_ch, args.tca9548_addr)

    psu_dbg.cmdloop()
