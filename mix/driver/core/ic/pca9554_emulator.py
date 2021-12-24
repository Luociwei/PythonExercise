# -*- coding: utf-8 -*-
from ..tracer.recorder import *
from pca9554 import PCA9554Def


class PCA9554Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class PCA9554(object):
    '''
    PCA9554 is a io expansion chip with 16bit port expansion

    :param     dev_addr:    instance/None,  I2C device address of PCA9554
    :param     i2c_bus:     instance/None,  Class instance of I2C bus,
                                             If not using this parameter, will create Emulator
    :param     lock:        instance/None,  Class instance of lock
    :example:
                pca9554 = PCA9554(0x3c,'/dev/MIX_I2C_0')
    '''
    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        self.i2c_bus = i2c_bus
        self.lock = lock
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
        PCA9554 read specific length datas from address

        :param    reg_addr:   hexmial(0-0xFF), Read datas from this address
        :param    rd_len:     int(0-1024),     Length to read
        :returns:  type is list
        :example:
                   rd_data = pca9554.read_register(0x00, 10)
                   print(rd_data)
        '''
        assert reg_addr in self._reg.keys()
        if self.lock is not None:
            self._recorder.record("PCA9554 lock acquire")

        self._recorder.record("PCA9554 read_register %s with %d bytes" % (hex(reg_addr), rd_len))

        if self.lock is not None:
            self._recorder.record("PCA9554 lock release")

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def write_register(self, reg_addr, write_data):
        '''
        PCA9554 write datas to address, support cross pages writing operation

        :param    reg_addr:    int(0-1024), Write data to this address
        :param    write_data:  list,        Data to write
        :example:
                   wr_data = [0x01, 0x02, 0x03, 0x04]
                   pca9554.write_register(0x00, wr_data)
        '''
        assert reg_addr in self._reg.keys()

        if self.lock is not None:
            self._recorder.record("PCA9554 lock acquire")

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("PCA9554 write %s to 0x%02x" % (record_data, reg_addr))

        if self.lock is not None:
            self._recorder.record("PCA9554 lock release")

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCA9554 pin

        :param    pin_id:   int(0-7),   Pin id you can choose of pca9554
        :param    dir:      string,      Set pin dir like 'output','input'
        :example:
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
        Get the direction of PCA9554 pin

        :param    pin_id:   int(0-7),   Pin id you can choose of pca9554
        :returns:  type is string
        :example:
                   result = pca9554.get_pin_dir(1)
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
        Set the level of PCA9554 pin

        :param    pin_id:   int(0-7),  Pin id you can choose of pca9554
        :param    level:    int(0/1),   set pin level like 0 or 1
        :example:
                   pca9554.set_pin(2, 1)
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
        Get the level of PCA9554 pin

        :param    pin_id:   int(0-7)    Pin id you can choose of pca9554
        :returns:  type is int
        :example:
                   pca9554.get_pin(2)
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
        Get the pin state of PCA9554

        :param    pin_id:   int(0-7),   Pin id you can choose of pca9554
        :returns:  type is int
        :example:
                   result = pca9554.get_pin_state(1)
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
        Set the inversion of PCA9554 pin

        :param    pin_id:       int(0-7), Pin id you can choose of pca9554
        :param    is_inversion: boolean,   Set pin inversion like True or False
        :example:
                   pca9554.set_pin_inversion(2,True)
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
        Get the polarity inversion of PCA9554 pin

        :param    pin_id:      int(0-15), Pin id you can choose of pca9554
        :returns:  type is boolean
        :example:
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

    def set_pins_dir(self, pins_dir_mask):
        '''
        Set the direction of PCA9554 all pins

        :param    pins_dir_mask:  list, Element takes one byte.eg:[0x12]
        :example:
                   pca9554.set_pins_dir([0x12])
        '''
        assert len(ports_pins_mask) == 1
        self.write_register(PCA9554Def.DIR_CONFIGURATION_REGISTERS, ports_pins_mask)

    def get_pins_dir(self):
        '''
        Get the direction of PCA9554 all pins.

        :returns:  type is list
        :example:
                   result = pca9554.get_pins_dir()
                   print(result)
        '''
        return self.read_register(PCA9554Def.DIR_CONFIGURATION_REGISTERS, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        :returns:  type is list
        :example:
                   result = pca9554.get_ports()
                   print(result)
        '''
        return self.read_register(PCA9554Def.INTPUT_PORT_REGISTERS, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        :param    ports_level_mask:   list, Element takes one byte.
                                             eg:[0x12]
        :example:
                   pca9554.set_ports([0x12])
        '''
        assert len(ports_level_mask) == 1
        self.write_register(PCA9554Def.OUTPUT_PORT_REGISTERS, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of PCA9554 pin

        :returns: type is list
        :example:
                  result = pca9554.get_ports_state()
                  print(result)
        '''
        return self.read_register(PCA9554Def.OUTPUT_PORT_REGISTERS, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        :param    ports_inversion_mask: list, Element takes one byte.
                                               eg:[0x12]
        :example:
                   pca9554.set_ports_inversion([0x12])
        '''
        assert len(ports_inversion_mask) == 1
        self.write_register(PCA9554Def.POLARITY_INVERSION_REGISTERS, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        :returns:  type is list
        :example:
                   result = pca9554.get_ports_inversion()
                   print(result)
        '''
        return self.read_register(PCA9554Def.POLARITY_INVERSION_REGISTERS, 1)
