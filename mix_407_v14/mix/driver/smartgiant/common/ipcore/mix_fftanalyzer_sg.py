# -*- coding: utf-8 -*-
from __future__ import division
import math
from time import sleep
from time import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator

__author__ = "Zhangsong Deng"
__version__ = "1.2"


class MIXFftAnalyzerSGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXFftAnalyzerSGDef:
    VERSION_REGISTER = 0x00
    MODULE_EN_REGISTER = 0x10
    FFT_START_REGISTER = 0x13
    FFT_STATE_REGISTER = 0x14
    DEC_PARAM_CFG_REGISTER = 0x15
    DEC_PARAM_VALUE_REGISTER = 0x16
    DEC_CTRL_REGISTER = 0x17
    FFT_RAM_RD_REGISTER = 0x80
    FFT_RAM_DCNT_REGISTER = 0x84

    REG_SIZE = 65536

    FFT_READY_STATE = 0x01
    FFT_BUSY_STATE = 0x00
    FFT_START = 0x01
    DECIMATE_PARAMETER_ENABLE = 0x01
    DECIMATE_PARAMETER_DISABLE = 0x00

    DECIMATION_MIN = 0x1
    DECIMATION_MAX = 0xFF
    MEASURE_INTERVAL_S = 0.01
    MEASURE_TIME_OUT_S = 3
    HARMONIC_COUNT_MIN = 1
    HARMONIC_COUNT_MAX = 10
    SAMPLE_RATE_MAX = 125000000
    BAND_WIDTH_MAX = 2000000

    FREQ_CALCULATE_CONST = 0.5
    FFT_RAM_RD_BYTE = 4
    FFT_VALID_DATA_COUNT = 1
    FFT_POW_IGNORE_BYTE = 8
    THDN_DB_AGLORITHM_CONST = 10
    THD_DB_AGLORITHM_CONST = 10
    # this is defined by fpga
    BEST_BANDWIDTH_FOR_THDN = 20000  # Hz

    ALPHA_COEFFICIENT_1 = 2.95494514
    ALPHA_COEFFICIENT_2 = 0.17671943
    ALPHA_COEFFICIENT_3 = 0.09230694
    NUTTAL_COEFFICIENT_1 = 3.20976143
    NUTTAL_COEFFICIENT_2 = 0.9187393
    NUTTAL_COEFFICIENT_3 = 0.14734229

    FFT_POINT_NUMBER_16K = 16384
    FFT_POINT_NUMBER_8K = 8192
    ENELOPE_4 = 4
    ENELOPE_8 = 8
    NOISEFLOOR_COEFFICIENT = 2.02376242639988


class MIXFftAnalyzerSGDataDef():
    def __init__(self, k1_index, k1_data, k2_index, k2_data):
        self.k1_index = k1_index
        self.k1_data = k1_data
        self.k2_index = k2_index
        self.k2_data = k2_data


class MIXFftAnalyzerSGNuttallDef():
    def __init__(self, beta, alpha, nuttall):
        self.beta = beta
        self.alpha = alpha
        self.nuttall = nuttall


class MIXFftAnalyzerSG(object):
    '''
    MIX FFT Analyzer module API class. This module can measure amplitude, frequency, THD+N, THD.

    ClassType = FFTAnalyzer

    Args:
        axi4_bus:        instance(AXI4LiteBus)/string/None,  AXI4lite bus instance, or dev path;
                                                             if None, will create emulator object.
        fft_data_cnt:    int/None,  get fft absolute data count,
                                    if None, with get count from register.

    Examples:
        fft_analyzer = MIXFftAnalyzerSG('/dev/MIX_FFT_Analyzer_0')

    '''

    rpc_public_api = ['enable', 'disable', 'enable_upload', 'disable_upload',
                      'analyze_config', 'analyze', 'get_vpp', 'get_frequency',
                      'get_vpp_by_freq', 'get_thdn', 'get_thd']

    def __init__(self, axi4_bus=None, fft_data_cnt=None, fft_point_number=MIXFftAnalyzerSGDef.FFT_POINT_NUMBER_8K):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator("axi4_mix_fftanalyzer_sg_emulator",
                                                MIXFftAnalyzerSGDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXFftAnalyzerSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.dev_name = self.axi4_bus._dev_name

        # for measure configuration
        self.sample_rate = 0
        self.freq_resolution = 0
        self.bandwidth_index = 0
        self.harmonic_count = 5
        self.freq_point = 1000
        self.fft_point_number = fft_point_number
        self.fft_point_number_half = int(self.fft_point_number / 2)
        if self.fft_point_number == MIXFftAnalyzerSGDef.FFT_POINT_NUMBER_8K:
            self.envelope = MIXFftAnalyzerSGDef.ENELOPE_4
        elif self.fft_point_number == MIXFftAnalyzerSGDef.FFT_POINT_NUMBER_16K:
            self.envelope = MIXFftAnalyzerSGDef.ENELOPE_8

        # for measure result
        self._fft_data_cnt = fft_data_cnt
        self._vpp_by_freq = 0
        self._frequency = 0
        self._vpp = 0
        self._thdn = 0
        self._thd = 0

    def enable(self):
        '''
        MIXFftAnalyzerSG module enable function when you first use.

        Other measurement related interfaces can be used only after this module enabled.

        Returns:
            None.

        Examples:
            fft_analyzer.enable()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, 1)
        # set bit0 of the 0x10 register to 1
        rd_data[0] = rd_data[0] | 0x01
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, rd_data)

    def disable(self):
        '''
        MIXFftAnalyzerSG module disable function.

        Returns:
            None.

        Examples:
            fft_analyzer.disable()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, 1)
        # set bit0 of the 0x10 register to 0
        rd_data[0] = rd_data[0] & 0xFE
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, rd_data)

    def enable_upload(self):
        '''
        MIXFftAnalyzerSG module enable data upload.

        If you want to upload the data of ADC when doing measurement,
        call this function before. Data will be uploading when doing measurement.

        Returns:
            None.

        Examples:
            fft_analyzer.enable_upload()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, 1)
        # set bit1 of the 0x10 register to 1
        rd_data[0] = rd_data[0] | 0x02
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, rd_data)

    def disable_upload(self):
        '''
        MIXFftAnalyzerSG module disable data upload.

        Close data upload. This function doesn't affect normal measurement.

        Returns:
            None.

        Examples:
            fft_analyzer.disable_upload()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, 1)
        # set bit1 of the 0x10 register to 0
        rd_data[0] = rd_data[0] & 0xFD
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.MODULE_EN_REGISTER, rd_data)

    def analyze_config(self, sample_rate, decimation_type, bandwidth='auto', harmonic_count=None, freq_point=None):
        '''
        MIXFftAnalyzerSG module measurement config. Set parameter at first when you start doing FFT.

        Args:
            bandwidth:       int/string,       FFT calculation bandwidth limit, must smaller than half of sample_rate,
                                               unit is Hz. Eg. 20000. If 'auto' given, bandwidth will be automatically
                                               adjust based on base frequency.
            sample_rate:     int, [0~125000000], Sample rate of your ADC device, unit is Hz. Eg. 192000.
            decimation_type: int, [1~255],     Config 0x15 register. When 0xff given, IP will set decimation auto
            harmonic_count:  int/None, [1~10]  The harmonic count of signal, default is None will not do calculate.
            freq_point:      int/None,         Specified frequency for calculating amplitude at this special frequency,
                                               default is None will not do this.

        Raises:
            MIXFftAnalyzerSGException:          Raise an Exception when get FFT data from ADC timeout.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff)

        '''
        assert bandwidth == 'auto' or (bandwidth >= 0 and bandwidth <= MIXFftAnalyzerSGDef.BAND_WIDTH_MAX)
        assert isinstance(sample_rate, int)
        assert sample_rate >= 0 and sample_rate <= MIXFftAnalyzerSGDef.SAMPLE_RATE_MAX
        assert isinstance(decimation_type, int)
        assert decimation_type >= MIXFftAnalyzerSGDef.DECIMATION_MIN
        assert decimation_type <= MIXFftAnalyzerSGDef.DECIMATION_MAX

        if harmonic_count:
            assert isinstance(harmonic_count, int)
            assert harmonic_count >= MIXFftAnalyzerSGDef.HARMONIC_COUNT_MIN
            assert harmonic_count <= MIXFftAnalyzerSGDef.HARMONIC_COUNT_MAX
        if freq_point:
            assert isinstance(freq_point, int)

        self.harmonic_count = harmonic_count
        self.freq_point = freq_point

        # config decimation and enable decimate parameter
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.DEC_PARAM_CFG_REGISTER, [decimation_type])
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.DEC_CTRL_REGISTER,
                                     [MIXFftAnalyzerSGDef.DECIMATE_PARAMETER_ENABLE])

        rd_data = [0x00]
        timeout = 0
        start_time = time()
        # check is decimate parameter is enable
        while ((rd_data[0] == MIXFftAnalyzerSGDef.DECIMATE_PARAMETER_DISABLE) and
               timeout < MIXFftAnalyzerSGDef.MEASURE_TIME_OUT_S):
            # check interval
            sleep(MIXFftAnalyzerSGDef.MEASURE_INTERVAL_S)
            rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.DEC_CTRL_REGISTER, 1)
            timeout = time() - start_time

        if timeout > MIXFftAnalyzerSGDef.MEASURE_TIME_OUT_S:
            raise MIXFftAnalyzerSGException(self.dev_name, 'Wait for estimate signal frequency timeout')

        # get current active decimate parameter
        rd_data = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.DEC_PARAM_VALUE_REGISTER, 1)
        if 0 == rd_data[0]:
            raise MIXFftAnalyzerSGException(self.dev_name, "The divisor is equal to 0")
        self.decimation = rd_data[0]
        # calculate true sample rate
        self.sample_rate = sample_rate / rd_data[0]
        # calculate frequency resolution
        self.freq_resolution = sample_rate / (self.fft_point_number * rd_data[0])
        # calculate bandwidth index by bandwidth in frequency domain
        if bandwidth == 'auto':
            self.bandwidth_index = 'auto'
        else:
            self.bandwidth_index = int(bandwidth / self.freq_resolution)

    def analyze(self):
        '''
        Start FFT analyze.

        Before analysis, make sure module has enabled, and config measurement parameters.
        This function will calculate amplitude, frequency, THD, THD+N, amplitude at specified frequency domain.

        Returns:
            None.

        Raises:
            MIXFftAnalyzerSGException:  Raise an Exception when get fft data from ADC timeout,
                                        , data counts equal to 0 or illegal mathematical operation.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()

        '''
        # Set the FFT transform to busy and start the conversion
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.FFT_STATE_REGISTER, [MIXFftAnalyzerSGDef.FFT_BUSY_STATE])
        self.axi4_bus.write_8bit_inc(MIXFftAnalyzerSGDef.FFT_START_REGISTER, [MIXFftAnalyzerSGDef.FFT_START])

        fft_state = [0x00]
        timeout = 0
        start_time = time()
        # check FFT transform is complete or transform timeout
        while (fft_state[0] == MIXFftAnalyzerSGDef.FFT_BUSY_STATE and
               timeout < MIXFftAnalyzerSGDef.MEASURE_TIME_OUT_S):
            sleep(MIXFftAnalyzerSGDef.MEASURE_INTERVAL_S)
            fft_state = self.axi4_bus.read_8bit_inc(MIXFftAnalyzerSGDef.FFT_STATE_REGISTER, 1)
            timeout = time() - start_time
            if timeout > MIXFftAnalyzerSGDef.MEASURE_TIME_OUT_S:
                raise MIXFftAnalyzerSGException(self.dev_name, 'wait for FFT calculate timeout')

        fft_power_data = []
        # get FFT absolute data counts
        if self._fft_data_cnt:
            fft_data_cnt = self._fft_data_cnt
        else:
            fft_data_cnt = self.axi4_bus.read_32bit_inc(MIXFftAnalyzerSGDef.FFT_RAM_DCNT_REGISTER, 1)[0]

        for i in range(0, int(fft_data_cnt / 2)):
            # The valid data of the FFT is 6 bytes, but FFT_RAM_RD register is 4 bytes. So read the FIFO twice.
            read_data = self.axi4_bus.read_32bit_fix(MIXFftAnalyzerSGDef.FFT_RAM_RD_REGISTER,
                                                     MIXFftAnalyzerSGDef.FFT_VALID_DATA_COUNT)
            read_data += self.axi4_bus.read_32bit_fix(MIXFftAnalyzerSGDef.FFT_RAM_RD_REGISTER,
                                                      MIXFftAnalyzerSGDef.FFT_VALID_DATA_COUNT)
            # FFT data conbined with first 6 byte data, raw data is a 32bit value
            fft_power_data.append(read_data[0] | read_data[1] << 32)

        # if the waveform has DC component, need to remove the influence DC component,
        # and the first 5 point is about DC component
        fft_power_data[:5] = [0, 0, 0, 0, 0]
        if 0 == len(fft_power_data):
            raise MIXFftAnalyzerSGException(self.dev_name, "FFT power data count is zero")

        refer_data = self._base_index_find(fft_power_data)
        self.refer_data = refer_data
        self.fft_power_data = fft_power_data

        self._calculate_signal()

    def set_harmonic_count(self, harmonic_count):
        '''
        MIXFftAnalyzerSG set harmonic count.

        Args:
            harmonic_count:  int/None, [1~10]  The harmonic count of signal, default is None will not do calculate.

        Examples:
            fft_analyzer.set_harmonic_count(2)

        '''
        assert isinstance(harmonic_count, int)
        assert harmonic_count >= MIXFftAnalyzerSGDef.HARMONIC_COUNT_MIN
        assert harmonic_count <= MIXFftAnalyzerSGDef.HARMONIC_COUNT_MAX
        self.harmonic_count = harmonic_count

    def get_noisefloor(self):
        '''
        MIXFftAnalyzerSG get noisefloor.

        Returns:
            float, value, unit V,  Result of signal's noisefloor.

        '''
        if self.bandwidth_index == 'auto':
            bandwidth = MIXFftAnalyzerSGDef.BEST_BANDWIDTH_FOR_THDN / self.decimation
            bandwidth_index = int(bandwidth / self.freq_resolution)
            if bandwidth_index > self.fft_point_number_half:
                bandwidth_index = self.fft_point_number_half
        else:
            bandwidth_index = self.bandwidth_index

        all_power = sum(self.fft_power_data[MIXFftAnalyzerSGDef.FFT_POW_IGNORE_BYTE: bandwidth_index])
        noisefloor = ((all_power ** 0.5) / self.fft_point_number / self.fft_point_number_half /
                      (2 ** 0.5) * MIXFftAnalyzerSGDef.NOISEFLOOR_COEFFICIENT)
        return noisefloor

    def get_vpp(self):
        '''
        Signal's vpp calculate result.

        Returns:
            float, value, unit V, Result of signal's amplitude.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()
            print fft_analyzer.get_vpp()

        '''
        return self._vpp

    def get_frequency(self):
        '''
        Signal's frequency calculate result.

        Returns:
            float, value, unit Hz,  Result of signal's frequency.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()
            print fft_analyzer.get_frequency()

        '''
        return self._frequency

    def get_vpp_by_freq(self):
        '''
        Result of vpp in specifical frequency whose desired at frequency domain.

        Returns:
            float, value, unit V, Amplitude value.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()
            print fft_analyzer.get_vpp_by_freq()

        '''
        if self.freq_point:
            self._calculate_vpp_by_freq()
        return self._vpp_by_freq

    def get_thdn(self):
        '''
        THD+N calculate result.

        Returns:
            float, value, unit dB, Value of THD+N.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()
            print fft_analyzer.get_thdn()

        '''
        self._calculate_thdn()
        return self._thdn

    def get_thd(self):
        '''
        THD calculate result.

        Returns:
            float, value, unit dB,Value of THD.

        Examples:
            fft_analyzer.disable()
            fft_analyzer.enable()
            fft_analyzer.analyze_config(20000, 192000, 0xff, 5)
            fft_analyzer.analyze()
            print fft_analyzer.get_thd()

        '''
        if self.harmonic_count:
            self._calculate_thd()
        return self._thd

    def _calculate_signal(self):
        '''
        Fundamental wave frequency and ampvpplitude value calculate. This function only use in this module.

        Returns:
            None.

        '''
        nuttall_data = self._correction_polynomial(self.refer_data.k1_data, self.refer_data.k2_data)
        self._vpp = nuttall_data.nuttall / self.fft_point_number_half
        # f = (0.5 + α + k1) * (Fs / 8192)
        self._frequency = (MIXFftAnalyzerSGDef.FREQ_CALCULATE_CONST + nuttall_data.alpha + self.refer_data.k1_index) * \
            (self.sample_rate / self.fft_point_number)

    def _calculate_vpp_by_freq(self):
        '''
        Vpp value calculate in specific frequency. This function only use in this module.

        Returns:
            None.

        '''
        # find the index of the specified frequency on frequency domain
        k1_index = int(self.freq_point / self.freq_resolution)
        k2_index = k1_index + 1
        k1_data = self.fft_power_data[k1_index]
        k2_data = self.fft_power_data[k2_index]
        nuttall_data = self._correction_polynomial(k1_data, k2_data)
        self._vpp_by_freq = nuttall_data.nuttall / self.fft_point_number_half

    def _calculate_thdn(self):
        '''
        THD+N calculate. This function only use in this module.

        Returns:
            None.

        '''
        # each harmonic power's calculate
        fundamental_power = sum(self.fft_power_data[self.refer_data.k1_index - self.envelope:
                                                    self.refer_data.k2_index + self.envelope])
        if 0 == fundamental_power:
            raise MIXFftAnalyzerSGException(self.dev_name, "The divisor is equal to 0")
        if self.bandwidth_index == 'auto':
            # when bandwidth is auto, best bandwidth is 20000 / decimation
            bandwidth = MIXFftAnalyzerSGDef.BEST_BANDWIDTH_FOR_THDN / self.decimation
            bandwidth_index = int(bandwidth / self.freq_resolution)
            if bandwidth_index > self.fft_point_number_half:
                bandwidth_index = self.fft_point_number_half
        else:
            bandwidth_index = self.bandwidth_index
        # Ignore the first 8 data
        # Nn = ∑((n=2)^(k1 - 3))(AA) + ∑((n=k2 + 3)^(k21 - 3))(AA) + ∑((n=k22 - 3)^(k31 - 3))(AA) +
        #      ∑((n=k32 - 3)^(k41 - 3))(AA) + ∑((n=42 - 3)^(k51 - 3))(AA) + ∑((n=52 - 3)^(N / 2))(AA), AA = An^2
        all_power = sum(self.fft_power_data[MIXFftAnalyzerSGDef.FFT_POW_IGNORE_BYTE: bandwidth_index])
        # index = (Nn - A1) / A1
        index = (all_power - fundamental_power) / fundamental_power
        if index <= 0:
            raise MIXFftAnalyzerSGException(self.dev_name, "Logarithmic index is less than 0 or equal to 0")

        # THD+N = 20 * log10((A2^2 + A3^2 + A4^2 + A5^2 + Nn^2) / A1^2), A(n) is the amplitude of each harmonic
        # the power to amplitude have a 2x relationship in dB algorithm
        self._thdn = MIXFftAnalyzerSGDef.THDN_DB_AGLORITHM_CONST * math.log10(index)

    def _calculate_thd(self):
        '''
        THD calculate. This function only use in this module.

        Returns:
            None.

        '''
        harmonic_power = []
        # harmonic number begin with 1 to 10, loop at lesst 1 times
        for i in range(1, self.harmonic_count + 1):
            freq_data = i * self._frequency
            # find the index of the specified frequency on frequency domain
            k1_index = int(freq_data / self.freq_resolution)
            k2_index = k1_index + 1
            power_temp = sum(self.fft_power_data[k1_index - self.envelope: k2_index +
                             self.envelope])
            harmonic_power.append(power_temp)

        if harmonic_power[0] == 0:
            raise MIXFftAnalyzerSGException(self.dev_name, "The divisor is equal to 0")

        # index = (Nn - A1) / A1
        index = (sum(harmonic_power) - harmonic_power[0]) / harmonic_power[0]
        if index <= 0:
            raise MIXFftAnalyzerSGException(self.dev_name, "Logarithmic index is less than 0 or equal to 0")

        # THD = 20 * log10((A2^2 + A3^2 + A4^2 + A5^2) / A1^2)
        # the power to amplitude have a 2x relationship in dB algorithm
        self._thd = MIXFftAnalyzerSGDef.THD_DB_AGLORITHM_CONST * math.log10(index)

    def _base_index_find(self, fft_power_data):
        '''
        Find base index. Intrinsic function, only use in this module after doing FFT.
        To find the point of maximum amplitude and the second largest point, record the serial number of these points.

        Returns:
            None.

        '''
        max_data = max(fft_power_data)
        max_index = fft_power_data.index(max_data)
        max_left_index = max_index - 1
        max_left_data = fft_power_data[max_left_index]
        max_right_index = max_index + 1
        max_right_data = fft_power_data[max_right_index]

        second_index = max_left_index if max_left_data > max_right_data else max_right_index
        second_data = max_left_data if max_left_data > max_right_data else max_right_data

        # the maximum amplitude list data's index, or second largest point
        k1_index = second_index if max_index > second_index else max_index
        # the maximum amplitude or second largest point
        k1_data = second_data if max_index > second_index else max_data
        # the maximum amplitude list data's index, or second largest point
        k2_index = max_index if max_index > second_index else second_index
        # the maximum amplitude or second largest point
        k2_data = max_data if max_index > second_index else second_data

        return MIXFftAnalyzerSGDataDef(k1_index, k1_data, k2_index, k2_data)

    def _correction_polynomial(self, k1_data, k2_data):
        '''
        The correction polynomial of Nuttall. Intrinsic function, only use in this module after doing FFT.

        Returns:
            float, value, The result of correction polynomial calculation.

        '''
        y1 = math.sqrt(k1_data)
        y2 = math.sqrt(k2_data)
        if y2 + y1 == 0:
            raise MIXFftAnalyzerSGException(self.dev_name, "The divisor is equal to 0")

        # interpolation algorithm
        # β = (y2 - y1) / (y2 + y1), y1 or y2 is the largest or second largest amplitude
        beta = (y2 - y1) / (y2 + y1)
        # α = 2.95494514 * β + 0.17671943 * β^3 + 0.09230694 * β^5
        alpha = MIXFftAnalyzerSGDef.ALPHA_COEFFICIENT_1 * \
            pow(beta, 1) + MIXFftAnalyzerSGDef.ALPHA_COEFFICIENT_2 * \
            pow(beta, 3) + MIXFftAnalyzerSGDef.ALPHA_COEFFICIENT_3 * pow(beta, 5)
        # A = (y1 + y2) * (3.20976143 + 0.9187393 * a^2 + 0.14734229 * a^4) / N, N is 8192 here
        temp = MIXFftAnalyzerSGDef.NUTTAL_COEFFICIENT_1 + MIXFftAnalyzerSGDef.NUTTAL_COEFFICIENT_2 * \
            pow(alpha, 2) + MIXFftAnalyzerSGDef.NUTTAL_COEFFICIENT_3 * pow(alpha, 4)
        nuttall = (y1 + y2) * temp / self.fft_point_number
        return MIXFftAnalyzerSGNuttallDef(beta, alpha, nuttall)
