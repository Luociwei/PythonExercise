# -*- coding: utf-8 -*-
import functools
import math
import time
import struct
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard, BoardArgCheckError

__author__ = 'jinkun.lin@SmartGiant'
__version__ = '0.1'


class MimicCoeffDef:
    # These coefficient obtained from Mimic Driver ERS
    VOLT_2_REAL_UNIT = (8.2 / 10.2)
    VOLT_2_REAL_GAIN1 = 1001.0
    VOLT_2_REAL_GAIN2 = 101.0
    VOLT_2_REAL_GAIN3 = 11.0
    VOLT_2_REAL_GAIN4 = 10.1
    RES_LOAD_2Mohm = 2000000.0
    RES_LOAD_2Kohm = 2000.0
    RES_LOAD_2ohm = 2.0
    RES_LOAD_1_20ohm = 0.05
    # current source gain
    RES_GAIN_5 = 5.0
    RES_GAIN_1_10 = 0.1
    RES_GAIN_1_100 = 0.01
    RES_GAIN_1_1000 = 0.001
    RES_GAIN_1_2000 = 0.0005
    RES_GAIN_1_20000 = 0.00005
    DIODE_VOLT_UNIT = (10.2 / 8.2)
    mV_2_V = 0.001
    mA_2_nA = 1000000.0
    mA_2_uA = 1000.0
    ohm_2_Kohm = 0.001
    ohm_2_Mohm = 0.000001

    CAL_DATA_LEN = 12
    WRITE_CAL_DATA_PACK_FORMAT = '2f4B'
    WRITE_CAL_DATA_UNPACK_FORMAT = '12B'

    READ_CAL_BYTE = 12
    READ_CAL_DATA_PACK_FORMAT = '12B'
    READ_CAL_DATA_UNPACK_FORMAT = '2f4B'


mimic_function_info = {
    # bits output state definition can be found from 'Mimic Driver ERS'
    'voltage': {
        '6mV': {
            'coefficient':
            1.0 / (MimicCoeffDef.VOLT_2_REAL_GAIN1 *
                   MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':  # 0x0402
                [(8, 0), (0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (9, 0), (10, 1), (11, 0)]
        },
        '6V': {
            'coefficient':
            1.0 / (MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':  # 0x0002
                [(8, 0), (0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (9, 0), (10, 0), (11, 0)]
        },
        '60V': {
            'coefficient':
            1.0 * (MimicCoeffDef.VOLT_2_REAL_GAIN4 / MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':  # 0x0001
                [(8, 0), (0, 1), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (9, 0), (10, 0), (11, 0)]
        },
        '6V_AC': {
            'coefficient':
            1.0 / (MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mV',
            'bits':  # 0x0004
                [(8, 0), (0, 0), (1, 0), (2, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (9, 0), (10, 0), (11, 0)]
        }
    },
    'current': {
        '10nA': {
            'coefficient':
            1.0 * (
                MimicCoeffDef.mA_2_nA / (
                    MimicCoeffDef.RES_LOAD_2Mohm * MimicCoeffDef.VOLT_2_REAL_GAIN2 *
                    MimicCoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':  # 0x0a83
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 1),
                    (8, 0), (10, 0), (11, 1), (9, 1)]
        },
        '100nA': {
            'coefficient':
            1.0 * (
                MimicCoeffDef.mA_2_nA / (
                    MimicCoeffDef.RES_LOAD_2Mohm * MimicCoeffDef.VOLT_2_REAL_GAIN3 *
                    MimicCoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':  # 0x0e83
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 1),
                    (8, 0), (10, 1), (11, 1), (9, 1)]
        },
        '1000nA': {
            'coefficient':
            1.0 * (
                MimicCoeffDef.mA_2_nA / (
                    MimicCoeffDef.RES_LOAD_2Kohm * MimicCoeffDef.VOLT_2_REAL_GAIN1 *
                    MimicCoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'nA',
            'bits':  # 0x0643
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 0),
                    (8, 0), (10, 1), (11, 0), (9, 1)]
        },
        '10uA': {
            'coefficient':
            1.0 * (MimicCoeffDef.mA_2_uA / (
                MimicCoeffDef.RES_LOAD_2Kohm * MimicCoeffDef.VOLT_2_REAL_GAIN2 *
                MimicCoeffDef.VOLT_2_REAL_UNIT
            )),
            'unit': 'uA',
            'bits':  # 0x0a43
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 0),
                    (8, 0), (10, 0), (11, 1), (9, 1)]
        },
        '100uA': {
            'coefficient':
            1.0 * (
                MimicCoeffDef.mA_2_uA / (
                    MimicCoeffDef.RES_LOAD_2Kohm * MimicCoeffDef.VOLT_2_REAL_GAIN3 *
                    MimicCoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':  # 0x0e43
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 0),
                    (8, 0), (10, 1), (11, 1), (9, 1)]
        },
        '1000uA': {
            'coefficient':
            1.0 * (
                MimicCoeffDef.mA_2_uA / (
                    MimicCoeffDef.RES_LOAD_2ohm * MimicCoeffDef.VOLT_2_REAL_GAIN1 *
                    MimicCoeffDef.VOLT_2_REAL_UNIT
                )),
            'unit': 'uA',
            'bits':  # 0x0623
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 1), (6, 0), (7, 0),
                    (8, 0), (10, 1), (11, 0), (9, 1)]
        },
        '10mA': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_LOAD_2ohm * MimicCoeffDef.VOLT_2_REAL_GAIN2 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':  # 0x0a23
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 1), (6, 0), (7, 0),
                    (8, 0), (10, 0), (11, 1), (9, 1)]
        },
        '100mA': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_LOAD_2ohm * MimicCoeffDef.VOLT_2_REAL_GAIN3 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':  # 0x0e23
                [(9, 0), (0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 1), (6, 0), (7, 0),
                    (8, 0), (10, 1), (11, 1), (9, 1)]
        },
        '1000mA': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_LOAD_1_20ohm * MimicCoeffDef.VOLT_2_REAL_GAIN2 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':  # 0x0903
                [(0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 1), (9, 0), (10, 0), (11, 1)]
        },
        '3000mA': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_LOAD_1_20ohm * MimicCoeffDef.VOLT_2_REAL_GAIN3 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'mA',
            'bits':  # 0x0d03
                [(0, 1), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 1), (9, 0), (10, 1), (11, 1)]
        }
    },
    'resistor': {
        '4line_1ohm': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_GAIN_5 * MimicCoeffDef.VOLT_2_REAL_GAIN1 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x7402
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 1), (11, 0), (12, 1), (13, 1), (14, 1), (15, 0)]
        },
        '4line_100ohm': {
            'coefficient':
            1.0 / (
                MimicCoeffDef.RES_GAIN_5 * MimicCoeffDef.VOLT_2_REAL_GAIN3 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x7c02
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 0)]
        },
        '4line_1Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x5002
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 0), (11, 0), (12, 1), (13, 0), (14, 1), (15, 0)]
        },
        '4line_10Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_10 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x1002
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 0), (11, 0), (12, 1), (13, 0), (14, 0), (15, 0)]
        },
        '4line_100Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_100 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x6002
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 1), (14, 1), (15, 0)]
        },
        '4line_1Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_1000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x2002
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 1), (14, 0), (15, 0)]
        },
        '4line_10Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_2000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x4002
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 1), (15, 0)]
        },
        '4line_100Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_20000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x0202
                [(0, 0), (1, 1), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 1), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0)]
        },
        '2line_100ohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_5 *
                       MimicCoeffDef.VOLT_2_REAL_GAIN3 * MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':   # 0x7c0a
                [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                    (8, 0), (9, 0), (10, 1), (11, 1), (12, 1), (13, 1), (14, 1), (15, 0)]
        },
        '2line_1Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x500a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 1), (13, 0), (14, 1), (15, 0)]
        },
        '2line_10Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_10 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x100a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 1), (13, 0), (14, 0), (15, 0)]
        },
        '2line_100Kohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_100 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x600a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 1), (14, 1), (15, 0)]
        },
        '2line_1Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_1000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x200a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 1), (14, 0), (15, 0)]
        },
        '2line_10Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_2000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x400a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 1), (15, 0)]
        },
        '2line_100Mohm': {
            'coefficient':
                1.0 / (MimicCoeffDef.RES_GAIN_1_20000 *
                       MimicCoeffDef.VOLT_2_REAL_UNIT),
            'unit': 'ohm',
            'bits':  # 0x000a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0)]
        }
    },
    'diode': {
        'mV': {
            'coefficient': 1.0 * MimicCoeffDef.DIODE_VOLT_UNIT,
            'unit': 'mV',
            'bits':  # 0x520a
                    [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0),
                        (8, 0), (9, 1), (10, 0), (11, 0), (12, 1), (13, 0), (14, 1), (15, 0)]
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


mimic_calibration_info = {
    '6mV': {
        'level1': {'unit_index': 26, 'limit': (-1, 'mV')},
        'level2': {'unit_index': 27, 'limit': (-0.6, 'mV')},
        'level3': {'unit_index': 28, 'limit': (0, 'mV')},
        'level4': {'unit_index': 29, 'limit': (0.6, 'mV')},
        'level5': {'unit_index': 30, 'limit': (1, 'mV')},
        'level6': {'unit_index': 31, 'limit': (7, 'mV')}
    },
    '6V': {
        'level1': {'unit_index': 32, 'limit': (-1000, 'mV')},
        'level2': {'unit_index': 33, 'limit': (-600, 'mV')},
        'level3': {'unit_index': 34, 'limit': (-100, 'mV')},
        'level4': {'unit_index': 35, 'limit': (-60, 'mV')},
        'level5': {'unit_index': 36, 'limit': (-10, 'mV')},
        'level6': {'unit_index': 37, 'limit': (-6, 'mV')},
        'level7': {'unit_index': 38, 'limit': (0, 'mV')},
        'level8': {'unit_index': 39, 'limit': (6, 'mV')},
        'level9': {'unit_index': 40, 'limit': (10, 'mV')},
        'level10': {'unit_index': 41, 'limit': (60, 'mV')},
        'level11': {'unit_index': 42, 'limit': (100, 'mV')},
        'level12': {'unit_index': 43, 'limit': (600, 'mV')},
        'level13': {'unit_index': 44, 'limit': (1000, 'mV')},
        'level14': {'unit_index': 45, 'limit': (7000, 'mV')}
    },
    '60V': {
        'level1': {'unit_index': 46, 'limit': (-26000, 'mV')},
        'level2': {'unit_index': 47, 'limit': (-20000, 'mV')},
        'level3': {'unit_index': 48, 'limit': (-16000, 'mV')},
        'level4': {'unit_index': 49, 'limit': (-10000, 'mV')},
        'level5': {'unit_index': 50, 'limit': (-6000, 'mV')},
        'level6': {'unit_index': 51, 'limit': (0, 'mV')},
        'level7': {'unit_index': 52, 'limit': (6000, 'mV')},
        'level8': {'unit_index': 53, 'limit': (10000, 'mV')},
        'level9': {'unit_index': 54, 'limit': (16000, 'mV')},
        'level10': {'unit_index': 55, 'limit': (20000, 'mV')},
        'level11': {'unit_index': 56, 'limit': (26000, 'mV')},
        'level12': {'unit_index': 57, 'limit': (65000, 'mV')}

    },
    '6V_AC': {
        'level1': {'unit_index': 110, 'limit': (15, 'mV')},
        'level2': {'unit_index': 111, 'limit': (75, 'mV')},
        'level3': {'unit_index': 112, 'limit': (150, 'mV')},
        'level4': {'unit_index': 113, 'limit': (650, 'mV')},
        'level5': {'unit_index': 114, 'limit': (1010, 'mV')},
        'level6': {'unit_index': 115, 'limit': (7000, 'mV')}
    },
    '10nA': {
        'level1': {'unit_index': 67, 'limit': (0, 'nA')},
        'level2': {'unit_index': 68, 'limit': (30, 'nA')}
    },
    '100nA': {
        'level1': {'unit_index': 69, 'limit': (0, 'nA')},
        'level2': {'unit_index': 70, 'limit': (300, 'nA')}
    },
    '1000nA': {
        'level1': {'unit_index': 71, 'limit': (0, 'nA')},
        'level2': {'unit_index': 72, 'limit': (3000, 'nA')}
    },
    '10uA': {
        'level1': {'unit_index': 73, 'limit': (0, 'uA')},
        'level2': {'unit_index': 74, 'limit': (30, 'uA')}
    },
    '100uA': {
        'level1': {'unit_index': 75, 'limit': (0, 'uA')},
        'level2': {'unit_index': 76, 'limit': (300, 'uA')}
    },
    '1000uA': {
        'level1': {'unit_index': 77, 'limit': (0, 'uA')},
        'level2': {'unit_index': 78, 'limit': (3000, 'uA')}
    },
    '10mA': {
        'level1': {'unit_index': 79, 'limit': (0, 'mA')},
        'level2': {'unit_index': 80, 'limit': (30, 'mA')}
    },
    '100mA': {
        'level1': {'unit_index': 81, 'limit': (0, 'mA')},
        'level2': {'unit_index': 82, 'limit': (300, 'mA')}
    },
    '1000mA': {
        'level1': {'unit_index': 83, 'limit': (-500, 'mA')},
        'level2': {'unit_index': 84, 'limit': (0, 'mA')},
        'level3': {'unit_index': 85, 'limit': (500, 'mA')},
        'level4': {'unit_index': 86, 'limit': (1200, 'mA')}
    },
    '3000mA': {
        'level1': {'unit_index': 87, 'limit': (-2000, 'mA')},
        'level2': {'unit_index': 88, 'limit': (-1000, 'mA')},
        'level3': {'unit_index': 89, 'limit': (0, 'mA')},
        'level4': {'unit_index': 90, 'limit': (1000, 'mA')},
        'level5': {'unit_index': 91, 'limit': (2000, 'mA')},
        'level6': {'unit_index': 92, 'limit': (5000, 'mA')}

    },
    '4line_1ohm': {
        'level1': {'unit_index': 1, 'limit': (0.012, 'ohm')},
        'level2': {'unit_index': 2, 'limit': (0.12, 'ohm')},
        'level3': {'unit_index': 5, 'limit': (1.24533, 'ohm')}
    },
    '4line_100ohm': {
        'level1': {'unit_index': 3, 'limit': (113, 'ohm')}
    },
    '4line_1Kohm': {
        'level1': {'unit_index': 4, 'limit': (6226, 'ohm')}
    },
    '4line_10Kohm': {
        'level1': {'unit_index': 100, 'limit': (62260, 'ohm')}
    },
    '4line_100Kohm': {
        'level1': {'unit_index': 101, 'limit': (622600, 'ohm')}
    },
    '4line_1Mohm': {
        'level1': {'unit_index': 102, 'limit': (1245330, 'ohm')}
    },
    '4line_10Mohm': {
        'level1': {'unit_index': 103, 'limit': (12453300, 'ohm')}
    },
    '4line_100Mohm': {
        'level1': {'unit_index': 104, 'limit': (124533000, 'ohm')}
    },
    '2line_100ohm': {
        'level1': {'unit_index': 7, 'limit': (15, 'ohm')},
        'level2': {'unit_index': 8, 'limit': (133, 'ohm')}
    },
    '2line_1Kohm': {
        'level1': {'unit_index': 9, 'limit': (90, 'ohm')},
        'level2': {'unit_index': 10, 'limit': (520, 'ohm')},
        'level3': {'unit_index': 11, 'limit': (6226, 'ohm')}
    },
    '2line_10Kohm': {
        'level1': {'unit_index': 12, 'limit': (900, 'ohm')},
        'level2': {'unit_index': 13, 'limit': (62260, 'ohm')}
    },
    '2line_100Kohm': {
        'level1': {'unit_index': 14, 'limit': (9000, 'ohm')},
        'level2': {'unit_index': 15, 'limit': (52000, 'ohm')},
        'level3': {'unit_index': 16, 'limit': (622600, 'ohm')}
    },
    '2line_1Mohm': {
        'level1': {'unit_index': 17, 'limit': (90000, 'ohm')},
        'level2': {'unit_index': 18, 'limit': (520000, 'ohm')},
        'level3': {'unit_index': 19, 'limit': (1245330, 'ohm')}
    },
    '2line_10Mohm': {
        'level1': {'unit_index': 20, 'limit': (900000, 'ohm')},
        'level2': {'unit_index': 21, 'limit': (12453300, 'ohm')}
    },
    '2line_100Mohm': {
        'level1': {'unit_index': 22, 'limit': (9000000, 'ohm')},
        'level2': {'unit_index': 23, 'limit': (52000000, 'ohm')},
        'level3': {'unit_index': 24, 'limit': (124533000, 'ohm')}
    }

}

mimic_range_table = {
    '6mV': 0,
    '6V': 1,
    '60V': 2,
    '6V_AC': 3,
    '10nA': 4,
    '100nA': 5,
    '1000nA': 6,
    '10uA': 7,
    '100uA': 8,
    '1000uA': 9,
    '10mA': 10,
    '100mA': 11,
    '1000mA': 12,
    '3000mA': 13,
    '4line_1ohm': 14,
    '4line_100ohm': 15,
    '4line_1Kohm': 16,
    '4line_10Kohm': 17,
    '4line_100Kohm': 18,
    '4line_1Mohm': 19,
    '4line_10Mohm': 20,
    '4line_100Mohm': 21,
    '2line_100ohm': 22,
    '2line_1Kohm': 23,
    '2line_10Kohm': 24,
    '2line_100Kohm': 25,
    '2line_1Mohm': 26,
    '2line_10Mohm': 27,
    '2line_100Mohm': 28
}


class MimicDef:
    CHANNEL_VOLTAGE = 'voltage'
    CHANNEL_CURRENT = 'current'
    CHANNEL_RESISTOR = 'resistor'
    CHANNEL_DIODE = 'diode'
    CHANNEL_CC = 'cc_output'

    CHANNEL_CAL_PATH = ('current', 'voltage', 'resistor')

    SWITCH_DELAY_S = 0.001
    RELAY_DELAY_MS = 5
    SAMPLING_RATE = 5
    DEFAULT_CHAN = 'voltage'
    DEFAULT_RANGE = '60V'
    ADC_VREF_VOLTAGE_5000mV = 5000
    EMULATOR_REG_SIZE = 256
    MIXDAQT1_REG_SIZE = 0x8000
    ADC_60VOLTAGE_CHANNEL = 0
    ADC_VOLTAGE_CHANNEL = 1
    ADC_CHANNEL_LIST = (0, 1)

    EEPROM_DEV_ADDR = 0x52
    SENSOR_DEV_ADDR = 0x4A
    CAT9555_DEV_ADDR = 0x20


class MimicException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Mimic(MIXBoard):

    '''
    Mimic function class

    compatible = ["GQQ-DMM003003-000"]

    Args:
        i2c:        instance(I2C)/None,  instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        ipcore:     instance(MIXDAQT1)/string/None,  instance of MIX_DAQT1, which is used to control AD7175.
        ad7175:     instance(ADC)/None,  Class instance of AD7175.

    Examples:
        # use non-aggregated IP
        vref = 5000
        i2c_bus = I2C('/dev/i2c-1')
        ad7175 = PLAD7175('/dev/MIX_AD717X_0', vref)
        mimic = Mimic(i2c_bus, None, ad7175)

        # use MIXDAQT1 aggregated IP
        vref = 5000
        i2c_bus = I2C('/dev/i2c-1')
        daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_mvref=vref, use_spi=False, use_gpio=False)
        mimic = Mimic(i2c_bus, daqt1, None)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-DMM003003-000"]

    rpc_public_api = ['module_init', 'get_sampling_rate', 'set_measure_path', 'get_measure_path', 'dc_voltage_measure',
                      'ac_voltage_measure', 'current_measure', 'resistor_measure', 'diode_voltage_measure',
                      'continuous_sample', 'multi_points_measure', 'multi_points_voltage_measure',
                      'multi_points_current_measure', 'multi_points_resistor_measure',
                      'multi_points_diode_measure'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, ipcore=None, ad7175=None):

        if i2c:
            self.eeprom = CAT24C32(MimicDef.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(MimicDef.SENSOR_DEV_ADDR, i2c)
            self.cat9555 = CAT9555(MimicDef.CAT9555_DEV_ADDR, i2c)
        else:
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.sensor = NCT75Emulator('nct75_emulator')
            self.cat9555 = CAT9555Emulator(
                MimicDef.CAT9555_DEV_ADDR, None, None)

        if ipcore:
            if isinstance(ipcore, basestring):
                daqt1_axi4_bus = AXI4LiteBus(ipcore, MimicDef.MIXDAQT1_REG_SIZE)
                self.ip = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                      ad717x_mvref=MimicDef.ADC_VREF_VOLTAGE_5000mV,
                                      use_spi=True, use_gpio=False)
                self.ad7175 = self.ip.ad717x
            else:
                self.ip = ipcore
                self.ad7175 = self.ip.ad717x
        elif ad7175:
            self.ad7175 = ad7175
        else:
            self.ad7175 = MIXAd7175SGEmulator(
                'mix_ad7175_sg_emulator', MimicDef.EMULATOR_REG_SIZE)

        self.ad7175.config = {
            'ch0': {'P': 'AIN0', 'N': 'AIN1'},
            'ch1': {'P': 'AIN2', 'N': 'AIN3'}
        }
        self.measure_path = dict()

        super(Mimic, self).__init__(self.eeprom, self.sensor, cal_table=mimic_calibration_info,
                                    range_table=mimic_range_table)

        self.function_info = mimic_function_info
        self.module_calibration_info = mimic_calibration_info

    def module_init(self):
        '''
        Mimic module initialization

        This is to handle the case when gpio pin used for sample-rate
        is behind an I2C mux, and when module instance is created the
        I2C mux is not configured so i2c to module is not working.
        User software need to switch i2c mux if there is, and call this function once
        Before using the module.

        Returns:
            string, "done", api execution successful.

        Examples:
            mimic.module_init()

        '''
        self.load_calibration()
        self.cat9555.set_pins_dir([0x00, 0x00])
        self.ad7175.channel_init()
        self.set_measure_path(MimicDef.DEFAULT_CHAN, MimicDef.DEFAULT_RANGE)
        self.set_sampling_rate(0, MimicDef.SAMPLING_RATE)
        self.set_sampling_rate(1, MimicDef.SAMPLING_RATE)

        return 'done'

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Mimic set sampling rate. This is private function.

        Args:
            channel:           int, [0, 1], 0 for 60V channel, 1 for others channel.
            sampling_rate:     float, [5~250000], adc measure sampling rate, which not continuouse,
                                                  please refer ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
           mimic.set_sampling_rate(1, 10000)

        '''
        assert channel in MimicDef.ADC_CHANNEL_LIST
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(channel, sampling_rate)

    def get_sampling_rate(self, channel):
        '''
        Mimic get sampling rate of adc

        Args:
            channel:     int, [0, 1], 0 for 60V channel, 1 for others channel.

        Returns:
            string, "done", api execution successful.

        Examples:
            sampling_rate = mimic.get_sampling_rate(1)
            print(sampling_rate)

        '''
        assert channel in MimicDef.ADC_CHANNEL_LIST

        return self.ad7175.get_sampling_rate(channel)

    def _volt_to_target_unit(self, channel, scope, volt):
        '''
        Mimic get target unit value (mimic_function_info) from measured voltage

        Args:
            channel:    string, ['voltage', 'current', 'resistor', 'diode'].
            scope:      string, the range of channel measure.
            volt:       float, the measured voltage by ad7175.

        Returns:
            float, value.

        '''
        assert channel in self.function_info
        assert scope in self.function_info[channel]

        return volt * self.function_info[channel][scope]['coefficient']

    def set_measure_path(self, channel, scope, delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic set channel path. This is private function.

        Args:
            channel:     string, ['voltage', 'current', 'resistor', 'diode', 'cc_output'], note that cc_output
                                 should not be called by user.
            scope:       string, '6V', '6mV', '60V' for voltage,\
                                 '6V_AC' for AC voltage measure,\
                                 '10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',\
                                 '100mA', '1000mA', '3000mA' for current,\
                                 '4line_1ohm', '4line_100ohm', '4line_1Kohm',\
                                 '4line_10Kohm', '4line_100Kohm',\
                                 '4line_1Mohm', '4line_10Mohm', '4line_100Mohm',\
                                 '2line_100ohm', '2line_1Kohm', '2line_10Kohm',\
                                 '2line_100Kohm', '2line_1Mohm', '2line_10Mohm',\
                                 '2line_100Mohm' for resistor,\
                                 'mV' for diode.\
                                 '50nA', '500nA', '1uA', '10uA', '100uA', '1mA', '5mA' for constant current.
            delay_time:  int, (>0), default 5, unit ms.

        Returns:
            string, "done", api execution successful.

        Examples:
            mimic.set_measure_path('voltage', '6V')

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

    def get_measure_path(self):
        '''
        Mimic get measure path.

        Returns:
            dict, {key, value}, the key is channel, value is scope.

        Examples:
            path = mimic.get_measure_path()
            print(path)

        '''
        return self.measure_path

    def _single_measure(self, channel, sampling_rate):
        '''
        Mimic measure voltage once

        Args:
            channel:           string,  ['voltage', 'current', 'resistor', 'diode'].
            sampling_rate:     float, [5~250000], adc measure sampling rate, which not continuouse,
                                                  please refer ad7175 datasheet.

        Returns:
            list, [value, unit].

        Examples:
            target = mimic._single_measure('voltage', 1000)

        '''
        measure_path = self.get_measure_path()
        if channel not in measure_path or channel == MimicDef.CHANNEL_CC:
            raise MimicException('error voltage channel')
        if measure_path[channel] not in \
                self.function_info[channel]:
            raise MimicException('error voltage scope')

        adc_channel = MimicDef.ADC_60VOLTAGE_CHANNEL if \
            measure_path[channel] == '60V' else \
            MimicDef.ADC_VOLTAGE_CHANNEL

        # Set sampling rate
        self.set_sampling_rate(adc_channel, sampling_rate)

        voltage = self.ad7175.read_volt(adc_channel)
        target_value = self._volt_to_target_unit(
            channel, measure_path[channel], voltage)
        unit = self.function_info[channel][measure_path[channel]]['unit']

        if measure_path[channel] in self.module_calibration_info:
            target_value = self.calibrate(measure_path[channel], target_value)

        return [target_value, unit]

    def dc_voltage_measure(self, volt_range,
                           sampling_rate=MimicDef.SAMPLING_RATE,
                           delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure voltage once

        Args:
            volt_range:      string, ['6V', '6mV', '60V'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            volt = mimic.dc_voltage_measure('6V', 1000)
            print(volt)

        '''

        if volt_range not in self.function_info[MimicDef.CHANNEL_VOLTAGE]:
            raise MimicException("error voltage scope")

        # Select measure range
        self.set_measure_path(MimicDef.CHANNEL_VOLTAGE, volt_range, delay_time)

        return self._single_measure(MimicDef.CHANNEL_VOLTAGE, sampling_rate)

    def ac_voltage_measure(self, sampling_rate=MimicDef.SAMPLING_RATE, delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure ac voltage once

        Args:
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            rms_volt = mimic.ac_voltage_measure(1000)
            print(rms_volt)

        '''

        # Select measure range
        self.set_measure_path(MimicDef.CHANNEL_VOLTAGE, "6V_AC", delay_time)

        return self._single_measure(MimicDef.CHANNEL_VOLTAGE, sampling_rate)

    def current_measure(self, curr_range,
                        sampling_rate=MimicDef.SAMPLING_RATE,
                        delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure current once

        Args:
            curr_range:      string, ['10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',
                                      '100mA', '1000mA', '3000mA'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            current = mimic.current_measure("100uA")
            print(current)

        '''

        if curr_range not in \
                self.function_info[MimicDef.CHANNEL_CURRENT]:
            raise MimicException("error current scope")

        # Select measure range
        self.set_measure_path(MimicDef.CHANNEL_CURRENT, curr_range, delay_time)

        return self._single_measure(MimicDef.CHANNEL_CURRENT, sampling_rate)

    def resistor_measure(self, res_range,
                         sampling_rate=MimicDef.SAMPLING_RATE,
                         delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure resistor

        Args:
            res_range:       string, ['4line_1ohm', '4line_100ohm', '4line_1Kohm',
                                      '4line_10Kohm', '4line_100Kohm', '4line_1Mohm',
                                      '4line_10Mohm', '4line_100Mohm', '2line_100ohm',
                                      '2line_1Kohm', '2line_10Kohm', '2line_100Kohm',
                                      '2line_1Mohm', '2line_10Mohm', '2line_100Mohm'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            resistor = mimic.resistor_measure("2line_10Mohm")
            print(resistor)

        '''

        if res_range not in \
                self.function_info[MimicDef.CHANNEL_RESISTOR]:
            raise MimicException('error resistor scope')

        # Select measure range
        self.set_measure_path(MimicDef.CHANNEL_RESISTOR, res_range, delay_time)
        result = self._single_measure(MimicDef.CHANNEL_RESISTOR, sampling_rate)
        if result[0] < 0:
            raise MimicException('2-wire and 4-wire short circuit or 4-wire open circuit')

        return result

    def diode_voltage_measure(self, diode_range,
                              sampling_rate=MimicDef.SAMPLING_RATE,
                              delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure diode voltage

        Args:
            diode_range:     string, ['mV'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            list, [value, unit].

        Examples:
            diode_voltage = mimic.diode_voltage_measure("mV")
            print(diode_voltage)

        '''

        if diode_range not in \
                self.function_info[MimicDef.CHANNEL_DIODE]:
            raise MimicException('error diode voltage scope')

        # Select measure range
        self.set_measure_path(MimicDef.CHANNEL_DIODE, diode_range, delay_time)

        return self._single_measure(MimicDef.CHANNEL_DIODE, sampling_rate)

    def continuous_sample(self, count, sampling_rate):
        '''
        Mimic get measure data in continuous mode and return list of data without any calculation;

        station sw could do further analysis base on raw data returned. This is private function.

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points
                                           to get in continuous mode; from FPGA internal buffer not from DMA.
            sampling_rate:   float, [5~250000], unit Hz, default 5.

        Returns:
            list, [[value,value,...], unit].

        Examples:
            mimic.set_measure_path('voltage', '6V')
            result = mimic.continuous_sample(10, 1000)
            print(result)

        '''
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()

        if measure_path == {} or measure_path.keys()[0] == MimicDef.CHANNEL_CC:
            raise MimicException('error continuous measure channel')

        measure_channel = measure_path.keys()[0]
        measure_scope = measure_path.values()[0]

        adc_channel = MimicDef.ADC_60VOLTAGE_CHANNEL if measure_scope == '60V' else MimicDef.ADC_VOLTAGE_CHANNEL

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(MimicDef.SWITCH_DELAY_S)

        self.ad7175.enable_continuous_sampling(adc_channel, sampling_rate)

        unit = self.function_info[measure_channel][measure_scope]['unit']
        target_data = []
        try:
            adc_volt = self.ad7175.get_continuous_sampling_voltage(adc_channel, count)
        except Exception:
            raise
        else:
            if measure_scope in self.module_calibration_info:
                calibrate = functools.partial(self.calibrate, measure_scope)
                adc_volt = map(calibrate, adc_volt)

            volt_to_target_unit = functools.partial(self._volt_to_target_unit, measure_channel, measure_scope)
            target_data = [map(volt_to_target_unit, adc_volt), unit]

        finally:
            self.ad7175.disable_continuous_sampling(adc_channel)

        return target_data

    def multi_points_measure(self, count, channel, scope,
                             sampling_rate=MimicDef.SAMPLING_RATE,
                             delay_time=MimicDef.RELAY_DELAY_MS):
        '''
        Mimic measure voltage/current/resistor in continuous mode. This is private function.

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points.
            channel:         string, Get count voltage/current/resistor in continuous mode.
            scope:           string, channel scope.
            sampling_rate:   float, [5~250000], unit Hz, default 5, sampling rate.
            delay_time:      int, (>0), default 5, unit ms.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            result = mimic.multi_points_measure(10, "current", "100uA")
            print(result)

        '''

        # Select measure range
        self.set_measure_path(channel, scope, delay_time)

        target_data = self.continuous_sample(count, sampling_rate)
        min_data = min(target_data[0])
        max_data = max(target_data[0])
        sum_Data = sum(target_data[0])
        avg_data = sum_Data / len(target_data[0])
        square_sum_data = sum([x**2 for x in target_data[0]])
        rms_data = math.sqrt(square_sum_data / len(target_data[0]))

        unit = target_data[1]
        result = dict()
        result['rms'] = (rms_data, unit + 'rms')
        result['avg'] = (avg_data, unit)
        result['max'] = (max_data, unit)
        result['min'] = (min_data, unit)

        return result

    def multi_points_voltage_measure(self, count, volt_range,
                                     sampling_rate=MimicDef.SAMPLING_RATE):
        '''
        Mimic measure voltage in continuous mode

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points.
            volt_range:      string, ['6V', '6mV', '60V', '6V_AC'].
            sampling_rate:   float, [5~250000], unit Hz, default 5, Hzsampling rate.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
             mimic.multi_points_voltage_measure(10, "60V")

        '''
        if volt_range not in self.function_info[MimicDef.CHANNEL_VOLTAGE]:
            raise MimicException("error voltage scope")

        return self.multi_points_measure(count, MimicDef.CHANNEL_VOLTAGE,
                                         volt_range, sampling_rate)

    def multi_points_current_measure(self, count, curr_range,
                                     sampling_rate=MimicDef.SAMPLING_RATE):
        '''
        Mimic measure current in continuous mode

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points.
            curr_range:      string, ['10nA', '100nA', '1000nA', '10uA', '100uA', '1000uA', '10mA',
                                      '100mA', '1000mA', '3000mA'].
            sampling_rate:   float, [5~250000], unit Hz, default 5, Hzsampling rate.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            mimic.multi_points_current_measure(10, "1000nA")

        '''
        if curr_range not in \
                self.function_info[MimicDef.CHANNEL_CURRENT]:
            raise MimicException("error current scope")

        return self.multi_points_measure(count, MimicDef.CHANNEL_CURRENT,
                                         curr_range, sampling_rate)

    def multi_points_resistor_measure(self, count, res_range,
                                      sampling_rate=MimicDef.SAMPLING_RATE):
        '''
        Mimic measure resistor in continuous mode

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points.
            res_range:       string, ['4line_1ohm', '4line_100ohm', '4line_1Kohm',
                                      '4line_10Kohm', '4line_100Kohm',
                                      '4line_1Mohm', '4line_10Mohm', '4line_100Mohm',
                                      '2line_100ohm', '2line_1Kohm', '2line_10Kohm',
                                      '2line_100Kohm', '2line_1Mohm', '2line_10Mohm',
                                      '2line_100Mohm'].
            sampling_rate:   float, [5~250000], unit Hz, default 5, Hzsampling rate.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            mimic.multi_points_resistor_measure(10, "2line_100Kohm")

        '''
        if res_range not in \
                self.function_info[MimicDef.CHANNEL_RESISTOR]:
            raise MimicException('error resistor scope')

        result = self.multi_points_measure(count, MimicDef.CHANNEL_RESISTOR,
                                           res_range, sampling_rate)
        if result['min'][0] < 0:
            raise MimicException('2-wire and 4-wire short circuit or 4-wire open circuit')

        return result

    def multi_points_diode_measure(self, count, diode_range,
                                   sampling_rate=MimicDef.SAMPLING_RATE):
        '''
        Mimic measure diode in continuous mode

        Args:
            count:           int, [1~512], count of voltage/current/resistor data points.
            diode_range:     string, ['mV'].
             sampling_rate:   float, [5~250000], unit Hz, default 5, Hzsampling rate.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
             mimic.multi_points_diode_measure(10, "mV")

        '''
        if diode_range not in \
                self.function_info[MimicDef.CHANNEL_DIODE]:
            raise MimicException('error diode voltage scope')

        return self.multi_points_measure(count, MimicDef.CHANNEL_DIODE,
                                         diode_range, sampling_rate)

    def legacy_write_calibration_cell(self, unit_index, gain, offset, threshold):
        '''
        Mimic calibration data write

        Args:
            unit_index:   int, calibration unit index.
            gain:         float, calibration gain.
            offset:       float, calibration offset.
            threshold:    float, if value < threshold, use this calibration unit data.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.legacy_write_calibration_cell(0, 1.1, 0.1, 100)

        Raise:
            BoardArgCheckError:  unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset
        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        use_flag = self.calibration_info['use_flag']
        data = (gain, offset, use_flag, 0xff, 0xff, 0xff)
        s = struct.Struct(MimicCoeffDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(MimicCoeffDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info['unit_start_addr'] + \
            MimicCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'

    def legacy_read_calibration_cell(self, unit_index):
        '''
        Mimic read calibration data

        Args:
            unit_index: int, calibration unit index.

        Returns:
            dict, {'gain': value, 'offset': value, 'threshold': value, 'is_use': value}, calibraiton data

        Examples:
            data = board.legacy_read_calibration_cell(0)
            print(data)

        Raise:
            BoardArgCheckError:  unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset
        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        address = self.calibration_info['unit_start_addr'] + \
            MimicCoeffDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, MimicCoeffDef.READ_CAL_BYTE)

        s = struct.Struct(MimicCoeffDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(MimicCoeffDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_item in self.module_calibration_info:
            for level in self.module_calibration_info[cal_item]:
                if unit_index == self.module_calibration_info[cal_item][level]['unit_index']:
                    threshold = self.module_calibration_info[cal_item][level]['limit'][0]
                    break

        if self.calibration_info['use_flag'] != result[2]:
            return {'gain': 1.0, 'offset': 0.0, 'threshold': 0, 'is_use': False}
        else:
            return {'gain': result[0], 'offset': result[1], 'threshold': threshold, 'is_use': True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        Mimic erase calibration unit

        Args:
            unit_index:  int, calibration unit index.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.legacy_erase_calibration_cell(0)

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        data = [0xff for i in range(MimicCoeffDef.CAL_DATA_LEN)]
        address = self.calibration_info['unit_start_addr'] + \
            MimicCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'
