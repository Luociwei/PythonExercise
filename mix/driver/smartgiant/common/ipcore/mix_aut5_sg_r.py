# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad7177_sg_emulator import MIXAd7177SGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG, MIXAd7177SG

__author__ = 'Hanyong Huang@SmartGiant'
__version__ = '0.1'


class MIXDAQT5Exception(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXAUT5SGRDef:
    MIX_AD717X_IPCORE_ADDR = 0x8000
    MIX_FFT_ANAYLZER_IPCORE_ADDR = 0x6000
    MIX_SIGNAL_SOURCE_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x2000

    MIX_FFT_REG_SIZE = 256
    MIX_SIGNAL_SOURCE_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256
    # MIXAUT5SGR overall regsize
    REG_SIZE = 65535
    AD717X_REG_SIZE = 8192


class MIXAUT5SGR(object):
    '''
    MIXAUT5SGR aggregated IPcore has 3 child IP, MIXFFTAnalyzer, MIXSignalSource, MIXGPIO.

    :param axi4_bus:            Instance(AXI4LiteBus)/string, axi4lite instance or dev path
    :param fft_data_cnt:        int,    get fft absolute data count, if not give, with get count from register.
    :example:
             mix_aut1 = MIXAUT5SGR('/dev/MIX_AUT1_x')
    '''

    def __init__(self, axi4_bus=None, fft_data_cnt=None, ad717x_chip="ad7175", ad717x_mvref=5000,
                 code_polar="bipolar", reference="extern", buffer_flag="enable", clock="crystal"):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAUT5SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        if self.axi4_bus is None:
            self.analyzer = MIXFftAnalyzerSGEmulator('mix_fftanalyzer_sg_emulator')
            self.signal_source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.gpio = MIXGPIOSGEmulator("mix_gpio_sg_emulator", 256)
            if ad717x_chip == 'ad7175':
                self.ad717x = MIXAd7175SGEmulator("mix_ad7175_sg_emulator", 2500)
            else:
                self.ad717x = MIXAd7177SGEmulator("mix_ad7177_sg_emulator", 2500)
        else:
            self.fft_analyzer_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT5SGRDef.MIX_FFT_ANAYLZER_IPCORE_ADDR,
                                                        MIXAUT5SGRDef.MIX_FFT_REG_SIZE)
            self.analyzer = MIXFftAnalyzerSG(self.fft_analyzer_axi4_bus, fft_data_cnt)

            self.signal_source_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT5SGRDef.MIX_SIGNAL_SOURCE_IPCORE_ADDR,
                                                         MIXAUT5SGRDef.MIX_SIGNAL_SOURCE_REG_SIZE)
            self.signal_source = MIXSignalSourceSG(self.signal_source_axi4_bus)

            self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT5SGRDef.MIX_GPIO_IPCORE_ADDR,
                                                MIXAUT5SGRDef.MIX_GPIO_REG_SIZE)

            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)

            self.ad717x_chip = ad717x_chip
            self.ad717x_mvref = ad717x_mvref
            self.code_polar = code_polar
            self.reference = reference
            self.buffer_flag = buffer_flag
            self.clock = clock

            # self.open()
            self.ad717x_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAUT5SGRDef.MIX_AD717X_IPCORE_ADDR,
                                                  MIXAUT5SGRDef.AD717X_REG_SIZE)

            if self.ad717x_chip == "ad7175":
                self.ad717x = MIXAd7175SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                          self.buffer_flag, self.clock)
            elif self.ad717x_chip == "ad7177":
                self.ad717x = MIXAd7177SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                          self.buffer_flag, self.clock)
            else:
                raise MIXDAQT5Exception("Unsupported AD717x chip type %s." % (self.ad717x_chip))
