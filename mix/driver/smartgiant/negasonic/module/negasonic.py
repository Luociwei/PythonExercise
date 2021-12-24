# -*- coding: utf-8 -*-

import time
import struct
import math

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.pin import Pin
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_aut1_sg_r import MIXAUT1SGR
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.module.mix_board import BoardArgCheckError


__author__ = "Zhangsong Deng"
__version__ = "1.0"


negasonic_calibration_info = {
    "OUTPUT": {
        "level1": {"unit_index": 0, "limit": (10, "mV")},
        "level2": {"unit_index": 1, "limit": (100, "mV")},
        "level3": {"unit_index": 2, "limit": (1000, "mV")},
        "level4": {"unit_index": 3, "limit": (2000, "mV")},
    },
    "RMS": {
        "level1": {"unit_index": 4, "limit": (100, "mV")},
        "level2": {"unit_index": 5, "limit": (1000, "mV")},
        "level3": {"unit_index": 6, "limit": (2000, "mV")},
    }
}

negasonic_range_table = {
    "OUTPUT": 0,
    "RMS": 1
}


class NegasonicDef():
    ANALYZER_REG_SIZE = 256
    SIGNALSOURCE_REG_SIZE = 256
    MIXAUT1_REG_SIZE = 0x8000
    GPIO_EMULATOR_REG_SIZE = 256
    EEPROM_I2C_ADDR = 0x53
    SENSOR_I2C_ADDR = 0x4B

    DELAY_S = 0.001

    MAX_SAMPLING_RATE = 192000
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)
    SIGNAL_ALWAYS_OUTPUT = 0xffffff
    # output signal range defined in HW Spec
    OUTPUT_SIGNAL_DUTY = 0.5
    OUTPUT_FREQ_MIN = 10
    OUTPUT_FREQ_MAX = 50000
    OUTPUT_RMS_MIN = 0
    OUTPUT_RMS_MAX = 2300  # mVrms
    # this can be found in HW spec
    # max rms is 2000 mVrms
    AUDIO_ANALYZER_VREF = 2 * math.sqrt(2) * 2000
    # max rms is 2300 mVrms
    SIGNAL_SOURCE_VREF = 2 * math.sqrt(2) * OUTPUT_RMS_MAX
    OUTPUT_WAVE = "sine"
    VPP_2_SCALE_RATIO = 0.999
    MEASURE_CAL_ITEM = "RMS"
    OUTPUT_CAL_ITEM = "OUTPUT"

    CAL_DATA_LEN = 9
    WRITE_CAL_DATA_PACK_FORMAT = "2fB"
    WRITE_CAL_DATA_UNPACK_FORMAT = "9B"

    READ_CAL_BYTE = 9
    READ_CAL_DATA_PACK_FORMAT = "9B"
    READ_CAL_DATA_UNPACK_FORMAT = "2fB"

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9


class NegasonicException(Exception):
    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class NegasonicBase(MIXBoard):
    '''
    Base class of Negasonic and NegasonicCompatible,Providing common Negasonic methods.

    Args:
        i2c:              instance(I2C), which is used to access eeprom and nct75, if not given,
                                         will create eeprom and nct75 emulator.
        analyzer:         instance(FFTAnalyzer)/string, if not given, will create emulator.
        signalsource:     instance(MIXSignalSourceSG)/string, if not given, will create emulator.
        adc_rst_pin:      instance(GPIO), used to reset ADC CS5361. Setting low to reset CS5361,
                                          seting high to enable CS5361.
        i2s_rx_en_pin:    instance(GPIO), used to enable fft analyzer module.
        dac_rst_pin:      instance(GPIO), used to reset IIS of the CS4398.
        i2s_tx_en_pin:    instance(GPIO), used to enable signal source module.
        sample_rate:      int, unit Hz, default 192000, used to config the CS5361 or CS4398.
        ipcore:               instance(UART), aggregated MIXAUT1SGR wrapper.
        eeprom_dev_addr:  int,            Eeprom device address.
        sensor_dev_addr:  int,            NCT75 device address.

    '''

    rpc_public_api = ['module_init', 'enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output'] + MIXBoard.rpc_public_api

    def __init__(
            self, i2c, analyzer=None, signal_source=None, adc_rst_pin=None, i2s_rx_en_pin=None,
            dac_rst_pin=None, i2s_tx_en_pin=None, sample_rate=192000, ipcore=None,
            eeprom_dev_addr=NegasonicDef.EEPROM_I2C_ADDR, sensor_dev_addr=NegasonicDef.SENSOR_I2C_ADDR,
            cal_info=None, range_table=None):

        assert sample_rate > 0 and sample_rate <= NegasonicDef.MAX_SAMPLING_RATE
        self.i2c = i2c
        if self.i2c is None:
            self.eeprom = EepromEmulator("cat24cxx_emulator")
            self.nct75 = NCT75Emulator("nct75_emulator")
        else:
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.nct75 = NCT75(sensor_dev_addr, i2c)

        super(NegasonicBase, self).__init__(self.eeprom, self.nct75,
                                            cal_table=cal_info, range_table=range_table)

        if (ipcore and not analyzer and not signal_source):
            if isinstance(ipcore, basestring):
                axi4 = AXI4LiteBus(ipcore, NegasonicDef.MIXAUT1_REG_SIZE)
                self.ipcore = MIXAUT1SGR(axi4)
            else:
                self.ipcore = ipcore
            self.analyzer = self.ipcore.analyzer
            self.signal_source = self.ipcore.signal_source
            self.adc_rst_pin = adc_rst_pin or Pin(self.ipcore.gpio, NegasonicDef.ADC_RESET_PIN)
            self.i2s_rx_en_pin = i2s_rx_en_pin or Pin(self.ipcore.gpio, NegasonicDef.I2S_RX_EN_PIN)
            self.dac_rst_pin = dac_rst_pin or Pin(self.ipcore.gpio, NegasonicDef.DAC_RESET_PIN)
            self.i2s_tx_en_pin = i2s_tx_en_pin or Pin(self.ipcore.gpio, NegasonicDef.I2S_TX_EN_PIN)
        elif (not ipcore and analyzer and signal_source):
            if isinstance(analyzer, basestring):
                axi4 = AXI4LiteBus(analyzer, NegasonicDef.ANALYZER_REG_SIZE)
                analyzer = MIXFftAnalyzerSG(axi4)
            else:
                self.analyzer = analyzer
            if isinstance(signal_source, basestring):
                axi4 = AXI4LiteBus(signal_source, NegasonicDef.SIGNALSOURCE_REG_SIZE)
                signal_source = MIXSignalSourceSG(axi4)
            else:
                self.signal_source = signal_source
            self.adc_rst_pin = adc_rst_pin
            self.i2s_rx_en_pin = i2s_rx_en_pin
            self.dac_rst_pin = dac_rst_pin
            self.i2s_tx_en_pin = i2s_tx_en_pin
        elif (not ipcore and not analyzer and not signal_source and not adc_rst_pin and
                not i2s_rx_en_pin and not dac_rst_pin and not i2s_tx_en_pin):
            self.analyzer = MIXFftAnalyzerSGEmulator("mix_fftanalyzer_sg_emulator")
            self.signal_source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.adc_rst_pin = Pin(None, NegasonicDef.ADC_RESET_PIN)
            self.i2s_rx_en_pin = Pin(None, NegasonicDef.I2S_RX_EN_PIN)
            self.dac_rst_pin = Pin(None, NegasonicDef.DAC_RESET_PIN)
            self.i2s_tx_en_pin = Pin(None, NegasonicDef.I2S_TX_EN_PIN)
        else:
            if ipcore:
                raise NegasonicException("parameter 'ipcore' can not be given at same time with 'analyzer', "
                                         "'signal_source', 'adc_rst_pin', 'i2s_rx_en_pin', "
                                         "'dac_rst_pin', 'i2s_tx_en_pin'")
            else:
                raise NegasonicException("parameter 'analyzer', 'signal_source', 'adc_rst_pin', "
                                         "'i2s_rx_en_pin', 'dac_rst_pin' and 'i2s_tx_en_pin'"
                                         " must be given at the same time")

        self.sample_rate = sample_rate

    def __del__(self):
        self.adc_rst_pin.set_level(0)
        self.i2s_rx_en_pin.set_level(0)
        self.dac_rst_pin.set_level(0)
        self.i2s_tx_en_pin.set_level(0)
        self.signal_source.close()

    def module_init(self):
        '''
        Negasonic init module, will reset dac/adc and i2s module.

        Returns:
            string, "done", api execution successful.

        Examples:
            negasonic.module_init()

        '''
        self.adc_rst_pin.set_dir('output')
        self.dac_rst_pin.set_dir('output')
        self.i2s_rx_en_pin.set_dir('output')
        self.i2s_tx_en_pin.set_dir('output')

        # reset ADC
        self.adc_rst_pin.set_level(0)
        time.sleep(NegasonicDef.DELAY_S)
        self.adc_rst_pin.set_level(1)

        # reset DAC
        self.dac_rst_pin.set_level(0)
        time.sleep(NegasonicDef.DELAY_S)
        self.dac_rst_pin.set_level(1)

        self.i2s_rx_en_pin.set_level(1)
        self.load_calibration()

        return "done"

    def enable_upload(self):
        '''
        Negasonic upoad mode open.

        Control audio upload data of ADC when doing measurement. It's not necessary
        enable upload when doing measurement. Note that data transfered into DMA is 32bit each data,
        but high 24bit data is valid. Low 8bit data is invalid. The data format is twos complement.

        Returns:
            string, "done", api execution successful.

        '''
        self.analyzer.enable_upload()
        return "done"

    def disable_upload(self):
        '''
        Negasonic upoad mode close. Close data upload doesn't influence to measure.

        Returns:
            string, "done", api execution successful.

        '''
        self.analyzer.disable_upload()
        return "done"

    def measure(self, bandwidth_hz, harmonic_num, decimation_type=0xFF):
        '''
        Negasonic measure signal's Vpp, RMS, THD+N, THD.

        Args:
            bandwidth_hz:    int, [24~95977], Measure signal's limit bandwidth, unit is Hz. The frequency of the
                                              signal should not be greater than half of the bandwidth.
            harmonic_num:    int, [2~10],     Use for measuring signal's THD.
            decimation_type: int, [1~255],    Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                              choose one suitable number.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value),
                  dict with vpp, freq, thd, thdn, rms.

        Examples:
            result = negasonic.measure(20000, 5, 0xff)
            print result.frequency, result.vpp, result.thdn, result.thd, result.rms

        '''
        assert bandwidth_hz == 'auto' or isinstance(bandwidth_hz, int)
        assert isinstance(harmonic_num, int) and harmonic_num > 0
        assert isinstance(decimation_type, int) and decimation_type > 0

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(self.sample_rate, decimation_type, bandwidth_hz, harmonic_num)
        self.analyzer.analyze()

        # calculate the actual vpp of HW by VREF
        vpp = self.analyzer.get_vpp() * NegasonicDef.AUDIO_ANALYZER_VREF
        # vpp = RMS * 2 * sqrt(2)
        rms = vpp / NegasonicDef.RMS_TO_VPP_RATIO

        rms = self.calibrate(NegasonicDef.MEASURE_CAL_ITEM, rms)
        vpp = rms * NegasonicDef.RMS_TO_VPP_RATIO

        result = dict()
        result["vpp"] = vpp
        result["freq"] = self.analyzer.get_frequency()
        result["thd"] = self.analyzer.get_thd()
        result["thdn"] = self.analyzer.get_thdn()
        result["rms"] = rms
        return result

    def enable_output(self, freq, rms):
        '''
        Negasonic output sine wave, differencial mode.

        Args:
            freq:    int, [10~50000], unit Hz, Ouput signal's frequency.
            rms:     float, [0~2300], unit mV, Ouput wave's RMS.

        Returns:
            string, "done", api execution successful.

        Examples:
            negasonic.enable_output(10000, 500)

        '''
        assert freq >= NegasonicDef.OUTPUT_FREQ_MIN
        assert freq <= NegasonicDef.OUTPUT_FREQ_MAX
        assert rms >= NegasonicDef.OUTPUT_RMS_MIN
        assert rms <= NegasonicDef.OUTPUT_RMS_MAX

        # enable I2S tx module
        self.i2s_tx_en_pin.set_level(1)

        self.signal_source.open()
        rms = self.calibrate(NegasonicDef.OUTPUT_CAL_ITEM, rms)
        # vpp = RMS * 2 * sqrt(2)
        vpp = rms * NegasonicDef.RMS_TO_VPP_RATIO
        # calculate vpp to vpp scale for FPGA
        vpp_scale = vpp * NegasonicDef.VPP_2_SCALE_RATIO / NegasonicDef.SIGNAL_SOURCE_VREF
        self.signal_source.set_signal_type(NegasonicDef.OUTPUT_WAVE)
        self.signal_source.set_signal_time(NegasonicDef.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.set_swg_paramter(self.sample_rate, freq, vpp_scale, NegasonicDef.OUTPUT_SIGNAL_DUTY)
        self.signal_source.output_signal()
        return "done"

    def disable_output(self):
        '''
        Negasonic close sine wave output.

        Returns:
            string, "done", api execution successful.

        Examples:
            negasonic.disable_output()

        '''
        self.signal_source.close()
        self.i2s_tx_en_pin.set_level(0)
        return "done"

    def legacy_write_calibration_cell(self, unit_index, gain, offset, threshold):
        '''
        MIXBoard calibration data write

        Args:
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.
            threshold:    float,  if value < threshold, use this calibration unit data.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.write_calibration_cel(0, 1.1, 0.1, 100)

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
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, use_flag)
        s = struct.Struct(NegasonicDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(NegasonicDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info["unit_start_addr"] + NegasonicDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return "done"

    def legacy_read_calibration_cell(self, unit_index):
        '''
        MIXBoard read calibration data

        Args:
            unit_index: int, calibration unit index.

        Returns:
            dict, {'gain': value, 'offset': value, 'threshold': value, 'is_use': value}.

        Examples:
            data = board.read_calibration_cel(0)
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
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = self.calibration_info["unit_start_addr"] + NegasonicDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, NegasonicDef.READ_CAL_BYTE)

        s = struct.Struct(NegasonicDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(NegasonicDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_item in negasonic_calibration_info:
            for level in negasonic_calibration_info[cal_item]:
                if unit_index == negasonic_calibration_info[cal_item][level]["unit_index"]:
                    threshold = negasonic_calibration_info[cal_item][level]["limit"][0]

        if self.calibration_info["use_flag"] != result[2]:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0, "is_use": True}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": threshold, "is_use": True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        MIXBoard erase calibration unit

        Returns:
            string, "done", api execution successful.

        Examples:
            board.erase_calibration_cell(0)

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        data = [0xff for i in range(9)]
        address = self.calibration_info["unit_start_addr"] + 9 * unit_index
        self.write_eeprom(address, data)
        return "done"


class Negasonic(NegasonicBase):
    '''
    Negasonic function class.

    compatible = ["GQQ-AUD002002-000"]

    The negasonic has a output sine(diffenencial mode) function and one measure channel.
    It can measure signal's frequency, vpp, THD+N, THD. If the input is a single-end signal, the vpp & RMS
    will be the half of themselves.
    Note:This class is legacy driver for normal boot.

    Args:
        i2c:              instance(I2C), which is used to access eeprom and nct75, if not given,
                                         will create eeprom and nct75 emulator.
        analyzer:         instance(FFTAnalyzer), if not given, will create emulator.
        signalsource:     instance(MIXSignalSourceSG), if not given, will create emulator.
        adc_rst_pin:      instance(GPIO), used to reset ADC CS5361. Setting low to reset CS5361,
                                          seting high to enable CS5361.
        i2s_rx_en_pin:    instance(GPIO), used to enable fft analyzer module.
        dac_rst_pin:      instance(GPIO), used to reset IIS of the CS4398.
        i2s_tx_en_pin:    instance(GPIO), used to enable signal source module.
        sample_rate:      int, unit Hz, default 192000, used to config the CS5361 or CS4398.
        ipcore:               instance(UART), aggregated MIXAUT1SGR wrapper.

    Examples:
        Example for using no-aggregated IP:
            analyzer = MIXFftAnalyzerSG('/dev/MIX_FftAnalyzer_0')
            signal_source = MIXSignalSourceSG('/dev/MIX_Signal_Source_0')
            gpio = PLGPIO('/dev/MIX_GPIO')
            adc_rst_pin = Pin(gpio, 2)
            i2s_rx_en_pin = Pin(gpio, 3)
            dac_rst_pin = Pin(gpio, 0)
            i2s_tx_en_pin = Pin(gpio, 1)
            i2c = I2C('/dev/i2c-1')
            sample_rate = 192000
            negasonic = Negasonic(i2c, analyzer, signal_source, adc_rst_pin, i2s_rx_en_pin, \
            dac_rst_pin, i2s_tx_en_pin, sample_rate)

        Example for using aggregated IP:
            aut1 = MIXAUT1SGR('/dev/MIX_AUT1_0')
            i2c = I2C('/dev/i2c-1')
            negasonic = Negasonic(i2c, ipcore=aut1)

        Example for measure, bandwith is 20000Hz, harmonic_num is 5:
            result = negasonic.measure(20000, 5)
            print("vpp={}, freq={}, thd={}, thdn={}, rms={}".format(result["vpp"], result["freq"], result["thd"],
                  result["thdn"], result["rms"]))

        Example for data upload:
            dma = Dma("/dev/MIX_DMA")

            dma.config_channel(0, 1024 * 1024)
            dma.enable_channel(0)
            negasonic.enable_upload()
            time.sleep(1)
            negasonic.disable_upload()
            data = dma.read_channel_all_data(0)
            dma.disable_channel(0)
            print(data)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-AUD002002-000"]

    def __init__(
            self, i2c, analyzer=None, signal_source=None, adc_rst_pin=None, i2s_rx_en_pin=None,
            dac_rst_pin=None, i2s_tx_en_pin=None,
            sample_rate=192000, ipcore=None):
        super(Negasonic, self).__init__(
            i2c, analyzer, signal_source, adc_rst_pin, i2s_rx_en_pin,
            dac_rst_pin, i2s_tx_en_pin, sample_rate, ipcore,
            NegasonicDef.EEPROM_I2C_ADDR, NegasonicDef.SENSOR_I2C_ADDR,
            negasonic_calibration_info, negasonic_range_table)
