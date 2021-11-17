# -*- coding: utf-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from io_expander_base import IOExpanderBase


class PCA9554Def:
    INTPUT_PORT_REGISTERS = 0x00
    OUTPUT_PORT_REGISTERS = 0x01
    POLARITY_INVERSION_REGISTERS = 0x02
    DIR_CONFIGURATION_REGISTERS = 0x03
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class PCA9554(IOExpanderBase):
    '''
    PCA9554 is a io expansion chip with 16bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:    hexmial,  I2C device address of CAT9555.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter, will create Emulator.
        lock:        instance/None,  Class instance of lock.

    Examples:
        pca9554 = PCA9554(0x3c, '/dev/MIX_I2C_0')

    '''
    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        # PCA9554 dev_addr is 0x20 ~ 0x27
        # PCA9554A dev_addr is 0x38 ~ 0x3F
        assert (dev_addr & (~0x07)) == 0x20 or dev_addr & (~0x07) == 0x38
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("pca9554_emulator", 256)
        else:
            self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self.lock = lock
        super(PCA9554, self).__init__()

    def read_register(self, register_addr, read_length):
        '''
        pca9554 read specific length datas from address

        Args:
            register_addr:   hexmial, [0~0xFF], Read datas from this address.
            read_length:     int, [0~1024],     Length to read.

        Returns:
            list.

        Examples:
            rd_data = pca9554.read_register(0x00, 10)
            print(rd_data)

        '''
        if self.lock is not None:
            self.lock.acquire()

        result = self.i2c_bus.write_and_read(self.dev_addr, [register_addr], read_length)

        if self.lock is not None:
            self.lock.release()
        return result

    def write_register(self, register_addr, write_data):
        '''
        pca9554 write datas to address, support cross pages writing operation

        Args:
            register_addr:    int, [0~1024], Write data to this address.
            write_data:  list,          Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            pca9554.write_register(0x00, wr_data)

        '''
        wr_data = []
        wr_data.append(register_addr)
        wr_data.extend(write_data)

        if self.lock is not None:
            self.lock.acquire()

        self.i2c_bus.write(self.dev_addr, wr_data)

        if self.lock is not None:
            self.lock.release()

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of pca9554 pin

        Args:
            pin_id:   int, [0~7],   Pin id you can choose of pca9554.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
            pca9554.set_pin_dir(1,'output')

        '''
        assert pin_id >= 0 and pin_id <= 7
        assert dir in [PCA9554Def.PIN_DIR_INPUT, PCA9554Def.PIN_DIR_OUTPUT]

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        dir_config &= ~(1 << pin_id)
        if dir == PCA9554Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of pca9554 pin

        Args:
            pin_id:   int, [0~7],   Pin id you can choose of pca9554.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = pca9554.get_pin_dir(6)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        if (dir_config & (1 << pin_id)) != 0:
            return PCA9554Def.PIN_DIR_INPUT
        else:
            return PCA9554Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of pca9554 pin

        Args:
            pin_id:   int, [0~7],   Pin id you can choose of pca9554.
            level:    int, [0~1],   set pin level like 0 or 1.

        Examples:
            pca9554.set_pin(1,1)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_ports_state()
        port_config = rd_data[0]
        port_config &= ~(1 << pin_id)
        if level == 1:
            port_config |= (1 << pin_id)
        self.set_ports([port_config & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of pca9554 pin

        Args:
            pin_id:   int, [0~7],   Pin id you can choose of pca9554.

        Returns:
            int, [0, 1].

        Examples:
            pca9554.get_pin(1)

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
        Get the pin state of pca9554

        Args:
            pin_id:   int, [0~7],   Pin id you can choose of pca9554.

        Returns:
            int, [0, 1].

        Examples:
            result = pca9554.get_pin_state(7)
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
        Set the inversion of pca9554 pin

        Args:
            pin_id:       int, [0~7],   Pin id you can choose of pca9554.
            is_inversion: boolean, [True, False],Set pin inversion like True or False.

        Examples:
            pca9554.set_pin_inversion(1,True)

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
        Get the polarity inversion of pca9554 pin

        Args:
            pin_id:       int, [0~7],   Pin id you can choose of pca9554.

        Returns:
            boolean, [True, False].

        Examples:
            result = pca9554.get_pin_inversion(1)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 7

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, ports_pins_mask):
        '''
        Set the direction of pca9554 all pins， 1 input, 0 output

        Args:
            ports_pins_mask:  list, Element takes one byte.eg:[0x12].

        Examples:
            pca9554.set_pins_dir([0x12])

        '''
        assert len(ports_pins_mask) == 1
        self.write_register(PCA9554Def.DIR_CONFIGURATION_REGISTERS, ports_pins_mask)

    def get_pins_dir(self):
        '''
        Get the direction of pca9554 all pins.

        Returns:
            list.

        Examples:
            result = pca9554.get_pins_dir()
            print(result)

        '''
        return self.read_register(PCA9554Def.DIR_CONFIGURATION_REGISTERS, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = pca9554.get_ports()
            print(result)

        '''
        return self.read_register(PCA9554Def.INTPUT_PORT_REGISTERS, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte, eg:[0x12].

        Examples:
            pca9554.set_ports([0x12])

        '''
        assert len(ports_level_mask) == 1
        self.write_register(PCA9554Def.OUTPUT_PORT_REGISTERS, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of pca9554 pin

        Returns:
            list.

        Examples:
            result = pca9554.get_ports_state()
            print(result)

        '''
        return self.read_register(PCA9554Def.OUTPUT_PORT_REGISTERS, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte, eg:[0x12].

        Examples:
            pca9554.set_ports_inversion([0x12])

        '''
        assert len(ports_inversion_mask) == 1
        self.write_register(PCA9554Def.POLARITY_INVERSION_REGISTERS, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = pca9554.get_ports_inversion()
            print(result)

        '''
        return self.read_register(PCA9554Def.POLARITY_INVERSION_REGISTERS, 1)
