# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'Jiashegn.Xie@SmartGiant'
__version__ = '0.1'


class PCAL6524Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


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

    RESET_ADDR = 0x00
    RESET_VALUE = [0x06]

    PIN_DIR_INPUT = 'input'
    PIN_DIR_OUTPUT = 'output'


class PCAL6524Emulator(object):
    '''
    PCAL6524 is a io expansion chip with 16bit port expansion

    ClassType = GPIO

    Args:
        dev_addr:    int,  I2C device address of PCAL6524.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                     If not using this parameter, will create Emulator.
        lock:        instance/None,  Class instance of lock.

    Examples:
        cat9555 = PCAL6524(0x20,'/dev/MIX_I2C_0')

    '''

    def __init__(self, dev_addr, i2c_bus=None, lock=None):
        assert (dev_addr & (~0x03)) == 0x20
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
            0x07: 0x00,
            0x0c: 0x00,
            0x0d: 0x00,
            0x0e: 0x00,
            0x4c: 0x00,
            0x4d: 0x00,
            0x4e: 0x00,
            0x50: 0x00,
            0x51: 0x00,
            0x52: 0x00,
            0x5c: 0x00,
            0x70: 0x00,
            0x71: 0x00,
            0x72: 0x00
        }
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def read_register(self, reg_addr, rd_len):
        '''
        PCAL6524 read specific length datas from address

        Args:
            reg_addr:   hexmial, [0~0xFF], Read datas from this address.
            rd_len:     int, [0~1024],     Length to read.

        Examples:
            rd_data = cat9555.read_register(0x00, 10)
            print(rd_data)

        '''
        assert reg_addr in self._reg.keys()
        # if self.lock is not None:
        #     self._recorder.record("PCAL6524 lock acquire")

        self._recorder.record("PCAL6524 read_register 0x%02x with %d bytes" % (reg_addr, rd_len))

        # if self.lock is not None:
        #     self._recorder.record("PCAL6524 lock release")

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def write_register(self, reg_addr, write_data):
        '''
        PCAL6524 write datas to address, support cross pages writing operation

        Args:
            reg_addr:    int, [0~1024], Write data to this address.
            write_data:  list,          Data to write.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            cat9555.write_register(0x00, wr_data)

        '''
        assert reg_addr in self._reg.keys()

        # if self.lock is not None:
        #     self._recorder.record("PCAL6524 lock acquire")

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("PCAL6524 write %s to 0x%02x" % (record_data, reg_addr))

        # if self.lock is not None:
        #     self._recorder.record("PCAL6524 lock release")

    def set_pin_dir(self, pin_id, dir):
        '''
        Set the direction of PCAL6524 pin

        Args:
            pin_id:   int, [0~23], Pin id.
            dir:      string, ['output', 'input'], Set pin dir.

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
            pin_id:   int, [0~23], Pin id you can choose of pca9536.

        Returns:
            string, ['output', 'input'].

        Examples:
            pcal6524.get_pin_dir(15)

        '''
        assert pin_id >= 0 and pin_id <= 23

        state = self.get_pins_dir([pin_id])
        if state != 0:
            return PCAL6524Def.PIN_DIR_INPUT
        else:
            return PCAL6524Def.PIN_DIR_OUTPUT

    def set_pin(self, pin_id, level):
        '''
        Set the level of PCAL6524 pin

        Args:
            pin_id:   int, [0~23], Pin id you can choose of pcal6524.
            level:    int, [0, 1], set pin level like 0 or 1.

        Examples:
            pcal6524.set_pin(12,1)

        '''
        assert pin_id >= 0 and pin_id <= 23
        self.set_pins_state([(pin_id, level)])

    def get_pin(self, pin_id):
        '''
        Get the level of pcal6524 pin

        Args:
            pin_id:   int, [0~23], Pin id you can choose of pcal6524.

        Returns:
            int, [0, 1].

        Examples:
            pcal6524.get_pin(1)

        '''
        assert pin_id >= 0 and pin_id <= 23

        self.get_pins_state([pin_id])[1]

    def get_ports(self):
        '''
        Get the value of input port register

        Returns:
            list, [value].

        Examples:
            result = pcal6524.get_ports()
            print(result)

        '''
        return self.read_register(PCAL6524Def.INPUT_PORT_0_REGISTER, 3)

    def set_ports(self, ports_list):
        '''
        Set the value of input port register.

        Args:
            ports_list:   list, Element takes one byte. eg:[0x12].

        Examples:
            pcal6524.set_ports([0x12])

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
                                pin number starts from 0

        Returns:
            list, eg:[[1,1], [2, 1]] means read pin1 = 1,pin2 = 1

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
                                           low level or high level

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
                                               output or input

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
                                           pin number starts from 0

        Returns:
            list,          eg:[[1,1], [2, 1]] means
                           pin1 is input,pin2 is output

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
                                               pin number starts from 0

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
            pins_dir_list: list,    eg:[1, 2] means read pin1, pin2,
                                           pin number starts from 0

        Returns:
            list,          eg:[[1,"up"], [2,"down"]] means
                           pin1 pull up,pin2 pull down

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
            pin_pupd_configure: list,    [[int,str],...]
                                                eg:[[0,"pp"], [1,"od"]] means
                                                pin1 pull up,pin2 pull down,
                                                pin number starts from 0

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
            list,          eg:[[0,"pp"], [2,"od"]] means
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
