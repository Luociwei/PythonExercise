# -*- coding: UTF-8 -*-
from ..tracer.recorder import *
from ..bus.i2c_bus_emulator import I2CEmulator


class I2CMUXEmulator(object):
    '''
    Emulator for I2CMUX
    :param   dev_addr:  hexmial(0-0xff),  i2c bus device address
    :param   i2c_bus:   Instance/None,    i2c bus class instance, if not
                                           using, will create emulator
    :example:
              axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
              # create a 8 channel emulator
              i2c_mux_emulator = I2CMUXEmulator(0x70, 8)
    '''

    def __init__(self, dev_addr, num_channel):

        self._i2c_bus = I2CEmulator('i2c_emulator')
        self._dev_addr = dev_addr
        self.num_channel = num_channel

        # internal registers emulation; init all channels to be off (0)
        self.channel_status = [0] * num_channel
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def __del__(self):
        del_recorder(self._recorder)

    def set_channel_state(self, channel):
        '''
        Set the channel state.

        :param channel: list of list,  [(channel_id, on_off), ...]
                                        0<= channel_id < 8, on_off: 1=>on, 0=>off
        :example:
                i2c_mux_emulator.set_channel_state([[0, 1], [1, 0])
        '''
        assert type(channel) is list and len(channel) <= self.num_channel
        for [channel_id, on_off] in channel:
            self.channel_status[channel_id] = on_off
        msg = 'i2c_mux_emulator {:x} set channel {}'.format(self._dev_addr, channel)
        self._recorder.record(msg)

    def get_channel_state(self, channel):
        '''
        Set channel state.

        :param   channel:  list,  eg: [0,1,2,3]
        :returns: [(channel_id, on_off), ...], on_off: 1=>on, 0=>off
        :example:
                  data = i2c_mux_emulator.get_channel_state([0, 1, 2])
                  print(data)
        '''
        assert type(channel) is list and len(channel) <= self.num_channel
        msg = 'i2c_mux_emulator {:x} get channel {}'.format(self._dev_addr, channel)
        self._recorder.record(msg)
        return [[i, self.channel_status[i]] for i in channel]

