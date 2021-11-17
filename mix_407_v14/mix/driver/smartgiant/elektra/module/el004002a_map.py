# -*- coding: utf-8 -*-
from elektra_map import ElektraBase
from elektra_map import ElektraDef
from elektra_map import elektra_range_table
from elektra_map import ElektraException
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
import time


__author__ = 'dongdongzhang@SmartGiant'
__version__ = 'V0.1.2'


class EL004002ADef:
    VLOT_CH1 = 2
    VLOT_CH2 = 3
    CURR_CH1 = 0
    CURR_CH2 = 1

    AD7175_REG_SIZE = 256
    MIXDAQT1_REG_SIZE = 0x8000
    ADC_VREF_VOLTAGE_5000mV = 5000
    DEFAULT_TIMEOUT = 1  # s


class EL004002A(ElektraBase):
    '''
    The Eload004002A is a two-channel dc electronic load.Each channel has the function of CC,CV and CR,
    and also has the function of voltage and current measurement.

    compatible = ["GQQ-LWFT-5-02C", "GQQ-LWFT-5-02A"]

    Args:
        i2c:              instance(I2C)/None, instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        spi:              instance(MIXQSPISG)/None, which is used to control AD5663R.
        ad7175:           instance(ADC)/None,  Class instance of AD7175.
        gpio:             instance(GPIO)/None, which is used to control AD5663R pin.
        volt_ch1:         int, default 0, ADC channel id for read voltage ch1.
        volt_ch2:         int, default 2, ADC channel id for read voltage ch2.
        curr_ch1:         int, default 1, ADC channel id for read current ch1.
        curr_ch2:         int, default 3, ADC channel id for read current ch2.
        ipcore:     instance(MIXDAQT1)/string/None,  instance of MIX_DAQT1, which is used to control AD7175.

    Examples:
        Example for using no-aggregated IP:
            i2c = I2C("/dev/i2c-0")
            axi4 = AXI4LiteBus('/dev/AXI4_SPI_0', 8192)
            spi = MIXQSPISG(axi4)
            ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
            io = GPIO(86, "output")
            gpio = Pin(io, 86, "output")
            elektra = EL004002A(i2c, spi, ad7175, gpio)

        Example for using aggregated IP:
            i2c_bus = I2C('/dev/i2c-1')
            daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1_0', ad717x_mvref=5000, use_spi=True, use_gpio=False)
            elektra = EL004002A(i2c=i2c_bus, ipcore=daqt1)

        Example of set cv/cc & read voltage/current, set cr:
            elektra.post_power_on_init()
            elektra.channel_enable("ch1")
            elektra.set_cv("ch1", 200)  # elektra.set_cc("ch1", 100)
            elektra.read_voltage("ch1") # elektra.read_current("ch1")

            elektra.set_cr("ch1", 200)

    '''

    compatible = ["GQQ-LWFT-5-02C", "GQQ-LWFT-5-02A"]

    def __init__(self, i2c=None, spi=None, ad7175=None, gpio=None, ipcore=None):

        if (ipcore and i2c):
            if isinstance(ipcore, basestring):
                daqt1_axi4_bus = AXI4LiteBus(ipcore, EL004002ADef.MIXDAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                          ad717x_mvref=EL004002ADef.ADC_VREF_VOLTAGE_5000mV,
                                          use_spi=True, use_gpio=False)
            else:
                self.ipcore = ipcore

            super(EL004002A, self).__init__(i2c=i2c, spi=None, blade=None, gpio=None,
                                            volt_ch1=EL004002ADef.VLOT_CH1, volt_ch2=EL004002ADef.VLOT_CH2,
                                            curr_ch1=EL004002ADef.CURR_CH1, curr_ch2=EL004002ADef.CURR_CH2,
                                            eeprom_dev_addr=ElektraDef.EEPROM_DEV_ADDR,
                                            sensor_dev_addr=ElektraDef.SENSOR_DEV_ADDR,
                                            ipcore=self.ipcore, cat9555_dev_addr=ElektraDef.CAT9555_ADDR,
                                            range_table=elektra_range_table)
        elif (ad7175 and i2c and spi and gpio):
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, EL004002ADef.AD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4_bus, mvref=EL004002ADef.ADC_VREF_VOLTAGE_5000mV)
            else:
                self.ad7175 = ad7175

            super(EL004002A, self).__init__(i2c=i2c, spi=spi, blade=None, gpio=gpio,
                                            volt_ch1=EL004002ADef.VLOT_CH1, volt_ch2=EL004002ADef.VLOT_CH2,
                                            curr_ch1=EL004002ADef.CURR_CH1, curr_ch2=EL004002ADef.CURR_CH2,
                                            eeprom_dev_addr=ElektraDef.EEPROM_DEV_ADDR,
                                            sensor_dev_addr=ElektraDef.SENSOR_DEV_ADDR,
                                            ipcore=None, cat9555_dev_addr=ElektraDef.CAT9555_ADDR,
                                            range_table=elektra_range_table)
        else:
            raise ElektraException('__init__ error! Please check the parameters!')

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN4"},
            "ch1": {"P": "AIN1", "N": "AIN4"},
            "ch2": {"P": "AIN2", "N": "AIN4"},
            "ch3": {"P": "AIN3", "N": "AIN4"}
        }

        self.spi.set_mode('MODE2')

    def post_power_on_init(self, timeout=EL004002ADef.DEFAULT_TIMEOUT):
        '''
        Init Elektra module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=EL004002ADef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        This function will configure GPIO pin default direction and values, reset ad5663 and ad7175.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                if self.gpio is not None:
                    self.gpio.set_dir('output')

                self.cat9555.set_pins_dir(ElektraDef.IO_INIT_DIR)
                self.cat9555.set_ports(ElektraDef.IO_INIT_VALUE)

                self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.HIGH_LEVEL)
                self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.LOWE_LEVEL)
                if self.gpio is not None:
                    self.gpio.set_level(ElektraDef.AD5663R_PIN_LEVEL)
                self.ad5663.initial()
                self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.HIGH_LEVEL)

                if self.gpio is not None:
                    self.gpio.set_level(ElektraDef.AD7175_PIN_LEVEL)

                if not self.ad7175.is_communication_ok():
                    raise ElektraException("communication with ad7175 failed!")
                self.ad7175.channel_init()
                for channel in ElektraDef.AD7175_CHANNEL_LIST:
                    self.ad7175.disable_continuous_sampling(channel)
                    self.ad7175.set_setup_register("ch%d" % channel, "unipolar")
                    self.ad7175.set_sampling_rate(channel, ElektraDef.AD7175_DEFAULT_SAMPLING_RATE)

                # board reset
                self.reset_board('ch1')
                self.reset_board('ch2')
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise ElektraException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=EL004002ADef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and disable E-load channel.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        super(EL004002A, self).pre_power_down(timeout)

    def get_driver_version(self):
        '''
        Get Elektra driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def _read_adc(self, channel):
        assert channel in ElektraDef.AD7175_CHANNEL_LIST
        COUNT = 30
        STRIP = 5

        # get average value
        if self.gpio is not None:
            self.gpio.set_level(ElektraDef.AD7175_PIN_LEVEL)
        adc_volt_list = [self.ad7175.read_volt(channel) for _ in range(COUNT)]
        adc_volt_list.sort()
        avg = reduce(lambda x, y: x + y, adc_volt_list[STRIP: -STRIP], 0) / (COUNT - 2 * STRIP)

        return avg
