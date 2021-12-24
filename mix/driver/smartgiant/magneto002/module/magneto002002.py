# -*- coding: utf-8 -*-
import math

from mix.driver.core.bus.uart_bus_emulator import UARTBusEmulator
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator

from mix.driver.smartgiant.common.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.ipcore.mix_pwm_sg_emulator import MIXPWMSG
from mix.driver.smartgiant.common.ic.ad5592r import AD5592R
from mix.driver.smartgiant.common.ic.ad5592r_emulator import AD5592REmulator
from mix.driver.smartgiant.common.ic.ad9833 import AD9833
from mix.driver.smartgiant.common.ic.ad9833_emulator import AD9833Emulator
from mix.driver.smartgiant.common.ic.led1642 import LED1642
from mix.driver.smartgiant.common.ic.led1642_emulator import LED1642Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


class MAGNETO002002Def:
    CAT9555_ADDR_0 = 0x20
    CAT9555_ADDR_1 = 0x21
    CAT9555_ADDR_2 = 0x22
    CAT9555_ADDR_3 = 0x23
    CAT9555_ADDR_4 = 0x24
    CAT9555_ADDR_5 = 0x25
    EEPROM_DEV_ADDR = 0x50

    DAC_MODE = 'DAC'
    ADC_MODE = 'ADC'
    CHANNEL_0 = 0
    CHANNEL_1 = 1
    CHANNEL_2 = 2
    CHANNEL_3 = 3
    CHANNEL_4 = 4
    CHANNEL_5 = 5
    CHANNEL_6 = 6
    CHANNEL_7 = 7
    MVREF = 2500
    ADC_GAIN = 2
    DAC_GAIN = 2
    DAC_VAL_MIN = 0
    DAC_VAL_MAX = 5000
    DAC_CHAN_COUNT = 4
    ADC_MEASURE_GAIN = 2
    ADC_MEASURE_CH = {
        'IN3': 7, 'IN4': 6, 'IN5': 5, 'IN6': 4,
        'IN7': 3, 'IN8': 2, 'IN9': 1, 'IN10': 0}

    PERCENTAHE_MIN = 0
    PERCENTAHE_MAX = 100
    GRAYSCALE_12 = 12
    GRAYSCALE_16 = 16
    PWM_CH_MIN = 1
    PWM_CH_MAX = 8
    CHIP_NUM_MIN = 0
    CHIP_NUM_MAX = 5
    PINS_OUTPUT = [0x00, 0x00]
    PINS_OUTPUT_HIGH = [0xff, 0xff]
    PINS_OUTPUT_LOW = [0x00, 0x00]

    LED_GRAYSCALE = 12
    PWM_GAIN = pow(2, LED_GRAYSCALE)
    LED_CH_MIN = 0
    LED_CH_MAX = 15
    DUTY_MIN = 0
    DUTY_MAX = 100
    LED_DUTY = 50
    LED_PULSE = 0xffffff
    LED_CHANNEL_COUNT = 16

    FREQ_MIN = 0
    FREQ_MAX = 25000000
    # fft analyzer
    SAMPLE_RATE = 192000
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)
    AUDIO_ANALYZER_VREF = 2 * math.sqrt(2) * 2000

    BIT71 = 71
    BIT72 = 72
    BIT73 = 73
    BIT74 = 74

    FREQ0_CH = 'FREQ0'
    FREQ1_CH = 'FREQ1'
    PHASE0_CH = 'PHASE0'
    PHASE1_CH = 'PHASE1'
    OUTPUT_MODE_SINE = 'sine'
    OUTPUT_MODE_TRIANGULAR = 'triangular'
    OUTPUT_MODE_SQUARE_DIV_2 = 'square_div_2'
    OUTPUT_MODE_SQUARE = 'square'

    UART_SIZE = 256
    SPI_SIZE = 256
    PWM_SIZE = 1024


magneto002002_calibration_info = {
    "DAC_0": {
        "level1": {"unit_index": 0, "limit": (100, "mV")},
        "level2": {"unit_index": 1, "limit": (500, "mV")},
        "level3": {"unit_index": 2, "limit": (1000, "mV")},
        "level4": {"unit_index": 3, "limit": (2000, "mV")},
        "level5": {"unit_index": 4, "limit": (3000, "mV")},
        "level6": {"unit_index": 5, "limit": (4000, "mV")},
        "level7": {"unit_index": 6, "limit": (5000, "mV")},
    },
    "DAC_1": {
        "level1": {"unit_index": 7, "limit": (100, "mV")},
        "level2": {"unit_index": 8, "limit": (500, "mV")},
        "level3": {"unit_index": 9, "limit": (1000, "mV")},
        "level4": {"unit_index": 10, "limit": (2000, "mV")},
        "level5": {"unit_index": 11, "limit": (3000, "mV")},
        "level6": {"unit_index": 12, "limit": (4000, "mV")},
        "level7": {"unit_index": 13, "limit": (5000, "mV")},
    },
    "ADC_4": {
        "level1": {"unit_index": 14, "limit": (100, "mV")},
        "level2": {"unit_index": 15, "limit": (500, "mV")},
        "level3": {"unit_index": 16, "limit": (1000, "mV")},
        "level4": {"unit_index": 17, "limit": (2000, "mV")},
        "level5": {"unit_index": 18, "limit": (3000, "mV")},
        "level6": {"unit_index": 19, "limit": (4000, "mV")},
        "level7": {"unit_index": 20, "limit": (5000, "mV")},
    },
    "ADC_5": {
        "level1": {"unit_index": 21, "limit": (100, "mV")},
        "level2": {"unit_index": 22, "limit": (500, "mV")},
        "level3": {"unit_index": 23, "limit": (1000, "mV")},
        "level4": {"unit_index": 24, "limit": (2000, "mV")},
        "level5": {"unit_index": 25, "limit": (3000, "mV")},
        "level6": {"unit_index": 26, "limit": (4000, "mV")},
        "level7": {"unit_index": 27, "limit": (5000, "mV")},
    },
    "ADC_6": {
        "level1": {"unit_index": 28, "limit": (100, "mV")},
        "level2": {"unit_index": 29, "limit": (500, "mV")},
        "level3": {"unit_index": 30, "limit": (1000, "mV")},
        "level4": {"unit_index": 31, "limit": (2000, "mV")},
        "level5": {"unit_index": 32, "limit": (3000, "mV")},
        "level6": {"unit_index": 33, "limit": (4000, "mV")},
        "level7": {"unit_index": 34, "limit": (5000, "mV")},
        "level8": {"unit_index": 35, "limit": (10000, "mV")},
    },
    "ADC_7": {
        "level1": {"unit_index": 36, "limit": (100, "mV")},
        "level2": {"unit_index": 37, "limit": (500, "mV")},
        "level3": {"unit_index": 38, "limit": (1000, "mV")},
        "level4": {"unit_index": 39, "limit": (2000, "mV")},
        "level5": {"unit_index": 40, "limit": (3000, "mV")},
        "level6": {"unit_index": 41, "limit": (4000, "mV")},
        "level7": {"unit_index": 42, "limit": (5000, "mV")},
        "level8": {"unit_index": 43, "limit": (10000, "mV")},
    }
}


magneto002002_range_table = {
    "DAC_0", 0,
    "DAC_1", 1,
    "DAC_4", 2,
    "DAC_5", 3,
    "DAC_6", 4,
    "DAC_7", 5
}


class MAGNETO002002Exception(Exception):
    pass


class MAGNETO002002(MIXBoard):
    '''
    MAGNETO002002 function class

    compatible = ['GQQ-MGO002002-000']

    Args:
        i2c_bus0:      instance(I2C)/None, i2c bus which is used to access CAT9555.
        led1642_bus:   instance(LED1642)/None, LED1642 bus which is used to access LED.
        pwm_gck_led:   instance(PWM)/None, PWM bus control.
        pwm_output:    instance(PWM)/None, PWM bus control.
        uart_rs485:    instance(UART)/None, UART bus control.
        ad5592r_spi:   instance(QSPI)/None, spi bus which is used to access ad5592r.
        ad9833_spi:    instance(QSPI)/None, spi bus which is used to access ad9833.
        analyzer:      instance(FFTAnalyzer)/None, ip core of FFTAnalyzer.
        gpio_state_pin:  instance(GPIO)/None, GPIO control, which is used to control input.
        pwm1_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm2_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm3_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm4_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm5_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm6_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm7_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        pwm8_en_pin:     instance(GPIO)/None, GPIO control, which is used to control input.
        signal_out_en:   instance(GPIO)/None, GPIO control, which is used to control output.
        iis_rx_en:       instance(GPIO)/None, GPIO control, which is used to control output.
        iis_rx_ovfl:     instance(GPIO)/None, GPIO control, which is used to control output.
        iis_rx_rst:      instance(GPIO)/None, GPIO control, which is used to control output.
    '''
    compatible = ['GQQ-MGO002002-000']

    rpc_public_api = ['module_init', 'io_set', 'io_get', 'io_set_dir',
                      'io_get_dir', 'get_ioexp_dev', 'ioexp_set', 'ioexp_get',
                      'ioexp_reset', 'dds_output', 'dds_close', 'read_volt',
                      'adc_measure_on', 'adc_measure_off', 'set_volt', 'reset_volt',
                      'pwm_output', 'pwm_close', 'led_pwm_output', 'led_pwm_close',
                      'led_on', 'led_off', 'led_on_all', 'led_off_all',
                      'led_grayscale_set', 'set_current_gain', 'set_current_range', 'fft_measure',
                      'uart_write', 'uart_read'] + MIXBoard.rpc_public_api

    def __init__(self, i2c_bus0=None, led1642_bus=None, pwm_gck_led=None, pwm_output=None, uart_rs485=None,
                 ad5592r_spi=None, ad9833_spi=None, analyzer=None, gpio_state_pin=None, pwm1_en_pin=None,
                 pwm2_en_pin=None, pwm3_en_pin=None, pwm4_en_pin=None, pwm5_en_pin=None,
                 pwm6_en_pin=None, pwm7_en_pin=None, pwm8_en_pin=None, signal_out_en=None,
                 iis_rx_en=None, iis_rx_ovfl=None, iis_rx_rst=None):

        if i2c_bus0:
            self.cat9555_0 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_0, i2c_bus0)
            self.cat9555_1 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_1, i2c_bus0)
            self.cat9555_2 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_2, i2c_bus0)
            self.cat9555_3 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_3, i2c_bus0)
            self.cat9555_4 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_4, i2c_bus0)
            self.cat9555_5 = CAT9555(MAGNETO002002Def.CAT9555_ADDR_5, i2c_bus0)
            self.eeprom = CAT24C32(MAGNETO002002Def.EEPROM_DEV_ADDR, i2c_bus0)

        else:
            self.cat9555_0 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_0, None, None)
            self.cat9555_1 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_1, None, None)
            self.cat9555_2 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_2, None, None)
            self.cat9555_3 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_3, None, None)
            self.cat9555_4 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_4, None, None)
            self.cat9555_5 = CAT9555Emulator(MAGNETO002002Def.CAT9555_ADDR_5, None, None)
            self.eeprom = EepromEmulator('eeprom_emulator')

        if ad5592r_spi:
            self.ad5592r = AD5592R(ad5592r_spi, MAGNETO002002Def.MVREF, 'internal', MAGNETO002002Def.ADC_GAIN,
                                   MAGNETO002002Def.DAC_GAIN)
        else:
            self.ad5592r = AD5592REmulator('ad5592r')

        self.dds_dev = AD9833(ad9833_spi) if ad9833_spi else AD9833Emulator()

        self.uart_rs485 = uart_rs485 or UARTBusEmulator('uart_emulator', MAGNETO002002Def.UART_SIZE)
        self.pwm_led = pwm_gck_led if pwm_gck_led else MIXPWMSG('pwm_gck_led', MAGNETO002002Def.PWM_SIZE)
        self.pwm_dev = pwm_output if pwm_output else MIXPWMSG('pwm_output', MAGNETO002002Def.PWM_SIZE)
        if isinstance(analyzer, basestring):
            analyzer = MIXFftAnalyzerSG(analyzer)
        elif analyzer:
            self.analyzer = analyzer
        else:
            self.analyzer = MIXFftAnalyzerSGEmulator('mix_fftanalyzer_sg_emulator')
        self.gpio_map = {
            "PWM1_EN_PIN": pwm1_en_pin or GPIOEmulator("PWM1_EN_PIN"),
            "PWM2_EN_PIN": pwm2_en_pin or GPIOEmulator("PWM2_EN_PIN"),
            "PWM3_EN_PIN": pwm3_en_pin or GPIOEmulator("PWM3_EN_PIN"),
            "PWM4_EN_PIN": pwm4_en_pin or GPIOEmulator("PWM4_EN_PIN"),
            "PWM5_EN_PIN": pwm5_en_pin or GPIOEmulator("PWM5_EN_PIN"),
            "PWM6_EN_PIN": pwm6_en_pin or GPIOEmulator("PWM6_EN_PIN"),
            "PWM7_EN_PIN": pwm7_en_pin or GPIOEmulator("PWM7_EN_PIN"),
            "PWM8_EN_PIN": pwm8_en_pin or GPIOEmulator("PWM8_EN_PIN"),
            "SIGNAL_OUT_EN": signal_out_en or GPIOEmulator("SIGNAL_OUT_EN"),
            "GPIO_STATE_PIN": gpio_state_pin or GPIOEmulator("GPIO_STATE_PIN"),
            "IIS_RX_EN": iis_rx_en or GPIOEmulator("IIS_RX_EN"),
            "IIS_RX_OVFL": iis_rx_ovfl or GPIOEmulator("IIS_RX_OVFL"),
            "IIS_RX_RST": iis_rx_rst or GPIOEmulator("IIS_RX_RST")
        }
        if led1642_bus:
            self.led1642 = LED1642(led1642_bus, self.gpio_map['SIGNAL_OUT_EN'])
        else:
            self.led1642 = LED1642Emulator(None, None)

        super(MAGNETO002002, self).__init__(self.eeprom, None, cal_table=magneto002002_calibration_info,
                                            range_table=magneto002002_range_table)

    def module_init(self):
        '''
        Initialize gpio and chip.

        Returns:
            string, "done", api execution successful.

        Examples:
            Magneto003002.module_init()

        '''
        # initialize the calibration configure.
        self.load_calibration()

        # cat9555_0 and cat9555_1 are initialized as inputs.
        self.cat9555_0.set_pins_dir([0xFF, 0xFF])
        self.cat9555_1.set_pins_dir([0xFF, 0xFF])

        # cat9555_2/3/4/5 are initialized as output and output high level.
        self.cat9555_2.set_ports([0x00, 0x00])
        self.cat9555_2.set_pins_dir([0x00, 0x00])
        self.cat9555_3.set_ports([0x00, 0x00])
        self.cat9555_3.set_pins_dir([0x00, 0x00])
        self.cat9555_4.set_ports([0x00, 0x00])
        self.cat9555_4.set_pins_dir([0x00, 0x00])
        self.cat9555_5.set_ports([0x00, 0x00])
        self.cat9555_5.set_pins_dir([0x00, 0x00])

        # ad5592r channel 0-3 is config as DAC and channel 4-7 is config as ADC.
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_0, MAGNETO002002Def.DAC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_1, MAGNETO002002Def.DAC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_2, MAGNETO002002Def.DAC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_3, MAGNETO002002Def.DAC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_4, MAGNETO002002Def.ADC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_5, MAGNETO002002Def.ADC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_6, MAGNETO002002Def.ADC_MODE)
        self.ad5592r.channel_config(MAGNETO002002Def.CHANNEL_7, MAGNETO002002Def.ADC_MODE)

        self.io_set_dir('GPIO_STATE_PIN', 'input')
        self.io_set_dir('PWM1_EN_PIN', 'output')
        self.io_set_dir('PWM2_EN_PIN', 'output')
        self.io_set_dir('PWM3_EN_PIN', 'output')
        self.io_set_dir('PWM4_EN_PIN', 'output')
        self.io_set_dir('PWM5_EN_PIN', 'output')
        self.io_set_dir('PWM6_EN_PIN', 'output')
        self.io_set_dir('PWM7_EN_PIN', 'output')
        self.io_set_dir('PWM8_EN_PIN', 'output')
        self.io_set_dir('IIS_RX_EN', 'output')
        self.io_set_dir('IIS_RX_OVFL', 'output')
        self.io_set_dir('IIS_RX_RST', 'output')
        self.io_set('IIS_RX_EN', 1)
        self.io_set('IIS_RX_OVFL', 1)
        self.io_set('IIS_RX_RST', 1)
        self.dds_close()
        self.led_off_all()
        return "done"

    def io_set(self, pin_name, level):
        '''
        Set io level by pin name.

        Args:
            pin_name:     string, the pin of name to set level.
            level:        int, [0, 1], io output level.

            The beload is the pin name table of io_set/io_get/io_set_dir/io_get_dir parameters.

            +---------------+---------------------------+-------------------+
            |     IO Type   |  pin_name                 |    pin number     |
            +===============+===========================+===================+
            |               |  PWM1_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM2_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM3_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM4_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM5_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM6_EN_PIN              |        /          |
            |   External    +---------------------------+-------------------+
            |               |  PWM7_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  PWM8_EN_PIN              |        /          |
            |               +---------------------------+-------------------+
            |               |  GPIO_STATE_PIN           |        /          |
            |               +---------------------------+-------------------+
            |               |  UART_DIR_PIN             |        /          |
            |               +---------------------------+-------------------+
            |               |  IIS_RX_EN                |        /          |
            |               +---------------------------+-------------------+
            |               |                           |        /          |
            +---------------+---------------------------+-------------------+

        Returns:
            string, "done", api execution successful.

        '''
        assert pin_name in self.gpio_map
        assert level in [0, 1]
        self.gpio_map[pin_name].set_level(level)
        return "done"

    def io_get(self, pin_name):
        '''
        Get io level by pin name.

        Args:
            pin_name:    string, the pin to get input level.

        Returns:
            int, [0, 1], io input level.

        '''
        assert pin_name in self.gpio_map
        return self.gpio_map[pin_name].get_level()

    def io_set_dir(self, pin_name, pindir):
        '''
        Set io direction by pin name.

        Args:
            pin_name:     string, the pin name to set direction.
            pindir:       string, ['input', 'output'], pin direction.

        Returns:
            string, "done", api execution successful.

        '''
        assert pin_name in self.gpio_map
        assert pindir in ['input', 'output']
        self.gpio_map[pin_name].set_dir(pindir)
        return "done"

    def io_get_dir(self, pin_name):
        '''
        Get io direction by pin name.

        Args:
            pin_name:     string, the pin to get direction.

        Returns:
            string, ['input', 'output'], pin direction.

        '''
        assert pin_name in self.gpio_map
        return self.gpio_map[pin_name].get_dir()

    def get_ioexp_dev(self, io_num):
        '''
        Get extend io device and pin num.

        Args:
            io_num:    int, extend io pin.

        '''
        pin_list = divmod(io_num - 1, 16)
        device = eval('self.cat9555_' + str(pin_list[0]))
        pin_num = pin_list[1]
        return (device, pin_num)

    def ioexp_set(self, io_num, level):
        '''
        Set extend io level state by io number.

        Args:
            io_num:    int, extend io pin.
            level:     int, [0, 1], level state: 0|1.

        Returns:
            string, "done", api execution successful.

        Examples:
            io.ioexp_set(17, 1)

        '''
        assert io_num >= 0
        assert level >= 0 or level <= 1
        device, pin_id = self.get_ioexp_dev(io_num)
        device.set_pin_dir(pin_id, 'output')
        device.set_pin(pin_id, level)
        return "done"

    def ioexp_get(self, io_num):
        '''
        Get extend io level state by io number.

        Args:
            io_num:    int, extend io pin.

        Returns:
            string, str, bitx=y: x(1-16),y(0|1).

        Examples:
            io.ioexp_get(1)

        '''
        assert io_num >= 0
        device, pin_id = self.get_ioexp_dev(io_num)
        device.set_pin_dir(pin_id, 'input')
        return device.get_pin(pin_id)

    def ioexp_reset(self, chip_num, status):
        '''
        Reset io expander to ensure output level.

        Args:
            chip_num:    int, [0~5], chip id.
            status:      string, ['low', 'high'], the all pins to high level or low level.

        Returns:
            string, "done", api execution successful.

        Examples:
            io.ioexp_reset(2, 'low')

        '''
        assert chip_num >= MAGNETO002002Def.CHIP_NUM_MIN
        assert chip_num <= MAGNETO002002Def.CHIP_NUM_MAX
        assert status in ['low', 'high']

        device = eval('self.cat9555_' + str(chip_num))
        device.set_pins_dir(MAGNETO002002Def.PINS_OUTPUT)
        if status == 'low':
            device.set_ports(MAGNETO002002Def.PINS_OUTPUT_LOW)
        else:
            device.set_ports(MAGNETO002002Def.PINS_OUTPUT_HIGH)
        return "done"

    def dds_output(self, frequency, freq_ch='FREQ0', phase_ch='PHASE0', phase=0, output_mode='sine'):
        '''
        DDS Waveform generator function.

        Args:
            frequency:    int, frequency of out put wave.
            freq_ch:      string, ['FREQ0', 'FREQ1'], default 'FREQ0'.
            phase_ch:     string, ['PHASE0', 'PHASE0', 'PHASE1'], default 'PHASE0'.
            output_mode:  string, ['sine','square','square/2','triangular'], default 'sine'.

        Returns:
            boolean, [True, False].

        Examples:
            Magneto003002.frequency_output(1000)

        '''
        assert isinstance(frequency, int) and frequency > 0
        assert freq_ch in [MAGNETO002002Def.FREQ0_CH, MAGNETO002002Def.FREQ1_CH]
        assert phase_ch in [MAGNETO002002Def.PHASE0_CH, MAGNETO002002Def.PHASE1_CH]
        assert phase >= 0 and phase <= 2 * math.pi
        assert output_mode in [MAGNETO002002Def.OUTPUT_MODE_SINE, MAGNETO002002Def.OUTPUT_MODE_SQUARE]

        self.dds_dev.reset()
        self.dds_dev.output(freq_ch, frequency, phase_ch, phase, output_mode)

        return 'done'

    def dds_close(self):
        '''
        DDS Waveform generator close function.

        Returns:
            string, "done", api execution successful.

        Examples:
            Magneto003002.frequency_close()

        '''
        self.dds_dev.reset()
        return 'done'

    def read_volt(self, channel, sample_size=10):
        '''
        AD5592r function to read input voltage.

        Args:
            channel:        int, [4~7], channel id.
            sample_size:    int, (>=1), sample size for average.

        Returns:
            float, value, unit mV, adc voltage.

        Examples:
            ad5592r.read_volt(4)

        '''
        assert isinstance(channel, int)
        assert isinstance(sample_size, int)
        assert channel >= MAGNETO002002Def.CHANNEL_4
        assert channel <= MAGNETO002002Def.CHANNEL_7
        assert sample_size >= 1

        volt_list = [self.ad5592r.read_volt(channel) for _ in range(sample_size)]
        volt = sum(volt_list) / sample_size

        volt = self.calibrate('ADC_{}'.format(channel), volt)

        return volt

    def adc_measure_on(self, channel, sample_size=10):
        '''
        AD5592r function to read input voltage.

        Args:
            channel:        string, ['IN3'~'IN10'], channel id.
            sample_size:    int, (>=1), sample size for average.

        Returns:
            float, value, unit mV, adc voltage.

        Examples:
            ad5592r.adc_measure_on(IN10)

        '''
        assert isinstance(sample_size, int)
        assert channel in MAGNETO002002Def.ADC_MEASURE_CH
        assert sample_size >= 1

        self.ioexp_set(MAGNETO002002Def.BIT74, 1)
        bit = [MAGNETO002002Def.BIT73, MAGNETO002002Def.BIT72, MAGNETO002002Def.BIT71]
        value = []
        temp = bin(8 | MAGNETO002002Def.ADC_MEASURE_CH[channel])[-3:]
        for val in temp:
            value.append(int(val))

        for ch in zip(bit, value):
            self.ioexp_set(ch[0], ch[1])

        volt_list = [self.ad5592r.read_volt(MAGNETO002002Def.CHANNEL_6) for _ in range(sample_size)]
        volt = sum(volt_list) / sample_size

        volt = self.calibrate('ADC_{}'.format(MAGNETO002002Def.CHANNEL_6), volt)

        return volt * MAGNETO002002Def.ADC_MEASURE_GAIN

    def adc_measure_off(self):
        '''
        AD5592r turn off adc measure channel.

        Returns:
            string, "done", api execution successful.

        Examples:
            ad5592r.adc_measure_off().

        '''
        self.ioexp_set(MAGNETO002002Def.BIT74, 0)
        return 'done'

    def set_volt(self, channel, volt):
        '''
        AD5592R function to output dc voltage, 12bit dac

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, [0~5000], unit mV, output voltage value.

        Returns:
            string, "done", api execution successful.

        Examples:
            ad5592r.set_volt(0, 1000)

        '''
        assert isinstance(channel, int)
        assert isinstance(volt, (int, float))
        assert channel >= MAGNETO002002Def.CHANNEL_0
        assert channel <= MAGNETO002002Def.CHANNEL_3
        assert volt >= MAGNETO002002Def.DAC_VAL_MIN
        assert volt <= MAGNETO002002Def.DAC_VAL_MAX

        if channel <= 1:
            volt = self.calibrate('ADC_{}'.format(channel), volt)

        self.ad5592r.output_volt_dc(channel, volt)
        return 'done'

    def reset_volt(self):
        '''
        AD5592R function to reset output dc voltage to zero, 12bit dac.

        Returns:
            string, "done", api execution successful.

        Examples:
            ad5592r.reset_volt()
     .
        '''
        for channel in range(MAGNETO002002Def.DAC_CHAN_COUNT):
            self.ad5592r.output_volt_dc(channel, 0)
        return 'done'

    def pwm_output(self, channel, frequency, pulse, duty=50):
        '''
        PWM output function.

        Args:
            channel:      int, [1~8], channel id 1-8.
            frequency:    int, output PWM's frequency.
            duty:         int, [0~100], adjust signal's duty.
            pulse:        int, [0~0xffffff], unit PWM's pulse count.

        Returns:
            string, "done", api execution successful.

        Examples:
            pwm.pwm_output(10000, 1000, 50)

        '''
        assert isinstance(channel, int)
        assert isinstance(frequency, int)
        assert isinstance(pulse, int) and pulse > 0
        assert channel >= MAGNETO002002Def.PWM_CH_MIN
        assert channel <= MAGNETO002002Def.PWM_CH_MAX
        assert frequency >= MAGNETO002002Def.FREQ_MIN
        assert frequency <= MAGNETO002002Def.FREQ_MAX
        assert duty >= MAGNETO002002Def.DUTY_MIN
        assert duty <= MAGNETO002002Def.DUTY_MAX

        self.io_set('PWM{}_EN_PIN'.format(channel), 1)

        self.pwm_dev.set_enable(False)
        self.pwm_dev.set_frequency(frequency)
        self.pwm_dev.set_duty(duty)
        self.pwm_dev.set_pulse(pulse)
        self.pwm_dev.set_enable(True)
        return 'done'

    def pwm_close(self, channel):
        '''
        PWM close function.

        Args:
            channel:    int, [1~8], channel id 1-8.

        Returns:
            string, "done", api execution successful.

        Examples:
            pwm.pwm_close()
     .
        '''
        self.io_set('PWM{}_EN_PIN'.format(channel), 0)
        self.pwm_dev.set_enable(False)
        return 'done'

    def led_pwm_output(self, frequency):
        '''
        Led pwm waveform output.

        Args:
            frequency:   int, [1~50000000], unit Hz, frequency value.

        Returns:
            string, "done", api execution successful.

        Examples:
            led_pwm_output(500)
        .
        '''
        assert isinstance(frequency, int)
        assert frequency >= MAGNETO002002Def.FREQ_MIN
        assert frequency <= MAGNETO002002Def.FREQ_MAX

        self.pwm_led.set_enable(False)
        self.pwm_led.set_frequency(frequency * MAGNETO002002Def.PWM_GAIN)
        self.pwm_led.set_duty(MAGNETO002002Def.LED_DUTY)
        self.pwm_led.set_pulse(MAGNETO002002Def.LED_PULSE)
        self.pwm_led.set_enable(True)
        return 'done'

    def led_pwm_close(self):
        '''
        Led PWM close function.

        Returns:
            string, "done", api execution successful.

        Examples:
            Magneto003002.led_pwm_close()

        '''
        self.pwm_led.set_enable(False)
        return 'done'

    def led_on(self, channel, frequency, duty):
        '''
        Turn on the led in channel 0 - 15.

        Args:
            channel:       int, [0~15], led channel.
            frequency:     int, [0~500], frequency value.
            duty:          int, [0~100], value of duty cycle.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.led_on(0,500,50)
.
        '''
        assert isinstance(channel, int)
        assert isinstance(frequency, int)
        assert isinstance(duty, (float, int))
        assert frequency > 0
        assert channel >= MAGNETO002002Def.LED_CH_MIN
        assert channel <= MAGNETO002002Def.LED_CH_MAX
        assert duty >= MAGNETO002002Def.DUTY_MIN
        assert duty <= MAGNETO002002Def.DUTY_MAX

        self.led_pwm_output(frequency)
        self.led1642.set_channels_duty([(channel, duty)])
        return 'done'

    def led_off(self, channel):
        '''
        Turn off the led in channel 0~15.

        Args:
            channel:       int, [0~15], led channel.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.led_off(0)

        '''
        assert isinstance(channel, int)
        assert channel >= MAGNETO002002Def.LED_CH_MIN
        assert channel <= MAGNETO002002Def.LED_CH_MAX

        self.led_pwm_close()
        self.led1642.set_channels_duty([(channel, 0)])
        return 'done'

    def led_on_all(self, frequency, duty):
        '''
        Turn on all led.

        Args:
            frequency:     int, [0~500], frequency value.
            duty:          int, [0~100], value of duty cycle.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.led_on_all(500,50)

        '''
        assert isinstance(frequency, int)
        assert isinstance(duty, (float, int))
        assert frequency > 0
        assert duty >= MAGNETO002002Def.DUTY_MIN
        assert duty <= MAGNETO002002Def.DUTY_MAX

        self.led_pwm_output(frequency)

        led_list = [(channel, duty) for channel in range(MAGNETO002002Def.LED_CHANNEL_COUNT)]
        self.led1642.set_channels_duty(led_list)
        return 'done'

    def led_off_all(self):
        '''
        Turn off all led.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.led_off_all()

        '''
        self.led_pwm_close()

        led_list = [(channel, 0) for channel in range(MAGNETO002002Def.LED_CHANNEL_COUNT)]
        self.led1642.set_channels_duty(led_list)
        return 'done'

    def led_grayscale_set(self, bits_wide):
        '''
        Set grayscale bits wide to 12-bit or 14-bit.

        Args:
            bits_wide:    int, [12, 16], grayscale bits wide.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.led_grayscale_set(12)

        '''
        assert bits_wide in [MAGNETO002002Def.GRAYSCALE_12, MAGNETO002002Def.GRAYSCALE_16]

        self.led1642.set_grayscale(bits_wide)
        return 'done'

    def set_current_gain(self, percentage):
        '''
        Set current gain percentage

        Args:
            percentage:    float, [0~100.0], current gain percentage.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.set_current_gain(0.0)

        '''
        assert isinstance(percentage, (int, float))
        assert percentage >= MAGNETO002002Def.PERCENTAHE_MIN
        assert percentage <= MAGNETO002002Def.PERCENTAHE_MAX

        self.led1642.set_current_gain(percentage)
        return 'done'

    def set_current_range(self, level):
        '''
        Set current range level to 0 or 1.

        Args:
            level:    int, [0, 1], current range level.

        Returns:
            string, "done", api execution successful.

        Examples:
            led.set_current_range(1)
     .
        '''
        assert isinstance(level, int)
        assert level in [0, 1]

        self.led1642.set_current_range(level)
        return 'done'

    def fft_measure(self, bandwidth_hz, harmonic_num=None, decimation_type=0xff):
        '''
        fft measure signal's Vpp, RMS, THD+N, THD.

        Args:
            bandwidth_hz:    int, [24~95977], Measure signal's limit bandwidth, unit is Hz. The frequency of the
                                              signal should not be greater than half of the bandwidth.
            harmonic_num:    int, [1~10], Use for measuring signal's THD.
            decimation_type: int, [1~255], Decimation for FPGA to get datas. If decimation is 0xFF, FPGA will
                                           choose one suitable number.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value},
                  ict with vpp, freq, thd, thdn, rms.

        Examples:
            result = fft.fft_measure(20000, 5, 0xff)
            print result.frequency, result.vpp, result.thdn, result.thd, result.rms

        '''
        assert bandwidth_hz == 'auto' or isinstance(bandwidth_hz, int)
        assert isinstance(harmonic_num, int) or harmonic_num is None
        assert isinstance(decimation_type, int) and decimation_type > 0

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(MAGNETO002002Def.SAMPLE_RATE, decimation_type, bandwidth_hz, harmonic_num)
        self.analyzer.analyze()

        # calculate the actual vpp of HW by VREF
        vpp = self.analyzer.get_vpp() * MAGNETO002002Def.AUDIO_ANALYZER_VREF
        # vpp = RMS * 2 * sqrt(2)
        rms = vpp / MAGNETO002002Def.RMS_TO_VPP_RATIO

        result = dict()
        result["vpp"] = vpp
        result["freq"] = self.analyzer.get_frequency()
        result["thd"] = self.analyzer.get_thd()
        result["thdn"] = self.analyzer.get_thdn()
        result["rms"] = rms
        return result

    def uart_write(self, data, timeout_s=None):
        '''
        Uart write the bytes data to the port.

        Args:
            data:          list, the list data to be write.
            timeout_s:     float, set a write timeout value, default is blocking.

        Returns:
            string, "done", api execution successful.

        Examples:
            rs485.uart_write([1,2,3,4])

        '''
        assert isinstance(data, list) and len(data) > 0
        assert (timeout_s >= 0) or (timeout_s is None)
        self.uart_rs485.write_hex(data, timeout_s)
        return 'done'

    def uart_read(self, size, timeout_s=0):
        '''
        Uart write the bytes data to the port.

        Args:
            size:        int, number of bytes to read. Default size is 1 byte.
            timeout_s:   float, default 0, set a read timeout value.

        Returns:
            list, [value], list read from the port.

        Examples:
            message = rs485.uart_read(10, 3)
            print(message)

        '''
        assert (timeout_s >= 0) or (timeout_s is None)
        return self.uart_rs485.read_hex(size, timeout_s)
