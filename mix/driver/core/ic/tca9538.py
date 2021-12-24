# -*- coding: UTF-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from io_expander_base import IOExpanderBase


class TCA9538Def:
    INTPUT_PORT_REGISTERS = 0x00
    OUTPUT_PORT_REGISTERS = 0x01
    POLARITY_INVERSION_REGISTERS = 0x02
    DIR_CONFIGURATION_REGISTERS = 0x03
    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'
    PIN_ID_MIN = 0
    PIN_ID_MAX = 7


class TCA9538(IOExpanderBase):
    '''
    TCA9538 is a io expansion chip with 8bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:    hexmial,  I2C device address of TCA9538.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator.

    Examples:
        tca9538 = TCA9538(0x70,'/dev/MIX_I2C_0')

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        assert dev_addr & (~0x03) == 0x70
        if i2c_bus is None:
            self._i2c_bus = I2CBusEmulator("tca9538_emulator", 256)
        else:
            self._i2c_bus = i2c_bus
        self._dev_addr = dev_addr
        super(TCA9538, self).__init__()

    def read_register(self, register_addr, read_length):
        '''
        TCA9538 read specific length datas from address

        Args:
            register_addr:   hexmial, [0~0xFF], Read datas from this address.
            read_length:     int, [0~1024],     Length to read.

        Returns:
            list.

        Examples:
            rd_data = tca9538.read_register(0x00, 10)
            print(rd_data)

        '''
        result = self._i2c_bus.write_and_read(self._dev_addr, [register_addr], read_length)
        return result

    def write_register(self, register_addr, write_data):
        '''
        TCA9538 write datas to address, support cross pages writing operation

        Args:
            register_addr:    int, [0~1024], Write data to this address.
            write_data:  list,          Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            tca9538.write_register(0x00, wr_data)

        '''
        wr_data = []
        wr_data.append(register_addr)
        wr_data.extend(write_data)
        self._i2c_bus.write(self._dev_addr, wr_data)

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of TCA9538 pin.

        Args:
            pin_id:   int, [0~7], Pin id you can choose of tca9538.
            dir:      string, ['output', 'input'], Set pin dir.

        Examples:
            tca9538.set_pin_dir(3,'output')

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        assert dir in [TCA9538Def.PIN_DIR_INPUT, TCA9538Def.PIN_DIR_OUTPUT]

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        dir_config &= ~(1 << pin_id)
        if dir == TCA9538Def.PIN_DIR_INPUT:
            dir_config |= (1 << pin_id)
        self.set_pins_dir([dir_config & 0xFF])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of TCA9538 pin.

        Args:
            pin_id:   int, [0~7], Pin id you can choose of tca9538.

        Returns:
            string, ['output', 'input'].

        Examples:
            result = tca9538.get_pin_dir(3)
            print(result)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX

        rd_data = self.get_pins_dir()
        dir_config = rd_data[0]
        if (dir_config & (1 << pin_id)) != 0:
            return TCA9538Def.PIN_DIR_INPUT
        else:
            return TCA9538Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of tca9538 pin.

        Args:
            pin_id:   int, [0~7], Pin id you can choose of tca9538.
            level:    int, [0, 1], set pin level like 0 or 1.

        Examples:
            tca9538.set_pin(3,1)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        rd_data = self.get_ports_state()
        port_config = rd_data[0]
        port_config &= ~(1 << pin_id)
        if level == 1:
            port_config |= (1 << pin_id)
        self.set_ports([port_config & 0xFF])

    def get_pin(self, pin_id):
        '''
        Get the level of tca9538 pin.

        Args:
            pin_id:   int, [0~7], Pin id you can choose of tca9538.

        Returns:
            int, [0, 1].

        Examples:
            tca9538.get_pin(3)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        rd_data = self.get_ports()
        port_config = rd_data[0]
        if (port_config & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def get_pin_state(self, pin_id):
        '''
        Get the pin state of tca9538.

        Args:
            pin_id:   int, [0~7], Pin id you can choose of tca9538.

        Returns:
            int, [0, 1].

        Examples:
            result = tca9538.get_pin_state(3)
            print(result)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        rd_data = self.get_ports_state()
        port_state = rd_data[0]
        if (port_state & (1 << pin_id)) != 0:
            return 1
        else:
            return 0

    def set_pin_inversion(self, pin_id, is_inversion):
        '''
        Set the inversion of tca9538 pin.

        Args:
            pin_id:       int, [0~7], Pin id you can choose of tca9538.
            is_inversion: boolean, [True, False], Set pin inversion like True or False.

        Examples:
            tca9538.set_pin_inversion(3,True)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        port_inv &= ~(1 << pin_id)
        if is_inversion is True:
            port_inv |= (1 << pin_id)
        self.set_ports_inversion([port_inv & 0xFF])

    def get_pin_inversion(self, pin_id):
        '''
        Get the polarity inversion of tca9538 pin.

        Args:
            pin_id:       int, [0~7], Pin id you can choose of tca9538.

        Returns:
            boolean, [True, False].

        Examples:
            result = tca9538.get_pin_inversion(3)
            print(result)

        '''
        assert pin_id >= TCA9538Def.PIN_ID_MIN and pin_id <= TCA9538Def.PIN_ID_MAX
        rd_data = self.get_ports_inversion()
        port_inv = rd_data[0]
        if (port_inv & (1 << pin_id)) != 0:
            return True
        else:
            return False

    def set_pins_dir(self, ports_pins_mask):
        '''
        Set the direction of tca9538 all pins.

        Args:
            ports_pins_mask:  list, Element takes one byte.eg:[0x02].

        Examples:
            tca9538.set_pins_dir([0x02])

        '''
        assert len(ports_pins_mask) == 1
        self.write_register(TCA9538Def.DIR_CONFIGURATION_REGISTERS, ports_pins_mask)

    def get_pins_dir(self):
        '''
        Get the direction of tca9538 all pins.

        Returns:
            list.

        Examples:
            result = tca9538.get_pins_dir()
            print(result)

        '''
        return self.read_register(TCA9538Def.DIR_CONFIGURATION_REGISTERS, 1)

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list.

        Examples:
            result = tca9538.get_ports()
            print(result)

        '''
        return self.read_register(TCA9538Def.INTPUT_PORT_REGISTERS, 1)

    def set_ports(self, ports_level_mask):
        '''
        Set the value of input port register.

        Args:
            ports_level_mask:   list, Element takes one byte.
                                      eg:[0x02].

        Examples:
            tca9538.set_ports([0x12])

        '''
        assert len(ports_level_mask) == 1
        self.write_register(TCA9538Def.OUTPUT_PORT_REGISTERS, ports_level_mask)

    def get_ports_state(self):
        '''
        Get the ports state of tca9538 pin.

        Returns:
            list.

        Examples:
            result = tca9538.get_ports_state()
            print(result)

        '''
        return self.read_register(TCA9538Def.OUTPUT_PORT_REGISTERS, 1)

    def set_ports_inversion(self, ports_inversion_mask):
        '''
        Set the polarity inversion.

        Args:
            ports_inversion_mask: list, Element takes one byte.
                                        eg:[0x12].

        Examples:
            tca9538.set_ports_inversion([0x12])

        '''
        assert len(ports_inversion_mask) == 1
        self.write_register(TCA9538Def.POLARITY_INVERSION_REGISTERS, ports_inversion_mask)

    def get_ports_inversion(self):
        '''
        Get the polarity inversion about all ports

        Returns:
            list.

        Examples:
            result = tca9538.get_ports_inversion()
            print(result)

        '''
        return self.read_register(TCA9538Def.POLARITY_INVERSION_REGISTERS, 1)
