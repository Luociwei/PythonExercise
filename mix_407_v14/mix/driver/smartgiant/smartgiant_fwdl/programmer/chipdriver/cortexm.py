#-*- coding: UTF-8 -*-
__author__ = 'jk'
'''cortexm program driver
'''

import sys
import time
import threading
import copy
from math import sqrt

class Cortexm():
    def __init__(self):
        self.swd_driver = None
        self.cortexm_ap_select = 0x00
        logger.info("create Cortexm")

#     @abstract
    def create_instance(self,dev_path,what_chip):
        "in :                    \
           dev_path:string"
        self.swd_driver = Axi4SwdCore(dev_path)
        logger.info("create Axi4SwdCore in cortexm")
        return True,"NULL",""
    
    def destroy_instance(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        del  self.swd_driver
        self.swd_driver = None
        return True,"NULL",""
    
    def instance_initial(self,freqency_hz,instance_sequence = 0):
        "in:\
            frequency_hz:unsigned int\
            instance_sequence:unsigned int"
        logger.info("create instance_initial in cortexm")
        if self.swd_driver != None:
            self.swd_driver.disable()
            self.swd_driver.enable()
        else:
            return False,"JSON_STRING","function param input error"

        self.swd_driver.swd_freq_set(int(freqency_hz))
        return True,"NULL","executing normal"

    def set_frequency(self,freqency_hz,instance_sequence = 0):
        "in:\
            frequency_hz:unsigned int\
            instance_sequence:unsigned int"
        logger.info("create set_frequency in cortexm")
        if self.swd_driver != None:
            self.swd_driver.swd_freq_set(int(freqency_hz))
        else:
            return False,"JSON_STRING","function param input error"

        return True,"NULL","executing normal"

    def get_frequency(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        return True,"NULL","executing normal"

    def dut_initial(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        dp_id = 0
        ap_id = 0
        logger.info("create dut_initial in cortexm")
        swd_switch_time_sequence_group =  [0xFF for i in range(0,30)] #30*8 bit = 240 bit
        swd_switch_time_sequence_group[8] = 0x9E;
        swd_switch_time_sequence_group[9] = 0xE7;
        swd_switch_time_sequence_group[18] = 0xB6;
        swd_switch_time_sequence_group[19] = 0xED;
        swd_switch_time_sequence_group[28] = 0x0;
        swd_switch_time_sequence_group[29] = 0x0;

        params = {}
        params["instance_sequence"] = instance_sequence
        
        response = self.rpc_client_node.call("DutInitial",**params)
        # pring(response)
        if response["state"] < 0:
#             logger.info(response["return"])
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

        '''

        '''
        #reset dut
        self.swd_driver.swd_rst_pin_ctrl("H")
        time.sleep(0.001)#1ms
        self.swd_driver.swd_rst_pin_ctrl("L")
        time.sleep(0.001)#1ms
        self.swd_driver.swd_rst_pin_ctrl("H")
        #switch sequence
        self.swd_driver.swd_switch_timing_gen(swd_switch_time_sequence_group)
        #read dp id
        ret = self.__DapOperate(0xA5)
        dp_id = ret[1]
        if ret[0] != True:
            return False,"NULL",ret[2]

        #clear abort
        ret = self.__DapOperate(0x81,0x1E)
        #initial ap register
        #systen power on
        ret = self.__DapOperate(0xA9,0x50000000)
        #delay
        time.sleep(0.0005)#1ms
        #read ap id
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0xF0&0xF0))
        ret = self.__DapOperate(0x9F)
        ap_id = ret[1]
        #ap csw mode
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0x00&0xF0))
        ret = self.__DapOperate(0xA3,0x23000002)
        #read room table address
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0xF0&0xF0))
        ret = self.__DapOperate(0xB7)
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0x00&0xF0))
        #halt system
        ret = self.RegWrite(0xE000EDF0,0xA05F0003)
        #read system state
        ret= self.RegRead(0xE000EDF0)

        return True,"JSON_ARRAY",[dp_id,ap_id]


    def dut_exit(self,instance_sequence = 0):
        "in:\
            instance_sequence:unsigned int"
        logger.info("create dut_exit in cortexm")
        #reset dut
        self.swd_driver.swd_rst_pin_ctrl("H")
        time.sleep(0.001)#1ms
        self.swd_driver.swd_rst_pin_ctrl("L")
        time.sleep(0.001)#1ms
        self.swd_driver.swd_rst_pin_ctrl("H")

        return True,"NULL",""

    def __DapOperate(self,req,write_data = 0):
        '''
        in:
        req:    swd require data 8bit
        write_data:     wrtie 32bit data
        out:
        return T/F,read data,state_str
        '''
        state_str = "executing normal"
        state = True
        swd_wr_data = [write_data&0xFF,(write_data>>8)&0xFF,(write_data>>16)&0xFF,(write_data>>24)&0xFF]
        swd_rd_data = []
        read_data = 0
        ack_data = 0x00

        if (req|0x04) != 0x00:#read
            swd_rd_data = self.swd_driver.swd_rd_operate(self,req)
            ack_data = swd_rd_data[4]
            read_data = swd_rd_data[0]|(swd_rd_data[1]<<8)|(swd_rd_data[2]<<16)|(swd_rd_data[3]<<24)
        else:#write
            ack_data = self.swd_driver.swd_wr_operate(self,req,swd_wr_data)

        #read ack data
        ack_data &= 0x07
        if ack_data == 0x01:#success
            state_str = "executing normal"
            state = True
        elif ack_data == 0x02:#wait
            state_str = "executing busy in protocol response"
            state = False
        elif ack_data == 0x04:#protocol err
            state_str = "executing Fault in protocol response"
            state = False
        else:#hardware error
            state_str = "executing Fault in hardware response"
            state = False

        return state,read_data,state_str

    def RegRead(self,address):
        '''
        in:
        address:    read address
        out:
        return T/F,read data,statestr 
        '''

        #dp select
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0x004&0xf0))
        if ret[0] == False:
            return ret
        #ap address
        ret = self.__DapOperate(0x8B,address)
        if ret[0] == False:
            return ret
        #read ap data register
        ret = self.__DapOperate(0x9F)
        if ret[0] == False:
            return ret
        #read ap data register
        ret = self.__DapOperate(0x9F)
        if ret[0] == False:
            return ret

        return ret


    def RegWrite(self,address,write_data):
        '''
        in:
        req:    swd require data
        out:
        return T/F,read data,state 
        '''
        #dp select
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0x004&0xf0))
        if ret[0] == False:
            return ret
        #ap address
        ret = self.__DapOperate(0x8B,address)
        if ret[0] == False:
            return ret
        #write ap data register
        ret = self.__DapOperate(0xBB,write_data)
        if ret[0] == False:
            return ret
        return ret
        
    def ApRegWrite(self,req,ap_reg,write_data):
        #select
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(ap_reg&0xf0))
        if ret[0] == False:
            return ret

        ret = self.__DapOperate(req,)

    def ApRegRead(self):
        #select
        ret = self.__DapOperate(0xB1,self.cortexm_ap_select|(0x004&0xf0))
        if ret[0] == False:
            return ret
