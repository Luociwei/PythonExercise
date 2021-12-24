# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.smartgiant.common.ic.mcp4725_emulator import MCP4725Emulator
from mix.driver.smartgiant.omega.module.omega import OmegaBase

__author__ = 'ning.wu@gzseeing.com'
__version__ = '0.1'


# calibration info
dmm005003_calibration_info = {
    '200mv_100pf': {
        'level1': {'unit_index': 6, 'limit': (65, 'pf')},
        'level2': {'unit_index': 7, 'limit': (95, 'pf')},
        'level3': {'unit_index': 8, 'limit': (130, 'pf')},
    },
    '200mv_1000pf': {
        'level1': {'unit_index': 11, 'limit': (400, 'pf')},
        'level2': {'unit_index': 12, 'limit': (680, 'pf')},
        'level3': {'unit_index': 13, 'limit': (1100, 'pf')},
    },
    '200mv_10nf': {
        'level1': {'unit_index': 16, 'limit': (5, 'nf')},
        'level2': {'unit_index': 17, 'limit': (6.8, 'nf')},
        'level3': {'unit_index': 18, 'limit': (30, 'nf')},
    },
    '200mv_100nf': {
        'level1': {'unit_index': 21, 'limit': (33, 'nf')},
        'level2': {'unit_index': 22, 'limit': (68, 'nf')},
        'level3': {'unit_index': 23, 'limit': (300, 'nf')},
    },
    '200mv_1000nf': {
        'level1': {'unit_index': 26, 'limit': (330, 'nf')},
        'level2': {'unit_index': 27, 'limit': (700, 'nf')},
        'level3': {'unit_index': 28, 'limit': (3000, 'nf')},
    },
    '200mv_10uf': {
        'level1': {'unit_index': 31, 'limit': (5, 'uf')},
        'level2': {'unit_index': 32, 'limit': (20, 'uf')},
    },
    '200mv_50uf': {
        'level1': {'unit_index': 36, 'limit': (250, 'uf')},
    },
    '200mv_500uf': {
        'level1': {'unit_index': 41, 'limit': (200, 'uf')},
        'level2': {'unit_index': 42, 'limit': (1000, 'uf')},
    },
    '500mv_100pf': {
        'level1': {'unit_index': 43, 'limit': (65, 'pf')},
        'level2': {'unit_index': 44, 'limit': (95, 'pf')},
        'level3': {'unit_index': 45, 'limit': (130, 'pf')},
    },
    '500mv_1000pf': {
        'level1': {'unit_index': 46, 'limit': (400, 'pf')},
        'level2': {'unit_index': 47, 'limit': (680, 'pf')},
        'level3': {'unit_index': 48, 'limit': (1100, 'pf')},
    },
    '500mv_10nf': {
        'level1': {'unit_index': 49, 'limit': (5, 'nf')},
        'level2': {'unit_index': 50, 'limit': (6.8, 'nf')},
        'level3': {'unit_index': 51, 'limit': (30, 'nf')},
    },
    '500mv_100nf': {
        'level1': {'unit_index': 52, 'limit': (33, 'nf')},
        'level2': {'unit_index': 53, 'limit': (68, 'nf')},
        'level3': {'unit_index': 54, 'limit': (300, 'nf')},
    },
    '500mv_1000nf': {
        'level1': {'unit_index': 55, 'limit': (330, 'nf')},
        'level2': {'unit_index': 56, 'limit': (700, 'nf')},
        'level3': {'unit_index': 57, 'limit': (3000, 'nf')},
    },
    '500mv_10uf': {
        'level1': {'unit_index': 58, 'limit': (5, 'uf')},
        'level2': {'unit_index': 59, 'limit': (20, 'uf')},
    },
    '500mv_50uf': {
        'level1': {'unit_index': 60, 'limit': (250, 'uf')},
    },
    '500mv_500uf': {
        'level1': {'unit_index': 61, 'limit': (200, 'uf')},
        'level2': {'unit_index': 62, 'limit': (1000, 'uf')},
    },
}


dmm005003_range_table = {
    "200mv_100pf": 0,
    "200mv_1000pf": 1,
    "200mv_10nf": 2,
    "200mv_100nf": 3,
    "200mv_1000nf": 4,
    "200mv_10uf": 5,
    "200mv_50uf": 6,
    "200mv_500uf": 7,
    "500mv_100pf": 8,
    "500mv_1000pf": 9,
    "500mv_10nf": 10,
    "500mv_100nf": 11,
    "500mv_1000nf": 12,
    "500mv_10uf": 13,
    "500mv_50uf": 14,
    "500mv_500uf": 15
}


# range defines
dmm005003_line_select = {
    'vref_test': {
        'bits': 0x30,  # io-expander bits defined in ERS
        'resistance': (20000, 'ohm'),
        'dds_freq': '1kHz'
    },

    '100pf': {
        'bits': 0x21,
        'resistance': (20000, 'ohm'),
        'dds_freq': '100kHz'
    },

    '1000pf': {
        'bits': 0x21,
        'resistance': (20000, 'ohm'),
        'dds_freq': '30kHz'
    },

    '10nf': {
        'bits': 0x22,
        'resistance': (2000, 'ohm'),
        'dds_freq': '10kHz'
    },

    '100nf': {
        'bits': 0x24,
        'resistance': (200, 'ohm'),
        'dds_freq': '10kHz'
    },

    '1000nf': {
        'bits': 0x24,
        'resistance': (200, 'ohm'),
        'dds_freq': '1kHz'
    },

    '10uf': {
        'bits': 0x24,
        'resistance': (200, 'ohm'),
        'dds_freq': '200Hz'
    },

    '50uf': {
        'bits': 0x28,
        'resistance': (20, 'ohm'),
        'dds_freq': '100Hz'
    },

    '500uf': {
        'bits': 0x28,
        'resistance': (20, 'ohm'),
        'dds_freq': '20Hz'
    },

    'close': {
        'bits': 0x00,
        'resistance': (1, 'ohm'),
        'dds_freq': '0Hz'
    }
}


class Dmm005003Def:
    CAT9555_DEV3_ADDR = 0x20
    EEPROM_DEV3_ADDR = 0x50
    SENSOR_DEV3_ADDR = 0x48
    MCP4725_DEV_ADDR = 0x60

    DEFAULT_SAMPLE_RATE = 5
    MCP4725_RANGE_PIN = 6
    # mcp4725 normal voltage output
    NORMAL_VOLTAGE_200 = 1391.4
    NORMAL_VOLTAGE_500 = 1603.3
    # mcp4725 power down voltage output
    PD_VOLTAGE_200 = 1510
    PD_VOLTAGE_500 = 1925
    # mcp4725 offset voltage
    OFFSET_VOLTAGE_200 = 1369
    OFFSET_VOLTAGE_500 = 1581


class DMM005003(OmegaBase):
    '''
    DMM005003Base(DMM-005-003) is a high-accuracy capacitance measurement module,

    capacitance ranging from 10pF to 500uF can be measured.

    compatible = ["GQQ-DMM005003-000"]

    Test flow to measure capacitance:
        1.  DDS (AD9832) generate a SINE wave of frequency (20Hz to 100kHz – low freq for high cap)
            and apply the Voltage that will be sampled by ADC (AD7175).
        2.  One of relays (K1 thru K4) is toggled (depends on the capacitance measurement range)
        3.  DC is sampled by ADC (AD7175)
        4.  calculating capacitance formula: cap = Vo / (2 * Pi * f * R * Us)
        5.  K5 is toggled so the DDS’s SINE RMS is conveniented to DC and sampled by ADC (AD7175)

    Args:
        i2c:      instance(I2C),      If not given, AD7175 emulator will be created.
        spi:      instance(QSPI)/None, If not given, PLSPIBus emulator will be created.
        ipcore:   instance(MIXDAQT1)/string/None, If daqt1 given, then use MIXDAQT1's AD7175,MIXQSPI.

    Examples:
        If the params `daqt1` is valid, then use MIXDAQT1 aggregated IP;
        Otherwise, if the params `ad7175` and `ad9832` are valid, use non-aggregated IP.

        # use MIXDAQT1 aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        ip_daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                 use_spi=True, use_gpio=False)
        DMM005003 = DMM005003(i2c=i2c_bus,
                      spi=None,
                      ip=ip_daqt1)

        # use non-aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        spi_bus = PLSPIBus('/dev/MIX_SPI_0')
        DMM005003 = DMM005003(i2c=i2c_bus,
                      spi=spi_bus,
                      ip=None)

        # DMM005003Base measure capacitance using capacitance range
        result = omega.measure_capacitance('500uf')
        print(result)
        # terminal show "xxx uF"

    '''
    compatible = ["GQQ-DMM005003-000"]
    rpc_public_api = ['mcp4725_voltage_output', 'dds_mode_select', 'select_range'] + OmegaBase.rpc_public_api

    def __init__(self, i2c, spi=None, ipcore=None):

        if i2c:
            self.mcp4725 = MCP4725(Dmm005003Def.MCP4725_DEV_ADDR, i2c)
        else:
            self.mcp4725 = MCP4725Emulator(Dmm005003Def.MCP4725_DEV_ADDR, None, 3300)

        super(DMM005003, self).__init__(
            i2c, spi, None, ipcore, Dmm005003Def.EEPROM_DEV3_ADDR,
            Dmm005003Def.SENSOR_DEV3_ADDR, Dmm005003Def.CAT9555_DEV3_ADDR,
            dmm005003_calibration_info, dmm005003_range_table)

        self.dds_value_dict_200mv = {
            '20Hz': None,
            '100Hz': None,
            '200Hz': None,
            '1kHz': None,
            '10kHz': None,
            '30kHz': None,
            '100kHz': None,
        }

        self.dds_value_dict_500mv = {
            '20Hz': None,
            '100Hz': None,
            '200Hz': None,
            '1kHz': None,
            '10kHz': None,
            '30kHz': None,
            '100kHz': None,
        }
        self.omega_line_select = dmm005003_line_select
        self.omega_calibration_info = dmm005003_calibration_info

    def measure_dds_voltage(self):
        '''
        DMM005003 measure standard dds voltage value, used when board initializes.

        Returns:
            string, "done", api execution successful.

        Examples:
            omega.measure_dds_voltage()

        '''

        # select vref line
        self.mcp4725_voltage_output(Dmm005003Def.NORMAL_VOLTAGE_200)
        self.dds_mode_select('200mv')

        super(DMM005003, self).measure_dds_voltage()
        self.dds_value_dict_200mv = self.dds_value_dict

        self.mcp4725_voltage_output(Dmm005003Def.NORMAL_VOLTAGE_500)
        self.dds_mode_select('500mv')
        super(DMM005003, self).measure_dds_voltage()
        self.dds_value_dict_500mv = self.dds_value_dict

        self.mcp4725_voltage_output(Dmm005003Def.PD_VOLTAGE_200)
        self.dds_mode_select('200mv')

        return 'done'

    def _get_capacitance_result(self, frequency, cap_range, adc_samples):
        '''
        Omega measure adc value and convert it to capacitance result

        Args:
            frequency:      string, ['20Hz','100Hz','200Hz','1kHz','10kHz','100kHz'].
            cap_range:      string, ['100pF','1000pF','10nF','100nF','1000nF','10uF','50uF','500uF'],  unit mV.
            adc_samples:    int, (>0), adc sample numbers.

        Returns:
            float, value, capacitance value, unit is 'pF'/'nF'/'uF'.

        '''
        volt_list = []
        for i in range(adc_samples):
            volt = self._get_adc_voltage()
            volt_list.append(volt)

        volt_avg = sum(volt_list) / len(volt_list)
        cap_value = self._voltage_2_capacitance(volt_avg, frequency,
                                                cap_range)

        value = self.calibrate(self.cap_cal_range, cap_value[0])
        return [value, cap_value[1]]

    def measure_capacitance(self, cap_range,
                            sampling_rate=Dmm005003Def.DEFAULT_SAMPLE_RATE,
                            adc_samples=2, mcp4725_range="200mv"):
        '''
        DMM005003 measure capacitance using capacitance range

        Args:
            cap_range:       string, ['100pF', '1000pF', '10nF', '100nF', '1000nF', '10uF', '50uF', '500uF'].
            sampling_rate:   int, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            adc_samples:     int, (>0), default 2.
            mcp4725_range:   string, ['200mv', '500mv'], default '200mv'.

        Returns:
            float, value, capacitance value, unit is 'pF'/'nF'/'uF'.

        Examples:
            omega.measure_capacitance('100pF', 1000, 2, '200mv')

        '''
        self.cap_cal_range = mcp4725_range + '_' + cap_range.lower()
        if '200mv' == mcp4725_range:
            self.dds_value_dict = self.dds_value_dict_200mv
        elif '500mv' == mcp4725_range:
            self.dds_value_dict = self.dds_value_dict_500mv
        if "200mv" == mcp4725_range:
            self.mcp4725_voltage_output(Dmm005003Def.OFFSET_VOLTAGE_200)
        else:
            self.mcp4725_voltage_output(Dmm005003Def.OFFSET_VOLTAGE_500)

        cap_value = super(DMM005003, self).measure_capacitance(cap_range, sampling_rate, adc_samples)
        if "200mv" == mcp4725_range:
            self.mcp4725_voltage_output(Dmm005003Def.PD_VOLTAGE_200)
        else:
            self.mcp4725_voltage_output(Dmm005003Def.PD_VOLTAGE_500)

        return cap_value

    def mcp4725_voltage_output(self, volt):
        '''
        set the DAC output voltage(0-3.3V)

        Args:
            volt:    int, [0~3300].

        Returns:
            boolean, [True].

        Examples:
            omega.mcp4725_voltage_output(1000)

        '''
        self.mcp4725.output_volt_dc(volt)

        return True

    def dds_mode_select(self, mode):
        '''
        select dds range (200/500)mv

        Args:
            mode:  string, ['200mv', '500mv'].

        Returns:
            boolean, [True].

        Examples:
            omega.dds_mode_select('200mv')

        '''
        assert mode in ('500mv', '200mv')
        if '500mv' == mode:
            self.cat9555.set_pin(Dmm005003Def.MCP4725_RANGE_PIN, 1)
        elif '200mv' == mode:
            self.cat9555.set_pin(Dmm005003Def.MCP4725_RANGE_PIN, 0)
        return True
