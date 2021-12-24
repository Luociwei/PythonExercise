# -*- coding: utf-8 -*-
import time
import math
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667
from mix.driver.smartgiant.common.ipcore.mix_qi_asklink_encode_sg import MIXQIASKLinkEncodeSG
from mix.driver.smartgiant.common.ipcore.mix_qi_fsklink_decode_sg import MIXQIFSKLinkDecodeSG
from mix.driver.smartgiant.common.ipcore.mix_ad760x_sg import MIXAd7608SG
from mix.driver.smartgiant.common.ipcore.mix_xadc_sg import MIXXADCSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_scope007_sg_r import MIXScope007SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.core.ipcore.iioxadc import _IIOXADC


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1.2'


# Three AD5667s: Each has 2 channels, channel_id: 0-5
# ch0 ~ ch3: Analog Output
# ch4: fsk measurement circuit driver
# ch5: frequency measurement circuit driver
blade_dac_channel_info = {
    'ch0': {
        'id': 0,
    },
    'ch1': {
        'id': 1,
    },
    'ch2': {
        'id': 2,
    },
    'ch3': {
        'id': 3,
    },
    'ch4': {
        'id': 4,
    },
    'ch5': {
        'id': 5,
    },
}


blade_range_table = {
    'DAC_CH0': 0,
    'DAC_CH1': 1,
    'DAC_CH2': 2,
    'DAC_CH3': 3,

    'ADC_CH0_5V': 4,
    'ADC_CH1_5V': 5,
    'ADC_CH2_5V': 6,
    'ADC_CH3_5V': 7,
    'ADC_CH4_5V': 8,
    'ADC_CH5_5V': 9,
    'ADC_CH6_5V': 10,
    'ADC_CH7_5V': 11,

    'ADC_CH0_10V': 12,
    'ADC_CH1_10V': 13,
    'ADC_CH2_10V': 14,
    'ADC_CH3_10V': 15,
    'ADC_CH4_10V': 16,
    'ADC_CH5_10V': 17,
    'ADC_CH6_10V': 18,
    'ADC_CH7_10V': 19
}


class BladeDef:
    # CAT24C32 device address
    EEPROM_DEV_ADDR = 0x54
    # AD5667 device address
    DAC1_DEV_ADDR = 0x0C
    DAC2_DEV_ADDR = 0x0F
    DAC3_DEV_ADDR = 0x0E
    # AD5667 referance voltage
    DAC1_VOLTAGE_REF = 5500
    DAC2_VOLTAGE_REF = 5500
    DAC3_VOLTAGE_REF = 5500
    # PLGPIOEmulator reg_size
    PL_GPIO_REG_SIZE = 256
    # MIXAd7608SG reg_size
    PL_AD7608_REG_SIZE = 8192
    # MIXXADCSG reg_size
    PL_XADC_REG_SIZE = 2048
    # MIXSignalMeterSG reg_size
    SIGNAL_METER_REG_SIZE = 1024
    # MIXQIASKLinkEncodeSG reg_size
    MIX_QI_ASKLINK_CODE_REG_SIZE = 8192
    # MIXQIFSKLinkDecodeSG sample rate
    MIX_QI_FSKLINK_DECODE_REG_SIZE = 8192
    # MIXSignalMeterSG sample rate
    SIGNAL_METER_SAMPLE_RATE = 125000000

    # Switch to ADC conversion, supported by FPGA
    ADC_CTRL_PIN_0 = 91
    ADC_CTRL_PIN_1 = 92
    FSK_CTRL_PIN = 94
    FSK_CIC_CTRL_PIN = 93
    ADC_FILTER_PIN_0 = 86
    ADC_FILTER_PIN_1 = 87
    ADC_FILTER_PIN_2 = 88

    # AD7608: Simultaneous Sampling on All Analog Input Channels
    # Using PLGPIOs to filter each channel's sampled data
    ADC_FILTER_CONFIG = {
        'ch0': [0, 0, 0],
        'ch1': [1, 0, 0],
        'ch2': [0, 1, 0],
        'ch3': [1, 1, 0],
        'ch4': [0, 0, 1],
        'ch5': [1, 0, 1],
        'ch6': [0, 1, 1],
        'ch7': [1, 1, 1]
    }

    # AD7608: without over sampling
    ADC_OVER_SAMPLING = 0
    ADC_RANGES = ['5V', '10V']
    ADC_OPTIONS = ['AVG', 'RMS']
    ADC_5V_CALC_RATIO = (1000 * 5)
    ADC_10V_CALC_RATIO = (1000 * 10)

    # MIXXADCSG sample rate
    XADC_SAMPLING_RATE = 1000000
    XADC_BIPOLAR = 1
    # XADC anolog input range: 0-0.5V, if > 950, abnormal
    XADC_MAX_VOLTAGE = 950
    # XADC read 1000 voltage samples
    XADC_SAMPLE_COUNT = 1000
    # Average the maximum/minimum 150 voltage samples
    XADC_AVERAGE_COUNT = 150
    # VPP Calculate Ratio
    CALC_VPP_RATIO = 10
    # ASK Frequncy Default 2kHz
    DEFAULT_ASK_FREQ = 2000
    MIN_ASK_FREQ = 100
    MAX_ASK_FREQ = 100000
    TIME_OUT = 1


class BladeException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class BladeBase(SGModuleDriver):

    '''
    Base class of Blade and BladeCompatible.
    Providing common iceman methods.

    Args:
        i2c:              instance(I2C), If not given, PLI2CBus emulator will be created.
        adc:              instance(ADC)/string, If not given, AD760X emulator will be created.
        xadc:             instance(XADC)/string, if not given, MIXXADCSG emulator will be created.
        adc_signal_meter: instance(MIXSignalMeterSG)/string, if not given, MIXSignalMeterSG emulator will be created.
        ac_signal_meter:  instance(MIXSignalMeterSG)/string, if not given, MIXSignalMeterSG emulator will be created.
        fsk_signal_meter: instance(MIXSignalMeterSG)/string, if not given, MIXSignalMeterSG emulator will be created.
        ask_code:         instance(MIXQIASKLinkEncodeSG)/string,
                          if not given, MIXQIASKLinkEncodeSG emulator will be created.
        fsk_decode:       instance(MIXQIFSKLinkDecodeSG)/string,
                          if not given,MIXQIFSKLinkDecodeSG emulator will be created.
        adc_ctrl_pin_0:   instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        adc_ctrl_pin_1:   instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        fsk_ctrl_pin:     instance(GPIO), fsk enable/disable control pin.
        fsk_cic_ctrl_pin: instance(GPIO), fsk enable/disable cic_filter control pin.
        adc_filter_pin_0: instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_1: instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_2: instance(GPIO), determine which AD7608's channel to select.
        eeprom_devaddr:   int,            Eeprom device address.

    '''

    rpc_public_api = ['adc_voltage_measure', 'dac_output', 'ac_signal_measure',
                      'ask_write_encode_data', 'fsk_frequency_measure', 'fsk_decode_state',
                      'fsk_read_decode_data', 'adc_measure_upload_enable', 'adc_fft_measure',
                      'adc_measure_upload_disable'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, adc, xadc, adc_signal_meter,
                 ac_signal_meter, fsk_signal_meter,
                 ask_code, fsk_decode, adc_ctrl_pin_0,
                 adc_ctrl_pin_1, fsk_ctrl_pin,
                 fsk_cic_ctrl_pin,
                 adc_filter_pin_0, adc_filter_pin_1,
                 adc_filter_pin_2, ipcore, eeprom_devaddr):

        self.dac1 = AD5667(BladeDef.DAC1_DEV_ADDR, i2c, BladeDef.DAC1_VOLTAGE_REF)
        self.dac2 = AD5667(BladeDef.DAC2_DEV_ADDR, i2c, BladeDef.DAC2_VOLTAGE_REF)
        self.dac3 = AD5667(BladeDef.DAC3_DEV_ADDR, i2c, BladeDef.DAC3_VOLTAGE_REF)
        self.eeprom = CAT24C32(eeprom_devaddr, i2c)
        super(BladeBase, self).__init__(self.eeprom, None, range_table=blade_range_table)

        self.ipcore = ipcore
        if ipcore:
            if isinstance(ipcore, basestring):
                self.ipcore = MIXScope007SGR(ipcore)
            ac_signal_meter = self.ipcore.ac_signal_meter
            adc_signal_meter = self.ipcore.adc_signal_meter
            adc_filter_pin_0 = self.ipcore.adc_filter_pin_0
            adc_filter_pin_1 = self.ipcore.adc_filter_pin_1
            adc_filter_pin_2 = self.ipcore.adc_filter_pin_2
            adc_ctrl_pin_0 = self.ipcore.adc_ctrl_pin_0
            adc_ctrl_pin_1 = self.ipcore.adc_ctrl_pin_1
            fsk_ctrl_pin = self.ipcore.fsk_ctrl_pin
            fsk_cic_ctrl_pin = self.ipcore.fsk_cic_ctrl_pin
            self.adc_fft_pin_0 = self.ipcore.adc_fft_pin_0
            self.adc_fft_pin_1 = self.ipcore.adc_fft_pin_1
            self.adc_fft_pin_2 = self.ipcore.adc_fft_pin_2
            self.freq_gear_pin_0 = self.ipcore.freq_gear_pin_0
            self.freq_gear_pin_1 = self.ipcore.freq_gear_pin_1
            adc = self.ipcore.adc
            fsk_decode = self.ipcore.fsk_decode
            ask_code = self.ipcore.ask_code
            self.fftanalyzer = self.ipcore.fftanalyzer

        if isinstance(adc, basestring):
            axi4_bus = AXI4LiteBus(adc, BladeDef.PL_AD7608_REG_SIZE)
            self.adc = MIXAd7608SG(axi4_bus)
        elif adc:
            self.adc = adc
        else:
            raise BladeException("parameter 'adc' and 'ipcore' Can't be empty at the same time")

        if isinstance(xadc, basestring):
            axi4_bus = AXI4LiteBus(xadc, BladeDef.PL_XADC_REG_SIZE)
            self.xadc = MIXXADCSG(axi4_bus)
        elif xadc:
            self.xadc = xadc
        else:
            raise BladeException("parameter 'xadc' can not be None")

        if isinstance(adc_signal_meter, basestring):
            axi4_bus = AXI4LiteBus(adc_signal_meter, BladeDef.SIGNAL_METER_REG_SIZE)
            self.adc_signal_meter = MIXSignalMeterSG(axi4_bus)
        elif adc_signal_meter:
            self.adc_signal_meter = adc_signal_meter
        else:
            raise BladeException("parameter 'adc_signal_meter' and 'ipcore' Can't be empty at the same time")

        if isinstance(ac_signal_meter, basestring):
            axi4_bus = AXI4LiteBus(ac_signal_meter, BladeDef.SIGNAL_METER_REG_SIZE)
            self.ac_signal_meter = MIXSignalMeterSG(axi4_bus)
        elif ac_signal_meter:
            self.ac_signal_meter = ac_signal_meter
        else:
            raise BladeException("parameter 'ac_signal_meter' and 'ipcore' Can't be empty at the same time")

        if isinstance(fsk_signal_meter, basestring):
            axi4_bus = AXI4LiteBus(fsk_signal_meter, BladeDef.SIGNAL_METER_REG_SIZE)
            self.fsk_signal_meter = MIXSignalMeterSG(axi4_bus)
        else:
            self.fsk_signal_meter = fsk_signal_meter

        if isinstance(ask_code, basestring):
            axi4_bus = AXI4LiteBus(ask_code, BladeDef.MIX_QI_ASKLINK_CODE_REG_SIZE)
            self.ask_code = MIXQIASKLinkEncodeSG(axi4_bus)
        elif ask_code:
            self.ask_code = ask_code
        else:
            raise BladeException("parameter 'ask_code' and 'ipcore' Can't be empty at the same time")

        if isinstance(fsk_decode, basestring):
            axi4_bus = AXI4LiteBus(fsk_decode, BladeDef.MIX_QI_FSKLINK_DECODE_REG_SIZE)
            self.fsk_decode = MIXQIFSKLinkDecodeSG(axi4_bus)
        elif fsk_decode:
            self.fsk_decode = fsk_decode
        else:
            raise BladeException("parameter 'fsk_decode' and 'ipcore' Can't be empty at the same time")

        # These Pins supported by FPGA
        self.adc_ctrl_pin_0 = adc_ctrl_pin_0
        self.adc_ctrl_pin_1 = adc_ctrl_pin_1
        self.fsk_ctrl_pin = fsk_ctrl_pin
        self.fsk_cic_ctrl_pin = fsk_cic_ctrl_pin
        self.adc_filter_pin_0 = adc_filter_pin_0
        self.adc_filter_pin_1 = adc_filter_pin_1
        self.adc_filter_pin_2 = adc_filter_pin_2

    def post_power_on_init(self, timeout=BladeDef.TIME_OUT):
        '''
        Init Blade module to a know harware state.

        Configure GPIO pin default direction.
        Configure XADC sampling rate and polar.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        self.reset(timeout)

    def reset(self, timeout=BladeDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_ctrl_pin_0.set_dir('output')
                self.adc_ctrl_pin_1.set_dir('output')
                self.fsk_ctrl_pin.set_dir('output')
                self.fsk_cic_ctrl_pin.set_dir('output')
                self.adc_filter_pin_0.set_dir('output')
                self.adc_filter_pin_1.set_dir('output')
                self.adc_filter_pin_2.set_dir('output')
                if (self.ipcore is not None):
                    self.adc_fft_pin_0.set_dir('output')
                    self.adc_fft_pin_1.set_dir('output')
                    self.adc_fft_pin_2.set_dir('output')

                if isinstance(self.xadc, MIXXADCSG):
                    self.xadc.config(BladeDef.XADC_SAMPLING_RATE, BladeDef.XADC_BIPOLAR)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise BladeException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=BladeDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set pin level to 0 and close signal source.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.dac_output('ch0', 0)
                self.dac_output('ch1', 0)
                self.dac_output('ch2', 0)
                self.dac_output('ch3', 0)
                self.dac_output('ch4', 0)
                self.dac_output('ch5', 0)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise BladeException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Blade driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def _check_adc_channel(self, adc_channel):
        '''
        Check the channel if it is valid.

        Args:
            adc_channel:    string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'], the channel to check.

        Returns:
            string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'], the channel in specific format.

        Raise:
            BladeException:  If adc_channel is invalid, exception will be raised.

        '''
        for ch in BladeDef.ADC_FILTER_CONFIG:
            if adc_channel.lower() == ch.lower():
                return ch
        raise BladeException("adc_channel {} is invalid".format(adc_channel))

    def _check_dac_channel(self, dac_channel):
        '''
        Check the channel if it is valid.

        Args:
            dac_channel:    string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5'], the channel to check.

        Returns:
            string,    ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5'], the channel in specific format.

        Raise:
            BladeException:  If dac_channel is invalid, exception will be raised.

        '''
        for ch in blade_dac_channel_info:
            if dac_channel.lower() == ch.lower():
                return ch
        raise BladeException("dac_channel {} is invalid".format(dac_channel))

    def _check_adc_range(self, adc_range):
        '''
        Check the range if it is valid.

        Args:
            adc_range:    string, ['5V', '10V'], the range to check.

        Returns:
            string, ['5V', '10V'], the range in specific format.

        Raise:
            BladeException:  If adc_range is invalid, exception will be raised.

        '''
        for ch in BladeDef.ADC_RANGES:
            if adc_range.upper() == ch.upper():
                return ch
        raise BladeException("adc_range {} is invalid".format(adc_range))

    def _check_adc_option(self, option):
        '''
        Check the option if it is valid.

        Args:
            option:    string, ['AVG', 'RMS'], the option to check.

        Returns:
            string, ['AVG', 'RMS'], the option in specific format.

        Raise:
            BladeException:  If option is invalid, exception will be raised.

        '''
        for ch in BladeDef.ADC_OPTIONS:
            if option.upper() == ch.upper():
                return ch
        raise BladeException("ADC option {} is invalid".format(option))

    def _select_adc_channel(self, adc_channel):
        '''
        Blade select specific analog input channel.

        Note AD7608 simultaneous sampling on all analog input channels,
        filter specific channel data with PLGPIOs, supported by FPGA.

        Args:
            adc_channel:    string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'], the analog input channel.

        '''
        adc_channel = self._check_adc_channel(adc_channel)

        bit = BladeDef.ADC_FILTER_CONFIG[adc_channel]
        self.adc_filter_pin_0.set_level(bit[0])
        self.adc_filter_pin_1.set_level(bit[1])
        self.adc_filter_pin_2.set_level(bit[2])

    def _select_adc_fft_channel(self, adc_channel):
        '''
        Blade select specific analog input channel.

        Note AD7608 simultaneous sampling on all analog input channels,
        filter specific channel data with PLGPIOs, supported by FPGA.

        Args:
            adc_channel:    string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'], the analog input channel.

        '''
        adc_channel = self._check_adc_channel(adc_channel)

        bit = BladeDef.ADC_FILTER_CONFIG[adc_channel]
        if (self.ipcore is not None):
            self.adc_fft_pin_0.set_level(bit[0])
            self.adc_fft_pin_1.set_level(bit[1])
            self.adc_fft_pin_2.set_level(bit[2])

    def adc_voltage_measure(self, option, adc_channel, adc_range,
                            sampling_rate, count, time_ms):
        '''
        Blade Analog input measurement, measure DC voltage with option `AVG` or `RMS`.

        Args:
            option:          string, ['AVG', 'RMS'], 'AVG' means average, 'RMS' means Root Mean Square.
            adc_channel:     string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7'], ADC channel.
            adc_range:       string, ['10V', '5V'], measure range.
            sampling_rate:   int, [2000~200000], sampling rate.
            count:           int, [1~512], sample count.
            time_ms:         int, [1~2000], unit ms.

        Returns:
            list, [value, "mV"], voltage data list.

        '''
        option = self._check_adc_option(option)
        adc_channel = self._check_adc_channel(adc_channel)
        adc_range = self._check_adc_range(adc_range)
        assert isinstance(sampling_rate, int) and (2000 <= sampling_rate <= 200000)
        assert isinstance(count, int) and (count > 0)
        assert isinstance(time_ms, int) and (1 <= time_ms <= 2000)

        # Switch to ADC conversion, supported by FPGA.
        self.adc_ctrl_pin_0.set_level(0)
        self.adc_ctrl_pin_1.set_level(0)

        # Use Ip to control signal meter.
        if (self.ipcore is not None):
            measure_mask = 0x30
        else:
            measure_mask = 0x00

        # Select specific AD7608 channel, supported by FPGA.
        self._select_adc_channel(adc_channel)

        # Enable AD7608 continuous sampling, without over sampling.
        self.adc.enable_continuous_sampling(BladeDef.ADC_OVER_SAMPLING,
                                            adc_range, sampling_rate)

        # Use Signal Meter to measure
        self.adc_signal_meter.close()
        self.adc_signal_meter.open()

        voltage = list()
        for i in range(count):
            adc_value = 0
            self.adc_signal_meter.start_measure(time_ms, sampling_rate, measure_mask)
            rms_value = self.adc_signal_meter.rms()

            if adc_range == '5V':
                adc_value = rms_value[1] * BladeDef.ADC_5V_CALC_RATIO
            elif adc_range == '10V':
                adc_value = rms_value[1] * BladeDef.ADC_10V_CALC_RATIO
            adc_value = self.calibrate('ADC_' + adc_channel.upper() + "_" + adc_range, adc_value)

            voltage.append(adc_value)

        # Close Signal Meter, Disable AD7608 continuous sampling.
        self.adc_signal_meter.close()
        self.adc.disable_continuous_sampling()

        result = list()
        if option == 'RMS':
            # The sign of rms value
            sign = -1 if voltage[0] < 0 else 1
            rms = math.sqrt(sum(x**2 for x in voltage) / count)
            result = [sign * rms, 'mV']
        elif option == 'AVG':
            avg = sum(voltage) / count
            result = [avg, 'mV']

        return result

    def dac_output(self, dac_channel, voltage):
        '''
        Blade adc output voltage, 0-5500mV.

        Note 'ch0'~'ch3' for analog output circuit driver,
        'ch4'~'ch5' for fsk and frequency measurement circuit driver.

        Args:
            dac_channel:    string, ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5'].
            voltage:        int, [0~5500], unit mV.

        Returns:
            string, "done", api execution successful.

        Raise:
            BladeException:  If dac_channel_id is invalid, exception will be raised.

        '''

        dac_channel = self._check_dac_channel(dac_channel)
        assert 0 <= voltage <= BladeDef.DAC1_VOLTAGE_REF

        cal_item = 'DAC_' + dac_channel.upper()
        if cal_item in blade_range_table:
            voltage = self.calibrate(cal_item, voltage)

        channel_id = blade_dac_channel_info[dac_channel]['id']
        if channel_id // 2 == 0:
            self.dac1.output_volt_dc(channel_id % 2, voltage)
        elif channel_id // 2 == 1:
            self.dac2.output_volt_dc(channel_id % 2, voltage)
        elif channel_id // 2 == 2:
            self.dac3.output_volt_dc(channel_id % 2, voltage)
        else:
            raise BladeException("dac_channel_id {} is invalid".format(channel_id))

        return 'done'

    def _read_vpp_value(self):
        '''
        Blade XADC read vpp voltage value, anolog input connect to pin VP_0 and VN_0.

        XADC read 1000 voltage samples and sort them;
        Average the maximum 150 voltage samples as volt_max;
        Average the minimum 150 voltage samples as volt_min;
        Vpp = volt_max – volt_min

        Returns:
            int, value, unit mV.

        '''

        voltage = list()

        if isinstance(self.xadc, MIXXADCSG):
            # XADC read 1000 voltage samples.
            for i in range(BladeDef.XADC_SAMPLE_COUNT):
                rd_data = self.xadc.read_volt()
                voltage.append(rd_data)

        if isinstance(self.xadc, _IIOXADC):
            for i in range(BladeDef.XADC_SAMPLE_COUNT):
                rd_data = self.xadc.read_voltage('vpvn')
                voltage.append(rd_data)

        # Sort them, pick up the maximum or minimum samples.
        voltage.sort()

        # Remove abnormal voltage samples
        for i in range(BladeDef.XADC_SAMPLE_COUNT):
            if max(voltage) > BladeDef.XADC_MAX_VOLTAGE:
                voltage.remove(max(voltage))
            else:
                break

        # Calculate volt_max and volt_min
        volt_max = sum(voltage[-BladeDef.XADC_AVERAGE_COUNT:]) / BladeDef.XADC_AVERAGE_COUNT
        volt_min = sum(voltage[:BladeDef.XADC_AVERAGE_COUNT]) / BladeDef.XADC_AVERAGE_COUNT
        # Calculate vpp
        vpp = volt_max - volt_min

        return vpp

    def ac_signal_measure(self, option, ref_volt, time_ms, gear=None):
        '''
        Blade AC signal measurement, Amplitude,Frequency and Duty Cycle Measurement.

        Args:
            option:        string, ['f', 'd', 'v', 'w']. 'f', freq, unit is Hz, 'd', duty, unit is '%%'.
                                    'v', vpp, unit is 'mV'. 'w', width, unit is 'us',
                                    You can combine them any way you want.
            ref_volt:      int, [0~5000], unit mV, control voltage comparator
                                                   ref_volt should be 1/4 Amplitude input.
            time_ms:       int, [1~2000], unit ms.
            gear:          string, ['high', 'mid', 'low'] 'high':<1MHz;'mid":1MHz~7.5MHz;'low':>7.5MHz.

        Returns:
            dict, {"freq": (value, 'Hz'), "duty": (value, '%'), "width": (value, 'us'), "vpp": (value, 'mV')}.

        '''
        assert isinstance(time_ms, int) and (1 <= time_ms <= 2000)
        assert isinstance(ref_volt, int)
        assert (0 <= ref_volt <= BladeDef.DAC1_VOLTAGE_REF)

        # Use Ip to control signal measure.
        if (self.ipcore is not None):
            measure_mask = 0xC0
        else:
            measure_mask = 0x00

        if (gear is not None):
            assert isinstance(gear, basestring)
            if gear == 'high':
                self.freq_gear_pin_0.set_level(1)
                self.freq_gear_pin_1.set_level(0)
            elif gear == 'mid':
                self.freq_gear_pin_0.set_level(0)
                self.freq_gear_pin_1.set_level(1)
            elif gear == 'low':
                self.freq_gear_pin_0.set_level(0)
                self.freq_gear_pin_1.set_level(0)
            else:
                raise BladeException('Please check the parameters!')

        # dac_ch5 output voltage, hardware devider 1/2.
        # ref_volt should be 1/4 Amplitude input.
        self.dac_output('ch5', ref_volt)

        self.ac_signal_meter.open()
        self.ac_signal_meter.start_measure(time_ms, BladeDef.SIGNAL_METER_SAMPLE_RATE, measure_mask)
        freq = self.ac_signal_meter.measure_frequency('LP')
        duty = self.ac_signal_meter.duty()
        # Calculate Width Unit is 'us'
        width = 1000000.0 / freq * duty / 100
        self.ac_signal_meter.close()

        result = dict()
        if 'f' in option:
            result['freq'] = (freq, 'Hz')
        if 'd' in option:
            result['duty'] = (duty, '%')
        if 'w' in option:
            result['width'] = (width, 'us')
        if 'v' in option:
            vpp = self._read_vpp_value() * BladeDef.CALC_VPP_RATIO
            result['vpp'] = (vpp, 'mV')

        return result

    def adc_fft_measure(self, adc_channel, adc_range, decimation_type, sampling_rate, bandwidth, harmonic_count=5):
        '''
         adc fft measure, measure frequency ,thd, thdn, vpp

         Args:
              adc_channel:       string,     ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7']
              adc_range:         string,     ('10V', '5V')
              decimation_type:   int,        [1~255]
              sampling_rate:     int,        [2000- 200000]
              bandwidth:         int/string,  FFT calculation bandwidth limit, must smaller than half of sample_rate,
                                               unit is Hz. Eg. 20000. If 'auto' given, bandwidth will be automatically
                                               adjust based on base frequency.
         Returns:
              dict, {"freq": (value, 'Hz'),  "thd":(vslue,'dB'),  "vpp": (value, 'V'),  "thdn":(value,'dB')}.
        '''
        assert isinstance(sampling_rate, int) and (2000 <= sampling_rate <= 200000)
        adc_channel = self._check_adc_channel(adc_channel)
        self.adc_ctrl_pin_0.set_level(0)
        self.adc_ctrl_pin_1.set_level(1)
        self._select_adc_fft_channel(adc_channel)
        self.adc.enable_continuous_sampling(BladeDef.ADC_OVER_SAMPLING, adc_range, sampling_rate)
        self.fftanalyzer.disable()
        self.fftanalyzer.enable()
        self.fftanalyzer.disable_upload()
        self.fftanalyzer.analyze_config(sampling_rate, decimation_type, bandwidth, harmonic_count)
        self.fftanalyzer.analyze()
        result = dict()
        result['vpp'] = (self.fftanalyzer.get_vpp() * (20 if(adc_range == '10V') else 10), 'V')
        result['freq'] = (self.fftanalyzer.get_frequency(), 'Hz')
        result['thdn'] = (self.fftanalyzer.get_thdn(), 'dB')
        result['thd'] = (self.fftanalyzer.get_thd(), 'dB')

        return result

    def ask_write_encode_data(self, data, freq=BladeDef.DEFAULT_ASK_FREQ):
        '''
        Blade Write Ask encoded signal data.

        Args:
            data:  list, Data to write, the list item is byte.
            freq:  int, [100~100000], unit Hz,  Ask square wave frequency.

        Returns:
            string, "done", api execution successful.

        '''
        assert isinstance(freq, int) and BladeDef.MIN_ASK_FREQ <= freq <= BladeDef.MAX_ASK_FREQ
        assert isinstance(data, list) and len(data) > 0

        self.ask_code.set_frequency(freq)
        self.ask_code.write_encode_data(data)
        return 'done'

    def fsk_frequency_measure(self, time_ms):
        '''
        Blade measure FSK signal frequency.

        Args:
            time_ms:    int, [1~2000], unit ms, signal meter measure time.

        Returns:
            int, value, unit Hz.

        '''
        assert isinstance(time_ms, int) and (1 <= time_ms <= 2000)

        if not self.fsk_signal_meter:
            raise BladeException("parameter 'fsk_signal_meter' is None")
        self.fsk_signal_meter.open()
        self.fsk_signal_meter.start_measure(time_ms, BladeDef.SIGNAL_METER_SAMPLE_RATE)
        freq = self.fsk_signal_meter.measure_frequency('LP')
        self.fsk_signal_meter.close()

        return freq

    def fsk_decode_state(self):
        '''
        Blade Get Fsk Decode state.

        Returns:
            boolean, [True, False], True: Fsk decode Parity bit is ok,
                                    False: Fsk decode Parity bit is error

        '''
        # FSK Decode enable
        self.fsk_ctrl_pin.set_level(0)

        return self.fsk_decode.state()

    def fsk_read_decode_data(self, cic_filter=True):
        '''
        Blade Read FSK signal data from fifo.

        Args:
            cic_filter:  boolean, [True, False], True: enable CIC_Filter
                                                 False:disable CIC_Filter

        Returns:
            list, [value], the returned data list item is byte.

        '''
        # FSK Decode enable
        self.fsk_ctrl_pin.set_level(0)

        # CIC filter enable/disable
        if cic_filter:
            self.fsk_cic_ctrl_pin.set_level(0)
        else:
            self.fsk_cic_ctrl_pin.set_level(1)

        return self.fsk_decode.read_decode_data()

    def adc_measure_upload_enable(self, adc_range, sampling_rate):
        '''
        Blade adc measure data upoad mode open. Control ad7608 upload data of ADC when doing measurement.

        It's not necessary enable upload when doing measurement.
        Note that data transfered into DMA is 32bit each data,
        formate: bit[0-17] adc_value; bit[29-31] channel number; bit[18-28] unused.

        Args:
            adc_range:       string, ['10V', '5V'], measure range.
            sampling_rate:   int, [2000~200000], sampling rate.

        Returns:
            string, "done", api execution successful.

        '''
        adc_range = self._check_adc_range(adc_range)
        assert isinstance(sampling_rate, int) and (2000 <= sampling_rate <= 200000)

        # Switch to data upoad mode, supported by FPGA.
        self.adc_ctrl_pin_0.set_level(1)
        self.adc_ctrl_pin_1.set_level(0)

        self.adc.enable_continuous_sampling(BladeDef.ADC_OVER_SAMPLING, adc_range, sampling_rate)
        return 'done'

    def adc_measure_upload_disable(self):
        '''
        Blade upoad mode close. Close data upload doesn't influence to measure.

        Returns:
            string, "done", api execution successful.

        '''
        self.adc.disable_continuous_sampling()
        return 'done'


class Scope007001(BladeBase):

    '''
    This class is legacy driver for normal boot.

    The Blade(SCOPE-007) module can perform simultaneously, continuously data recording;
    analog output; frequency conditioning;
    It includes eight ADC channels, four DAC channels, and AC signal measurement
    conditioning circuit.
    It can be used to recording DC voltage of power rail continuously and current
    sampling resistor’s voltage. And analog output signals to drive any device,
    such like PSU, reference level, etc..

    Args:
        i2c:                 instance(I2C), If not given, PLI2CBus emulator will be created.
        adc:                 instance(ADC), If not given, AD760X emulator will be created.
        xadc:                instance(XADC), if not given, MIXXADCSG emulator will be created.
        adc_signal_meter:    instance(MIXSignalMeterSG), if not given, MIXSignalMeterSG emulator will be created.
        ac_signal_meter:     instance(MIXSignalMeterSG), if not given, MIXSignalMeterSG emulator will be created.
        fsk_signal_meter:    instance(MIXSignalMeterSG), if not given, MIXSignalMeterSG emulator will be created.
        ask_code:            instance(MIXQIASKLinkEncodeSG),
                             if not given, MIXQIASKLinkEncodeSG emulator will be created.
        fsk_decode:          instance(MIXQIFSKLinkDecodeSG),
                             if not given, MIXQIFSKLinkDecodeSG emulator will be created.
        adc_ctrl_pin_0:      instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        adc_ctrl_pin_1:      instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        fsk_ctrl_pin:        instance(GPIO), fsk enable/disable control pin.
        fsk_cic_ctrl_pin:    instance(GPIO), fsk enable/disable cic_filter control pin.
        adc_filter_pin_0:    instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_1:    instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_2:    instance(GPIO), determine which AD7608's channel to select.
        eeprom_devaddr:      int,           Eeprom device address.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_I2C_0', 256)
        i2c_bus = PLI2CBus(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_AD760x_0', 8192)
        ad7608 = AD7608(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_XADC_0', 2048)
        xadc = MIXXADCSG(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_0', 1024)
        adc_signal_meter= MIXSignalMeterSG(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_1', 1024)
        ac_signal_meter = MIXSignalMeterSG(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_2', 1024)
        fsk_signal_meter = MIXSignalMeterSG(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_ASK_Encode_0', 2048)
        ask_code = MIXQIASKLinkEncodeSG(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_FSK_Decode_0', 2048)
        fsk_decode = MIXQIFSKLinkDecodeSG(axi4_bus)

        axi4_bus = AXI4LiteBus('/dev/AXI4_GPIO_0', 256)
        gpio = PLGPIO(axi4_bus)
        adc_ctrl_pin_0 = Pin(gpio, 91)
        adc_ctrl_pin_1 = Pin(gpio, 92)
        fsk_cic_ctrl_pin = Pin(gpio, 93)
        fsk_ctrl_pin = Pin(gpio, 94)
        adc_filter_pin_0 = Pin(gpio, 86)
        adc_filter_pin_1 = Pin(gpio, 87)
        adc_filter_pin_2 = Pin(gpio, 88)

        scope007001 = Scope007001(i2c=i2c_bus,
                      adc=ad7608,
                      xadc=xadc,
                      adc_signal_meter=adc_signal_meter,
                      ac_signal_meter=ac_signal_meter,
                      fsk_signal_meter=fsk_signal_meter,
                      ask_code=ask_code,
                      fsk_decode=fsk_decode,
                      adc_ctrl_pin_0=adc_ctrl_pin_0,
                      adc_ctrl_pin_1=adc_ctrl_pin_1,
                      fsk_ctrl_pin=fsk_ctrl_pin,
                      fsk_cic_ctrl_pin=fsk_cic_ctrl_pin,
                      adc_filter_pin_0=adc_filter_pin_0,
                      adc_filter_pin_1=adc_filter_pin_1,
                      adc_filter_pin_2=adc_filter_pin_2)

        Example for Analog input measurement:
            # scope007001 Analog input measurement, measure DC voltage with option `AVG` or `RMS`.
            adc_value = scope007001.adc_voltage_measure('AVG', 'ch0', '5V', 20000, 5, 100)
            print(adc_value)
            # Terminal shows "[xxx.xxx, 'mV']"

        Example for Analog output:
            # scope007001 dac output voltage, 0-5500 mV
            scope007001.dac_output('ch0', 1000)

        Example for AC signal measurement:
            # Signal: Square,100000Hz,2.5 VPP, 50%, High 1.25V

            # scope007001 measure ac signal with option 'f': freq
            result = scope007001.ac_signal_measure('f', 2500, 1000)
            print(result)
            # Terminal shows "{'freq': (xxx.x, 'Hz')}"

            # scope007001 measure ac signal with option 'v': vpp
            result = scope007001.ac_signal_measure('v', 2500, 1000)
            print(result)
            # Terminal shows "{'vpp': (xxx, 'mV')}"

            # scope007001 measure ac signal with option 'fwd': freq, width, duty
            result = scope007001.ac_signal_measure('fwd', 2500, 1000)
            print(result)
            # Terminal shows "{'duty': (xxx, '%%'), 'width': (xxx, 'us'), 'freq': (xxx, 'Hz')}"

        Example for ASK signal Encode:
            data = [1, 2, 3, 4, 5]
            scope007001.ask_write_encode_data(data)

        Example for FSK signal Decode:
            # scope007001 measure FSK signal frequency and receive data.
            freq = scope007001.fsk_frequency_measure(2000)
            print(freq)
            # FSK Decode State
            state = scope007001.fsk_decode_state()
            print(state)
            data = scope007001.fsk_read_decode_data()
            print(data)

        Example for data upload:
            dma = DMA("/dev/MIX_DMA_0")
            dma_channel = 0
            dma.config_channel(dma_channel, 0x1000000)
            dma.enable_channel(dma_channel)
            dma.reset_channel(dma_channel)
            scope007001.adc_measure_upload_enable('10V', 2000)
            time.sleep(1)
            result, data, data_num, overflow = dma.read_channel_all_data(dma_channel)
            dma.read_done(dma_channel, data_num)
            dma.disable_channel(dma_channel)
            scope007001.adc_measure_upload_disable()

            if result == 0:
                _len = 0
                    while data_num >= _len + 3:
                    code = data[_len + 0] | data[_len + 1] << 8 |
                            data[_len+2] << 16 | data[_len + 3] << 24
                    channel = code & 0x7
                    value = float((code>>14) & 0x3FFFF) / pow(2,17) * 10
                    print("chanel:%d, data:%f " % (channel, value))
                    _len = _len + 4
            else:
                print('error_code: %d' % (result))

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-LWFV-5-010"]

    def __init__(self, i2c=None, adc=None, xadc=None, adc_signal_meter=None,
                 ac_signal_meter=None, fsk_signal_meter=None,
                 ask_code=None, fsk_decode=None,
                 adc_ctrl_pin_0=None, adc_ctrl_pin_1=None,
                 fsk_ctrl_pin=None, fsk_cic_ctrl_pin=None,
                 adc_filter_pin_0=None, adc_filter_pin_1=None,
                 adc_filter_pin_2=None, ipcore=None):

        super(Scope007001, self).__init__(i2c, adc, xadc, adc_signal_meter,
                                          ac_signal_meter, fsk_signal_meter,
                                          ask_code, fsk_decode,
                                          adc_ctrl_pin_0, adc_ctrl_pin_1,
                                          fsk_ctrl_pin, fsk_cic_ctrl_pin,
                                          adc_filter_pin_0, adc_filter_pin_1,
                                          adc_filter_pin_2, ipcore,
                                          eeprom_devaddr=BladeDef.EEPROM_DEV_ADDR)
