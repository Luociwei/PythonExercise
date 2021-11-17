# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.core.bus.pin import Pin

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.2'


class MIXAUT1SGRDef:
    MIX_FFT_ANAYLZER_IPCORE_ADDR = 0x6000
    MIX_SIGNAL_SOURCE_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x2000

    MIX_FFT_REG_SIZE = 256
    MIX_SIGNAL_SOURCE_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256
    # MIXAUT1SGR overall regsize
    REG_SIZE = 65536

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9

    OUTPUT_TYPE = 'sine'
    ALWAYS_OUTPUT = 0xffffffff
    OUTPUT_DUTY = 0.5


class MIXAUT1SGR(object):
    '''
    MIXAUT1SGR aggregated IPcore has 3 child IP, MIXFftAnalyzerSG, MIXSignalSourceSG, MIXGPIOSG.

    ClassType = MIXAUT1SGR

    Args:
        axi4_bus:            instance(AXI4LiteBus)/string, axi4lite instance or dev path.
        fft_data_cnt:        int,    get fft absolute data count, if not give, with get count from register.

    Examples:
        mix_aut1 = MIXAUT1SGR('/dev/MIX_AUT1_x')

    '''

    rpc_public_api = ['reset_adc', 'reset_dac', 'enable_rx', 'disable_rx', 'enable_tx',
                      'disable_tx', 'enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output']

    def __init__(self, axi4_bus, fft_data_cnt=None):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAUT1SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        if self.axi4_bus is None:
            self.analyzer = MIXFftAnalyzerSGEmulator('mix_fftanalyzer_sg_emulator')
            self.signal_source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.gpio = MIXGPIOSGEmulator("mix_gpio_sg_emulator", 256)
        else:
            self.fft_analyzer_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT1SGRDef.MIX_FFT_ANAYLZER_IPCORE_ADDR,
                                                        MIXAUT1SGRDef.MIX_FFT_REG_SIZE)
            self.analyzer = MIXFftAnalyzerSG(self.fft_analyzer_axi4_bus, fft_data_cnt)

            self.signal_source_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT1SGRDef.MIX_SIGNAL_SOURCE_IPCORE_ADDR,
                                                         MIXAUT1SGRDef.MIX_SIGNAL_SOURCE_REG_SIZE)
            self.signal_source = MIXSignalSourceSG(self.signal_source_axi4_bus)

            self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT1SGRDef.MIX_GPIO_IPCORE_ADDR,
                                                MIXAUT1SGRDef.MIX_GPIO_REG_SIZE)
            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)
        self.adc_rst_pin = Pin(self.gpio, MIXAUT1SGRDef.ADC_RESET_PIN)
        self.i2s_rx_en_pin = Pin(self.gpio, MIXAUT1SGRDef.I2S_RX_EN_PIN)
        self.dac_rst_pin = Pin(self.gpio, MIXAUT1SGRDef.DAC_RESET_PIN)
        self.i2s_tx_en_pin = Pin(self.gpio, MIXAUT1SGRDef.I2S_TX_EN_PIN)

    def reset_adc(self, delay_ms):
        '''
        Reset ADC.

        Args:
            delay_ms:   int, unit ms, reset time in ms

        Returns:
            "done"

        '''
        self.adc_rst_pin.set_level(0)
        time.sleep(delay_ms / 1000.0)
        self.adc_rst_pin.set_level(1)
        return "done"

    def reset_dac(self, delay_ms):
        '''
        Reset DAC.

        Args:
            delay_ms:   int, unit ms, reset time in ms

        Returns:
            "done"

        '''
        self.dac_rst_pin.set_level(0)
        time.sleep(delay_ms / 1000.0)
        self.dac_rst_pin.set_level(1)
        return "done"

    def enable_rx(self):
        '''
        Enable I2S RX
        '''
        self.i2s_rx_en_pin.set_level(1)
        return "done"

    def disable_rx(self):
        '''
        Disable I2S RX
        '''
        self.i2s_rx_en_pin.set_level(0)
        return "done"

    def enable_tx(self):
        '''
        Enable I2S TX
        '''
        self.i2s_tx_en_pin.set_level(1)
        return "done"

    def disable_tx(self):
        '''
        Disable I2S TX
        '''
        self.i2s_tx_en_pin.set_level(0)
        return "done"

    def enable_upload(self):
        '''
        Enable FFT data upload

        Returns:
            string, "done", api execution successful.

        '''
        self.analyzer.enable_upload()
        return "done"

    def disable_upload(self):
        '''
        Disable FFT data upload

        Returns:
            string, "done", api execution successful.

        '''
        self.analyzer.disable_upload()
        return "done"

    def measure(self, sampling_rate, decimation_type, bandwidth_hz='auto', harmonic_num=None, freq_point=None):
        '''
        Measure signal's freq, vpp, THD+N, THD.

        Args:
            sample_rate:     int, Sample rate of your ADC device, unit is Hz. Eg. 192000.
            decimation_type: int, [1~255],    Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                              choose one suitable number.
            bandwidth:       int/string,       FFT calculation bandwidth limit, must smaller than half of sample_rate,
                                               unit is Hz. Eg. 20000. If 'auto' given, bandwidth will be automatically
                                               adjust based on base frequency.
            harmonic_count:  int/None, [1~10]  The harmonic count of signal, default is None will not do calculate.
            freq_point:      int/None,         Specified frequency for calculating amplitude at this special frequency,
                                               default is None will not do this.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value),
                  dict with vpp, freq, thd, thdn.

        Examples:
            result = aut1.measure(48000, 5, 0xff)
            print(result['frequency'], result['vpp'], ['thdn'], ['thd'])

        '''
        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz, harmonic_num, freq_point)
        self.analyzer.analyze()
        result = dict()
        result["vpp"] = self.analyzer.get_vpp()
        result["freq"] = self.analyzer.get_frequency()
        result["thd"] = self.analyzer.get_thd()
        result["thdn"] = self.analyzer.get_thdn()

        return result

    def enable_output(self, sampling_rate, freq, vpp):
        '''
        Enable signal source output

        Args:
            sampling_rate:  int, in SPS, DAC sampling rate.
            freq:           int, unit Hz, Ouput signal's frequency.
            vpp:            float, [0.000~0.999], output signal vpp scale.

        Returns:
            string, "done", api execution successful.

        Examples:
            aut1.enable_output(10000, 500)

        '''
        self.signal_source.open()

        self.signal_source.set_signal_type(MIXAUT1SGRDef.OUTPUT_TYPE)
        self.signal_source.set_signal_time(MIXAUT1SGRDef.ALWAYS_OUTPUT)
        self.signal_source.set_swg_paramter(sampling_rate, freq, vpp, MIXAUT1SGRDef.OUTPUT_DUTY)
        self.signal_source.output_signal()
        return "done"

    def disable_output(self):
        '''
        Disable signal source output
        '''
        self.signal_source.close()
        return "done"
