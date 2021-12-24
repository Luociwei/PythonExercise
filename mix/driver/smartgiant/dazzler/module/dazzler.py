# -*- coding: utf-8 -*-

import time
import math

from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ipcore.mix_aut1_sg_r import MIXAUT1SGR
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator

__author__ = "zhiwei.deng"
__version__ = "1.0"


dazzler_calibration_info = {
    "OUTPUT": {
        "level1": {"unit_index": 0, 'limit': (10, 'mV')},
        "level2": {"unit_index": 1, 'limit': (100, 'mV')},
        "level3": {"unit_index": 2, 'limit': (1000, 'mV')},
        "level4": {"unit_index": 3, 'limit': (2000, 'mV')},
    },
    "RMS": {
        "level1": {"unit_index": 4, 'limit': (100, 'mV')},
        "level2": {"unit_index": 5, 'limit': (600, 'mV')},
        "level3": {"unit_index": 6, 'limit': (1000, 'mV')},
        "level4": {"unit_index": 7, 'limit': (4000, 'mV')},
    }
}

dazzler_range_table = {
    "OUTPUT": 0,
    "RMS": 1
}


class DazzlerDef():
    ANALYZER_EMULATOR_REG_SIZE = 65536
    SIGNALSOURCE_EMULATOR_REG_SIZE = 65536
    GPIO_EMULATOR_REG_SIZE = 256
    MIX_AUT1_REG_SIZE = 65535
    EEPROM_I2C_ADDR = 0x50
    SENSOR_I2C_ADDR = 0x48

    DELAY_S = 0.001

    MAX_SAMPLING_RATE = 192000
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)
    SIGNAL_ALWAYS_OUTPUT = 0xffffff
    # output signal range defined in HW Spec
    OUTPUT_SIGNAL_DUTY = 0.5
    OUTPUT_FREQ_MIN = 10
    OUTPUT_FREQ_MAX = 50000
    OUTPUT_RMS_MIN = 0
    OUTPUT_RMS_MAX = 2368.8  # mVrms
    # this can be found in HW spec
    # max rms is 3536 mVrms
    AUDIO_ANALYZER_VREF = 2 * math.sqrt(2) * 3536
    # max rms is 2368.8 mVrms
    SIGNAL_SOURCE_VREF = 2 * math.sqrt(2) * OUTPUT_RMS_MAX
    OUTPUT_WAVE = "sine"
    VPP_2_SCALE_RATIO = 0.999
    MEASURE_CAL_ITEM = "RMS"
    OUTPUT_CAL_ITEM = "OUTPUT"

    CAL_DATA_LEN = 13
    WRITE_CAL_DATA_PACK_FORMAT = "3fB"
    WRITE_CAL_DATA_UNPACK_FORMAT = "13B"

    READ_CAL_BYTE = 13
    READ_CAL_DATA_PACK_FORMAT = "13B"
    READ_CAL_DATA_UNPACK_FORMAT = "3fB"

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9


class DazzlerException(Exception):

    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class Dazzler(MIXBoard):

    '''
    Dazzler function class.

    compatible = ['GQQ-AUD001004-000']

    The dazzler has a output sine function and one measure channel.
    It can measure signal's frequency, vpp, THD+N, THD.

    Args:
        i2c:                 instance(I2C),                  which is used to access eeprom and nct75, if not given,
                                                             will create eeprom and nct75 emulator.
        adc_rst_pin:         instance(GPIO),                 used to reset ADC CS5361. Setting low to reset CS5361,
                                                             seting high to enable CS5361.
        i2s_rx_en_pin:       instance(GPIO),                 used to enable fft analyzer module.
        dac_rst_pin:         instance(GPIO),                 used to reset IIS of the CS4398.
        i2s_tx_en_pin:       instance(GPIO),                 used to enable signal source module.
        sample_rate:         int,                            Use to config the CS5361 or CS4398, unit is Hz,
                                                             default 192000.
        ipcore:              instance(MIXAUT1SGR),              aggregated MIXAUT1SGR wrapper.

    Examples:
        i2c = I2C('/dev/i2c-1')
        aut1 = MIXAUT1SGR('/dev/MIX_AUT1_0')
        dazzler = Dazzler(i2c, ipcore=aut1)

        Example for measure, bandwith is 20000Hz, harmonic_num is 5:
            result = dazzler.measure(20000, 5)
            print("vpp={}, freq={}, thd={}, thdn={}, rms={}".format(result["vpp"], result["freq"], result["thd"],
                  result["thdn"], result["rms"]))

        Example for data upload:
            dma = Dma("/dev/MIX_DMA")
            dma.config_channel(0, 1024 * 1024)
            dma.enable_channel(0)
            dazzler.enable_upload()
            time.sleep(1)
            dazzler.disable_upload()
            data = dma.read_channel_all_data(0)
            dma.disable_channel(0)
            print(data)

    '''
    compatible = ['GQQ-AUD001004-000']

    rpc_public_api = ['module_init', 'enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, adc_rst_pin=None, i2s_rx_en_pin=None,
                 dac_rst_pin=None, i2s_tx_en_pin=None,
                 sample_rate=192000, ipcore=None):
        assert sample_rate > 0 and sample_rate <= DazzlerDef.MAX_SAMPLING_RATE
        if i2c is None:
            self.eeprom = EepromEmulator("cat24cxx_emulator")
            self.nct75 = NCT75Emulator("nct75_emulator")
        else:
            self.eeprom = CAT24C32(DazzlerDef.EEPROM_I2C_ADDR, i2c)
            self.nct75 = NCT75(DazzlerDef.SENSOR_I2C_ADDR, i2c)

        MIXBoard.__init__(self, self.eeprom, self.nct75, cal_table=dazzler_calibration_info,
                          range_table=dazzler_range_table)

        if ipcore:
            if isinstance(ipcore, basestring):
                axi4 = AXI4LiteBus(ipcore, DazzlerDef.MIX_AUT1_REG_SIZE)
                self.ip = MIXAUT1SGR(axi4)
            else:
                self.ip = ipcore
            self.analyzer = self.ip.analyzer
            self.signal_source = self.ip.signal_source
            self.adc_rst_pin = adc_rst_pin or Pin(self.ip.gpio, DazzlerDef.ADC_RESET_PIN)
            self.i2s_rx_en_pin = i2s_rx_en_pin or Pin(self.ip.gpio, DazzlerDef.I2S_RX_EN_PIN)
            self.dac_rst_pin = dac_rst_pin or Pin(self.ip.gpio, DazzlerDef.DAC_RESET_PIN)
            self.i2s_tx_en_pin = i2s_tx_en_pin or Pin(self.ip.gpio, DazzlerDef.I2S_TX_EN_PIN)
        elif (not ipcore and not adc_rst_pin and not i2s_rx_en_pin and not dac_rst_pin and not i2s_tx_en_pin):
            self.analyzer = MIXFftAnalyzerSGEmulator("mix_fftanalyzer_sg_emulator")
            self.signal_source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.adc_rst_pin = Pin(None, DazzlerDef.ADC_RESET_PIN)
            self.i2s_rx_en_pin = Pin(None, DazzlerDef.I2S_RX_EN_PIN)
            self.dac_rst_pin = Pin(None, DazzlerDef.DAC_RESET_PIN)
            self.i2s_tx_en_pin = Pin(None, DazzlerDef.I2S_TX_EN_PIN)
        else:
            if ipcore:
                raise DazzlerException("parameter 'ipcore' can not be given at same time with 'analyzer', "
                                       "'signal_source', 'adc_rst_pin', 'i2s_rx_en_pin', "
                                       "'dac_rst_pin', 'i2s_tx_en_pin'")
            else:
                raise DazzlerException("parameter 'analyzer', 'signal_source', 'adc_rst_pin', "
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
        Dazzler init module, will reset dac/adc and i2s module.

        Returns:
            string, "done", api execution successful.

        '''
        self.adc_rst_pin.set_dir('output')
        self.dac_rst_pin.set_dir('output')
        self.i2s_rx_en_pin.set_dir('output')
        self.i2s_tx_en_pin.set_dir('output')

        # reset ADC
        self.adc_rst_pin.set_level(0)
        time.sleep(DazzlerDef.DELAY_S)
        self.adc_rst_pin.set_level(1)

        # reset DAC
        self.dac_rst_pin.set_level(0)
        time.sleep(DazzlerDef.DELAY_S)
        self.dac_rst_pin.set_level(1)

        self.i2s_rx_en_pin.set_level(1)

        self.load_calibration()

        return "done"

    def enable_upload(self):
        '''
        Dazzler upoad mode open.

        Control audio upload data of ADC when doing measurement.
        It's not necessary enable upload when doing measurement.
        Note that data transfered into DMA is 32bit each data, but high 24bit data is valid.
        Low 8bit data is invalid. The data format is twos complement.

        Returns:
            string, "done", api execution successful.
        '''
        self.analyzer.enable_upload()
        return "done"

    def disable_upload(self):
        '''
        Dazzler upoad mode close.

        Close data upload doesn't influence to measure.

        Returns:
            string, "done", api execution successful.
        '''
        self.analyzer.disable_upload()
        return "done"

    def measure(self, bandwidth_hz, harmonic_num, decimation_type=0xFF):
        '''
        Dazzler measure signal's Vpp, RMS, THD+N, THD.

        Args:
            bandwidth_hz:    int, [24~95977], Measure signal's limit bandwidth, unit is Hz. The frequency of the
                                              signal should not be greater than half of the bandwidth.
            harmonic_num:    int, [2-10], Use for measuring signal's THD.
            decimation_type: int, [1~255], Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                           choose one suitable number.

        Returns:
            dict, {"vpp":value, "freq":value, "thd":value, "thdn":value, "rms":value},
                  vpp, freq, thd, thdn, rms value.

        Examples:
            dazzler.measure(20000, 5, 0xff)
        '''
        assert bandwidth_hz == 'auto' or isinstance(bandwidth_hz, int)
        assert isinstance(harmonic_num, int) and harmonic_num > 0
        assert isinstance(decimation_type, int) and decimation_type > 0

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(self.sample_rate, decimation_type, bandwidth_hz, harmonic_num)
        self.analyzer.analyze()

        # calculate the actual vpp of HW by VREF
        vpp = self.analyzer.get_vpp() * DazzlerDef.AUDIO_ANALYZER_VREF
        # vpp = RMS * 2 * sqrt(2)
        rms = vpp / DazzlerDef.RMS_TO_VPP_RATIO

        rms = self.calibrate(DazzlerDef.MEASURE_CAL_ITEM, rms)
        vpp = rms * DazzlerDef.RMS_TO_VPP_RATIO

        result = dict()
        result["vpp"] = vpp
        result["freq"] = self.analyzer.get_frequency()
        result["thd"] = self.analyzer.get_thd()
        result["thdn"] = self.analyzer.get_thdn()
        result["rms"] = rms
        return result

    def enable_output(self, freq, rms):
        '''
        Dazzler output sine wave, differencial mode.

        Args:
            freq:    int, [10~100000], Ouput signal's frequency, unit is Hz.
            rms:     float, [0~2300], Ouput wave's RMS, unit is mV.

        Returns:
            string, "done", api execution successful.

        Examples:
            dazzler.enable_output(10000, 500)
        '''
        assert freq >= DazzlerDef.OUTPUT_FREQ_MIN
        assert freq <= DazzlerDef.OUTPUT_FREQ_MAX
        assert rms >= DazzlerDef.OUTPUT_RMS_MIN
        assert rms <= DazzlerDef.OUTPUT_RMS_MAX

        # enable I2S tx module
        self.i2s_tx_en_pin.set_level(1)

        self.signal_source.open()

        rms = self.calibrate(DazzlerDef.OUTPUT_CAL_ITEM, rms)
        # vpp = RMS * 2 * sqrt(2)
        vpp = rms * DazzlerDef.RMS_TO_VPP_RATIO
        # calculate vpp to vpp scale for FPGA
        vpp_scale = vpp * DazzlerDef.VPP_2_SCALE_RATIO / DazzlerDef.SIGNAL_SOURCE_VREF
        self.signal_source.set_signal_type(DazzlerDef.OUTPUT_WAVE)
        self.signal_source.set_signal_time(DazzlerDef.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.set_swg_paramter(self.sample_rate, freq, vpp_scale, DazzlerDef.OUTPUT_SIGNAL_DUTY)
        self.signal_source.output_signal()
        return "done"

    def disable_output(self):
        '''
        Dazzler close sine wave output.

        Returns:
            string, "done", api execution successful.

        Examples:
            dazzler.disable_output()
        '''
        self.signal_source.close()
        self.i2s_tx_en_pin.set_level(0)
        return "done"
