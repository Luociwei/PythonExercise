# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator

__author__ = 'yongjiu.tan@SmartGiant'
__version__ = '0.1'


class AD5592RDef:
    SPI_MODE = 'MODE2'
    SPI_SPEED = 5000000     # 5 MHz

    REGISTER_OFFSET = 11
    REGISTER_DATA_MASK = 0x7FF  # 11 bits

    DUMMY_DATA = 0

    MIN_REGISTER = 0
    MAX_REGISTER = 15

    REGISTER_NOP = 0
    REGISTER_DAC_READBACK = 1
    REGISTER_ADC_SEQUENCE = 2
    REGISTER_GENERAL_PURPOSE_CONTROL = 3
    REGISTER_ADC_PIN_CONFIG = 4
    REGISTER_DAC_PIN_CONFIG = 5
    REGISTER_PULL_DOWN_CONFIG = 6
    REGISTER_READBACK_LDAC_MODE = 7
    REGISTER_GPIO_WRITE_CONFIG = 8
    REGISTER_GPIO_WRITE_DATA = 9
    REGISTER_GPIO_READ_CONFIG = 10
    REGISTER_POWERDOWN_REFERENCY = 11
    REGISTER_GPIO_OPEN_DRAIN_CONFIG = 12
    REGISTER_THREE_STATE_CONFIG = 13
    REGISTER_RESERVED = 14
    REGISTER_SOFTWARE_RESET = 15

    REGISTER_MODE_REGISTER_LIST = [
        REGISTER_DAC_PIN_CONFIG,
        REGISTER_ADC_PIN_CONFIG,
        REGISTER_GPIO_WRITE_CONFIG,
        REGISTER_GPIO_READ_CONFIG,
        REGISTER_GPIO_OPEN_DRAIN_CONFIG,
        REGISTER_THREE_STATE_CONFIG,
        REGISTER_PULL_DOWN_CONFIG
    ]

    MIN_CHANNEL = 0
    MAX_CHANNEL = 7

    DAC_CHANNEL_BASEADDR = 8
    DAC_CHANNEL_OFFSET = 12     # 12 bits
    DAC_DATA_MASK = 0xFFF
    DAC_READ_BACK_ENABLE = 0b11000     # bit4=1, bit3=1 to enable readback
    DAC_READ_BACK_DISABLE = 0b00000    # bit4=0, bit3=0 to disable readback

    ADC_CHANNEL_OFFSET = 12
    ADC_DATA_MASK = 0xFFF   # 12 bits

    GAIN_1 = 1
    GAIN_2 = 2

    RESET_COMMAND = 0b0111110110101100

    MODE_DAC = 'DAC'
    MODE_ADC = 'ADC'
    MODE_OUTPUT = 'OUTPUT'
    MODE_INPUT = 'INPUT'
    MODE_OPEN_DRAIN_OUTPUT = 'OPEN_DRAIN_OUTPUT'
    MODE_THREE_STATE = 'THREE_STATE'
    MODE_PULLDOWN_85KOHM = 'PULLDOWN_85KOHM'
    MODE_LIST = [MODE_DAC, MODE_ADC, MODE_OUTPUT, MODE_INPUT,
                 MODE_OPEN_DRAIN_OUTPUT, MODE_THREE_STATE, MODE_PULLDOWN_85KOHM]

    REFERENCY_INTERNAL = 'internal'
    REFERENCY_EXTERNAL = 'external'
    REFERENCY_LIST = [REFERENCY_EXTERNAL, REFERENCY_INTERNAL]


class AD5592RException(Exception):
    def __init__(self, err_str):
        self.err_reason = 'AD5592R: %s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD5592R(object):
    '''
    AD5592R function class, 8 channel 12bit ADC/DAC, per support ADC, DAC or GPIO,
    default pulldown 85 KOhm when powerup or reset.

    ClassType = ADC/DAC

    Args:
        spi_bus:     instance(QSPI)/None,  MIXQSPISG class instance, if not using, will create emulator.
        mvref:       int, default 5000,             reference voltage.
        ref_mode:    string, default 'external',    reference mode, external or internal, default=external.
        adc_gain:    int, [1, 2], default 1,     ADC voltage range gain.
        dac_gain:    int, [1, 2], default 1,     DAC voltage range gain, default=1.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_SPI_0', 256)
        spi_bus = MIXQSPISG(axi4_bus)
        mvref = 5000
        ad5592r = AD5592R(spi_bus, mvref)

    '''

    def __init__(self, spi_bus=None, mvref=5000, ref_mode='external', adc_gain=1, dac_gain=1):
        self.spi = spi_bus if spi_bus is not None else MIXQSPISGEmulator('mix_qspi_sg_emulator', 64)
        self.mvref = mvref
        self.ref_mode = ref_mode
        self.adc_gain = adc_gain
        self.dac_gain = dac_gain

        self.spi.set_mode(AD5592RDef.SPI_MODE)
        self.spi.set_speed(AD5592RDef.SPI_SPEED)

        self.reset()

    def spi_write(self, data):
        '''
        spi write 16bit data

        Args:
            data:    int, [0~0xFFFF].

        Examples:
            ad5592r.spi_write(123)

        '''
        assert isinstance(data, int)
        assert data >= 0
        assert data <= 0xFFFF

        write_list = [data >> 8, data & 0xFF]      # high 8 bit first send
        self.spi.write(write_list)

    def spi_read(self):
        '''
        spi read 16bit data

        Returns:
            int, value, 16 bit data.

        Examples:
            print ad5592r.spi_read()

        '''
        read_list = self.spi.transfer([AD5592RDef.DUMMY_DATA, AD5592RDef.DUMMY_DATA], 2)           # read 2 Bytes
        read_data = (read_list[0] << 8) + read_list[1]     # high 8 bit first read

        return read_data

    def register_write(self, register, data):
        '''
        write data to control register

        Args:
            register:    int, [0~15], register address.
            data:        int, [0~0x7FF], register data, 11 bits.

        Examples:
            ad5592r.register_write(2, 0)

        '''
        assert isinstance(register, int)
        assert isinstance(data, int)
        assert register >= AD5592RDef.MIN_REGISTER
        assert register <= AD5592RDef.MAX_REGISTER
        assert data >= 0
        assert data <= 0x7FF

        write_data = (register << AD5592RDef.REGISTER_OFFSET) + data
        self.spi_write(write_data)

    def register_read(self, register):
        '''
        read data from control register

        Args:
            register:    int, [0~15], register address.

        Returns:
            int, [0~0x7FF], register data, 11 bits.

        Examples:
            ad5592r.register_read(2)

        '''
        assert isinstance(register, int)
        assert register >= AD5592RDef.MIN_REGISTER
        assert register <= AD5592RDef.MAX_REGISTER

        write_data = (1 << 6) | (register << 2)     # bit6=1 to enable readback
        self.register_write(AD5592RDef.REGISTER_READBACK_LDAC_MODE, write_data)

        read_data = self.spi_read()

        return read_data & AD5592RDef.REGISTER_DATA_MASK

    def reset(self):
        '''
        soft reset chip, I/O*8 all pulldown to  85 KOhm

        Examples:
            ad5592r.reset()

        '''
        self.spi_write(AD5592RDef.RESET_COMMAND)
        self.gain_set(self.adc_gain, self.dac_gain)
        self.reference = self.ref_mode

    @property
    def reference(self):
        '''
        AD5592R get mode of reference voltage

        Returns:
            string, ['internal', 'external'].

        Examples:
            result = ad5592r.reference

        '''

        read_data = self.register_read(AD5592RDef.REGISTER_POWERDOWN_REFERENCY)
        # POWERDOWN_REFERENCY register bit9, 0 is external, 1 is internal
        ref_mode = (read_data >> 9) & 1
        return AD5592RDef.REFERENCY_LIST[ref_mode]

    @reference.setter
    def reference(self, ref_mode):
        '''
        AD5592R set mode of reference voltage

        Args:
            ref_mode:  string, ["internal, "external"], default is "external".

        Examples:
            ad5592r.reference("external")

        '''
        assert ref_mode in AD5592RDef.REFERENCY_LIST

        read_data = self.register_read(AD5592RDef.REGISTER_POWERDOWN_REFERENCY)

        # set POWERDOWN_REFERENCY register bit9, 0 is external, 1 is internal
        write_data = read_data & ~(1 << 9) | (AD5592RDef.REFERENCY_LIST.index(ref_mode) << 9)

        self.register_write(AD5592RDef.REGISTER_POWERDOWN_REFERENCY, write_data)

    def gain_set(self, adc_gain, dac_gain):
        '''
        config ADC and DAC range gain

        Args:
            adc_gain:    int, [1, 2], ADC range gain.
            dac_gain:    int, [1, 2], DAC range gain.

        Examples:
            ad5592r.gain_set(1, 2)

        '''
        assert isinstance(adc_gain, int)
        assert isinstance(dac_gain, int)
        assert adc_gain in [AD5592RDef.GAIN_1, AD5592RDef.GAIN_2]
        assert dac_gain in [AD5592RDef.GAIN_1, AD5592RDef.GAIN_2]

        # bit4 set 0 or 1 means dac gain is 1 or 2, likewise bit5 set adc gain
        bit4 = dac_gain >> 1
        bit5 = adc_gain >> 1
        write_data = (bit5 << 5) | (bit4 << 4)
        self.register_write(AD5592RDef.REGISTER_GENERAL_PURPOSE_CONTROL, write_data)

        self.adc_gain = adc_gain
        self.dac_gain = dac_gain

    def channel_config(self, channel, mode):
        '''
        set pin mode to ADC, DAC or GPIO

        Args:
            channel:     int, [0~7], channel id.
            mode:        string, ['DAC', 'ADC', 'INPUT', 'OUTPUT', 'OPEN_DRAIN_OUTPUT',
                                  'THREE_STATE', 'PULLDOWN_85KOHM'], eg.'INPUT'.

        Examples:
            ad5592r.channel_config(1, 'DAC')

        '''
        assert isinstance(channel, int)
        assert isinstance(mode, (str, unicode))
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL
        assert mode in AD5592RDef.MODE_LIST

        if mode == AD5592RDef.MODE_ADC:
            register = AD5592RDef.REGISTER_ADC_PIN_CONFIG
        elif mode == AD5592RDef.MODE_DAC:
            register = AD5592RDef.REGISTER_DAC_PIN_CONFIG
        elif mode == AD5592RDef.MODE_INPUT:
            register = AD5592RDef.REGISTER_GPIO_READ_CONFIG
        elif mode == AD5592RDef.MODE_OUTPUT:
            register = AD5592RDef.REGISTER_GPIO_WRITE_CONFIG
        elif mode == AD5592RDef.MODE_OPEN_DRAIN_OUTPUT:
            register = AD5592RDef.REGISTER_GPIO_OPEN_DRAIN_CONFIG
        elif mode == AD5592RDef.MODE_THREE_STATE:
            register = AD5592RDef.REGISTER_THREE_STATE_CONFIG
        else:
            register = AD5592RDef.REGISTER_PULL_DOWN_CONFIG

        # clean legacy config for single channel
        for i in AD5592RDef.REGISTER_MODE_REGISTER_LIST:
            read_data = self.register_read(i)
            write_data = read_data & ~(1 << channel) | (0 << channel)
            self.register_write(i, write_data)

        read_data = self.register_read(register)
        write_data = read_data | (1 << channel)
        self.register_write(register, write_data)

    def output_volt_dc(self, channel, volt):
        '''
        output dc voltage, 12bit dac

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, output voltage value.

        Examples:
            ad5592r.output_volt_dc(0, 1000)

        '''
        assert isinstance(channel, int)
        assert isinstance(volt, (int, float))
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL
        assert volt >= 0
        assert volt <= (self.mvref * self.dac_gain)

        def volt_to_code(volt):
            '''volt to code, 12bit'''
            code = float(volt) / (self.mvref * self.dac_gain) * AD5592RDef.DAC_DATA_MASK
            return int(code)

        write_data = ((AD5592RDef.DAC_CHANNEL_BASEADDR + channel) << AD5592RDef.DAC_CHANNEL_OFFSET) + volt_to_code(volt)

        self.spi_write(write_data)

        '''read back verify'''
        self.register_write(AD5592RDef.REGISTER_DAC_READBACK, AD5592RDef.DAC_READ_BACK_ENABLE + channel)

        read_data = self.spi_read()

        if write_data != read_data:
            raise AD5592RException('DAC set fail!')

        self.register_write(AD5592RDef.REGISTER_DAC_READBACK, AD5592RDef.DAC_READ_BACK_DISABLE + channel)

    def read_volt(self, channel):
        '''
        AD5592R read input voltage

        Args:
            channel:     int, [0~7], channel id.

        Returns:
            float, value, unit mV.

        Examples:
            volt = ad5592r.read_volt(0)
            print(volt)

        '''
        assert isinstance(channel, int)
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL

        self.register_write(AD5592RDef.REGISTER_ADC_SEQUENCE, 1 << channel)

        '''read the second data valid'''
        self.spi_read()

        read_data = self.spi_read()

        readback_channel = (read_data >> AD5592RDef.ADC_CHANNEL_OFFSET)
        if channel != readback_channel:
            raise AD5592RException('ADC read fail!')

        volt_code = read_data & AD5592RDef.ADC_DATA_MASK
        volt = float(volt_code) / AD5592RDef.ADC_DATA_MASK * self.mvref * self.adc_gain

        return volt
