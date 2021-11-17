# -*- coding: UTF-8 -*-
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ic.ad56x3r import AD5663R
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
import time


__author__ = 'dongdongzhang@SmartGiant'
__version__ = 'V0.1.3'


elektra_range_table = {
    'ch1_read_current': 0,
    'ch1_read_voltage': 1,
    'ch1_set_cc': 2,
    'ch1_set_cv': 3,
    'ch2_read_current': 4,
    'ch2_read_voltage': 5,
    'ch2_set_cc': 6,
    'ch2_set_cv': 7
}


class ElektraDef:

    CAT9555_ADDR = 0x23
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x4A

    DEFAULT_TIMEOUT = 1  # s
    ADC_VREF_VOLTAGE_5000mV = 5000
    MIXDAQT1_REG_SIZE = 0x8000
    DAC_MV_REF = 5000
    DAC_MODE_REF = "EXTERN"

    # cat9555 pin dir output
    IO_INIT_DIR = [0x00, 0x00]
    # cat9555 bit5, bit9 and bit10 set 1. bit5:SYNC_AD5663R
    # bit9:RST1, bit10:RST2  ,clear over protect state
    IO_INIT_VALUE = [0x20, 0x06]

    # spi bus switch level, Set to 1, spi bus controls ad5663r. Set to 0, spi bus controls ad7175
    AD5663R_PIN_LEVEL = 1
    AD7175_PIN_LEVEL = 0

    # partial voltage resistance  360 / (820 + 360)
    VOLTAGE_COEFFICIENT = 0.305
    # partial voltage resistance  0.05 * (1+49.4/2)
    CURRENT_COEFFICIENT = 1.285
    # partial voltage resistance  8000 * (1/1001) mV
    VOLTAGE_OFFSET = 8
    # partial voltage resistance  8000 * (1/1001) mA
    CURRENT_OFFSET = 8

    HIGH_LEVEL = 1
    LOWE_LEVEL = 0
    CAT9555_BIT = {
        'ON/OFF1': 1,
        'Mode_Select1': 2,
        'ON/OFF2': 3,
        'Mode_Select2': 4,
        'SYNC_AD5663R': 5,
        'CLR_AD5663R': 6,
        'E-LOAD_ON/OFF1': 7,
        'E-LOAD_ON/OFF2': 8,
        'RST1': 9,
        'RST2': 10
    }

    AD7175_A_CHANNEL = 0
    AD7175_B_CHANNEL = 1
    AD7175_C_CHANNEL = 2
    AD7175_D_CHANNEL = 3
    AD7175_CHANNEL_LIST = (AD7175_A_CHANNEL, AD7175_B_CHANNEL, AD7175_C_CHANNEL, AD7175_D_CHANNEL)
    AD7175_DEFAULT_SAMPLING_RATE = 100   # Hz

    VLOT_CH1 = 0
    VLOT_CH2 = 2
    CURR_CH1 = 1
    CURR_CH2 = 3


class ElektraException(Exception):
    def __init__(self, err_str):
        self._err_reason = err_str

    def __str__(self):
        return self._err_reason


class ElektraBase(SGModuleDriver):
    '''
    Base class of Elektra and ElektraCompatible.

    Args:
        i2c:              instance(I2C)/None, instance of I2CBus, which is used to control cat9555, eeprom and nct75.
        spi:              instance(MIXQSPISG)/None, which is used to control AD5663R.
        blade:            instance(Blade)/None, which is used to control AD7608.
        gpio:             instance(GPIO)/None, which is used to control AD5663R pin.
        volt_ch1:         int, AD7608 channel id for read voltage ch1.
        volt_ch2:         int, AD7608 channel id for read voltage ch2.
        curr_ch1:         int, AD7608 channel id for read current ch1.
        curr_ch2:         int, AD7608 channel id for read current ch2.
        eeprom_dev_addr:  int, Eeprom device address.
        sensor_dev_addr:  int, NCT75 device address.
        ipcore:           instance(MIXDAQT1SGR), MIXDAQT1SGR IP driver instance, provide SPI, ad717x and gpio function.
        cat9555_dev_addr: int, CAT9555 device address.
        range_table:      dict, which is ICI calibration range table.

    '''

    rpc_public_api = ['read_voltage', 'read_current', 'set_cc', 'set_cv', 'set_cr',
                      'channel_enable', 'channel_disable', 'reset_board'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c=None, spi=None, blade=None, gpio=None, volt_ch1=2, volt_ch2=3, curr_ch1=0, curr_ch2=1,
                 eeprom_dev_addr=None, sensor_dev_addr=None, ipcore=None, cat9555_dev_addr=ElektraDef.CAT9555_ADDR,
                 range_table=elektra_range_table):

        self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
        self.sensor = NCT75(sensor_dev_addr, i2c)
        self.cat9555 = CAT9555(cat9555_dev_addr, i2c)

        if (i2c is not None and spi is not None and gpio is not None):
            self.spi = spi
            self.spi.set_mode('MODE2')
            self.ad5663 = AD5663R(spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            # if not using wrapper IP, blade is ad7608 IP driver
            self.ad7608 = blade
            self.gpio = gpio
        elif (ipcore is not None and i2c is not None):
            if isinstance(ipcore, basestring):
                daqt1_axi4_bus = AXI4LiteBus(ipcore, ElektraDef.MIXDAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                          ad717x_mvref=ElektraDef.ADC_VREF_VOLTAGE_5000mV,
                                          use_spi=True, use_gpio=False)
                self.spi = self.ipcore.spi
                self.ad7175 = self.ipcore.ad717x
            else:
                self.ipcore = ipcore
                self.spi = self.ipcore.spi
                self.ad7175 = self.ipcore.ad717x

            self.spi.set_mode('MODE2')
            self.ad5663 = AD5663R(self.spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.gpio = None
            if blade:
                self.blade = blade
                self.ad7608 = blade.adc
        else:
            raise ElektraException('__init__ error! Please check the parameters!')

        super(ElektraBase, self).__init__(self.eeprom, self.sensor, range_table=range_table)
        self.adc_voltage_channel = {
            'ch1': volt_ch1,
            'ch2': volt_ch2
        }
        self.adc_current_channel = {
            'ch1': curr_ch1,
            'ch2': curr_ch2
        }

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
        start_time = time.time()

        while True:
            try:
                if self.gpio is not None:
                    self.gpio.set_dir('output')
                    self.gpio.set_level(ElektraDef.AD5663R_PIN_LEVEL)

                self.cat9555.set_pins_dir(ElektraDef.IO_INIT_DIR)
                self.cat9555.set_ports(ElektraDef.IO_INIT_VALUE)

                self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.LOWE_LEVEL)
                self.ad5663.initial()
                self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.HIGH_LEVEL)

                self.ad7608.reset()

                # board reset
                self.reset_board('ch1')
                self.reset_board('ch2')
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise ElektraException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=ElektraDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and disable E-load channel.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.reset_board('ch1')
                self.reset_board('ch2')
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise ElektraException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Elektra driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def _read_adc(self, channel):
        '''
        read Ad7608 average value

        Args:
            channel:  int, [0~7], adc channel num.

        Returns:
            float, value, unit mV.

        Examples:
            elektrabase._read_adc(0)

        '''
        assert channel >= 0 and channel <= 7
        COUNT = 30
        STRIP = 5

        # get average value
        value_list = [self.ad7608.single_sampling(0, '5V')[channel] for _ in range(COUNT)]
        value_list.sort()
        avg = reduce((lambda x, y: x + y), value_list[STRIP:-STRIP], 0) / (COUNT - 2 * STRIP)

        return avg

    def read_voltage(self, channel):
        '''
        Ad7608 voltage read

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.

        Returns:
            float, value, unit mV.

        Examples:
            elektrabase.read_voltage('ch1')

        '''
        assert channel in {'ch1', 'ch2'}

        value = self._read_adc(self.adc_voltage_channel[channel])
        value = value / ElektraDef.VOLTAGE_COEFFICIENT

        value = self.calibrate('%s_read_voltage' % channel, value)

        return value

    def read_current(self, channel):
        '''
        Ad7608 current read

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.

        Returns:
            float, value, unit mV.

        Examples:
            elektrabase.read_current('ch1')

        '''
        assert channel in {'ch1', 'ch2'}
        value = self._read_adc(self.adc_current_channel[channel])
        value = value / ElektraDef.CURRENT_COEFFICIENT

        value = self.calibrate('%s_read_current' % channel, value)

        return value

    def _output_voltage(self, channel, value):
        '''
        DAC ad5663r output.

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.
            value:    float, [0~5000], dac output value unit 'mV', eg.1000.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase._output_voltage(1, 1000)

        '''
        assert channel in {'ch1', 'ch2'}
        assert value <= 5000
        DAC_CHANEL = {'ch1': 0, 'ch2': 1}

        if value < 0:
            value = 0

        if self.gpio is not None:
            self.gpio.set_level(ElektraDef.AD5663R_PIN_LEVEL)

        self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.HIGH_LEVEL)
        self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.LOWE_LEVEL)
        self.ad5663.output_volt_dc(DAC_CHANEL[channel], value)
        self.cat9555.set_pin(ElektraDef.CAT9555_BIT['SYNC_AD5663R'], ElektraDef.HIGH_LEVEL)

        return "done"

    def set_cc(self, channel, value):
        '''
        CC(constant-current) mode set

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.
            value:    float, [1~3500], unit mA, CC mode current.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.set_cc('ch1', 10)

        '''
        assert channel in {'ch1', 'ch2'}
        assert isinstance(value, (int, float))

        value = self.calibrate('%s_set_cc' % channel, value)

        # Iset = a * value + offset, a is coefficent
        Iset = value * ElektraDef.CURRENT_COEFFICIENT + ElektraDef.CURRENT_OFFSET
        io_set = ElektraDef.CAT9555_BIT['Mode_Select' + channel[2:3]]

        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)

        self._output_voltage(channel, Iset)

        return "done"

    def set_cv(self, channel, value):
        '''
        CV(constant-voltage) mode set

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.
            value:    float, [500~5500], unit mV, CV mode voltage, eg.1000.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.set_cv('ch1', 10)

        '''
        assert channel in {'ch1', 'ch2'}
        assert isinstance(value, (int, float))

        value = self.calibrate('%s_set_cv' % channel, value)

        # Vset = a * value + offset, a is coefficent
        Vset = value * ElektraDef.VOLTAGE_COEFFICIENT + ElektraDef.VOLTAGE_OFFSET
        io_set = ElektraDef.CAT9555_BIT['Mode_Select' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.HIGH_LEVEL)

        self._output_voltage(channel, Vset)

        return "done"

    def set_cr(self, channel, value):
        '''
        CR(constant-resistance) mode set, just set one time not loop

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.
            value:    float, [1.6~500], unit Ohm, CR mode resistance, eg.100.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.set_cr('ch1', 10)

        '''
        assert channel in {'ch1', 'ch2'}
        assert isinstance(value, (int, float))

        voltage = self.read_voltage(channel)
        # I = U / R
        current = voltage / value

        # Iset = a * current + offset, a is coefficent
        Iset = current * ElektraDef.CURRENT_COEFFICIENT + ElektraDef.CURRENT_OFFSET

        Iset = self.calibrate('%s_set_cc' % channel, Iset)

        io_set = ElektraDef.CAT9555_BIT['Mode_Select' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)

        self._output_voltage(channel, Iset)

        return "done"

    def channel_enable(self, channel):
        '''
        channel enable, Gate_switch and E-load_switch ON

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.channel_enable('ch1')

        '''
        assert channel in {'ch1', 'ch2'}

        self.channel_disable(channel)
        io_set = ElektraDef.CAT9555_BIT['ON/OFF' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.HIGH_LEVEL)
        io_set = ElektraDef.CAT9555_BIT['E-LOAD_ON/OFF' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.HIGH_LEVEL)

        return "done"

    def channel_disable(self, channel):
        '''
        channel disable, Gate_switch and E-load_switch OFF

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.channel_disable('ch1')

        '''
        assert channel in {'ch1', 'ch2'}

        io_set = ElektraDef.CAT9555_BIT['ON/OFF' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)
        io_set = ElektraDef.CAT9555_BIT['E-LOAD_ON/OFF' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)
        io_set = ElektraDef.CAT9555_BIT['Mode_Select' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)
        self._output_voltage(channel, 0)

        return "done"

    def reset_board(self, channel):
        '''
        board reset, clear over protect state and disable

        Args:
            channel:  string, ['ch1', 'ch2'], adc channel name.

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.reset_board('ch1')

        '''
        assert channel in {'ch1', 'ch2'}

        self.channel_disable(channel)
        io_set = ElektraDef.CAT9555_BIT['RST' + channel[2:3]]
        self.cat9555.set_pin(io_set, ElektraDef.LOWE_LEVEL)
        self.cat9555.set_pin(io_set, ElektraDef.HIGH_LEVEL)

        return "done"


class Elektra(ElektraBase):
    '''
    The Elektra(el-004-001) is a two-channel dc electronic load.

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
        blade = Scope007002()
        io = GPIO(86, "output")
        gpio = Pin(io, 86, "output")

        elektra = Elektra(i2c, spi, blade, gpio)

    '''

    def __init__(self, i2c=None, spi=None, blade=None, gpio=None,
                 volt_ch1=0, volt_ch2=2, curr_ch1=1, curr_ch2=3, ipcore=None):
        super(Elektra, self).__init__(i2c, spi, blade, gpio,
                                      volt_ch1, volt_ch2, curr_ch1, curr_ch2,
                                      ElektraDef.EEPROM_DEV_ADDR, ElektraDef.SENSOR_DEV_ADDR,
                                      ipcore, ElektraDef.CAT9555_ADDR)
