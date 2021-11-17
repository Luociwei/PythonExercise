# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.ic.io_expander_base import IOExpanderBase


class PCA9536Def:
    INPUT_PORT_REGISTER = 0x00
    OUTPUT_PORT_REGISTER = 0x01
    POLARITY_INVERSION_REGISTER = 0x02
    CONFIGURATION_REGISTER = 0x03
    PIN_MIN_NUM = 0
    PIN_MAX_NUM = 3
    PIN_DIR_OUTPUT = 'output'  # 'output' = 1
    PIN_DIR_INPUT = 'input'  # 'input' = 0


class PCA9536Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PCA9536(IOExpanderBase):
    '''
    PCA9536 function class

    ClassType = GPIO

    Args:
        dev_addr: hexmial,  I2C device address of PCA9536.
        i2c_bus:  instance(I2C)/None, Class instance of I2C bus,
                                      If not using the parameter
                                      will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_I2C_0', 256)
        i2c = MIXI2CSG(axi)
        pca9536 = PCA9536(0x41, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        # 7-bit address, excluding read/write bits, lower two bits are variable
        assert dev_addr == 0x41
        self.dev_addr = dev_addr
        if not i2c_bus:
            self.i2c_bus = I2CBusEmulator('pca9536_emulator', 256)
        else:
            self.i2c_bus = i2c_bus
        super(PCA9536, self).__init__()

    def read_register(self, register_address, read_length):
        '''
        PCA9536 read specific length data from address

        Args:
            register_address: hexmial, [0~0xFF], Read data from address.
            read_length:      int, [0~512],      Length to read.

        Returns:
            list, [value], eg:[0x12, 0x13], each element takes one byte.

        Examples:
            rd_data = pca9536.read_register(0x00, 2)
            print(rd_data)

        '''
        assert register_address >= 0
        assert read_length > 0

        return self.i2c_bus.write_and_read(
            self.dev_addr, [register_address], read_length)

    def write_register(self, register_address, write_data):
        '''
        PCA9536 write data to address

        Args:
            register_address: int, [0~1024], Write data to this address.
            write_data:       list, Length to read.

        Examples:
            wr_data = [0x01, 0x02]
            pca9536.write_register(0x00, wr_data)
        '''
        assert register_address >= 0
        assert isinstance(write_data, list)

        write_data = [register_address] + write_data
        self.i2c_bus.write(self.dev_addr, write_data)

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCA9536 pin

        Args:
            pin_id:   int, [0~3], Pin id.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
                  pca9536.set_pin_dir(1,'output')
        '''

        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM
        assert dir in [PCA9536Def.PIN_DIR_INPUT, PCA9536Def.PIN_DIR_OUTPUT]

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        dir_config &= ~(1 << pin_id)
        if dir == PCA9536Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of PCA9536 pin

        Args:
            pin_id:   int, [0~3], Pin id you can choose of pca9536.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = pca9536.get_pin_dir(6)
            print(result)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        if (dir_config & (1 << pin_id)) != 0:
            return PCA9536Def.PIN_DIR_INPUT
        else:
            return PCA9536Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of PCA9536 pin

        Args:
            pin_id:   int, [0~3], Pin id you can choose of pca9536.
            level:    int, [0, 1], set pin level like 0 or 1.

        Examples:
            pca9536.set_pin(1,1)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_ports_state()
        port_config = rd_data[0]
        port_config &= ~(1 << pin_id)
        if level == 1:
            port_config |= (1 << pin_id)
        self.set_ports([port_config & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of PCA9536 pin

        Args:
            pin_id:   int, [0~3], Pin id you can choose of pca9536.

        Returns:
            int, [0, 1].

        Examples:
            pca9536.get_pin(1)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_ports()
        port_config = rd_data[0]
        if (port_config & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def get_pin_state(self, pin_id):
        '''
        Get the pin state of PCA9536

        Args:
            pin_id:   int, [0~7], Pin id you can choose of pca9536.

        Returns:
            int, [0, 1].

        Examples:
            result = pca9536.get_pin_state(7)
            print(result)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_ports_state()
        port_state = rd_data[0]
        if (port_state & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def set_pin_inversion(self, pin_id, is_inversion):
        '''
        Set the inversion of PCA9536 pin

        Args:
            pin_id:       int, [0~7], Pin id you can choose of pca9536.
            is_inversion: boolean,    Set pin inversion like True or False.

        Examples:
            pca9536.set_pin_inversion(1,True)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        port_inv &= ~(1 << pin_id)
        if is_inversion is True:
            port_inv |= (1 << pin_id)
        self.set_ports_inversion([port_inv & 0xFF])

    def get_pin_inversion(self, pin_id):
        '''
        Get the polarity inversion of PCA9536 pin

        Args:
            pin_id:      int, [0~3], Pin id you can choose of pca9536.

        Returns:
            boolean, [True, False].

        Examples:
            result = pca9536.get_pin_inversion(1)
            print(result)
        '''
        assert pin_id >= PCA9536Def.PIN_MIN_NUM and pin_id <= PCA9536Def.PIN_MAX_NUM

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, ports_pins_mask):
        '''
        Set the direction of PCA9536 all pins， 1 input, 0 output

        Args:
            pins_dir_mask:  list, Element takes one byte.eg:[0x12].

        Examples:
            pca9536.set_pins_dir([0x12])
        '''
        assert len(ports_pins_mask) == 1
        self.write_register(PCA9536Def.CONFIGURATION_REGISTER, ports_pins_mask)

    def get_pins_dir(self):
        '''
        Get the direction of PCA9536 all pins.

        Returns:
            list, [value].

        Examples:
            result = pca9536.get_pins_dir()
            print(result)
        '''
        return self.read_register(PCA9536Def.CONFIGURATION_REGISTER, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list, [value].

        Examples:
            result = pca9536.get_ports()
            print(result)
        '''
        return self.read_register(PCA9536Def.INPUT_PORT_REGISTER, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte. eg:[0x12].

        Examples:
            pca9536.set_ports([0x12])
        '''
        assert len(ports_level_mask) == 1
        self.write_register(PCA9536Def.OUTPUT_PORT_REGISTER, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of PCA9536 pin

        Returns:
            list, [value].

        Examples:
            result = pca9536.get_ports_state()
            print(result)
        '''
        return self.read_register(PCA9536Def.OUTPUT_PORT_REGISTER, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte. eg:[0x12].

        Examples:
            pca9536.set_ports_inversion([0x12])
        '''
        assert len(ports_inversion_mask) == 1
        self.write_register(PCA9536Def.POLARITY_INVERSION_REGISTER, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list, [value].

        Examples:
            result = pca9536.get_ports_inversion()
            print(result)
        '''
        return self.read_register(PCA9536Def.POLARITY_INVERSION_REGISTER, 1)
