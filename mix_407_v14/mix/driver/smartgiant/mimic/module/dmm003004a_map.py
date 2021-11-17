# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.mimic.module.dmm003003_map import MimicBase
from mix.driver.smartgiant.mimic.module.dmm003004_map import DMM003004


__author__ = 'tufeng.mao@SmartGiant'
__version__ = 'V0.1.5'


class DMM003004ACoeffDef:
    # These coefficient obtained from DMM003004A Driver ERS
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
    RES_LOAD_1_40ohm = 0.025
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


dmm003004A_function_info = {
    # bits output state definition can be found from 'DMM003004A Driver ERS'
    'voltage': {
        '6mV': {
            'coefficient':
            1.0 / (DMM003004ACoeffDef.VOLT_2_REAL_GAIN1 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '6V': {
            'coefficient':
            1.0 / (DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '60V': {
            'coefficient':
            1.0 / (DMM003004ACoeffDef.VOLT_2_REAL_GAIN6 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 1),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 0)]
        },
        '600mV_AC': {
            'coefficient':
            1.0 / (DMM003004ACoeffDef.VOLT_2_REAL_GAIN4 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':
                    [(15, 1), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 1), (0, 1)]
        },
        '6V_AC': {
            'coefficient':
            1.0 / (DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
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
                DMM003004ACoeffDef.mA_2_nA / (
                    DMM003004ACoeffDef.RES_LOAD_2Mohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN2 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100nA': {
            'coefficient':
            1.0 * (
                DMM003004ACoeffDef.mA_2_nA / (
                    DMM003004ACoeffDef.RES_LOAD_2Mohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000nA': {
            'coefficient':
            1.0 * (
                DMM003004ACoeffDef.mA_2_nA / (
                    DMM003004ACoeffDef.RES_LOAD_2Kohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN1 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '10uA': {
            'coefficient':
            1.0 * (DMM003004ACoeffDef.mA_2_uA / (
                DMM003004ACoeffDef.RES_LOAD_2Kohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT
            )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100uA': {
            'coefficient':
            1.0 * (
                DMM003004ACoeffDef.mA_2_uA / (
                    DMM003004ACoeffDef.RES_LOAD_2Kohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 1), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000uA': {
            'coefficient':
            1.0 * (
                DMM003004ACoeffDef.mA_2_uA / (
                    DMM003004ACoeffDef.RES_LOAD_2ohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN1 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '10mA': {
            'coefficient':
            1.0 / (
                DMM003004ACoeffDef.RES_LOAD_2ohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '100mA': {
            'coefficient':
            1.0 / (
                DMM003004ACoeffDef.RES_LOAD_2ohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(9, 0), (15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 1), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 0), (3, 0), (2, 1), (1, 1), (0, 0), (9, 1)]
        },
        '1000mA': {
            'coefficient':
            1.0 / (
                DMM003004ACoeffDef.RES_LOAD_1_40ohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN2 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 1), (10, 0), (9, 0), (8, 0), (7, 0),
                     (6, 0), (5, 1), (4, 1), (3, 1), (2, 1), (1, 1), (0, 0)]
        },
        '5000mA': {
            'coefficient':
            1.0 / (
                DMM003004ACoeffDef.RES_LOAD_1_40ohm * DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
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
                DMM003004ACoeffDef.RES_GAIN_5 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN1 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 0), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100ohm': {
            'coefficient':
            1.0 / (
                DMM003004ACoeffDef.RES_GAIN_5 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 *
                DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 1), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_1Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_1 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_10Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_10 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100Kohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_100 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_1Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_1000 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x2002
                    [(15, 0), (14, 0), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_10Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_2000 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '4line_100Mohm': {
            'coefficient':
                1.0 / (
                    DMM003004ACoeffDef.RES_GAIN_1_20000 * DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 *
                    DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 0), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100ohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_5 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN3 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':   # 0x7c0a
                    [(15, 0), (14, 1), (13, 1), (12, 1), (11, 1), (10, 1), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_1Kohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_1 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_10Kohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_10 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 1), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100Kohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_100 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_1Mohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_1000 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 1), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]},
        '2line_10Mohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_2000 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 1), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        },
        '2line_100Mohm': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_20000 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':
                    [(15, 0), (14, 0), (13, 0), (12, 0), (11, 0), (10, 0), (9, 0), (8, 1), (7, 0),
                     (6, 1), (5, 0), (4, 0), (3, 0), (2, 1), (1, 0), (0, 1)]
        }
    },
    'diode': {
        'diode_5000mV': {
            'coefficient':
                1.0 / (DMM003004ACoeffDef.RES_GAIN_1_1 *
                       DMM003004ACoeffDef.VOLT_2_REAL_GAIN5 * DMM003004ACoeffDef.VOLT_2_REAL_UNIT),
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


dmm003004A_range_table = {
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
    '5000mA': 14,
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


class DMM003004ADef:
    CHANNEL_CURRENT = 'current'

    DEFAULT_TIMEOUT = 1  # s
    SAMPLING_RATE = 5
    RELAY_DELAY_MS = 5
    MIXDAQT1_REG_SIZE = 0x8000
    ADC_VREF_VOLTAGE_5000mV = 5000
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    CAT9555_DEV_ADDR = 0x20


class DMM003004AException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class DMM003004A(DMM003004, MimicBase):

    '''
    DMM003004A function class.

    compatible = ["GQQ-ML3Y-5-04A"]

    Args:
        i2c:           instance(I2C)/None,  instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        ipcore:        instance(MIXDAQT1SGR)/string/None, instance of MIXDAQT1SGR, which is used to control AD7175.

    Examples:
        vref = 5000
        i2c_bus = I2C('/dev/i2c-1')
        daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1_0', ad717x_chip='AD7175' ad717x_mvref=vref, use_spi=False, use_gpio=False)
        dmm003004A = DMM003004A(i2c_bus, daqt1)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-ML3Y-5-04A"]

    def __init__(self, i2c=None, ipcore=None):

        if isinstance(ipcore, basestring):
            daqt1_axi4_bus = AXI4LiteBus(ipcore, DMM003004ADef.MIXDAQT1_REG_SIZE)
            self.ip = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                  ad717x_mvref=DMM003004ADef.ADC_VREF_VOLTAGE_5000mV,
                                  use_spi=False, use_gpio=False)
            self.ad7175 = self.ip.ad717x
        else:
            self.ip = ipcore
            self.ad7175 = self.ip.ad717x

        super(DMM003004, self).__init__(i2c, ipcore, ad7175=None,
                                        eeprom_dev_addr=DMM003004ADef.EEPROM_DEV_ADDR,
                                        sensor_dev_addr=DMM003004ADef.SENSOR_DEV_ADDR,
                                        cat9555_dev_addr=DMM003004ADef.CAT9555_DEV_ADDR,
                                        range_table=dmm003004A_range_table)
        self.function_info = dmm003004A_function_info

    def post_power_on_init(self, timeout=DMM003004ADef.DEFAULT_TIMEOUT):
        '''
        Init Mimic module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=DMM003004ADef.DEFAULT_TIMEOUT):
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

    def set_measure_path(self, channel, scope, delay_time=DMM003004ADef.RELAY_DELAY_MS):
        '''
        DMM003004A set channel path. This is private function.

        Args:
            channel:     string, ['voltage', 'current', 'resistor', 'diode', 'cc_output'], note that cc_output
                                 should not be called by user.
            scope:       string, '6V', '6mV', '60V' for voltage,\
                                 '600mV_AC', '6V_AC' for AC voltage measure,\
                                 '10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',\
                                 '100mA', '1000mA', '5000mA' for current,\
                                 '4line_1ohm', '4line_100ohm', '4line_1Kohm',\
                                 '4line_10Kohm', '4line_100Kohm',\
                                 '4line_1Mohm', '4line_10Mohm', '4line_100Mohm',\
                                 '2line_100ohm', '2line_1Kohm', '2line_10Kohm',\
                                 '2line_100Kohm', '2line_1Mohm', '2line_10Mohm',\
                                 '2line_100Mohm' for resistor,\
                                 'diode_5000mV' for diode.\
                                 '50nA', '500nA', '1uA', '10uA', '100uA', '1mA', '5mA' for constant current.
            delay_time:  int, (>0), default 5, unit ms.

        Returns:
            string, "done", api execution successful.

        Examples:
            dmm003004A.set_measure_path('voltage', '6V')

        '''

        assert channel in self.function_info
        assert scope in self.function_info[channel]

        if channel not in self.measure_path or \
                scope != self.measure_path[channel]:
            bits = self.function_info[channel][scope]['bits']
            for bit in bits:
                self.cat9555.set_pin(bit[0], bit[1])

            time.sleep(delay_time / 1000.0)

            self.measure_path.clear()
            self.measure_path[channel] = scope

        return 'done'

    def current_measure(self, curr_range, sampling_rate=DMM003004ADef.SAMPLING_RATE,
                        delay_time=DMM003004ADef.RELAY_DELAY_MS):
        '''
        DMM003004A measure current once

        Args:
            curr_range:      string, ['10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',
                                      '100mA', '1000mA', '5000mA'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            current = dmm003004A.current_measure("100uA")
            print(current)

        '''

        if curr_range not in \
                dmm003004A_function_info[DMM003004ADef.CHANNEL_CURRENT]:
            raise DMM003004AException("error current scope")

        # Select measure range
        self.set_measure_path(DMM003004ADef.CHANNEL_CURRENT, curr_range, delay_time)

        return self._single_measure(DMM003004ADef.CHANNEL_CURRENT, sampling_rate)

    def multi_points_current_measure(self, count, curr_range,
                                     sampling_rate=DMM003004ADef.SAMPLING_RATE,
                                     delay_time=DMM003004ADef.RELAY_DELAY_MS):
        '''
        DMM003004A measure current in continuous mode

        Args:
            count:           int, [1~512], count of current data points.
            curr_range:      string, ['10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',
                                      '100mA', '1000mA', '5000mA'].
            sampling_rate:   float, [5~250000], unit Hz, default 5, Hzsampling rate.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            dmm003004A.multi_points_current_measure(10, "1000nA")

        '''
        if curr_range not in \
                dmm003004A_function_info[DMM003004ADef.CHANNEL_CURRENT]:
            raise DMM003004AException("error current scope")

        return self.multi_points_measure(count, DMM003004ADef.CHANNEL_CURRENT,
                                         curr_range, sampling_rate, delay_time)
