# -*- coding: UTF-8 -*-
import struct

from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.module.mix_board import ICIDef
from mix.driver.smartgiant.common.module.mix_board import ICIException
from mix.driver.core.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.ic.ad56x3r import AD5663R
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ipcore.mix_ad760x_sg_emulator import MIXAD760XSGEmulator


__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.3'

elektra_calibration_base_addr = {
    'ch1_read_voltage': 0x301,
    'ch1_read_current': 0x201,
    'ch1_set_cc': 0x401,
    'ch1_set_cv': 0x501,
    'ch2_read_voltage': 0x701,
    'ch2_read_current': 0x601,
    'ch2_set_cc': 0x801,
    'ch2_set_cv': 0x901
}


elektra_calibration_info = {
    'ch1_read_voltage': {
        'level1': {'unit_index': 0, 'limit': (500, 'mV')},
        'level2': {'unit_index': 1, 'limit': (1000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (2500, 'mV')},
        'level4': {'unit_index': 3, 'limit': (5000, 'mV')},
        'level5': {'unit_index': 4, 'limit': (7500, 'mV')},
        'level6': {'unit_index': 5, 'limit': (10000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (12500, 'mV')},
        'level8': {'unit_index': 7, 'limit': (16000, 'mV')}
    },
    'ch1_read_current': {
        'level1': {'unit_index': 0, 'limit': (100, 'mA')},
        'level2': {'unit_index': 1, 'limit': (500, 'mA')},
        'level3': {'unit_index': 2, 'limit': (1000, 'mA')},
        'level4': {'unit_index': 3, 'limit': (1500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (2000, 'mA')},
        'level6': {'unit_index': 5, 'limit': (2500, 'mA')},
        'level7': {'unit_index': 6, 'limit': (3000, 'mA')},
        'level8': {'unit_index': 7, 'limit': (3600, 'mA')}
    },
    'ch1_set_cv': {
        'level1': {'unit_index': 0, 'limit': (650, 'mV')},
        'level2': {'unit_index': 1, 'limit': (1000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (2000, 'mV')},
        'level4': {'unit_index': 3, 'limit': (3000, 'mV')},
        'level5': {'unit_index': 4, 'limit': (4000, 'mV')},
        'level6': {'unit_index': 5, 'limit': (5000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (6000, 'mV')}
    },
    'ch1_set_cc': {
        'level1': {'unit_index': 0, 'limit': (100, 'mA')},
        'level2': {'unit_index': 1, 'limit': (500, 'mA')},
        'level3': {'unit_index': 2, 'limit': (1000, 'mA')},
        'level4': {'unit_index': 3, 'limit': (1500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (2000, 'mA')},
        'level6': {'unit_index': 5, 'limit': (2500, 'mA')},
        'level7': {'unit_index': 6, 'limit': (3000, 'mA')},
        'level8': {'unit_index': 7, 'limit': (3600, 'mA')}
    },
    'ch2_read_voltage': {
        'level1': {'unit_index': 0, 'limit': (500, 'mV')},
        'level2': {'unit_index': 1, 'limit': (1000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (2500, 'mV')},
        'level4': {'unit_index': 3, 'limit': (5000, 'mV')},
        'level5': {'unit_index': 4, 'limit': (7500, 'mV')},
        'level6': {'unit_index': 5, 'limit': (10000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (12500, 'mV')},
        'level8': {'unit_index': 7, 'limit': (16000, 'mV')}
    },
    'ch2_read_current': {
        'level1': {'unit_index': 0, 'limit': (100, 'mA')},
        'level2': {'unit_index': 1, 'limit': (500, 'mA')},
        'level3': {'unit_index': 2, 'limit': (1000, 'mA')},
        'level4': {'unit_index': 3, 'limit': (1500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (2000, 'mA')},
        'level6': {'unit_index': 5, 'limit': (2500, 'mA')},
        'level7': {'unit_index': 6, 'limit': (3000, 'mA')},
        'level8': {'unit_index': 7, 'limit': (3600, 'mA')}
    },
    'ch2_set_cv': {
        'level1': {'unit_index': 0, 'limit': (650, 'mV')},
        'level2': {'unit_index': 1, 'limit': (1000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (2000, 'mV')},
        'level4': {'unit_index': 3, 'limit': (3000, 'mV')},
        'level5': {'unit_index': 4, 'limit': (4000, 'mV')},
        'level6': {'unit_index': 5, 'limit': (5000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (6000, 'mV')}
    },
    'ch2_set_cc': {
        'level1': {'unit_index': 0, 'limit': (100, 'mA')},
        'level2': {'unit_index': 1, 'limit': (500, 'mA')},
        'level3': {'unit_index': 2, 'limit': (1000, 'mA')},
        'level4': {'unit_index': 3, 'limit': (1500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (2000, 'mA')},
        'level6': {'unit_index': 5, 'limit': (2500, 'mA')},
        'level7': {'unit_index': 6, 'limit': (3000, 'mA')},
        'level8': {'unit_index': 7, 'limit': (3600, 'mA')}
    }
}

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

    # PLGPIOEmulator reg_size
    PL_GPIO_REG_SIZE = 256

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

    CAL_DATA_LEN = 16
    WRITE_CAL_DATA_PACK_FORMAT = "3f4B"
    WRITE_CAL_DATA_UNPACK_FORMAT = "16B"

    READ_CAL_BYTE = 16
    READ_CAL_DATA_PACK_FORMAT = "16B"
    READ_CAL_DATA_UNPACK_FORMAT = "3f4B"

    PLSPIBUS_EMULATOR_REG_SIZE = 8192
    AD7175_EMULATOR_REG_SIZE = 256
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


class ElektraBase(MIXBoard):
    '''
    Base class of Elektra and ElektraCompatible.

    Args:
        i2c:              instance(I2C)/None,  If not given, PLI2CBus emulator will be created.
        spi:              instance(QSPI)/None, if not given, PLSPIBus emulator will be created.
        ad7608:           instance(ADC)/None,  If not given, AD760X emulator will be created.
        gpio:             instance(GPIO)/None, If not given, PinEmulator emulator will be created.
        volt_ch1:         int, ADC channel id for read voltage ch1.
        volt_ch2:         int, ADC channel id for read voltage ch2.
        curr_ch1:         int, ADC channel id for read current ch1.
        curr_ch2:         int, ADC channel id for read current ch2.
        eeprom_dev_addr:  int, Eeprom device address.
        sensor_dev_addr:  int, NCT75 device address.
        ipcore:           instance(MIXDAQT1SGR), MIXDAQT1SGR IP driver instance, provide QSPI, ad717x
                                                 and gpio function.

    '''

    rpc_public_api = ['module_init', 'read_voltage', 'read_current', 'set_cc',
                      'set_cv', 'set_cr', 'channel_enable', 'channel_disable',
                      'reset_board'] + MIXBoard.rpc_public_api

    def __init__(self, i2c=None, spi=None, ad7608=None, gpio=None, volt_ch1=2, volt_ch2=3, curr_ch1=0, curr_ch2=1,
                 eeprom_dev_addr=None, sensor_dev_addr=None, ipcore=None):

        self.ipcore = ipcore
        if (i2c is not None and spi is not None and ad7608 is not None and gpio is not None):
            spi.set_mode('MODE2')
            self.cat9555 = CAT9555(ElektraDef.CAT9555_ADDR, i2c)
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.sensor = NCT75(sensor_dev_addr, i2c)
            self.ad5663 = AD5663R(spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.ad7608 = ad7608
            self.gpio = gpio
        elif (ipcore is not None and i2c is not None):
            self.spi = ipcore.spi
            self.spi.set_mode('MODE2')
            self.ad5663 = AD5663R(ipcore.spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.gpio = None
            self.cat9555 = CAT9555(ElektraDef.CAT9555_ADDR, i2c)
            self.eeprom = CAT24C32(ElektraDef.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(ElektraDef.SENSOR_DEV_ADDR, i2c)
            self.ad7608 = ad7608 or MIXAD760XSGEmulator("mix_ad760x_sg_emulator")
        elif (i2c is None and spi is None and ad7608 is None and gpio is None):
            self.cat9555 = CAT9555Emulator(ElektraDef.CAT9555_ADDR, None, None)
            self.eeprom = None
            self.sensor = None
            self.ad5663 = AD5663R(spi, ElektraDef.DAC_MV_REF, ElektraDef.DAC_MODE_REF)
            self.ad7608 = MIXAD760XSGEmulator("mix_ad760x_sg_emulator")
            self.gpio = GPIOEmulator("gpio_emulator")
        else:
            raise ElektraException('__init__ error! Please check the parameters!')
        super(ElektraBase, self).__init__(self.eeprom, self.sensor,
                                          cal_table=elektra_calibration_info, range_table=elektra_range_table)
        self.adc_voltage_channel = {
            'ch1': volt_ch1,
            'ch2': volt_ch2
        }
        self.adc_current_channel = {
            'ch1': curr_ch1,
            'ch2': curr_ch2
        }

    def module_init(self):
        '''
        Configure GPIO pin default direction and values, initial ad5663 and reset ad7608

        Returns:
            string, "done", api execution successful.

        Examples:
            elektrabase.module_init()

        '''
        self.load_calibration()

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

        return 'done'

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

    def load_legacy_ici_calibration(self):
        '''
        Load ICI calibration data.
        Refactoring mix_board load_legacy_ici_calibration function
        (get item count address, use little endian byte order)

        This function is used to load calibration data defined by ICI Spec 2.7

        '''
        self._calibration_table = {}
        # get calibration base address
        try:
            base_addr = self.read_legacy_ici_cal_start_addr() + ICIDef.CAL_VERSION_SIZE
        except Exception as e:
            self._cal_common_error = e
            return "done"

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            # get range address
            addr = base_addr + index * ICIDef.CAL_RANGE_LEN
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                continue
            data = self.read_eeprom(addr, ICIDef.CAL_RANGE_LEN)
            # get item count address, use little endian byte order
            addr = (data[1] << 8) | data[0]
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                continue
            count = self.read_eeprom(addr, 1)[0]
            # get cal cell address
            addr += ICIDef.CAL_COUNT_LEN
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                self._cal_common_error = ICIException("Range {} cell address 0x{:x} "
                                                      "is invalid".format(range_name, addr))
                continue
            if addr + count > ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                self._cal_common_error = ICIException("Range {} cell count {} is invalid".format(range_name, count))
                continue

            for i in range(count):
                data = self.read_eeprom(addr, ICIDef.CAL_CELL_LEN)
                addr = addr + ICIDef.CAL_CELL_LEN
                s = struct.Struct('16B')
                pack_data = s.pack(*data)

                s = struct.Struct('3f4B')
                result = s.unpack(pack_data)
                if result[3] != ICIDef.CAL_SAVE_FLAG:
                    self._calibration_table[range_name].append({'gain': 1.0, "offset": 0.0,
                                                                "threshold": 0.0, "is_use": False})
                else:
                    self._calibration_table[range_name].append({"gain": result[0], "offset": result[1],
                                                                "threshold": result[2], "is_use": True})
        return "done"


class Elektra(ElektraBase):
    '''
    The Elektra(el-004-001) is a two-channel dc electronic load.

    compatible = ["GQQ-EL0004001-000"]

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
    compatible = ["GQQ-EL0004001-000"]

    def __init__(self, i2c=None, spi=None, ad7608=None, gpio=None,
                 volt_ch1=0, volt_ch2=2, curr_ch1=1, curr_ch2=3, ipcore=None):
        super(Elektra, self).__init__(i2c, spi, ad7608, gpio, volt_ch1, volt_ch2, curr_ch1, curr_ch2,
                                      ElektraDef.EEPROM_DEV_ADDR, ElektraDef.SENSOR_DEV_ADDR, ipcore)
