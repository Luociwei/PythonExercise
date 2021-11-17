# -*- coding: UTF-8 -*-
import os
import time
from array import array

from mix.driver.smartgiant.common.ic.tps6598x.tps6598x import TPS6598x
from mix.driver.smartgiant.common.ic.tps6598x import hi_functions
from mix.driver.smartgiant.common.ic.tps6598x import register_definitions
from mix.driver.smartgiant.common.ic.tps6598x import device_rw

__author__ = 'jionghao@SmartGiant' + 'yuchen@SmartGiant'
__version__ = '0.4'


class REGION0:
    APP_START_ADDR = 0x2000
    HEADER_ADDR = 0x00
    NUMBER = 0


class REGION1:
    APP_START_ADDR = 0x20000
    HEADER_ADDR = 0x1000
    NUMBER = 1


class USBC001001Def:
    REGION0_NAME = "region0"
    REGION1_NAME = "region1"

    CURRENT_COEFFICIENT = 10
    VOLTAGE_COEFFICIENT = 50
    DEVICE_ID_LIST = [0x01, 0x00, 0xE0, 0xAC]   # ID=0xACE00001
    APP_SECTOR_SIZE = 17                        # 4K Bytes per sector
    FLASH_WRITE_PAGE_SIZE = 16                  # Bytes

    SN_ADDRESS = 0x40000
    REGION0_VERSION_ADDRESS = 0x41000
    REGION1_VERSION_ADDRESS = 0x42000

    INT_2_BYTE_ARRAY_LEN = 4
    INT_2_BYTE_ARRAY_FILLING_VAL = 0
    STR_EOF_MARK = 0xff
    READ_STR_LOOP_TIMES = 5
    TPS6598X_EMULATOR_DEVICE_ADDR = 0x38
    HEADER_OFFSET = 0x1000 - 4
    FIRMWARE_DIV_SIZE = 0x400
    FLOAT_TO_PERCENT = 100

    FLWD_OFFSET_CONFIG_ARRAY = array('B', [0, 0, 0, 0])

    PD0_MIN_NUMBER = 0
    PD0_MAX_NUMBER = 7
    MIN_CURRENT = 0
    MAX_CURRENT = 10230
    MIN_VOLTAGE = 0
    MAX_VOLTAGE = 51150
    AGID_HW_SLEEP_MS = 500

    GPIO_MIN_NUM = 0
    GPIO_MAX_NUM = 17
    HIGH_LEVEL = 1
    LOW_LEVEL = 0

    PDO1_SWITCH = {'PP_5V': 0, 'PP_HV': 2, 'PP_HVE': 3}
    PDOn_SWITCH = {'PP_HV': 0, 'PP_HVE': 1}
    INPUT_DIR = "input"
    OUTPUT_DIR = "output"

    FLRD_WRITE_DATA_LEN = 5
    FLRD_WRITE_ADDR = 0x09
    FLRD_WRITE_4CC_ADDR = 0x08
    FLRD_CHECK_DATA_LEN = 17

    GAID_WRITE_4CC_REG = 0x08

    NUM_PDOs_file_name = 'numPDOs'
    NUM_PDOs_MIN = 0
    NUM_PDOs_MAX = 7

    PEAK_CURRENT_MAP = {
        "100%": 0,
        "130%": 1,
        "150%": 2,
        "200%": 3
    }

    TPS6598X_DEVICE_ADDR_LIST = {"XA": 0x38, "XB": 0X39}
    usbc_option_dict = {
        # These bits are controled by tps6598x which on usbc001001, and setting configure to different mode for U disk.
        "RESET": {0: 0, 1: 0, 2: 0, 3: 0, 6: 0, 7: 1, 8: 0, 12: 0, 13: 0, 14: 0, 15: 0},
        "USB2.0_TOP": {0: 0, 1: 1, 2: 0, 3: 0, 6: 0, 7: 0, 8: 0, 12: 0, 13: 1, 14: 1, 15: 1},
        "USB2.0_BOT": {0: 0, 1: 0, 2: 1, 3: 0, 6: 0, 7: 0, 8: 1, 12: 1, 13: 1, 14: 0, 15: 0},
        "USB3.0_TOP": {0: 0, 1: 0, 2: 0, 3: 1, 6: 0, 7: 0, 8: 0, 12: 1, 13: 1, 14: 1, 15: 1},
        "USB3.0_BOT": {0: 0, 1: 0, 2: 0, 3: 0, 6: 1, 7: 0, 8: 1, 12: 1, 13: 1, 14: 1, 15: 1},
        "Eload_TOP": {0: 1, 7: 0, 8: 0, 13: 0},
        "Eload_BOT": {0: 1, 7: 0, 8: 1, 13: 0}
    }

    USBC_ID = ["XA", "XB"]


ADC_NAME_LIST = [
    'BRICKID_RFU', 'CC1_BY2', 'CC1_BY5', 'CC2_BY2', 'CC2_BY5', 'GPIO_0', 'GPIO_1', 'GPIO_10 (BUSPOWER_Z)',
    'GPIO_2', 'GPIO_3', 'GPIO_4', 'GPIO_5', 'GPIO_5_RAW', 'GPIO_6', 'GPIO_7', 'GPIO_8', 'I2CADDR', 'IN_3P3V',
    'I_CC', 'I_PP_5V0', 'I_PP_EXT', 'I_PP_HV', 'OUT_3P3V', 'PP_5V0', 'PP_CABLE', 'PP_HV', 'SENSEP', 'V1P8_A',
    'V1P8_D', 'V3P3', 'VBUS', 'THERMAL_SENSE'
]

PORT_MAP = {'PP_5V': 'PP_5V0config',
            'PP_HV': 'PP_HVconfig', 'PP_HVE': 'PP_HVEconfig'}

STATE_MAP = {
    'SwitchConfig_DISABLED': 0,
    'SwitchConfig_AS_OUT': 1,
    'SwitchConfig_AS_IN': 2,
    'SwitchConfig_AS_IN_AFTER_SYSRDY': 3,
    'SwitchConfig_AS_OUT_IN': 4,
    'SwitchConfig_AS_OUT_IN_AFTER_SYSRDY': 5
}

TypeCCurrent_map_list = {'STD': 0, '1.5A': 1, '3.0A': 2, 'NONE': 3}


def show(register):
    '''
    Show register info.

    insert 'RAW DATA' info to register.show(), as bellow:\r\n
    PD Status (0x40)\r\n
    RAW DATA: 0x00000030\r\n
    [1:0]     PlugDetails     USB type-C fully featured plug\r\n
    [3:2]     CCPullUp        Not in CC pull-down mode / no CC pull-up detected\r\n
    [5:4]     PortType        Source/Sink\r\n
    [6:6]     PresentRole     Sink\r\n
    [12:8]    SoftResetType   SoftResetType_None\r\n
    [21:16]   HardResetType   HardReset_None\r\n

    Args:
        register:   instance(cRegister),    cRegister instance.

    Returns:
        string, str, information of register.

    Examples:
        register_info = show(register_definitions.PD_STATUS)\r\n
        print(register_info)\r\n
    '''
    byteArray = register.byteArray()
    raw_string = reduce((lambda x, y: "%.2x" % (y) + x), byteArray, '')
    raw_string = 'RAW DATA: 0x' + raw_string

    info = register.show()
    info_list = info.split('\r\n')
    info_list.insert(1, raw_string)
    info_string = '\r\n'.join(info_list)

    return info_string


class Usbc001001Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s' % (err_str)

    def __str__(self):
        return self.err_reason


class USBC001001(object):
    '''
    USBC001001 function class

    Args:
        i2c:    instance(I2C), class of I2C, which is used to control TPS6598x.
        source_capabilities:    instance(list), is used to reconfig source capabilities, effect after module init.
                                            source_capabilities list support max 7 capabilities, and the voltage of
                                            the first capability must is 5000. Unit is mV and mA. If default, will
                                            be configured to advertise 5V, 9V, 12V, 15V, 20V by tps6598x chip FW.
                                            Example as bellow:
                                            "source_capabilities": [
                                                {"voltage": 5000, "max_current": 3000, "source_switch": "PP_5V"},
                                                {"voltage": 12000, "max_current": 3000, "source_switch": "PP_HVE"},
                                                {"voltage": 15000, "max_current": 3000, "source_switch": "PP_HVE"}
                                            ],
        emarker:  instance(bool), is used to enable/disable Emarker function for support > 3A current, default is False.

    Examples:
        i2c = I2C('/dev/i2c-1')
        source_capabilities = [
            {"voltage": 5000, "max_current": 3000, "source_switch": "PP_5V"},
            {"voltage": 12000, "max_current": 3000, "source_switch": "PP_HVE"},
            {"voltage": 15000, "max_current": 3000, "source_switch": "PP_HVE"}
        ],
        usbc001001 = USBC001001(i2c, source_capabilities, emarker=False)

    '''

    rpc_public_api = ['usbc_set_pin', 'usbc_option', 'usbc_get_pin', 'module_init', 'read_all_registers',
                      'read_register_by_address', 'read_register_by_name', 'flash_programmer',
                      'set_sink_capabilities', 'set_source_capabilities', 'read_all_adc', 'read_adc_by_name',
                      'set_firmware_region_pointer', 'reset', 'set_power_switch_config', 'set_pin_dir',
                      'set_pin', 'get_pin', 'change_source_pdo_count', 'change_pullup',
                      'write_register_by_address', 'write_register_by_name', 'enable_emarker',
                      'disable_emarker']

    def __init__(self, i2c, source_capabilities=[], emarker=False):

        self.i2c = i2c
        self.tps6598x_0 = TPS6598x(
            USBC001001Def.TPS6598X_DEVICE_ADDR_LIST['XA'], self.i2c)
        self.tps6598x_1 = TPS6598x(
            USBC001001Def.TPS6598X_DEVICE_ADDR_LIST['XB'], self.i2c)

        self.tps6598x = {
            'XA': self.tps6598x_0,
            'XB': self.tps6598x_1
        }
        self.source_capabilities = source_capabilities
        self.emarker = emarker

    def module_init(self, chip_id):
        '''
        USBC001001 Configure source capabilities.

        Args:
            chip_id:     string, ["XA", "XB"].

        Returns:
            string, "done", api execution successful.

        Examples:
            usbc001001.module_init("XA")

        '''
        if isinstance(self.source_capabilities, list) and len(self.source_capabilities) > 0:
            try:
                # assert for limit the first capability to 5V
                assert isinstance(
                    self.source_capabilities[0], dict) and self.source_capabilities[0]['voltage'] == 5000
                for index in range(len(self.source_capabilities)):
                    assert isinstance(self.source_capabilities[index], dict)
                    params = self.source_capabilities[index]
                    params['PDO_number'] = index + 1
                    self.set_source_capabilities(chip_id, **params)
                self.change_source_pdo_count(
                    chip_id, len(self.source_capabilities))
            except (AssertionError, Usbc001001Exception):
                raise Usbc001001Exception("\r\n\
                    source_capabilities profile config error, max 7 capabilities, \r\n\
                    and the voltage of the first capability must is 5000. Unit is mV and mA. If default, will \r\n\
                    be configured to advertise 5V, 9V, 12V, 15V, 20V by tps6598x chip FW. Example as bellow:\r\n \
                    \"source_capabilities\": [\r\n\
                        {\"voltage\": 5000, \"max_current\": 3000, \"source_switch\": \"PP_5V\"},\r\n\
                        {\"voltage\": 12000, \"max_current\": 3000, \"source_switch\": \"PP_HVE\"},\r\n\
                        {\"voltage\": 15000, \"max_current\": 3000, \"source_switch\": \"PP_HVE\"}\r\n\
                    ]\r\n\
                    Detail please refer to set_source_capabilities function for parameter description")

        # config emarker enable/disable
        assert isinstance(self.emarker, bool), "profile config error, emarker need bool type, but {}".format(
            type(self.emarker))
        self.enable_emarker(
            chip_id) if self.emarker else self.disable_emarker(chip_id)

        return 'done'

    def usbc_set_pin(self, chip_id, bit_num_and_state_dict):
        '''
        USBC001001 set pin of usbc

        Args:
            chip_id:                     string, ["XA", "XB"].
            bit_num_and_state_dict:      dict, make up bit number and bit status such as {0:1, 1:1}.

        Returns:
            string, str, set result info.

        Examples:
            usbc001001.usbc_set_pin('XA', {0:1, 1:1})

        Raise:
            Usbc001001Exception: set chip  pin not Success.

        '''
        assert chip_id in USBC001001Def.USBC_ID

        for bit_num in bit_num_and_state_dict:

            assert (int(bit_num) >= 0) and (int(bit_num) <= 17)
            result = self.set_pin(
                chip_id, int(bit_num), bit_num_and_state_dict[bit_num])
            if result != "Success":
                raise Usbc001001Exception(
                    "set chip [%s] pin [%d] result: %s" % (chip_id, int(bit_num), result))

        return result

    def usbc_get_pin(self, chip_id, bit_number_list):
        '''
        USBC001001 usbc_get_pin

        Args:
            chip_id:            string, ["XA", "XB"].
            bit_number_list:    list, (1-17).

        Returns:
            string, str, set result info.

        Examples:
            usbc001001.usbc_get_pin('XA', [0,1,2])

        '''
        assert chip_id in USBC001001Def.USBC_ID

        ret_str = ''

        for bit_number in bit_number_list:
            assert (bit_number >= 0) and (bit_number <= 17)
            result = self.get_pin(chip_id, bit_number)
            ret_str += "bit" + str(bit_number) + "=" + str(result) + ','

        return ret_str

    def usbc_option(self, chip_id, option_name):
        '''
        USBC001001 set option.

        Args:
            chip_id:     string, ["XA", "XB"].
            option_name: string, ['RESET', 'USB2.0_TOP', 'USB2.0_BOT', 'USB3.0_TOP',
                                  'USB3.0_BOT', 'Eload_TOP', 'Eload_BOT']

        Returns:
            string, str, set result info.

        Examples:
            usbc001001.usbc_option('XA', 'USB3.0_TOP')

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert option_name in USBC001001Def.usbc_option_dict

        return self.usbc_set_pin(chip_id, USBC001001Def.usbc_option_dict[option_name])

    def _int_2_byte_array(self, value):
        '''
        Int value to byte array function, called inside.
        '''
        byte_array = hi_functions.byteArray(value)
        for i in range(USBC001001Def.INT_2_BYTE_ARRAY_LEN - len(byte_array)):
            byte_array.append(USBC001001Def.INT_2_BYTE_ARRAY_FILLING_VAL)

        return byte_array

    def _FLrd(self, handle, address):
        '''
        Flash memory read 16_Byte from address
        '''
        data_in = hi_functions.byteArray(address)
        for i in range(USBC001001Def.FLRD_WRITE_DATA_LEN - len(data_in)):
            data_in.append(0)
        device_rw.write_reg(handle, USBC001001Def.FLRD_WRITE_ADDR, data_in)
        device_rw.write_reg_4cc(
            handle, USBC001001Def.FLRD_WRITE_4CC_ADDR, 'FLrd')

        cmdret = hi_functions.verify_cmd_completed(
            handle, hi_functions.FLASH_HI_TIMEOUT)
        if (cmdret == "Success"):
            (count, data_out) = device_rw.read_reg(
                handle, USBC001001Def.FLRD_WRITE_ADDR, USBC001001Def.FLRD_CHECK_DATA_LEN)
            return data_out

        return cmdret

    def _GAID(self, chip_id):
        '''
        Refactoring hi_functions' AGID function
        '''
        device_rw.write_reg_4cc(
            self.tps6598x[chip_id], USBC001001Def.GAID_WRITE_4CC_REG, 'GAID')
        device_rw.hw_sleep_ms(USBC001001Def.AGID_HW_SLEEP_MS)

    def _is_file_valid(self, file_name):
        '''match with device id'''
        with open(file_name, 'rb') as fd:
            read_data = fd.read(len(USBC001001Def.DEVICE_ID_LIST))
            read_id = array('B', read_data).tolist()
            if read_id != USBC001001Def.DEVICE_ID_LIST:
                raise Usbc001001Exception('not a valid low-region file_name, %s != %s' %
                                          (read_id, USBC001001Def.DEVICE_ID_LIST))

    def _flash_erase(self, chip_id, region):
        if 'Success' != hi_functions.FLem(self.tps6598x[chip_id], region.APP_START_ADDR, USBC001001Def.APP_SECTOR_SIZE):
            raise Usbc001001Exception("flash erase fail.")
        print("Falsh erase")

    def _flash_write(self, chip_id, region, file_name):
        with open(file_name, 'rb') as fd:
            file_size = os.path.getsize(file_name)
            file_data = fd.read(USBC001001Def.FLASH_WRITE_PAGE_SIZE)
            write_addr = region.APP_START_ADDR

            while file_data:
                if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], write_addr):
                    raise Usbc001001Exception(
                        "FLad function gets wrong when doing flash writing")
                if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], array('B', file_data)):
                    raise Usbc001001Exception(
                        "FLwd function gets wrong when doing flash writing")

                write_addr += len(file_data)
                file_data = fd.read(USBC001001Def.FLASH_WRITE_PAGE_SIZE)

                # Progress information printing
                if 0 == ((write_addr - region.APP_START_ADDR) % USBC001001Def.FIRMWARE_DIV_SIZE):
                    print('Flash written: %d %%' % (USBC001001Def.FLOAT_TO_PERCENT *
                                                    (write_addr - region.APP_START_ADDR) / file_size))

            # updata header
            if 'Success' != hi_functions.FLem(self.tps6598x[chip_id], region.HEADER_ADDR, 1):
                raise Usbc001001Exception("FLem function checks header wrong")

            if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], region.HEADER_ADDR):
                raise Usbc001001Exception("FLad function checks header wrong")
            if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], self._int_2_byte_array(region.APP_START_ADDR)):
                raise Usbc001001Exception("FLwd function checks header wrong")

            # write again for insurance
            if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], region.HEADER_ADDR):
                raise Usbc001001Exception("FLad function checks header wrong")
            if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], self._int_2_byte_array(region.APP_START_ADDR)):
                raise Usbc001001Exception("FLwd function checks header wrong")

            # set app offset with 0, in address=hearder_addr + 0x1000 - 4
            if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], region.HEADER_ADDR + USBC001001Def.HEADER_OFFSET):
                raise Usbc001001Exception("FLad sets offset fail")
            if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], USBC001001Def.FLWD_OFFSET_CONFIG_ARRAY):
                raise Usbc001001Exception("FLwd sets offset fail")

    def _flash_verify(self, chip_id, region):
        '''Check write flash success or not'''
        app_addr = hi_functions.FLrr(self.tps6598x[chip_id], region.NUMBER)
        if 0 != hi_functions.FLvy(self.tps6598x[chip_id], app_addr):
            raise Usbc001001Exception("Flash verify fail")

    def _chip_reset(self, chip_id):

        self._GAID(chip_id)

    def read_all_registers(self, chip_id):
        '''
        USBC001001 read TPS6598x chip all registers informations.

        Args:
            chip_id:     string, ["XA", "XB"].

        Returns:
            string, str, information of all register.

        Examples:
            register_info = usbc001001.read_all_registers('XA')\r\n
            print(register_info)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID

        info = ''
        sorted_list = sorted(
            register_definitions.REGS_LIST, key=lambda x: x.addr)
        for reg in sorted_list:
            reg.read(self.tps6598x[chip_id])
            info += str(reg.show())

        return info

    def read_register_by_address(self, chip_id, register_address):
        '''
        USBC001001 read TPS6598x chip register information by address.

        Args:
            chip_id:             string, ["XA", "XB"].
            register_address:    int,    address range as follow:\r\n
                                            0x00, 0x01, 0x03, 0x05, 0x06, 0x0F, 0x14, 0x15, 0x16, 0x17,
                                            0x1A, 0x20, 0x28, 0x29, 0x2D, 0x2F, 0x30, 0x31, 0x32, 0x33,
                                            0x34, 0x35, 0x36, 0x37, 0x38, 0x3F, 0x40, 0x47, 0x48, 0x49,
                                            0x4A, 0x4E, 0x4F, 0x50, 0x51, 0x52, 0x57, 0x58, 0x59, 0x5B,
                                            0x5C, 0x5D, 0x5F, 0x60, 0x61, 0x68, 0x69, 0x6E, 0x70, 0x72,
                                            0x7C, 0x7D, 0x7E, 0x7F

        Returns:
            string, str, information of all register.

        Examples:
            register_info = usbc001001.read_register_by_address('XA', 0x03)\r\n
            print(register_info)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID

        register = register_definitions.registerByAddr(register_address)
        register.read(self.tps6598x[chip_id])
        return show(register)

    def read_register_by_name(self, chip_id, register_name):
        '''
        USBC001001 read TPS6598x chip register information by name.

        Args:
            chip_id:         string, ["XA", "XB"].
            register_name:   string,    name as follow:
                                        VID, DID, UID, MODE_REG, VERSION_REG,
                                        DEVICE_INFO_REG, CUSTUSE, BOOT_FLAGS, STATUS_REG,
                                        DATA_STATUS_REG,CONTROL_CONFIG_REG, SYS_CONFIG_REG, SYS_POWER,
                                        PWR_STATUS, PD_STATUS, ACTIVE_CONTRACT_PDO,ACTIVE_CONTRACT_RDO,
                                        SINK_REQUEST_RDO, TX_SOURCE_CAP, TX_SINK_CAP,RX_SOURCE_CAP,
                                        RX_SINK_CAP, AUTONEGOTIATE_SINK, INT_EVENT1, INT_MASK1,
                                        INT_EVENT2, INT_MASK2, GPIO_CONFIG_REG_1, GPIO_CONFIG_REG_2,
                                        GPIO_STATUS, TX_IDENTITY_REG, RX_IDENTITY_SOP_REG,
                                        RX_IDENTITY_SOPP_REG, RX_VDM_REG, RX_ATTN_REG, ALT_MODE_ENTRY,
                                        DATA_CONTROL_REG, DP_CAPABILITIES_REG, INTEL_CONFIG_REG,
                                        DP_STATUS_REG, INTEL_STATUS_REG, PWR_SWITCH, CCn_PINSTATE,
                                        SLEEP_CONFIG_REG, FW_STATE_HISTORY, FW_STATE_CONFIG, FW_STATE,
                                        FW_STATE_FOCUS, MUX_DEBUG_REG, TI_VID_STATUS_REG,
                                        USER_VID_CONFIG, USER_VID_STATUS_REG,
                                        RX_USER_SVID_ATTN_VDM_REG, RX_USER_SVID_OTHER_VDM_REG

        Returns:
            string, str, information of all register.

        Examples:
            register_info = usbc001001.read_register_by_name('XA', 'VID')\r\n
            print(register_info)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID

        register = register_definitions.registerByName(register_name)
        register.read(self.tps6598x[chip_id])
        return show(register)

    def write_register_by_address(self, chip_id, register_address, field_name, value):
        '''
        USBC001001 write TPS6598x chip register information by address.

        Args:
            chip_id:            string, ["XA", "XB"].
            register_address:   int,    address range as follow:\r\n
                                            0x16, 0x17, 0x20, 0x28, 0x29, 0x32, 0x33, 0x37, 0x38, 0x47,
                                            0x4a, 0x50, 0x51, 0x52, 0x5c, 0x5d, 0x6e, 0x70, 0x72, 0x7c.

            field_name:         str,    register file name.
            value:              int,    field value

        Returns:
            None

        Raise:
            Usbc001001Exception: if register not support filed name will throw exception and raise what support

        Examples:
            usbc001001.write_register_by_address('XA', 0x28, "PortInfo", 0)

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(register_address, int)
        assert isinstance(field_name, basestring)
        assert isinstance(value, int)

        register = register_definitions.registerByAddr(register_address)
        field_list = [field.name for field in register.fields]
        if field_name not in field_list:
            raise Usbc001001Exception(
                'field name \'{}\' not in {}'.format(field_name, field_list))

        register.read(self.tps6598x[chip_id])
        register.fieldByName(field_name).value = value
        register.write(self.tps6598x[chip_id])

    def flash_programmer(self, chip_id, region_name, firmware_name):
        '''
        USBC001001 burning TPS6598x chip.

        Args:
            region_name:     string,    ['region0', 'region1'], in TI's definition, TPS6598x firmware
                                        have two regions and save in different flash memory.
            firmware_name:   string,    file name with full dir.

        Returns:
            string, str, burning time. eg.'time: 76.33 s'.

        Examples:
            used_time = usbc001001.flash_programme('XA', region0', '/home/test_region0.bin')\r\n
            print used_time\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(region_name, basestring)
        assert region_name in [
            USBC001001Def.REGION0_NAME, USBC001001Def.REGION1_NAME]

        if region_name == USBC001001Def.REGION0_NAME:
            region = REGION0
        else:
            region = REGION1

        time_start = time.time()
        self._is_file_valid(firmware_name)
        self._flash_erase(chip_id, region)
        self._flash_write(chip_id, region, firmware_name)
        self._flash_verify(chip_id, region)
        self._chip_reset(chip_id)
        return 'time: %s s' % (time.time() - time_start)

    def write_register_by_name(self, chip_id, register_name, field_name, value):
        '''
        USBC001001 write TPS6598x chip register information by name.

        Args:
            chip_id:        string, ["XA", "XB"].
            register_name:  str,    name range as follow:\r\n
                                            INT_MASK1, INT_MASK2, SYS_POWER, SYS_CONFIG_REG, CONTROL_CONFIG_REG,
                                            TX_SOURCE_CAP, TX_SINK_CAP, AUTONEGOTIATE_SINK, ALT_MODE_ENTRY,
                                            TX_IDENTITY_REG, USER_VID_CONFIG, DATA_CONTROL_REG, DP_CAPABILITIES_REG,
                                            INTEL_CONFIG_REG, GPIO_CONFIG_REG_1, GPIO_CONFIG_REG_2, MUX_DEBUG_REG,
                                            SLEEP_CONFIG_REG, GPIO_STATUS, FW_STATE_CONFIG.

            field_name:     str,    register file name.
            value:          int,    field value

        Returns:
            None

        Raise:
            Usbc001001Exception: if register not support filed name will throw exception and raise what support

        Examples:
            usbc001001.write_register_by_name(
                'XA', "SYS_CONFIG_REG", "PortInfo", 0)

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(register_name, basestring)
        assert isinstance(field_name, basestring)
        assert isinstance(value, int)

        register = register_definitions.registerByName(register_name)
        field_list = [field.name for field in register.fields]
        if field_name not in field_list:
            raise Usbc001001Exception(
                'field name \'{}\' not in {}'.format(field_name, field_list))

        register.read(self.tps6598x[chip_id])
        register.fieldByName(field_name).value = value
        register.write(self.tps6598x[chip_id])

    def set_sink_capabilities(self, chip_id, PDO_number, operating_current, voltage, min_current, max_current):
        '''
        USBC001001 config TPS6598x chip sink capabilities register.

        Args:
            chip_id:             string, ["XA", "XB"].
            PDO_number:          string, [1~7],     PDO(Power Data object) which define Power Delivery
                                                        messages.We can set seven sink PDOs at most.
            operating_current:   string, [0~10230], unit mA, eg.3000.
            voltage:             string, [0~51150], unit mV, eg.5000.
            min_current:         string, [0~10230], unit mA, eg.900.
            max_current:         string, [0~10230], unit mA, eg.4000.

        Returns:
            None.

        Examples:
            usbc001001.set_sink_capabilities('XA', 1, 3000, 5000, 900, 4000)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(PDO_number, (int, basestring))
        assert isinstance(operating_current, (int, basestring))
        assert isinstance(voltage, (int, basestring))
        assert isinstance(min_current, (int, basestring))
        assert isinstance(max_current, (int, basestring))

        PDO_number = int(PDO_number)
        operating_current = int(operating_current)
        voltage = int(voltage)
        min_current = int(min_current)
        max_current = int(max_current)

        assert PDO_number >= USBC001001Def.PD0_MIN_NUMBER
        assert PDO_number <= USBC001001Def.PD0_MAX_NUMBER
        assert operating_current >= USBC001001Def.MIN_CURRENT
        assert operating_current <= USBC001001Def.MAX_CURRENT
        assert voltage >= USBC001001Def.MIN_VOLTAGE
        assert voltage <= USBC001001Def.MAX_VOLTAGE
        assert min_current >= USBC001001Def.MIN_CURRENT
        assert min_current <= USBC001001Def.MAX_CURRENT
        assert max_current >= USBC001001Def.MIN_CURRENT
        assert max_current <= USBC001001Def.MAX_CURRENT

        sink_voltage_field_name = 'PDO%d: Min Voltage or Power' % (PDO_number)
        sink_operating_current_field_name = 'PDO%d: Operating Current or Power' % (
            PDO_number)
        sink_min_current_field_name = 'PDO%d: MinCurrent or Power' % (
            PDO_number)
        sink_max_current_field_name = 'PDO%d: MaxCurrent or Power' % (
            PDO_number)

        register_definitions.TX_SINK_CAP.read(self.tps6598x[chip_id])
        register_definitions.TX_SINK_CAP.fieldByName(sink_voltage_field_name).value = \
            voltage // USBC001001Def.VOLTAGE_COEFFICIENT
        register_definitions.TX_SINK_CAP.fieldByName(sink_operating_current_field_name).value = \
            operating_current // USBC001001Def.CURRENT_COEFFICIENT
        register_definitions.TX_SINK_CAP.fieldByName(sink_min_current_field_name).value = \
            min_current // USBC001001Def.CURRENT_COEFFICIENT
        register_definitions.TX_SINK_CAP.fieldByName(sink_max_current_field_name).value = \
            max_current // USBC001001Def.CURRENT_COEFFICIENT
        register_definitions.TX_SINK_CAP.write(self.tps6598x[chip_id])

    def set_source_capabilities(self, chip_id, PDO_number, source_switch, voltage, max_current, peak_current='None'):
        '''
        USBC001001 config TPS6598x chip source capabilities register.

        Args:
            chip_id:         string, ["XA", "XB"].
            PDO_number:      int, [1~7],     PDO(Power Data object) which define Power Delivery.
                                                    messages.We can set seven sink PDOs at most.
            source_switch:   string, ['PP_5V', 'PP_HV', 'PP_HVE'], eg.'PP_HVE'.
                                                    'PP_5V'   Internal 5 Volt power path, only support PDO1;
                                                    'PP_HV'   Internal high voltage power path;
                                                    'PP_HVE'  External high voltage power path.
            voltage:         int, [0~51150], set source voltage, unit is mV. eg.5000
            max_current:     int, [0~10230], set max capabilities current, unit is mA. eg.1000
            peak_current:    string, ['100%', '130%', '150%', '200%', 'None'], default is None.
                                                    support power path peak current percentage.
                                                    '100%'  PeakCurrentType_100PercentIOC
                                                    '130%'  PeakCurrentType_150_110_PercentIOC
                                                    '150%'  PeakCurrentType_200_125_PercentIOC
                                                    '200%'  PeakCurrentType_200_150_PercentIOC
                                                    'None'  uesing default config

        Returns:
            None.

        Raise:
            Usbc001001Exception, source switch not found.

        Examples:
            usbc001001.set_source_capabilities('XA', 1, 'PP_HVE', 5000, 4000)
            usbc001001.set_source_capabilities(
                'XA', 1, 'PP_HVE', 5000, 4000, "150%")

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(PDO_number, (int, basestring))
        assert isinstance(voltage, (int, basestring))
        assert isinstance(max_current, (int, basestring))
        assert isinstance(peak_current, basestring)

        PDO_number = int(PDO_number)
        voltage = int(voltage)
        max_current = int(max_current)

        assert PDO_number >= USBC001001Def.PD0_MIN_NUMBER
        assert PDO_number <= USBC001001Def.PD0_MAX_NUMBER
        assert voltage >= USBC001001Def.MIN_VOLTAGE
        assert voltage <= USBC001001Def.MAX_VOLTAGE
        assert max_current >= USBC001001Def.MIN_CURRENT
        assert max_current <= USBC001001Def.MAX_CURRENT
        assert peak_current == 'None' or peak_current in USBC001001Def.PEAK_CURRENT_MAP

        if PDO_number == 1:
            if source_switch not in USBC001001Def.PDO1_SWITCH:
                raise Usbc001001Exception("source switch not found in PD01")
        else:
            if source_switch not in USBC001001Def.PDOn_SWITCH:
                raise Usbc001001Exception("source switch not found in PD0n")

        source_current_field_name = 'PDO%d: MaxCurrent or Power' % (PDO_number)
        source_voltage_field_name = 'PDO%d: Min Voltage or Power' % (
            PDO_number)
        source_switch_field_name = 'PP Switch for PDO%d' % (PDO_number)
        source_max_percentage_field_name = 'PDO%d: Max Voltage' % (PDO_number)

        if PDO_number == 1:
            source_switch_value = USBC001001Def.PDO1_SWITCH[source_switch]
        else:
            source_switch_value = USBC001001Def.PDOn_SWITCH[source_switch]

        register_definitions.TX_SOURCE_CAP.read(self.tps6598x[chip_id])
        register_definitions.TX_SOURCE_CAP.fieldByName(source_voltage_field_name).value = \
            voltage // USBC001001Def.VOLTAGE_COEFFICIENT
        register_definitions.TX_SOURCE_CAP.fieldByName(source_current_field_name).value = \
            max_current // USBC001001Def.CURRENT_COEFFICIENT
        register_definitions.TX_SOURCE_CAP.fieldByName(
            source_switch_field_name).value = source_switch_value

        if not peak_current == 'None':
            register_definitions.TX_SOURCE_CAP.fieldByName(source_max_percentage_field_name).value = \
                USBC001001Def.PEAK_CURRENT_MAP[peak_current]
        register_definitions.TX_SOURCE_CAP.write(self.tps6598x[chip_id])

    def read_all_adc(self, chip_id):
        '''
        USBC001001 read TPS6598x chip all ADC value

        Args:
            chip_id:     string, ["XA", "XB"].

        Returns:
            string, str, ADC value informations string.

        Examples:
            rd_value = usbc001001.read_all_adc('XA')\r\n
            print(rd_value)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        return_str = ''
        for channel in hi_functions.ADC.channels:
            result = hi_functions.ADCs(self.tps6598x[chip_id], channel)
            return_str = return_str + \
                'channel:%-5sname:%-20svalue:%s\r\n' % (
                    channel.channel, channel.name, result)
        return return_str

    def read_adc_by_name(self, chip_id, channel_name):
        '''
        USBC001001 read TPS6598x ADC informations by channel name

        Args:
            chip_id:         string,   ["XA", "XB"].
            channel_name:    string,   ['BRICKID_RFU', 'CC1_BY2', 'CC1_BY5', 'CC2_BY2', 'CC2_BY5',
                                        'GPIO_0', 'GPIO_1', 'GPIO_10 (BUSPOWER_Z)', 'GPIO_2', 'GPIO_3',
                                        'GPIO_4', 'GPIO_5', 'GPIO_5_RAW', 'GPIO_6', 'GPIO_7', 'GPIO_8',
                                        'I2CADDR', 'IN_3P3V', 'I_CC', 'I_PP_5V0', 'I_PP_EXT', 'I_PP_HV',
                                        'OUT_3P3V', 'PP_5V0', 'PP_CABLE', 'PP_HV', 'SENSEP',
                                        'V1P8_A', 'V1P8_D', 'V3P3', 'VBUS','THERMAL_SENSE'],
                                        range as follow:
                                        'BRICKID_RFU', 'CC1_BY2', 'CC1_BY5', 'CC2_BY2', 'CC2_BY5',
                                        'GPIO_0', 'GPIO_1', 'GPIO_10 (BUSPOWER_Z)', 'GPIO_2', 'GPIO_3',
                                        'GPIO_4', 'GPIO_5', 'GPIO_5_RAW', 'GPIO_6', 'GPIO_7', 'GPIO_8',
                                        'I2CADDR', 'IN_3P3V', 'I_CC', 'I_PP_5V0', 'I_PP_EXT', 'I_PP_HV',
                                        'OUT_3P3V', 'PP_5V0', 'PP_CABLE', 'PP_HV', 'SENSEP',
                                        'V1P8_A', 'V1P8_D', 'V3P3', 'VBUS','THERMAL_SENSE'
                                        eg.'GPIO_0'

        Returns:
            string, str, ADC value informations string.

        Examples:
            rd_value = usbc001001.read_adc_by_name('XA', 'PP_5V0')\r\n
            print(rd_value)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(channel_name, basestring)
        assert channel_name in ADC_NAME_LIST

        channel = hi_functions.ADC.channelByName(channel_name)
        result = hi_functions.ADCs(self.tps6598x[chip_id], channel)
        return 'channel:%-5sname:%-20svalue:%s\r\n' % (channel.channel, channel.name, result)

    def set_firmware_region_pointer(self, chip_id, region_name):
        '''
        USBC001001 TPS6598x chip reboot with firmware in region0 or region1.

        Args:
            chip_id:         string,  ["XA", "XB"].
            region_name:     string,  ['region0', 'region1'], in TI's definition, TPS6598x firmware have two
                                      regions and save in different flash memory.

        Returns:
            None.

        Raise:
            Usbc001001Exception, register write fail.

        Examples:
            usbc001001.set_firmware_region_pointer('XA', region1')\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert region_name in [
            USBC001001Def.REGION0_NAME, USBC001001Def.REGION1_NAME]

        if region_name == USBC001001Def.REGION0_NAME:
            new_pointer = REGION0.APP_START_ADDR
        else:
            new_pointer = REGION1.APP_START_ADDR

        header_addr = REGION0.HEADER_ADDR

        # change write start address
        if 'Success' != hi_functions.FLem(self.tps6598x[chip_id], header_addr, 1):
            raise Usbc001001Exception("change write start address fail")

        # write new pointer twice
        if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], header_addr):
            raise Usbc001001Exception("FLad function write new pointer fail")
        if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], self._int_2_byte_array(new_pointer)):
            raise Usbc001001Exception("FLwd function write new pointer fail")
        if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], header_addr):
            raise Usbc001001Exception("FLad function write new pointer fail")
        if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], self._int_2_byte_array(new_pointer)):
            raise Usbc001001Exception("FLwd function write new pointer fail")

        # set app offset with 0, in address=hearder_addr + 0x1000 - 4
        if 'Success' != hi_functions.FLad(self.tps6598x[chip_id], header_addr + USBC001001Def.HEADER_OFFSET):
            raise Usbc001001Exception("FLad function set app offset fail")
        if 'Success' != hi_functions.FLwd(self.tps6598x[chip_id], USBC001001Def.FLWD_OFFSET_CONFIG_ARRAY):
            raise Usbc001001Exception("FLwd function set app offset fail")

        # reset
        self._GAID(chip_id)

    def reset(self, chip_id):
        '''
        USBC001001 board cold restart TPS6598x function.

        Args:
            chip_id:         string,  ["XA", "XB"].

        Returns:
            None.

        Examples:
            usbc001001.reset('XA')\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        self._GAID(chip_id)

    def set_power_switch_config(self, chip_id, power_port, state):
        '''
        USBC001001 configurate TPS6598x power switch state as output, input or output_input etc.

        Args:
            chip_id:     string,  ["XA", "XB"].
            power_port:  string, ['PP_5V','PP_HV', 'PP_HVE'], eg.'PP_HVE';
                                  'PP_5V'   Internal 5 Volt power path;
                                  'PP_HV'   Internal high voltage power path;
                                  'PP_HVE'  External high voltage power path.
            state:       string, ['SwitchConfig_DISABLED',  'SwitchConfig_AS_OUT',
                                 'SwitchConfig_AS_IN',     'SwitchConfig_AS_IN_AFTER_SYSRDY',
                                 'SwitchConfig_AS_OUT_IN', 'SwitchConfig_AS_OUT_IN_AFTER_SYSRDY'],
                                 eg.'SwitchConfig_DISABLED'

        Examples:
            usbc001001.set_power_switch_config('XA', 'PP_HV', 'SwitchConfig_DISABLED')\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(power_port, basestring)
        assert isinstance(state, basestring)

        assert power_port in PORT_MAP
        assert state in STATE_MAP

        port = PORT_MAP[power_port]
        state_value = STATE_MAP[state]

        register_definitions.SYS_CONFIG_REG.read(self.tps6598x[chip_id])
        register_definitions.SYS_CONFIG_REG.fieldByName(
            port).value = state_value
        register_definitions.SYS_CONFIG_REG.write(self.tps6598x[chip_id])

    def set_pin_dir(self, chip_id, gpio_number, state):
        '''
        USBC001001 configurate TPS6598x gpio direction state to input or output.

        Args:
            gpio_number:     int, [0~17], TPS6598x pin index.
            state:           string, input or output. GPIO pin direction.

        Examples:
            usbc001001.set_pin_dir('XA', 3, 'output')\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(gpio_number, int)
        assert isinstance(state, basestring)
        assert gpio_number >= USBC001001Def.GPIO_MIN_NUM
        assert gpio_number <= USBC001001Def.GPIO_MAX_NUM
        assert state in [USBC001001Def.INPUT_DIR, USBC001001Def.OUTPUT_DIR]

        if state == USBC001001Def.INPUT_DIR:
            result = hi_functions.GPie(self.tps6598x[chip_id], gpio_number)
        else:
            result = hi_functions.GPoe(self.tps6598x[chip_id], gpio_number)

        return result

    def set_pin(self, chip_id, gpio_number, level):
        '''
        USBC001001 set TPS6598x output gpio output level to high or low.

        Args:
            chip_id:         string,  ["XA", "XB"].
            gpio_number:     int, [0~17], TPS6598x pin index.
            level:           int, [0, 1], 0 is low level, 1 is high level

        Returns:
            string, str, set result info.

        Examples:
             usbc001001.set_pin('XA', 3, 1)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(gpio_number, int)
        assert isinstance(level, int)

        assert gpio_number >= USBC001001Def.GPIO_MIN_NUM
        assert gpio_number <= USBC001001Def.GPIO_MAX_NUM
        assert level in [USBC001001Def.LOW_LEVEL, USBC001001Def.HIGH_LEVEL]

        if level == USBC001001Def.HIGH_LEVEL:
            result = hi_functions.GPsh(self.tps6598x[chip_id], gpio_number)
        else:
            result = hi_functions.GPsl(self.tps6598x[chip_id], gpio_number)

        return result

    def get_pin(self, chip_id, gpio_number):
        '''
        USBC001001 get TPS6598x gpio pin level.

        Args:
            chip_id:         string,  ["XA", "XB"].
            gpio_number:     int, [0~17],  TPS6598x pin index.

        Returns:
            int, [0, 1], 0 is low level, 1 is high level.

        Examples:
            result = usbc001001.get_pin('XA', 3)\r\n
            print(result)\r\n

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert isinstance(gpio_number, int)
        assert gpio_number >= USBC001001Def.GPIO_MIN_NUM
        assert gpio_number <= USBC001001Def.GPIO_MAX_NUM

        register_definitions.GPIO_STATUS.read(self.tps6598x[chip_id])

        field_name = 'GPIO {}'.format(gpio_number)
        gpio_field = filter(lambda x: field_name in x.name,
                            register_definitions.GPIO_STATUS.fields)[0]
        return gpio_field.value

    def change_source_pdo_count(self, chip_id, count):
        '''
        USBC001001 change source pdo count.

        Args:
            chip_id:   string,  ["XA", "XB"].
            count:     int, [1~7], source pdo count.

        Examples:
            usbc001001.change_source_pdo_count('XA', 1)

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert count >= USBC001001Def.NUM_PDOs_MIN and count <= USBC001001Def.NUM_PDOs_MAX

        register_definitions.TX_SOURCE_CAP.read(self.tps6598x[chip_id])
        register_definitions.TX_SOURCE_CAP.fieldByName(
            USBC001001Def.NUM_PDOs_file_name).value = count
        register_definitions.TX_SOURCE_CAP.write(self.tps6598x[chip_id])

    def change_pullup(self, chip_id, pullup_mode):
        '''
        USBC001001 change pullup.

        Args:
            chip_id:         string, ["XA", "XB"].
            pullup_mode:     string, ['STD', '1.5A', '3.0A', 'NONE'],  source pdo count.

        Examples:
            usbc001001.change_pullup('XA', 'STD')

        '''
        assert chip_id in USBC001001Def.USBC_ID
        assert pullup_mode in TypeCCurrent_map_list

        pullup_mode_file_name = 'TypeCCurrent'

        register_definitions.SYS_CONFIG_REG.read(self.tps6598x[chip_id])
        register_definitions.SYS_CONFIG_REG.fieldByName(pullup_mode_file_name).value = \
            TypeCCurrent_map_list[pullup_mode]
        register_definitions.SYS_CONFIG_REG.write(self.tps6598x[chip_id])

    def enable_emarker(self, chip_id):
        '''
        USBC001001 Enable emarker for providing VBus Current > 3A.

        Args:
            chip_id:         string, ["XA", "XB"].

        Returns:
            string, "done", api execution successful.

        Examples:
            usbc001001.enable_emarker("XA")
        '''
        assert chip_id in USBC001001Def.USBC_ID
        type_value = register_definitions.ReceptacleType_list.index(
            "UsbReceptacle_TETH_FULL_TypeC_Plug")
        vbus_current_value = register_definitions.VBUS_CurrentCap_List.index(
            "5 A")
        self.write_register_by_address(
            chip_id, register_definitions.SYS_CONFIG_REG.addr, "ReceptacleType", type_value)
        self.write_register_by_address(
            chip_id, register_definitions.TX_IDENTITY_REG.addr, "Num Valid SOP Prime IDOs", 4)
        self.write_register_by_address(
            chip_id, register_definitions.TX_IDENTITY_REG.addr, "VBUS Through Cable", True)
        self.write_register_by_address(chip_id, register_definitions.TX_IDENTITY_REG.addr,
                                       "VBUS Current Capability", vbus_current_value)
        return 'done'

    def disable_emarker(self, chip_id):
        '''
        USBC001001 Disable emarker for providing VBus Current <= 3A.

        Args:
            chip_id:         string, ["XA", "XB"].

        Returns:
            string, "done", api execution successful.

        Examples:
            usbc001001.disable_emarker("XA")
        '''
        assert chip_id in USBC001001Def.USBC_ID
        type_value = register_definitions.ReceptacleType_list.index(
            "UsbReceptacle_STD_FULL_TypeC_Receptacle")
        vbus_current_value = register_definitions.VBUS_CurrentCap_List.index(
            "1.5 A")
        self.write_register_by_address(
            chip_id, register_definitions.SYS_CONFIG_REG.addr, "ReceptacleType", type_value)
        self.write_register_by_address(
            chip_id, register_definitions.TX_IDENTITY_REG.addr, "Num Valid SOP Prime IDOs", 0)
        self.write_register_by_address(
            chip_id, register_definitions.TX_IDENTITY_REG.addr, "VBUS Through Cable", False)
        self.write_register_by_address(chip_id, register_definitions.TX_IDENTITY_REG.addr,
                                       "VBUS Current Capability", vbus_current_value)
        return 'done'