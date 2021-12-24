# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'Suncode_D@SunCode'
__version__ = '0.1'

class ltc2309Ref:
    channel_mode = {'SINGLE_ENDED_UNIP':0x88,'SINGLE_ENDED_BIP':0x80,'DIFF_UNIP':0x08,'DIFF_BIP':0x00}

    channel_select_diff =   {'CH0':0x00,'CH1':0x10,'CH2':0x20,'CH3':0x30,'CH4':0x40,'CH5':0x50,'CH6':0x60,'CH7':0x70}

    channel_select_single = {'CH0':0x00,'CH1':0x40,'CH2':0x10,'CH3':0x50,'CH4':0x20,'CH5':0x60,'CH6':0x30,'CH7':0x70}

class LTC2309(object):
    '''
    LTC2309 function class

    ClassType = ADC

    Args:
        dev_addr:   hexmial,             I2C device address of AD56X7R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5602.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        ad56x7r = AD5602(0x50, i2c)

    '''

    def __init__(self, dev_addr, mode, bus_rate, i2c_bus=None):
        self.bus_rate = bus_rate
        self.dev_addr = dev_addr
        self.mode_init = str(mode)
        if not i2c_bus:
            self.i2c_bus = I2CBusEmulator('ad5667_emulator', 256)
        else:
            self.i2c_bus = i2c_bus
        # self.set_mode(self.mode_init)

    def set_mode(self,mode):
        # mode_select = ltc2309Ref.channel_mode[str(mode)]
        # self.write_operation(mode_select)
        # high_byte = mode>>4
        # low_byte = (mode&0x0f)<<4
        # print("mode is ==",mode)
        # print("hex mode is ",ltc2309Ref.channel_mode[str(mode)])
        self.write_operation([ltc2309Ref.channel_mode[str(mode)]])

    def channel_select(self,channel):
        mode_select = ltc2309Ref.channel_mode[str(self.mode_init)]
        # print("self.mode_init",self.mode_init)
        # print("ltc2309Ref.channel_select_single[str(channel)]",ltc2309Ref.channel_select_single[str(channel)])
        # print("mode_select",mode_select)
        # print("after|",mode_select|ltc2309Ref.channel_select_diff[str(channel)])

        if 'SINGLE_ENDED' in str(self.mode_init):
            return self.write_operation([mode_select|ltc2309Ref.channel_select_single[str(channel)]])
        if 'DIF' in str(self.mode_init):
            return self.write_operation([mode_select|ltc2309Ref.channel_select_diff[str(channel)]])

    def read_volt(self,channel):
        self.channel_select(channel)
        volt = self.read_operation(2)
        volt_mv = volt[0]<<4|volt[1]>>4
        return volt_mv

    def read_operation(self,count):
        '''
        LTC2309 read operation

        Returns:
            list, [value, value, value].

        Examples:
            LTC2309.write_operation(0x00, [0x12,0x12])
            rd_data = LTC2309.read_operation()
            print(rd_data)

        '''
        return self.i2c_bus.read(self.dev_addr, int(count))

    def write_operation(self, data):
        '''
        LTC2309 write command and data to address

        Args:
            command:    int, [0~7], Write command to chip.
            data:       list, each element takes one byte,eg:[0x01,0x04].

        Examples:
            wr_data = [0x01, 0x04]
            LTC2309.write(0x00, wr_data)

        '''
        # assert isinstance(command, int) and command >= 0
        assert isinstance(data, list)
        assert all(isinstance(x, int) and x >= 0 for x in data)
        self.i2c_bus.write(self.dev_addr, data)
