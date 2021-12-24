# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.1'


class MP8859Def:
    DEVICE_ADDR_LIST = [0x60, 0x62, 0x64, 0x66]
    DEV_ID = 0x58

    # register
    VOUT_L_REGISTER = 0x00
    VOUT_H_REGISTER = 0x01
    VOUT_GO_REGISTER = 0x02
    IOUT_LIM_REGISTER = 0x03
    CTL1_REGISTER = 0x04
    CTL2_REGISTER = 0x05
    STATUS_REGISTER = 0x09
    DEV_ID_REGISTER = 0x28

    # register function fields
    VOUT_L_MASK = 0x7  # [2:0]
    VOUT_H_MASK = 0x7F8  # [10:3]
    VOUT_H_OFFSET = 3
    VOUT_TRIGGER_MASK = 0x01  # bit0=1, trigger Vout change
    IOUT_LIM_MASK = 0x7F  # [6:0]

    ENABLE_MASK = 0x80  # [7:7]
    ENABLE_OFFSET = 7
    ENABLE_DELAY = 0.055  # 55 ms

    PROTECT_MODE = ["latch-off", "hiccup"]
    PROTECT_MODE_MASK = 0x40  # [6:6]
    PROTECT_MODE_OFFSET = 6

    PWM_MODE = ["auto", "FPWM"]
    PWM_MODE_MASK = 0x10  # [4:4]
    PWM_MODE_OFFSET = 4

    LINE_DROP_COMP = [0, 150, 300, 500]
    LINE_DROP_COMP_MASK = 0xC0  # [7:6]
    LINE_DROP_COMP_OFFSET = 6


class MP8859Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MP8859(object):
    '''
    MP8859 function class, support output voltage 5 V ~ 20 V, current limit max 6.35 A

    ClassType = POWER

    Args:
        dev_addr:   hexmial,             MP8859 i2c bus device address.
        i2c_bus:    instance(I2C)/None,  i2c bus class instance, if not using, will create emulator.

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        mp8859 = MP8859(0x40, i2c_bus)

    '''
    rpc_public_api = ['init', 'output_volt_dc', 'output_current_dc', 'config', 'enable', 'disable']

    def __init__(self, dev_addr, i2c_bus=None):
        assert dev_addr in MP8859Def.DEVICE_ADDR_LIST

        self._dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('MP8859_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

    def init(self):
        '''
        MP8859 init.
        '''
        id_data = self._read_register(MP8859Def.DEV_ID_REGISTER, 1)[0]
        if id_data != MP8859Def.DEV_ID:
            raise MP8859Exception("MP8859 communication error, read id {} != {}".format(id_data, MP8859Def.DEV_ID))

        ctl1_data = self._read_register(MP8859Def.CTL1_REGISTER, 1)[0]
        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data & (~MP8859Def.ENABLE_MASK)])  # EN_bit=0
        time.sleep(MP8859Def.ENABLE_DELAY)
        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data | MP8859Def.ENABLE_MASK])  # EN_bit=1

    def _write_register(self, register, data):
        '''
        Write data to register.

        Args:
            register:  int, [0~0xff], register byte.
            data:      list, register bytes, as [0x00, 0xff].

        Examples:
            mp8859._write_register(0x00, [0x00, 0x07])

        '''
        assert isinstance(register, int)
        assert isinstance(data, list)

        self.i2c_bus.write(self._dev_addr, [register] + data)

    def _read_register(self, register, length):
        '''
        Read data from register.

        Args:
            register:  int, [0~0xff], register byte.
            length:    int, data length.

        Returns:
            list, data list

        Examples:
            data_list = mp8859._read_register(0x00, 1)
            print(data_list)

        '''
        assert isinstance(register, int)
        assert isinstance(length, int)

        return self.i2c_bus.write_and_read(self._dev_addr, [register], length)

    def output_volt_dc(self, channel, voltage):
        '''
        MP8859 output voltage, range 5 V ~ 20 V. If param voltage < 5 V, then output 5 V

        Args:
            channel:    int, [0], Channel index must be zero.
            voltage:    int, [0~20470], unit mV.

        Examples:
            mp8859.output_volt_dc(0, 5000)

        '''
        assert channel == 0
        assert isinstance(voltage, (int, float))
        assert 0 <= voltage and voltage <= 20470

        # 10mV/LSB
        code = int(voltage / 10)
        volt_l = code & MP8859Def.VOUT_L_MASK
        volt_h = (code & MP8859Def.VOUT_H_MASK) >> MP8859Def.VOUT_H_OFFSET

        reg_value = self._read_register(MP8859Def.VOUT_GO_REGISTER, 1)[0]
        reg_value = reg_value | MP8859Def.VOUT_TRIGGER_MASK

        self._write_register(MP8859Def.VOUT_L_REGISTER, [volt_l, volt_h, reg_value])

    def output_current_dc(self, channel, current):
        '''
        MP8859 output max current limit

        Args:
            channel:    int, [0], Channel index must be zero.
            current:    int, [0~6350], output max current, unit mA.

        Examples:
            mp8859.output_current_dc(0, 3000)

        '''
        assert channel == 0
        assert isinstance(current, (int, float))
        assert 0 <= current and current <= 6350

        # 50mA/LSB
        code = int(current / 50)
        current_data = code & MP8859Def.IOUT_LIM_MASK
        self._write_register(MP8859Def.IOUT_LIM_REGISTER, [current_data])

    def config(self, protect_mode, pwm_mode, line_drop_comp):
        '''
        config MP8859.

        Args:
            protect_mode:   string, ["hiccup", "latch-off"], over-current and over-voltage protection mode.
            pwm_mode:       string, ["auto", "FPWM"], pwm work mode, auto PFM/PWM or force PWM mode.
            line_drop_comp: int,    [0, 150, 300, 500], output voltage compensation vs. the load feature, unit is mV

        Examples:
            mp8859.config("hiccup", "auto", 150)
        '''
        assert protect_mode in MP8859Def.PROTECT_MODE
        assert pwm_mode in MP8859Def.PWM_MODE
        assert line_drop_comp in MP8859Def.LINE_DROP_COMP

        ctl1_data = self._read_register(MP8859Def.CTL1_REGISTER, 1)[0]
        ctl2_data = self._read_register(MP8859Def.CTL2_REGISTER, 1)[0]

        ctl1_data = ctl1_data & (~MP8859Def.PROTECT_MODE_MASK) | (
            MP8859Def.PROTECT_MODE.index(protect_mode) << MP8859Def.PROTECT_MODE_OFFSET)
        ctl1_data = ctl1_data & (~MP8859Def.PWM_MODE_MASK) | (
            MP8859Def.PWM_MODE.index(pwm_mode) << MP8859Def.PWM_MODE_OFFSET)
        ctl1_data = ctl1_data & (~MP8859Def.ENABLE_MASK)

        ctl2_data = ctl2_data & (~MP8859Def.LINE_DROP_COMP_MASK) | (
            MP8859Def.LINE_DROP_COMP.index(line_drop_comp) << MP8859Def.LINE_DROP_COMP_OFFSET)

        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data, ctl2_data])
        # enable config by setting EN_bit=1 after EN_bit=0
        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data | MP8859Def.ENABLE_MASK])

    def enable(self):
        '''
        Output enable.
        '''
        ctl1_data = self._read_register(MP8859Def.CTL1_REGISTER, 1)[0]
        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data | MP8859Def.ENABLE_MASK])
        return 'done'

    def disable(self):
        '''
        Output disable.
        '''
        ctl1_data = self._read_register(MP8859Def.CTL1_REGISTER, 1)[0]
        self._write_register(MP8859Def.CTL1_REGISTER, [ctl1_data & (~MP8859Def.ENABLE_MASK)])
        return 'done'
