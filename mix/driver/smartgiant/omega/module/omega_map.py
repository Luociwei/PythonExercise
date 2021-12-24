# -*- coding: utf-8 -*-

import math
import time
import re
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ic.ad9832 import AD9832
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1.1'


# range defines
omega_line_select = {
    'vref_test': {
        'bits': 0x70,  # io-expander bits defined in ERS
        'resistance': (20000, 'ohm'),
        'dds_freq': '1kHz'
    },

    '100pf': {
        'bits': 0x61,
        'resistance': (20000, 'ohm'),
        'dds_freq': '100kHz'
    },

    '1000pf': {
        'bits': 0x61,
        'resistance': (20000, 'ohm'),
        'dds_freq': '30kHz'
    },

    '10nf': {
        'bits': 0x62,
        'resistance': (2000, 'ohm'),
        'dds_freq': '10kHz'
    },

    '100nf': {
        'bits': 0x64,
        'resistance': (200, 'ohm'),
        'dds_freq': '10kHz'
    },

    '1000nf': {
        'bits': 0x64,
        'resistance': (200, 'ohm'),
        'dds_freq': '1kHz'
    },

    '10uf': {
        'bits': 0x64,
        'resistance': (200, 'ohm'),
        'dds_freq': '200Hz'
    },

    '50uf': {
        'bits': 0x68,
        'resistance': (20, 'ohm'),
        'dds_freq': '100Hz'
    },

    '500uf': {
        'bits': 0x68,
        'resistance': (20, 'ohm'),
        'dds_freq': '20Hz'
    },

    'close': {
        'bits': 0x00,
        'resistance': (1, 'ohm'),
        'dds_freq': '0Hz'
    }
}

omega_range_table = {
    "100pf": 0,
    "1000pf": 1,
    "10nf": 2,
    "100nf": 3,
    "1000nf": 4,
    "10uf": 5,
    "50uf": 6,
    "500uf": 7
}


class OmegaDef:
    MIXDAQT1_REG_SIZE = 0x8000
    PLAD7175_REG_SIZE = 0x8192
    CAT9555_DEV_ADDR = 0x25
    EEPROM_DEV_ADDR = 0x55
    SENSOR_DEV_ADDR = 0x4D
    COMPATIBLE_EEPROM_DEV_ADDR = 0x50
    COMPATIBLE_SENSOR_DEV_ADDR = 0x48

    DEFAULT_SAMPLE_RATE = 5
    ADC_VOLTAGE_CHANNEL = 0
    ADC_VREF_VOLTAGE_5000mV = 5000
    ADC_SAMPLES = 2
    DDS_OUTPUT_PHASE = 0
    DDS_OUTPUT_FREQ_0HZ = 0
    DDS_DELAY_400MS = 0.4
    DDS_DELAY_100MS = 0.1
    RELAY_DELAY_10MS = 0.01
    SPI_REG_SIZE = 256
    TIME_OUT = 1  # s
    DEFAULT_TIMEOUT = 15  # s


class OmegaException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class OmegaBase(SGModuleDriver):

    '''
    Base class of Omega and OmegaCompatible.

    Providing common Omega methods.

    Args:
        i2c:    instance(I2C)/None,             If not given, AD7175 emulator will be created.
        spi:    instance(QSPI)/None,            If not given, PLSPIBus emulator will be created.
        ad7175: instance(ADC)/string/None,      If not given, AD7175 emulator will be created.
        ipcore:     instance(MIXDAQT1SGR)/string/None, If daqt1 given, then use MIXDAQT1SGR's AD7175,MIXQSPI
        eeprom_devaddr:  int,                   Eeprom device address.
        sensor_dev_addr: int,                   NCT75 device address.
        cat9555_dev_addr: int,                  CAT9555 device address.

    '''

    rpc_public_api = ['get_sampling_rate', 'get_range', 'measure_dds_voltage',
                      'measure_capacitance'] + SGModuleDriver.rpc_public_api

    def __init__(
            self, i2c, spi=None, ad7175=None, ipcore=None,
            eeprom_dev_addr=OmegaDef.EEPROM_DEV_ADDR, sensor_dev_addr=OmegaDef.SENSOR_DEV_ADDR,
            cat9555_dev_addr=OmegaDef.CAT9555_DEV_ADDR, range_table=None):

        if ipcore and ad7175:
            raise OmegaException('Not allowed to use both aggregated IP and AD7175 at the same time')
        elif ipcore and spi:
            raise OmegaException('Not allowed to use both aggregated IP and MIXQSPI at the same time')

        self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
        self.sensor = NCT75(sensor_dev_addr, i2c)
        self.cat9555 = CAT9555(cat9555_dev_addr, i2c)

        if ipcore is None:
            if isinstance(ad7175, basestring):
                ad717x_axi4_bus = AXI4LiteBus(ad7175, OmegaDef.PLAD7175_REG_SIZE)
                ad7175 = MIXAd7175SG(ad717x_axi4_bus, OmegaDef.ADC_VREF_VOLTAGE_5000mV)

            if ad7175 is None:
                raise OmegaException('Not allowed both aggregated IP and ad7175 are None')
            else:
                self.ad7175 = ad7175

            if spi is None:
                raise OmegaException('Not allowed both aggregated IP and spi are None')
            else:
                self.spi = spi
            self.ad9832 = AD9832(self.spi)
        else:
            if isinstance(ipcore, basestring):
                daqt1_axi4_bus = AXI4LiteBus(ipcore, OmegaDef.MIXDAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                     ad717x_mvref=OmegaDef.ADC_VREF_VOLTAGE_5000mV,
                                     use_spi=True, use_gpio=False)

            self.ipcore = ipcore
            self.spi = self.ipcore.spi
            self.ad7175 = self.ipcore.ad717x
            self.ad9832 = AD9832(self.spi)

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }

        super(OmegaBase, self).__init__(self.eeprom, self.sensor, range_table=range_table)

        # RMS Voltage of DDS Output wave during board initialization
        self.dds_value_dict = {
            '20Hz': None,
            '100Hz': None,
            '200Hz': None,
            '1kHz': None,
            '10kHz': None,
            '30kHz': None,
            '100kHz': None,
        }
        self.line_select = None
        self.omega_line_select = omega_line_select

    def post_power_on_init(self, timeout=OmegaDef.DEFAULT_TIMEOUT):
        '''
        Init Omega module to a know harware state.

        Configure GPIO pin default direction.
        Configure QSPI speed and mode.
        Measure DDS voltage(used for calculating capacitance formula) during board initialization.
        This needs to be outside of __init__();
        Because when GPIO expander is behind an i2c-mux, set_dir() will fail unless
        i2c-mux channel is set, and setting channel is an external action beyond module.
        See example below for usage.

        Args:
            timeout:      float, (>=0), default 15, unit Second, execute timeout.
        '''
        self.spi.set_speed(400000)
        self.spi.set_mode('MODE1')
        self.reset(timeout)

    def reset(self, timeout=OmegaDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 15, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.cat9555.set_pins_dir([0x00, 0x00])
                self.ad7175.channel_init()
                self.set_sampling_rate(OmegaDef.DEFAULT_SAMPLE_RATE)
                self.measure_dds_voltage()
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise OmegaException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=OmegaDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.select_range('close')
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise OmegaException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Omega driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def _freq_str2int(self, freq):
        '''
        Omega convert string frequency to int value

        Args:
            freq:    string, endswith 'Hz'/'kHz'/'MHz'.

        Returns:
            int, value.

        '''

        # Match digits
        freq_value = int(re.findall(r'\d+', freq)[0])

        freq = freq.upper()
        if freq.endswith('MHZ') is True:
            freq_value *= 1000000
        elif freq.endswith('KHZ') is True:
            freq_value *= 1000
        elif freq.endswith('HZ') is True:
            freq_value = freq_value
        else:
            raise OmegaException('Frequency string value error')

        return freq_value

    def set_sampling_rate(self, sampling_rate):
        '''
        Omega set adc sampling rate, output rate: 5 SPS to 250 kSPS. This is private function.

        Args:
            sampling_rate:     float, [5~250000], adc measure sampling rate, which
                                                 is not continuous, please refer to ad7175 datasheet.

        Examples:
            omega.set_sampling_rate(5)

        '''
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate():
            self.ad7175.set_sampling_rate(OmegaDef.ADC_VOLTAGE_CHANNEL, sampling_rate)

    def get_sampling_rate(self):
        '''
        Omega get sampling rate of adc

        Returns:
            float, value, unit Hz, ad7175 sample rate value.

        Examples:
            omega.get_sampling_rate()

        '''

        return self.ad7175.get_sampling_rate(OmegaDef.ADC_VOLTAGE_CHANNEL)

    def select_range(self, cap_range):
        '''
        Omega select capacitance range. This is private function.

        Args:
            cap_range:    string, ['vref_test', '100pF', '1000pF', '10nF', '100nF', '1000nF', '10uF',
                                   '50uF', '500uF', 'close']. User usually does not need to use 'vref_test',
                                    it is only used when the board is initialized.

        Examples:
            omega.select_range('100pF')

        '''

        cap_range = cap_range.lower()
        assert cap_range in self.omega_line_select

        if self.line_select != cap_range:
            bits_value = self.omega_line_select[cap_range]['bits']
            self.cat9555.set_ports([bits_value & 0xFF, (bits_value >> 8) & 0xFF])
            self.line_select = cap_range

    def get_range(self):
        '''
        Omega get current capacitance range

        Returns:
            string, current selected range.

        Examples:
            omega.get_range()

        '''
        return self.line_select

    def _output_sine_waveform(self, frequency):
        '''
        Omega ad9832 output sine waveform

        Args:
            frequency:   float, [0~25000000], unit is Hz, waveform frequency.

        '''

        assert isinstance(frequency, (int, float))
        assert 0 <= frequency <= 25000000

        self.ad9832.output('FREQ0', frequency, 'PHASE0', OmegaDef.DDS_OUTPUT_PHASE)

    def _get_adc_voltage(self):
        '''
        Omega read adc voltage at single conversion mode

        Returns:
            float, value, unit Hz, ad7175 voltage value.

        '''

        voltage = self.ad7175.read_volt(OmegaDef.ADC_VOLTAGE_CHANNEL)
        return voltage

    def measure_dds_voltage(self):
        '''
        Omega measure standard dds voltage value, used when board initializes.

        Returns:
            string, "done", api execution successful.

        Examples:
            omega.measure_dds_voltage()

        '''

        # select vref line
        self.select_range('vref_test')
        time.sleep(OmegaDef.RELAY_DELAY_10MS)

        # measure standard dds voltage value
        for freq in self.dds_value_dict:
            self._output_sine_waveform(self._freq_str2int(freq))
            time.sleep(OmegaDef.DDS_DELAY_400MS)

            volt_list = []
            for i in range(OmegaDef.ADC_SAMPLES):
                volt = self._get_adc_voltage()
                volt_list.append(volt)

            volt_avg = sum(volt_list) / len(volt_list)
            self.dds_value_dict[freq] = volt_avg

        self._output_sine_waveform(OmegaDef.DDS_OUTPUT_FREQ_0HZ)
        self.select_range('close')

        return 'done'

    def _voltage_2_capacitance(self, voltage, frequency, cap_range):
        '''
        Omega convert ADC measure value to capacitance value

        Args:
            voltage:        float, unit mV.
            frequency:      string, ['20Hz', '100Hz', '200Hz', '1kHz', '10kHz', '100kHz'].
            cap_range:      string, ['100pF', '1000pF', '10nF', '100nF', '1000nF', '10uF', '50uF', '500uF'].

        Returns:
            list, [value, unit].

        '''
        dds_voltage = self.dds_value_dict[frequency]

        if dds_voltage is None:
            raise OmegaException('dds_voltage must be measured during board initialization')

        freq_hz = self._freq_str2int(frequency)
        resistance_value = self.omega_line_select[cap_range]['resistance'][0]

        # cap = Vo / (2 Pi * f * R * Us)
        cap_value = voltage / (2 * math.pi * freq_hz *
                               resistance_value * dds_voltage) * pow(10, 9)
        unit = 'nF'
        if cap_range in ['10pf', '100pf', '1000pf']:
            cap_value = cap_value * 1000.0
            unit = 'pF'
        elif cap_range in ['10uf', '50uf', '500uf']:
            cap_value = cap_value / 1000.0
            unit = 'uF'

        return [cap_value, unit]

    def _get_capacitance_result(self, frequency, cap_range, adc_samples):
        '''
        Omega measure adc value and convert it to capacitance result

        Args:
            frequency:      string, ['20Hz', '100Hz', '200Hz', '1kHz', '10kHz', '100kHz'].
            cap_range:      string, ['100pF', '1000pF', '10nF', '100nF', '1000nF', '10uF', '50uF', '500uF'], unit mV.
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

        value = self.calibrate(cap_range, cap_value[0])
        return [value, cap_value[1]]

    def measure_capacitance(self, cap_range,
                            sampling_rate=OmegaDef.DEFAULT_SAMPLE_RATE,
                            adc_samples=2):
        '''
        Omega measure capacitance using capacitance range

        Args:
            cap_range:       string, ['100pF', '1000pF', '10nF', '100nF', '1000nF', '10uF', '50uF', '500uF'].
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            adc_samples:     int, (>0), default 2.

        Returns:
            float, value, capacitance value, unit is 'pF'/'nF'/'uF'.

        Examples:
            omega.measure_capacitance('100pF', 1000, 2)

        '''
        cap_range = cap_range.lower()
        assert(cap_range in self.omega_line_select)
        assert isinstance(adc_samples, int) and (adc_samples > 0)

        frequency = self.omega_line_select[cap_range]['dds_freq']

        # select capacitance range
        self.select_range(cap_range)

        # set sampling rate
        self.set_sampling_rate(sampling_rate)

        # relay need some time
        time.sleep(OmegaDef.RELAY_DELAY_10MS)

        # dds output
        self._output_sine_waveform(self._freq_str2int(frequency))

        # dds need output some time
        time.sleep(OmegaDef.DDS_DELAY_100MS)

        # get capacitance result
        cap_value = self._get_capacitance_result(frequency, cap_range, adc_samples)

        # dds output close
        self._output_sine_waveform(OmegaDef.DDS_OUTPUT_FREQ_0HZ)
        # close range
        self.select_range('close')

        return cap_value


class DMM005002(OmegaBase):

    '''
    Omega(DMM-005-002) is a high-accuracy capacitance measurement module.

    capacitance ranging from 10pF to 500uF can be measured.
    This class is legacy driver for normal boot.

    Test flow to measure capacitance:
        1.  DDS (AD9832) generate a SINE wave of frequency (20Hz to 100kHz – low freq for high cap)
            and apply the Voltage that will be sampled by ADC (AD7175).
        2.  One of relays (K1 thru K4) is toggled (depends on the capacitance measurement range)
        3.  DC is sampled by ADC (AD7175)
        4.  calculating capacitance formula: cap = Vo / (2 * Pi * f * R * Us)
        5.  K5 is toggled so the DDS’s SINE RMS is conveniented to DC and sampled by ADC (AD7175)

    Args:
        i2c:    Instance(I2C)/None,             If not given, AD7175 emulator will be created.
        spi:    Instance(QSPI)/None,            If not given, PLSPIBus emulator will be created.
        ad7175: Instance(ADC)/string/None,      If not given, AD7175 emulator will be created.
        ipcore:     Instance(MIXDAQT1SGR)/string/None, If daqt1 given, then use MIXDAQT1SGR's AD7175,MIXQSPI

    Examples:
        If the params `daqt1` is valid, then use MIXDAQT1SGR aggregated IP;
        Otherwise, if the params `ad7175` and `ad9832` are valid, use non-aggregated IP.

        # use MIXDAQT1SGR aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        ip_daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                 use_spi=True, use_gpio=False)
        omega = DMM005002(i2c=i2c_bus,
                      spi=None,
                      ad7175=None,
                      ipcore=ip_daqt1)

        # use non-aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
        spi_bus = PLSPIBus('/dev/MIX_SPI_0')
        omega = DMM005002(i2c=i2c_bus,
                      spi=spi_bus,
                      ad7175=ad7175,
                      ipcore=None)

        # Omega measure capacitance using capacitance range
        result = omega.measure_capacitance('500uf')
        print(result)
        # terminal show "xxx uF"

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-ML3X-5-020"]

    def __init__(self, i2c, spi=None, ad7175=None, ipcore=None):
        super(DMM005002, self).__init__(
            i2c, spi, ad7175, ipcore, OmegaDef.EEPROM_DEV_ADDR, OmegaDef.SENSOR_DEV_ADDR,
            OmegaDef.CAT9555_DEV_ADDR, omega_range_table)
