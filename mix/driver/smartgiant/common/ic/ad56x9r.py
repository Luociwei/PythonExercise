# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'ZiCheng.Huang@SmartGiant'
__version__ = '0.1'


class AD56X9RDef:
    '''
    AD56X9R definitions of internal registers and some const variable.
    '''
    REG_SIZE = 256
    REGISTER_WRITE_TO_INPUT_REG = 0x00
    REGISTER_UPDATE_DAC_REG = 0x10
    REGISTER_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x20
    REGISTER_WRITE_AND_UPDATE_DAC_CHAN = 0x30
    REGISTER_POWER_UP_OR_DOWN = 0x40
    REGISTER_LOAD_CLEAR_CODE_REG = 0x50
    REGISTER_LDAC_SETUP = 0x60
    REGISTER_RESET = 0x70
    REGISTER_INTERNAL_REFERENCE_REG = 0x80
    REGISTER_MULTIPLE_BYTE_MODE_REG = 0x90
    ALL_CHANNEL = 0xFF
    DAC_OUTPUT_ZERO = 0x0000
    ENABLE_LDAC = "enable"
    DISABLE_LDAC = "disable"

    AD5669R_RESOLUTION = 16
    AD5629R_RESOLUTION = 12

    CHANNEL_LIST_DEF = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x0f]

    MODE_LIST_DEF = {"normal": 0x00, "1kohm_gnd": 0x01, "100kohm_gnd": 0x02, "high_z": 0x03}


class AD56X9RException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s' % (err_str)

    def __str__(self):
        return self.err_reason


class AD56X9R(object):
    '''
    AD56X9R is a base class which provide all function to access AD56X9R DAC. AD56X9R devices are low power,
    octal, 12-/16-bit, buffered voltage-output DACs. All devices are guaranteed monotonic by design. Note that
    if i2c_bus not given, i2c bus emulator will be created for unit test.

    ClassType = DAC

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    instance(I2C)/None,  created using I2CBus, which is used to access AD56X9R internal register.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD56X9R.

    Example for AD5669R channel 0 output voltage 1000 mV, internal reference voltage 2500 mV.

    Examples:
        i2c_bus = I2CBus('/dev/MIX_I2C_0')
        ad5669r = AD5669R(0x54, i2c_bus, 'internal', 2500)
        ad5669r.output_volt_dc(0, 1000)

    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=2500.0):
        # 7-bit slave address. The two LSBs are variable
        assert isinstance(dev_addr, int) and (dev_addr & (~0x03)) == 0x54
        assert isinstance(mvref, (float, int))
        assert mvref > 0.0
        self.dev_addr = dev_addr
        if not i2c_bus:
            self.i2c_bus = I2CBusEmulator('ad56x9r_emulator', AD56X9RDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus
        self.mvref = float(mvref)
        self.resolution = AD56X9RDef.AD5669R_RESOLUTION
        self.ref_mode = "extern"

    def _read_register(self, register):
        '''
        Read register value from AD56X9R device. This is a private function. User should not call this function.

        Args:
            register:     int, [0~0x9F], register address from which read data.

        Returns:
            list, [value], data read from register address.

        Examples:
            ad56x9r.read_register(0x10)

        '''
        assert isinstance(register, int) and register >= 0x00 and register <= 0x9F
        return self.i2c_bus.write_and_read(self.dev_addr, [register], 2)

    def _write_register(self, register, data):
        '''
        Write data to specific register of AD56X9R. This is a private function. User should not call this function.

        Args:
            register:    int, [0~0x9F], specific register to write data.
            data:        int, [0~0xFFFF], high byte data to write.

        Examples:
            ad56x9r.write_register(0x10, 0x20, 0x30)

        '''
        assert isinstance(register, int) and register >= 0x00 and register <= 0x9F
        assert isinstance(data, int) and data >= 0x00 and data <= 0xFFFF
        high_byte = (data >> 8) & 0xFF
        low_byte = data & 0xFF
        self.i2c_bus.write(self.dev_addr, [register, high_byte, low_byte])

    def reset(self):
        '''
        Reset DAC to the power-on reset code. This is important to know the state of powering up.

        Examples:
            ad56x9r.reset()

        '''
        # when power on reset code, the AD5629R/AD5669R DAC output powers up to 0V
        register = AD56X9RDef.REGISTER_RESET
        data = AD56X9RDef.DAC_OUTPUT_ZERO
        self._write_register(register, data)

    def select_work_mode(self, channel=0xFF, mode="normal"):
        '''
        Select AD56X9R work mode, which contain four separate modes of operation. Default working in normal mode.
        Work modes shown as below.

        +------------------------------+------------------------------+
        |   mode                       |   Operation Mode             |
        +==============================+==============================+
        |   "normal"  "NORMAL"         |   Normal operation           |
        +------------------------------+------------------------------+
        |  "1kohm_gnd" "1KOHM_GND"     |  1 kohm pulldown to GND      |
        +------------------------------+------------------------------+
        |  "100kohm_gnd" "100KOHM_GND" | 100 kohm pulldown to GND     |
        +------------------------------+------------------------------+
        |   "high_z" "HIGH_Z"          |  Three-state, high impedance |
        +------------------------------+------------------------------+

        Args:
            channel: int, [0, 1, 2, 3, 4, 5, 6, 7, 0xff], channel index to set work mode. 0xff mean both channel.
            mode:    string, ["normal", "1kohm_gnd", "100kohm_gnd", "high_z"],
                             dac output work mode, defualt is normal mode.

        Examples:
            ad56x9r.select_work_mode(0xff, 0x00)

        '''
        # DB5-DB4
        assert channel in [0, 1, 2, 3, 4, 5, 6, 7, 0xFF]
        assert mode in AD56X9RDef.MODE_LIST_DEF.keys()
        register = AD56X9RDef.REGISTER_POWER_UP_OR_DOWN
        if channel == 0xFF:
            low_byte = 0xFF
        else:
            low_byte = 0x01 << channel
        data = (AD56X9RDef.MODE_LIST_DEF[mode.lower()] << 8) | low_byte
        self._write_register(register, data)

    def set_ldac_pin(self, channel, control_mode):
        '''
        AD56X9R configure ldac pin enable. DAC output will be update controlled by
        the ldac pin. Ohterwise.

        Args:
            channel:  int, [0, 1, 2, 3, 4, 5, 6, 7, 0xff], channel index to enable ldac pin, 0xff mean all channel.

        Examples:
            ad56x9r.set_ldac_pin_enable(7)

        '''
        assert channel in [0, 1, 2, 3, 4, 5, 6, 7, 0xFF]
        assert control_mode in ["enable", "disable", "ENABLE", "DISABLE"]
        register = AD56X9RDef.REGISTER_LDAC_SETUP
        rd_data = self._read_register(register)
        data_high_byte = 0x00
        if control_mode.lower() == "enable":
            if channel == 0xff:
                data_low_byte = rd_data[1] | 0xff
            else:
                data_low_byte = rd_data[1] | (0x01 << channel)
        else:
            if channel == 0xff:
                data_low_byte = rd_data[1] & 0x00
            else:
                data_low_byte = rd_data[1] & (~(0x01 << channel))

        data_low_byte = data_low_byte & 0xff
        data = (data_high_byte << 8) | data_low_byte
        self._write_register(register, data)

    def _volt_to_code(self, volt):
        '''
        AD56X9R voltage value transform for code

        Args:
            volt:    float, unit mV, DAC desired output voltage.

        Returns:
            int, value, DAC register value which define DAC output voltage.

        Examples:
            ad56x9r.volt_to_code(1000)

        '''
        assert isinstance(volt, (int, float)) and volt >= 0.0
        code = volt if self.ref_mode == "extern" else volt / 2
        code = int(code * (0x1 << self.resolution) / self.mvref)
        if code >= (1 << self.resolution):
            code = (1 << self.resolution) - 1

        code = code << (16 - self.resolution) & 0xffff
        return code

    def output_volt_dc(self, channel, volt):
        '''
        Set specific dac channel to output voltage. volt shall between 0-2x of mvref.

        Args:
            channel:  int, [0, 1, 2, 3, 4, 5, 6, 7, 0xff], channel index to enable ldac pin, 0xff mean all channel.
            volt:     float/int, unit mV, DAC output voltage.

        Examples:
            ad56x9r.output_volt_dc(8, 1000)

        '''
        assert channel in [0, 1, 2, 3, 4, 5, 6, 7, 0xFF]
        assert isinstance(volt, (int, float))
        assert volt >= 0.0
        code = self._volt_to_code(volt)
        if channel == 0xff:
            channel = 8
        register = AD56X9RDef.REGISTER_WRITE_AND_UPDATE_DAC_CHAN | AD56X9RDef.CHANNEL_LIST_DEF[channel]
        return self._write_register(register, code)

    def reference(self, ref_mode):
        '''
        Set the DAC select reference value, when set up the reference value, only LSB vaild

        Args:
            ref_mode:    string, ["extern", "internal", "EXTERN", "INTERNAL"],  set the reference value of "internal"
                                                                                or "extern"

        Returns:
            None

        Examples:
            ad56x9r.reference("internal")

        '''
        assert ref_mode in ["extern", "internal", "EXTERN", "INTERNAL"]
        self.ref_mode = ref_mode.lower()
        # Set up internal REF register, 0x01 means choose internal, 0x00 means extern
        register = AD56X9RDef.REGISTER_INTERNAL_REFERENCE_REG
        data_high_byte = 0x00
        ref_mode_select = {"extern": 0x00, "internal": 0x01}
        data_low_byte = ref_mode_select[self.ref_mode]
        data = (data_high_byte << 8) | data_low_byte
        self._write_register(register, data)

    def initialization(self):
        '''
        Initialize the DAC, first reset the DAC, set the reference value, disable the ldac, select the DAC
        channel work mode

        Examples:
            ad56x9r.initialization()

        '''
        self.reset()
        self.reference(self.ref_mode)
        self.set_ldac_pin(AD56X9RDef.ALL_CHANNEL, AD56X9RDef.DISABLE_LDAC)
        self.select_work_mode(AD56X9RDef.ALL_CHANNEL, 'normal')


class AD5629R(AD56X9R):
    '''
    AD5629R is a low power, octal 12-bit, buffered voltage-output DAC. If i2c_bus not given, i2c bus emulator
    will be created for unit test.

    ClassType = DAC

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    Instance(I2C)/None,  created using I2CBus, which is used to access AD5629R internal register.
        ref_mode:   string, ["extern", "internal"], default "extern",  reference mode of AD5629R.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD5629R.

    '''

    def __init__(self, dev_addr, i2c_bus=None,
                 ref_mode="extern", mvref=2500.0):
        super(AD5629R, self).__init__(dev_addr, i2c_bus, mvref)
        self.resolution = AD56X9RDef.AD5629R_RESOLUTION
        self.ref_mode = ref_mode


class AD5669R(AD56X9R):
    '''
    AD5669R is a low power, octal 16-bit, buffered voltage-output DAC, if i2c_bus not given, i2c bus emulator
    will be created for unit test.

    ClassType = DAC

    Args:
        dev_addr:   int,                 bit i2c device address.
        i2c_bus:    Instance(I2C)/None,  created using I2CBus, which is used to access AD5669R internal register.
        ref_mode:   string, ["extern", "internal"], default "extern",  reference mode of AD5669R.
        mvref:      float/int, unit mV, default 2500.0, the reference voltage of AD5669R.

    '''

    def __init__(self, dev_addr, i2c_bus=None,
                 ref_mode="extern", mvref=2500.0):
        super(AD5669R, self).__init__(dev_addr, i2c_bus, mvref)
        self.resolution = AD56X9RDef.AD5669R_RESOLUTION
        self.ref_mode = ref_mode
