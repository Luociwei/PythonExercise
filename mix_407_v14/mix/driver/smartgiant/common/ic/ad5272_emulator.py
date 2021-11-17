# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = '0.1'


class AD5272Emulator(object):
    '''
    AD5272 Emulator class
    '''

    def __init__(self, name='ad5272'):
        self.name = name

        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._recorder.record("{}.__init__()".format(self.name))
        self.command = 0x00
        self.resistor = 100000
        self.control_reg = 0x00

    def write_command(self, command, data):
        '''
        AD527x write command and data to address, support control chip

        Args:
            command:    hexmial, [0~0xF], Write datas to this address.
            data:       hexmial, [0~0x3FF], Data for register.

        Examples:
                   AD527x.write_command(0x00, 0x2)

        '''
        assert type(data) is int and command in range(0xF)

        self._recorder.record("{}.write_command({}, {})".format(self.name, command, data))
        self.command = command

    def read_command(self, command):
        '''
        AD527x read data from address, support to read data

        Args:
            command:    hexmial, [0~0xF], Read data to this address.

        Returns:
            list.

        Examples:
            recv_byte = AD527x.read_command(0x00)
            print (recv_byte)

        '''
        # tell AD527x that I'm going to read
        assert command in range(0xF)
        self._recorder.record("{}.read_command({})".format(self.name, command))
        return self.command

    def get_resistor(self):
        '''
        AD527x get the resistor from address

        Returns:
            list.

        Examples:
            reg = AD527x.get_resistor()
            print(resistor)

        '''
        # reg = self.read_command(AD527xDef.READ_FROM_RDAC)
        # read_data = (reg[0] << 8) | reg[1]
        # # default 100KΩ, general formula is use the resolution and nominal
        # # resistance to calculate
        # resistor = (read_data &
        #             0x3FF) / math.pow(2, self.resolution) * math.pow(10, 5)
        self._recorder.record("{}.get_resistor()".format(self.name))
        return self.resistor  # unit: ohm

    def set_resistor(self, resistor):
        '''
        AD527x set the resistor to address

        Args:
            resistor:   float, [0~9812.1], Set the RDAC.

        Examples:
            AD527x.set_resistor(4583.9)

        '''
        # default 100KΩ, against general formula can get the resistor
        # data = int(resistor / math.pow(10, 5) *
        #            math.pow(2, self.resolution) + 0.5)
        # # send 0x1 command to write contents of serial register data to RDAC
        # self.write_command(AD527xDef.WRITE_TO_RDAC, data)
        self._recorder.record("{}.set_resistor({})".format(self.name, resistor))
        self.resistor = resistor

    def set_work_mode(self, work_mode):
        '''
        AD527x set the work mode to address

        Args:
            work_mode:  string, ["normal", "shutdown"], Set the mode.

        Examples:
            AD527x.set_resistor("shutdown")

        '''
        assert work_mode in ['normal', 'shutdown']
        # data = 0x0
        # if 'normal' == work_mode:
        #     data = 0x0
        # elif 'shutdown' == work_mode:
        #     data = 0x1
        # set AD527x work mode
        # self.write_command(AD527xDef.SOFTWARE_SHUTDOWN, data)
        self._recorder.record("{}.set_work_mode({})".format(self.name, work_mode))

    def set_control_register(self, reg_data):
        '''
        AD527x set the control data to address

        Args:
            reg_data:     int, [0~0x7], Set control register.

        Examples:
            AD527x.set_control_registers(0x6)

        '''
        assert type(reg_data) is int and reg_data in range(0x7)
        # send 0x7 command to write contents of the serial register data
        # to the control register.
        # self.write_command(AD527xDef.WRITE_TO_CONTROL, reg_data)
        self._recorder.record("{}.set_control_register({})".format(self.name, reg_data))
        self.control_req = reg_data

    def get_control_register(self):
        '''
        AD527x get the control data from address

        Returns:
            list.

        Examples:
            reg_data = AD527x.get_control_register()
            print(reg_data)

        '''
        # send 0x8 command to read contents of the control register.
        # reg_data = self.read_command(AD527xDef.READ_FROM_CONTROL)
        # only last four bit valid
        # return reg_data[1] & 0xF
        self._recorder.record("{}.get_control_register({})".format(self.name))
        return self.control_reg
