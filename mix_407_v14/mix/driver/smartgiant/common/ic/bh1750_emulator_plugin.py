# -*- coding: utf-8 -*-

__author__ = 'st@trantest.com'
__version__ = '0.1'


class BH1750EmulatorPlugin(object):
    BH_POWER_DOWN = 0x00
    BH_POWER_ON = 0x01
    BH_RESET = 0x07
    BH_Conti_H_Res_Mode = 0x10
    BH_Conti_H_Res_Mode2 = 0x11
    BH_Conti_L_Res_Mode = 0x13
    BH_OneTime_H_Res_Mode = 0x20
    BH_OneTime_H_Res_Mode2 = 0x21
    BH_OneTime_L_Res_Mode = 0x23
    BH_Chg_Meas_Time_765 = 0x40
    BH_Chg_Meas_Time_43210 = 0x60

    def __init__(self):
        pass

    def write(self, addr, wr_data):
        assert (addr == 0x23) or (addr == 0x5C)
        assert (len(wr_data) == 1)
        pass

    def read(self, addr, rd_len):
        assert (addr == 0x23) or (addr == 0x5C)
        assert rd_len == 2
        return [0x00, 0x00]

    def write_and_read(self, addr, wr_data, rd_len):
        raise NotImplementedError('Unsupported control due to waiting required after write')
