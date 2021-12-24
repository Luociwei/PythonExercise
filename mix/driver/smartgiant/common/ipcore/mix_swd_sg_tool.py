# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import time
import traceback
import inspect
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_swd_sg import MIXSWDSG, MIXSWDSGDef

__author__ = 'jihua.jiang@SmartGiant'
__version__ = '0.1'


_DP_REG = {'DP_IDCODE': 0x00, 'DP_ABORT': 0x00, 'DP_CTRnSTA': 0x01,
           'DP_WIRE_CTRL': 0x02, 'DP_SELECT': 0x02, 'DP_BUFFER': 0x03}

_AP_REG = {
    'AP_CTRLNSTAT': 0x00,
    'AP_TRANSFERADDRESS': 0x04,
    'AP_DATAREADWRITE': 0x0C,
    'AP_BANKDATA0': 0x10,
    'AP_BANKDATA1': 0x14,
    'AP_BANKDATA2': 0x18,
    'AP_BANKDATA3': 0x1C,
    'AP_UNDEFINE1': 0xF0,
    'AP_CONFIG': 0xF4,
    'AP_DEBUFROMADDR': 0xF8,
    'AP_IDREGISTER': 0xFC}

_BUS_SELECT = {
    'AHB_BUS': 0x00000000,
    'APB_BUS': 0x01000000,
    'JTAG_BUS': 0x02000000,
    'CORTEX_BUS': 0x03000000}


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


def get_function_doc(self=None):
    '''Get function.__doc__ '''
    func_name = inspect.stack()[1][3]
    if self is None:
        return eval('%s' % func_name).__doc__
    else:
        return getattr(self, func_name).__doc__


class MIXSWDSGDebuger(cmd.Cmd):
    prompt = 'swd>'
    intro = 'Xavier swd debug tool'
    _dap_bus_select = 'AHB_BUS'

    @handle_errors
    def do_enable(self, line):
        '''enable    --eg. enable'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd._enable()
        print('Done.')

    @handle_errors
    def do_disable(self, line):
        '''disable    --eg. disable'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd._disable()
        print('Done.')

    @handle_errors
    def do_set_speed(self, line):
        '''set_speed <speed>    --eg. set_speed 500000'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd.set_speed(eval(line))
        print('Done.')

    @handle_errors
    def do_set_rst_high(self, line):
        '''set_rst_high    --eg. set_rst_high'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd.set_rst_high()
        print('Done.')

    @handle_errors
    def do_set_rst_low(self, line):
        '''set_rst_low    --eg. set_rst_low'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd.set_rst_low()
        print('Done.')

    @handle_errors
    def do_switch_sequence(self, line):
        '''switch_sequence <timing_data>    --eg. switch_sequence [0x12,0xff,0x21]'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd.switch_sequence(eval(line))
        print('Done.')

    @handle_errors
    def do_write(self, line):
        '''write <addr> <data>    --eg. write 0x23 0x12345678'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.swd.write(*list(eval(line)))

        print('Done.')

    @handle_errors
    def do_read(self, line):
        '''read <addr>    --eg. read 0x23'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        print("0x%x" % self.swd.read(eval(line)))

    @handle_errors
    def do_write_dp_reg(self, line):
        '''write_dp_reg <reg> <data>    --eg. write_dp_reg 'DP_ABORT' 0x12345
        reg:DP_IDCODE,DP_ABORT,DP_CTRnSTA,DP_WIRE_CTRL,DP_SELECT,DP_BUFFER
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        reg, data = list(eval(line))

        self._write_swd_dap_reg('dp_reg', _DP_REG[reg], data & 0xffffffff)

        print('Done.')

    @handle_errors
    def do_read_dp_reg(self, line):
        '''read_dp_reg <reg>    --eg. read_dp_reg 'DP_ABORT'
        reg:DP_IDCODE,DP_ABORT,DP_CTRnSTA,DP_WIRE_CTRL,DP_SELECT,DP_BUFFER
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        reg = eval(line)

        print("0x%x" % self._read_swd_dap_reg('dp_reg', _DP_REG[reg]))

    @handle_errors
    def do_write_ap_reg(self, line):
        '''write_ap_reg <reg> <data>   --eg. write_ap_reg 'AP_CTRLNSTAT' 0x01
        reg:AP_CTRLNSTAT,AP_TRANSFERADDRESS,AP_DATAREADWRITE,AP_BANKDATA0,AP_BANKDATA1,AP_BANKDATA2,
        AP_BANKDATA3,AP_UNDEFINE1,AP_CONFIG,AP_DEBUFROMADDR,AP_IDREGISTER
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        reg, data = list(eval(line))

        self._write_ap_reg(reg, data)

        print('Done.')

    @handle_errors
    def do_read_ap_reg(self, line):
        '''read_ap_reg <reg>    --eg. read_ap_reg 'AP_CTRLNSTAT'
        reg:AP_CTRLNSTAT,AP_TRANSFERADDRESS,AP_DATAREADWRITE,AP_BANKDATA0,AP_BANKDATA1,AP_BANKDATA2,
        AP_BANKDATA3,AP_UNDEFINE1,AP_CONFIG,AP_DEBUFROMADDR,AP_IDREGISTER
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        reg = eval(line)

        print("0x%x" % self._read_ap_reg(reg))

    @handle_errors
    def do_write_swd_reg(self, line):
        '''write_swd_reg <reg> <data>   --eg. write_swd_reg 0x01234 0x01'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        reg, data = list(eval(line))

        self._write_swd_reg(reg, data)

        print('Done.')

    @handle_errors
    def do_read_swd_reg(self, line):
        '''read_swd_reg <reg>    --eg. read_swd_reg 0x12345'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        reg = eval(line)

        print("0x%x" % self._read_swd_reg(reg))

    @handle_errors
    def do_enter_swd_debug(self, line):
        '''enter_swd_debug <timing_data>    --eg. enter_swd_debug [0x12,0xff,0x21]'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.swd.set_rst_high()
        time.sleep(0.01)
        self.swd.set_rst_low()

        timing_data = MIXSWDSGDef.SWITCH_SEQUENCE
        if line:
            timing_data = eval(line)

        self.swd.switch_sequence(timing_data)

        dp_idcode = self._read_swd_dap_reg('dp_reg', _DP_REG['DP_IDCODE'])

        # clear abort
        self._write_swd_dap_reg('dp_reg', _DP_REG['DP_ABORT'], 0x1E)

        # system power on and debug power on
        self._write_swd_dap_reg('dp_reg', _DP_REG['DP_CTRnSTA'], 0x50000000)

        # read ap id
        ap_idcode = self._read_ap_reg('AP_IDREGISTER')

        # SWD_AP_CSW_DBGSWENABLE|SWD_AP_CSW_MASTER_DEBUG|SWD_AP_CSW_HPROT|SWD_AP_CSW_AUTO_INCREAMENT_OFF|SWD_AP_CSW_INC_WORD
        self._write_ap_reg('AP_CTRLNSTAT', 0x23000002)

        print("0x%x 0x%x" % (dp_idcode, ap_idcode))

    def __swdReqParityCheck(self, data):
        data &= 0xff
        data ^= (data >> 4)
        data ^= (data >> 2)
        data ^= (data >> 1)
        data &= 0x01
        return data

    def _write_swd_dap_reg(self, reg_type, addr, data):
        '''
        reg_type: dp_reg or ap_reg
        addr:A[2:3]data
        data:the uint32 data to write
        '''
        # A[2:3]
        request_data = 0x0
        request_data = (addr & 0x03) << 3

        if reg_type == 'dp_reg':
            request_data &= (~(0x01 << 1))

        else:
            request_data |= (0x01 << 1)

        # parity
        parity_flag = self.__swdReqParityCheck(request_data)

        request_data |= ((parity_flag & 0x01) << 5)
        # start: bit0:start,bit6:stop,bit7:park
        request_data |= 0x81

        # send data
        self.swd.write(request_data, int(data & 0xffffffff))

    def _read_swd_dap_reg(self, reg, addr):
        '''
        reg_type: dp_reg or ap_reg
        addr:A[2:3]data
        return: reg data(list)
        '''
        # A[2:3]
        request_data = 0x0
        request_data = (addr & 0x03) << 3
        # RnW = 1
        request_data |= (0x02 << 1)
        if reg == 'dp_reg':
            request_data &= (~(0x01 << 1))

        else:
            request_data |= (0x01 << 1)

        # parity
        parity_flag = self.__swdReqParityCheck(request_data)

        request_data |= ((parity_flag & 0x01) << 5)
        # start: bit0:start,bit6:stop,bit7:park
        request_data |= 0x81

        # send data
        return self.swd.read(request_data)

    def _write_ap_reg(self, reg, data):
        self._write_swd_dap_reg('dp_reg', _DP_REG['DP_SELECT'],
                                (_AP_REG[reg] & 0x0f0) | _BUS_SELECT[self._dap_bus_select])

        self._write_swd_dap_reg('ap_reg', (_AP_REG[reg] & 0x0f) >> 2, data)

    def _read_ap_reg(self, reg):
        self._write_swd_dap_reg('dp_reg', _DP_REG['DP_SELECT'],
                                (_AP_REG[reg] & 0x0f0) | _BUS_SELECT[self._dap_bus_select])
        ret = self._read_swd_dap_reg('ap_reg', (_AP_REG[reg] & 0x0f) >> 2)

        ret = self._read_swd_dap_reg('ap_reg', (_AP_REG[reg] & 0x0f) >> 2)

        return ret

    def _write_swd_reg(self, reg, data):
        self._write_swd_dap_reg(
            'dp_reg', _DP_REG['DP_SELECT'],
            (_AP_REG['AP_TRANSFERADDRESS'] & 0x0f0) | _BUS_SELECT[self._dap_bus_select])

        self._write_swd_dap_reg('ap_reg', (_AP_REG['AP_TRANSFERADDRESS'] & 0x0f) >> 2, reg)
        self._write_swd_dap_reg('ap_reg', (_AP_REG['AP_DATAREADWRITE'] & 0x0f) >> 2, data)

    def _read_swd_reg(self, reg):
        self._write_swd_dap_reg(
            'dp_reg', _DP_REG['DP_SELECT'],
            (_AP_REG['AP_TRANSFERADDRESS'] & 0x0f0) | _BUS_SELECT[self._dap_bus_select])

        self._write_swd_dap_reg('ap_reg', (_AP_REG['AP_TRANSFERADDRESS'] & 0x0f) >> 2, reg)

        ret = self._read_swd_dap_reg('ap_reg', (_AP_REG['AP_DATAREADWRITE'] & 0x0f) >> 2)

        ret = self._read_swd_dap_reg('ap_reg', (_AP_REG['AP_DATAREADWRITE'] & 0x0f) >> 2)

        return ret

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        fun_list = filter(lambda x: x.startswith('do_') and callable(getattr(self, x)), dir(self))
        for fun in fun_list:
            print(getattr(MIXSWDSGDebuger, fun).__doc__)


def create_swd_dbg(dev_name, reg_size=8192):
    swd_dbg = MIXSWDSGDebuger()
    axi4_bus = AXI4LiteBus(dev_name, reg_size)
    swd_dbg.swd = MIXSWDSG(axi4_bus)
    return swd_dbg


# python -m standard.ipcore.mix_swd_sg_tool -d /dev/AXI4_SWD_Core_0
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='fft analyzer device name', default="")

    args = parser.parse_args()

    swd_dbg = create_swd_dbg(args.device)

    swd_dbg.cmdloop()
