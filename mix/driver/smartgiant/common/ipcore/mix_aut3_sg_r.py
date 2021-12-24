# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXAUT3SGRDef:
    MIX_GPIO_IPCORE_ADDR = 0x2000
    MIX_SIGNAL_SOURCE_SG_IPCORE_ADDR = 0x4000
    MIX_FFT_ANALYZER_SG_IPCORE_ADDR = 0x6000

    MIX_FFT_REG_SIZE = 256
    MIX_SIGNAL_SOURCE_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256
    # MIXAUT3SGR overall regsize
    REG_SIZE = 0x8000

    PDM_RANGE_PIN = 10
    PDM_RANGE_TABLE = [50, 99]

    PDM_99RANGE_GAIN = 2.0


class MIXAUT3SGR(object):
    '''
    MIXAUT3SGR aggregated IPcore has 3 child IP, MIXFftAnalyzerSG, MIXSignalSourceSG, MIXGPIO.

    ClassType = MIXAUT3SGR

    Args:
        axi4_bus:            instance(AXI4LiteBus)/None,  which is used to access IP register.
        fft_data_cnt:        int,     get fft absolute data count, if not give, with get count from register.
        use_signal_source:   boolean, if True, enable signal source submodule, otherwise disable signal source.
        use_analyzer:        boolean, if True, enable fft analyzer, otherwise disable analyzer.
        use_gpio:            boolean, if True, enable gpio submodule, otherwise disable gpio.

    Examples:
        axi4 = AXI4LiteBus('/dev/MIX_AUT3_SG_R', 0x8000)
        # enable signal source, analyzeer and gpio sub IP in MIXAUT3SGR
        aut3sgr = MIXAUT3SGR(axi4, use_signal_source=True, use_analyzer=True, use_gpio=True)

    '''

    rpc_public_api = ['set_range', 'get_vpp']

    def __init__(self, axi4_bus, fft_data_cnt=None, use_signal_source=True, use_analyzer=True, use_gpio=True):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            axi4_bus = AXI4LiteBus(axi4_bus, MIXAUT3SGRDef.REG_SIZE)

        if axi4_bus is not None:
            if use_gpio:
                self._gpio_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXAUT3SGRDef.MIX_GPIO_IPCORE_ADDR,
                                                     MIXAUT3SGRDef.MIX_GPIO_REG_SIZE)
                self.gpio = MIXGPIOSG(self._gpio_axi4_bus)
            if use_signal_source:
                self._signal_source_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXAUT3SGRDef.MIX_SIGNAL_SOURCE_SG_IPCORE_ADDR,
                                                              MIXAUT3SGRDef.MIX_SIGNAL_SOURCE_REG_SIZE)
                self.signal_source = MIXSignalSourceSG(self._signal_source_axi4_bus)
            if use_analyzer:
                self._fft_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXAUT3SGRDef.MIX_FFT_ANALYZER_SG_IPCORE_ADDR,
                                                    MIXAUT3SGRDef.MIX_FFT_REG_SIZE)
                self.analyzer = MIXFftAnalyzerSG(self._fft_axi4_bus, fft_data_cnt)
        else:
            self.analyzer = MIXFftAnalyzerSGEmulator('mix_fftanalyzer_sg_emulator')
            self.signal_source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.gpio = MIXGPIOSGEmulator("mix_gpio_sg_emulator", 256)

    def set_range(self, range=50):
        '''
        Set PDM signal measure range, default is 50%FS.

        Args:
            range:      int, [50, 99], unit %FS, measure signal range
        '''
        assert range in MIXAUT3SGRDef.PDM_RANGE_TABLE
        if range == 50:
            self.gpio.set_pin(MIXAUT3SGRDef.PDM_RANGE_PIN, 0)
        else:
            self.gpio.set_pin(MIXAUT3SGRDef.PDM_RANGE_PIN, 1)
        self.pdm_range = range

    def get_vpp(self):
        '''
        Signal's vpp calculate result.

        If range be set to 99 %FS, must use this function, can not use get_vpp in MIX_FFTAnaylzer_SG.

        Returns:
            float, value, unit V, Result of signal's amplitude.

        '''
        if self.pdm_range == 50:
            return self.analyzer.get_vpp()
        else:
            return MIXAUT3SGRDef.PDM_99RANGE_GAIN * self.analyzer.get_vpp()

