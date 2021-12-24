# -*- coding: utf-8 -*-
import math
from mix.driver.core.bus.uart_bus_emulator import UARTBusEmulator
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator

from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.smartgiant.common.ic.ads1115 import ADS1115
from mix.driver.smartgiant.common.ic.ad9833 import AD9833
from mix.driver.smartgiant.common.ic.led1642 import LED1642
from mix.driver.smartgiant.common.ic.led1642_emulator import LED1642Emulator
from mix.driver.smartgiant.common.ic.ad9833_emulator import AD9833Emulator
from mix.driver.smartgiant.common.ic.mcp4725_emulator import MCP4725Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ic.ads1115_emulator import ADS1115Emulator
from mix.driver.smartgiant.common.ipcore.mix_pwm_sg_emulator import MIXPWMSG
from mix.driver.smartgiant.common.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


class MAGNETO003002Def:
    CAT9555_INPUT_DEV_ADDR = 0x20
    CAT9555_OUTPUT_DEV_ADDR = 0x21
    EEPROM_DEV_ADDR = 0x50
    ADS1115_DEV_ADDR = 0x48
    MCP4725_ELOAD_DEV_ADDR = 0x60
    MCP4725_SPK_DEV_ADDR = 0x61

    MCP4725_MVREF = 5000
    ADC_CHANNEL = 4
    DAC_VAL_MIN = 0
    DAC_VAL_MAX = 5000
    FREQ_MIN = 0
    FREQ_MAX = 25000000
    DUTY_MIN = 0
    DUTY_MAX = 100
    LED_CH_MIN = 0
    LED_CH_MAX = 15

    LED_DUTY = 50
    LED_PULSE = 0xffffff
    LED_CHANNEL_COUNT = 16
    GRAYSCALE_12 = 12
    GRAYSCALE_16 = 16
    PWM_GAIN = pow(2, GRAYSCALE_12)
    PERCENTAHE_MIN = 0
    PERCENTAHE_MAX = 100

    CHIP_NUM_MIN = 0
    CHIP_NUM_MAX = 1
    UART_SIZE = 256
    PWM_SIZE = 1024
    PINS_OUTPUT = [0x00, 0x00]
    PINS_OUTPUT_HIGH = [0xff, 0xff]
    PINS_OUTPUT_LOW = [0x00, 0x00]

    FREQ0_CH = 'FREQ0'
    FREQ1_CH = 'FREQ1'
    PHASE0_CH = 'PHASE0'
    PHASE1_CH = 'PHASE1'
    OUTPUT_MODE_SINE = 'sine'
    OUTPUT_MODE_TRIANGULAR = 'triangular'
    OUTPUT_MODE_SQUARE_DIV_2 = 'square_div_2'
    OUTPUT_MODE_SQUARE = 'square'
    SPI_BUS_MODE = 'MODE1'
    ELOAD_DAC_CAL_ITEM = 'DAC_ELOAD'
    SPK_DAC_CAL_ITEM = 'DAC_SPK'
    ELOAD_ADC_CAL_ITEM = 'ADC_ELOAD'


magneto003002_calibration_info = {
    "DAC_SPK": {
        "level1": {"unit_index": 0, "limit": (100, "mV")},
        "level2": {"unit_index": 1, "limit": (500, "mV")},
        "level3": {"unit_index": 2, "limit": (1000, "mV")},
        "level4": {"unit_index": 3, "limit": (2000, "mV")},
        "level5": {"unit_index": 4, "limit": (3000, "mV")},
        "level6": {"unit_index": 5, "limit": (4000, "mV")},
        "level7": {"unit_index": 6, "limit": (5000, "mV")},
    },
    "DAC_ELOAD": {
        "level1": {"unit_index": 7, "limit": (100, "mV")},
        "level2": {"unit_index": 8, "limit": (500, "mV")},
        "level3": {"unit_index": 9, "limit": (1000, "mV")},
        "level4": {"unit_index": 10, "limit": (2000, "mV")},
        "level5": {"unit_index": 11, "limit": (3000, "mV")},
        "level6": {"unit_index": 12, "limit": (4000, "mV")},
        "level7": {"unit_index": 13, "limit": (5000, "mV")},
    },
    "ADC_ELOAD": {
        "level1": {"unit_index": 14, "limit": (100, "mV")},
        "level2": {"unit_index": 15, "limit": (500, "mV")},
        "level3": {"unit_index": 16, "limit": (1000, "mV")},
        "level4": {"unit_index": 17, "limit": (2000, "mV")},
        "level5": {"unit_index": 18, "limit": (3000, "mV")},
        "level6": {"unit_index": 19, "limit": (4000, "mV")},
        "level7": {"unit_index": 20, "limit": (5000, "mV")},
    }
}

magneto003002_range_table = {
    "DAC_SPK", 0,
    "DAC_ELOAD", 1,
    "ADC_ELOAD", 2
}


class MAGNETO003002Exception(Exception):
    pass


class MAGNETO003002(MIXBoard):
    '''
    Magneto003002 module is designed for iphone QT project,Magneto003002
    module is currently only in use on projects D4x,D5x.

    compatible = ['GQQ-MGO003002-000']

    Args:
        i2c                instance(I2C)/None,               Used to control dac,adc,io and eeprom.
        spi                instance(SPI)/None,               Used to control dds output.
        led1642_bus:       instance(AXI4LiteBus),            Used to control led1642.
        pwm_gck_led:       instance(PWM),                    Used to provide gck clock to led1642.
        pwm_output:        instance(PWM),                    Used to output pwm waveform.
        uart_rs485:        instance(UART),                   Used to control the servo motor movement.
        green_led_en:      instance(Pin),                    Used to turn on green led to runing.
        signal_out_en:     instance(Pin),                    Used to control led1642 data transfer.
        spk_shdn_en:       instance(Pin),                    Used to enable/disable spk and hac .
        ringer_dir_pin:    instance(Pin),                    Used to control step motor dir pin.
        acc1_relay:        instance(Pin),                    Used to control acc1 relay.
        acc2_relay:        instance(Pin),                    Used to control acc2 relay.
        relay1_res:        instance(Pin),                    Used to control relay1 res.
        relay2_res:        instance(Pin),                    Used to control relay2 res.

    Examples:
        Example for using no-aggregate IP:

        i2c = I2C('/dev/i2c-0', 256)
        axi4 = AXI4LiteBus('/dev/MIX_QSPI_0', 256)
        spi = PLSPIBus(axi4)
        led1642_bus = AXI4LiteBus('/dev/MIXAxiLiteToStreamSG', 256)
        pwm_gck_led = PLPWM('/dev/MIX_SignalSource_0')
        pwm_output = PLPWM('/dev/MIX_SignalSource_1')
        axi4 = AXI4LiteBus('/dev/AXI4_Uart_0', 256)
        uart_rs485 = UART('/dev/ttyS2')
        green_led_en = GPIO(int(green_led_en))
        signal_out_en = GPIO(int(signal_out_en))
        spk_shdn_en = GPIO(int(spk_shdn_en))
        signal_out_en = GPIO(int(signal_out_en))
        ringer_dir_pin = GPIO(int(ringer_dir_pin))
        acc1_relay = GPIO(int(acc1_relay))
        acc2_relay = GPIO(int(acc2_relay))
        relay1_res = GPIO(int(relay1_res))
        relay2_res = GPIO(int(relay2_res))

        magneto003002 = MAGNETO003002(i2c, spi, led1642_bus=led1642_bus, pwm_gck_led=pwm_gck_led,
                                  pwm_output=pwm_output, uart_rs485=uart_rs485, green_led_en=green_led_en,
                                  signal_out_en=signal_out_en, spk_shdn_en=spk_shdn_en,
                                  ringer_dir_pin=ringer_dir_pin, acc1_relay=acc1_relay, acc2_relay=acc2_relay,
                                  relay1_res=relay1_res, relay2_res=relay2_res)

        magneto003002.module_init()
        result = magneto003002.set_eload_current(1000)
        print(result)
    '''
    compatible = ['GQQ-MGO003002-000']

    rpc_public_api = ['module_init', 'io_set', 'io_get', 'io_set_dir',
                      'io_get_dir', 'get_ioexp_dev', 'ioexp_set', 'ioexp_get',
                      'ioexp_reset', 'dds_output', 'dds_close', 'read_eload_current',
                      'set_eload_current', 'set_volt', 'pwm_output', 'pwm_close',
                      'led_pwm_output', 'led_pwm_close', 'led_on', 'led_off',
                      'led_on_all', 'led_off_all', 'led_grayscale_set', 'set_current_gain',
                      'set_current_range'] + MIXBoard.rpc_public_api

    def __init__(self, i2c=None, spi=None, led1642_bus=None, pwm_gck_led=None, pwm_output=None,
                 uart_rs485=None, green_led_en=None, signal_out_en=None, spk_shdn_en=None,
                 ringer_dir_pin=None, acc1_relay=None, acc2_relay=None, relay1_res=None, relay2_res=None,):

        if i2c:
            self.cat9555_0 = CAT9555(MAGNETO003002Def.CAT9555_INPUT_DEV_ADDR, i2c)
            self.cat9555_1 = CAT9555(MAGNETO003002Def.CAT9555_OUTPUT_DEV_ADDR, i2c)
            self.mcp4725_spk = MCP4725(MAGNETO003002Def.MCP4725_SPK_DEV_ADDR, i2c, MAGNETO003002Def.MCP4725_MVREF)
            self.mcp4725_eload = MCP4725(MAGNETO003002Def.MCP4725_SPK_DEV_ADDR, i2c, MAGNETO003002Def.MCP4725_MVREF)
            self.ads1115 = ADS1115(MAGNETO003002Def.ADS1115_DEV_ADDR, i2c)
            self.eeprom = CAT24C32(MAGNETO003002Def.EEPROM_DEV_ADDR, i2c)

        else:
            self.cat9555_0 = CAT9555Emulator(MAGNETO003002Def.CAT9555_INPUT_DEV_ADDR, None, None)
            self.cat9555_1 = CAT9555Emulator(MAGNETO003002Def.CAT9555_OUTPUT_DEV_ADDR, None, None)
            self.mcp4725_spk = MCP4725Emulator('mcp4725_emulator')
            self.mcp4725_eload = MCP4725Emulator('mcp4725_emulator')
            self.ads1115 = ADS1115Emulator('ads1115_emulator')
            self.eeprom = EepromEmulator('eeprom_emulator')

        self.dds_dev = AD9833(spi) if spi else AD9833Emulator()
        self.pwm_led = pwm_gck_led if pwm_gck_led else MIXPWMSG('pwm_gck_led', MAGNETO003002Def.PWM_SIZE)
        self.pwm_dev = pwm_output if pwm_output else MIXPWMSG('pwm_output', MAGNETO003002Def.PWM_SIZE)
        self.uart_rs485 = uart_rs485 or UARTBusEmulator('uart_emulator', MAGNETO003002Def.UART_SIZE)
        self.gpio_map = {
            "GREEN_LED": green_led_en or GPIOEmulator('GREEN_LED'),
            "SPK_SHDN_EN": spk_shdn_en or GPIOEmulator('SPK_SHDN_EN'),
            "ACC1_RELAY": acc1_relay or GPIOEmulator('ACC1_RELAY'),
            "ACC2_RELAY": acc2_relay or GPIOEmulator('ACC2_RELAY'),
            "RINGER_DIR": ringer_dir_pin or GPIOEmulator('RINGER_DIR'),
            "RELAY1_ERS": relay1_res or GPIOEmulator('RELAY1_ERS'),
            "RELAY2_ERS": relay2_res or GPIOEmulator('RELAY2_ERS'),
            "SIGNAL_OUT_EN": signal_out_en or GPIOEmulator('SIGNAL_OUT_EN')

        }

        if led1642_bus:
            self.led1642 = LED1642(led1642_bus, self.gpio_map['SIGNAL_OUT_EN'])
        else:
            self.led1642 = LED1642Emulator(None, None)

        super(MAGNETO003002, self).__init__(self.eeprom, None, cal_table=magneto003002_calibration_info,
                                            range_table=magneto003002_range_table)

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

        # cat9555_0 are initialized as inputs.
        self.cat9555_0.set_pins_dir([0xFF, 0xFF])
        # cat9555_1 are initialized as output and output high level.
        self.cat9555_1.set_ports([0x00, 0x00])
        self.cat9555_1.set_pins_dir([0x00, 0x00])

        self.io_set_dir('GREEN_LED', 'output')
        self.io_set_dir('SPK_SHDN_EN', 'output')
        self.io_set_dir('ACC1_RELAY', 'output')
        self.io_set_dir('ACC2_RELAY', 'output')
        self.io_set_dir('RINGER_DIR', 'output')
        self.io_set_dir('RELAY1_ERS', 'output')
        self.io_set_dir('RELAY2_ERS', 'output')
        self.io_set('RELAY1_ERS', 1)
        self.io_set('SPK_SHDN_EN', 1)
        self.io_set('GREEN_LED', 1)

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
            |               |  SPK_SHDN_EN              |        1          |
            |               +---------------------------+-------------------+
            |               |  RINGER_DIR               |        2          |
            |               +---------------------------+-------------------+
            |               |  ACC1_RELAY               |        3          |
            |               +---------------------------+-------------------+
            |   External    |  ACC2_RELAY               |        4          |
            |               +---------------------------+-------------------+
            |               |  RELAY1_RES               |        5          |
            |               +---------------------------+-------------------+
            |               |  RELAY2_RES               |        6          |
            |               +---------------------------+-------------------+
            |               |  GREEN_LED                |        8          |
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
        assert chip_num >= MAGNETO003002Def.CHIP_NUM_MIN
        assert chip_num <= MAGNETO003002Def.CHIP_NUM_MAX
        assert status in ['low', 'high']

        device = eval('self.cat9555_' + str(chip_num))
        device.set_pins_dir(MAGNETO003002Def.PINS_OUTPUT)
        if status == 'low':
            device.set_ports(MAGNETO003002Def.PINS_OUTPUT_LOW)
        else:
            device.set_ports(MAGNETO003002Def.PINS_OUTPUT_HIGH)
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
            Magneto003002.dds_output(1000)

        '''
        assert isinstance(frequency, int) and frequency > 0
        assert freq_ch in [MAGNETO003002Def.FREQ0_CH, MAGNETO003002Def.FREQ1_CH]
        assert phase_ch in [MAGNETO003002Def.PHASE0_CH, MAGNETO003002Def.PHASE1_CH]
        assert phase >= 0 and phase <= 2 * math.pi
        assert output_mode in [MAGNETO003002Def.OUTPUT_MODE_SINE, MAGNETO003002Def.OUTPUT_MODE_SQUARE]

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

    def read_eload_current(self):
        '''
        ADS1115 function to read input voltage.

        Returns:
            float, value, unit mV, adc voltage.

        Examples:
            ads1115.read_volt()

        '''
        volt_list = [(self.ads1115.read_volt(MAGNETO003002Def.ADC_CHANNEL)) for _ in range(10)]
        volt = sum(volt_list) / 10

        volt = self.calibrate('ADC_ELOAD', volt)
        return volt

    def set_eload_current(self, volt):
        '''
        MCP4725 function to output eload voltage, 12bit dac

        Args:
            volt:       float, [0~5000], unit mV, output voltage value.

        Returns:
            string, "done", api execution successful.

        Examples:
            mcp4725.output_volt_dc(1000)

        '''
        assert volt >= MAGNETO003002Def.DAC_VAL_MIN
        assert volt <= MAGNETO003002Def.DAC_VAL_MAX

        volt = self.calibrate('DAC_ELOAD', volt)

        self.mcp4725_eload.output_volt_dc(volt)
        return 'done'

    def set_volt(self, volt):
        '''
        MCP4725 function to output dc voltage, 12bit dac

        Args:
            volt:       float, [0~5000], unit mV, output voltage value.

        Returns:
            string, "done", api execution successful.

        Examples:
            mcp4725.output_volt_dc(1000)

        '''

        assert volt >= MAGNETO003002Def.DAC_VAL_MIN
        assert volt <= MAGNETO003002Def.DAC_VAL_MAX

        volt = self.calibrate('DAC_SPK', volt)

        self.mcp4725_spk.output_volt_dc(volt)
        return 'done'

    def pwm_output(self, frequency, pulse, duty=50):
        '''
        PWM output function.

        Args:
            frequency:    int, output PWM's frequency.
            duty:         int, [0~100], adjust signal's duty.
            pulse:        int, [0~0xffffff], unit PWM's pulse count.

        Returns:
            string, "done", api execution successful.

        Examples:
            pwm.pwm_output(10000, 1000, 50)

        '''
        assert isinstance(frequency, int)
        assert isinstance(pulse, int) and pulse > 0
        assert frequency >= MAGNETO003002Def.FREQ_MIN
        assert frequency <= MAGNETO003002Def.FREQ_MAX
        assert duty >= MAGNETO003002Def.DUTY_MIN
        assert duty <= MAGNETO003002Def.DUTY_MAX

        self.pwm_dev.set_enable(False)
        self.pwm_dev.set_frequency(frequency)
        self.pwm_dev.set_duty(duty)
        self.pwm_dev.set_pulse(pulse)
        self.pwm_dev.set_enable(True)
        return 'done'

    def pwm_close(self):
        '''
        PWM close function.

        Returns:
            string, "done", api execution successful.

        Examples:
            pwm.pwm_close()
     .
        '''
        self.pwm_dev.set_enable(False)
        return 'done'

    def led_pwm_output(self, frequency):
        '''
        Led pwm waveform output.

        Args:
            frequency:   int, [1~25000000], unit Hz, frequency value.

        Returns:
            string, "done", api execution successful.

        Examples:
            led_pwm_output(500)

        '''
        assert isinstance(frequency, int)
        assert frequency >= MAGNETO003002Def.FREQ_MIN
        assert frequency <= MAGNETO003002Def.FREQ_MAX

        self.pwm_led.set_enable(False)
        self.pwm_led.set_frequency(frequency * MAGNETO003002Def.PWM_GAIN)
        self.pwm_led.set_duty(MAGNETO003002Def.LED_DUTY)
        self.pwm_led.set_pulse(MAGNETO003002Def.LED_PULSE)
        self.pwm_led.set_enable(True)
        return 'done'

    def led_pwm_close(self):
        '''
        Led PWM close function.

        Returns:
            string, "done", api execution successful.

        Examples:
            led_pwm_close()

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

        '''
        assert isinstance(channel, int)
        assert isinstance(frequency, int)
        assert isinstance(duty, (float, int))
        assert frequency > 0
        assert channel >= MAGNETO003002Def.LED_CH_MIN
        assert channel <= MAGNETO003002Def.LED_CH_MAX
        assert duty >= MAGNETO003002Def.DUTY_MIN
        assert duty <= MAGNETO003002Def.DUTY_MAX

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
        assert channel >= MAGNETO003002Def.LED_CH_MIN
        assert channel <= MAGNETO003002Def.LED_CH_MAX

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
        assert duty >= MAGNETO003002Def.DUTY_MIN
        assert duty <= MAGNETO003002Def.DUTY_MAX

        self.led_pwm_output(frequency)

        for chn in range(MAGNETO003002Def.LED_CHANNEL_COUNT):
            self.led1642.set_channels_duty([(chn, duty)])
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
        for chn in range(MAGNETO003002Def.LED_CHANNEL_COUNT):
            self.led1642.set_channels_duty([(chn, 0)])
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
        assert bits_wide in [MAGNETO003002Def.GRAYSCALE_12, MAGNETO003002Def.GRAYSCALE_16]

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
        assert percentage >= MAGNETO003002Def.PERCENTAHE_MIN
        assert percentage <= MAGNETO003002Def.PERCENTAHE_MAX

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
            led.set_current_range(1).

        '''
        assert isinstance(level, int)
        assert level in [0, 1]

        self.led1642.set_current_range(level)
        return 'done'
