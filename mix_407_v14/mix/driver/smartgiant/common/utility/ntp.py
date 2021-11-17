# -*- coding: utf-8 -*-
import os
import time
import struct
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.5'


class AXI4UTCDef:
    REGISTER_SIZE = 256
    REG_MIRCOSECOND_WRITE = 0x40
    REG_SECOND_WRITE = 0x42
    REG_WRITE_UPDATE = 0x46
    REG_READ_UPDATE = 0x47
    REG_MIRCOSECOND_READ = 0x48
    REG_SECOND_READ = 0x4A
    ENABLE = 1
    DISABLE = 0


class AXI4UTC(object):
    '''
    AXI4UTC support configuration of UTC for fpga ipcore

    :param     emulator:      support emulator when emulator==True
    :example:
                fpga_rtc = AXI4UTC()
                fpga_rtc.set_rtc(time.time())
    '''

    def __init__(self, emulator=False):
        if emulator:
            self._axi4_bus = AXI4LiteBusEmulator('pl_utc_emulator', AXI4UTCDef.REGISTER_SIZE)
        else:
            self._axi4_bus = AXI4LiteBus('/dev/MIX_SysReg_0', 256)

    def get_fpga_version(self):
        '''
        Get fpga ipcore version

        :return:    string,     for example 'V0.1'
        :example:
                    ver_string = Axi4UTC.get_fpga_version()
                    print(ver_string)
        '''
        version_c_charArray = self._axi4_bus.get_ipcore_ver()[:4]
        version_str = struct.unpack('4s', version_c_charArray)[0]
        return version_str

    def set_rtc(self, second, millisecond):
        '''
        Set RTC(UTC(Universal Time Coordinated)), the total time since 1970-01-01 00:00:00

        :param     second:         int ( >=0 )
        :param     millisecond:    int (0 ~ 999)
        :return:    None or AssertError
        :example:
                    second = 1538296130  #2018-09-30 16:28:50 CST
                    millisecond = 0
                    Axi4UTC.set_rtc(second, millisecond)
        '''
        assert (second >= 0)
        assert (millisecond >= 0)
        assert (millisecond < 1000)

        self._axi4_bus.write_16bit_fix(AXI4UTCDef.REG_MIRCOSECOND_WRITE, [millisecond])
        self._axi4_bus.write_32bit_fix(AXI4UTCDef.REG_SECOND_WRITE, [second])
        self._axi4_bus.write_8bit_fix(AXI4UTCDef.REG_WRITE_UPDATE, [AXI4UTCDef.ENABLE])

    def get_rtc(self):
        '''
        Get RTC(UTC(Universal Time Coordinated)), the total time since 1970-01-01 00:00:00

        :return:    tuple(second, millisecond),     (int, float)
        :example:
                    (second, millisecond) = Axi4UTC.get_rtc()
        '''
        self._axi4_bus.write_8bit_fix(AXI4UTCDef.REG_READ_UPDATE, [AXI4UTCDef.ENABLE])
        millisecond = self._axi4_bus.read_16bit_fix(AXI4UTCDef.REG_MIRCOSECOND_READ, 1)[0] / 1000.0
        second = self._axi4_bus.read_32bit_fix(AXI4UTCDef.REG_SECOND_READ, 1)[0]

        return(second, millisecond)


class NTP(object):
    '''
    Place holder class to set and get xavier RTC as well as set FPGA RTC.
    Pending decision on whether put set_rtc in here in driver or put in rpc_server.
    '''

    rpc_public_api = ['set_rtc', 'get_rtc', 'set_ntp_server']

    def set_rtc(self, timestamp):
        '''
        This function will set Xavier Linux system RTC(Real Time Clock) to given value
        And set FPGA RTC to the same value.

        :param     timestamp:      float,   should be seconds from 1970/1/1 00:00:00 in float or int.
        :return:    string '--PASS--' when succeed; Error string in case of any error.
        :example:
                    client.server_set_rtc(time.time()) will set xavier RTC to current time.
                    timestamp = 1538296130  #2018-09-30 16:28:50 CST
                    client.server_set_rtc(timestamp)
        '''

        try:
            timestamp = float(timestamp)
        except:
            raise ValueError('timestamp value should be float or int!')

        assert timestamp >= 0

        if 0 != os.system('date -s @' + str(timestamp)):
            return '--FAIL--'

        def save_rtc_to_fpga(second, millisecond):
            from ntp import AXI4UTC
            mix_uct = AXI4UTC()
            mix_uct.set_rtc(second, millisecond)

        seconds = int(timestamp)
        milliseconds = int((timestamp - seconds) * 1000)
        save_rtc_to_fpga(seconds, milliseconds)

        return '--PASS--'

    def get_rtc(self):
        '''
        Getting RTC(Real-time clock), POSIXtime, the total second since 1970-01-01 00:00:00

        :return:    timestamp,      float
        :example:
                    timestamp = client.server_get_rtc()
                    print(timestamp)
        '''
        return time.time()

    def set_ntp_server(self, host_addr):
        '''
        Synchronizing date with host by NTP(Network Time Protocol) server

        :param     host_addr:          str(<IP>),     IPv4 address, as '64.236.96.53'
        :return:    'pass' or Assert
        :example:
                    host_addr = '210.72.145.44'
                    client.server_set_ntp_server(host_addr)
        '''
        def set_server_ip(host_addr):
            ntp_conf_file = '/etc/ntp.conf'
            with open(ntp_conf_file, 'wb') as f:
                f.writelines('server ' + str(host_addr) + ' ')

            return True

        set_server_ip(host_addr)
        assert (0 == os.system('service ntp stop')), 'ntp service stop fail'
        assert (0 == os.system('ntpdate ' + host_addr)), 'ntpdate get date fail'
        assert (0 == os.system('service ntp start')), 'ntp service start fail'

        return '--PASS--'
