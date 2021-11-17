# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_qi_asklink_encode_sg import MIXQIASKLinkEncodeSG
from mix.driver.smartgiant.common.ipcore.mix_qi_fsklink_decode_sg import MIXQIFSKLinkDecodeSG
from mix.driver.smartgiant.common.ipcore.mix_ad760x_sg import MIXAd7608SG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.core.bus.pin import Pin

__author__ = 'peiji.wu@SmartGiant'
__version__ = '0.1'


class MIXScope007SGRDef:
    IP_GPIO_OFFSET = 0x2000
    IP_AD760X_OFFSET = 0x4000
    IP_FFT_OFFSET = 0x6000
    IP_SIGNAL_METER_OFFSET = 0x8000
    IP_ASK_OFFSET = 0xA000
    IP_FSK_OFFSET = 0xC000

    IP_SIGNAL_METER_REG_SIZE = 256
    IP_AD760X_REG_SIZE = 8192
    IP_GPIO_REG_SIZE = 256
    IP_REG_SIZE = 65536
    MIX_QI_ASKLINK_CODE_REG_SIZE = 8192
    MIX_QI_FSKLINK_DECODE_REG_SIZE = 8192
    PL_SIGNAL_METER_SIZE = 256
    PL_ADC_SIZE = 8192
    PL_FFT_SIZE = 65535

    ADC_FILTER_PIN_0 = 4
    ADC_FILTER_PIN_1 = 5
    ADC_FILTER_PIN_2 = 6
    ADC_FFT_PIN_0 = 7
    ADC_FFT_PIN_1 = 8
    ADC_FFT_PIN_2 = 9
    ADC_CTRL_PIN_0 = 3
    ADC_CTRL_PIN_1 = 2
    FREQ_GEAR_0 = 1
    FREQ_GEAR_1 = 0
    ASK_CTRL_PIN = 15
    FSK_CTRL_PIN = 25
    FSK_CIC_CTRL_PIN = 44


class MIXScope007SGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXScope007SGR(object):
    '''
    MIXScope007SGR Driver
        MIXScope007SGR aggregated IP includes MIXAD7608, MIXQIAskLinkCode, MIXQIFskLinkDecode and MIXGPIO,
        PLSignalMeter ipcore will be created

    Args:
        axi4_bus:        instance(AXI4LiteBus)/string, axi4lit bus or dev path.

    Examples:
        scope007sg = MIXScope007SGR(axi4_bus='/dev/MIX_Scope_007_SG_0')

    '''

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXScope007SGRDef.IP_REG_SIZE)

        else:
            self.axi4_bus = axi4_bus

        ask_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXScope007SGRDef.IP_ASK_OFFSET,
                                      MIXScope007SGRDef.MIX_QI_ASKLINK_CODE_REG_SIZE)
        self.ask_code = MIXQIASKLinkEncodeSG(ask_axi4_bus)

        fsk_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXScope007SGRDef.IP_FSK_OFFSET,
                                      MIXScope007SGRDef.MIX_QI_FSKLINK_DECODE_REG_SIZE)
        self.fsk_decode = MIXQIFSKLinkDecodeSG(fsk_axi4_bus)

        gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXScope007SGRDef.IP_GPIO_OFFSET,
                                       MIXScope007SGRDef.IP_GPIO_REG_SIZE)
        gpio = MIXGPIOSG(gpio_axi4_bus)
        # set the pin to select the measurement mode and channel
        self.adc_filter_pin_0 = Pin(gpio, MIXScope007SGRDef.ADC_FILTER_PIN_0)
        self.adc_filter_pin_1 = Pin(gpio, MIXScope007SGRDef.ADC_FILTER_PIN_1)
        self.adc_filter_pin_2 = Pin(gpio, MIXScope007SGRDef.ADC_FILTER_PIN_2)
        self.adc_ctrl_pin_0 = Pin(gpio, MIXScope007SGRDef.ADC_CTRL_PIN_0)
        self.adc_ctrl_pin_1 = Pin(gpio, MIXScope007SGRDef.ADC_CTRL_PIN_1)
        self.adc_fft_pin_0 = Pin(gpio, MIXScope007SGRDef.ADC_FFT_PIN_0)
        self.adc_fft_pin_1 = Pin(gpio, MIXScope007SGRDef.ADC_FFT_PIN_1)
        self.adc_fft_pin_2 = Pin(gpio, MIXScope007SGRDef.ADC_FFT_PIN_2)
        self.freq_gear_pin_0 = Pin(gpio, MIXScope007SGRDef.FREQ_GEAR_0)
        self.freq_gear_pin_1 = Pin(gpio, MIXScope007SGRDef.FREQ_GEAR_1)
        self.ask_ctrl_pin = Pin(gpio, MIXScope007SGRDef.ASK_CTRL_PIN)
        self.fsk_ctrl_pin = Pin(gpio, MIXScope007SGRDef.FSK_CTRL_PIN)
        self.fsk_cic_ctrl_pin = Pin(gpio, MIXScope007SGRDef.FSK_CIC_CTRL_PIN)

        adc_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXScope007SGRDef.IP_AD760X_OFFSET,
                                      MIXScope007SGRDef.PL_ADC_SIZE)
        self.adc = MIXAd7608SG(adc_axi4_bus)

        signal_meter_axi4_bus = AXI4LiteSubBus(
            self.axi4_bus, MIXScope007SGRDef.IP_SIGNAL_METER_OFFSET, MIXScope007SGRDef.PL_SIGNAL_METER_SIZE)
        self.ac_signal_meter = MIXSignalMeterSG(signal_meter_axi4_bus)
        self.adc_signal_meter = MIXSignalMeterSG(signal_meter_axi4_bus)

        fft_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXScope007SGRDef.IP_FFT_OFFSET, MIXScope007SGRDef.PL_FFT_SIZE)
        self.fftanalyzer = MIXFftAnalyzerSG(fft_axi4_bus)
