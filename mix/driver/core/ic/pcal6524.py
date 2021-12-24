# -*- coding: utf-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from io_expander_base import IOExpanderBase


class PCAL6524Def:
    """ PCAL6524Def shows the registers address of PCAL6524
    """
    INPUT_PORT_0_REGISTER = 0x00
    INPUT_PORT_1_REGISTER = 0x01
    INPUT_PORT_2_REGISTER = 0x02
    OUTPUT_PORT_0_REGISTER = 0x04
    OUTPUT_PORT_1_REGISTER = 0x05
    OUTPUT_PORT_2_REGISTER = 0x06
    CONFIG_PORT_0_REGISTER = 0x0c
    CONFIG_PORT_1_REGISTER = 0x0d
    CONFIG_PORT_2_REGISTER = 0x0e
    PUPD_ENABLE_PORT_0_REGISTER = 0x4c
    PUPD_ENABLE_PORT_1_REGISTER = 0x4d
    PUPD_ENABLE_PORT_2_REGISTER = 0x4e
    PUPD_SELECTION_PORT_0_REGISTER = 0x50
    PUPD_SELECTION_PORT_1_REGISTER = 0x51
    PUPD_SELECTION_PORT_2_REGISTER = 0x52
    OUTPUT_PORT_CONFIGURATION_REGISTER = 0x5C
    INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION_REGISTER = 0x70
    INDIVIDUAL_PIN_OUTPUT_PORT_1_CONFIGURATION_REGISTER = 0x71
    INDIVIDUAL_PIN_OUTPUT_PORT_2_CONFIGURATION_REGISTER = 0x72

    # PCAL6524 has 3 ports, each port has 8 pins.
    ONE_PORT_MAX_PIN = 8
    RESET_ADDR = 0x00
    RESET_VALUE = [0x06]

    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class PCAL6524Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PCAL6524(IOExpanderBase):
    '''
    PCAL6524 function class

    ClassType = GPIO

    Args:
        dev_addr: hexmial, I2C device address of PCAL6524.
        i2c_bus:  instance(I2C)/None, Class instance of I2C bus,
                                      If not using the parameter
                                      will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        pcal6524 = PCAL6524(0x20, i2c)

    '''
    rpc_public_api = [
        'read_register', 'write_register', 'set_pin_dir', 'get_pin_dir',
        'set_pin', 'get_pin', 'get_ports', 'set_ports', 'reset_chip',
        'get_pins_state', 'set_pins_state', 'set_pins_dir', 'get_pins_dir',
        'set_pull_up_or_down', 'get_pull_up_or_down_state',
        'set_pins_mode', 'get_pins_mode'
    ]

    def __init__(self, dev_addr, i2c_bus=None):
        # 7-bit address, excluding read/write bits, lower two bits are variable
        assert (dev_addr & (~0x03)) == 0x20
        self.dev_addr = dev_addr
        if not i2c_bus:
            self.i2c_bus = I2CBusEmulator('pcal6524_emulator', 256)
        else:
            self.i2c_bus = i2c_bus
        super(PCAL6524, self).__init__()

    def read_register(self, register_address, read_length):
        '''
        PCAL6524 read specific length data from address

        Args:
            register_address:    hexmial, [0~0xFF], Read data from address.
            read_length:         int, [0~512],      Length to read.

        Returns:
            list, eg:[0x12, 0x13], each element takes one byte.

        Examples:
            rd_data = pcal6524.read_register(0x00, 2)
            print(rd_data)

        '''
        assert register_address >= 0
        assert read_length > 0

        return self.i2c_bus.write_and_read(
            self.dev_addr, [register_address], read_length)

    def write_register(self, register_address, write_data):
        '''
        PCAL6524 write data to address

        Args:
            register_address: int, [0~1024], Write data to this address.
            write_data:       list,          Length to read.

        Examples:
            wr_data = [0x01, 0x02]
            pcal6524.write_register(0x00, wr_data)

        '''
        assert register_address >= 0
        assert isinstance(write_data, list)

        write_data = [register_address] + write_data
        self.i2c_bus.write(self.dev_addr, write_data)

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCAL6524 pin

        Args:
            pin_id:   int, [0~23], Pin id.
            dir:      string, ['output','input'], Set pin dir like.

        Examples:
            pcal6524.set_pin_dir(15,'output')

        '''

        assert pin_id >= 0 and pin_id <= 23
        assert dir in [PCAL6524Def.PIN_DIR_INPUT, PCAL6524Def.PIN_DIR_OUTPUT]

        if dir == PCAL6524Def.PIN_DIR_INPUT:
            self.set_pins_dir([(pin_id, 1)])
        else:
            self.set_pins_dir([(pin_id, 0)])

    def get_pin_dir(self, pin_id):
        '''
        Get the direction of PCAL6524 pin

        Args:
            pin_id:    int, [0~23], Pin id.

        Returns:
            string, ['output', 'input'].

        Examples:
            pcal6524.get_pin_dir(15)

        '''
        assert pin_id >= 0 and pin_id <= 23

        state = self.get_pins_dir([pin_id])
        if state[0][1] != 0:
            return PCAL6524Def.PIN_DIR_INPUT
        else:
            return PCAL6524Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of PCAL6524 pin

        Args:
            pin_id:    int, [0~23], Pin id.
            level:     int, [0, 1], set pin level.

        Examples:
            pcal6524.set_pin(12,1)

        '''
        assert pin_id >= 0 and pin_id <= 23
        self.set_pins_state([(pin_id, level)])

    def get_pin(self, pin_id):
        '''
        Get the level of PCAL6524 pin

        Args:
            pin_id:    int, [0~23], Pin id.

        Returns:
            int, [0, 1].

        Examples:
                   pcal6524.get_pin(12)

        '''
        assert pin_id >= 0 and pin_id <= 23
        register_offset = pin_id // PCAL6524Def.ONE_PORT_MAX_PIN
        one_port_state = self.read_register(PCAL6524Def.INPUT_PORT_0_REGISTER + register_offset, 1)
        pin_state = (one_port_state[0] >> (pin_id % PCAL6524Def.ONE_PORT_MAX_PIN)) & 0x1
        return pin_state

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list, list if successful, list has 3 element,
                  each element takes one byte.

        Examples:
            pcal6524.get_ports()

        '''
        return self.read_register(PCAL6524Def.INPUT_PORT_0_REGISTER, 3)

    def set_ports(self, ports_list):
        '''
        Set the value of input port register.

        Args:
            ports_list:    list,    Element takes one byte.
                                    eg:[0x12,0x13].

        Examples:
            pcal6524.set_ports([0x12,0x13])

        '''
        assert (len(ports_list) == 1) or (len(ports_list) == 2)
        self.write_register(PCAL6524Def.OUTPUT_PORT_0_REGISTER, ports_list)

    def reset_chip(self):
        '''
        PCAL6524 reset chip

        Examples:
            pcal6524.reset()

        '''
        self.i2c_bus.write(PCAL6524Def.RESET_ADDR, PCAL6524Def.RESET_VALUE)

    def get_pins_state(self, pins_list):
        '''
        PCAL6524 get_pins_state

        Args:
            pins_list: list,    eg:[1, 2] means read pin1,pin2,
                                pin number starts from 0.

        Returns:
            list, eg:[[1,1], [2, 1]] means read pin1 = 1,pin2 = 1.

        Examples:
            rd_data = pcal6524.get_pins_state([0, 1]])
            print(rd_data)

        '''
        assert isinstance(pins_list, list) and pins_list
        assert all(0 <= pin < 24 for pin in pins_list)

        pins_list = [[x] for x in pins_list]
        all_pin_list = self.read_register(PCAL6524Def.INPUT_PORT_0_REGISTER, 3)

        for index, pin in enumerate(pins_list):
            group = pin[0] / 8
            pin_index = pin[0] % 8
            pins_list[index].append((all_pin_list[group] >> pin_index) & 0x1)
        return pins_list

    def set_pins_state(self, pins_configure):
        '''
        PCAL6524 set_pins_state

        Args:
            pins_configure: list,   [[pinx, level],...],
                                    level is 0 or 1,means
                                    low level or high level.

        Examples:
            pcal6524.set_pins_state([[1, 0], [3,1]])

        '''
        assert isinstance(pins_configure, list) and pins_configure
        assert all(0 <= x[0] < 24 and x[1] in (0, 1) for x in pins_configure)

        all_pin_conf_list = self.read_register(
            PCAL6524Def.OUTPUT_PORT_0_REGISTER, 3)

        for pin in pins_configure:
            group = pin[0] / 8
            index = pin[0] % 8
            if pin[1] == 1:
                all_pin_conf_list[group] |= (1 << index)
            else:
                all_pin_conf_list[group] &= ~(1 << index)
        self.write_register(
            PCAL6524Def.OUTPUT_PORT_0_REGISTER,
            all_pin_conf_list)

    def set_pins_dir(self, pins_dir_configure):
        '''
        PCAL6524 set_pins_dir

        Args:
            pins_dir_configure: list,   [[pinx, dir],...],
                                        dir is 0 or 1,means
                                        output or input.

        Examples:
            pcal6524.set_pins_dir([[1, 0], [3,1]])

        '''
        assert isinstance(pins_dir_configure, list) and pins_dir_configure
        assert all(0 <= x[0] < 24 and x[1] in (0, 1)
                   for x in pins_dir_configure)

        dir_conf_list = self.read_register(
            PCAL6524Def.CONFIG_PORT_0_REGISTER, 3)

        for pin in pins_dir_configure:
            group = pin[0] / 8
            index = pin[0] % 8
            if pin[1] == 1:
                dir_conf_list[group] |= (1 << index)
            else:
                dir_conf_list[group] &= ~(1 << index)
        self.write_register(PCAL6524Def.CONFIG_PORT_0_REGISTER, dir_conf_list)

    def get_pins_dir(self, pins_dir_list):
        '''
        PCAL6524 get_pins_dir

        Args:
            pins_dir_list: list,    eg:[1, 2] means read pin1,pin2,
                                    pin number starts from 0.

        Returns:
           list,          eg:[[1,1], [2, 1]] means
                          pin1 is input,pin2 is output.

        Examples:
            rd_data = pcal6524.get_pins_dir([0, 1]])
            print(rd_data)

        '''
        assert isinstance(pins_dir_list, list) and pins_dir_list
        assert all(0 <= pin < 24 for pin in pins_dir_list)

        pins_dir_list = [[x] for x in pins_dir_list]
        dir_list = self.read_register(PCAL6524Def.CONFIG_PORT_0_REGISTER, 3)

        for index, pin in enumerate(pins_dir_list):
            group = pin[0] / 8
            pin_index = pin[0] % 8
            pins_dir_list[index].append((dir_list[group] >> pin_index) & 0x1)
        return pins_dir_list

    def set_pull_up_or_down(self, pin_pupd_configure):
        '''
        PCAL6524 set_pull_up_or_down

        Args:
            pin_pupd_configure: list,   [[int,str],...]
                                        eg:[[1,"up"], [2,"down"]] means
                                        pin1 pull up,pin2 pull down,
                                        pin number starts from 0.

        Examples:
            pcal6524.set_pull_up_or_down([[1, 0], [3,1]])

        '''
        assert isinstance(pin_pupd_configure, list) and pin_pupd_configure
        assert all(0 <= x[0] < 24 and x[1] in ("up", "down")
                   for x in pin_pupd_configure)

        pin_pupd_conf_list = self.read_register(
            PCAL6524Def.PUPD_SELECTION_PORT_0_REGISTER, 3)
        pin_pupd_enable_list = self.read_register(
            PCAL6524Def.PUPD_ENABLE_PORT_0_REGISTER, 3)

        for pin in pin_pupd_configure:
            group = pin[0] / 8
            index = pin[0] % 8
            if pin[1] == "up":
                pin_pupd_conf_list[group] |= (1 << index)
            else:
                pin_pupd_conf_list[group] &= ~(1 << index)
            pin_pupd_enable_list[group] |= (1 << index)

        self.write_register(
            PCAL6524Def.PUPD_ENABLE_PORT_0_REGISTER,
            pin_pupd_conf_list)
        self.write_register(
            PCAL6524Def.PUPD_SELECTION_PORT_0_REGISTER,
            pin_pupd_conf_list)

    def get_pull_up_or_down_state(self, pins_list):
        '''
        PCAL6524 get_pull_up_or_down_state

        Args:
            pins_list: list,    eg:[1, 2] means read pin1, pin2,
                                    pin number starts from 0.

        Returns:
            list,          eg:[[1,"up"], [2,"down"]] means
                           pin1 pull up,pin2 pull down.

        Examples:
            rd_data = pcal6524.get_pull_up_or_down_state([0, 1]])
            print(rd_data)

        '''
        assert isinstance(pins_list, list) and pins_list
        assert all(0 <= pin < 24 for pin in pins_list)

        pins_list = [[x] for x in pins_list]
        pin_pupd_config_list = self.read_register(
            PCAL6524Def.PUPD_SELECTION_PORT_0_REGISTER, 3)

        for index, pin in enumerate(pins_list):
            group = pin[0] / 8
            pin_index = pin[0] % 8
            if ((pin_pupd_config_list[group] >> pin_index) & 0x1) == 1:
                pins_list[index].append("up")
            else:
                pins_list[index].append("down")
        return pins_list

    def set_pins_mode(self, output_mode):
        '''
        PCAL6524 set_pins_mode

        Args:
            output_mode: list,    [[int,str],...]
                                         eg:[[0,"pp"], [1,"od"]] means
                                         pin1 pull up,pin2 pull down,
                                         pin number starts from 0.

        Examples:
            pcal6524.set_pins_mode([[1, "pp"], [3,"od"]])

        '''
        assert isinstance(output_mode, list) and output_mode
        assert all(0 <= x[0] < 24 and x[1] in ("pp", "od")
                   for x in output_mode)

        pin_output_conf_list = self.read_register(
            PCAL6524Def.INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION_REGISTER, 3)
        pin_od_enable_list = self.read_register(
            PCAL6524Def.OUTPUT_PORT_CONFIGURATION_REGISTER, 1)

        for pin in output_mode:
            group = pin[0] / 8
            index = pin[0] % 8
            if pin[1] == "od":
                pin_output_conf_list[group] |= (1 << index)
            else:
                pin_output_conf_list[group] &= ~(1 << index)
            pin_od_enable_list[0] |= (1 << group)

        self.write_register(
            PCAL6524Def.OUTPUT_PORT_CONFIGURATION_REGISTER,
            pin_od_enable_list)
        self.write_register(
            PCAL6524Def.INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION_REGISTER,
            pin_output_conf_list)

    def get_pins_mode(self, pins_list):
        '''
        PCAL6524 get_pins_mode

        Args:
            pins_list: list,    eg:[1, 2] means read pin1, pin2,
                                pin number starts from 0.

        Returns:
            list,      eg:[[0,"pp"], [2,"od"]] means
                       pin0 push pull,pin2 open drain.

        Examples:
            rd_data = pcal6524.get_pins_mode([0, 1]])
            print(rd_data)

        '''
        assert isinstance(pins_list, list) and pins_list
        assert all(0 <= pin < 24 for pin in pins_list)

        pins_list = [[x] for x in pins_list]
        pin_output_config_list = self.read_register(
            PCAL6524Def.INDIVIDUAL_PIN_OUTPUT_PORT_0_CONFIGURATION_REGISTER, 3)
        pin_od_enable_list = self.read_register(
            PCAL6524Def.OUTPUT_PORT_CONFIGURATION_REGISTER, 1)

        for index, pin in enumerate(pins_list):
            group = pin[0] / 8
            pin_index = pin[0] % 8
            if pin_od_enable_list[0] & (1 << group):
                pins_list[index].append("od" if 1 == ((
                                        pin_output_config_list[group] >>
                                        pin_index) & 0x1) else "pp")
            else:
                pins_list[index].append("pp")
        return pins_list
