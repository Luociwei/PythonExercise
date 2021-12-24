# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_xtalkmeasure_sg import MIXXtalkMeasureSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG


__author__ = 'Shunreng.He@SmartGiant'
__version__ = '0.4'


class MIXMIK002SGRDef:

    MIX_FFT_ANAYLZER_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x2000

    MIX_FFT_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256
    # MIXMIK002SGR overall regsize
    REG_SIZE = 65535


class MIXMIK002SGR(object):
    '''
    MIXMIK002SGR aggregated IPcore has 2 child IP, MIXXtalkMeasureSG, MIXGPIOSG.

    ClassType = MIXMIK002SGR

    gpio bit0：ADC reset output
    gpio bit1：bit1=1 select I2S both channel
    gpio bit2：bit2=1 select left channel
    gpio bit3：bit3=1 select right channel
    gpio bit4：bit4=1 enable data upload to DMA directly
    gpio bit5：get TONE_DETECT pin state
    gpio bit6：get ADC_OVFL    pin state
    gpio bit7：bit7=1 select FFT measure

    Args:
        axi4_bus:            instance(AXI4LiteBus)/string, axi4lite instance or dev path.
        fft_data_cnt:        int/None,  get fft absolute data count,
                                        if None, with get count from register.
    Examples:
        mix_mik002 = MIXMIK002SGR('/dev/MIX_MIK002_SG_R_0')

    '''

    def __init__(self, axi4_bus, fft_data_cnt=None):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            axi4_bus = AXI4LiteBus(axi4_bus, MIXMIK002SGRDef.REG_SIZE)
        else:
            axi4_bus = axi4_bus

        self.fft_analyzer_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXMIK002SGRDef.MIX_FFT_ANAYLZER_IPCORE_ADDR,
                                                    MIXMIK002SGRDef.MIX_FFT_REG_SIZE)
        self.analyzer = MIXXtalkMeasureSG(self.fft_analyzer_axi4_bus, fft_data_cnt)

        self.gpio_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXMIK002SGRDef.MIX_GPIO_IPCORE_ADDR,
                                            MIXMIK002SGRDef.MIX_GPIO_REG_SIZE)
        self.gpio = MIXGPIOSG(self.gpio_axi4_bus)
