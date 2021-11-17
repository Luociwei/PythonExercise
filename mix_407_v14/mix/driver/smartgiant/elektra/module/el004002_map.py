# -*- coding: utf-8 -*-
from elektra_map import ElektraBase
from elektra_map import ElektraDef


__author__ = 'dongdongzhang@SmartGiant'
__version__ = 'V0.1.2'


class EL004002(ElektraBase):
    '''
    The EL004002(el-004-002) is a two-channel dc electronic load.

    compatible = ["GQQ-LWFT-5-02B", "GQQ-LWFT-5-020"]

    Each channel has the function of CC,CV and CR,
    and also has the function of voltage and current measurement.

    Args:
        i2c:              instance(I2C)/None, instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        spi:              instance(MIXQSPISG)/None, which is used to control AD5663R.
        blade:            instance(Blade)/None, which is used to control AD7608.
        gpio:             instance(GPIO)/None, which is used to control AD5663R pin.
        volt_ch1:         int, default 0, ADC channel id for read voltage ch1.
        volt_ch2:         int, default 2, ADC channel id for read voltage ch2.
        curr_ch1:         int, default 1, ADC channel id for read current ch1.
        curr_ch2:         int, default 3, ADC channel id for read current ch2.

    Examples:
        i2c = I2C("/dev/i2c-0")
        axi4 = AXI4LiteBus('/dev/AXI4_SPI_0', 8192)
        spi = MIXQSPISG(axi4)
        axi4 = AXI4LiteBus('/dev/AXI4_AD760x_0', 8192)
        ad7608 = MIXAd7608SG(axi4)
        io = GPIO(86, "output")
        gpio = Pin(io, 86, "output")

        elektra = EL004002(i2c, spi, ad7608, gpio)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-LWFT-5-02B", "GQQ-LWFT-5-020"]

    def __init__(self, i2c=None, spi=None, blade=None, gpio=None,
                 volt_ch1=0, volt_ch2=2, curr_ch1=1, curr_ch2=3, ipcore=None):
        super(EL004002, self).__init__(i2c, spi, blade, gpio,
                                       volt_ch1, volt_ch2, curr_ch1, curr_ch2,
                                       ElektraDef.EEPROM_DEV_ADDR, ElektraDef.SENSOR_DEV_ADDR,
                                       ipcore, ElektraDef.CAT9555_ADDR)

    def post_power_on_init(self, timeout=ElektraDef.DEFAULT_TIMEOUT):
        '''
        Init Elektra module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=ElektraDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        This function will configure GPIO pin default direction and values, reset ad5663 and ad7608.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        super(EL004002, self).reset(timeout)

    def pre_power_down(self, timeout=ElektraDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and disable E-load channel.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        super(EL004002, self).pre_power_down(timeout)

    def get_driver_version(self):
        '''
        Get Elektra driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
