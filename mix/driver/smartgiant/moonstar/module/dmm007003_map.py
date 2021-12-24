# -*- coding: utf-8 -*-
from mix.driver.smartgiant.moonstar.module.dmm007001_map import MoonstarBase


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = 'V0.0.1'


class DMM007003Def:
    # These coefficient obtained from Moonstar Driver ERS
    VOLT_2_REAL_GAIN_5mV = 931.232
    VOLT_2_REAL_GAIN_5V = 1.0

    # current source gain
    CURRENT_2_REAL_GAIN = 21.0
    RES_GAIN_1mA = 221.6
    RES_GAIN_10mA = 21.6
    RES_GAIN_1000mA = 0.1

    VOLTAGE_5mV_RANGE = '5mV'
    VOLTAGE_5V_RANGE = '5V'

    CURRENT_1mA_RANGE = '1mA'
    CURRENT_10mA_RANGE = '10mA'
    CURRENT_1000mA_RANGE = '1000mA'

dmm007003_function_info = {
    DMM007003Def.VOLTAGE_5mV_RANGE: {
        'coefficient':
        1.0 / DMM007003Def.VOLT_2_REAL_GAIN_5mV,
        'bits':
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 0)]
    },
    DMM007003Def.VOLTAGE_5V_RANGE: {
        'coefficient':
        1.0 / DMM007003Def.VOLT_2_REAL_GAIN_5V,
        'bits':
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
    },
    DMM007003Def.CURRENT_1mA_RANGE: {
        'coefficient':
        1.0 / (DMM007003Def.CURRENT_2_REAL_GAIN * DMM007003Def.RES_GAIN_1mA),
        'bits':
            [(0, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    },
    DMM007003Def.CURRENT_10mA_RANGE: {
        'coefficient':
        1.0 / (DMM007003Def.CURRENT_2_REAL_GAIN * DMM007003Def.RES_GAIN_10mA),
        'bits':
            [(0, 1), (2, 0), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    },
    DMM007003Def.CURRENT_1000mA_RANGE: {
        'coefficient':
        1.0 / (DMM007003Def.CURRENT_2_REAL_GAIN * DMM007003Def.RES_GAIN_1000mA),
        'bits':
            [(0, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    }
}


class DMM007003(MoonstarBase):
    '''
    This driver is used for DMM007001 and DMM007002 board cards.

    compatible = ["GQQ-1085-5-030", "GQQ-1085-5-03A"]

    Args:
        i2c:        instance(I2C),  instance of I2CBus, which is used to control tca9538, eeprom and nct75.
        ipcore:     instance(MIXDMM007SGR)/string,  instance of MIXDMM007SGR, which is used to control AD7175.

    Examples:
        vref = 5000
        i2c_bus = I2C('/dev/i2c-0')
        ip = MIXDMM007SGR('/dev/AXI4_DMM007_SG_R_0', ad717x_mvref=vref, use_spi=False, use_gpio=False)
        dmm007 = DMM007003(i2c_bus, ip)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-1085-5-030", "GQQ-1085-5-03A"]

    def __init__(self, i2c, ipcore):
        super(DMM007003, self).__init__(i2c, ipcore, function_info=dmm007003_function_info)

    def get_driver_version(self):
        '''
        Get Moonstar driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
