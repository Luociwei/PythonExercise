# -*- coding: UTF-8 -*-
import argparse
import cmd
import os
import sys
import traceback
from functools import wraps
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_powersequence_sg import MIXPowerSequenceSG
from mix.driver.smartgiant.se2300ps01pcb.module.se2300ps01pcb import SE2300PS01PCB
sys.path.append("..")

__author__ = 'ZiCheng.Huang@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class Se2300ps01pcbDebuger(cmd.Cmd):
    prompt = 'se2300ps01pcb>'
    intro = 'Xavier se2300ps01pcb debug tool'

    @handle_errors
    def do_start_monitor(self, line):
        '''start_monitor sample_rate attach_byte channel_list'''
        line = line.replace(' ', ',')
        self.se2300.start_monitor(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_stop_monitor(self, line):
        '''stop_monitor'''
        self.se2300.stop_monitor()
        print("Done.")

    @handle_errors
    def do_set_trigger_ref_voltage(self, line):
        '''set_trigger_ref_voltage channel voltage dac_num'''
        line = line.replace(' ', ',')
        self.se2300.set_trigger_ref_voltage(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_trigger_time_monitor_start(self, line):
        '''trigger_time_monitor_start measure_time'''
        result = self.se2300.trigger_time_monitor_start(eval(line))
        print(result)

    @handle_errors
    def do_read_trigger_time(self, line):
        '''read_trigger_time channel_list mode'''
        line = line.replace(' ', ',')
        result = self.se2300.read_trigger_time(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_board_init(self, line):
        '''board_init dac_num'''
        self.se2300.board_init(eval(line))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_start_monitor.__doc__)
        print(self.do_stop_monitor.__doc__)
        print(self.do_set_trigger_ref_voltage.__doc__)
        print(self.do_trigger_time_monitor_start.__doc__)
        print(self.do_read_trigger_time.__doc__)
        print(self.do_board_init.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_se2300_dbg(gpio_device, i2c_bus_1, i2c_bus_2, ps_ipcore, trigger_ipcore):
    se2300_dbg = Se2300ps01pcbDebuger()

    if gpio_device == '':
        gpio = None
    else:
        axi4_bus = AXI4LiteBus(gpio_device, 256)
        gpio = MIXGPIOSG(axi4_bus)
    ads5231_oea = Pin(gpio, 1)
    data_upload = Pin(gpio, 4)
    if i2c_bus_1 == '':
        iic_1 = None
    else:
        axi4_bus = AXI4LiteBus(i2c_bus_1, 256)
        iic_1 = MIXI2CSG(axi4_bus)

    if i2c_bus_2 == '':
        iic_2 = None
    else:
        axi4_bus = AXI4LiteBus(i2c_bus_2, 256)
        iic_2 = MIXI2CSG(axi4_bus)

    if ps_ipcore == '':
        power_sequency = None
    else:
        axi4_bus = AXI4LiteBus(ps_ipcore, 1024)
        power_sequency = MIXPowerSequenceSG(axi4_bus)

    if trigger_ipcore == '':
        trigger_core = None
    else:
        axi4_bus = AXI4LiteBus(trigger_ipcore, 1024)
        trigger_core = MIXPowerSequenceSG(axi4_bus)

    se2300_dbg.se2300 = SE2300PS01PCB(ads5231_oea, data_upload, iic_1, iic_2, power_sequency, trigger_core)
    return se2300_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-io', '--gpio', help='gpio device name',
                        default='/dev/MIX_GPIO_0')
    parser.add_argument('-i2c1', '--i2c1', help='DAC i2c bus name',
                        default='/dev/MIX_I2C_0')
    parser.add_argument('-i2c2', '--i2c2', help='DAC i2c bus name',
                        default='/dev/MIX_I2C_0')
    parser.add_argument('-ps', '--power_sequency', help='power sequency ipcore',
                        default='/dev/MIX_PowerSequence_0')
    parser.add_argument('-tri', '--trigger_ipcore', help='the trigger ipcore name', default='/dev/MIX_PowerSequence_1')

    args = parser.parse_args()
    se2300_dbg = create_se2300_dbg(args.gpio, args.i2c1, args.i2c2, args.power_sequency, args.trigger_ipcore)
    se2300_dbg.cmdloop()
