# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.mcp23008 import MCP23008Def

__author__ = 'jinkun.lin@SmartGiant'
__version__ = '0.1'


class MCP23008Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MCP23008Emulator(object):
    '''
    MCP23008 is a io expansion chip with 16bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:    int,  I2C device address of MCP23008.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                                 If not using this parameter, will create Emulator.

    Examples:
        mcp23008 = MCP23008(0x20,'/dev/MIX_I2C_0')

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        assert (dev_addr & (~0x07)) == 0x20
        self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self._reg = {
            0x00: 0x00,
            0x01: 0x00,
            0x02: 0x00,
            0x03: 0x00,
            0x04: 0x00,
            0x05: 0x00,
            0x06: 0x00,
            0x07: 0x00,
            0x08: 0x00,
            0x09: 0x00,
            0x0a: 0x00
        }
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def read_register(self, reg_addr, rd_len):
        '''
        MCP23008 read specific length datas from address

        Args:
            reg_addr:   hexmial, [0~0xFF], Read datas from this address.
            rd_len:     int, [0~1024], Length to read.

        Returns:
            list, [value].

        Examples:
            rd_data = mcp23008.read_register(0x00, 10)
            print(rd_data)

        '''
        assert reg_addr in self._reg.keys()

        self._recorder.record("MCP23008 read_register %s with %d bytes" % (hex(reg_addr), rd_len))

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def write_register(self, reg_addr, write_data):
        '''
        MCP23008 write datas to address, support cross pages writing operation

        Args:
            reg_addr:    int, [0~1024], Write data to this address.
            write_data:  list, Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            mcp23008.write_register(0x00, wr_data)

        '''
        assert reg_addr in self._reg.keys()

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("MCP23008 write %s to 0x%02x" % (record_data, reg_addr))

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of MCP23008 pin

        Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
            mcp23008.set_pin_dir(7, 'output')

        '''
        assert pin_id >= 0 and pin_id <= 15
        assert dir in ['input', 'output']

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        dir_config &= ~(1 << pin_id)
        if dir == MCP23008Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of MCP23008 pin

        Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = mcp23008.get_pin_dir(7)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        if (dir_config & (1 << pin_id)) != 0:
            return MCP23008Def.PIN_DIR_INPUT
        else:
            return MCP23008Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of MCP23008 pin

        Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.
            level:    int, [0, 1], set pin level like 0 or 1.

        Examples:
            mcp23008.set_pin(7,1)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_state()
        port_config = rd_data[0]
        port_config &= ~(1 << pin_id)
        if level == 1:
            port_config |= (1 << pin_id)
        self.set_ports([port_config & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of MCP23008 pin

        Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.

        Returns:
            int, [0, 1].

        Examples:
            mcp23008.get_pin(7)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports()
        port_config = rd_data[0]
        if (port_config & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def get_pin_state(self, pin_id):
        '''
        Get the pin state of MCP23008

         Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.

        Returns:
            int, [0, 1].

        Examples:
            result = mcp23008.get_pin_state(7)
            print(result)
        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_state()
        port_state = rd_data[0]
        if (port_state & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def set_pin_inversion(self, pin_id, is_inversion):
        '''
        Set the inversion of MCP23008 pin

        Args:
            pin_id:   int, [0~15],    Pin id you can choose of mcp23008.
            is_inversion: boolean,   Set pin inversion like True or False.

        Examples:
                   mcp23008.set_pin_inversion(7,True)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        port_inv &= ~(1 << pin_id)
        if is_inversion is True:
            port_inv |= (1 << pin_id)
        self.set_ports_inversion([port_inv & 0xFF])

    def get_pin_inversion(self, pin_id):
        '''
        Get the polarity inversion of MCP23008 pin

        Args:
            pin_id:   int, [0~15], Pin id you can choose of mcp23008.

        Returns:
            boolean, [True, False].

        Examples:
            result = mcp23008.get_pin_inversion(7)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, pins_dir_mask):
        '''
        Set the direction of MCP23008 all pins

        Args:
            pins_dir_mask:  list, Element takes one byte.eg:[0x12,0x13].

        Examples:
            mcp23008.set_pins_dir([0x12,0x13])

        '''
        assert (len(pins_dir_mask) == 1) or (len(pins_dir_mask) == 2)
        self.write_register(
            0x06, pins_dir_mask)

    def get_pins_dir(self):
        '''
        Get the direction of MCP23008 all pins.

        Returns:
            list.

        Examples:
            result = mcp23008.get_pins_dir()
            print(result)

        '''
        return self.read_register(0x06, 2)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports()
            print(result)

        '''
        return self.read_register(0x00, 2)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte. eg:[0x12,0x13].

        Examples:
            mcp23008.set_ports([0x12,0x13])

        '''
        assert (len(ports_level_mask) == 1) or (len(ports_level_mask) == 2)
        self.write_register(
            0x02, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of MCP23008 pin

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports_state()
            print(result)

        '''
        return self.read_register(0x02, 2)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte. eg:[0x12,0x13]

        Examples:
            mcp23008.set_ports_inversion([0x12,0x13])

        '''
        assert (len(ports_inversion_mask) == 1) or (
            len(ports_inversion_mask) == 2)
        self.write_register(
            0x04, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports_inversion()
            print(result)

        '''
        return self.read_register(0x04, 2)
