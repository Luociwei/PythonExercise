# -*- coding: utf-8 -*-
import copy
from mix.driver.smartgiant.cloak.module.cloak import CloakBase
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG

__author__ = 'shunreng.he@SmartGiant'
__version__ = '0.1'


scope002006_calibration_info = {
    'CURR_AVG': {
        'level1': {'unit_index': 0, 'unit': 'mA'},
        'level2': {'unit_index': 1, 'unit': 'mA'},
        'level3': {'unit_index': 2, 'unit': 'mA'},
        'level4': {'unit_index': 3, 'unit': 'mA'},
        'level5': {'unit_index': 4, 'unit': 'mA'},
        'level6': {'unit_index': 5, 'unit': 'mA'},
        'level7': {'unit_index': 6, 'unit': 'mA'},
        'level8': {'unit_index': 7, 'unit': 'mA'},
        'level9': {'unit_index': 8, 'unit': 'mA'},
        'level10': {'unit_index': 9, 'unit': 'mA'},
        'level11': {'unit_index': 10, 'unit': 'mA'},
        'level12': {'unit_index': 11, 'unit': 'mA'},
        'level13': {'unit_index': 12, 'unit': 'mA'},
        'level14': {'unit_index': 13, 'unit': 'mA'},
        'level15': {'unit_index': 14, 'unit': 'mA'},
        'level16': {'unit_index': 15, 'unit': 'mA'},
        'level17': {'unit_index': 16, 'unit': 'mA'},
        'level18': {'unit_index': 17, 'unit': 'mA'},
        'level19': {'unit_index': 18, 'unit': 'mA'},
        'level20': {'unit_index': 19, 'unit': 'mA'},
        'level21': {'unit_index': 20, 'unit': 'mA'},
        'level22': {'unit_index': 21, 'unit': 'mA'}
    }
}

scope002006_range_table = {
    "CURR_AVG": 0
}


class Scope002006Def:
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48

    DEFAULT_SAMPLING_RATE = 1000

    AD7175_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535
    AD7175_MVREF = 2500.0  # mv
    AD7175_CODE_POLAR = "bipolar"
    AD7175_BUFFER_FLAG = "enable"
    AD7175_REFERENCE_SOURCE = "extern"
    AD7175_CLOCK = "crystal"


class Scope002006(CloakBase):
    '''
    Scope002006 Module is used for high precision current (DC) measurement.

    compatible = ["GQQ-SCP002006-000"]

    simultaneously and continuously data recording, the raw data can be
    uploaded to PC real time through Ethernet. The module shall work together with integrated
    control unit (ICU), which could achieve high-precision, automatic measurement.
    Current Input Channel: 15uA ~ 1.5A

    Note:This class is legacy driver for normal boot.

    Args:
        i2c:        instance(I2C)/None,       If not given, PLI2CBus emulator will be created.
        ipcore:     instance(MIXDAQT1)/None,  If daqt1 given, then use MIXDAQT1's AD7175.

    Examples:
        If the params `ipcore` is valid, then use MIXDAQT1 aggregated IP;
        Otherwise, if the params `ad7175`, use non-aggregated IP.

        # use MIXDAQT1 aggregated IP
        i2c = PLI2CBus('/dev/MIX_I2C_0')
        ip_daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=2500,
                 use_spi=False, use_gpio=False)
        scope002006 = Scope002006(i2c=i2c,
                                  ad7175=None,
                                  ipcore=ip_daqt1)

        # use non-aggregated IP
        ad7175 = PLAD7175('/dev/MIX_AD717x_0', 2500)
        i2c = PLI2CBus('/dev/MIX_I2C_1')
        cloak = Cloak(i2c=i2c,
                      ad7175=ad7175,
                      ipcore=None)

        #Scope002006 measure current once
        scope002006.multi_points_measure_disable('CURR')
        current = scope002006.current_measure()
        print(current)
        # terminal show "[xx, 'mA']"

        # Scope002006 measure current in continuous mode
        scope002006.multi_points_measure_enable('CURR', 1000)
        result = scope002006.multi_points_current_measure(10)
        print(result)
        # terminal show "{'current': (xx, 'mA'), 'rms': (xx, 'mArms'),
                'min': (xx, 'mA'), 'max': (xx, 'mA')}"

    '''

    rpc_public_api = copy.deepcopy(CloakBase.rpc_public_api)
    rpc_public_api.remove('voltage_measure')
    rpc_public_api.remove('multi_points_voltage_measure')

    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP002006-000"]

    def __init__(self, i2c, ad7175=None, ipcore=None):

        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, Scope002006Def.MIX_DAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=Scope002006Def.AD7175_MVREF,
                                     code_polar=Scope002006Def.AD7175_CODE_POLAR,
                                     reference=Scope002006Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=Scope002006Def.AD7175_BUFFER_FLAG,
                                     clock=Scope002006Def.AD7175_CLOCK,
                                     use_spi=False, use_gpio=False)
            ipcore.ad717x.config = {
                "ch0": {"P": "AIN0", "N": "AIN1"}
            }
            self.ad7175 = ipcore.ad717x
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, Scope002006Def.AD7175_REG_SIZE)
                ad7175 = MIXAd7175SG(axi4_bus, mvref=Scope002006Def.AD7175_MVREF,
                                     code_polar=Scope002006Def.AD7175_CODE_POLAR,
                                     reference=Scope002006Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=Scope002006Def.AD7175_BUFFER_FLAG,
                                     clock=Scope002006Def.AD7175_CLOCK)

            ad7175.config = {
                "ch0": {"P": "AIN0", "N": "AIN1"}
            }
            self.ad7175 = ad7175
        else:
            ad7175 = MIXAd7175SGEmulator('ad7175_emulator', 2500)
            ad7175.config = {
                "ch0": {"P": "AIN0", "N": "AIN1"}
            }

            self.ad7175 = ad7175

        super(Scope002006, self).__init__(i2c, ad7175, ipcore,
                                          Scope002006Def.EEPROM_DEV_ADDR,
                                          Scope002006Def.SENSOR_DEV_ADDR,
                                          scope002006_calibration_info,
                                          scope002006_range_table)

    def module_init(self):
        '''
        Configure GPIO pin default direction.

        This needs to be outside of __init__();
        Because when GPIO expander is behind an i2c-mux, set_dir() will fail unless
        i2c-mux channel is set, and setting channel is an external action beyond module.
        See example below for usage.

        Returns:
            string, "done", api execution successful.

        Examples:
            # GPIO expander directly connected to xavier, not behind i2c-mux:
            scope002006 = Scope002006(...)
            scope002006.module_init()

            # GPIO expander is connected to downstream port of i2c-mux:
            scope002006 = Scope002006(...)
            # some i2c_mux action
            ...
            scope002006.module_init()

        '''
        self.ad7175.reset()
        self.ad7175.channel_init()
        self.set_sampling_rate('CURR', Scope002006Def.DEFAULT_SAMPLING_RATE)
        self.load_calibration()

        return 'done'

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Cloak set sampling rate.

        AD717x output rate: 5 SPS to 10 kSPS.
        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad717x datasheet.

        Args:
            channel:        string, ['CURR'].
            sampling_rate:  int, [5~250000], Adc measure sampling rate, which is not continuous,
                                            please refer to ad717x datasheet.

        '''
        super(Scope002006, self).set_sampling_rate(channel, sampling_rate)

    def voltage_measure(self, sampling_rate=Scope002006Def.DEFAULT_SAMPLING_RATE):
        raise NotImplementedError("Can not use measure voltage function!")

    def multi_points_voltage_measure(self, count):
        raise NotImplementedError("Can not use measure voltage function!")
