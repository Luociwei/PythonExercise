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
from mix.driver.smartgiant.magneto003.module.magneto003002 import MAGNETO003002


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


class MAGNETO003002Debuger(cmd.Cmd):
    prompt = 'magneto>'
    intro = 'Mix magneto debug tool'

    @handle_errors
    def do_io_set(self, line):
        '''io_set "pin_name" level'''
        line = line.replace(' ', ',')
        self.magneto003002.io_set(*list(eval(line)))
        print("done")

    @handle_errors
    def do_io_get(self, line):
        '''io_get "pin_name"'''
        result = self.magneto003002.io_get(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_io_set_dir(self, line):
        '''io_set "pin_name" "dir"'''
        line = line.replace(' ', ',')
        self.magneto003002.io_set_dir(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_io_get_dir(self, line):
        '''io_get_dir "pin_name"'''
        result = self.magneto003002.io_get_dir(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_ioexp_set(self, line):
        '''ioexp_set io_num level'''
        line = line.replace(' ', ',')
        self.magneto003002.ioexp_set(*list(eval(line)))
        print("done")

    @handle_errors
    def do_ioexp_get(self, line):
        '''ioexp_get io_num'''
        result = self.magneto003002.ioexp_get(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_ioexp_reset(self, line):
        '''ioexp_reset chip_num state'''
        line = line.replace(' ', ',')
        self.magneto003002.ioexp_reset(*list(eval(line)))
        print("done")

    @handle_errors
    def do_dds_output(self, line):
        '''dds_output frequency'''
        line = line.replace(' ', ',')
        result = self.magneto003002.dds_output(eval(line))
        print('Result:')
        print(result)

    @handle_errors
    def do_dds_close(self, line):
        '''dds_close'''
        result = self.magneto003002.dds_close()
        print('Result:')
        print(result)

    @handle_errors
    def do_read_eload_current(self, line):
        '''read_eload_current'''
        result = self.magneto003002.read_eload_current()
        print('Result:')
        print(result)

    @handle_errors
    def do_set_eload_current(self, line):
        '''set_eload_current volt'''
        line = line.replace(' ', ',')
        result = self.magneto003002.set_eload_current(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_volt(self, line):
        '''set_volt value'''
        line = line.replace(' ', ',')
        result = self.magneto003002.set_volt(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_pwm_output(self, line):
        '''pwm_output freq pulse duty'''
        result = self.magneto003002.motor_pwm_output(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_pwm_close(self, line):
        '''pwm_close'''
        self.magneto003002.pwm_close()
        print("Done")

    @handle_errors
    def do_led_pwm_output(self, line):
        '''led_pwm_output frequency'''
        result = self.magneto003002.led_pwm_output(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_led_pwm_close(self, line):
        '''led_pwm_close'''
        result = self.magneto003002.led_pwm_close()
        print("Result:")
        print(result)

    @handle_errors
    def do_led_on(self, line):
        '''led_on ch frequency duty_value'''
        line = line.replace(' ', ',')
        self.magneto003002.led_on(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_led_off(self, line):
        '''led_off ch'''
        line = line.replace(' ', ',')
        self.magneto003002.led_off(eval(line))
        print("Done")

    @handle_errors
    def do_led_on_all(self, line):
        '''led_on_all frequency duty_value'''
        result = self.magneto003002.led_on_all(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_led_off_all(self, line):
        '''led_off_all'''
        result = self.magneto003002.led_off_all()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_cal(self, line):
        '''read_cal unit_index'''
        result = self.magneto003002.read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_cal(self, line):
        '''write_cal index gain offset threshold'''
        line = line.replace(' ', ',')
        self.magneto003002.write_calibration_cell(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_set_cal_mode(self, line):
        '''set_cal_mode mode'''
        line = line.replace(' ', ',')
        self.magneto003002.set_calibration_mode(eval(line))
        print("Done")

    @handle_errors
    def do_get_cal_mode(self, line):
        '''get_cal_mode'''
        result = self.magneto003002.get_calibration_mode()
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
        print(self.do_ioexp_reset.__doc__)
        print(self.do_dds_output.__doc__)
        print(self.do_dds_close.__doc__)
        print(self.do_read_eload_current.__doc__)
        print(self.do_set_eload_current.__doc__)
        print(self.do_set_volt.__doc__)
        print(self.do_pwm_output.__doc__)
        print(self.do_pwm_close.__doc__)
        print(self.do_led_pwm_output.__doc__)
        print(self.do_led_pwm_close.__doc__)
        print(self.do_led_on.__doc__)
        print(self.do_led_off.__doc__)
        print(self.do_led_on_all.__doc__)
        print(self.do_led_off_all.__doc__)
        print(self.do_write_cal.__doc__)
        print(self.do_read_cal.__doc__)
        print(self.do_set_cal_mode.__doc__)
        print(self.do_get_cal_mode.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_magneto003002_dbg(i2c, spi, led1642_bus, pwm_gck_led, pwm_output, uart_rs485,
                             green_led_en, signal_out_en, spk_shdn_en, ringer_dir_pin,
                             acc1_relay, acc2_relay, relay1_res, relay2_res):

    i2c = I2C(i2c)
    axi4 = AXI4LiteBus(spi, 256)
    spi = MIXQSPISG(axi4)
    led1642_bus = AXI4LiteBus(led1642_bus, 256)
    pwm_gck_led = MIXPWMSG(pwm_gck_led, 1024)
    pwm_output = MIXPWMSG(pwm_output, 1024)

    uart_rs485 = UART(uart_rs485)

    green_led_en = GPIO(int(green_led_en))
    signal_out_en = GPIO(int(signal_out_en))
    spk_shdn_en = GPIO(int(spk_shdn_en))
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

    magneto003002_dbg = MAGNETO003002Debuger()
    magneto003002.module_init()
    magneto003002_dbg.magneto003002 = magneto003002
    return magneto003002_dbg


arguments = [
    ['-i2c', '--i2c', 'i2c device name, used to control adc, dac, ioexpand, eeprom', '/dev/i2c-2'],
    ['-spi', '--spi', 'spi bus device name', '/dev/MIX_QSPI_0'],
    ['-led1642_bus', '--led1642_bus', 'led1642 bus device name', '/dev/MIX_AxiLiteToStream_0'],
    ['-pwm_gck_led', '--pwm_gck_led', 'led gck pl pwm device name', '/dev/MIX_SignalSource_0'],
    ['-pwm_output', '--pwm_output', 'motor pl pwm device name', '/dev/MIX_SignalSource_1'],
    ['-uart_rs485', '--uart_rs485', 'pl uart device name', '/dev/ttyS2'],
    ['-green_led_en', '--green_led_en', 'green led enable gpio', 87],
    ['-signal_out_en', '--signal_out_en', 'led signal out gpio', 90],
    ['-spk_shdn_en', '--spk_shdn_en', 'spk shdn enable gpio', 91],
    ['-ringer_dir_pin', '--ringer_dir_pin', 'ringer dir pin status gpio', 92],
    ['-acc1_relay', '--acc1_relay', 'control acc1 gpio', 93],
    ['-acc2_relay', '--acc2_relay', 'controlacc2 gpio', 94],
    ['-relay1_res', '--relay1_res', 'connect relay1 gpio', 95],
    ['-relay2_res', '--relay2_res', 'connect relay2 gpio', 96]
]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])
    args = parser.parse_args()

    magneto003002_dbg = create_magneto003002_dbg(i2c=args.i2c, spi=args.spi, led1642_bus=args.led1642_bus,
                                                 pwm_gck_led=args.pwm_gck_led, pwm_output=args.pwm_output,
                                                 uart_rs485=args.uart_rs485, green_led_en=args.green_led_en,
                                                 signal_out_en=args.signal_out_en, spk_shdn_en=args.spk_shdn_en,
                                                 ringer_dir_pin=args.ringer_dir_pin, acc1_relay=args.acc1_relay,
                                                 acc2_relay=args.acc2_relay, relay1_res=args.relay1_res,
                                                 relay2_res=args.relay2_res)
    magneto003002_dbg.cmdloop()
