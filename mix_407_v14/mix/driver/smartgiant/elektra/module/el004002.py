# -*- coding: utf-8 -*-
from elektra import ElektraBase
from elektra import ElektraDef


__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.2'


class EL004002(ElektraBase):
    '''
    The EL004002(el-004-002) is a two-channel dc electronic load.

    compatible = ["GQQ-EL0004002-000"]

    Each channel has the function of CC,CV and CR,
    and also has the function of voltage and current measurement.

    Args:
        i2c:              instance(I2C)/None,  If not given, PLI2CBus emulator will be created.
        spi:              instance(QSPI)/None, if not given, PLSPIBus emulator will be created.
        ad7608:           instance(ADC)/None,  If not given, AD760X emulator will be created.
        gpio:             instance(GPIO)/None, If not given, PinEmulator emulator will be created.
        volt_ch1:         int, default 0, ADC channel id for read voltage ch1.
        volt_ch2:         int, default 2, ADC channel id for read voltage ch2.
        curr_ch1:         int, default 1, ADC channel id for read current ch1.
        curr_ch2:         int, default 3, ADC channel id for read current ch2.

    Examples:
        axi4 = AXI4LiteBus('/dev/AXI4_I2C_8', 256)
        i2c = PLI2CBus(axi4)
        axi4 = AXI4LiteBus('/dev/AXI4_SPI_0', 8192)
        spi = PLSPIBus(axi4)
        axi4 = AXI4LiteBus('/dev/AXI4_AD760x_0', 8192)
        ad7608 = AD7608(axi4)
        axi4 = AXI4LiteBus('/dev/AXI4_GPIO_0', 256)
        gpio = PLGPIO(axi4)

        elektra = Elektra(i2c, spi, ad7608, gpio)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-EL0004002-000"]

    def __init__(self, i2c=None, spi=None, ad7608=None, gpio=None,
                 volt_ch1=0, volt_ch2=2, curr_ch1=1, curr_ch2=3, ipcore=None):
        super(EL004002, self).__init__(i2c, spi, ad7608, gpio, volt_ch1, volt_ch2, curr_ch1, curr_ch2,
                                       ElektraDef.EEPROM_DEV_ADDR, ElektraDef.SENSOR_DEV_ADDR, ipcore)
