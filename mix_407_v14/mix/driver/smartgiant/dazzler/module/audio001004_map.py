# -*- coding: utf-8 -*-

import time
import math
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_aut1_sg_r import MIXAUT1SGR

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1.1'


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

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9
    TIME_OUT = 1


class DazzlerException(Exception):

    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class DazzlerBase(SGModuleDriver):

    '''
    Base class of audio001.

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

    '''

    rpc_public_api = ['enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, adc_rst_pin=None, i2s_rx_en_pin=None,
                 dac_rst_pin=None, i2s_tx_en_pin=None,
                 sample_rate=192000, ipcore=None):
        assert sample_rate > 0 and sample_rate <= DazzlerDef.MAX_SAMPLING_RATE

        self.eeprom = CAT24C32(DazzlerDef.EEPROM_I2C_ADDR, i2c)
        self.nct75 = NCT75(DazzlerDef.SENSOR_I2C_ADDR, i2c)

        super(DazzlerBase, self).__init__(self.eeprom, self.nct75, range_table=dazzler_range_table)

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
        else:
            raise DazzlerException("parameter 'ipcore' can not be None")

        self.sample_rate = sample_rate

    def post_power_on_init(self, timeout=DazzlerDef.TIME_OUT):
        '''
        Init Dazzler module to a know harware state.

        This function will reset dac/adc and i2s module.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        self.reset(timeout)

    def reset(self, timeout=DazzlerDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
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
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise DazzlerException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=DazzlerDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set pin level to 0 and close signal source.

        Args:
            timeout:      float, default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_rst_pin.set_level(0)
                self.i2s_rx_en_pin.set_level(0)
                self.dac_rst_pin.set_level(0)
                self.i2s_tx_en_pin.set_level(0)
                self.signal_source.close()
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise DazzlerException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Dazzler driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

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
            freq:    int, [10~50000], Ouput signal's frequency, unit is Hz.
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


class Audio001004(DazzlerBase):

    '''
    Audio001004 has a output sine function and one measure channel.
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
        ipcore:              instance(MIXAUT1SGR),           aggregated MIXAUT1SGR wrapper.

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
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-LTJX-5-040"]

    def __init__(self, i2c, adc_rst_pin=None, i2s_rx_en_pin=None,
                 dac_rst_pin=None, i2s_tx_en_pin=None, sample_rate=192000, ipcore=None):
        super(Audio001004, self).__init__(
            i2c, adc_rst_pin, i2s_rx_en_pin, dac_rst_pin, i2s_tx_en_pin, sample_rate, ipcore)
