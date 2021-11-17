# -*- coding: utf-8 -*-
from ..tracer.recorder import *
from cat9555 import CAT9555Def


class CAT9555Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class CAT9555Emulator(object):
    '''
    CAT9555 is a io expansion chip with 16bit port expansion

    :param     dev_addr:    instance/None,  I2C device address of CAT9555
    :param     i2c_bus:     instance/None,  Class instance of I2C bus,
                                             If not using this parameter, will create Emulator
    :param     lock:        instance/None,  Class instance of lock
    :example:
                cat9555 = CAT9555(0x20,'/dev/MIX_I2C_0')
    '''
    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        assert (dev_addr & (~0x07)) == 0x20
        self.i2c_bus = i2c_bus
        self.lock = lock
        self.dev_addr = dev_addr
        self._reg = {
            0x00: 0x00,
            0x01: 0x00,
            0x02: 0x00,
            0x03: 0x00,
            0x04: 0x00,
            0x05: 0x00,
            0x06: 0x00,
            0x07: 0x00
        }
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def read_register(self, reg_addr, rd_len):
        '''
        CAT9555 read specific length datas from address

        :param    reg_addr:   hexmial(0-0xFF), Read datas from this address
        :param    rd_len:     int(0-1024),     Length to read
        :returns:  type is list
        :example:
                   rd_data = cat9555.read_register(0x00, 10)
                   print(rd_data)
        '''
        assert reg_addr in self._reg.keys()
        if self.lock is not None:
            self._recorder.record("CAT9555 lock acquire")

        self._recorder.record("CAT9555 read_register %s with %d bytes" % (hex(reg_addr), rd_len))

        if self.lock is not None:
            self._recorder.record("CAT9555 lock release")

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def write_register(self, reg_addr, write_data):
        '''
        CAT9555 write datas to address, support cross pages writing operation

        :param    reg_addr:    int(0-1024), Write data to this address
        :param    write_data:  list,        Data to write
        :example:
                   wr_data = [0x01, 0x02, 0x03, 0x04]
                   cat9555.write_register(0x00, wr_data)
        '''
        assert reg_addr in self._reg.keys()

        if self.lock is not None:
            self._recorder.record("CAT9555 lock acquire")

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("CAT9555 write %s to 0x%02x" % (record_data, reg_addr))

        if self.lock is not None:
            self._recorder.record("CAT9555 lock release")

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of CAT9555 pin

        :param    pin_id:   int(0-15),   Pin id you can choose of cat9555
        :param    dir:      string,      Set pin dir like 'output','input'
        :example:
                   cat9555.set_pin_dir(15,'output')
        '''
        assert pin_id >= 0 and pin_id <= 15
        assert dir in ['input', 'output']

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0] | (rd_data[1] << 8)
        dir_config &= ~(1 << pin_id)
        if dir == CAT9555Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF, (dir_config >> 8) & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of CAT9555 pin

        :param    pin_id:   int(0-15),   Pin id you can choose of cat9555
        :returns:  type is string
        :example:
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

        :param    pin_id:   int(0-15),  Pin id you can choose of cat9555
        :param    level:    int(0/1),   set pin level like 0 or 1
        :example:
                   cat9555.set_pin(12,1)
        '''
        assert pin_id >= 0 and pin_id <= 15

        rd_data = self.get_ports_state()
        port_config = rd_data[0] | (rd_data[1] << 8)
        port_config &= ~(1 << pin_id)
        if level == 1:
            port_config |= (1 << pin_id)
        self.set_ports([port_config & 0xFF, (port_config >> 8) & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of CAT9555 pin

        :param    pin_id:   int(0-15)    Pin id you can choose of cat9555
        :returns:  type is int
        :example:
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

        :param    pin_id:   int(0-15),   Pin id you can choose of cat9555
        :returns:  type is int
        :example:
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

        :param    pin_id:       int(0-15), Pin id you can choose of cat9555
        :param    is_inversion: boolean,   Set pin inversion like True or False
        :example:
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

        :param    pin_id:      int(0-15), Pin id you can choose of cat9555
        :returns:  type is boolean
        :example:
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

        :param    pins_dir_mask:  list, Element takes one byte.eg:[0x12,0x13]
        :example:
                   cat9555.set_pins_dir([0x12,0x13])
        '''
        assert (len(pins_dir_mask) == 1) or (len(pins_dir_mask) == 2)
        self.write_register(
            0x06, pins_dir_mask)

    def get_pins_dir(self):
        '''
        Get the direction of CAT9555 all pins.

        :returns:  type is list
        :example:
                   result = cat9555.get_pins_dir()
                   print(result)
        '''
        return self.read_register(0x06, 2)

    def get_ports(self):
        '''
        Get the value of input port register

        :returns:  type is list
        :example:
                   result = cat9555.get_ports()
                   print(result)
        '''
        return self.read_register(0x00, 2)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        :param    ports_level_mask:   list, Element takes one byte.
                                             eg:[0x12,0x13]
        :example:
                   cat9555.set_ports([0x12,0x13])
        '''
        assert (len(ports_level_mask) == 1) or (len(ports_level_mask) == 2)
        self.write_register(
            0x02, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of CAT9555 pin

        :returns: type is list
        :example:
                  result = cat9555.get_ports_state()
                  print(result)
        '''
        return self.read_register(0x02, 2)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        :param    ports_inversion_mask: list, Element takes one byte.
                                               eg:[0x12,0x13]
        :example:
                   cat9555.set_ports_inversion([0x12,0x13])
        '''
        assert (len(ports_inversion_mask) == 1) or (
            len(ports_inversion_mask) == 2)
        self.write_register(
            0x04, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        :returns:  type is list
        :example:
                   result = cat9555.get_ports_inversion()
                   print(result)
        '''
        return self.read_register(0x04, 2)
