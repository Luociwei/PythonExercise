# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536Def

__author__ = 'zicheng@SmartGiant'
__version__ = '0.1'


class PCA9536Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class PCA9536(object):
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
        self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self._reg = {
            0x00: 0x00,
            0x01: 0x00,
            0x02: 0x00,
            0x03: 0x00
        }
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def read_register(self, reg_addr, rd_len):
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
        assert reg_addr in self._reg.keys()

        self._recorder.record("PCA9536 read_register %s with %d bytes" % (hex(reg_addr), rd_len))

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def write_register(self, reg_addr, write_data):
        '''
        PCA9536 write data to address

        Args:
            register_address: int, [0~1024], Write data to this address.
            write_data:       list, Length to read.

        Examples:
            wr_data = [0x01, 0x02]
            pca9536.write_register(0x00, wr_data)
        '''
        assert reg_addr in self._reg.keys()

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("PCA9536 write %s to 0x%02x" % (record_data, reg_addr))

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCA9536 pin

        Args:
            pin_id:   int, [0~3], Pin id.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
                  pca9536.set_pin_dir(1,'output')
        '''
        assert pin_id >= 0 and pin_id <= 3
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
        assert pin_id >= 0 and pin_id <= 3

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
        assert pin_id >= 0 and pin_id <= 3

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
        assert pin_id >= 0 and pin_id <= 7

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
        assert pin_id >= 0 and pin_id <= 3

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
        assert pin_id >= 0 and pin_id <= 7

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
        assert pin_id >= 0 and pin_id <= 3

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, pins_dir_mask):
        '''
        Set the direction of PCA9536 all pins， 1 input, 0 output

        Args:
            pins_dir_mask:  list, Element takes one byte.eg:[0x12].

        Examples:
            pca9536.set_pins_dir([0x12])
        '''
        assert len(pins_dir_mask) == 1
        self.write_register(PCA9536Def.CONFIGURATION_REGISTER, pins_dir_mask)

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
        return self.read_register(PCA9536Def.INTPUT_PORT_REGISTER, 1)

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
