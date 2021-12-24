# -*- coding: utf-8 -*-
from ..bus.ft_gpio import FTGPIO
from ..bus.ft_spi import FTSPI
from ..bus.ft4222 import FT4222
from ..ic.ad717x import AD7175, AD7177
from ..ic.ad717x_emulator import AD717XEmulator

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FT4222WrapperException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class FT4222Wrapper(object):
    '''
    FT4222Wrapper Driver
        FT4222Wrapper includes AD717x, FTSPI and FTGPIO,
        AD717x and FTSPI will be created, and change flags (use_gpio)
        to decide FTGPIO to be created. The location id can be get using FT4222 official
        command 'get-info' in library source code.

    :param locid_a:         string/int,    locid of FT4222 device, Used to generate spi bus,
                                           if locid < 100, locid means device index.
                                           0 and 1 can be used to automatically open the one FT4222 device.
                                           0 is used to open SPI and I2C.
    :param locid_b:         string/int,    locid of FT4222 device, Used to generate gpio bus,
                                           if locid < 100, locid means device index.
                                           0 and 1 can be used to automatically open the one FT4222 device.
                                           1 is used to open GPIO
    :param ad717x_chip:     string,        ADC chip type('AD7175'/'AD7177').
    :param ad717x_mvref:    int,           ADC reference voltage,default is 5000.
    :param use_gpio:        boolean,       gpio use flag.
    :param gpio_delay:      int,           Optional delay between Init and Write (in miliseconds) in FT4222H.

    .. code-block:: python

        example:
        FT4222Wrapper = FT4222Wrapper(locid_a='0', locid_b='1', ad717x_chip='AD7175', ad717x_mvref=5000,
                        use_gpio=True)

    '''

    def __init__(self, locid_a=None, locid_b=None, ad717x_chip='AD7175', ad717x_mvref=5000, code_polar='bipolar',
                 reference='extern', buffer_flag='enable', clock='crystal',
                 spi_ioline='SPI', spi_speed=64, spi_mode='MODE3', spi_ssomap='SS0O',
                 use_gpio=False, gpio_delay=0):

        self._locid_a = locid_a
        self._locid_b = locid_b
        self._ad717x_chip = ad717x_chip
        self._ad717x_mvref = ad717x_mvref
        self._code_polar = code_polar
        self._reference = reference
        self._buffer_flag = buffer_flag
        self._clock = clock
        self._spi_ioline = spi_ioline
        self._spi_speed = spi_speed
        self._spi_mode = spi_mode
        self._spi_ssomap = spi_ssomap
        self._gpio_delay = gpio_delay
        self.open(use_gpio)

    def __del__(self):
        self.close()

    def open(self, use_gpio):
        '''
        FT4222Wrapper open device

        :example:
                    FT4222wrapper.open()
        '''

        if self._locid_a is not None:
            ft4222_a = FT4222(self._locid_a)
            self.spi = FTSPI(ft4222_a, self._spi_ioline, self._spi_speed, self._spi_mode, self._spi_ssomap)

            if self._ad717x_chip == 'AD7175':
                self.ad717x = AD7175(self.spi, self._ad717x_mvref, self._code_polar, self._reference,
                                     self._buffer_flag, self._clock)
            elif self._ad717x_chip == 'AD7177':
                self.ad717x = AD7177(self.spi, self._ad717x_mvref, self._code_polar, self._reference,
                                     self._buffer_flag, self._clock)
            else:
                raise FT4222WrapperException('Unsupported AD717x chip type %s.' % (self._ad717x_chip))
        else:
            self.spi = FTSPI(None, self._spi_ioline, self._spi_speed, self._spi_mode, self._spi_ssomap)
            if self._ad717x_chip == 'AD7175':
                self.ad717x = AD717XEmulator('ad7175_emulator')
            elif self._ad717x_chip == 'AD7177':
                self.ad717x = AD717XEmulator('ad7177_emulator')
            else:
                raise FT4222WrapperException('Unsupported AD717x chip type %s.' % (self._ad717x_chip))

        # if locid_b is not None and use_gpio is True, GPIO will be created.
        if self._locid_b is not None and use_gpio is True:
            ft4222_b = FT4222(self._locid_b)
            self.gpio = FTGPIO(ft4222_b, self._gpio_delay)
        else:
            self.gpio = FTGPIO(None, self._gpio_delay)

    def close(self):
        '''
        FT4222Wrapper close device

        :example:
                    FT4222wrapper.close()
        '''

        self.ad717x.reset()
