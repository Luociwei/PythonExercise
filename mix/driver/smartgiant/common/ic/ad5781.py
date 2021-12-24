# -*- coding: utf-8 -*-

__author__ = 'hongshen.wang@SmartGiant'
__version__ = '0.1'


class AD5781Def:

    DAC_REGISTER = 0x1
    CONTROL_REGISTER = 0x2

    READBACK_DAC_REGISTER = 0x9
    READBACK_CONTROL_REGISTER = 0xa
    READBACK_CLEAR_REGISTER = 0xb

    DAC_REGISTER_WIDTH = 18
    # "MODE2" means CPOL=1, CPHA=0
    SPI_MODE = "MODE2"


class AD5781Exception(Exception):
    '''
    AD5781Exception shows the exception of AD5781

    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD5781(object):
    '''
    AD5781 class provide function write and read register output voltage

    ClassType = DAC

    Args:
        mvref_p:      int,    Positive Reference Voltage Input.
        mvref_n:      int,    Negative Reference Voltage Input.
        spi_bus:      instance(QSPI),  MIXQSPISG class instance.

    Example for AD5781 output voltage 1000 mV, reference voltage 2048 mV.

    Examples:
       axi = AXI4LiteBus("/dev/XXX", 256)
       spi_bus = MIXQSPISG(axi)
       ad5781 = AD5781(2048, 0, spi_bus)
       ad5781.output_volt_dc(1000)
    '''
    def __init__(self, mvref_p, mvref_n, spi_bus=None):

        self.spi_bus = spi_bus
        self.spi_bus.set_mode(AD5781Def.SPI_MODE)
        self.data_width = AD5781Def.DAC_REGISTER_WIDTH

        self.mvref_p = mvref_p
        self.mvref_n = mvref_n

    def write_register(self, reg_addr, reg_data):
        '''
        AD5781 function write value to register

        Args:
            reg_addr:     hexmial(0x00~0x04),   Register address
            reg_data:     hexmial(0x00~0x0FFFFF), Write to the register

        Examples:
                   ad5781.write_register(0x01, 0xff)
        '''
        assert isinstance(reg_addr, int) and isinstance(reg_data, int)
        assert (reg_addr >= 0) and (reg_addr <= AD5781Def.READBACK_CLEAR_REGISTER)
        assert (reg_data >= 0x0) and (reg_data <= 0x00FFFFFF)

        # the high 4 bit is valid in reg_addr
        write_data = [(reg_addr << 4) | ((reg_data >> 16) & 0x0F),
                      (reg_data >> 8) & 0xFF,
                      (reg_data) & 0xFF]
        self.spi_bus.write(write_data)

    def read_register(self, reg_addr):
        '''
        AD5781 function to read register

        Args:
            reg_addr:    hexmial(0x00~0xff), Register address

        Returns:
            list  data read from register address.

        Examples:
            ad5781.read_register(0x22)
        '''
        assert isinstance(reg_addr, int) and reg_addr >= 0

        # tell the ad5781 the address we are going to read,
        # 0x0 is invalid, use 0x0 to put together to 3 bytes.
        self.write_register(reg_addr, 0x0)

        # register width is 24 bits wide, 3 bytes
        read_data_list = self.spi_bus.read(3)
        if not read_data_list:
            raise AD5781Exception(
                "An error occurred when read data from AD5781 register ")

        return read_data_list

    def output_volt_dc(self, volt):
        '''
        AD5781 function set output voltage

        Args:
            volt:    int(0~Vref), unit is mV

        Examples:
                  ad5781.output_volt_dc(500)
        '''
        assert isinstance(volt, (float, int))

        code = (volt - self.mvref_n)
        code = code * (pow(2, self.data_width) - 1)
        code = code / (self.mvref_p - self.mvref_n)
        code = code
        code = (int(code)) << 2
        self.write_register(AD5781Def.DAC_REGISTER, code)

    def readback_output_voltage(self):
        '''
        AD5781 function readback output voltage

        Returns:
            float, the voltage value, unit is mV

        Examples:
            volt = ad5781.readback_output_voltage()
            print(volt)
        '''
        recv_list = self.read_register(AD5781Def.READBACK_DAC_REGISTER)

        if recv_list is None:
            raise AD5781Exception(
                "An error occurred when get output voltage from AD5781 fail.")

        code = (recv_list[0] & 0x0F) | (recv_list[1] & 0xFF) | (recv_list[2] & 0xFC)
        code = float(code >> 2)
        volt = code / (pow(2, self.data_width) - 1)
        volt = volt * (self.mvref_p - self.mvref_n)
        volt = volt + self.mvref_n

        return volt
