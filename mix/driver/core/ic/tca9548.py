# -*- coding: UTF-8 -*-
from ..bus.i2c_bus_emulator import I2CBusEmulator
from ..bus.axi4_lite_def import PLI2CDef
from i2c_mux_base import I2CMUXBase


class TCA9548Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class TCA9548(I2CMUXBase):
    '''
    TCA9548 is 8 channels switch reset

    ClassType = I2C

    you can use it to control the i2c bus device.

    Args:
        dev_addr:  hexmial(0-0xff),  i2c bus device address.
        i2c_bus:   Instance(I2C)/None,  i2c bus class instance, if not
                                        using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = PLI2CBus(axi4_bus)
        tac9548 = TCA9548(0x70, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        assert dev_addr & (~0x07) == 0x70
        self._dev_addr = dev_addr
        if i2c_bus is None:
            self._i2c_bus = I2CBusEmulator('i2c_emulator', PLI2CDef.REG_SIZE)
        else:
            self._i2c_bus = i2c_bus
        super(TCA9548, self).__init__(self._i2c_bus)

    def set_channel_state(self, channel):
        '''
        TCA9548 set the channel state.

        Args:
            channel: list of list,  [[channel_id, on_off], ...]
                                    0<= channel_id < 8, on_off: 1=>on, 0=>off

        Examples:
            cat9548.set_channel_state([[0, 1], [1, 0])

        '''
        assert type(channel) is list and len(channel) <= 8
        data = 0
        for index in range(len(channel)):
            assert channel[index][0] in range(8)
            assert channel[index][1] in range(2)
            data |= channel[index][1] << channel[index][0]
        write_data = []
        write_data.append(data)
        self._i2c_bus.write(self._dev_addr, write_data)

    def get_channel_state(self, channel):
        '''
        TCA9548 set the channel state.

        Args:
            channel:  list,  eg: [0,1,2,3]

        Returns:
            list, [(channel_id, on_off), ...], on_off: 1=>on, 0=>off.

        Examples:
            data = tca9548.get_channel_state([0, 1, 2])
            print(data)

        '''
        assert type(channel) is list and len(channel) <= 8
        ret = self._i2c_bus.read(self._dev_addr, 1)
        read_data = []
        for index in range(len(channel)):
            assert channel[index] in range(8)
            read_data.append([channel[index], (ret[0] >> channel[index]) & 0x1])
        return read_data

    def open_all_channel(self):
        '''
        TCA9548 open all channel.

        Examples:
            tca9548.open_all_channel()

        '''

        write_data = [0xff]
        self._i2c_bus.write(self._dev_addr, write_data)

    def close_all_channel(self):
        '''
        TCA9548 close all channel.

        Examples:
            tca9548.close_all_channel()

        '''

        write_data = [0x00]
        self._i2c_bus.write(self._dev_addr, write_data)
