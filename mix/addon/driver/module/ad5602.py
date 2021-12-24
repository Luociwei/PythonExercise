# -*- coding: utf-8 -*-

__author__ = 'Suncode_D@SunCode'
__version__ = '0.1'

from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator


class AD5602Ref:
    work_mode = {'normal':0x00,'power_down_mode_1K':0x10,'power_down_mode_10K':0x20,'tri_state':0x30}

class AD5602RException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD5602(object):
    '''
    AD5602 function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD56X7R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5602.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        ad56x7r = AD5602(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None,mvref=5000):
        # 7-bit slave address. The two LSBs are variable
        # assert dev_addr == 0x0F

        self.dev_addr = dev_addr

        if not i2c_bus:
            self.i2c_bus = I2CBusEmulator('ad5667_emulator', 256)
        else:
            self.i2c_bus = i2c_bus
        self.vref = mvref

    def output_reset(self):

        write_operation(self, [0x0,0x0])

    def output_volt_dc(self, volt):
        '''
        AD56X7R output voltage

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel.
            volt:       float/int, [0~reference voltage], unit mV.

        Examples:
            ad56x7r.output_volt_dc(0, 1000)

        '''
        # assert channel in [0, 1, 2]
        assert isinstance(volt, (int, float)) and volt >= 0 and volt<=4500
        # assert  mode in AD5602Ref.work_mode
        mode = AD5602Ref.work_mode['normal']
        code = int(volt*256)/self.vref
        high_byte = mode | (code>>4)
        low_byte = (code&0x0f)<<4

        self.write_operation([high_byte,low_byte])

    def read_volt(self):
        '''
        AD56X7R read back the voltage from register

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel.

        Returns:
            float, value, unit mV.

        Examples:
            volt = ad56x7r.read_volt(0)
            print(volt)

        '''
        # assert channel in [0, 1, 2]
        data_list = self.read_operation()
        return data_list

    def read_operation(self):
        '''
        AD56X7R read operation

        Returns:
            list, [value, value, value].

        Examples:
            ad56x7r.write_operation(0x00, [0x12,0x12])
            rd_data = ad56x7r.read_operation()
            print(rd_data)

        '''
        return self.i2c_bus.read(self.dev_addr, 3)

    def write_operation(self, data):
        '''
        AD56X7R write command and data to address

        Args:
            command:    int, [0~7], Write command to chip.
            data:       list, each element takes one byte,eg:[0x01,0x04].

        Examples:
            wr_data = [0x01, 0x04]
            ad56x7r.write(0x00, wr_data)

        '''
        # assert isinstance(command, int) and command >= 0
        assert isinstance(data, list)
        assert all(isinstance(x, int) and x >= 0 for x in data)
        self.i2c_bus.write(self.dev_addr, data)
