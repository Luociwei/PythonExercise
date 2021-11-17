# -*- coding: utf-8 -*-
import argparse
import cmd
import inspect
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_mik002_sg_r import MIXMIK002SGR
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ipcore.mix_xtalkmeasure_sg import MIXXtalkMeasureSG
from mix.driver.smartgiant.warlock.module.mik002004_map import MIK002004
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.utility import utility


__author__ = 'Jiasheng.Xie'
__version__ = "V0.0.2"


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


class MIK002004Debuger(cmd.Cmd):
    prompt = 'warlock>'
    intro = 'Mix warlock debug tool'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout_s
        MIK002004 reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_start_record_data(self, line):
        '''start_record_data channel
        MIK002004 start collect the data and upload to DMA directly.
        channel:     string, ['left', 'right', 'both']
        eg: start_record_data "left" '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.start_record_data(eval(line))
        print("Done.")

    @handle_errors
    def do_stop_record_data(self, line):
        '''stop_record_data
        MIK002004  stop collect the data.
        eg: stop_record_data'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.stop_record_data()
        print("Done.")

    @handle_errors
    def do_enable_upload(self, line):
        '''enable_upload
        MIK002004 upoad mode open.
        eg:           enable_upload
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        # line = line.replace(' ', ',')
        self.warlock.enable_upload()
        print("Done.")

    @handle_errors
    def do_disable_upload(self, line):
        '''disable_upload
        MIK002004 upoad mode close.
        eg:           disable_upload
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        # line = line.replace(' ', ',')
        self.warlock.disable_upload()
        print("Done.")

    @handle_errors
    def do_set_sampling_rate(self, line):
        '''set_sampling_rate sampling_rate
        MIK002004 set sampling rate
        sampling_rate:     int, [192000, 96000, 48000], adc measure sampling rate.
        eg: set_sampling_rate 192000 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.set_sampling_rate(eval(line))
        print("Done.")

    @handle_errors
    def do_get_sampling_rate(self, line):
        '''get_sampling_rate
        MIK002004 get sampling rate.
        eg: get_sampling_rate '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.get_sampling_rate()
        print("Result:")
        print(result)

    @handle_errors
    def do_headset_loopback(self, line):
        '''headset_loopback mode
        MIK002004 set headset_loopback function.
        mode:      string, ['GB', 'CH'], GB mean global mode, CH mean china mode.
        eg: headset_loopback 'GB'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.headset_loopback(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_headphone_out(self, line):
        '''headphone_out range_name mode
        MIK002004 set headphone_out function.
        range_name: string, ['1Vrms', '3.5Vrms'].
        mode:       string, ['GB', 'CH'], GB mean global mode, CH mean china mode.
        eg: headphone_out '1Vrms' 'GB'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.warlock.headphone_out(*eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_line_out(self, line):
        '''line_out mode
        MIK002004 set line_out function.
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.line_out()
        print("Result:")
        print(result)

    @handle_errors
    def do_hp2mic_xtalk(self, line):
        '''hp2mic_xtalk range_name mode
        MIK002004 set hp2mic_xtalk function.
        mode:       string, ['GB', 'CH'], GB mean global mode, CH mean china mode.
        range_name: string, ["32ohm", "400ohm"]
        eg: hp2mic_xtalk 'GB' '32ohm'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.warlock.hp2mic_xtalk(*eval(line))
        print("Done.")

    @handle_errors
    def do_io_set(self, line):
        '''io_set io_list
        MIK002004 set io state.
        io_list:   list, [[pin,state],[pin,state]], pin [0~15], state [0,1].
        eg: io_set [[0,1],[1,1]] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.io_set(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_io_dir_set(self, line):
        '''io_dir_set io_list
        MIK002004 set io state.
        io_list:   list, [[pin,state],[pin,state]], pin [0~15], state [0,1].
        eg: io_dir_set [[0,'output'],[1,'output']] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.io_dir_set(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_io_read(self, line):
        '''io_read io_list
        MIK002004 read io state.
        io_list:   list, [pinx,pinx,… ,pinx], pin x mean [0~15].
        eg: io_read [0,1,15] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.io_read(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_io_dir_read(self, line):
        '''io_dir_read io_list
        MIK002004 read io direction.
        io_list:   list, [pinx,pinx,… ,pinx], pin x mean [0~15].
        eg: io_dir_read [0,5,15] '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.io_dir_read(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_adc_reset(self, line):
        '''adc_reset
        MIK002004 reset adc.'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.adc_reset()
        print('Result:')
        print(result)

    @handle_errors
    def do_measure(self, line):
        '''measure channel bandwidth_hz harmonic_num
        MIK002004 measure signal's Vpp, RMS, THD+N, THD.
        channel:         string, ["left", "right"].
        bandwidth_hz:    int, [24~95977], Measure signal's limit bandwidth, unit is Hz. The frequency of the
                                          signal should not be greater than half of the bandwidth.
        harmonic_num:    int, [2~10],     Use for measuring signal's THD.
        decimation_type: int, [1~255],    Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                          choose one suitable number.
        eg: measure "left" 20000 5'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.warlock.measure(*eval(line))
        print(result)

    @handle_errors
    def do_xtalk_measure(self, line):
        '''xtalk_measure channel bandwidth_hz harmonic_num
        MIK002004 xtalk_measure signal's Vpp, RMS, THD+N, THD.
        channel:         string, ["hp2mic", "hpl2r", "hpr2l"].
        bandwidth_hz:    int, [24~95977], Measure signal's limit bandwidth, unit is Hz. The frequency of the
                                          signal should not be greater than half of the bandwidth.
        harmonic_num:    int, [2~10],     Use for measuring signal's THD.
        decimation_type: int, [1~255],    Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                          choose one suitable number.
        eg: xtalk_measure "hp2mic" 20000 5'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.warlock.xtalk_measure(*eval(line))
        print(result)

    @handle_errors
    def do_mikey_tone(self, line):
        '''mikey_tone freq mode
        MIK002004 set signal output.
        freq:      string, ['S1', 'S2', 'S3', 'S0'].
        mode:      string, ['GB', 'CH'], GB mean global mode, CH mean china mode.
        eg: mikey_tone 'S1' 'CH' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.warlock.mikey_tone(*eval(line))
        print(result)

    @handle_errors
    def do_get_tone_detect_state(self, line):
        '''get_tone_detect_state
        MIK002004 get tone detect state.
        eg: get_tone_detect_state '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.get_tone_detect_state()
        print("Result:")
        print(result)

    @handle_errors
    def do_get_overflow_state(self, line):
        '''get_overflow_state
        MIK002004 get tone detect state.
        eg: get_overflow_state '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.get_overflow_state()
        print("Result:")
        print(result)

    @handle_errors
    def do_adc_hpf_state(self, line):
        '''adc_hpf_state state.
        MIK002004 set adc hpf pin.
        eg: adc_hpf_state "enable" '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.adc_hpf_state(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.warlock.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.is_use_cal_data()
        print('Result:')
        print(result)

    @handle_errors
    def do_get_calibration_mode(self, line):
        '''get_calibration_mode
        get calibration mode
        eg: get_calibration_mode'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.warlock.get_calibration_mode()
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


def create_warlock_dbg(ipcore_name, i2c_dev, analyzer_dev, adc_rst_pin, adc_ovfl_l_pin,
                       i2s_left_select_pin, i2s_right_select_pin, i2s_both_select_pin,
                       tone_detect_pin, upload_enable_pin, measure_enable_pin, sample_rate):

    warlock_dbg = MIK002004Debuger()

    if i2c_dev != '':
        if utility.is_pl_device(i2c_dev):
            axi4_bus = AXI4LiteBus(i2c_dev, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_dev)
    else:
        i2c_bus = None

    if ipcore_name != '':
        ipcore = MIXMIK002SGR(ipcore_name)
        warlock_dbg.warlock = MIK002004(i2c_bus, ipcore=ipcore)
    else:
        axi4 = AXI4LiteBus(analyzer_dev, 65535)
        analyzer = MIXXtalkMeasureSG(axi4)

        adc_rst_pin = GPIO(int(adc_rst_pin), 'output') if adc_rst_pin != "" else None
        adc_ovfl_l_pin = GPIO(int(adc_ovfl_l_pin), 'input') if adc_ovfl_l_pin != "" else None
        i2s_left_select_pin = GPIO(int(i2s_left_select_pin), 'output') if i2s_left_select_pin != "" else None
        i2s_right_select_pin = GPIO(int(i2s_right_select_pin), 'output') if i2s_right_select_pin != "" else None
        i2s_both_select_pin = GPIO(int(i2s_both_select_pin), 'output') if i2s_both_select_pin != "" else None
        tone_detect_pin = GPIO(int(tone_detect_pin), 'input') if tone_detect_pin != "" else None
        upload_enable_pin = GPIO(int(upload_enable_pin), 'output') if upload_enable_pin != "" else None
        measure_enable_pin = GPIO(int(measure_enable_pin), 'output') if measure_enable_pin != "" else None
        sample_rate = int(sample_rate)
        warlock_dbg.warlock = MIK002004(i2c=i2c_bus, ipcore=None,
                                        analyzer=analyzer, adc_rst_pin=adc_rst_pin,
                                        adc_ovfl_l_pin=adc_ovfl_l_pin, i2s_left_select_pin=i2s_left_select_pin,
                                        i2s_right_select_pin=i2s_right_select_pin,
                                        i2s_both_select_pin=i2s_both_select_pin,
                                        tone_detect_pin=tone_detect_pin, upload_enable_pin=upload_enable_pin,
                                        measure_enable_pin=measure_enable_pin, sample_rate=sample_rate)

    return warlock_dbg


arguments = [
    ['-ipcore', '--mix_mik002_sg_r', 'aggregated ipcore name', '/dev/MIX_MIK002_SG_R'],
    ['-i2c', '--i2c_device', 'i2c device name', '/dev/i2c-0'],
    ['-ip', '--analyzer', 'MIXAUT1 device name', '/dev/MIX_FftAnalyzer_SG_0'],
    ['-adc_rst', '--adc_rst_pin', 'i2c adc_rst name', '88'],
    ['-adc_ovfl', '--adc_ovfl_l_pin', 'i2c adc_ovfl name', '87'],
    ['-i2s_left', '--i2s_left_select_pin', 'i2s left channel select pin name', '92'],
    ['-i2s_right', '--i2s_right_select_pin', 'i2s right channel select pin name', '93'],
    ['-i2s_both', '--i2s_both_select_pin', 'i2s both channel select pin name', '90'],
    ['-tone_detect', '--tone_detect_pin', 'i2c tone_detect name', '86'],
    ['-upload_en', '--upload_enable_pin', 'upload enable pin name', '91'],
    ['-measure_en', '--measure_enable_pin', 'measure enable pin', '89'],
    ['-rate', '--sample_rate', 'set sample rate', '48000']
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()

    warlock_dbg = create_warlock_dbg(args.mix_mik002_sg_r, args.i2c_device, args.analyzer,
                                     args.adc_rst_pin, args.adc_ovfl_l_pin, args.i2s_left_select_pin,
                                     args.i2s_right_select_pin, args.i2s_both_select_pin, args.tone_detect_pin,
                                     args.upload_enable_pin, args.measure_enable_pin, args.sample_rate)
    warlock_dbg.cmdloop()
