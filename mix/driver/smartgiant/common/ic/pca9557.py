# -*- coding: utf-8 -*-
from threading import Lock
from mix.driver.core.ic.io_expander_base import IOExpanderBase


__author__ = 'huangjianxuan@SmartGiant'
__version__ = '0.1'


class PCA9557Def:

    INTPUT_PORT_REGISTERS = 0x00
    OUTPUT_PORT_REGISTERS = 0x01
    POLARITY_INVERSION_REGISTERS = 0x02
    DIR_CONFIGURATION_REGISTERS = 0x03
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class PCA9557(IOExpanderBase):
    '''
    PCA9557 is a io expansion chip with 16bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:       hexmial,  I2C device address of CAT9555.
        i2c_bus:        instance(I2C)/None,  Class instance of I2C bus.
        lock:           instance/None,  Class instance of lock.

    Examples:
        pca9557 = PCA9557(0x3c, '/dev/MIX_I2C_0')

    '''
    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        assert (dev_addr & (~0x07)) == 0x18

        self.i2c_bus = i2c_bus
        self.lock = lock
        self.lock_set_pin = Lock()
        self.dev_addr = dev_addr
        super(PCA9557, self).__init__()

    def read_register(self, reg_addr, rd_len):
        '''
        PCA9557 read specific length datas from address

        Args:
            reg_addr:       hexmial, [0~0xFF], Read datas from this address.
            rd_len:         int, [0~1024],     Length to read.

        Returns:
            list, [value, ...].

        Examples:
            rd_data = pca9557.read_register(0x00, 10)
            print(rd_data)

        '''
        if self.lock is not None:
            self.lock.acquire()
        result = self.i2c_bus.write_and_read(self.dev_addr, [reg_addr], rd_len)
        if self.lock is not None:
            self.lock.release()
        return result

    def write_register(self, reg_addr, write_data):
        '''
        PCA9557 write datas to address, support cross pages writing operation

        Args:
            reg_addr:       int, [0~1024], Write data to this address.
            write_data:     list, Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            pca9557.write_register(0x00, wr_data)

        '''
        wr_data = []
        wr_data.append(reg_addr)
        wr_data.extend(write_data)
        if self.lock is not None:
            self.lock.acquire()
        self.i2c_bus.write(self.dev_addr, wr_data)
        if self.lock is not None:
            self.lock.release()

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.
            dir:            string, ['output', 'input'], Set pin dir.

        Examples:
            pca9557.set_pin_dir(1, 'output')

        '''
        assert pin_id >= 0 and pin_id <= 7
        assert dir in [PCA9557Def.PIN_DIR_INPUT, PCA9557Def.PIN_DIR_OUTPUT]

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        dir_config &= ~(1 << pin_id)
        if dir == PCA9557Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = pca9557.get_pin_dir(6)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        if (dir_config & (1 << pin_id)) != 0:
            return PCA9557Def.PIN_DIR_INPUT
        else:
            return PCA9557Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.
            level:          int, [0~1], set pin level like 0 or 1.

        Examples:
            pca9557.set_pin(1, 1)

        '''
        assert pin_id >= 0 and pin_id <= 7

        with self.lock_set_pin:
            rd_data = self.get_ports_state()
            port_config = rd_data[0]
            port_config &= ~(1 << pin_id)
            if level == 1:
                port_config |= (1 << pin_id)
            self.set_ports([port_config & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.

        Returns:
            int, [0, 1].

        Examples:
            pca9557.get_pin(1)

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
        Get the pin state of PCA9557

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.

        Returns:
            int, [0, 1].

        Examples:
            result = pca9557.get_pin_state(7)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_ports_state()
        port_state = rd_data[0]
        if (port_state & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def set_pin_inversion(self, pin_id, is_inversion):
        '''
        Set the inversion of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.
            is_inversion:   boolean, [True, False], Set pin inversion like True or False.

        Examples:
            pca9557.set_pin_inversion(1, True)

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
        Get the polarity inversion of PCA9557 pin

        Args:
            pin_id:         int, [0~7], Pin id you can choose of pca9557.

        Returns:
            boolean, [True, False].

        Examples:
            result = pca9557.get_pin_inversion(1)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, pins_dir_mask):
        '''
        Set the direction of PCA9557 all pins. 1 input, 0 output.

        Args:
            pins_dir_mask:  list, Element takes one byte.eg:[0x12].

        Examples:
            pca9557.set_pins_dir([0x12])

        '''
        assert len(pins_dir_mask) == 1
        self.write_register(PCA9557Def.DIR_CONFIGURATION_REGISTERS, pins_dir_mask)

    def get_pins_dir(self):
        '''
        Get the direction of PCA9557 all pins.

        Returns:
            list.

        Examples:
            result = pca9557.get_pins_dir()
            print(result)

        '''
        return self.read_register(PCA9557Def.DIR_CONFIGURATION_REGISTERS, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = pca9557.get_ports()
            print(result)

        '''
        return self.read_register(PCA9557Def.INTPUT_PORT_REGISTERS, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte, eg:[0x12].

        Examples:
            pca9557.set_ports([0x12])

        '''
        assert len(ports_level_mask) == 1
        self.write_register(PCA9557Def.OUTPUT_PORT_REGISTERS, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of PCA9557 pin

        Returns:
            list.

        Examples:
            result = pca9557.get_ports_state()
            print(result)

        '''
        return self.read_register(PCA9557Def.OUTPUT_PORT_REGISTERS, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask:   ist, Element takes one byte, eg:[0x12].

        Examples:
            pca9557.set_ports_inversion([0x12])

        '''
        assert len(ports_inversion_mask) == 1
        self.write_register(PCA9557Def.POLARITY_INVERSION_REGISTERS, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = pca9557.get_ports_inversion()
            print(result)

        '''
        return self.read_register(PCA9557Def.POLARITY_INVERSION_REGISTERS, 1)
