# -*- coding: utf-8 -*-
import os
import hashlib
import struct
import math
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_hdmi_sink_emulate_sg import MIXHDMISinkEmulateSG
from mix.driver.smartgiant.common.module.mix_board import MIXBoard


__author__ = 'qingzhen.zhu@SmartGiant'
__version__ = '0.2'


class SG2700SU09PCADef:
    REG_SIZE = 256
    NTC_ADDR = 0x48
    EEPROM_ADDR = 0X50
    PS8409_ADDR = 0x0C
    PS8409_STATUS_REG = 0x90
    EDID_SIZE_1 = 128
    EDID_SIZE_2 = 256
    EDID_PAGE_SIZE = 16

    EDID_PAGE_SIZE = 16
    EDID_PAGE_SIZE = 16

    EDID_EEPROM_ID = 0
    EDID_EEPROM_SPEED = 100000
    EDID_EEPROM_ADDR = 0x50
    EDID_EEPROM_REG_LEN = 1
    EDID_EEPROM_DATA_WIDTH = 1

    SCDC_EEPROM_ID = 1
    SCDC_EEPROM_SPEED = 100000
    SCDC_EEPROM_ADDR = 0x54
    SCDC_EEPROM_REG_LEN = 1
    SCDC_EEPROM_DATA_WIDTH = 1

    EEPROM_MULATE = {
        'EDID_eeprom': EDID_EEPROM_ID,
        'SCDC_eeprom': SCDC_EEPROM_ID,
    }

    PS8409_REG_INFO = {
        'clock': ['unstable', 'stable'],
        'data rate': ['higher', 'lower'],
        'scdc mode': ['1.4', '2.0']
    }

    FILE_PATH = "/mix/driver/smartgiant/sg2700_su09pc_a/module/"

    SWITCH_INFO = {'ICI': 0, 'HDMI': 1}
    STATUS_INFO = {'disable': 0, 'enable': 1}


class SG2700SU09PCAException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class SG2700SU09PCA(MIXBoard):

    '''
    Driver for SG2700SU09PCA board. only control CAT24C32 & NCT75 & PS8409 chip

    hdmixx.Bin file is a data file conforming to EDID specification.
    hdmi1_4_1920x1080.bin: hdmi specification = 1.4, screen resolution = 1920 x 1080
    hdmi1_4_460x540.bin: hdmi specification = 1.4, screen resolution = 460x540
    hdmi2_0.bin: hdmi specification = 2.0, screen resolution = 4k@60Hz
    hdmi2_0_A.bin: hdmi specification = 2.0, screen resolution = 4k@60Hz, provided by A.


    Args:
        ps8409_i2c:          instance(I2C),     for connect to PS8409 chip.
        eeprom_i2c:          instance(I2C),     for connect to CAT24C32 & NCT75F chip.
        hpd_io:              instance(gpio)/instance(cat9555.pin), for control hpd pin.
        signal_source_io     instance(gpio)/instance(cat9555.pin), for control signal source pin.
        signal_ctrol_io:     instance(gpio)/instance(cat9555.pin), for control signal funtion pin.
        ipcore:              instance(MIXHDMISinkEmulateSG) for HDMI i2c master read config message.
        init_file:           string, the file name to write to edid eeprom, default hdmi2_0.bin.

    '''
    rpc_public_api = ["read_PS8409", "write_PS8409", "config_SCDC_eeprom", "config_eeprom_emulate",
                      "write_eeprom_emulate", "read_eeprom_emulate", "init_eeprom_emulate",
                      "hpd_level", "signal_source_switch", "signal_ctrol", "get_hdmi_status",
                      "hdmi_standard_switch"] + MIXBoard.rpc_public_api

    def __init__(self, ps8409_i2c, eeprom_i2c, hpd_io, signal_source_io,
                 signal_ctrol_io, ipcore=None, init_file='hdmi2_0.bin'):
        self.ps8409_i2c = ps8409_i2c
        self.eeprom_i2c = eeprom_i2c
        self.hpd_io = hpd_io
        self.signal_source_io = signal_source_io
        self.signal_ctrol_io = signal_ctrol_io
        self.hpd_io.set_dir('output')
        self.signal_source_io.set_dir('output')
        self.signal_ctrol_io.set_dir('output')
        self.eeprom = CAT24C32(SG2700SU09PCADef.EEPROM_ADDR, self.eeprom_i2c)
        self.nct75 = NCT75(SG2700SU09PCADef.NTC_ADDR, self.eeprom_i2c)

        if isinstance(ipcore, basestring):
            axi4_bus = AXI4LiteBus(ipcore, SG2700SU09PCADef.REG_SIZE)
            self.ipcore = MIXHDMISinkEmulateSG(axi4_bus)
        else:
            self.ipcore = ipcore

        if ipcore is not None:
            # init edid and scdc eeprom
            self.config_eeprom_emulate("EDID_eeprom", SG2700SU09PCADef.EDID_EEPROM_SPEED,
                                       SG2700SU09PCADef.EDID_EEPROM_ADDR, SG2700SU09PCADef.EDID_EEPROM_REG_LEN,
                                       SG2700SU09PCADef.EDID_EEPROM_DATA_WIDTH)
            self.config_eeprom_emulate("SCDC_eeprom", SG2700SU09PCADef.SCDC_EEPROM_SPEED,
                                       SG2700SU09PCADef.SCDC_EEPROM_ADDR, SG2700SU09PCADef.SCDC_EEPROM_REG_LEN,
                                       SG2700SU09PCADef.SCDC_EEPROM_DATA_WIDTH)
            self.config_SCDC_eeprom()

            # init hdmi info to hdmi2.0
            self.init_eeprom_emulate("EDID_eeprom", SG2700SU09PCADef.FILE_PATH + init_file)
            self.hpd_level(1)
            self.signal_source_switch('ICI')
            self.signal_ctrol('enable')

        super(SG2700SU09PCA, self).__init__(self.eeprom, self.nct75)

    def hpd_level(self, status):
        '''
        Output hpd signal status.

        Args:
            status: int, [0,1], Output hpd signal status.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert status in [0, 1]
        self.hpd_io.set_level(status)
        return 'done'

    def signal_source_switch(self, source):
        '''
        Select the source input mode.

        Args:
            source:     string, ['ICI','HDMI'], Select the source input mode..

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert source in ['ICI', 'HDMI']
        self.signal_source_io.set_level(SG2700SU09PCADef.SWITCH_INFO[source])
        return 'done'

    def signal_ctrol(self, status):
        '''
        Enable signal.

        Args:
            status:     string, ['enable','disable'], Enable signal.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert status in ['enable', 'disable']
        self.signal_ctrol_io.set_level(SG2700SU09PCADef.STATUS_INFO[status])
        return 'done'

    def config_SCDC_eeprom(self):
        '''
        config SCDC state and control data channel

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        self.write_eeprom_emulate("SCDC_eeprom", 0x00, [
                                  0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x10, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x20, [
                                  0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x30, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x40, [
                                  0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x50, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x60, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x70, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x80, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0x90, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xa0, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xb0, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xc0, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xd0, [
                                  0xEF, 0xCD, 0xAB, 0x27, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xe0, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_eeprom_emulate("SCDC_eeprom", 0xf0, [
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        return 'done'

    def get_hdmi_status(self):
        '''
        get hdmi status.

        Retruns:
            dict, {'scdc mode': scdc_mode_value, 'data rate': data_rate_value, 'clock': clock_value},\
                   'clock_value': ['unstable', 'stable']\
                   'data_rate_value': ['higher', 'lower']\
                   'scdc_mode_value': ['1.4', '2.0']
        '''
        value = self.ps8409_i2c.write_and_read(SG2700SU09PCADef.PS8409_ADDR,
                                               [SG2700SU09PCADef.PS8409_STATUS_REG], 1)[0]

        scdc_mode_value = SG2700SU09PCADef.PS8409_REG_INFO['scdc mode'][value & 0x01]
        data_rate_value = SG2700SU09PCADef.PS8409_REG_INFO['data rate'][(value >> 1) & 0x01]
        clock_value = SG2700SU09PCADef.PS8409_REG_INFO['clock'][(value >> 2) & 0x01]

        status = {
            'scdc mode': scdc_mode_value,
            'data rate': data_rate_value,
            'clock': clock_value,
        }

        return status

    def read_PS8409(self, reg, len_size):
        '''
        read data from PS8409 chip

        Args:
            reg:        int, (>=0), reg addr of chip.
            len_size:   int, (>=0), read data size.

        Returns:
            list, [value], return reg data.
        '''
        assert isinstance(reg, int)
        assert isinstance(len_size, int)
        return self.ps8409_i2c.write_and_read(SG2700SU09PCADef.PS8409_ADDR, [reg], len_size)

    def write_PS8409(self, reg, data_list):
        '''
        write data to PS8409 chip

        Args:
            reg:         int, (>=0), reg addr of chip.
            data_list:   list, (>=0), write data list.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert isinstance(reg, int)
        assert isinstance(data_list, list)
        data_list.insert(0, reg)
        self.ps8409_i2c.write(SG2700SU09PCADef.PS8409_ADDR, data_list)
        return 'done'

    def config_eeprom_emulate(self, eeprom_name, speed_hz, dev_addr, reg_len, data_width):
        '''
        Config emulator speed, device address, register address length and data width.

        Args:
            eeprom_name: string, ["EDID_eeprom", "SCDC_eeprom"], eeprom emulate name.
            speed_hz:   int, [0~2000000], I2C bus speed in Hz.
            dev_addr:   int, [0~0x7F], device address.
            reg_len:    int, [1,2], register address length.
            data_width: int, [1,2,3,4], one data width in byte.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert eeprom_name in SG2700SU09PCADef.EEPROM_MULATE.keys()

        return self.ipcore.config(SG2700SU09PCADef.EEPROM_MULATE[eeprom_name],
                                  speed_hz, dev_addr, reg_len, data_width)

    def write_eeprom_emulate(self, eeprom_name, addr, data_list):
        '''
        Write data to eeprom emulate.

        Args:
            eeprom_name: string, ["EDID_eeprom", "SCDC_eeprom"], eeprom emulate name.
            addr:        int, [0x00~0xffff], register address.
            data_list:   list, (>=0), data to be write, One data width is decided by config function.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert eeprom_name in SG2700SU09PCADef.EEPROM_MULATE.keys()

        return self.ipcore.register_write(SG2700SU09PCADef.EEPROM_MULATE[eeprom_name], addr, data_list)

    def read_eeprom_emulate(self, eeprom_name, addr, data_len):
        '''
        Read data from eeprom emulate.

        Args:
            eeprom_name: string, ["EDID_eeprom", "SCDC_eeprom"],    eeprom emulate name.
            addr:   int, (>=0), register address
            rd_len:     int, (>=0), length of data to be read.

        Returns:
            list, [value], data has been read. One data width is decided by config function.
        '''
        assert eeprom_name in SG2700SU09PCADef.EEPROM_MULATE.keys()

        return self.ipcore.register_read(SG2700SU09PCADef.EEPROM_MULATE[eeprom_name], addr, data_len)

    def init_eeprom_emulate(self, eeprom_name, fileName, checksum=None):
        '''
        init eeprom emulate.

        Args:
            eeprom_name:    string, ["EDID_eeprom", "SCDC_eeprom"], eeprom emulate name.
            fileName:       string, data file path, need file full path.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert eeprom_name in SG2700SU09PCADef.EEPROM_MULATE.keys()

        data_list = []
        raw_data = []

        # expand to full path for ~
        fileName = os.path.expanduser(fileName)
        try:
            if os.path.isfile(fileName):
                if checksum is None:
                    with open(fileName, 'rb') as fd:
                        data_list = fd.read()
                        print("no md5, file size %s" % len(data_list))
                else:
                    print("file name: {}, md5: {}".format(fileName, checksum))
                    with open(fileName, 'rb') as fd:
                        fd_md5 = hashlib.md5()
                        data_list = fd.read()
                        fd_md5.update(data_list)
                        file_md5 = fd_md5.hexdigest()
                        if file_md5 == checksum:
                            pass
                        else:
                            fd.close()
                            raise SG2700SU09PCAException(
                                "file <{}> md5: {}, expect md5: {}".format(fileName, file_md5, checksum))
            else:
                raise SG2700SU09PCAException("not find file <%s>" % (fileName))

        except Exception as e:
            raise e

        for i in range(len(data_list)):
            raw_data.append(struct.unpack('B', data_list[i])[0])

        data_size = SG2700SU09PCADef.EDID_SIZE_1
        if len(data_list) > 128:
            data_size = SG2700SU09PCADef.EDID_SIZE_2

        page = SG2700SU09PCADef.EDID_PAGE_SIZE
        i_range = math.ceil(data_size * 1.0 / page)

        write_addr = 0x00

        for i in range(int(i_range)):
            index = i * page
            size = page
            if len(raw_data) < index + page:
                size = len(raw_data) - index

            chunk = raw_data[index:size + index]

            self.write_eeprom_emulate(eeprom_name, write_addr, chunk)
            write_addr += size

        return 'done'

    def hdmi_standard_switch(self, file_name, signal_source='ICI'):
        '''
        Switch hdmi standard.

        Args:
            file_name:      string, ['hdmi1_4_1920x1080.bin', 'hdmi1_4_460x540.bin',\
                                    'hdmi2_0.bin', 'hdmi2_0_A.bin'], file name.
            signal_source:  string, ['ICI','HDMI'], default ICI, signal source.

        Retruns:
            string: str, "done", return "done" if execute successfully..
        '''
        assert file_name in ['hdmi1_4_1920x1080.bin', 'hdmi1_4_460x540.bin',
                             'hdmi2_0.bin', 'hdmi2_0_A.bin']
        assert signal_source in ['ICI', 'HDMI']

        self.init_eeprom_emulate("EDID_eeprom", SG2700SU09PCADef.FILE_PATH + file_name)
        self.hpd_level(1)
        self.signal_source_switch(signal_source)
        self.signal_ctrol('enable')

        return 'done'
