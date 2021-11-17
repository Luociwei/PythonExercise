# -*- coding: utf-8 -*-
from ..tracer.recorder import *


class NCT75Emulator(object):
    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._reg = {
            0x00: 0x00,
            0x01: 0x00,
            0x02: 0x00,
            0x03: 0x00
        }
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def __del__(self):
        del_recorder(self._recorder)

    def get_temperature(self):
        self._recorder.record("read temperature")
        return 25

    def get_work_mode(self):
        self._work_mode

    def set_work_mode(self, mode):
        self._work_mode = mode

    def register_read(self, reg_addr, rd_len):
        '''
        NCT75 read specific length datas from address

        Args:
            reg_addr:       hex, [0~0xFF], Read datas from this address.
            rd_len:         int, [0~1024], Length to read.

        Returns:
            list

        Examples:
            rd_data = nct75.register_read(0x00, 1)
            print(rd_data)

        '''
        assert reg_addr in self._reg.keys()

        self._recorder.record("NCT75 read_register %s with %d bytes" % (hex(reg_addr), rd_len))

        return [self._reg[reg_addr + i] for i in range(rd_len)]

    def register_write(self, reg_addr, write_data):
        '''
        NCT75 write datas to address, support cross pages writing operation

        Args:
            reg_addr:       int, [0~1024], Write data to this address.
            write_data:     list, Data to write.

        Examples:
            wr_data = [0x01]
            nct75.register_write(0x00, wr_data)

        '''
        assert reg_addr in self._reg.keys()

        record_data = "["
        for i in range(len(write_data)):
            self._reg[reg_addr + i] = write_data[i]
            record_data += "0x%02x" % (write_data[i])
            if i != len(write_data) - 1:
                record_data += ", "
        record_data += "]"

        self._recorder.record("NCT75 write %s to 0x%02x" % (record_data, reg_addr))

    def config_overtemperature(self, t_os, t_hyst, mode='cmp', polarity='low'):
        '''
        Config nct75 over temperature

        Args:
            t_os:       float, temperature limit at which the part asserts an OS/Alert.
            t_hyst:     float, temperature hysteresis value for the overtemperature output.
            mode:       string, ['cmp', 'int'], default 'cmp', overtemperature modes.
            polarity:   string, ['low', 'high'], default 'low', active polarity of the OS
                                Alert output pin.
        '''
        self._recorder.record('NCT75 config_overtemperature')
