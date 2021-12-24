# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MCP23008Def:
    IODIR = 0x00
    IPOL = 0x01
    GPINTEN = 0x02
    DEFVAL = 0x03
    INTCON = 0x04
    IOCON = 0x05
    GPPU = 0x06
    INTF = 0x07
    INTCAP = 0x08
    GPIO = 0x09
    OLAT = 0x0a

    PIN_DIR_OUTPUT = 'output'
    PIN_DIR_INPUT = 'input'
    PINS_INDEX = [i for i in range(8)]


class MCP23008(object):
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

    def __init__(self, dev_addr, i2c_bus):
        assert dev_addr & ~0x07 == 0x20
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("i2c_emulator", 256)
        else:
            self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr

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
        result = self.i2c_bus.write_and_read(self.dev_addr, [reg_addr], rd_len)
        return result

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
        wr_data = []
        wr_data.append(reg_addr)
        wr_data.extend(write_data)
        self.i2c_bus.write(self.dev_addr, wr_data)

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of MCP23008 pin

        Args:
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
            mcp23008.set_pin_dir(7, 'output')

        '''
        assert pin_id in MCP23008Def.PINS_INDEX
        assert dir in [MCP23008Def.PIN_DIR_INPUT, MCP23008Def.PIN_DIR_OUTPUT]

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
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = mcp23008.get_pin_dir(7)
            print(result)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.
            level:    int, [0, 1], set pin level like 0 or 1.

        Examples:
            mcp23008.set_pin(7,1)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.

        Returns:
            int, [0, 1].

        Examples:
            mcp23008.get_pin(7)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.

        Returns:
            int, [0, 1].

        Examples:
            result = mcp23008.get_pin_state(7)
            print(result)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
            pin_id:   int, [0~7],    Pin id you can choose of mcp23008.
            is_inversion: boolean,   Set pin inversion like True or False.

        Examples:
                   mcp23008.set_pin_inversion(7,True)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
            pin_id:   int, [0~7], Pin id you can choose of mcp23008.

        Returns:
            boolean, [True, False].

        Examples:
            result = mcp23008.get_pin_inversion(7)
            print(result)

        '''
        assert pin_id in MCP23008Def.PINS_INDEX

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
        assert len(pins_dir_mask) == 1
        self.write_register(
            MCP23008Def.IODIR, pins_dir_mask)

    def get_pins_dir(self):
        '''
        Get the direction of MCP23008 all pins.

        Returns:
            list.

        Examples:
            result = mcp23008.get_pins_dir()
            print(result)

        '''
        return self.read_register(MCP23008Def.IODIR, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports()
            print(result)

        '''
        return self.read_register(MCP23008Def.GPIO, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte. eg:[0x12,0x13].

        Examples:
            mcp23008.set_ports([0x12,0x13])

        '''
        assert (len(ports_level_mask) == 1)
        self.write_register(
            MCP23008Def.GPIO, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of MCP23008 pin

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports_state()
            print(result)

        '''
        return self.read_register(MCP23008Def.OLAT, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte. eg:[0x12,0x13]

        Examples:
            mcp23008.set_ports_inversion([0x12,0x13])

        '''
        assert (len(ports_inversion_mask) == 1)
        self.write_register(
            MCP23008Def.IPOL, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = mcp23008.get_ports_inversion()
            print(result)

        '''
        return self.read_register(MCP23008Def.IPOL, 1)
