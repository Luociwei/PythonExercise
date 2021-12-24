# -*- coding: UTF-8 -*-
import struct
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_wct001_sg_r import MIXWCT001001SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.ic.ads1119 import ADS1119
from mix.driver.smartgiant.common.ic.mp8859 import MP8859
from mix.driver.core.ic.cat24cxx import CAT24C32


__author__ = 'Weiping.Xuan@SmartGiant'
__version__ = '0.2'

OUTPUT_GEARS = {
    'inductance': {'L1': 0x01, 'L2': 0X02, 'L3': 0X04, 'L4': 0X08},
    'capacitance': {'C1': 0x01, 'C2': 0x02, 'C3': 0x04, 'C4': 0x08, 'C5': 0x10, 'C6': 0x20, 'C7': 0x40}
}

CAT9555_IO = {'ADC_RST_L_IO': 0, 'CAP_P_CTL_1_IO': 1, 'CAP_P_CTL_2_IO': 2, 'CAP_P_CTL_3_IO': 3, 'CAP_P_CTL_4_IO': 4,
              'CAP_P_CTL_5_IO': 5, 'CAP_P_CTL_6_IO': 6, 'CAP_P_CTL_7_IO': 7, 'EN_PP5V_FET_DRIVER_IO': 8,
              'VRAIL_DISCHARGE_EN_IO': 9, 'Reserved_IO': 9, 'EN_PP_VRAIL_IO': 10, 'ADC_DRDY_L_IO': 11,
              'RLY_CTRL_1_IO': 12, 'CAP_P_CTL_8_IO': 12, 'RLY_CTRL_2_IO': 13, 'CAP_P_CTL_9_IO': 13,
              'RLY_CTRL_3_IO': 14, 'CAP_P_CTL_10_IO': 14, 'RLY_CTRL_4_IO': 15, 'CAP_P_CTL_0_IO': 15
              }

magma_range_table = {
    'VOLTOUT': 0,
    'READ_VOLTOUT': 1,
    "READ_CURREN_5V": 2,
    "READ_CURREN_12V": 3,
    "READ_CURREN_20V": 4
}


class MagmaDef:
    WCT001_REG_SIZE = 65536
    CAT9555_ADDR = 0x20
    ADS1119_ADDR = 0X40
    MAX6642_ADDR = 0X48
    MP8859_ADDR = 0X62
    CAT24C32_ADDR = 0X50
    EN_PP_FET_DRIVER = 8
    EN_PP_VRAIL = 10
    H_LEVEL = 1
    L_LEVEL = 0
    SIGNAL_TIME = 0xFFFFFFFF
    SPS = 125000000
    VPP_SCALE = 0.5
    OFFSET_VOLT = 0
    PROTECT_MODE = ["hiccup", "latch-off"]
    PWM_MODE = ["auto", "FPWM"]
    LINE_DROP_COMP = [0, 150, 300, 500]
    MAXIMUM_POWER = 30000000
    ADC_DRDY = 11
    ADC_RST = 0
    VOLT_CHANNEL = 3
    CURRENT_CHANNEL = 5
    SAMPLE_RATE = [20, 90, 330, 1000]
    MEASURE_TIME = 2000
    FRQE_CHANNEL = ['P', 'N']
    TIME_OUT = 6
    DIR = ['input', 'output']
    SENSER_CURRENT_GAIN = 50
    I_VRAIL_CURRENT_GAIN = 50 * 0.01
    PPVAIL_VOLTAGE_GAIN = 0.0991
    INDUCTOR_CALIBRATION_ADDRESS = 0xAF
    INDUCTOR_CALIBRATION_COUNT = 5
    ADS1119_CHANNEL_MIN = 0
    ADS1119_CHANNEL_MAX = 7
    PWM_FREQUENCY_MIN = 80000
    PWM_FREQUENCY_MAX = 500000
    PWM_DUTY_MIN = 0.05
    PWM_DUTY_MAX = 0.5
    CURRENT_OUTPUT_MIN = 0
    CURRENT_OUTPUT_MAX = 6350
    VOLTAGE_OUTPUT_MIN = 0
    VOLTAGE_OUTPUT_MAX = 20470
    MP8859_VOLTAGE_CHANNEL = 0
    MP8859_CURRENT_CHANNEL = 0
    CAP_P_CTL_L_MASK = 0x7f
    CAP_P_CTL_H_MASK = 0x07
    CAP_P_CTL_L_OFFSET = 1
    CAP_P_CTL_H_OFFSET = 4
    RLY_CTRL_MASK = 0x0f
    RLY_CTRL_OFFSET = 4
    DEFAULT_CURRENT = 5000
    BIT_STATUS_LEN = 10
    MAX6642_CHANNEL = ['local', 'remote']


class MagmaException(Exception):
    def __init__(self, err_str):
        self._err_reason = err_str

    def __str__(self):
        return self._err_reason


class Magma(SGModuleDriver):
    '''
    The Magma is Wireless charging module, it has voltage and current output function and
    also has the function of voltage and current measurement, pwm output, io set, frequency function.

    Args:
        i2c:              instance(I2C)/None,  If not given, I2CBus emulator will be created.
        ipcore:           instance(MIXWCT001), MIXWCT001 IP driver instance, provide signalsource, signalmeter_p
                                                 and signalmeter_n function.

    Examples:
        i2c = I2C('/dev/i2c-0')
        axi4_bus = AXI4LiteBus('dev/MIX_WCT001_001_SG_R_0', 65536)
        ipcore = MIXWCT001001SGR(axi4_bus, use_signalmeter_p=True, use_signalmeter_n=True, use_signalsource=True)
        magma = Magma(i2c,ipcore)
    '''
    compatible = ['GQQ-03X7-5-010', 'GQQ-03X7-5-001']

    rpc_public_api = ['set_vrail_output_voltage', 'set_vrail_output_current_limit', 'mp8859_config',
                      'pwm_output', 'set_output_gears', 'read_vrail_voltage', 'read_vrail_current',
                      'read_ads1119_volt', 'set_adc_sampling_rate', 'read_frequency', 'io_set_dir',
                      'io_get_dir', 'io_set', 'io_get', 'read_max6642_temperature', 'reset',
                      'inductor_calibration_read', 'pwm_disable', 'mp8859_enable', 'mp8859_disable',
                      'mp8859_init', 'max6642_write_high_limit', 'max6642_read_high_limit',
                      'max6642_read_state'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c=None, ipcore=None, range_table=magma_range_table):

        self.ipcore = ipcore
        if (ipcore is not None and i2c is not None):
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, MagmaDef.WCT001_REG_SIZE)
                self.ipcore = MIXWCT001001SGR(axi4_bus, use_signalmeter_p=True,
                                              use_signalmeter_n=True, use_signalsource=True)
            self.signalsource = self.ipcore.signalsource
            self.signalmeter_p = self.ipcore.signalmeter_p
            self.signalmeter_n = self.ipcore.signalmeter_n
            self.cat9555 = CAT9555(MagmaDef.CAT9555_ADDR, i2c)
            self.ads1119 = ADS1119(MagmaDef.ADS1119_ADDR, i2c)
            self.sensor = MAX6642(MagmaDef.MAX6642_ADDR, i2c)
            self.mp8859 = MP8859(MagmaDef.MP8859_ADDR, i2c)
            self.eeprom = CAT24C32(MagmaDef.CAT24C32_ADDR, i2c)
        else:
            raise MagmaException('__init__ error! Please check the parameters!')
        self.signalmeter = {'P': self.signalmeter_p, 'N': self.signalmeter_n}
        super(Magma, self).__init__(eeprom=self.eeprom, temperature_device=self.sensor, range_table=range_table)

    def post_power_on_init(self, timeout=MagmaDef.TIME_OUT):
        '''
        Init Magma module to a know harware state.

        This function will set cat9555 io direction to output and set ADC and DAC.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=MagmaDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        Returns:
            string, "done", api execution successful.
        '''
        start_time = time.time()
        while True:
            try:
                self.signalsource.close()
                self.cat9555.set_ports([0x00, 0x00])
                self.cat9555.set_pins_dir([0, 0x08])
                self._adc_init()
                self.mp8859_init()
                self.load_calibration()
                return 'done'
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise MagmaException("Timeout: {}".format(e.message))

    def mp8859_enable(self):
        '''
        Enable mp8859.
        '''
        self.mp8859.enable()
        return 'done'

    def mp8859_disable(self):
        '''
        Disable mp8859.
        '''
        self.mp8859.disable()
        return 'done'

    def mp8859_init(self):
        '''
        mp8859 init.
        Examples:
            mp8859_init()
        '''
        self.cat9555.set_pin(MagmaDef.EN_PP_VRAIL, MagmaDef.L_LEVEL)
        time.sleep(0.2)
        self.cat9555.set_pin(MagmaDef.EN_PP_VRAIL, MagmaDef.H_LEVEL)
        self.mp8859.init()
        self.mp8859.config(MagmaDef.PROTECT_MODE[1], MagmaDef.PWM_MODE[0], MagmaDef.LINE_DROP_COMP[1])
        self.set_vrail_output_current_limit(MagmaDef.DEFAULT_CURRENT)
        self.mp8859_disable()
        return 'done'

    def set_vrail_output_voltage(self, voltage):
        '''
        mp8859 output voltage, range 0 V ~ 20 V.

        Args:
            voltage:    int, [0~20470], unit mV.

        Examples:
            set_vrail_output_voltage(5000)

        '''
        assert isinstance(voltage, (int, float))
        assert MagmaDef.VOLTAGE_OUTPUT_MIN <= voltage and voltage <= MagmaDef.VOLTAGE_OUTPUT_MAX

        self.mp8859.output_volt_dc(MagmaDef.MP8859_VOLTAGE_CHANNEL, voltage)
        current = MagmaDef.MAXIMUM_POWER / voltage
        if current > MagmaDef.CURRENT_OUTPUT_MAX:
            current = MagmaDef.CURRENT_OUTPUT_MAX
        self.mp8859.output_current_dc(MagmaDef.MP8859_CURRENT_CHANNEL, current)
        return "done"

    def set_vrail_output_current_limit(self, current):
        '''
        MP8859 output max current limit

        Args:
            current:    int, [0~6350], output max current, unit mA.

        Examples:
           set_vrail_output_current_limit(3000)

        '''
        assert isinstance(current, (int, float))
        assert MagmaDef.CURRENT_OUTPUT_MIN <= current and current <= MagmaDef.CURRENT_OUTPUT_MAX

        self.mp8859.output_current_dc(MagmaDef.MP8859_CURRENT_CHANNEL, current)
        return "done"

    def mp8859_config(self, protect_mode, pwm_mode, line_drop_comp):
        '''
        config MP8859.

        Args:
            protect_mode:   string, ["hiccup", "latch-off"], over-current and over-voltage protection mode.
            pwm_mode:       string, ["auto", "FPWM"], pwm work mode, auto PFM/PWM or force PWM mode.
            line_drop_comp: int,    [0, 150, 300, 500], output voltage compensation vs. the load feature, unit is mV

        Examples:
            mp8859_onfig("hiccup", "auto", 150)
        '''
        assert protect_mode in MagmaDef.PROTECT_MODE
        assert pwm_mode in MagmaDef.PWM_MODE
        assert line_drop_comp in MagmaDef.LINE_DROP_COMP

        self.mp8859.config(protect_mode, pwm_mode, line_drop_comp)
        return "done"

    def pwm_disable(self):
        '''
        Disable pwm output function

        Examples:
            pwm_disable()
        '''

        self.signalsource.close()
        return "done"

    def pwm_output(self, frequency, duty):
        '''
        pwm output function

        Args:
            frequency:  int, [80000~500000]output signal frequency.
            duty:       float, [0.05~0.5], duty of square

        Examples:
            pwm_output(80000, 0.5)

        '''
        assert MagmaDef.PWM_FREQUENCY_MIN <= frequency <= MagmaDef.PWM_FREQUENCY_MAX
        assert MagmaDef.PWM_DUTY_MIN <= duty <= MagmaDef.PWM_DUTY_MAX

        self.signalsource.close()
        self.signalsource.open()
        self.signalsource.set_signal_type('square')
        self.signalsource.set_signal_time(MagmaDef.SIGNAL_TIME)
        self.signalsource.set_swg_paramter(MagmaDef.SPS, frequency, MagmaDef.VPP_SCALE, duty, MagmaDef.OFFSET_VOLT)
        self.signalsource.output_signal()
        return "done"

    def set_output_gears(self, inductance, capacitance):
        '''
        select inductance and capacitance channel.

        Args:
            inductance:    string, ['L1', 'L2', 'L3', 'L4'], Corresponding to the four inductance channels.
            capacitance:   string, ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'], Corresponding to the seven
                                                                               capacitor channels.
        Examples:
            set_output_gears('L1', 'C1')
        '''
        assert inductance in OUTPUT_GEARS['inductance'].keys()
        assert capacitance in OUTPUT_GEARS['capacitance'].keys()

        pins_dir = self.cat9555.get_pins_dir()
        pins_dir_L = pins_dir[0]
        pins_dir_L &= ~(MagmaDef.CAP_P_CTL_L_MASK << MagmaDef.CAP_P_CTL_L_OFFSET)
        pins_dir_H = pins_dir[1]
        pins_dir_H &= ~(MagmaDef.RLY_CTRL_MASK << MagmaDef.RLY_CTRL_OFFSET)
        self.cat9555.set_pins_dir([pins_dir_L, pins_dir_H])

        pins_level = self.cat9555.get_ports()
        pins_level_L = pins_level[0]
        pins_level_L &= ~(MagmaDef.CAP_P_CTL_L_MASK << MagmaDef.CAP_P_CTL_L_OFFSET)
        pins_level_L |= (OUTPUT_GEARS['capacitance'][capacitance] << MagmaDef.CAP_P_CTL_L_OFFSET)
        pins_level_H = pins_level[1]
        pins_level_H &= ~(MagmaDef.RLY_CTRL_MASK << MagmaDef.RLY_CTRL_OFFSET)
        pins_level_H |= (OUTPUT_GEARS['inductance'][inductance] << MagmaDef.RLY_CTRL_OFFSET)
        self.cat9555.set_ports([pins_level_L, pins_level_H])
        return "done"

    def _adc_init(self):

        self.cat9555.set_pin_dir(MagmaDef.ADC_DRDY, 'input')
        self.cat9555.set_pin_dir(MagmaDef.ADC_RST, 'output')
        self.cat9555.set_pin(MagmaDef.ADC_RST, MagmaDef.H_LEVEL)
        self.ads1119.init()

    def read_vrail_voltage(self, mode='ppvrail'):
        '''
        read voltage function.

        Args:
            mode:   string, ['ppvrail','adc'],'ppvrail':read the vlotage from ppvrail.
                                              'adc':read the vlotage from ads1119.

        Returns:
            float, voltage, unit is mV.

        Examples:
            voltage = read_vrail_voltage('ppvrail')
        '''

        assert mode in ['ppvrail', 'adc']
        voltage = self.ads1119.read_volt(MagmaDef.VOLT_CHANNEL)
        if mode == 'ppvrail':
            voltage = float(voltage / MagmaDef.PPVAIL_VOLTAGE_GAIN)
        return voltage

    def read_vrail_current(self, mode='senseR'):
        '''
        read current function.

        Args:
            mode:   string, ['senseR','adc','i_vrail'].'senseR':read the vlotage from senseR.
                                             'adc':read the vlotage from ads1119.

        Returns:
            float, current, unit is mA.

        Examples:
            current = read_vrail_current('ppvrail')
        '''

        assert mode in ['senseR', 'adc', 'i_vrail']
        current = self.ads1119.read_volt(MagmaDef.CURRENT_CHANNEL)
        if mode == 'senseR':
            current = float(current / MagmaDef.SENSER_CURRENT_GAIN)
        if mode == 'i_vrail':
            current = float(current / MagmaDef.I_VRAIL_CURRENT_GAIN)
        return current

    def read_ads1119_volt(self, channel):
        '''
        ADS1119 read voltage function.

        Args:
            channel:    int, [0~7],
                                    0 : AIN0-AIN1
                                    1 : AIN2-AIN3
                                    2 : AIN1-AIN2
                                    3 : AIN0-AGND
                                    4 : AIN1-AGND
                                    5 : AIN2-AGND
                                    6 : AIN3-AGND
                                    7 : AINP and AINN shorted to AVDD / 2

        Returns:
            float, voltage, unit is mV.

        Examples:
            voltage = read_ads1119_volt(0)
            print(voltage)

        '''
        assert isinstance(channel, int)
        assert MagmaDef.ADS1119_CHANNEL_MIN <= channel and channel <= MagmaDef.ADS1119_CHANNEL_MAX

        return self.ads1119.read_volt(channel)

    def set_adc_sampling_rate(self, rate):
        '''
        ADS1119 set sampling rate

        Args:
            rate:       int, [20,90,330,1000], unit SPS, sample rate value.

        Examples:
            set_adc_sampling_rate(90)

        '''
        assert isinstance(rate, int)
        assert rate in MagmaDef.SAMPLE_RATE

        self.ads1119.set_sampling_rate(rate)
        return "done"

    def read_frequency(self, channel):
        '''
        Measuring frequency function.
        Args:
            channel:       string, ['P', 'N'], frequency channel.

        Returns:
            int/float, value, unit Hz.

        Examples:
           frequency, duty = read_frequency('P')
        '''
        assert channel in MagmaDef.FRQE_CHANNEL

        self.signalmeter[channel].close()
        self.signalmeter[channel].open()
        self.signalmeter[channel].start_measure(MagmaDef.MEASURE_TIME, MagmaDef.SPS)
        frequency = self.signalmeter[channel].measure_frequency('LP')
        duty = self.signalmeter[channel].duty()
        return frequency, duty

    def read_max6642_temperature(self, channel, extended=False):
        '''
        MAX6642 read local or remote temperature, chose to read extended resolution.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            extended:   boolean, [True, False], enable or disable extended resolution.

        Returns:
            int/float, value, unit °C.

        Examples:
           temperature = read_max6642_temperature('local', False)
        '''
        channel = channel.lower()
        assert channel in ['local', 'remote']
        assert isinstance(extended, bool)

        return self.sensor.get_temperature(channel, extended)

    def io_set_dir(self, pin_name, pindir):
        '''
        Set io direction by pin name.

        Args:
            pin_name:     string, the pin name to set direction.
            pindir:       string, ['input', 'output'], pin direction.

        The beload is the pin name table of io_set/io_get/io_set_dir/io_get_dir parameters.

            +---------------+------------------------------------+-------------------+
            |     IO Type   |  pin_name                          |    pin number     |
            +===============+====================================+===================+
            |               |  ADC_RST_L_IO                      |        0          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_1_IO                    |        1          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_2_IO                    |        2          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_3_IO                    |        3          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_4_IO                    |        4          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_5_IO                    |        5          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_6_IO                    |        6          |
            |               +------------------------------------+-------------------+
            |               |  CAP_P_CTL_7_IO                    |        7          |
            |    CAT9555    +------------------------------------+-------------------+
            |               |  EN_PP5V_FET_DRIVER_IO             |        8          |
            |               +------------------------------------+-------------------+
            |               |  VRAIL_DISCHARGE_EN_IO/Reserved_IO |        9          |
            |               +------------------------------------+-------------------+
            |               |  EN_PP_VRAIL_IO                    |       10          |
            |               +------------------------------------+-------------------+
            |               |  ADC_DRDY_L_IO                     |       11          |
            |               +------------------------------------+-------------------+
            |               |  RLY_CTRL_1_IO/CAP_P_CTL_8_IO      |       12          |
            |               +------------------------------------+-------------------+
            |               |  RLY_CTRL_2_IO/CAP_P_CTL_9_IO      |       13          |
            |               +------------------------------------+-------------------+
            |               |  RLY_CTRL_3_IO/CAP_P_CTL_10_IO     |       14          |
            |               +------------------------------------+-------------------+
            |               |  RLY_CTRL_4_IO/CAP_P_CTL_0_IO      |       15          |
            |---------------+------------------------------------+-------------------+

        Returns:
            string, "done", api execution successful.

        Examples:
            io_set_dir('RLY_CTRL_4_IO', 'output')

        '''
        assert pin_name in CAT9555_IO.keys()
        assert pindir in MagmaDef.DIR

        self.cat9555.set_pin_dir(CAT9555_IO[pin_name], pindir)
        return 'done'

    def io_get_dir(self, pin_name):
        '''
        Get io direction by pin name.

        Args:
            pin_name:      string, the pin to get direction.

        Returns:
            string, ['input', 'output'], pin direction.

        Examples:
             direction = io_get_dir('RLY_CTRL_4_IO')
        '''
        assert pin_name in CAT9555_IO.keys()

        return self.cat9555.get_pin_dir(CAT9555_IO[pin_name])

    def io_set(self, pin_name, level):
        '''
        Set io level by pin name.

        Args:
            pin_name:     string, the pin of name to set level.
            level:        int, [0, 1], io output level.
        Returns:
            string, "done", api execution successful.

        Examples:
            io_set('RLY_CTRL_4_IO', 1)
        '''
        assert pin_name in CAT9555_IO.keys()
        assert level in [0, 1]

        self.cat9555.set_pin(CAT9555_IO[pin_name], level)
        return 'done'

    def io_get(self, pin_name):
        '''
        Get io level by pin name.

        Args:
            pin_name:     string, the pin to get input level.

        Returns:
            int, [0, 1], io input level.

        Examples:
            level = io_get('RLY_CTRL_4_IO')
        '''
        assert pin_name in CAT9555_IO.keys()

        return self.cat9555.get_pin(CAT9555_IO[pin_name])

    def inductor_calibration_read(self):
        '''
        read the inductor and CAP_P_CTL bits status in the eeprom.

        Returns:
            dict,{'bit_status':0b1001000,'L':26.4}
        bit_status meaning CAP_P_CTL7-CAP_P_CTL1 level.

        Examples:
            data = inductor_calibration_read()
            print(inductor_calibration_read)
        '''
        data = self.eeprom.read(MagmaDef.INDUCTOR_CALIBRATION_ADDRESS, MagmaDef.INDUCTOR_CALIBRATION_COUNT)
        s = struct.Struct('5B')
        pack_data = s.pack(*data)
        s = struct.Struct('1f1B')
        result = s.unpack(pack_data)
        return {'bit_status': '0b' + bin(result[1])[2:].zfill(7), 'L': result[0]}

    def max6642_write_high_limit(self, channel, limit):
        '''
        MAX6642 write local or remote high limit.
        The intended measuring range for the MAX6642 is 0 to +150 (Celsius).
        However, the limit is an 8 bit unsigned number and can be set between 0 and +255.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            limit:      int, [0~255], temperature limit.
        Returns:
            string, "done", api execution successful.

        Examples:
            max6642_write_high_limit('local', 120)
        '''
        assert channel in MagmaDef.MAX6642_CHANNEL
        assert isinstance(limit, int) and 0 <= limit <= 0xff

        self.sensor.write_high_limit(channel, limit)
        return "done"

    def max6642_read_high_limit(self, channel):
        '''
        MAX6642 read local or remote high limit.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
        Returns:
            int/float, value, unit °C.

        Examples:
            limit = max6642_read_high_limit('local')
            print(limit)
        '''
        assert channel in MagmaDef.MAX6642_CHANNEL

        return self.sensor.read_high_limit(channel)

    def max6642_read_state(self):
        '''
        MAX6642 read status byte.

        Returns:
            init

        Examples:
            max6642_read_state()
        '''
        return self.sensor.read_state()

    def get_driver_version(self):
        '''
        Get Magma driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
