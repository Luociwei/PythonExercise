# -*- coding: utf-8 -*-
import argparse
import os
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.utility.utility import utility
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.module.mix_board_tool import MIXBoardDebuger
from mix.driver.smartgiant.wolverine.module.wolverine import Wolverine

__author__ = 'jihuajiang@SmartGiant'
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


class WolverineDebugger(MIXBoardDebuger):
    prompt = 'wolverine>'
    intro = 'Xavier wolverine debug tool'

    def __init__(self, wolverine):
        self.wolverine = wolverine
        MIXBoardDebuger.__init__(self)
        self._mix = super(Wolverine, self.wolverine)

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.module_init()
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate
        Wolverine get sampling rate of adc
        channel:  string('VOLT'/'CURR')
        eg: get_sampling_rate 'CURR' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_sampling_rate(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_measure_path(self, line):
        '''get_measure_path
        Wolverine get measure path'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_measure_path()
        print("Result:")
        print(result)

    @handle_errors
    def do_voltage_measure(self, line):
        '''voltage_measure
        Wolverine measure voltage once
        sampling_rate:  int(5-250000)
        eg: voltage_measure 5 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.voltage_measure(eval(line))

        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_voltage_measure(self, line):
        '''multi_points_voltage_measure
        Wolverine measure voltage in continuous mode
        count:          int(1-512)
        sampling_rate:  int(5-250000)
        multi_points_voltage_measure 20,5 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.wolverine.multi_points_voltage_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_current_measure(self, line):
        '''current_measure
        Wolverine measure current once
        curr_range:     string('2mA','100uA')
        sampling_rate:  int(5-250000)
        eg: current_measure '2mA',5 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.wolverine.current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_multi_points_current_measure(self, line):
        '''multi_points_current_measure
        Wolverine measure current in continuous mode
        count:          int(1-512)
        curr_range:     string('2mA','100uA')
        sampling_rate:  int(5-250000)
        eg: multi_points_current_measure 20,'2mA',5 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.wolverine.multi_points_current_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.ad7175.read_register(eval(line))
        print("Result:")
        print(hex(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr data'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.wolverine.ad7175.write_register(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature
        Wolverine read temperature from sensor
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.get_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold
        MIXBoard calibration data write
        unit_index:   int,    calibration unit index
        gain:         float,  calibration gain
        offset:       float,  calibration offset
        threshold:    float,  if value < threshold,
                            use this calibration unit data
        eg: write_calibration_cell 0,1.1,0.1,100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.wolverine.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        unit_index: int, calibration unit index
        eg: read_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.legacy_read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell
        MIXBoard erase calibration unit
        unit_index: int, calibration unit index
        eg: erase_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.legacy_erase_calibration_cell(eval(line))
        print("Done.")

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        MIXBoard enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.wolverine.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        MIXBoard query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.wolverine.is_use_cal_data()
        print('Result:')
        print(result)

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode raw|cal'''
        self.wolverine.set_calibration_mode(line)
        print("Done.")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.wolverine.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')

        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_wolverine_dbg(ad7175_bus_name, vref, i2c_bus0_name, i2c_bus1_name, i2c_dev_addr1,
                         range_sel_bit, meter_sel_bit, ip_dev_name):

    if ad7175_bus_name == '':
        ad7175 = None
    else:
        axi4_bus = AXI4LiteBus(ad7175_bus_name, 8192)
        ad7175 = MIXAd7175SG(axi4_bus, vref)
    if i2c_bus0_name == '':
        i2c_bus0 = None
    else:
        if utility.is_pl_device(i2c_bus0_name):
            axi4_bus = AXI4LiteBus(i2c_bus0_name, 256)
            i2c_bus0 = MIXI2CSG(axi4_bus)
        else:
            i2c_bus0 = I2C(i2c_bus0_name)

    if i2c_bus1_name == '':
        cat9555 = None
    else:
        if utility.is_pl_device(i2c_bus1_name):
            axi4_bus = AXI4LiteBus(i2c_bus1_name, 256)
            i2c_bus1 = MIXI2CSG(axi4_bus)
        else:
            i2c_bus1 = I2C(i2c_bus1_name)
        cat9555 = CAT9555(i2c_dev_addr1, i2c_bus1)

    if ip_dev_name == '':
        ipcore = None
    else:
        axi4_bus = AXI4LiteBus(ip_dev_name, 0x8000)
        ipcore = MIXDAQT1SGR(axi4_bus, ad717x_chip='AD7175', use_spi=False, use_gpio=True)

    if range_sel_bit == '':
        range_sel_bit = None
    else:
        range_sel_bit = int(range_sel_bit)

    if meter_sel_bit == '':
        meter_sel_bit = None
    else:
        meter_sel_bit = int(meter_sel_bit)

    wolverine_dbg = WolverineDebugger(Wolverine(i2c_bus0, ad7175,
                                                Pin(cat9555, range_sel_bit), Pin(cat9555, meter_sel_bit), ipcore))
    return wolverine_dbg


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
    parser.add_argument('-ad', '--ad7175', help='ad7175 devcie name',
                        default='')
    parser.add_argument('-v', '--vref', help='ad7175 reference',
                        default='5000')
    parser.add_argument('-i2c0', '--i2c0',
                        help='i2c device name, which is used to control eeprom and nct75', default='')
    parser.add_argument('-i2c1', '--i2c1', help='cat9555 i2c bus name',
                        default='')
    parser.add_argument('-a1', '--addr1', help='cat9555 device address',
                        default='0x20')
    parser.add_argument('-ip', '--ipcore', help='MIX DAQT1 ipcore device name', default='')
    parser.add_argument('-rb', '--range_bit', help='range select bit', default='')
    parser.add_argument('-mb', '--meter_bit', help='meter select bit', default='')
    args = parser.parse_args()
    wolverine_dbg = create_wolverine_dbg(args.ad7175, args.vref, args.i2c0, args.i2c1,
                                         int(args.addr1, 16), args.range_bit, args.meter_bit, args.ipcore)

    wolverine_dbg.cmdloop()
