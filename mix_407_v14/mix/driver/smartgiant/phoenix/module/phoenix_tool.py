# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import inspect
import traceback
from functools import wraps

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.smartgiant.common.ic.tps6598x.tps6598x import TPS6598x
from mix.driver.smartgiant.phoenix.module.phoenix import Phoenix

__author__ = 'TangentLin@SmartGiant' + 'yongjiu@SmartGiant' + 'zhangsong.deng@SmartGiant'
__version__ = '0.2'


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


class PhoenixDebuger(cmd.Cmd):
    prompt = 'phoenix>'
    intro = 'Xavier phoenix debug tool'

    @handle_errors
    def do_read_register_by_address(self, line):
        '''read_register_by_address <address>,
        <address>:
            0x00, 0x01, 0x03, 0x05, 0x06, 0x0f, 0x14, 0x15, 0x16, 0x17,
            0x1a, 0x20, 0x28, 0x29, 0x2d, 0x2f, 0x30, 0x31, 0x32, 0x33,
            0x34, 0x35, 0x36, 0x37, 0x38, 0x3f, 0x40, 0x47, 0x48, 0x49,
            0x4a, 0x4e, 0x4f, 0x50, 0x51, 0x52, 0x57, 0x58, 0x59, 0x5b,
            0x5c, 0x5d, 0x5f, 0x60, 0x61, 0x68, 0x69, 0x6e, 0x70, 0x72,
            0x7c, 0x7d, 0x7e, 0x7f
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.phoenix.read_register_by_address(eval(line))
        print(result)

    @handle_errors
    def do_read_all_registers(self, line):
        '''read_all_registers'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.phoenix.read_all_registers()
        print(result)

    @handle_errors
    def do_read_register_by_name(self, line):
        '''read_register_by_name <name>,
        <name>:
            VID, DID, UID, MODE_REG, VERSION_REG,
            DEVICE_INFO_REG, CUSTUSE, BOOT_FLAGS, STATUS_REG,
            DATA_STATUS_REG,CONTROL_CONFIG_REG, SYS_CONFIG_REG, SYS_POWER,
            PWR_STATUS, PD_STATUS, ACTIVE_CONTRACT_PDO,ACTIVE_CONTRACT_RDO,
            SINK_REQUEST_RDO, TX_SOURCE_CAP, TX_SINK_CAP,RX_SOURCE_CAP,
            RX_SINK_CAP, AUTONEGOTIATE_SINK, INT_EVENT1, INT_MASK1,
            INT_EVENT2, INT_MASK2, GPIO_CONFIG_REG_1, GPIO_CONFIG_REG_2,
            GPIO_STATUS, TX_IDENTITY_REG, RX_IDENTITY_SOP_REG,
            RX_IDENTITY_SOPP_REG, RX_VDM_REG, RX_ATTN_REG, ALT_MODE_ENTRY,
            DATA_CONTROL_REG, DP_CAPABILITIES_REG, INTEL_CONFIG_REG,
            DP_STATUS_REG, INTEL_STATUS_REG, PWR_SWITCH, CCn_PINSTATE,
            SLEEP_CONFIG_REG, FW_STATE_HISTORY, FW_STATE_CONFIG, FW_STATE,
            FW_STATE_FOCUS, MUX_DEBUG_REG, TI_VID_STATUS_REG,
            USER_VID_CONFIG, USER_VID_STATUS_REG,
            RX_USER_SVID_ATTN_VDM_REG, RX_USER_SVID_OTHER_VDM_REG
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.phoenix.read_register_by_name(line)
        print(result)

    @handle_errors
    def do_flash_programmer(self, line):
        '''flash_programmer <region> <file>
        <region>: region0 or region1
            In TI's definition, phoenix firmware have two regions and save in different flash memory.
        <file>: BIN file, as './test_region0.bin'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        result = self.phoenix.flash_programmer(*line)
        print(result)

    @handle_errors
    def do_set_sink_capabilities(self, line):
        '''set_sink_capabilities <PDO_number> <operating_current> <voltage> <min_current> <max_current>,
        PDO_number:           (1 ~ 7)
            PDO(Power Data object) which define Power Delivery messages. We can set seven sink PDOs at most.
        <operating_current>:  (0 ~ 10230) mA
        <voltage>:            (0 ~ 51150) mV
        <min_current>:        (0 ~ 10230) mA
        <max_current>:        (0 ~ 10230) mA
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        self.phoenix.set_sink_capabilities(*line)
        print('Done')

    @handle_errors
    def do_set_source_capabilities(self, line):
        '''set_source_capabilities <PDO_number> <source_switch> <voltage> <max_current>,<peak_current>
        <PDO_number>:   (1 ~ 7)
            PDO(Power Data Object) which define Power Delivery messages. We can set seven source PDOs at most.
        <source_switch>: (PP_5V, PP_HV or PP_HVE)
            PP_5V  --- Internal 5 Volt power path, only support PDO1
            PP_HV  --- Internal high voltage power path,
            PP_HVE --- External high voltage power path
        <voltage>:      (0 ~ 51150) mV
        <max_current>:  (0 ~ 10230) mA
        <peak_current>: (None,"100%","130%","150%","200%")
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        self.phoenix.set_source_capabilities(*line)
        print('Done')

    @handle_errors
    def do_read_all_adc(self, line):
        '''read_all_adc'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.phoenix.read_all_adc()
        print(result)

    @handle_errors
    def do_read_adc_by_name(self, line):
        '''read_adc_by_name <channel_name>,
        <channel_name>:
            BRICKID_RFU, CC1_BY2, CC1_BY5, CC2_BY2, CC2_BY5, GPIO_0, GPIO_1,
            GPIO_10 (BUSPOWER_Z), GPIO_2, GPIO_3, GPIO_4, GPIO_5, GPIO_5_RAW,
            GPIO_6, GPIO_7, GPIO_8, I2CADDR, IN_3P3V, I_CC, I_PP_5V0, I_PP_EXT,
            I_PP_HV, OUT_3P3V, PP_5V0, PP_CABLE, PP_HV, SENSEP, V1P8_A, V1P8_D,
            V3P3, VBUS, THERMAL_SENSE
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.phoenix.read_adc_by_name(line)
        print(result)

    @handle_errors
    def do_set_firmware_region_pointer(self, line):
        '''set_firmware_region_pointer <region_name>,
        <region_name>: region0 or region1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.phoenix.set_firmware_region_pointer(line)
        print('Done')

    @handle_errors
    def do_reset(self, line):
        '''reset'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.phoenix.reset()
        print('Done')

    @handle_errors
    def do_set_power_switch_config(self, line):
        '''set_power_switch_config <power_port> <state>,
        <power_port>: PP_5V, PP_HV or PP_HVE
                    PP_5V   Internal 5 Volt power path,
                    PP_HV   Internal high voltage power path,
                    PP_HVE  External high voltage power path
        <state>: state as follow,
                SwitchConfig_DISABLED,  SwitchConfig_AS_OUT,
                SwitchConfig_AS_IN,     SwitchConfig_AS_IN_AFTER_SYSRDY,
                SwitchConfig_AS_OUT_IN, SwitchConfig_AS_OUT_IN_AFTER_SYSRDY
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        self.phoenix.set_power_switch_config(*line)
        print('Done')

    @handle_errors
    def do_set_pin_dir(self, line):
        '''set_pin_dir <gpio_num> <state>,
        <gpio_num>: 0 ~ 17
        <state>: input or output
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        gpio_num = int(line[0])
        state = line[1]
        self.phoenix.set_pin_dir(gpio_num, state)
        print('Done')

    @handle_errors
    def do_set_pin(self, line):
        '''set_pin <gpio_num> <level>,
        <gpio_num>: 0 ~ 17
        <level>: 0 or 1
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        gpio_num = int(line[0])
        level = int(line[1])
        self.phoenix.set_pin(gpio_num, level)
        print('Done')

    @handle_errors
    def do_get_pin(self, line):
        '''get_pin <gpio_num>,
        <gpio_num>: 0 ~ 17
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.split(' ')
        gpio_num = int(line[0])
        result = self.phoenix.get_pin(gpio_num)
        print(result)

    @handle_errors
    def do_read_firmware_version(self, line):
        '''read_firmware_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.phoenix.read_firmware_version()
        print(result)

    @handle_errors
    def do_change_source_pdo_count(self, line):
        '''change_source_pdo_count <count>
        <count>: 1 ~ 7
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.phoenix.change_source_pdo_count(int(line))
        print('Done')

    @handle_errors
    def do_change_pullup(self, line):
        '''change_pullup <pullup_mode>
        pullup_mode: str(STD, 1.5A, 3.0A, NONE)
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.phoenix.change_pullup(line)
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        if '?' == line:
            print(get_function_doc(self))
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_bus(dev_name):
    if dev_name == '':
        return None

    axi4 = AXI4LiteBus(dev_name, 256)
    bus = PLI2CBus(axi4)
    return bus


def create_phoenix_dbg(dev_name, device_address):
    phoenix_dbg = PhoenixDebuger()
    bus = create_bus(dev_name)
    tps6598x = TPS6598x(device_address, bus)
    phoenix_dbg.phoenix = Phoenix(tps6598x)
    return phoenix_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='/dev/AXI4_I2C_0')
    parser.add_argument('-a', '--device_address', help='phoenix device address', default='0x38')

    args = parser.parse_args()

    phoenix_dbg = create_phoenix_dbg(args.device, int(args.device_address, 16))

    phoenix_dbg.cmdloop()
