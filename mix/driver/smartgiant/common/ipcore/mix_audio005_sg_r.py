# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_ram_signal_sg import MIXRamSignalSG
from mix.driver.smartgiant.common.ipcore.mix_audio_cache_sg import MIXAudioCacheSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.0.2'


class MIXAudio005SGRException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXAudio005SGRDef:
    MIX_AUDIO_CACHE_IPCORE_ADDR = 0xa000
    MIX_RAM_SIGNAL_IPCORE_ADDR = 0x8000
    MIX_FFT_ANAYLZER_IPCORE_ADDR = 0x6000
    MIX_SIGNAL_SOURCE_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x2000

    MIX_AUDIO_CACHE_REG_SIZE = 256
    MIX_RAM_SIGNAL_REG_SIZE = 256
    MIX_FFT_REG_SIZE = 256
    MIX_SIGNAL_SOURCE_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256
    # MIXAudio005SGR overall regsize
    REG_SIZE = 65535


class MIXAudio005SGR(object):
    '''
    MIXAudio005SGR aggregated IPcore has 3 child IP, MIXFFTAnalyzer, MIXSignalSource, MIXGPIOSG.

    ClassType = MIXAudio005SGR

    Args:
        axi4_bus:            Instance(AXI4LiteBus)/string, axi4lite instance or dev path.
        fft_data_cnt:        int, get fft absolute data count, if not give, with get count from register.

    Examples:
             mix_Audio = MIXAudio005SGR('/dev/MIX_Audio005_SG_R')
    '''

    def __init__(self, axi4_bus, fft_data_cnt=None):
        if axi4_bus:
            if isinstance(axi4_bus, basestring):
                # device path; create axi4lite instance
                self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAudio005SGRDef.REG_SIZE)
            else:
                self.axi4_bus = axi4_bus
        else:
            raise MIXAudio005SGRException("parameter 'axi4_bus' can not be None")

        self.fft_analyzer_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAudio005SGRDef.MIX_FFT_ANAYLZER_IPCORE_ADDR,
                                                    MIXAudio005SGRDef.MIX_FFT_REG_SIZE)
        self.analyzer = MIXFftAnalyzerSG(self.fft_analyzer_axi4_bus, fft_data_cnt)

        self.signal_source_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAudio005SGRDef.MIX_SIGNAL_SOURCE_IPCORE_ADDR,
                                                     MIXAudio005SGRDef.MIX_SIGNAL_SOURCE_REG_SIZE)
        self.signal_source = MIXSignalSourceSG(self.signal_source_axi4_bus)

        self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAudio005SGRDef.MIX_GPIO_IPCORE_ADDR,
                                            MIXAudio005SGRDef.MIX_GPIO_REG_SIZE)
        self.gpio = MIXGPIOSG(self.gpio_axi4_bus)

        self.ram_signal_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAudio005SGRDef.MIX_RAM_SIGNAL_IPCORE_ADDR,
                                                  MIXAudio005SGRDef.MIX_RAM_SIGNAL_REG_SIZE)
        self.ram_signal = MIXRamSignalSG(self.ram_signal_axi4_bus)

        self.audio_cache_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXAudio005SGRDef.MIX_AUDIO_CACHE_IPCORE_ADDR,
                                                   MIXAudio005SGRDef.MIX_AUDIO_CACHE_REG_SIZE)
        self.audio_cache = MIXAudioCacheSG(self.audio_cache_axi4_bus)
