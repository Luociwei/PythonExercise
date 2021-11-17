# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ad9628 import AD9628
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_def import PLSPIDef

__author__ = 'zhangdongdong@SmartGiant'
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


class AD9628Debuger(cmd.Cmd):
    prompt = 'ad9628>'
    intro = 'Xavier ad9628 debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register <register>
        <register>:0-0x102
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad9628.read_register(eval(line))
        print('{}'.format(result))

    @handle_errors
    def do_write_register(self, line):
        '''write_register <register> <value>
        <register>:0-0x102
        <value>:0~0xFF
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.write_register(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_get_chip_id(self, line):
        '''get_chip_id'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad9628.get_chip_id()
        print('{}'.format(result))

    @handle_errors
    def do_get_clock_speed_grade(self, line):
        '''git_clock_speed_grade'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.ad9628.git_clock_speed_grade()
        print('{}'.format(result))

    @handle_errors
    def do_select_channel(self, line):
        '''select_channel <channel>
        <channel>:"A", "B", "BOTH"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.select_channel(eval(line))
        print('Done')

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.get_sampling_rate()
        print('Done')

    @handle_errors
    def do_setup(self, line):
        '''setup <type> <format> <msps> <bits>
        <type>:"CMOS", "LVDS_ANSI", "LVDS_REDUCED"
        <format>:"OFFSET_BIN", "TWOS_COMPLEMENT", "GRAY_CODE"
        <msps>:80, 105, 125
        <bits>:"WIDTH_10", "WIDTH_12"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.setup(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_clock_phase(self, line):
        '''clock_phase <dco_invert_ctrl> <phase_ratio>
        <dco_invert_ctrl>:"NOT_INVERT", "INVERT"
        <phase_ratio>:"NO_DELAY", "ONE_INPUT", "TWO_INPUT", "THREE_INPUT",
                      "FOUR_INPUT", "FIVE_INPUT", "SIX_INPUT", "SEVEN_INPUT"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.clock_phase(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_clock_divide(self, line):
        '''clock_divide <divide_ratio> <div_next_sync> <div_sync_en>
        <divide_ratio>:"BY_1", "BY_2", "BY_3", "BY_4", "BY_5", "BY_6", "BY_7", "BY_8"
        <div_next_sync>:"NEX_SYNC", "NEX_ASYNC"
        <div_sync_en>:"SYNC_OPEN", "SYNC_CLOSE"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.clock_divide(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_clock_stabilizer(self, line):
        '''clock_stabilizer <state>
        <state>:"DIS_STABILIZE", "EN_STABILIZE"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.clock_stabilizer(eval(line))
        print('Done')

    @handle_errors
    def do_cmos_output_adjust(self, line):
        '''cmos_output_adjust <dco_strength> <data_strength>
        <dco_strength>:"1X", "2X", "3X", "4X"
        <data_strength>:"1X", "2X", "3X", "4X"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.cmos_output_adjust(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_data_output_delay(self, line):
        '''data_output_delay <dco_delay_en> <data_delay_en> <delay>
        <dco_delay_en>:"DCO_DELAY_OPEN", "DCO_DELAY_CLOSE"
        <data_delay_en>:"DATA_DELAY_OPEN", "DATA_DELAY_CLOSE"
        <delay>:"0_56_NS", "1_12_NS", "1_68_NS", "2_24_NS",
                "2_80_NS", "3_36_NS", "3_92_NS", "4_48_NS"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.data_output_delay(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_vref_set(self, line):
        '''vref_set <vref> <overrange_en>
        <vref>:"1_00", "1_14", "1_33", "1_60", "2_00"
        <overrange_en>:"OVERRANGE", "NOT_OVERRANGE"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.vref_set(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_power_mode(self, line):
        '''power_mode <refer> <work_mode>
        <refer>:"INTERNAL", "EXTERNAL"
        <work_mode>:"POWER_ON", "POWER_DOWN", "STANDBY", "DIGITAL_RESET"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.power_mode(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_soft_reset(self, line):
        '''soft_reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.soft_reset()
        print('Done')

    @handle_errors
    def do_chop_mode_open(self, line):
        '''chop_mode_open'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.chop_mode_open()
        print('Done')

    @handle_errors
    def do_chop_mode_close(self, line):
        '''chop_mode_close'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.chop_mode_close()
        print('Done')

    @handle_errors
    def do_test_mode_config(self, line):
        '''test_mode_config <user_mode> <rst_pn_l_en> <rst_pn_s_en> <output_mode>
        <user_mode>:"SINGLE", "ALTERNATE_REPEAT", "ONCE", "ALTERNATE_ONCE"
        <rst_pn_l_en>:"EN_RESET_L", "DIS_RESET_L"
        <rst_pn_s_en>:"EN_RESET_S", "DIS_RESET_S"
        <output_mode>:"OFF", "MIDSCALE_SHORT", "POSITIVE_FS", "NEGATIVE_FS",
                      "ALTERNATING_CHECKERBOARD", "PN_LONG_SEQUENCE", "PN_SHORT_SEQUENCE",
                      "ONE_WORD_TOGGLE", "USER_TEST_MODE", "RAMP_OUTPUT"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad9628.test_mode_config(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_bist_mode_open(self, line):
        '''bist_mode_open <init_sequence>
        <init_sequence>:"INIT_SEQ", "NOT_INIT_SEQ"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.bist_mode_open(eval(line))
        print('Done')

    @handle_errors
    def do_bist_mode_close(self, line):
        '''bist_mode_close'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad9628.bist_mode_close()
        print('Done')

    @handle_errors
    def do_customer_offset_adjust(self, line):
        '''customer_offset_adjust <data>
        <data>:0x00~0xFF
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.ad5592r.customer_offset_adjust(eval(line))
        print('Done')

    @handle_errors
    def do_user_define_pattern(self, line):
        '''user_define_pattern <pattern> <format>
        <pattern>:"PATTERN_1", "PATTERN_2"
        <format>:0x00~0xFFFF
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.user_define_pattern(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_user_io_ctrl(self, line):
        '''user_io_ctrl <io> <state>
        <io>:"OEB", "PDWN", "VCM", "SDIO"
        <state>:"EN_PIN", "DIS_PIN"
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.ad5592r.user_io_ctrl(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_ad9628_dbg(dev_name, pdwn_ctrl, oeb_ctrl, cs_ctrl, use_cs):
    ad9628_dbg = AD9628Debuger()
    if dev_name == '':
        spi_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLSPIDef.REG_SIZE)
            spi_bus = MIXQSPISG(axi4_bus)
            spi_bus.mode = 'MODE1'
        else:
            raise NotImplementedError('ps spi bus not support')
    ad9628_dbg.ad9628 = AD9628(spi_bus, pdwn_ctrl, oeb_ctrl, cs_ctrl, use_cs)
    return ad9628_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-io0', '--pdwn_ctrl', help='GPIO ctrl', default='')
    parser.add_argument('-io1', '--oeb_ctrl', help='GPIO ctrl', default='')
    parser.add_argument('-io2', '--cs_ctrl', help='GPIO ctrl', default='')
    parser.add_argument('-u', '--use_cs', help='whether to use cs ctrl', default=True)
    args = parser.parse_args()

    ad9628_dbg = create_ad9628_dbg(args.device, args.pdwn_ctrl, args.oeb_ctrl, args.cs_ctrl, args.use_cs)

    ad9628_dbg.cmdloop()
