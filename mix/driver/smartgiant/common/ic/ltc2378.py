# -*- coding: UTF-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_adc_emulator import PLSPIADCEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.2'


class LTC2378Def:
    FFT_VPP_MAX = 0.99999
    FFT_VPP_MIN = 0.0

    METER_VPP_MAX = 1.99998
    METER_VPP_MIN = 0

    METER_REG_SIZE = 1024
    ADC_REG_SIZE = 256
    AUDIO_REG_SIZE = 65536
    SAMPLE_RATE = 1000
    SMAPLE_TIME = 0xFFFFFFFF
    PAYLOAD_WIDTH = 4
    DECIMATION_TYPE = 'auto'
    UPFRAME_MODE = 'DEBUG'
    MAX_SAMPLE_RATE = 1000000  # 1Msps


class LTC2378Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class LTC2378(object):
    '''
    LTC2378 class provide function to measure rms average amplitude max min voltage thdn

    ClassType = ADC

    Args:
        meter_dev:       instance(MIXSignalMeterSG)/None,   Ipcore of signal meter device.
        bus_dev:         instance(QSPI)/None,            Ipcore of spi adc device.
        audio_dev:       instance(MIXFftAnalyzerSG)/None, Ipcore of audio analyzer device.
        adc_volt_range:  [-4096, 4096]/[-5000, 5000],    Set voltage range.

    Examples:
        LTC2378(meter_dev, bus_dev, audio_dev, adc_volt_range)

    '''

    def __init__(self, meter_dev, bus_dev, audio_dev, adc_volt_range):
        if audio_dev is None and bus_dev is None and meter_dev is None:
            self.meter = MIXSignalMeterSGEmulator(
                'mix_signalmeter_sg_emulator', LTC2378Def.METER_REG_SIZE)
            self.spi_adc = PLSPIADCEmulator(
                'pl_spi_adc_emulator', LTC2378Def.ADC_REG_SIZE)
            self.audio = MIXFftAnalyzerSGEmulator('mix_fftanalyzer_sg_emulator')
        else:
            self.audio = audio_dev
            self.spi_adc = bus_dev
            self.meter = meter_dev

        self.sample_rate = LTC2378Def.SAMPLE_RATE
        self.sample_time = LTC2378Def.SMAPLE_TIME
        self.payload_width = LTC2378Def.PAYLOAD_WIDTH
        self.decimation_type = LTC2378Def.DECIMATION_TYPE
        self.upframe_mode = LTC2378Def.UPFRAME_MODE

        # signal meter calibration formula
        self.meter_vpp_k = (adc_volt_range[1] - adc_volt_range[0]) \
            / (LTC2378Def.METER_VPP_MAX - LTC2378Def.METER_VPP_MIN)
        self.meter_vpp_b = (adc_volt_range[1] - adc_volt_range[0]) - self.meter_vpp_k * LTC2378Def.METER_VPP_MAX

        # FFT calibration formula
        self.fft_vpp_k = (adc_volt_range[1] - adc_volt_range[0]) / (LTC2378Def.FFT_VPP_MAX - LTC2378Def.FFT_VPP_MIN)
        self.fft_vpp_b = (adc_volt_range[1] - adc_volt_range[0]) - self.fft_vpp_k * LTC2378Def.FFT_VPP_MAX

    def measure_rms_average_amplitude_max_min(self, sample_rate, sample_time,
                                              upload_adc_data,
                                              sample_interval, upframe_mode):
        '''
        LTC2378 class provide function to measure rms average amplitude max min

        Args:
            sample_rate:     int, unit Hz.
            sample_time:     int, [1~0xFFFFFFFF], unit ms.
            upload_adc_data: string, ['off', 'on'], if upload is 'on' , then upload the raw data from ADC to DMA.
                                                    else disable the function.
            sample_interval: int, unit ms, less sample time.
            upframe_mode:    string, ['DEBUG', 'BYPASS'], choose mode.

        Returns:
            dict, {"rms": value, "avg": value, "vpp": value, "max": value, "min": value}, unit mV,
                  ret.rms,ret.average,ret.amp,ret.max,ret.min.

        Examples:
            ret = LTC2378.measure_rms_average_amplitude_max_min(256000, 1000, 'on', 500, 'DEBUG')

        '''
        assert sample_rate in range(1, LTC2378Def.MAX_SAMPLE_RATE + 1)
        assert sample_time > 0
        assert upload_adc_data in ("on", "off")
        assert 0 < sample_interval <= sample_time
        assert upframe_mode in ("DEBUG", "BYPASS")

        self.sample_rate = sample_rate
        self.sample_time = sample_time
        self.upload_raw_adc = upload_adc_data
        self.sample_interval = sample_interval
        self.upframe_mode = upframe_mode

        if self.spi_adc is not None:
            self.spi_adc.open()
            self.spi_adc.set_sample_rate(self.sample_rate)

        if self.upload_raw_adc == 'on':
            self.meter.enable_upframe(self.upframe_mode)
        else:
            self.meter.disable_upframe()

        self.meter.open()
        self.meter.set_vpp_interval(self.sample_interval)
        self.meter.start_measure(self.sample_time, self.sample_rate)

        result = self.meter.vpp()
        vpp = result[2] * self.meter_vpp_k + self.meter_vpp_b
        max = result[0] * self.meter_vpp_k + self.meter_vpp_b
        min = result[1] * self.meter_vpp_k + self.meter_vpp_b
        result = self.meter.rms()
        rms = result[0] * self.meter_vpp_k + self.meter_vpp_b
        average = result[1] * self.meter_vpp_k + self.meter_vpp_b

        return {"rms": rms, "avg": average, "vpp": vpp, "max": max, "min": min}

    def read_volt(self, channel=0):
        '''
        LTC2378 read the adc voltage

        Args:
            channel: int, [0], channel must be 0.

        Returns:
            float, value, unit mV.

        Examples:
            voltage = ltc2378.read_volt(0)

        '''
        assert channel == 0
        reg_data = 0

        self.spi_adc.open()
        self.spi_adc.set_sample_rate(self.sample_rate)
        reg_data = self.spi_adc.get_sample_data()
        voltage = reg_data * self.meter_vpp_k + self.meter_vpp_b
        return voltage

    def measure_thdn(self, bandwidth_hz=20000, sample_rate=192000,
                     decimation_type=0xFF, upload='off',
                     harmonic_count=8):
        '''
        LTC2378 class provide function to measure thdn

        Args:
            bandwidth_hz:    int, [0~20000], default 20000, unit Hz.
            sample_rate:     int, [0~1000000, default 192000, unit sps.
            decimation_type: int, [1~255], default 0xFF, it means auto decimation.

            upload:          string, ['off', 'on'], default 'off', if upload is 'on' ,
                                     then upload the raw data from ADC to DMA, else disable the function.
            harmonic_count:  int, [1~10]|None, Default 8, if it is None, it will not do calculate.

        Returns:
            dict, {"freq": value, "vpp": value, "thd": value, "thdn": value},
                  ret.freq,unit is Hz,ret.thdn,unit is dB,ret.thd,unit is dB, ret.vpp,unit is mV.

        Raises:
            LTC2378Exception:open audio upload function fail!

        Examples:
            ret = LTC2378.measure_thdn('auto', 192000, 0xFF, 8)

        '''
        assert bandwidth_hz in range(1, 20001) or bandwidth_hz == "auto"
        assert 0 < sample_rate <= LTC2378Def.MAX_SAMPLE_RATE
        assert decimation_type in range(1, 256)
        assert upload in ("on", "off")
        assert harmonic_count in range(1, 11) or harmonic_count is None
        signal_result = 0
        freq = 0
        vpp = 0
        thd = 0
        thdn = 0
        self.sample_rate = sample_rate
        self.bandwidth_hz = bandwidth_hz
        self.decimation_type = decimation_type

        upload = upload.lower()

        self.spi_adc.close()
        self.spi_adc.open()
        self.spi_adc.set_sample_rate(self.sample_rate)
        self.audio.disable_upload()
        if upload == "on":
            self.audio.enable_upload()
        elif upload == "off":
            self.audio.disable_upload()
        else:
            raise LTC2378Exception(self.audio, "open audio upload function fail!")

        self.audio.disable()
        self.audio.enable()
        self.audio.analyze_config(self.sample_rate, self.decimation_type, self.bandwidth_hz, harmonic_count)
        self.audio.analyze()
        signal_result = self.audio.get_vpp()
        vpp = signal_result * self.fft_vpp_k + self.fft_vpp_b
        freq = self.audio.get_frequency()
        thd = self.audio.get_thd()
        thdn = self.audio.get_thdn()
        return {"freq": freq, "vpp": vpp, "thd": thd, "thdn": thdn}
