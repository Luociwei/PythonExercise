# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps

from mix.driver.core.bus.uart import UART
from mix.driver.smartgiant.common.ipcore.mix_pwm_sg import MIXPWMSG
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.magneto002.module.magneto002002 import MAGNETO002002


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MAGNETO002002Debuger(cmd.Cmd):
    prompt = 'magneto>'
    intro = 'Mix magneto debug tool'

    @handle_errors
    def do_io_set(self, line):
        '''io_set "pin_name" level'''
        line = line.replace(' ', ',')
        self.magneto002002.io_set(*list(eval(line)))
        print("done")

    @handle_errors
    def do_io_get(self, line):
        '''io_get "pin_name"'''
        result = self.magneto002002.io_get(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_io_set_dir(self, line):
        '''io_set_dir "pin_name" "dir"'''
        line = line.replace(' ', ',')
        self.magneto002002.io_set_dir(*list(eval(line)))
        print("done")

    @handle_errors
    def do_io_get_dir(self, line):
        '''io_get_dir "pin_name"'''
        result = self.magneto002002.io_get_dir(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_ioexp_set(self, line):
        '''ioexp_set io_num level'''
        line = line.replace(' ', ',')
        self.magneto002002.ioexp_set(*list(eval(line)))
        print("done")

    @handle_errors
    def do_ioexp_get(self, line):
        '''ioexp_get io_num'''
        result = self.magneto002002.ioexp_get(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_ioexp_reset(self, line):
        '''ioexp_reset chip_num state'''
        line = line.replace(' ', ',')
        self.magneto002002.ioexp_reset(*list(eval(line)))
        print("done")

    @handle_errors
    def do_dds_output(self, line):
        '''dds_output frequency'''
        line = line.replace(' ', ',')
        result = self.magneto002002.dds_output(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_dds_close(self, line):
        '''dds_close'''
        result = self.magneto002002.dds_close()
        print('Result:')
        print(result)

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt'''
        line = line.replace(' ', ',')
        result = self.magneto002002.read_volt(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_set_volt(self, line):
        '''set_volt volt'''
        line = line.replace(' ', ',')
        result = self.magneto002002.set_volt(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_reset_volt(self, line):
        '''reset_volt value'''
        line = line.replace(' ', ',')
        result = self.magneto002002.reset_volt()
        print("Result:")
        print(result)

    @handle_errors
    def do_pwm_output(self, line):
        '''pwm_output channel freq pulse duty'''
        result = self.magneto002002.pwm_output(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_pwm_close(self, line):
        '''pwm_close channel'''
        line = line.replace(' ', ',')
        self.magneto002002.pwm_close(eval(line))
        print("done")

    @handle_errors
    def do_led_pwm_output(self, line):
        '''led_pwm_output frequency'''
        result = self.magneto002002.led_pwm_output(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_led_pwm_close(self, line):
        '''led_pwm_close'''
        result = self.magneto002002.led_pwm_close()
        print("Result:")
        print(result)

    @handle_errors
    def do_led_on(self, line):
        '''led_on ch frequency duty_value'''
        line = line.replace(' ', ',')
        self.magneto002002.led_on(*list(eval(line)))
        print("done")

    @handle_errors
    def do_led_off(self, line):
        '''led_off ch'''
        line = line.replace(' ', ',')
        self.magneto002002.led_off(eval(line))
        print("done")

    @handle_errors
    def do_led_on_all(self, line):
        '''led_on_all frequency duty_value'''
        result = self.magneto002002.led_on_all(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_led_off_all(self, line):
        '''led_off_all'''
        result = self.magneto002002.led_off_all()
        print("Result:")
        print(result)

    @handle_errors
    def do_fft_measure(self, line):
        '''fft_measure io_number level'''
        line = line.replace(' ', ',')
        result = self.magneto002002.fft_measure(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_uart_write(self, line):
        '''uart_write data, tomeout_s'''
        line = line.replace(' ', ',')
        result = self.magneto002002.uart_write(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_uart_read(self, line):
        '''uart_read size, timeout_s'''
        line = line.replace(' ', ',')
        result = self.magneto002002.uart_read(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_read_cal(self, line):
        '''read_calibration_cell unit_index'''
        result = self.magneto002002.read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_cal(self, line):
        '''write_calibration_cell unit_index gain offset threshold'''
        line = line.replace(' ', ',')
        self.magneto002002.write_calibration_cell(*list(eval(line)))
        print("done")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode mode'''
        line = line.replace(' ', ',')
        self.magneto002002.set_calibration_mode(eval(line))
        print("done")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.magneto002002.get_calibration_mode()
        print("Result:")
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_io_set.__doc__)
        print(self.do_io_get.__doc__)
        print(self.do_io_set_dir.__doc__)
        print(self.do_io_get_dir.__doc__)
        print(self.do_ioexp_set.__doc__)
        print(self.do_ioexp_get.__doc__)
        print(self.do_dds_output.__doc__)
        print(self.do_dds_close.__doc__)
        print(self.do_read_volt.__doc__)
        print(self.do_reset_volt.__doc__)
        print(self.do_set_volt.__doc__)
        print(self.do_pwm_output.__doc__)
        print(self.do_pwm_close.__doc__)
        print(self.do_led_pwm_output.__doc__)
        print(self.do_led_pwm_close.__doc__)
        print(self.do_led_on.__doc__)
        print(self.do_led_off.__doc__)
        print(self.do_led_on_all.__doc__)
        print(self.do_led_off_all.__doc__)
        print(self.do_fft_measure.__doc__)
        print(self.do_uart_write.__doc__)
        print(self.do_uart_read.__doc__)
        print(self.do_write_cal.__doc__)
        print(self.do_read_cal.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_magneto002002_dbg(i2c_bus0, led1642_bus, pwm_gck_led, pwm_output, uart_rs485, ad5592r_spi, ad9833_spi,
                             analyzer, gpio_state_pin, pwm1_en_pin, pwm2_en_pin, pwm3_en_pin, pwm4_en_pin,
                             pwm5_en_pin, pwm6_en_pin, pwm7_en_pin, pwm8_en_pin, signal_out_en, iis_rx_en,
                             iis_rx_ovfl, iis_rx_rst):

    i2c = I2C(i2c_bus0)

    led1642_bus = AXI4LiteBus(led1642_bus, 256)
    pwm_gck_led = MIXPWMSG(pwm_gck_led, 1024)
    pwm_output = MIXPWMSG(pwm_output, 1024)

    uart_rs485 = UART(uart_rs485)

    axi4 = AXI4LiteBus(ad5592r_spi, 256)
    ad5592r_spi = MIXQSPISG(axi4)

    axi4 = AXI4LiteBus(ad9833_spi, 256)
    ad9833_spi = MIXQSPISG(axi4)

    analyzer = MIXFftAnalyzerSG(analyzer)

    gpio_state_pin = GPIO(int(gpio_state_pin))
    pwm1_en_pin = GPIO(int(pwm1_en_pin))
    pwm2_en_pin = GPIO(int(pwm2_en_pin))
    pwm3_en_pin = GPIO(int(pwm3_en_pin))
    pwm4_en_pin = GPIO(int(pwm4_en_pin))
    pwm5_en_pin = GPIO(int(pwm5_en_pin))
    pwm6_en_pin = GPIO(int(pwm6_en_pin))
    pwm7_en_pin = GPIO(int(pwm7_en_pin))
    pwm8_en_pin = GPIO(int(pwm8_en_pin))
    signal_out_en = GPIO(int(signal_out_en))
    iis_rx_en = GPIO(int(iis_rx_en))
    iis_rx_ovfl = GPIO(int(iis_rx_ovfl))
    iis_rx_rst = GPIO(int(iis_rx_rst))

    magneto002002 = MAGNETO002002(i2c, led1642_bus, pwm_gck_led, pwm_output, uart_rs485, ad5592r_spi,
                                  ad9833_spi, analyzer, gpio_state_pin, pwm1_en_pin, pwm2_en_pin, pwm3_en_pin,
                                  pwm4_en_pin, pwm5_en_pin, pwm6_en_pin, pwm7_en_pin, pwm8_en_pin, signal_out_en,
                                  iis_rx_en, iis_rx_ovfl, iis_rx_rst)

    magneto002002_dbg = MAGNETO002002Debuger()
    magneto002002.module_init()
    magneto002002_dbg.magneto002002 = magneto002002
    return magneto002002_dbg


arguments = [
    ['-i2c', '--i2c', 'i2c device name, used to control adc, dac, ioexpand, eeprom', '/dev/i2c-2'],
    ['-led', '--led1642', 'led1642 bus device name', '/dev/MIX_AxiLiteToStream_0'],
    ['-pwm_led', '--pwm_gck_led', 'led gck pl pwm device name', '/dev/MIX_SignalSource_0'],
    ['-pwm', '--pwm_output', 'motor pl pwm device name', '/dev/MIX_SignalSource_1'],
    ['-uart', '--rs485', 'pl uart device name', '/dev/ttyS2'],
    ['-ad5592r', '--ad5592r', 'ad or da output', '/dev/MIX_QSPI_1'],
    ['-ad9833', '--ad9833', 'dds output', '/dev/MIX_QSPI_0'],
    ['-analyzer', '--analyzer', 'frequency measure', '/dev/MIX_FftAnalyzer_0'],
    ['-gpio_state', '--gpio_state_pin', 'read level', 86],
    ['-pwm1_en', '--pwm1_en_pin', 'control pwm1 output', 92],
    ['-pwm2_en', '--pwm2_en_pin', 'control pwm2 output', 93],
    ['-pwm3_en', '--pwm3_en_pin', 'control pwm3 output', 94],
    ['-pwm4_en', '--pwm4_en_pin', 'control pwm4 output', 95],
    ['-pwm5_en', '--pwm5_en_pin', 'control pwm5 output', 96],
    ['-pwm6_en', '--pwm6_en_pin', 'control pwm6 output', 97],
    ['-pwm7_en', '--pwm7_en_pin', 'control pwm7 output', 98],
    ['-pwm8_en', '--pwm8_en_pin', 'control pwm8 output', 99],
    ['-signal_out', '--signal_out_pin', 'led signal output', 87],
    ['-iis_rx_en', '--iis_rx_en', 'iis rx en', 90],
    ['-iis_rx_ovfl', '--iis_rx_ovfl', 'iis rx ovfl', 88],
    ['-iis_rx_rst', '--iis_rx_rst', 'iis rx rst', 89]
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()

    magneto002002_dbg = create_magneto002002_dbg(i2c_bus0=args.i2c, led1642_bus=args.led1642,
                                                 pwm_gck_led=args.pwm_gck_led, pwm_output=args.pwm_output,
                                                 uart_rs485=args.rs485, ad5592r_spi=args.ad5592r,
                                                 ad9833_spi=args.ad9833, analyzer=args.analyzer,
                                                 gpio_state_pin=args.gpio_state_pin, pwm1_en_pin=args.pwm1_en_pin,
                                                 pwm2_en_pin=args.pwm2_en_pin, pwm3_en_pin=args.pwm3_en_pin,
                                                 pwm4_en_pin=args.pwm4_en_pin, pwm5_en_pin=args.pwm5_en_pin,
                                                 pwm6_en_pin=args.pwm6_en_pin, pwm7_en_pin=args.pwm7_en_pin,
                                                 pwm8_en_pin=args.pwm8_en_pin, signal_out_en=args.signal_out_pin,
                                                 iis_rx_en=args.iis_rx_en, iis_rx_ovfl=args.iis_rx_ovfl,
                                                 iis_rx_rst=args.iis_rx_rst)
    magneto002002_dbg.cmdloop()
