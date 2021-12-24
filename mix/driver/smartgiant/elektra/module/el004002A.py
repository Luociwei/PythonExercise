# -*- coding: utf-8 -*-
from elektra import ElektraBase
from elektra import ElektraDef
from elektra import ElektraException
from elektra import elektra_calibration_info
from elektra import elektra_range_table
from mix.driver.core.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ic.ad56x3r import AD5663R
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator


__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.2'


class EL004002A(ElektraBase):
    '''
    The Eload004002A is a two-channel dc electronic load.Each channel has the function of CC,CV and CR,
    and also has the function of voltage and current measurement.

    Args:
        i2c:              instance(I2C)/None,  If not given, PLI2CBus emulator will be created.
        spi:              instance(QSPI)/None, if not given, PLSPIBus emulator will be created.
        ad7175:           instance(ADC)/None,  If not given, ad7175 emulator will be created.
        gpio:             instance(GPIO)/None, If not given, PinEmulator emulator will be created.
        volt_ch1:         int, default 2, ADC channel id for read voltage ch1.
        volt_ch2:         int, default 3, ADC channel id for read voltage ch2.
        curr_ch1:         int, default 0, ADC channel id for read current ch1.
        curr_ch2:         int, default 1, ADC channel id for read current ch2.
        ipcore:           instance(MIXDAQT1SGR)/None,, If not given, relative instance will be created by judgically.

    Examples:
        Example for using no-aggregated IP:
            axi4 = AXI4LiteBus('/dev/AXI4_I2C_8', 256)
            i2c = PLI2CBus(axi4)
            axi4 = AXI4LiteBus('/dev/AXI4_SPI_0', 8192)
            spi = PLSPIBus(axi4)
            axi4 = AXI4LiteBus('/dev/AXI4_AD7175_0', 8192)
            ad7175 = PLAD7175(axi4)
            axi4 = AXI4LiteBus('/dev/AXI4_GPIO_0', 256)
            io_instance = PLGPIO(axi4)
            gpio = Pin(io_instance, 0)
            elektra = Eload004002(i2c, spi, ad7175, gpio)

        Example for using aggregated IP:
            daqt1 = MIXDAQT1('/dev/MIX_AUT1_0')
            i2c_bus = I2C('/dev/i2c-1')
            elektra = Eload004002(i2c=i2c_bus, ip=daqt1)

        Example of set cv/cc & read voltage/current, set cr:
            elektra.module_init()
            elektra.channel_enable("ch1")
            elektra.set_cv("ch1", 200)  # elektra.set_cc("ch1", 100)
            elektra.read_voltage("ch1") # elektra.read_current("ch1")

            elektra.set_cr("ch1", 200)

    '''

    compatible = ['GQQ-EL0004002-00A']

    def __init__(self, i2c=None, spi=None, ad7175=None, gpio=None, ipcore=None):
        super(EL004002A, self).__init__(None, None, None, None, ElektraDef.VLOT_CH1, ElektraDef.VLOT_CH2,
                                        ElektraDef.CURR_CH1, ElektraDef.CURR_CH2,
                                        ElektraDef.EEPROM_DEV_ADDR, ElektraDef.SENSOR_DEV_ADDR)
        if ipcore:
            self.ad7175 = ipcore.ad717x
            self.spi = ipcore.spi
            self.ad5663 = AD5663R(ipcore.spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.gpio = None
        else:
            self.spi = spi or MIXQSPISGEmulator("mix_qspi_sg_emulator", ElektraDef.PLSPIBUS_EMULATOR_REG_SIZE)
            self.ad7175 = ad7175 or MIXAd7175SGEmulator("mix_ad7175_sg_emulator", ElektraDef.AD7175_EMULATOR_REG_SIZE)
            self.ad5663 = AD5663R(spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.gpio = gpio or GPIOEmulator("gpio_emulator")

        if i2c:
            self.cat9555 = CAT9555(ElektraDef.CAT9555_ADDR, i2c)
            self.eeprom = CAT24C32(ElektraDef.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(ElektraDef.SENSOR_DEV_ADDR, i2c)
        else:
            self.cat9555 = CAT9555Emulator(ElektraDef.CAT9555_ADDR, None, None)
            self.eeprom = None
            self.sensor = None

        super(ElektraBase, self).__init__(self.eeprom, self.sensor,
                                          cal_table=elektra_calibration_info, range_table=elektra_range_table)

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN4"},
            "ch1": {"P": "AIN1", "N": "AIN4"},
            "ch2": {"P": "AIN2", "N": "AIN4"},
            "ch3": {"P": "AIN3", "N": "AIN4"}
        }

        self.spi.set_mode('MODE2')

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

    def module_init(self):
        '''
        Configure GPIO pin default direction and values, initial ad5663 and reset ad7175.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.module_init()

        Raise:
            ElektraException:  communication with ad7175 failed!

        '''
        self.load_calibration()
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

        return 'done'
