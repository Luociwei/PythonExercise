# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.pin import Pin


__author__ = 'Yongjiu.tan@SmartGiant'
__version__ = 'V0.0.1'


class MIXMagneto002SGRDef:
    MIX_FFT_ANAYLZER_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x2000

    MIX_FFT_REG_SIZE = 1024
    MIX_GPIO_REG_SIZE = 1024
    REG_SIZE = 65535

    CS5361_RST_BIT = 0
    CS5361_OVFL_BIT = 6
    I2S_EN_BIT = 1
    I2S_CONF0_BIT = 2
    I2S_CONF1_BIT = 3
    I2S_DATA_MODE = {
        'left': [0, 0],
        'right': [0, 1],
        'differential': [1, 0]
    }

    DELAY = 0.001  # ms


class MIXMagneto002SGR (object):
    '''
    MIXMagneto002SGR, support GPIO, FFT.

    Args:
        axi4_bus:            Instance(AXI4LiteBus)/string, axi4lite instance or dev path
        fft_data_cnt:        int,    get fft absolute data count, if not give, with get count from register.

    Example:
             magneto002 = MIXMagneto002SGR('/dev/MIX_Magneto002_SG_R_0')
    '''

    def __init__(self, axi4_bus, fft_data_cnt=None):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXMagneto002SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.fft_analyzer_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXMagneto002SGRDef.MIX_FFT_ANAYLZER_IPCORE_ADDR,
                                                    MIXMagneto002SGRDef.MIX_FFT_REG_SIZE)
        self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXMagneto002SGRDef.MIX_GPIO_IPCORE_ADDR,
                                            MIXMagneto002SGRDef.MIX_GPIO_REG_SIZE)

        self.gpio = MIXGPIOSG(self.gpio_axi4_bus)

        self.i2s_conf_0 = Pin(self.gpio, MIXMagneto002SGRDef.I2S_CONF0_BIT)
        self.i2s_conf_1 = Pin(self.gpio, MIXMagneto002SGRDef.I2S_CONF1_BIT)

        self.cs5361_ovfl = Pin(self.gpio, MIXMagneto002SGRDef.CS5361_OVFL_BIT)
        self.cs5361_rst = Pin(self.gpio, MIXMagneto002SGRDef.CS5361_RST_BIT)
        self.i2s_en = Pin(self.gpio, MIXMagneto002SGRDef.I2S_EN_BIT)
        self.analyzer = MIXFftAnalyzerSG(self.fft_analyzer_axi4_bus, fft_data_cnt)

        self.reset()

    def reset(self):
        self.i2s_conf_0.set_dir('output')
        self.i2s_conf_1.set_dir('output')
        self.cs5361_ovfl.set_dir('input')
        self.cs5361_rst.set_dir('output')
        self.i2s_en.set_dir('output')

        # disable ipcore
        self.i2s_en.set_level(0)

        self.config('left')

        # reset ic
        self.cs5361_rst.set_level(0)
        time.sleep(MIXMagneto002SGRDef.DELAY)
        self.cs5361_rst.set_level(1)

    def config(self, mode):
        '''
        Config.

        Args：
            mode:   string, ['left', 'right', 'differential'],  data mode.

        Example:
            magneto002.config('right')

        '''
        assert mode in MIXMagneto002SGRDef.I2S_DATA_MODE

        self.i2s_conf_0.set_level(MIXMagneto002SGRDef.I2S_DATA_MODE[mode][1])
        self.i2s_conf_1.set_level(MIXMagneto002SGRDef.I2S_DATA_MODE[mode][0])
        return 'done'

    def get_driver_version(self):
        return __version__
