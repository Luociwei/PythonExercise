# -*- coding: utf-8 -*-
from __future__ import division
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.utility.data_operate import DataOperate
import time

__author__ = 'GraceWang@Apple'
__version__ = '2.2'



class PLTimerDef:
    #constant
    SYS_CLK_FREQ = 125000000
    REG_SIZE     = 65536
    #registers
    MODE    = 0x00
    CFG     = 0x04
    LEN_L   = 0x08
    LEN_H   = 0x0C
    SYSCTRL = 0x10
    CCR_L   = 0x14
    CCR_H   = 0x18
    CNT_L   = 0x1C
    CNT_H   = 0x20
    STATUS  = 0x24
    REG_EXCLK_EN = 0x04 
    REG_TRIGGER  = 0x05 
    REG_FREQ     = 0x06 
    REG_ENABLE   = 0x10 
    REG_IP_RST   = 0x13 
    REG_FLAG     = 0x24 
    REG_DONE     = 0x27
    #funcitonal mode parameter
    IDLE_MODE = 0x00
    FREQ_M    = 0x01
    PULSE_M_S = 0x02
    PULSE_M_D = 0x03
    EDGE_C    = 0x04
    PULSE_G   = 0x05
    EDGE_M    = 0x06
    #trigger control
    ACTIVE_LOW  = 0x00
    ACTIVE_HIGH = 0x01
    FALL2FALL   = 0x00
    FALL2RISE   = 0x01
    RISE2FALL   = 0x02
    RISE2RISE   = 0x03
    COUNT_RISE  = 0x00
    COUNT_FALL  = 0x02
    COUNT_BOTH  = 0x03
    #system control
    EN_SYS_CLK = 0x00
    EN_EXT_CLK = 0x01
    EN_FUNC    = 0x01
    STOP_FUNC  = 0x00
    IP_RESET   = 0x80
    IP_UNRESET = 0x00
    #exception flag control
    BIT_ERROR   = 0x01
    BIT_OVF     = 0x02
    BIT_TIMEOUT = 0x04


class PLTimerException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class PLTimer(object):
    '''
    MIX_Timer_APL driver function class

    :param    axi4_bus:    instance/string/None,    AXI4LiteBus class intance or device path
                                                    if None, will create emulator
    :example:
               mix_timer = PLTimer('/dev/MIX_Timer_APL_0')
    '''

    def __init__(self, axi4_bus=None):
        if not axi4_bus:
            self.axi4_bus = AXI4LiteBusEmulator("axi4_bus_emulator", PLTimerDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # dev path; create axi4lite bus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, PLTimerDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.dev_name = self.axi4_bus._dev_name

    def reset_sys(self):
        '''
        reset IP before initilization or exception raised

        :example:
                  mix_timer.reset_sys()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_IP_RST, [PLTimerDef.IP_RESET])
        time.sleep(0.001)
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_IP_RST, [PLTimerDef.IP_UNRESET])
        print("reset done!")

    def init_sys(self):
        '''
        initialize the system

        :example:
                  mix_timer.init_sys()
        '''
        # set MODE regiter: IDLE MODE
        self.axi4_bus.write_32bit_inc(PLTimerDef.MODE, [0x00000000])
        # set CFG regiter: extclk_en = 0, Prescaler = 0 (125MHz), trigger = 0
        self.axi4_bus.write_32bit_inc(PLTimerDef.CFG, [0x00000000])
        # set LEN register: gate length = 1s
        self.axi4_bus.write_32bit_inc(PLTimerDef.LEN_L, [0x07735940, 0x00000000] )
        # set SYSCTRL register: IPrst = 0, enable = 0
        self.axi4_bus.write_32bit_inc(PLTimerDef.SYSCTRL, [0x00000000])
        # check default value of all read-only registers
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CCR_L, 8))
        try:
            assert rd_data == 0
        except AssertionError:
            print(self.dev_name, "reset value wrong for CCR!\nTips: try reset again, if this error still occurs, contact IP design team")
            return False
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
        try:
            assert rd_data == 0
        except AssertionError:
            print(self.dev_name, "reset value wrong for CNT!\nTips: try reset again, if this error still occurs, contact IP design team")
            return False
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.STATUS, 4))
        try:
            assert rd_data == 0
        except AssertionError:
            print(self.dev_name, "reset value wrong for STATUS!\nTips: try reset again, if this error still occurs, contact IP design team")
            return False
        return True

    def func_select(self, mode, extclk_en=0, trigger=0, edge_cnt=2048, prescaler=0, gate_len=1000000, extclk_freq=10):
        '''
        select Timer function with configuration parameters

        :param    mode:             int (0 ~ 6)                 funcitonal mode
        :param    extclk_en:        int (0 ~ 1)                 (optional, default 0, using system clock) enable external source as reference clock
        :param    trigger:          int (0 ~ 3)                 (optional, default 0) trigger status, refer to IP spec
        :param    edge_cnt:         int (1 ~ 2048)              (optional, default 2048) edge cnt, only used for mode 6
        :param    prescaler:        int (0 ~ 7)                 (optional, default no prescale) reference clock prescaler control, only valid when extclk_en is set to 0
        :param    gate_len:         long int                    (optional, default 1s) gate length in unit of us
        :param    extclk_freq:      long int                    (optional, default 10MHz) external clock frequency, used for frequency calculation, only valid when extclk_en is set to 1

        :example:
                   mix_timer.func_select(mode=FREQ_M, extclk=0, prescale = 1, gate_len=1000000)  
                   mix_timer.func_select(mode=FREQ_M, extclk=1, gate_len=1000000, extclk_freq = 10)  
        ''' 
        mode_dict = {
            PLTimerDef.IDLE_MODE:   'in idle mode',
            PLTimerDef.FREQ_M:      'in frequency measurement',
            PLTimerDef.PULSE_M_S:   'in single-line pulse measurement',
            PLTimerDef.PULSE_M_D:   'in dual-line pulse measurement',
            PLTimerDef.EDGE_C:      'in edge counting',
            PLTimerDef.PULSE_G:     'in pulse generation',
            PLTimerDef.EDGE_M:      'in edge time measurement',
        }
        # check invalid input
        assert mode in mode_dict, 'wrong mode {}; expecting int (0 - 6)'.format(mode)
        assert 0 <= trigger <= 3, 'trigger out of range, expecting int (0 - 3)'
        assert 1 <= edge_cnt <= 2048, 'egde count out of range, expecting int (1 - 2048)'
        assert 0 <= prescaler <= 7, 'prescaler out of range, expecting int (0 - 7)'
        # set MODE register
        self.axi4_bus.write_8bit_inc(PLTimerDef.MODE, [mode])
        mode_info = mode_dict[mode]
        print(mode_info)
        # calculate LEN register value to be written based on user configuration
        if extclk_en:
            real_len = int(gate_len * extclk_freq)
        elif prescaler == 0:
            real_len = int(gate_len * 125)
        else :
            real_len = int(gate_len * 125 / 2 / prescaler)
        # configure registers according to function input
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_EXCLK_EN, [extclk_en])
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_TRIGGER, [trigger])
        edge_cnt_and_prescaler = edge_cnt << 4 + prescaler
        self.axi4_bus.write_16bit_inc(PLTimerDef.REG_FREQ, [edge_cnt_and_prescaler])
        self.axi4_bus.write_8bit_inc(PLTimerDef.LEN_L, DataOperate.int_2_list(real_len, 8))
        return True

    def enable_proc(self):
        '''
        enable the current funciton mode, start process (used as sub function)

        :example:
                    mix_timer.enable_proc()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.EN_FUNC])
        done = 0
        Exception_flag = 0
        # check Complete register until it is asserted
        while done == 0 : 
            done = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_DONE, 1)[0]
            Exception_flag = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FLAG, 1)[0]
            flag_error = Exception_flag & PLTimerDef.BIT_ERROR
            if flag_error:
                print("in processing, cannot switch mode")
            flag_ovf = Exception_flag & PLTimerDef.BIT_OVF
            flag_timeout = Exception_flag & PLTimerDef.BIT_TIMEOUT
            if (flag_timeout != 0):
                print("timeout exception! please check input signal")
                return False
            if (flag_ovf != 0):
                print("overflow exception! measured signal out of spec")
                return False
        return True

    def get_frequency(self, extclk_freq=10000000):
        '''
        return measured signal frequency in unit of Hz when in correct function mode
        need to implement software timeout when apply the function

        :param      extclk_freq         int             specify the external reference clock frequency in unit of Hz if used

        :example:
                    mix_timer.get_frequency()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if this_mode != PLTimerDef.FREQ_M :
            print("this function is only valid in frequency measurement mode! currently in mode %d") % (this_mode)
            return 0
        print("in frequency measurement\n")
        if self.enable_proc():
            # get register value and calculate frequency
            CCR = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CCR_L, 8))
            CNT = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
            print('CCR=',CCR,'  CNT=', CNT)
            prescaler = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FREQ, 1)[0] % 8
            extclk_en = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_EXCLK_EN, 1)[0]
            freq_res = CCR * ( extclk_freq if extclk_en else ( PLTimerDef.SYS_CLK_FREQ / (1 if prescaler == 0 else prescaler * 2) ) )/ CNT 
            # get result done, clear enable bit
            self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
            return freq_res  
        else: 
            raise PLTimerException(self.dev_name, "overflow or timeout, need to reset IP ... ")

    def get_pulseWidth(self):
        '''
        return measured pulse width in unit of us when in correct function mode
        need to implement software timeout when apply the function

        :example:
                    mix_timer.get_pulseWidth()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if ((this_mode != PLTimerDef.PULSE_M_S) and (this_mode != PLTimerDef.PULSE_M_D) ):
            print("this function is only valid in pulse width measurement mode! currently in mode %d") % (this_mode)
            return 0
        if self.enable_proc():
            CNT = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
            prescaler = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FREQ, 1)[0] % 8
            res = CNT * (1000000.0 / (PLTimerDef.SYS_CLK_FREQ / (1 if prescaler == 0 else prescaler * 2) ) )
            # get result done, clear enable bit
            self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
            return res
        else:
            raise PLTimerException(self.dev_name, "overflow or timeout, need to reset IP ... ")

    def enable_unblocking(self):
        '''
        enable the current funciton mode, start process without checking the done flag 

        :example:
                    mix_timer.enable_unblocking()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.EN_FUNC])
        Exception_flag = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FLAG, 1)[0]
        flag_error = Exception_flag & PLTimerDef.BIT_ERROR
        if flag_error:
            print("in processing, cannot switch mode")
            return False
        return True

    def get_pulseWidth_unblocking(self):
        '''
        return measured pulse width in unit of us when in correct function mode
        need to implement software timeout when apply the function

        :example:
                    mix_timer.get_pulseWidth_unblocking()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if ((this_mode != PLTimerDef.PULSE_M_S) and (this_mode != PLTimerDef.PULSE_M_D) ):
            print("this function is only valid in pulse width measurement mode! currently in mode %d") % (this_mode)
            return 0

        done = 0
        Exception_flag = 0
        # check Complete register until it is asserted
        while done == 0 : 
            done = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_DONE, 1)[0]
            Exception_flag = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FLAG, 1)[0]
            flag_ovf = Exception_flag & PLTimerDef.BIT_OVF
            flag_timeout = Exception_flag & PLTimerDef.BIT_TIMEOUT
            if (flag_timeout != 0):
                raise PLTimerException(self.dev_name, "timeout exception! please check input signal, need to reset IP ... ") 
            if (flag_ovf != 0):
                raise PLTimerException(self.dev_name, "overflow exception! measured signal out of spec, need to reset IP ... ") 
        #Complete flag check done
        CNT = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
        prescaler = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FREQ, 1)[0] % 8
        res = CNT * (1000000.0 / (PLTimerDef.SYS_CLK_FREQ / (1 if prescaler == 0 else prescaler * 2) ) )
        # get result done, clear enable bit
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])

        return res        

    def get_edgeCount(self):
        '''
        return the number of edges when in correct function mode
        need to implement software timeout when apply the function

        :example:
                    mix_timer.get_edgeCount()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if this_mode != PLTimerDef.EDGE_C :
            print("this function is only valid in edge counter mode! currently in mode %d") % (this_mode)
            return 0
        if self.enable_proc() :
            CCR = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CCR_L, 8))
            # get result done, clear enable bit
            self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
            return CCR
        else :
            raise PLTimerException(self.dev_name, "overflow or timeout, need to reset IP ... ")

    def get_delaySignal(self):
        '''
        return 1 if correctly generate the pulse when in correct function mode
        need to implement software timeout when apply the function

        :example:
                    mix_timer.get_delaySignal()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if this_mode != PLTimerDef.PULSE_G :
            print("this function is only valid in pulse generation mode! currently in mode %d") % (this_mode)
            return 0
        if self.enable_proc():
            # get result done, clear enable bit
            self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
            return 1
        else :
            raise PLTimerException(self.dev_name, "overflow or timeout, need to reset IP ... ")
    
    def get_edgeTime(self):
        '''
        return the The period of time beginning from the first edge 
        and stopping at the predefined number of edge when in correct function mode
        in unit of us
        need to implement software timeout when apply the function

        :example:
                    mix_timer.get_edgeTime()
        '''
        this_mode = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        if this_mode != PLTimerDef.EDGE_M :
            print("this function is only valid in edge time measurement mode! currently in mode %d") % (this_mode)
            return 0
        if self.enable_proc():
            CNT = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
            prescaler = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FREQ, 1)[0] % 8
            res = CNT * (1000000.0 / (PLTimerDef.SYS_CLK_FREQ / (1 if prescaler == 0 else prescaler * 2) ) )
            # get result done, clear enable bit
            # self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
            return res
        else:
            raise PLTimerException(self.dev_name, "overflow or timeout, need to reset IP ... ")

    def close(self):
        '''
        Disable timer function class

        :example:
                  mix_timer.close()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_IP_RST, [PLTimerDef.IP_RESET])

    def rd_all_regs(self):
        '''
        print all register values for debug purpose

        :example:
                mix_timer.rd_all_regs()
        '''
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.MODE, 1)[0]
        print("MODE reg value = ", hex(rd_data))
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_EXCLK_EN, 1)[0]
        print("EXCLK_EN reg value = ", hex(rd_data)) 
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_TRIGGER, 1)[0]
        print("Trigger_ctrl reg value = ", hex(rd_data)) 
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FREQ, 1)[0] 
        print("Freq_prescaler reg value = ", hex(rd_data % 8)) 
        rd_data = self.axi4_bus.read_16bit_inc(PLTimerDef.REG_FREQ, 1)[0]
        print("edge_cnt reg value = ", hex(rd_data >> 4)) 
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.LEN_L, 8))
        print("LEN reg value = ", rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_ENABLE, 1)[0]
        print("Enable reg value = ", hex(rd_data))
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_IP_RST, 1)[0]
        print("IP_rst reg value = ", hex(rd_data))
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CCR_L, 8))
        print("CCR reg value = ", rd_data)
        rd_data = DataOperate.list_2_int(self.axi4_bus.read_8bit_inc(PLTimerDef.CNT_L, 8))
        print("CNT reg value = ", rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_FLAG, 1)[0]
        print("Exception_flag reg value = ", hex(rd_data))
        rd_data = self.axi4_bus.read_8bit_inc(PLTimerDef.REG_DONE, 1)[0]
        print("Complete reg value = ", hex(rd_data))
        
    def set_enable(self):
        '''
        enable measurement, only for debug purpose

        :example:
                mix_timer.set_enable()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.EN_FUNC])
        return True

    def clear_enable(self):
        '''
        stop measurement, only for debug purpose

        :example:
                mix_timer.clear_enable()
        '''
        self.axi4_bus.write_8bit_inc(PLTimerDef.REG_ENABLE, [PLTimerDef.STOP_FUNC])
        return True


