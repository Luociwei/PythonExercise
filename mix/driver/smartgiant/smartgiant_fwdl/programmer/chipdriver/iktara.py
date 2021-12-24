#-*- coding: UTF-8 -*-
__author__ = 'jk'
'''cortexm program driver
'''

import sys
import time
import threading
import copy
from math import sqrt
from cortexm import Cortexm


class Iktara(Cortexm):
    def __init__(self):
        Cortexm.__init__(self)

    @staticmethod
    def chip_type_name(self):
        return "iktara"

    def __wait_for_status(self,state,timeout):
        ret= self.RegRead(0xf0000a18)

        while (((ret[1]&state) == 0)and(timeout>0)):
            ret= self.RegRead(0xf0000a18)
            time.sleep(0.0005)
            timeout =timeout -1
        if timeout == 0:
            #error
            return False,"NULL","waiting timeout in operating DUT"
        return True,"NULL","executing normal"


    def __program_flash_setting(self):
        ret = self.RegWrite(0xf0000a30,0x01)
        ret= self.RegRead(0xf0000a30)
        ret = self.RegWrite(0xf0000a04,0x20)
        ret = self.RegWrite(0xf0000a04,0x28)
        ret= self.RegRead(0xf0000a18)

        ret = self.RegWrite(0xf0000a08,0x0)#a
        ret = self.RegWrite(0xf0000a0c,0x0)#b
        ret = self.RegWrite(0xf0000a10,0xf)#c
        ret = self.RegWrite(0xf0000a14,0x00000102)#d
        ret = self.__wait_for_status(0x2,2000)#e wait until bit 1 is set
        if ret[0] != True:
            return ret
        ret = self.RegRead(0xf0000a18)#check status is 0xB8000002
        # if ret[1] != 0xb8000802:
        #     return False,"NULL","DUT illegal operation occurs"
        ret = self.RegWrite(0xf0000a10,0x4)#f
        ret = self.RegWrite(0xf0000a14,0x0102)#g
        ret = self.__wait_for_status(0x2,2000)#h wait until bit 1 is set
        if ret[0] != True:
            return ret
        ret = self.RegRead(0xf0000a18)#check status is 0xB8000002
        # if ret[1] != 0xb8000802:
        #     return False,"NULL","DUT illegal operation occurs"
        ret = self.RegWrite(0xf0000a10,0x8)#i
        ret = self.RegWrite(0xf0000a14,0x0102)#j
        ret = self.__wait_for_status(0x2,2000)#k wait until bit 1 is set
        if ret[0] != True:
            return ret
        ret = self.RegRead(0xf0000a18)#check status is 0xB8000002
        # if ret[1] != 0xb8000802:
        #     return False,"NULL","DUT illegal operation occurs"
        ret = self.RegWrite(0xf0000a10,0xd)#l
        ret = self.RegWrite(0xf0000a14,0x0102)#m
        ret = self.__wait_for_status(0x3,2000)#n wait until bit 1 is set
        if ret[0] != True:
            return ret
        ret = self.RegRead(0xf0000a18)#o check status is 0xB8000002
        if (ret[1]&0x04) == 0:
            return False,"NULL","DUT illegal operation occurs"
        return True,"NULL","executing normal"

    def __program_flash_exit(self):
        ret = self.RegWrite(0xf0000a14,0x0103)#g
        ret = self.__wait_for_status(0x2,2000)#h wait until bit 1 is set
        if ret[0] != True:
            return ret
        ret = self.RegRead(0xf0000a18)#check status is 0xB8000002
        ret = self.RegWrite(0xf0000a04,0x20)#l
        ret = self.RegWrite(0xf0000a30,0x0)#m
        return True,"NULL","executing normal"


    def dut_storage_infusing(self,target_file_name,target_address,file_offset,size,instance_sequence = 0):
        "in:\
        target_file_name:str,the file path\
        target_address: unsigned int,the DUT target infusing address\
        file_offset:unsigned int,loading the firmware file start address\
        size:unsigned int,program size\
        instance_sequence:unsigned int\
        "
        nOtpStartAddr = 0x00200000
        nOtpEndAddr = 0x00202000

        if ((target_address%8 )!=0) or ((size%8 )!=0):
            return False,"NULL","file is not exist or not suitable"


        with open(target_file_name,'rb') as firmware_file:
            firmware_file.seek(0,0)
            #program setting
            ret = self.__program_flash_setting()
            #loop
            loaded_byte = 0
            while loaded_byte < size:
                nRow = (target_address - 0x00200000 + loaded_byte)/8
                ret = self.RegWrite(0xf0000a08,nRow)
                read_byte_list = firmware_file.read(4)
                write_data = read_byte_list[0]|(read_byte_list[1]<<8)|(read_byte_list[2]<<16)|(read_byte_list[3]<<24)
                ret = self.RegWrite(0xf0000a10,write_data)

                loaded_byte += 4
                if loaded_byte >= size -1:
                    break
                read_byte_list = firmware_file.read(4)
                write_data = read_byte_list[0]|(read_byte_list[1]<<8)|(read_byte_list[2]<<16)|(read_byte_list[3]<<24)
                ret = self.RegWrite(0xf0000a0c,write_data)

                loaded_byte += 4
                ret = self.RegWrite(0xf0000a14,0x113)
                ret = self.__wait_for_status(0x2,2000)#n wait until bit 1 is set
                if ret[0] != True:
                    firmware_file.close()
                    return ret
            ret = self.__program_flash_exit()

        firmware_file.close()

        return True,"NULL",""


    def dut_storage_checkout(self,target_file_name,target_address,file_offset,size,instance_sequence = 0):
        "in:\
        target_file_name:str,the file path\
        target_address: unsigned int,the DUT target checkout address\
        file_offset:unsigned int,loading the firmware file start address\
        size:unsigned int,program size\
        instance_sequence:unsigned int\
        "
        nOtpStartAddr = 0x00200000
        nOtpEndAddr = 0x00202000
        nReadFileWord1 = 0
        nReadFileWord2 = 0
        nReadFileWord3 = 0
        nReadFileByteList1 = []
        nReadFileByteList2 = []
        nReadDutWord1 = 0
        nReadDutWord2 = 0
        nReadDutWord3 = 0
        nTimeOut = 2000

        if ((target_address%8 )!=0) or ((size%8 )!=0):
            return False,"NULL","file is not exist or not suitable"

        ret = self.RegWrite(0xf0000a04,0x30)
        ret = self.RegRead(0xf0000a04)
        #check OTPSTATUS is 0xB8000002
        ret = self.RegRead(0xf0000a18)
        status = ret[1]
        nTimeCnt = 0
        while status != 0x68000802:
            time.sleep(0.0001)
            ret = self.RegRead(0xf0000a18)
            status = ret[1]
            nTimeCnt += 1
            if nTimeCnt>=nTimeOut:
                return False,"NULL","waiting timeout in operating DUT"

        with open(target_file_name,'rb') as firmware_file:
            firmware_file.seek(0,0)

            #loop
            loaded_byte = 0
            while loaded_byte < size:
                nRow = (target_address - nOtpStartAddr + loaded_byte)/8
                nReadFileByteList1 = firmware_file.read(4)
                nReadFileWord1 = nReadFileByteList1[0]|(nReadFileByteList1[1]<<8)|(nReadFileByteList1[2]<<16)|(nReadFileByteList1[3]<<24)
                nReadFileByteList2 = firmware_file.read(4)
                nReadFileWord2 = nReadFileByteList2[0]|(nReadFileByteList2[1]<<8)|(nReadFileByteList2[2]<<16)|(nReadFileByteList2[3]<<24)
                ret = self.RegWrite(0xf0000a08,nRow)
                ret = self.RegWrite(0xf0000a14,0x0112)
                ret = self.__wait_for_status(0x2,2000)#n wait until bit 1 is set
                if ret[0] != True:
                    firmware_file.close()
                    return ret
                ret = self.RegWrite(0xf0000a18)
                status = ret[1]
                ret = self.RegRead(0xf0000a24)
                nReadDutWord2 = ret[1]
                ret = self.RegRead(0xf0000a20)
                nReadDutWord1 = ret[1]
                ret = self.RegRead(0xf0000a28)
                nReadDutWord3 = ret[1]
                if (nReadFileWord1 != nReadDutWord2) or (nReadFileWord2 != nReadDutWord1):
                    firmware_file.close()
                    return False,"NULL","fwdl verify error"
                loaded_byte += 8

        firmware_file.close()
        ret = self.RegWrite(0xf0000a14,0x0111)
        ret = self.RegWrite(0xf0000a04,0x20)

        return True,"NULL",""

        
    def dut_storage_reading(self,target_file_name,target_address,size,instance_sequence = 0):
        "in:\
            target_file_name:str,the file path\
            target_address: unsigned int,the DUT target checkout address\
            size:unsigned int,program size\
            instance_sequence:unsigned int\
            "
        return True,"NULL",""

    def dut_storage_erase(self,instance_sequence,target_address= None,size= None):
        "in:\
            instance_sequence:unsigned int\
            "
        return True,"NULL",""
