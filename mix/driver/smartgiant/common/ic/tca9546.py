# -*- coding: UTF-8 -*-
from mix.driver.core.ic.i2c_mux_base import I2CMUXBase


class TCA9546Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class TCA9546(I2CMUXBase):
    '''
    The TCA9546 is a quad bidirectional translating switch controlled via the I2C bus.

    ClassType = I2C

    Args:
        dev_addr:  hexmial(0-0xff),  tca9546 i2c bus device address.
        i2c_bus:   instance(I2C),    the i2c bus is used to control tca9546.

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        tca9546 = TCA9546(0x70, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert dev_addr & (~0x07) == 0x70
        self._dev_addr = dev_addr
        self._i2c_bus = i2c_bus
        super(TCA9546, self).__init__(self._i2c_bus)

    def set_channel_state(self, channel):
        '''
        TCA9546 set the channel state.

        Args:
            channel: list of list,  [[channel_id, on_off], ...]
                                    0 <= channel_id < 4, on_off: 1=>on, 0=>off

        Examples:
            tca9546.set_channel_state([0, 1], [1, 0])

        '''
        assert type(channel) is list and len(channel) <= 4
        data = 0
        for index in range(len(channel)):
            assert channel[index][0] in range(4)
            assert channel[index][1] in range(2)
            data |= channel[index][1] << channel[index][0]
        write_data = []
        write_data.append(data)
        self._i2c_bus.write(self._dev_addr, write_data)

    def get_channel_state(self, channel):
        '''
        TCA9546 get the channel state.

        Args:
            channel:  list,  eg: [0,1,2,3]

        Returns:
            list, [(channel_id, on_off), ...], on_off: 1=>on, 0=>off.

        Examples:
            data = tca9546.get_channel_state([0, 1, 2])
            print(data)

        '''
        assert type(channel) is list and len(channel) <= 4
        ret = self._i2c_bus.read(self._dev_addr, 1)
        read_data = []
        for index in range(len(channel)):
            assert channel[index] in range(4)
            read_data.append([channel[index], (ret[0] >> channel[index]) & 0x1])
        return read_data

    def open_all_channel(self):
        '''
        TCA9546 open all channel.

        Examples:
            tca9546.open_all_channel()

        '''
        write_data = [0x0f]
        self._i2c_bus.write(self._dev_addr, write_data)

    def close_all_channel(self):
        '''
        TCA9546 close all channel.

        Examples:
            tca9546.close_all_channel()

        '''
        write_data = [0x00]
        self._i2c_bus.write(self._dev_addr, write_data)
