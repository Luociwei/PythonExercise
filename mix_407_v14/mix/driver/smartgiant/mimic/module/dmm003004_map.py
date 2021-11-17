# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.mimic.module.dmm003003_map import MimicBase

__author__ = 'yongjiu.tan@SmartGiant'
__version__ = 'V0.1.5'


class DMM003004CoeffDef:
    # These coefficient obtained from DMM003004 Driver ERS
    VOLT_2_REAL_UNIT = (8.2 / 10.2)
    VOLT_2_REAL_GAIN1 = 993.556
    VOLT_2_REAL_GAIN2 = 100.925
    VOLT_2_REAL_GAIN3 = 11.0
    VOLT_2_REAL_GAIN4 = 5.02
    VOLT_2_REAL_GAIN5 = 1.0
    VOLT_2_REAL_GAIN6 = (1.0 / 10.1)

    RES_LOAD_2Mohm = 2000000.0
    RES_LOAD_2Kohm = 2000.0
    RES_LOAD_2ohm = 2.0
    RES_LOAD_1_20ohm = 0.05
    # current source gain
    RES_GAIN_5 = 5.0
    RES_GAIN_1_1 = 1.0
    RES_GAIN_1_10 = 0.1
    RES_GAIN_1_100 = 0.01
    RES_GAIN_1_1000 = 0.001
    RES_GAIN_1_2000 = 0.0005
    RES_GAIN_1_20000 = 0.00005

    mV_2_V = 0.001
    mA_2_nA = 1000000.0
    mA_2_uA = 1000.0
    ohm_2_Kohm = 0.001
    ohm_2_Mohm = 0.000001


dmm003004_function_info = {
    # bits output state definition can be found from 'DMM003004 Driver ERS'
    'voltage': {
        '6mV': {
            'coefficient':
            1.0 / (DMM003004CoeffDef.VOLT_2_REAL_GAIN1 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '6V': {
            'coefficient':
            1.0 / (DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '60V': {
            'coefficient':
            1.0 / (DMM003004CoeffDef.VOLT_2_REAL_GAIN6 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 1),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 0)]
        },
        '600mV_AC': {
            'coefficient':
            1.0 / (DMM003004CoeffDef.VOLT_2_REAL_GAIN4 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 1), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 1), (0, 1)]
        },
        '6V_AC': {
            'coefficient':
            1.0 / (DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 1), (0, 1)]
        }
    },
    'current': {
        '10nA': {
            'coefficient':
            1.0 * (
                DMM003004CoeffDef.mA_2_nA / (
                    DMM003004CoeffDef.RES_LOAD_2Mohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN2 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100nA': {
            'coefficient':
            1.0 * (
                DMM003004CoeffDef.mA_2_nA / (
                    DMM003004CoeffDef.RES_LOAD_2Mohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN3 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000nA': {
            'coefficient':
            1.0 * (
                DMM003004CoeffDef.mA_2_nA / (
                    DMM003004CoeffDef.RES_LOAD_2Kohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN1 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '10uA': {
            'coefficient':
            1.0 * (DMM003004CoeffDef.mA_2_uA / (
                DMM003004CoeffDef.RES_LOAD_2Kohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT
            )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100uA': {
            'coefficient':
            1.0 * (
                DMM003004CoeffDef.mA_2_uA / (
                    DMM003004CoeffDef.RES_LOAD_2Kohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN3 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000uA': {
            'coefficient':
            1.0 * (
                DMM003004CoeffDef.mA_2_uA / (
                    DMM003004CoeffDef.RES_LOAD_2ohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN1 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '10mA': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_LOAD_2ohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100mA': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_LOAD_2ohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000mA': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_LOAD_1_20ohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 0)]
        },
        '3000mA': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_LOAD_1_20ohm * DMM003004CoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 0)]
        }
    },
    'resistor': {
        '4line_1ohm': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_GAIN_5 * DMM003004CoeffDef.VOLT_2_REAL_GAIN1 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 0), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100ohm': {
            'coefficient':
            1.0 / (
                DMM003004CoeffDef.RES_GAIN_5 * DMM003004CoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 1), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_1Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_1 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_10Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_10 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_100 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_1Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_1000 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x2002
                    [(15, 0), (14, 0), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_10Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_2000 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004CoeffDef.RES_GAIN_1_20000 * DMM003004CoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100ohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_5 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN3 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':   # 0x7c0a
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 1), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_1Kohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_1 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_10Kohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_10 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100Kohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_100 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_1Mohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_1000 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]},
        '2line_10Mohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_2000 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100Mohm': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_20000 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        }
    },
    'diode': {
        'diode_5000mV': {
            'coefficient':
                1.0 / (DMM003004CoeffDef.RES_GAIN_1_1 *
                       DMM003004CoeffDef.VOLT_2_REAL_GAIN5 * DMM003004CoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]

        }
    },
    'cc_output': {
        '50nA': {
            'bits':
                [(12, 0), (13, 0), (14, 0), (15, 0)]  # 0x0000
        },
        '500nA': {
            'bits':
                [(12, 0), (13, 0), (14, 1), (15, 0)]  # 0x4000
        },
        '1uA': {
            'bits':
                [(12, 0), (13, 1), (14, 0), (15, 0)]  # 0x2000
        },
        '10uA': {
            'bits':
                [(12, 0), (13, 1), (14, 1), (15, 0)]  # 0x6000
        },
        '100uA': {
            'bits':
                [(12, 1), (13, 0), (14, 0), (15, 0)]  # 0x1000
        },
        '1mA': {
            'bits':
                [(12, 1), (13, 0), (14, 1), (15, 0)]  # 0x5000
        },
        '5mA': {
            'bits':
                [(12, 1), (13, 1), (14, 1), (15, 0)]  # 0x7000
        }
    }
}


dmm003004_range_table = {
    '6mV': 0,
    '6V': 1,
    '60V': 2,
    '600mV_AC': 3,
    '6V_AC': 4,
    '10nA': 5,
    '100nA': 6,
    '1000nA': 7,
    '10uA': 8,
    '100uA': 9,
    '1000uA': 10,
    '10mA': 11,
    '100mA': 12,
    '1000mA': 13,
    '3000mA': 14,
    '4line_1ohm': 15,
    '4line_100ohm': 16,
    '4line_1Kohm': 17,
    '4line_10Kohm': 18,
    '4line_100Kohm': 19,
    '4line_1Mohm': 20,
    '4line_10Mohm': 21,
    '4line_100Mohm': 22,
    '2line_100ohm': 23,
    '2line_1Kohm': 24,
    '2line_10Kohm': 25,
    '2line_100Kohm': 26,
    '2line_1Mohm': 27,
    '2line_10Mohm': 28,
    '2line_100Mohm': 29,
    'diode_5000mV': 24
}


class DMM003004Def:
    CHANNEL_VOLTAGE = 'voltage'
    CHANNEL_DIODE = 'diode'

    DEFAULT_TIMEOUT = 1  # s
    AD7175_REG_SIZE = 256
    SAMPLING_RATE = 5
    RELAY_DELAY_MS = 5
    EMULATOR_REG_SIZE = 256
    MIXDAQT1_REG_SIZE = 0x8000
    ADC_VREF_VOLTAGE_5000mV = 5000
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    CAT9555_DEV_ADDR = 0x20


class DMM003004Exception(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class DMM003004(MimicBase):

    '''
    DMM003004 function class.

    compatible = ["GQQ-ML3Y-5-04B", "GQQ-ML3Y-5-040"]

    Args:
        i2c:           instance(I2C)/None,  instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        ipcore:        instance(MIXDAQT1SGR)/string/None, instance of MIX_DAQT1, which is used to control AD7175.
        ad7175:        instance(ADC)/None, Class instance of AD7175.

    Examples:
        # use non-aggregated IP
        vref = 5000
        i2c_bus = I2C('/dev/i2c-1')
        ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', vref)
        dmm003004 = DMM003004(i2c_bus, None, ad7175)

        # use MIXDAQT1SGR aggregated IP
        vref = 5000
        i2c_bus = I2C('/dev/i2c-1')
        daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1_0', ad717x_mvref=vref, use_spi=False, use_gpio=False)
        dmm003004 = DMM003004(i2c_bus, daqt1, None)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-ML3Y-5-04B", "GQQ-ML3Y-5-040"]

    def __init__(self, i2c=None, ipcore=None, ad7175=None):

        if ipcore:
            if isinstance(ipcore, basestring):
                daqt1_axi4_bus = AXI4LiteBus(ipcore, DMM003004Def.MIXDAQT1_REG_SIZE)
                self.ip = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                      ad717x_mvref=DMM003004Def.ADC_VREF_VOLTAGE_5000mV,
                                      use_spi=True, use_gpio=False)
                self.ad7175 = self.ip.ad717x
            else:
                self.ip = ipcore
                self.ad7175 = self.ip.ad717x
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, DMM003004Def.AD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4_bus, mvref=DMM003004Def.ADC_VREF_VOLTAGE_5000mV)
            else:
                self.ad7175 = ad7175
        else:
            raise DMM003004Exception("Invalid parameter, please check")

        super(DMM003004, self).__init__(i2c, ipcore, ad7175,
                                        DMM003004Def.EEPROM_DEV_ADDR,
                                        DMM003004Def.SENSOR_DEV_ADDR,
                                        DMM003004Def.CAT9555_DEV_ADDR,
                                        range_table=dmm003004_range_table)
        self.function_info = dmm003004_function_info

    def post_power_on_init(self, timeout=DMM003004Def.DEFAULT_TIMEOUT):
        '''
        Init Mimic module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=DMM003004Def.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        super(DMM003004, self).reset(timeout)

    def get_driver_version(self):
        '''
        Get Mimic driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def ac_voltage_measure(self, volt_range="6V_AC", sampling_rate=DMM003004Def.SAMPLING_RATE,
                           delay_time=DMM003004Def.RELAY_DELAY_MS):
        '''
        DMM003004 measure ac voltage once

        Args:
            volt_range:      string, ["600mV_AC", "6V_AC"], default "6V_AC".
            sampling_rate:   float, [5~250000], default 5, not continuous.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            rms_volt = dmm003004.ac_voltage_measure()
            print(rms_volt)

        Raise:
            DMM003004Exception:  error voltage scope.

        '''
        if volt_range not in \
                dmm003004_function_info[DMM003004Def.CHANNEL_VOLTAGE]:
            raise DMM003004Exception("error voltage scope")

        # Select measure range
        self.set_measure_path(DMM003004Def.CHANNEL_VOLTAGE, volt_range, delay_time)

        return self._single_measure(DMM003004Def.CHANNEL_VOLTAGE, sampling_rate)

    def diode_voltage_measure(self, diode_range,
                              sampling_rate=DMM003004Def.SAMPLING_RATE,
                              delay_time=DMM003004Def.RELAY_DELAY_MS):
        '''
        Mimic measure diode voltage

        Args:
            diode_range:     string, ['diode_5000mV'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            diode_voltage = dmm003004.diode_voltage_measure("diode_5000mV")
            print(diode_voltage)

        '''
        if diode_range not in \
                self.function_info[DMM003004Def.CHANNEL_DIODE]:
            raise DMM003004Exception('error diode voltage scope')

        self.set_measure_path(DMM003004Def.CHANNEL_DIODE, diode_range, delay_time)

        return self._single_measure(DMM003004Def.CHANNEL_DIODE, sampling_rate)

    def multi_points_diode_measure(self, count, diode_range,
                                   sampling_rate=DMM003004Def.SAMPLING_RATE,
                                   delay_time=DMM003004Def.RELAY_DELAY_MS):
        '''
        Mimic measure diode in continuous mode

        Args:
            count:           int, [1~512], count of resistor data points.
            diode_range:     string, ['diode_5000mV'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
             dmm003004.multi_points_diode_measure(10, "diode_5000mV")

        '''
        if diode_range not in \
                self.function_info[DMM003004Def.CHANNEL_DIODE]:
            raise DMM003004Exception('error diode voltage scope')

        return self.multi_points_measure(count, DMM003004Def.CHANNEL_DIODE,
                                         diode_range, sampling_rate, delay_time)
