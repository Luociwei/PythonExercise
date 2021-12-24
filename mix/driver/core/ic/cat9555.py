# -*- coding: utf-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from threading import Lock
from io_expander_base import IOExpanderBase


class CAT9555Def:
    INPUT_PORT_0_REGISTER = 0x00
    INPUT_PORT_1_REGISTER = 0x01
    OUTPUT_PORT_0_REGISTER = 0x02
    OUTPUT_PORT_1_REGISTER = 0x03
    INVERSION_PORT_0_REGISTER = 0x04
    INVERSION_PORT_1_REGISTER = 0x05
    DIR_CONFIG_PORT_0_REGISTER = 0x06
    DIR_CONFIG_PORT_1_REGISTER = 0x07
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class CAT9555(IOExpanderBase):
    '''
    CAT9555 is a io expansion chip with 16bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:    hexmial,  I2C device address of CAT9555.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter, will create Emulator.
        lock:        instance/None,  Class instance of lock.

    Examples:
        cat9555 = CAT9555(0x20,'/dev/MIX_I2C_0')

    '''

    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        assert (dev_addr & (~0x07)) == 0x20
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("cat9555_emulator", 256)
        else:
            self.i2c_bus = i2c_bus
        self.lock = lock
        self.lock_set_pin = Lock()
        self.dev_addr = dev_addr
        super(CAT9555, self).__init__()

    def read_register(self, reg_addr, rd_len):
        '''
        CAT9555 read specific length datas from address

        Args:
            reg_addr:   hexmial, [0~0xFF], Read datas from this address.
            rd_len:     int, [0~1024],     Length to read.

        Returns:
            list, [value, ...].

        Examples:
            rd_data = cat9555.read_register(0x00, 10)
            print(rd_data)

        '''
        if self.lock is not None:
            self.lock.acquire()

        try:
            result = self.i2c_bus.write_and_read(self.dev_addr, [reg_addr], rd_len)
        except Exception as error:
            if self.lock is not None:
                self.lock.release()
            raise error

        if self.lock is not None:
            self.lock.release()
        return result

    def write_register(self, reg_addr, write_data):
        '''
        CAT9555 write datas to address, support cross pages writing operation

        Args:
            reg_addr:    int, [0~1024], Write data to this address.
            write_data:  list,          Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            cat9555.write_register(0x00, wr_data)

        '''
        wr_data = []
        wr_data.append(reg_addr)
        wr_data.extend(write_data)
        if self.lock is not None:
            self.lock.acquire()

        try:
            self.i2c_bus.write(self.dev_addr, wr_data)
        except Exception as error:
            if self.lock is not None:
                self.lock.release()
            raise error

        if self.lock is not None:
            self.lock.release()

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of CAT9555 pin

        Args:
            pin_id:   int, [0~15],   Pin id you can choose of cat9555.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
            cat9555.set_pin_dir(15,'output')

        '''
        assert pin_id >= 0 and pin_id <= 15
        assert dir in [CAT9555Def.PIN_DIR_INPUT, CAT9555Def.PIN_DIR_OUTPUT]

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0] | (rd_data[1] << 8)
        dir_config &= ~(1 << pin_id)
        if dir == CAT9555Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF, (dir_config >> 8) & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of CAT9555 pin

        Args:
            pin_id:   int, [0~15],   Pin id you can choose of cat9555.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = cat9555.get_pin_dir(15)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0] | (rd_data[1] << 8)
        if (dir_config & (1 << pin_id)) != 0:
            return CAT9555Def.PIN_DIR_INPUT
        else:
            return CAT9555Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of CAT9555 pin

        Args:
            pin_id:   int, [0~15],   Pin id you can choose of cat9555.
            level:    int, [0, 1],   set pin level like 0 or 1.

        Examples:
            cat9555.set_pin(12,1)

        '''
        assert pin_id >= 0 and pin_id <= 15

        with self.lock_set_pin:
            rd_data = self.get_ports_state()
            port_config = rd_data[0] | (rd_data[1] << 8)
            port_config &= ~(1 << pin_id)
            if level == 1:
                port_config |= (1 << pin_id)
            self.set_ports([port_config & 0xFF, (port_config >> 8) & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of CAT9555 pin

        Args:
            pin_id:   int, [0~15],   Pin id you can choose of cat9555.

        Returns:
            int, [0, 1].

        Examples:
            cat9555.get_pin(12)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports()
        port_config = rd_data[0] | (rd_data[1] << 8)
        if (port_config & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def get_pin_state(self, pin_id):
        '''
        Get the pin state of CAT9555

        Args:
            pin_id:   int, [0~15],   Pin id you can choose of cat9555.

        Returns:
            int, [0, 1].

        Examples:
            result = cat9555.get_pin_state(15)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_state()
        port_state = rd_data[0] | (rd_data[1] << 8)
        if (port_state & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def set_pin_inversion(self, pin_id, is_inversion):
        '''
        Set the inversion of CAT9555 pin

        Args:
            pin_id:       int, [0~15], Pin id you can choose of cat9555.
            is_inversion: boolean, [True, False], Set pin inversion like True or False.

        Examples:
            cat9555.set_pin_inversion(12,True)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0] | (rd_data[1] << 8)
        port_inv &= ~(1 << pin_id)
        if is_inversion is True:
            port_inv |= (1 << pin_id)
        self.set_ports_inversion([port_inv & 0xFF, (port_inv >> 8) & 0xFF])

    def get_pin_inversion(self, pin_id):
        '''
        Get the polarity inversion of CAT9555 pin

        Args:
            pin_id:       int, [0~15],   Pin id you can choose of cat9555.

        Returns:
            boolean, [True, False].

        Examples:
            result = cat9555.get_pin_inversion(12)
            print(result)

        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0] | (rd_data[1] << 8)
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, pins_dir_mask):
        '''
        Set the direction of CAT9555 all pins

        Args:
            pins_dir_mask:  list, Element takes one byte.eg:[0x12,0x13].

        Examples:
            cat9555.set_pins_dir([0x12,0x13])

        '''
        assert (len(pins_dir_mask) == 1) or (len(pins_dir_mask) == 2)
        self.write_register(
            CAT9555Def.DIR_CONFIG_PORT_0_REGISTER, pins_dir_mask)

    def get_pins_dir(self):
        '''
        Get the direction of CAT9555 all pins.

        Returns:
            list.

        Examples:
            result = cat9555.get_pins_dir()
            print(result)

        '''
        return self.read_register(CAT9555Def.DIR_CONFIG_PORT_0_REGISTER, 2)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = cat9555.get_ports()
            print(result)

        '''
        return self.read_register(CAT9555Def.INPUT_PORT_0_REGISTER, 2)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte.
                                      eg:[0x12,0x13].

        Examples:
            cat9555.set_ports([0x12,0x13])

        '''
        assert (len(ports_level_mask) == 1) or (len(ports_level_mask) == 2)
        self.write_register(
            CAT9555Def.OUTPUT_PORT_0_REGISTER, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of CAT9555 pin

        Returns:
            list.

        Examples:
            result = cat9555.get_ports_state()
            print(result)

        '''
        return self.read_register(CAT9555Def.OUTPUT_PORT_0_REGISTER, 2)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte.
                                        eg:[0x12,0x13].

        Examples:
            cat9555.set_ports_inversion([0x12,0x13])

        '''
        assert (len(ports_inversion_mask) == 1) or (
            len(ports_inversion_mask) == 2)
        self.write_register(
            CAT9555Def.INVERSION_PORT_0_REGISTER, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = cat9555.get_ports_inversion()
            print(result)

        '''
        return self.read_register(CAT9555Def.INVERSION_PORT_0_REGISTER, 2)
