# -*- coding: utf-8 -*-

import time
import copy
import ctypes
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ic.ad5675 import AD5675
from mix.driver.smartgiant.common.ic.ad5781 import AD5781
from mix.driver.core.bus.gpio import GPIO

__author__ = 'haojiong.fang@SmartGiant'
__version__ = 'V0.0.2'


psu004001_range_table = {
    "PS1_VOLT_SET": 0,
    "PS2_VOLT_SET": 1,
    "PS1_CURR_SET_1A": 2,
    "PS2_CURR_SET_1A": 3,
    "PS2_CURR_SET_3A": 4,
    "PS2_CURR_SET_10A": 5,
    "PS2_CURR_SET_30A": 6,

    "PS1_VOLT_READ": 7,
    "PS2_VOLT_READ": 8,
    "PS1_CURR_READ_1A": 9,
    "PS2_CURR_READ_1A": 10,
    "PS2_CURR_READ_3A": 11,
    "PS2_CURR_READ_10A": 12,
    "PS2_CURR_READ_30A": 13
}


class PSU004001Def:
    # These parameter obtained from PSU-004 ERS.
    PS1 = 1
    PS2 = 2
    PS_SELECT = [PS1, PS2]

    EEPROM_DEV_ADDR = 0x50   # CAT24C32
    SENSOR_DEV_ADDR = {PS1: 0x49, PS2: 0x48}  # NCT75DMR2G
    IO_EXP_DEV_ADDR = {PS1: 0x21, PS2: 0x20}  # CAT9555
    DAC_DEV_ADDR = {PS1: 0x0D, PS2: 0x0C}     # AD5675R

    RELAY_DELAY_MS = 50
    TIME_OUT = 6  # S
    DCDC_RAISE_DELAY_MS = 10
    DCDC_FALL_DELAY_MS = 50
    VI_DELAY_MS = 50

    DAC_REF_VOLT_mV = 2500
    DROP_VOLTAGE = {PS1: {"1A": 500}, PS2: {"1A": 1000, "3A": 1500, "10A": 1500, "30A": 2000}}
    DCDC_OUTPUT_MIN = {PS1: 2700, PS2: 500}
    DCDC_OUTPUT_MAX = {PS1: 5500, PS2: 7000}
    AD5781_DYNAMIC_LIB_NAME = "libad5781_psu004_driver.so"
    AD5675_MAX_OUTPUT = 5000
    AD5781_MIX_SPI_DEFAULT_SPEED = 1000000
    AD5781_MIX_SPI_MAX_SPEED = 20000000

    AD5781_MVREF_P = 5000
    AD5781_MVREF_N = 0
    AD5781_CONTROL_REGISTER = 0x2
    AD5781_INIT_DATA = 0x12

    DISCHARGE_ENABLE = "enable"
    DISCHARGE_DISABLE = "disable"
    DISCHARGE_STATE = [DISCHARGE_ENABLE, DISCHARGE_DISABLE, None]
    SOURCE_CVS = "CVS"
    SOURCE_CCS = "CCS"
    SOURCE_TYPES = [SOURCE_CVS, SOURCE_CCS, None]
    SWITCH_OUTPUT_ON = "enable"
    SWITCH_OUTPUT_OFF = "disable"
    SWITCH_OUTPUT_SELECT = [SWITCH_OUTPUT_ON, SWITCH_OUTPUT_OFF]
    SWITCH_SLEW_RATE_ON = 'enable'
    SWITCH_SLEW_RATE_OFF = 'disable'
    SWITCH_SLEW_RATE_SELECT = [SWITCH_SLEW_RATE_ON, SWITCH_SLEW_RATE_OFF]
    RESPONSE_SPEED_FAST = "fast"
    RESPONSE_SPEED_NORMAL = "normal"
    RESPONSE_SPEED = [RESPONSE_SPEED_FAST, RESPONSE_SPEED_NORMAL]

    READBACK_STATE_MASK = {PS1: 0x7 << 10, PS2: 0x3 << 14}
    READBACK_STATE = {PS1: {0x1800: "SRC_CC", 0x1400: "SINK_CC", 0xC00: "CV"},
                      PS2: {0x8000: "CC", 0x4000: "CV"}}
    IO_EXP_PINS_DIR = {PS1: [0x00, 0x1E], PS2: [0x00, 0xE0]}
    PGA_GAIN_CTRL_DEFAULT = {PS1: {"1A": 0b10110}, PS2: {"1A": 0b10110, "3A": 0b00101, "10A": 0b11000, "30A": 0b00111}}
    DAC_OVP_MAX_VOLT = {PS1: 5500, PS2: 5500}
    DAC_OCP_MAX_VOLT = {PS1: {"1A": 1100}, PS2: {"1A": 1100, "3A": 3300, "10A": 11000, "30A": 33000}}

    V_DCDC_CHAN = 0
    V_OUTPUT_CHAN = 1
    I_OUTPUT_CHAN = 2
    DAC_CHANNEL_PRESET = "RESET"
    DAC_CHANNEL_OVP = "OVP"
    DAC_CHANNEL_OCP = "OCP"
    DAC_CHANNEL_OCP_P = "OCP_P"
    DAC_CHANNEL_OCP_N = "OCP_N"
    DAC_CHANNEL_VOLT_SET = "VOLT_SET"
    DAC_CHANNEL_CURR_SET = "CURR_SET"
    DAC_CHANNEL = {PS1: {DAC_CHANNEL_PRESET: 0, DAC_CHANNEL_OVP: 1, DAC_CHANNEL_OCP_P: 2, DAC_CHANNEL_OCP_N: 3,
                   DAC_CHANNEL_VOLT_SET: 4, DAC_CHANNEL_CURR_SET: 5},
                   PS2: {DAC_CHANNEL_PRESET: 0, DAC_CHANNEL_OVP: 1, DAC_CHANNEL_OCP: 2, DAC_CHANNEL_VOLT_SET: 3,
                   DAC_CHANNEL_CURR_SET: 4}}
    OUTPUT_TYPE_VOLT = "VOLT"
    OUTPUT_TYPE_CURR = "CURR"
    OUTPUT_TYPES = {PS1: [OUTPUT_TYPE_VOLT, OUTPUT_TYPE_CURR],
                    PS2: [OUTPUT_TYPE_VOLT, OUTPUT_TYPE_CURR]}
    # slew rate scope: provided by the hardware engineer.
    SLEW_RATE_SCOPE = {PS1: {"V": [0.01, 500000], "1A": [0.01, 500000]},
                       PS2: {"V": [0.01, 500000], "1A": [0.01, 500000], "3A": [0.01, 1000000],
                             "10A": [0.01, 1000000], "30A": [0.01, 3000000]}}
    SLEW_RATE_DEFAULT = {PS1: {"V": SLEW_RATE_SCOPE[PS1]["V"][1], "1A": SLEW_RATE_SCOPE[PS1]["1A"][1]},
                         PS2: {"V": SLEW_RATE_SCOPE[PS2]["V"][1], "1A": SLEW_RATE_SCOPE[PS2]["1A"][1],
                               "3A": SLEW_RATE_SCOPE[PS2]["3A"][1], "10A": SLEW_RATE_SCOPE[PS2]["10A"][1],
                               "30A": SLEW_RATE_SCOPE[PS2]["30A"][1]}}

    PS1_PGA_G0 = 0
    PS1_PGA_G1 = 1
    PS1_PGA_G2 = 2
    PS1_PGA_G3 = 3
    PS1_PGA_G4 = 4
    PS1_DCDC_EN = 5
    PS1_OUTPUT_EN = 6
    PS1_DIS_EN = 7
    PS1_FAULT_DET = 9
    PS1_SRC_CC_DET_L = 10
    PS1_SINK_CC_DET_L = 11
    PS1_CV_DET_L = 12

    PS2_3A_PATH = 0
    PS2_30A_PATH = 1
    PS2_SHUNT_A0 = 2
    PS2_SHUNT_A1 = 3
    PS2_PGA_G0 = 4
    PS2_PGA_G1 = 5
    PS2_PGA_G2 = 6
    PS2_PGA_G3 = 7
    PS2_PGA_G4 = 8
    PS2_DCDC_EN = 9
    PS2_OUTPUT_EN = 10
    PS2_DIS_EN = 11
    RESP_SEL = 12
    PS2_FAULT_DET = 13
    PS2_CC_DET_L = 14
    PS2_CV_DET_L = 15

    IO_BIT_FAULT_DET = {PS1: PS1_FAULT_DET, PS2: PS2_FAULT_DET}


# range defines
psu004001_line_info = {
    PSU004001Def.PS1: {
        "pga_gain_0":
        {
            "0": {"bits": [(PSU004001Def.PS1_PGA_G0, 0)]},
            "1": {"bits": [(PSU004001Def.PS1_PGA_G0, 1)]}
        },
        "pga_gain_1":
        {
            "0": {"bits": [(PSU004001Def.PS1_PGA_G1, 0)]},
            "1": {"bits": [(PSU004001Def.PS1_PGA_G1, 1)]}
        },
        "pga_gain_2":
        {
            "0": {"bits": [(PSU004001Def.PS1_PGA_G2, 0)]},
            "1": {"bits": [(PSU004001Def.PS1_PGA_G2, 1)]}
        },
        "pga_gain_3":
        {
            "0": {"bits": [(PSU004001Def.PS1_PGA_G3, 0)]},
            "1": {"bits": [(PSU004001Def.PS1_PGA_G3, 1)]}
        },
        "pga_gain_4":
        {
            "0": {"bits": [(PSU004001Def.PS1_PGA_G4, 0)]},
            "1": {"bits": [(PSU004001Def.PS1_PGA_G4, 1)]}
        },
        "curr_range_sw":
        {
            "1A": {"bits": []}
        },
        "dcdc_enable": {
            "run": {"bits": [(PSU004001Def.PS1_DCDC_EN, 1)]},
            "shutdown": {"bits": [(PSU004001Def.PS1_DCDC_EN, 0)]}
        },
        "output_enable": {
            "on": {"bits": [(PSU004001Def.PS1_OUTPUT_EN, 1)]},
            "off": {"bits": [(PSU004001Def.PS1_OUTPUT_EN, 0)]}
        },
        "discharge_enable": {
            "enable": {"bits": [(PSU004001Def.PS1_DIS_EN, 1)]},
            "disable": {"bits": [(PSU004001Def.PS1_DIS_EN, 0)]}
        },
        "src_cc_stat": {
            "normal": {"bits": [(PSU004001Def.PS1_SRC_CC_DET_L, 1)]},
            "action": {"bits": [(PSU004001Def.PS1_SRC_CC_DET_L, 0)]}
        },
        "sink_cc_stat": {
            "normal": {"bits": [(PSU004001Def.PS1_SINK_CC_DET_L, 1)]},
            "action": {"bits": [(PSU004001Def.PS1_SINK_CC_DET_L, 0)]}
        },
        "cv_stat'": {
            "normal": {"bits": [(PSU004001Def.PS1_CV_DET_L, 1)]},
            "action": {"bits": [(PSU004001Def.PS1_CV_DET_L, 0)]}
        },
    },

    PSU004001Def.PS2: {
        "current_path_3A": {
            "enable": {"bits": [(PSU004001Def.PS2_3A_PATH, 1)]},
            "off": {"bits": [(PSU004001Def.PS2_3A_PATH, 0)]}
        },
        "current_path_30A": {
            "enable": {"bits": [(PSU004001Def.PS2_30A_PATH, 1)]},
            "off": {"bits": [(PSU004001Def.PS2_30A_PATH, 0)]}
        },
        "pga_gain_0":
        {
            "0": {"bits": [(PSU004001Def.PS2_PGA_G0, 0)]},
            "1": {"bits": [(PSU004001Def.PS2_PGA_G0, 1)]}
        },
        "pga_gain_1":
        {
            "0": {"bits": [(PSU004001Def.PS2_PGA_G1, 0)]},
            "1": {"bits": [(PSU004001Def.PS2_PGA_G1, 1)]}
        },
        "pga_gain_2":
        {
            "0": {"bits": [(PSU004001Def.PS2_PGA_G2, 0)]},
            "1": {"bits": [(PSU004001Def.PS2_PGA_G2, 1)]}
        },
        "pga_gain_3":
        {
            "0": {"bits": [(PSU004001Def.PS2_PGA_G3, 0)]},
            "1": {"bits": [(PSU004001Def.PS2_PGA_G3, 1)]}
        },
        "pga_gain_4":
        {
            "0": {"bits": [(PSU004001Def.PS2_PGA_G4, 0)]},
            "1": {"bits": [(PSU004001Def.PS2_PGA_G4, 1)]}
        },
        "curr_range_sw":
        {
            "1A": {"bits": [(PSU004001Def.PS2_SHUNT_A0, 0), (PSU004001Def.PS2_SHUNT_A1, 0),
                            (PSU004001Def.PS2_PGA_G0, 0), (PSU004001Def.PS2_PGA_G1, 1), (PSU004001Def.PS2_PGA_G2, 1),
                            (PSU004001Def.PS2_PGA_G3, 0), (PSU004001Def.PS2_PGA_G4, 1)]},
            "3A": {"bits": [(PSU004001Def.PS2_SHUNT_A0, 0), (PSU004001Def.PS2_SHUNT_A1, 0),
                            (PSU004001Def.PS2_PGA_G0, 1), (PSU004001Def.PS2_PGA_G1, 0), (PSU004001Def.PS2_PGA_G2, 1),
                            (PSU004001Def.PS2_PGA_G3, 0), (PSU004001Def.PS2_PGA_G4, 0)]},
            "10A": {"bits": [(PSU004001Def.PS2_SHUNT_A0, 1), (PSU004001Def.PS2_SHUNT_A1, 0),
                             (PSU004001Def.PS2_PGA_G0, 0), (PSU004001Def.PS2_PGA_G1, 0), (PSU004001Def.PS2_PGA_G2, 0),
                             (PSU004001Def.PS2_PGA_G3, 1), (PSU004001Def.PS2_PGA_G4, 1)]},
            "30A": {"bits": [(PSU004001Def.PS2_SHUNT_A0, 1), (PSU004001Def.PS2_SHUNT_A1, 0),
                             (PSU004001Def.PS2_PGA_G0, 1), (PSU004001Def.PS2_PGA_G1, 1), (PSU004001Def.PS2_PGA_G2, 1),
                             (PSU004001Def.PS2_PGA_G3, 0), (PSU004001Def.PS2_PGA_G4, 0)]},
        },
        "shunt_select": {
            "100m": {"bits": [(PSU004001Def.PS2_SHUNT_A1, 0), (PSU004001Def.PS2_SHUNT_A0, 0)]},
            "10m": {"bits": [(PSU004001Def.PS2_SHUNT_A1, 0), (PSU004001Def.PS2_SHUNT_A0, 1)]},
            "gnd": {"bits": [(PSU004001Def.PS2_SHUNT_A1, 1), (PSU004001Def.PS2_SHUNT_A0, 0)]},
            "5v": {"bits": [(PSU004001Def.PS2_SHUNT_A1, 1), (PSU004001Def.PS2_SHUNT_A0, 1)]},
        },
        "pga_gain_ctrl": {
            "16": {"bits": [(PSU004001Def.PS2_PGA_G4, 0), (PSU004001Def.PS2_PGA_G3, 0),
                            (PSU004001Def.PS2_PGA_G2, 1), (PSU004001Def.PS2_PGA_G1, 1),
                            (PSU004001Def.PS2_PGA_G0, 1)]},
            "44": {"bits": [(PSU004001Def.PS2_PGA_G4, 1), (PSU004001Def.PS2_PGA_G3, 1),
                            (PSU004001Def.PS2_PGA_G2, 0), (PSU004001Def.PS2_PGA_G1, 0),
                            (PSU004001Def.PS2_PGA_G0, 0)]},
        },
        "dcdc_enable": {
            "run": {"bits": [(PSU004001Def.PS2_DCDC_EN, 1)]},
            "shutdown": {"bits": [(PSU004001Def.PS2_DCDC_EN, 0)]}
        },
        "output_enable": {
            "on": {"bits": [(PSU004001Def.PS2_OUTPUT_EN, 1)]},
            "off": {"bits": [(PSU004001Def.PS2_OUTPUT_EN, 0)]}
        },
        "discharge_enable": {
            "enable": {"bits": [(PSU004001Def.PS2_DIS_EN, 1)]},
            "disable": {"bits": [(PSU004001Def.PS2_DIS_EN, 0)]}
        },
        "resp_sel": {
            "fast": {"bits": [(PSU004001Def.RESP_SEL, 1)]},
            "normal": {"bits": [(PSU004001Def.RESP_SEL, 0)]}
        },
        "cc_stat": {
            "normal": {"bits": [(PSU004001Def.PS2_CC_DET_L, 1)]},
            "action": {"bits": [(PSU004001Def.PS2_CC_DET_L, 0)]}
        },
        "cv_stat": {
            "normal": {"bits": [(PSU004001Def.PS2_CV_DET_L, 1)]},
            "action": {"bits": [(PSU004001Def.PS2_CV_DET_L, 0)]}
        }
    }
}

formula_diff = {
    "Vout2Vadc_1_diff": 1.1,
    "Vout2Vadc_2_diff": 1.1,

    "I1A2Vdac_1_diff": 1,
    "-I1A2Vdac_1_diff": 1,

    "I1A2Vdac_2_diff": 1,
    "I3A2Vdac_2_diff": 2.75,
    "I10A2Vdac_2_diff": 2.5,
    "I30A2Vdac_2_diff": 6.875,
}

formula = {
    # the formula Provided by hardware engineer

    # output
    # Vdcdc=1.2*Vdac+7.8mV
    "Vdcdc2Vadc_1": lambda vdcdc: ((vdcdc - 7.8) / 1.2),
    # Vdcdc=1.4242*Vdac-168.5
    "Vdcdc2Vadc_2": lambda vdcdc: ((vdcdc + 168.5) / 1.4242),

    # Voutput= 1.1*Vdac-4.95
    "Vout2Vadc_1": lambda vout: ((vout + 4.95) / formula_diff["Vout2Vadc_1_diff"]),
    # Voutput= 1.1*Vdac-14.6
    "Vout2Vadc_2": lambda vout: ((vout + 14.6) / formula_diff["Vout2Vadc_2_diff"]),

    # PS1
    # Iout=Vdac-4.5
    "I1A2Vdac_1": lambda curr: ((curr + 4.5) / formula_diff["I1A2Vdac_1_diff"]),
    # Iout=Vdac+4.5
    "-I1A2Vdac_1": lambda curr: ((curr - 4.5) / formula_diff["-I1A2Vdac_1_diff"]),

    # PS2
    # Iout=Vdac-13.273
    "I1A2Vdac_2": lambda curr: ((curr + 13.273) / formula_diff["I1A2Vdac_2_diff"]),
    # Iout=2.75*Vdac-36.500
    "I3A2Vdac_2": lambda curr: ((curr + 36.500) / formula_diff["I3A2Vdac_2_diff"]),
    # Iout=2.5*Vdac-33.182
    "I10A2Vdac_2": lambda curr: ((curr + 33.182) / formula_diff["I10A2Vdac_2_diff"]),
    # Iout=6.875*Vdac-91.250
    "I30A2Vdac_2": lambda curr: ((curr + 91.250) / formula_diff["I30A2Vdac_2_diff"]),

    # measure
    # Vvolt_meas= -Vout
    "Vadc2Vout": lambda vadc: (vadc / -1),
    # Vcurr_meas= -1.1*Iout
    "Vadc2I1A": lambda vadc: (vadc / -1.1),
    # Vcurr_meas= -0.4*Iout
    "Vadc2I3A": lambda vadc: (vadc / -0.4),
    # Vcurr_meas= -0.44*Iout
    "Vadc2I10A": lambda vadc: (vadc / -0.44),
    # Vcurr_meas= -0.16*Iout
    "Vadc2I30A": lambda vadc: (vadc / -0.16),

    # OVP/OCP
    # Vdac_ovp=0.9*Vlimit       (PS1/PS2)
    "Vovp2Vlimit": lambda vovp: (vovp * 0.9),
    # Vdac_ocp=4.4*Ilimit       (PS1)
    "Vocp2I1A_1": lambda vocp: (vocp * 4.4),
    # Vadc_ocp=4.0964*Ilimit    (PS2)
    "Vocp2I1A_2": lambda vocp: (vocp * 4.0964 / 4),
    # Vadc_ocp=1.4896*Ilimit    (PS2)
    "Vocp2I3A_2": lambda vocp: (vocp * 1.4896 / 4),
    # Vadc_ocp=0.40964*Ilimit   (PS2)
    "Vocp2I10A_2": lambda vocp: (vocp * 0.40964),
    # Vadc_ocp=0.14896*Ilimit   (PS2)
    "Vocp2I30A_2": lambda vocp: (vocp * 0.14896),
}


class Psu004001Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PSU004001(SGModuleDriver):
    '''
    PSU004001(PSU-004-001) is a power module with single channel and two quadrants,

    which is used for output voltage/current, the range of voltage is 0~5V,
    the range of current is PS1:-1~1A, PS2:1~30A.

    Args:
        i2c:    instance(I2C), is used to create DAC(AD5675), EEPROM, temperature sensor and IO expender.
        spi:    string, is used to create AD5781 chip.
        gpio_vidac_reset1:  instance(GPIO), PS1 VI_DAC_RESET1_L GPIO pin
        gpio_idac_sync1:    instance(GPIO), PS1 IDAC_SYNC1_L GPIO pin
        gpio_vdac_sync1:    instance(GPIO), PS1 VDAC_SYNC1_L GPIO pin
        gpio_vidac_reset:   instance(GPIO), PS2 VI_DAC_RESET_L GPIO pin
        gpio_idac_sync:     instance(GPIO), PS2 IDAC_SYNC_L GPIO pin
        gpio_vdac_sync:     instance(GPIO), PS2 VDAC_SYNC_L GPIO pin

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        gpio_vidac_reset1 = GPIO(995, 'output')
        gpio_idac_sync1 = GPIO(996, 'output')
        gpio_vdac_sync1 = GPIO(997, 'output')
        gpio_vidac_reset = GPIO(992, 'output')
        gpio_idac_sync = GPIO(993, 'output')
        gpio_vdac_sync = GPIO(994, 'output')
        psu004001 = PSU004001(i2c_bus, '/dev/MIX_QSPI_SG_0', gpio_vidac_reset1, gpio_idac_sync1,
                              gpio_vdac_sync1, gpio_vidac_reset, gpio_idac_sync, gpio_vdac_sync)

        # PSU004001 PS1 output 2000mV, 1000mA
        psu004001.reset()
        psu004001.power_output(1, '1A', 2000, 1000)

    '''
    compatible = ["GQQ-PU04-5-010", "GQQ-PU04-5-020"]
    rpc_public_api = ['post_power_on_init', 'reset', 'power_output', 'output_enable', 'power_type',
                      'discharge_control', 'power_readback_voltage_calc', 'power_readback_current_calc',
                      'curr_range_switch', 'get_psu_temperatures', 'get_power_state', 'set_drop_voltage',
                      'set_gain', 'protection_set', 'slew_rate_enable', 'set_slew_rate', 'set_spi_speed',
                      'get_spi_speed', 'set_ad5675_voltage', 'set_ad5781_voltage', 'get_driver_version',
                      'resp_select'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, spi, gpio_vidac_reset1, gpio_idac_sync1, gpio_vdac_sync1,
                 gpio_vidac_reset, gpio_idac_sync, gpio_vdac_sync):
        if i2c and spi:
            self.nct75 = dict()
            self.nct75[PSU004001Def.PS1] = NCT75(PSU004001Def.SENSOR_DEV_ADDR[PSU004001Def.PS1], i2c)
            self.nct75[PSU004001Def.PS2] = NCT75(PSU004001Def.SENSOR_DEV_ADDR[PSU004001Def.PS2], i2c)
            self.eeprom = CAT24C32(PSU004001Def.EEPROM_DEV_ADDR, i2c)
            self.io_exp = dict()
            self.io_exp[PSU004001Def.PS1] = CAT9555(PSU004001Def.IO_EXP_DEV_ADDR[PSU004001Def.PS1], i2c)
            self.io_exp[PSU004001Def.PS2] = CAT9555(PSU004001Def.IO_EXP_DEV_ADDR[PSU004001Def.PS2], i2c)
            self.dac = dict()
            self.dac[PSU004001Def.PS1] = AD5675(PSU004001Def.DAC_DEV_ADDR[PSU004001Def.PS1],
                                                i2c, mvref=PSU004001Def.DAC_REF_VOLT_mV)
            self.dac[PSU004001Def.PS2] = AD5675(PSU004001Def.DAC_DEV_ADDR[PSU004001Def.PS2],
                                                i2c, mvref=PSU004001Def.DAC_REF_VOLT_mV)

            # Load AD5781 dynamic library.
            self.ad5781_lib = ctypes.cdll.LoadLibrary(PSU004001Def.AD5781_DYNAMIC_LIB_NAME)

            # Create the spi object of AD5781.
            self.mix_spi = self.ad5781_lib.mix_spi_open(ctypes.c_char_p(spi))
            if self.mix_spi == 0:
                raise Psu004001Exception("Open ad5781 device failure.")

            self.gpio_ps2_vidac_reset = gpio_vidac_reset
            self.gpio_ps2_idac_sync = gpio_idac_sync
            self.gpio_ps2_vdac_sync = gpio_vdac_sync
            self.gpio_ps1_vidac_reset = gpio_vidac_reset1
            self.gpio_ps1_idac_sync = gpio_idac_sync1
            self.gpio_ps1_vdac_sync = gpio_vdac_sync1
            # Map output type to gpio fd.
            self.type_gpio_map = {
                PSU004001Def.PS1: {PSU004001Def.OUTPUT_TYPE_VOLT: self.gpio_ps1_vdac_sync.gpio_value_fd,
                                   PSU004001Def.OUTPUT_TYPE_CURR: self.gpio_ps1_idac_sync.gpio_value_fd},
                PSU004001Def.PS2: {PSU004001Def.OUTPUT_TYPE_VOLT: self.gpio_ps2_vdac_sync.gpio_value_fd,
                                   PSU004001Def.OUTPUT_TYPE_CURR: self.gpio_ps2_idac_sync.gpio_value_fd}
            }
            self.ad5781 = {PSU004001Def.PS1: {PSU004001Def.OUTPUT_TYPE_VOLT: None, PSU004001Def.OUTPUT_TYPE_CURR: None},
                           PSU004001Def.PS2: {PSU004001Def.OUTPUT_TYPE_VOLT: None, PSU004001Def.OUTPUT_TYPE_CURR: None}}

            super(PSU004001, self).__init__(self.eeprom, self.nct75[PSU004001Def.PS1],
                                            range_table=psu004001_range_table)

        else:
            raise Psu004001Exception("Parameter error")

    def __del__(self):
        self.ad5781_lib.mix_spi_close(self.mix_spi)
        for ps in PSU004001Def.PS_SELECT:
            for type in PSU004001Def.OUTPUT_TYPES[ps]:
                self.ad5781_lib.ad5781_close(self.ad5781[ps][type])

    def post_power_on_init(self, timeout=PSU004001Def.TIME_OUT):
        '''
        Init psu004001 module to a know harware state.

        This function will set tca9538 io direction to output and set DAC.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.post_power_on_init()
        '''
        self.load_calibration()
        self.reset(timeout)
        return "done"

    def reset(self, timeout=PSU004001Def.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.reset()

        '''
        start_time = time.time()
        while 1:
            try:
                # Init the variables.
                self.line_path = {PSU004001Def.PS1: {}, PSU004001Def.PS2: {}}
                self.source_type = {PSU004001Def.PS1: PSU004001Def.SOURCE_CVS,
                                    PSU004001Def.PS2: PSU004001Def.SOURCE_CVS}
                self.set_pga_gain = {PSU004001Def.PS1: {}, PSU004001Def.PS2: {}}
                self.drop_voltage = copy.deepcopy(PSU004001Def.DROP_VOLTAGE)
                self.output_sw = {PSU004001Def.PS1: PSU004001Def.SWITCH_OUTPUT_OFF,
                                  PSU004001Def.PS2: PSU004001Def.SWITCH_OUTPUT_OFF}
                self.curr = {PSU004001Def.PS1: None, PSU004001Def.PS2: None}
                self.volt = {PSU004001Def.PS1: None, PSU004001Def.PS2: None}
                self.curr_path = None
                self.slew_rate = {PSU004001Def.PS1: dict(), PSU004001Def.PS2: dict()}
                self.sw_slew_rate = {PSU004001Def.PS1: None, PSU004001Def.PS2: None}

                # Set OVP, OCP to maximum.
                self.dac_ovp_set_volt = copy.deepcopy(PSU004001Def.DAC_OVP_MAX_VOLT)
                self.dac_ocp_set_volt = copy.deepcopy(PSU004001Def.DAC_OCP_MAX_VOLT)

                # Hardware reset AD5781 and AD5675.
                # The control timing must be pulled up first and then down.
                # AD5781 and AD5675 share the reset pin.
                self.gpio_ps1_vidac_reset.set_level(1)
                self.gpio_ps2_vidac_reset.set_level(1)
                time.sleep(0.1)
                self.gpio_ps1_vidac_reset.set_level(0)
                self.gpio_ps2_vidac_reset.set_level(0)
                time.sleep(0.1)
                self.gpio_ps1_vidac_reset.set_level(1)
                self.gpio_ps2_vidac_reset.set_level(1)
                time.sleep(0.1)

                for ps in PSU004001Def.PS_SELECT:
                    self.io_exp[ps].set_pins_dir(PSU004001Def.IO_EXP_PINS_DIR[ps])
                    # Init AD5675.
                    self.dac[ps].set_gain(2)
                    [self.dac[ps].set_mode(x, "normal") for x in range(6)]
                    [self.set_ad5675_voltage(ps, x, 0) for x in range(6)]

                    self.set_line_path(ps, "dcdc_enable", "shutdown")
                    self.set_line_path(ps, "output_enable", "off")
                    self.set_line_path(ps, "discharge_enable", "disable")
                    self.curr_range_switch(ps, "1A")
                    self.set_gain(ps, PSU004001Def.PGA_GAIN_CTRL_DEFAULT[ps]["1A"])

                    # The voltage of overcurrent protection set to max,
                    # for prevending spurious triggering from relay shaking.
                    self.protection_set(ps, "1A", self.dac_ovp_set_volt[ps], self.dac_ocp_set_volt[ps]["1A"])

                    # Init AD5781.
                    for type in PSU004001Def.OUTPUT_TYPES[ps]:
                        if self.ad5781[ps][type] is not None:
                            self.ad5781_lib.ad5781_close(self.ad5781[ps][type])

                        lib_open = self.ad5781_lib.ad5781_open
                        self.ad5781[ps][type] = lib_open(self.mix_spi,
                                                         ctypes.c_uint32(PSU004001Def.AD5781_MVREF_P),
                                                         ctypes.c_uint32(PSU004001Def.AD5781_MVREF_N),
                                                         ctypes.c_uint32(self.type_gpio_map[ps][type]))

                    # Calculate volt slew rate.
                    self.sw_slew_rate[ps] = PSU004001Def.SWITCH_SLEW_RATE_OFF
                    for type, rate in PSU004001Def.SLEW_RATE_DEFAULT[ps].items():
                        self.set_slew_rate(ps, type, rate)
                    self.output_sw[ps] = PSU004001Def.SWITCH_OUTPUT_OFF
                    self.curr[ps] = None
                    self.volt[ps] = None

                # Shut down current path.
                self.set_line_path(PSU004001Def.PS2, "current_path_3A", "off")
                self.set_line_path(PSU004001Def.PS2, "current_path_30A", "off")

                return "done"
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Psu004001Exception("Timeout: {}".format(e.message))

    def power_output(self, ps, curr_range, volt, curr):
        '''
        Set PSU004001 power output.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            curr_range:    string, ["1A", "3A", "10A, "30A"], the current range.
            volt:    int/float, [0~5000], unit mV.
            curr:    int/float, [-1000~30000], unit mA.
                     ps1: "1A", [-1000~1000]
                     ps2: "1A", [0~1000]
                          "3A", [0~3000]
                          "10A", [0~10000]
                          "30A", [0~30000]

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.power_output(1, '1A', 4000, 500)
            psu004001.power_output(1, '10A', 5000, 3000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert curr_range in psu004001_line_info[ps]["curr_range_sw"]
        assert isinstance(volt, (int, float))
        assert isinstance(curr, (int, float))
        assert 0 <= volt <= PSU004001Def.AD5781_MVREF_P
        assert 0 <= abs(curr) <= int(curr_range[:-1]) * 1000

        if self._get_io(ps, PSU004001Def.IO_BIT_FAULT_DET[ps]):
            print("----- [Protection detected] -----")
            self.output_enable(ps, 'disable')
            time.sleep(0.01)

        self.curr_range_switch(ps, curr_range)
        if ps == PSU004001Def.PS2:
            if curr < 0:
                raise Psu004001Exception("Set current error")
            if curr_range in ["1A", "3A"]:
                current_path = "current_path_3A"
            elif curr_range in ["10A", "30A"]:
                current_path = "current_path_30A"
            if self.curr_path != current_path:
                if current_path == "current_path_3A":
                    self.set_line_path(PSU004001Def.PS2, "current_path_3A", "enable")
                    self.set_line_path(PSU004001Def.PS2, "current_path_30A", "off")
                elif current_path == "current_path_30A":
                    self.set_line_path(PSU004001Def.PS2, "current_path_30A", "enable")
                    self.set_line_path(PSU004001Def.PS2, "current_path_3A", "off")
                self.curr_path = current_path

        # The voltage of overcurrent protection set to max,
        # for prevending spurious triggering from relay shaking.
        self.protection_set(ps, curr_range, self.dac_ovp_set_volt[ps],
                            self.dac_ocp_set_volt[ps][curr_range])

        self.set_line_path(ps, "dcdc_enable", "run")
        if PSU004001Def.SWITCH_OUTPUT_OFF == self.output_sw[ps]:
            time.sleep(0.03)
        elif volt != self.volt[ps]:
            time.sleep(0.01)
        self.set_line_path(ps, "output_enable", "on", PSU004001Def.RELAY_DELAY_MS)

        cal_volt = self.calibrate("PS" + str(ps) + "_VOLT_SET", volt)
        cal_curr = self.calibrate("PS" + str(ps) + "_CURR_SET_" + curr_range, curr)

        # This step is only required during the debugging phase because set_gain interface may be actively called.
        if self.set_pga_gain[ps] != PSU004001Def.PGA_GAIN_CTRL_DEFAULT[ps][curr_range]:
            self.set_gain(ps, PSU004001Def.PGA_GAIN_CTRL_DEFAULT[ps][curr_range])

        if self.output_sw[ps] == PSU004001Def.SWITCH_OUTPUT_OFF or self.volt[ps] is None or self.volt[ps] < volt:
            # Set dcdc_output
            Vadc = formula["Vdcdc2Vadc_" + str(ps)](volt + self.drop_voltage[ps][curr_range])
            if Vadc < PSU004001Def.DCDC_OUTPUT_MIN[ps]:
                Vadc = formula["Vdcdc2Vadc_" + str(ps)](PSU004001Def.DCDC_OUTPUT_MIN[ps])
            elif Vadc > PSU004001Def.DCDC_OUTPUT_MAX[ps]:
                Vadc = formula["Vdcdc2Vadc_" + str(ps)](PSU004001Def.DCDC_OUTPUT_MAX[ps])
            if Vadc > PSU004001Def.AD5675_MAX_OUTPUT:
                Vadc = PSU004001Def.AD5675_MAX_OUTPUT
            self.set_ad5675_voltage(ps, PSU004001Def.DAC_CHANNEL[ps][PSU004001Def.DAC_CHANNEL_PRESET], Vadc)
            time.sleep(PSU004001Def.DCDC_RAISE_DELAY_MS / 1000.0)

        if self.source_type[ps] == PSU004001Def.SOURCE_CVS:
            # Set output curr.
            if curr >= 0:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, curr_range,
                                        formula["I" + curr_range + "2Vdac_" + str(ps)](cal_curr))
            else:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, curr_range,
                                        formula["-I" + curr_range + "2Vdac_" + str(ps)](abs(cal_curr)))
            time.sleep(PSU004001Def.VI_DELAY_MS / 1000.0)

            # Set output volt.
            self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_VOLT, curr_range,
                                    formula["Vout2Vadc_" + str(ps)](cal_volt))

        elif self.source_type[ps] == PSU004001Def.SOURCE_CCS:
            # Set output volt.
            self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_VOLT, curr_range,
                                    formula["Vout2Vadc_" + str(ps)](cal_volt))
            time.sleep(PSU004001Def.VI_DELAY_MS / 1000.0)

            # Set output curr.
            if curr >= 0:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, curr_range,
                                        formula["I" + curr_range + "2Vdac_" + str(ps)](cal_curr))
            else:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, curr_range,
                                        formula["-I" + curr_range + "2Vdac_" + str(ps)](abs(cal_curr)))

        if self.output_sw[ps] == PSU004001Def.SWITCH_OUTPUT_ON and self.volt[ps] > volt:
            # Set dcdc_output
            time.sleep(PSU004001Def.DCDC_RAISE_DELAY_MS / 1000.0)
            Vadc = formula["Vdcdc2Vadc_" + str(ps)](volt + self.drop_voltage[ps][curr_range])
            if Vadc < PSU004001Def.DCDC_OUTPUT_MIN[ps]:
                Vadc = formula["Vdcdc2Vadc_" + str(ps)](PSU004001Def.DCDC_OUTPUT_MIN[ps])
            elif Vadc > PSU004001Def.DCDC_OUTPUT_MAX[ps]:
                Vadc = formula["Vdcdc2Vadc_" + str(ps)](PSU004001Def.DCDC_OUTPUT_MAX[ps])
            self.set_ad5675_voltage(ps, PSU004001Def.DAC_CHANNEL[ps][PSU004001Def.DAC_CHANNEL_PRESET], Vadc)

        self.curr[ps] = curr
        self.volt[ps] = volt
        self.output_sw[ps] = PSU004001Def.SWITCH_OUTPUT_ON

        return "done"

    def output_enable(self, ps, state):
        '''
        Enable/disable PSU power output.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            state:  string, ["enable", "disable"], output the switch.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.output_enable(1, "enable")

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert state in PSU004001Def.SWITCH_OUTPUT_SELECT

        if state == PSU004001Def.SWITCH_OUTPUT_ON:
            self.curr[ps] = self.curr[ps] if self.curr[ps] else 0
            self.volt[ps] = self.volt[ps] if self.volt[ps] else 0
            self.power_output(ps, self.line_path[ps]["curr_range_sw"], self.volt[ps], self.curr[ps])
        else:
            if self.source_type[ps] == PSU004001Def.SOURCE_CVS:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_VOLT, self.line_path[ps]["curr_range_sw"], 0)
                time.sleep(PSU004001Def.VI_DELAY_MS / 1000.0)
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, self.line_path[ps]["curr_range_sw"], 0)
                time.sleep(PSU004001Def.DCDC_FALL_DELAY_MS / 1000.0)
            elif self.source_type[ps] == PSU004001Def.SOURCE_CCS:
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_CURR, self.line_path[ps]["curr_range_sw"], 0)
                time.sleep(PSU004001Def.VI_DELAY_MS / 1000.0)
                self.set_ad5781_voltage(ps, PSU004001Def.OUTPUT_TYPE_VOLT, self.line_path[ps]["curr_range_sw"], 0)
                time.sleep(PSU004001Def.DCDC_FALL_DELAY_MS / 1000.0)

            self.set_line_path(ps, "output_enable", "off")
            self.set_line_path(ps, "dcdc_enable", "shutdown")
            self.output_sw[ps] = PSU004001Def.SWITCH_OUTPUT_OFF

        return "done"

    def power_type(self, ps, source_type=None):
        '''
        Get or set power type.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            source_type: string, ["CVS", "CCS", None],
                                 "CVS": set constant voltage source,
                                 "CCS": set constant current source.
                                 None: get voltage source

        Returns:
            string, ["done", "CVS", "CCS"],
                    "done": set power type successful;
                    "CVS", "CCS": get power type result.

        Example:
            result = psu004001.power_type(1)
            psu004001.power_type(1, "CVS")

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert source_type in PSU004001Def.SOURCE_TYPES

        if source_type is None:
            return self.source_type[ps]
        else:
            self.source_type[ps] = source_type
            return "done"

    def discharge_control(self, ps, state=None):
        '''
        Enable, disable power discharge, or read discharge state.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            state:  string, ["enable", "disable", None],
                            "enable": enable discharge,
                            "disable": disable discharge.
                            None: get state.

        Returns:
            string, ["enable", "disable", "done"],
                    "done": enable or disable power discharge successful;
                    "enable", "disable": read discharge state result.

        Example:
            result = psu004001.discharge_control(1)
            psu004001.discharge_control(1, "enable")

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert state in PSU004001Def.DISCHARGE_STATE

        if state is None:
            io_state_l = self.io_exp[ps].get_ports()
            io_state = io_state_l[0] + (io_state_l[1] << 8)
            if ps == PSU004001Def.PS1:
                mask = (1 << PSU004001Def.PS1_DIS_EN) & 0xFFFF
            elif ps == PSU004001Def.PS2:
                mask = (1 << PSU004001Def.PS2_DIS_EN) & 0xFFFF

            dis_select = 1 if io_state & mask else 0
            if dis_select:
                self.line_path[ps]["discharge_enable"] = "enable"
            else:
                self.line_path[ps]["discharge_enable"] = "disable"
            return self.line_path[ps]["discharge_enable"]
        else:
            self.set_line_path(ps, "discharge_enable", state)
            return "done"

    def power_readback_voltage_calc(self, ps, volt):
        '''
        Calculate and calibrate read back power voltage.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            volt:    float, ADC read back voltage, unit mV.

        Returns:
            float, unit mV, voltage value.

        Examples:
            volt = psu004001.power_readback_voltage_calc(1, 1000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert isinstance(volt, (int, float))

        volt = formula["Vadc2Vout"](volt)
        return self.calibrate("PS" + str(ps) + "_VOLT_READ", volt)

    def power_readback_current_calc(self, ps, volt):
        '''
        Calculate and calibrate read back power current.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            volt:   float, ADC read back voltage, unit mV.

        Returns:
            float, unit mA, current value.

        Examples:
            current = psu004001.power_readback_current_calc(1, 1000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert isinstance(volt, (int, float))

        curr_range = self.line_path[ps]["curr_range_sw"]
        curr = formula["Vadc2I" + curr_range](volt)
        return self.calibrate("PS" + str(ps) + "_CURR_READ_" + curr_range, curr)

    def curr_range_switch(self, ps, curr_range):
        '''
        Switch current range.

        Args:
            ps:             int, [1, 2], 1:PS1; 2:PS2
            curr_range:    string, ["1A", "3A", "10A, "30A"], the current range.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.curr_range_switch(2, "3A")

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert curr_range in psu004001_line_info[ps]["curr_range_sw"]

        self.set_line_path(ps, "curr_range_sw", curr_range, PSU004001Def.RELAY_DELAY_MS)
        if curr_range == "30A":
            self.resp_select(PSU004001Def.RESPONSE_SPEED_FAST)
        else:
            self.resp_select(PSU004001Def.RESPONSE_SPEED_NORMAL)

        return "done"

    def get_psu_temperatures(self):
        '''
        Get the temperatures of PS1 and PS2.

        Returns:
            string, "PS1: 34, PS2: 30"

        Example:
            result = psu004001.get_psu_temperatures()

        '''
        temp = []
        temp.append(self.nct75[PSU004001Def.PS1].get_temperature())
        temp.append(self.nct75[PSU004001Def.PS2].get_temperature())
        return "PS1: {0}, PS2: {1}".format(temp[0], temp[1])

    def get_power_state(self):
        '''
        Get power state.

        Returns:
            string, "PS1: SRC_CC, PS2: CV"

        Example:
            result = psu004001.get_power_state()

        '''
        state = []
        for ps in PSU004001Def.PS_SELECT:
            if self._get_io(ps, PSU004001Def.IO_BIT_FAULT_DET[ps]):
                state.append('fault')
            else:
                io_state_l = self.io_exp[ps].get_ports()
                io_state = io_state_l[0] + (io_state_l[1] << 8)
                power_state = "error"
                curr_select = io_state & PSU004001Def.READBACK_STATE_MASK[ps]
                if curr_select in PSU004001Def.READBACK_STATE[ps]:
                    power_state = PSU004001Def.READBACK_STATE[ps][curr_select]
                state.append(power_state)
        return "PS1: {0}, PS2: {1}".format(state[0], state[1])

    def set_drop_voltage(self, ps, curr_range, volt):
        '''
        Set the drop voltage from Vdcdc to Vout, this is a debug function.

        Args:
            ps:             int, [1, 2], 1:PS1; 2:PS2
            curr_range:     string, ["1A", "3A", "10A, "30A"], the current range.
            volt:           int/float, unit mV.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_drop_voltage(2, "30A", 2100)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert curr_range in psu004001_line_info[ps]["curr_range_sw"]
        assert isinstance(volt, (int, float))

        self.drop_voltage[ps][curr_range] = volt

        return "done"

    def set_gain(self, ps, gain):
        '''
        Set the PGA281 gain control, this is a debug function.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            gain:   int, [0 ~ 0b11111], max is 0x1f

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_gain(1, 0b10110)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert isinstance(gain, (int))

        self.set_line_path(ps, "pga_gain_0", str(gain >> 0 & 1))
        self.set_line_path(ps, "pga_gain_1", str(gain >> 1 & 1))
        self.set_line_path(ps, "pga_gain_2", str(gain >> 2 & 1))
        self.set_line_path(ps, "pga_gain_3", str(gain >> 3 & 1))
        self.set_line_path(ps, "pga_gain_4", str(gain >> 4 & 1))
        self.set_pga_gain[ps] = gain

        return "done"

    def protection_set(self, ps, curr_range, volt_ovp, volt_ocp):
        '''
        Protection set for PS1 or PS2, this is a debug function.
        Ovp, ocp do not require calibration.

        Args:
            ps:             int, [1, 2], 1:PS1; 2:PS2
            curr_range:     string, ["1A", "3A", "10A", "30A"], the current range.
            volt_ovp:       int, Vadc_ovp
            volt_ocp:       int, Vadc_ocp

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.protection_set(1, "1A", 5000, 1000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert curr_range in psu004001_line_info[ps]["curr_range_sw"]
        assert isinstance(volt_ovp, (int, float))
        assert isinstance(volt_ocp, (int, float))

        self.set_ad5675_voltage(ps, PSU004001Def.DAC_CHANNEL[ps][PSU004001Def.DAC_CHANNEL_OVP],
                                formula["Vovp2Vlimit"](volt_ovp))

        if ps == PSU004001Def.PS1:
            channels = [PSU004001Def.DAC_CHANNEL_OCP_P, PSU004001Def.DAC_CHANNEL_OCP_N]
        elif ps == PSU004001Def.PS2:
            channels = [PSU004001Def.DAC_CHANNEL_OCP]
        for channel in channels:
            self.set_ad5675_voltage(ps, PSU004001Def.DAC_CHANNEL[ps][channel],
                                    formula["Vocp2I" + curr_range + "_" + str(ps)](volt_ocp))
        self.dac_ovp_set_volt[ps] = volt_ovp
        self.dac_ocp_set_volt[ps][curr_range] = volt_ocp

        return "done"

    def slew_rate_enable(self, ps, state):
        '''
        Turn slew rate control on or off.

        Args:
            ps:     int, [1, 2], 1:PS1; 2:PS2
            state:  string, ["enable", "disable"], switch.

        Return:
            string, "done", api execution successful.

        Example:
            psu004001.slew_rate_enable(1, "enable")

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert state in PSU004001Def.SWITCH_SLEW_RATE_SELECT

        if state == PSU004001Def.SWITCH_SLEW_RATE_ON:
            self.set_spi_speed(PSU004001Def.AD5781_MIX_SPI_MAX_SPEED)
        else:
            self.output_enable(ps, 'disable')
            self.set_spi_speed(PSU004001Def.AD5781_MIX_SPI_DEFAULT_SPEED)
        self.sw_slew_rate[ps] = state

        return "done"

    def set_slew_rate(self, ps, types, slew_rate):
        '''
        By setting the ascending and descending slopes of DAC output to achieve
        a relatively smooth output, to control the establishment time of PSU,
        and to prevent overshoot.

        Args:
            ps:         int, [1, 2], 1:PS1; 2:PS2
            types:      string, ["V", "1A", "3A", "10A", "30A"], the slew rate of the voltage is only one.
                                                                 the slew rate of the current depends on the range.
            slew_rate:  int/float, the slew rate of volt or curr.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_slew_rate(1, "V", 1000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert types in PSU004001Def.SLEW_RATE_SCOPE[ps]
        assert isinstance(slew_rate, (int, float))
        assert slew_rate >= PSU004001Def.SLEW_RATE_SCOPE[ps][types][0]
        assert slew_rate <= PSU004001Def.SLEW_RATE_SCOPE[ps][types][1]

        if types == "V":
            # Vout2Vadc_1_diff
            self.slew_rate[ps][types] = slew_rate / formula_diff["Vout2Vadc_" + str(ps) + "_diff"]
        else:       # "1A", "3A", "10A", "30A"
            self.slew_rate[ps][types] = slew_rate / formula_diff["I" + types + "2Vdac_" + str(ps) + "_diff"]

        return "done"

    def set_spi_speed(self, freq):
        '''
        Set mix spi speed. It is not normally required, but only when the SPI rate
        is too high and the AD5781 output is abnormal.

        Args:
            freq:   uint32_t, [>0], spi speed, unit:Hz.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_spi_speed(1000000)

        '''
        assert isinstance(freq, int)
        assert 0 < freq <= PSU004001Def.AD5781_MIX_SPI_MAX_SPEED

        self.ad5781_lib.mix_spi_set_speed(self.mix_spi, ctypes.c_uint32(freq))

        return "done"

    def get_spi_speed(self):
        '''
        Get mix spi speed, this is a debug function.

        Args:

        Returns:
            uint32_t, spi speed.

        Example:
            result = psu004001.get_spi_speed()

        '''
        freq = ctypes.c_uint32()
        self.ad5781_lib.mix_spi_get_speed(self.mix_spi, ctypes.byref(freq))

        return freq.value

    def set_ad5675_voltage(self, ps, channel, volt):
        '''
        Set dac(ad5675) output voltage, this is a debug function.

        Args:
            ps:       int, [1, 2], 1:PS1; 2:PS2
            channel:  int, [0-7], dac channel
            volt:     float/int, unit mV.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_ad5675_voltage(1, 0, 2500)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert channel in range(7)
        assert isinstance(volt, (int, float))
        assert volt >= 0

        self.dac[ps].output_volt_dc(channel, volt)
        return "done"

    def _select_ad5781(self, ps, types, all_off=0):
        '''
        Select which piece of AD6781 to control by controlling the SYNC pin of AD5781.

        Args:
            ps:         int, [1, 2], 1:PS1; 2:PS2
            types:      string, ['VOLT', 'CURR'], the type of parameter.
            all_off:    int, [0, 1], 1 means select no one.
                                     The input shift register is updated at the rising edge of SYNC,
                                     so the SYNC pin must be pulled up after the data is written.

        Returns:
            string, "done", api execution successful.

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert types in PSU004001Def.OUTPUT_TYPES[ps]

        if all_off == 1:
            self.gpio_ps1_vdac_sync.set_level(1)
            self.gpio_ps1_idac_sync.set_level(1)
            self.gpio_ps2_vdac_sync.set_level(1)
            self.gpio_ps2_idac_sync.set_level(1)
            return "done"

        if ps == PSU004001Def.PS1:
            if types == PSU004001Def.OUTPUT_TYPE_VOLT:
                self.gpio_ps1_vdac_sync.set_level(0)
            else:
                self.gpio_ps1_idac_sync.set_level(0)
        else:
            if types == PSU004001Def.OUTPUT_TYPE_VOLT:
                self.gpio_ps2_vdac_sync.set_level(0)
            else:
                self.gpio_ps2_idac_sync.set_level(0)
        return "done"

    def set_ad5781_voltage(self, ps, types, curr_range, volt):
        '''
        Set dac(ad5781) output voltage, this is a debug function.

        Args:
            ps:             int, [1, 2], 1:PS1; 2:PS2
            types:          string, ['VOLT', 'CURR'], the type of parameter.
            curr_range:     string, ["1A", "3A", "10A, "30A"], the current range.
            volt:           float/int, unit mV.

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.set_ad5781_voltage(2, "VOLT", "10A", 5000)

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert types in PSU004001Def.OUTPUT_TYPES[ps]
        assert curr_range in psu004001_line_info[ps]["curr_range_sw"]
        assert isinstance(volt, (int, float))
        assert volt >= 0

        if self.sw_slew_rate[ps] == PSU004001Def.SWITCH_SLEW_RATE_ON:
            if PSU004001Def.OUTPUT_TYPE_VOLT == types:
                slew_rate_set = self.slew_rate[ps]["V"]
            else:
                slew_rate_set = self.slew_rate[ps][curr_range]

            self.ad5781_lib.ad5781_output_volt_dc(self.ad5781[ps][types], ctypes.c_float(volt),
                                                  ctypes.c_float(slew_rate_set))
        else:
            self.ad5781_lib.ad5781_output_volt_point(self.ad5781[ps][types], ctypes.c_float(volt))

        return "done"

    def _set_io(self, ps, io_list):
        '''
        Psu004001 set io, this is a private function.

        Args:
            ps:         int, [1, 2], 1:PS1; 2:PS2
            io_list:    list, format is [(bit, state),].

        Returns:
            string, "done", api execution successful.

        '''
        assert ps in PSU004001Def.PS_SELECT

        rd_data = self.io_exp[ps].get_ports()
        cp_state = rd_data[0] + (rd_data[1] << 8)

        for bit in io_list:
            cp_state &= ~(1 << (bit[0] & 0xf))
            if bit[1] == 1:
                cp_state |= (1 << (bit[0] & 0xf))
        self.io_exp[ps].set_ports([cp_state & 0xFF, (cp_state >> 8) & 0xFF])

        return "done"

    def _get_io(self, ps, bit):
        '''
        Psu004001 get the input io, this is a private function.

        Args:
            ps:         int, [1, 2], 1:PS1; 2:PS2
            bit:        int, [1-16], CAT9555 bit.

        Returns:
            int, the input io level.

        '''
        assert ps in PSU004001Def.PS_SELECT

        rd_data = self.io_exp[ps].get_ports()
        cp_state = rd_data[0] + (rd_data[1] << 8)

        return (cp_state >> (bit & 0xf)) & 1

    def set_line_path(self, ps, config, scope, delay_time_ms=0):
        '''
        psu004001 set line path, this is a private function.

        Args:
            ps:            int, [1, 2], 1:PS1; 2:PS2
            config:        string, ["dcdc_enable", "output_enable", "discharge_enable",
                           "dac_reset", "curr_range_sw", "dac_load"].
            scope:         string, ["run", "shutdown", "on", "off", "enable", "disable",
                           "high", "low", "1A", "10A", "high", "low"], the scope is rely on config, eg:
                           dcdc_enable:["run", "shutdown"], output_enable:["on", "off"],
                           discharge_enable:["enable", "disable"], dac_reset:["high", "low"],
                           curr_range_sw:["1A", "10A"], dac_load:["high", "low"].
            delay_time_ms: float/int, unit ms, default 0,  delay time of excitation output.

        Returns:
            string, "done", api execution successful.

        Examples:
            psu004001.set_line_path(1, 'dcdc_enable', 'run')

        '''
        assert ps in PSU004001Def.PS_SELECT
        assert config in psu004001_line_info[ps]
        assert scope in psu004001_line_info[ps][config]

        if config not in self.line_path[ps] or self.line_path[ps][config] != scope:
            self._set_io(ps, psu004001_line_info[ps][config][scope]["bits"])
            time.sleep(delay_time_ms / 1000.0)

            self.line_path[ps][config] = scope

        return "done"

    def get_driver_version(self):
        '''
        Get psu004001 driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def resp_select(self, speed):
        '''
        Select response speed.

        Args:
            speed:     string, ['fast', 'normal'], response speed

        Returns:
            string, "done", api execution successful.

        Example:
            psu004001.resp_select('normal')

        '''
        assert speed in PSU004001Def.RESPONSE_SPEED

        self.set_line_path(PSU004001Def.PS2, "resp_sel", speed)
        return "done"
