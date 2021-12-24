# -*- coding: utf-8 -*-
import re
import os
import time
from subprocess import PIPE, STDOUT, Popen
from mix.driver.core.bus.gpio_emulator import GPIOEmulator
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.ic.cat24cxx import CAT24C02
from mix.driver.smartgiant.common.module.mix_board import MIXBoard


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class DarkBeastDef:
    EXIT_STRING = 'Exit'
    RESULT_END_FLAG = '^_^)'
    RESULT_CHECK_FLAG = ')'

    DEFAULT_TIMEOUT = 5
    EEPROM_DEV_ADDR = 0x50

    PL_GPIO_REG_SIZE = 256
    PL_GPIO_PIN_NUM = 42
    LOWE_LEVEL = 0

    A0_PIN_ID = 0
    A1_PIN_ID = 1
    A2_PIN_ID = 2
    ELAOD_EN_PIN_ID = 6


class DarkBeastCMDDef:
    EXIT = 'EXIT'


class DarkBeastException(Exception):
    '''
    DarkBeast exception class.
    '''

    def __init__(self, err_str):
        self.reason = "DarkBeastException {}".format(err_str)

    def __str__(self):
        return self.reason


class DarkBeastBase(MIXBoard):
    '''
    Base class of DarkBeast and DarkBeastCompatible.

    Providing common DarkBeast methods

    Args:
        firmware_path:       string,           DarkBeast firmware absolute path
        pl_uart_drv_ko_file: string,           DarkBeast pl_uart_drv.ko drive absolute path
                                               if None creating emulator.
        i2c:             instance(I2C)/None,   Class instance of PLI2CBus, which is used to control cat9555,
                                               eeprom and AD5667 sensor.
        gpio:            instance(GPIO)/None,  Class instance of PLGPIO, UART RX connect AID to enable or disable.
                                               if None creating emulator.
        pull_up_pin:     instance(GPIO)/None,  Class instance of GPIO, data line pull-up control, Provider mode.
                                               if None creating emulator.
        pull_down_pin:   instance(GPIO)/None,  Class instance of GPIO, data line pull-down control, Consumer mode.
                                               if None creating emulator.
        tx_en_pin:       instance(GPIO)/None,  Class instance of GPIO, UART_TX buffer enable control.
                                               if None creating emulator.
        connect_det_pin: instance(GPIO)/None,  Class instance of GPIO, input pin control, detects whether
                                               the DUT is connected. if None creating emulator.
        removal_det_pin: instance(GPIO)/None,  Class instance of GPIO, Input pin control, detect disconnection
                                               from DUT. if None creating emulator.
        a0_pin:          instance(GPIO)/None,  Class instance of Pin, if None creating emulator.
        a1_pin:          instance(GPIO)/None,  Class instance of Pin, if None creating emulator.
        a2_pin:          instance(GPIO)/None,  Class instance of Pin, if None creating emulator.
        elaod_en_pin:    instance(GPIO)/None,  Class instance of Pin, if None creating emulator.
        eeprom_devaddr:  int,                  Eeprom device address.

    '''

    rpc_public_api = ['module_init', 'close', 'open', 'communicate',
                      'aid_connect_set', 'io_set', 'io_get'] + MIXBoard.rpc_public_api

    def __init__(self, firmware_path, pl_uart_drv_ko_file, i2c, pull_up_pin,
                 pull_down_pin, tx_en_pin, removal_det_pin, connect_det_pin,
                 a0_pin, a1_pin, a2_pin, elaod_en_pin, eeprom_devaddr, gpio):
        self.path = firmware_path
        self.process = None
        self.pl_uart_drv_ko_file = pl_uart_drv_ko_file
        if(firmware_path == '' and pl_uart_drv_ko_file == '' and i2c is None and
           pull_up_pin is None and pull_down_pin is None and tx_en_pin is None and
           removal_det_pin is None and connect_det_pin is None):
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.pull_up_pin = GPIOEmulator('pull_up_pin')
            self.pull_down_pin = GPIOEmulator('pull_down_pin')
            self.tx_en_pin = GPIOEmulator('tx_en_pin')
            self.removal_det_pin = GPIOEmulator('removal_det_pin')
            self.connect_det_pin = GPIOEmulator('connect_det_pin')
        elif(firmware_path != '' and pl_uart_drv_ko_file != '' and i2c is not None and
             pull_up_pin is not None and pull_down_pin is not None and tx_en_pin is not None and
             removal_det_pin is not None and connect_det_pin is not None):
            self.eeprom = CAT24C02(eeprom_devaddr, i2c)
            self.pull_up_pin = pull_up_pin
            self.pull_down_pin = pull_down_pin
            self.tx_en_pin = tx_en_pin
            self.removal_det_pin = removal_det_pin
            self.connect_det_pin = connect_det_pin
        else:
            raise DarkBeastException('__init__ error! Please check the parameters!')
        self.gpio = gpio
        if(a0_pin is None and a1_pin is None and a2_pin is None and elaod_en_pin is None):
            self.a0_pin = Pin(None, DarkBeastDef.A0_PIN_ID)
            self.a1_pin = Pin(None, DarkBeastDef.A1_PIN_ID)
            self.a2_pin = Pin(None, DarkBeastDef.A2_PIN_ID)
            self.elaod_en_pin = Pin(None, DarkBeastDef.ELAOD_EN_PIN_ID)
        elif(a0_pin is not None and a1_pin is not None and a2_pin is not None and elaod_en_pin is not None):
            self.a0_pin = a0_pin
            self.a1_pin = a1_pin
            self.a2_pin = a2_pin
            self.elaod_en_pin = elaod_en_pin
        else:
            raise DarkBeastException('__init__ error! Please check the parameters!')

        super(DarkBeastBase, self).__init__(self.eeprom, None)
        self.pin_def = {
            'PULL_UP': self.pull_up_pin,
            'PULL_DOWN': self.pull_down_pin,
            'TX_EN': self.tx_en_pin,
            'REMOVAL_DETECTION': self.removal_det_pin,
            'CONNECT_DETECTION': self.connect_det_pin,
            'A0': self.a0_pin,
            'A1': self.a1_pin,
            'A2': self.a2_pin,
            'ELAOD_EN': self.elaod_en_pin
        }

    def __del__(self):
        self.close()

    def _capture_by_flag(self):
        '''
        capture end flag of result.
        '''
        last_time = time.time()
        data_str = ""
        while(time.time() - last_time < DarkBeastDef.DEFAULT_TIMEOUT):
            read_str = self.process.stdout.read(1)
            data_str = data_str + read_str
            if read_str == DarkBeastDef.RESULT_CHECK_FLAG:
                if data_str.endswith(DarkBeastDef.RESULT_END_FLAG):
                    break
        if time.time() - last_time >= DarkBeastDef.DEFAULT_TIMEOUT:
            raise DarkBeastException('process read wait timeout!')

        return data_str.strip(DarkBeastDef.RESULT_END_FLAG)

    def _update_linux_driver(self):
        ''' update pl_uart_drv.ko if exist '''
        if os.path.isfile(self.pl_uart_drv_ko_file):
            os.system('rmmod ' + self.pl_uart_drv_ko_file)
            os.system('insmod ' + self.pl_uart_drv_ko_file)

    def module_init(self):
        '''
        DarkBeast module init, initialize ad5592r channel mode and open DarkBeast process.

        Returns:
            string, str, return open information.

        Examples:
            DarkBeast.module_init()

        '''
        self._update_linux_driver()
        ret_str = 'done'
        if os.path.isfile(self.path):
            ret_str = self.open()

        # set plgpio init
        if self.gpio:
            self.gpio.set_dir('output')
            self.gpio.set_level(DarkBeastDef.LOWE_LEVEL)

        # set gpio init
        self.pull_up_pin.set_dir('output')
        self.pull_up_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.pull_down_pin.set_dir('output')
        self.pull_down_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.tx_en_pin.set_dir('output')
        self.tx_en_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.connect_det_pin.set_dir('input')
        self.removal_det_pin.set_dir('input')

        # set pin init
        self.a0_pin.set_dir('output')
        self.a0_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.a1_pin.set_dir('output')
        self.a1_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.a2_pin.set_dir('output')
        self.a2_pin.set_level(DarkBeastDef.LOWE_LEVEL)
        self.elaod_en_pin.set_dir('output')
        self.elaod_en_pin.set_level(DarkBeastDef.LOWE_LEVEL)

        return ret_str

    def close(self):
        '''
        close the DarkBeast process.

        Returns:
            string, "done", api execution successful.

        '''
        if self.process is not None:
            string_list = []
            pid_list = []
            pgid = os.getpgid(self.process.pid)

            command = 'ps -C {}'.format(os.path.basename(self.path))
            progress = Popen(command, shell=True, stdin=PIPE, stdout=PIPE)
            string = progress.communicate()[0]
            string_list = string.split("\n")
            for line in string_list:
                pid = re.findall("\d+", line)
                if len(pid) != 0:
                    pid_list.append(pid[0])

            for pid in pid_list:
                if os.getpgid(int(pid)) == pgid:
                    command = "kill " + pid
                    os.system(command)
            self.process = None

        return 'done'

    def open(self):
        '''
        open DarkBeast process by Popen, and return open information or faild raising Exception

        Returns:
            string, str, return open information.

        '''
        assert os.access(self.path, os.F_OK | os.X_OK), 'path <{}> not exist or execute'.format(self.path)
        if self.process is not None:
            return 'done'

        command = 'cd {};./{}'.format(os.path.dirname(self.path), os.path.basename(self.path))

        # stderr is standard error output, can be file descriptors and STDOUT. None means no output
        self.process = Popen([command, ""], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        return self._capture_by_flag()

    def communicate(self, command):
        '''
        communicate with DarkBeast process. if process not open, raise DarkBeastException

        Args:
            command:  string, command string.

        Returns:
            string, str, return information.

        Examples:
            cmd_string = "SWITCH2HS"
            print DarkBeast.communicate(cmd_string)

        Raise:
            DarkBeastException:  process not open, communicate error!

        '''
        if self.process is not None:
            self.process.stdin.write(command + "\n")
            self.process.stdin.flush()
            if DarkBeastCMDDef.EXIT == command:
                self.process = None
                return DarkBeastDef.EXIT_STRING
            else:
                return self._capture_by_flag()

        raise DarkBeastException('process not open, communicate error!')

    def aid_connect_set(self, status):
        '''
        AID connect to dut enable or disable

        Args:
            status:  string, ['enable', 'disable'].

        Returns:
            string, "done", api execution successful.

        Examples:
            DarkBeast.aid_connect_set(1)

        '''
        assert status in ('enable', 'disable')
        if status == 'enable':
            level = 1
        else:
            level = 0
        if self.gpio:
            self.gpio.set_level(level)

        return 'done'

    def io_set(self, io_name, level):
        '''
        DarkBeast io control.

        Args:
            io_name:  string, ['PULL_UP', 'PULL_DOWN', 'TX_EN', 'CONNECT_DETECTION', 'REMOVAL_DETECTION',
                               'A0', 'A1', 'A2', 'ELAOD_EN'], io_name can be found in the table below.

                +---------------------+----------------------------------+
                |     io  name        |            io  meaning           |
                +=====================+==================================+
                |  PULL_UP            |  Data line pull-up control,      |
                |                     |  Provider mode.                  |
                +---------------------+----------------------------------+
                |  PULL_DOWN          |  Data line pull-down control,    |
                |                     |  Consumer mode.                  |
                +---------------------+----------------------------------+
                |  TX_EN              |  UART_TX buffer enable control   |
                +---------------------+----------------------------------+
                |  CONNECT_DETECTION  |  input pin control, detect       |
                |                     |  whether the DUT is connected.   |
                +---------------------+----------------------------------+
                |  REMOVAL_DETECTION  |  Input pin control, detect       |
                |                     |  disconnection from DUT.         |
                +--------------------------------------------------------+
                |       A0            |  ORION_COMM_CONN connect         |
                |                     |  PPVBUS_ORION_CONN.              |
                +---------------------+----------------------------------+
                |       A1            |  GND connect ORION_COMM_CONN     |
                +---------------------+----------------------------------+
                |       A2            |  GND connect PPVBUS_ORION_CONN   |
                +---------------------+----------------------------------+
                |       ELAOD_EN      |  A0, A1, A2 control1 disabled or |
                |                     |  enabled  (1/disabled  0/enabled)|
                +---------------------+----------------------------------+

            level:  int, [0, 1], 0/1 means lower/high

        Returns:
            string, "done", api execution successful.

        Examples:
            darkbeast.io_set("PULL_UP", 1)

        '''
        assert io_name in ["PULL_UP", "PULL_DOWN", "TX_EN",
                           "CONNECT_DETECTION", "REMOVAL_DETECTION",
                           "A0", "A1", "A2", "ELAOD_EN"]

        device = self.pin_def[io_name]
        device.set_level(level)

        return 'done'

    def io_get(self, io_name):
        '''
        DarkBeast io level get

        Args:
            io_name:  string, ['PULL_UP', 'PULL_DOWN', 'TX_EN', 'CONNECT_DETECTION', 'REMOVAL_DETECTION',
                               'A0', 'A1', 'A2', 'ELAOD_EN'], io_name can be found in the table below.

                +---------------------+----------------------------------+
                |     io  name        |            io  meaning           |
                +=====================+==================================+
                |  PULL_UP            |  Data line pull-up control,      |
                |                     |  Provider mode.                  |
                +---------------------+----------------------------------+
                |  PULL_DOWN          |  Data line pull-down control,    |
                |                     |  Consumer mode.                  |
                +---------------------+----------------------------------+
                |  TX_EN              |  UART_TX buffer enable control   |
                +---------------------+----------------------------------+
                |  CONNECT_DETECTION  |  input pin control, detect       |
                |                     |  whether the DUT is connected.   |
                +---------------------+----------------------------------+
                |  REMOVAL_DETECTION  |  Input pin control, detect       |
                |                     |  disconnection from DUT.         |
                +--------------------------------------------------------+
                |       A0            |  ORION_COMM_CONN connect         |
                |                     |  PPVBUS_ORION_CONN.              |
                +---------------------+----------------------------------+
                |       A1            |  GND connect ORION_COMM_CONN     |
                +---------------------+----------------------------------+
                |       A2            |  GND connect PPVBUS_ORION_CONN   |
                +---------------------+----------------------------------+
                |       ELAOD_EN      |  A0, A1, A2 control1 disabled or |
                |                     |  enabled  (1/disabled  0/enabled)|
                +---------------------+----------------------------------+

        Returns:
            int, [0, 1], io level.

        Examples:
            level = darkbeast.io_get("PULL_UP")
            print(level)

        '''
        assert io_name in ["PULL_UP", "PULL_DOWN", "TX_EN",
                           "CONNECT_DETECTION", "REMOVAL_DETECTION",
                           "A0", "A1", "A2", "ELAOD_EN"]

        device = self.pin_def[io_name]

        return device.get_level()


class DarkBeast(DarkBeastBase):
    '''
    Dark Beast is a keyboard peripheral simulation module.

    compatible = ["GGQQ-OA3001002-000"]

    OAB is short for Orion accessory board.
    The interface between the module and DUT has three connection points. ORION_COMM_CONN is the
    communication interface to carry out AID (slave) communication and UART communication with DUT,
    with the highest UART communication rate of 1Mbps. PPVBUS_ORION_CONN is the power interface.
    The first is the power supply capacity of DUT tested as CV ELOAD, and the second is to charge
    DUT as the power supply interface. A mock switch is also included for contamination testing at
    the DUT ORION interface point.
    This class is legacy driver for normal boot.

    Args:
        firmware_path:       string,           DarkBeast firmware absolute path
        pl_uart_drv_ko_file: string,           DarkBeast pl_uart_drv.ko drive absolute path
                                               if None creating emulator.
        i2c:             instance(I2C)/None,   Class instance of PLI2CBus, which is used to control cat9555,
                                               eeprom and AD5667 sensor.
        pull_up_pin:     instance(GPIO)/None,  Class instance of GPIO, data line pull-up control, Provider mode.
                                               if None creating emulator.
        pull_down_pin:   instance(GPIO)/None,  Class instance of GPIO, data line pull-down control, Consumer mode.
                                               if None creating emulator.
        tx_en_pin:       instance(GPIO)/None,  Class instance of GPIO, UART_TX buffer enable control.
                                               if None creating emulator.
        connect_det_pin: instance(GPIO)/None,  Class instance of GPIO, input pin control, detects whether
                                               the DUT is connected. if None creating emulator.
        removal_det_pin: instance(GPIO)/None,  Class instance of GPIO, Input pin control, detect disconnection
                                               from DUT. if None creating emulator.
        a0_pin:          instance(GPIO)/None,   Class instance of Pin, if None creating emulator.
        a1_pin:          instance(GPIO)/None,   Class instance of Pin, if None creating emulator.
        a2_pin:          instance(GPIO)/None,   Class instance of Pin, if None creating emulator.
        elaod_en_pin:    instance(GPIO)/None,   Class instance of Pin, if None creating emulator.
        gpio:            instance(GPIO)/None,  Class instance of PLGPIO, UART RX connect AID to enable or disable.
                                               It is not used for new project.

    Examples:
        firmware_path = '/root/HSAID_FCT.elf'
        pl_uart_drv_ko_file = '/root/pl_uart_drv.ko'
        axi4 = AXI4LiteBus('/dev/AXI4_I2C_2', 256)
        i2c = PLI2CBus(axi4)
        axi4 = AXI4LiteBus('/dev/AXI4_GPIO_0', 256)
        gpio = PLGPIO(axi4)
        pull_up_pin = GPIO(54)
        pull_down_pin = GPIO(55)
        tx_en_pin = GPIO(56)
        removal_det_pin = GPIO(57)
        connect_det_pin = GPIO(58)
        cat9555 = CAT9555(0x20, i2c)
        a0_pin = Pin(cat9555, 0)
        a1_pin = Pin(cat9555, 1)
        a2_pin = Pin(cat9555, 2)
        elaod_en_pin = Pin(cat9555, 6)
        darkbeast = DarkBeast(firmware_path, pl_uart_drv_ko_file, i2c, pull_up_pin,
                              pull_down_pin, tx_en_pin, removal_det_pin, connect_det_pin,
                              a0_pin, a1_pin, a2_pin, elaod_en_pin, gpio)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ['GQQ-OA3001002-000']

    def __init__(self, firmware_path='', pl_uart_drv_ko_file='', i2c=None, pull_up_pin=None,
                 pull_down_pin=None, tx_en_pin=None, removal_det_pin=None, connect_det_pin=None,
                 a0_pin=None, a1_pin=None, a2_pin=None, elaod_en_pin=None, gpio=None):

        super(DarkBeast, self).__init__(firmware_path, pl_uart_drv_ko_file, i2c, pull_up_pin,
                                        pull_down_pin, tx_en_pin, removal_det_pin, connect_det_pin,
                                        a0_pin, a1_pin, a2_pin, elaod_en_pin, DarkBeastDef.EEPROM_DEV_ADDR, gpio)
