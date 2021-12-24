#-*- coding: UTF-8 -*-
import sys
import os
import re
from ..dfucommon import dfu_common
#-----from rpc server-----
from ..chipprog.chipprog import ChipProg
from ..chipprog.cortexmprog import CortexMProg
from ..chipprog.psoc4prog import Psoc4Prog
from ..chipprog.otpprog import OtpProg
from ..chipprog.nrf5xbleprog import Nrf5XProg
from ..chipprog.spiflashprog import SpiFlash
from ..chipprog.stm32prog import Stm32Prog
#-----from python layer-----
from ..chipprog.hearstprog import HearstProg

import time

def _return_to_str(return_from_chip_prog):#[0] true/false,[1] type,[2] return
    ret_str = ""
    if dfu_common.return_type("JSON_STRING") == dfu_common.return_type(return_from_chip_prog[1]):
        ret_str += return_from_chip_prog[2]+"\r\n"
    elif dfu_common.return_type("JSON_BOOLEAN") == dfu_common.return_type(return_from_chip_prog[1]):
        ret_str += "0x%x"%return_from_chip_prog[2]+"\r\n"
    elif dfu_common.return_type("JSON_INTEGER") == dfu_common.return_type(return_from_chip_prog[1]):
        ret_str += "0x%x"%return_from_chip_prog[2]+"\r\n"
    elif dfu_common.return_type("JSON_REAL") == dfu_common.return_type(return_from_chip_prog[1]):
        ret_str += str(return_from_chip_prog[2])+"\r\n"
    elif dfu_common.return_type("JSON_ARRAY") == dfu_common.return_type(return_from_chip_prog[1]):
        idgroup = ""
        for val in return_from_chip_prog[2]:
            # #pring("0x%x"%(val))
            idgroup += "0x%x"%(val)
            idgroup += ","
        ret_str += idgroup[:len(idgroup)-1]+".\r\n"
    elif dfu_common.return_type("NULL") == dfu_common.return_type(return_from_chip_prog[1]):
        ret_str += str(return_from_chip_prog[2])
    else:
        ret_str += "not this return type.\r\n"
    return ret_str


class ProgApp():
    def __init__(self,dfu_rpc_node = None):
        self.prog_instance = None
        self.dfu_rpc_node = dfu_rpc_node
        self.arch_type = ""
        self.target_chip_type = ""
        pass
    
    def list_support_target(self):
        support_chip = ""
        if self.dfu_rpc_node != None: 
            #from the rpc server get support
            arch_type = dfu_common.get_chip_arch_type_support(self.dfu_rpc_node)
            for arch_keys in arch_type.keys():
                support_chip += arch_keys+":"
                chip_type = dfu_common.get_chip_type_support(self.dfu_rpc_node,arch_type[arch_keys])
                for chip_keys in chip_type.keys():
                    support_chip += chip_keys+" "
                pass
        #from the python layer get support
        support_chip += HearstProg.chip_type_name()+","
        support_chip += Iktara.chip_type_name()
        support_chip += "\r\n"
        #print(support_chip)
        return True,support_chip

    def distinguish_chip_architecture(self,what_chip,arch_type):
        if self.dfu_rpc_node != None:
            arch_type = dfu_common.get_chip_arch_type_support(self.dfu_rpc_node)
            #if rpc server support the chip type
            for arch_keys in arch_type.keys():
                chip_type = dfu_common.get_chip_type_support(self.dfu_rpc_node,arch_type[arch_keys]) 
                if what_chip in chip_type.keys():
                    if arch_keys == arch_type:
                        self.target_chip_type = arch_keys
                        return True
                    else:
                        return False

        #if other instance support the chip type
        arch_keys = None
        if (what_chip == "hearst") and self.dfu_rpc_node != None:
            self.prog_instance = HearstProg(self.dfu_rpc_node)
            arch_keys = "cortexm"
            self.target_chip_type = arch_keys
            if arch_keys == arch_type:
                return True
            else:
                return False
        elif what_chip == "iktara":
            self.prog_instance = Iktara()
            arch_keys = "cortexm"
            self.target_chip_type = arch_keys
            if arch_keys == arch_type:
                return True
            else:
                return False
        return False

    def set_target_id_group(self,match_id_group):
        ret = ChipProg.config_match_id(self.dfu_rpc_node,match_id_group)
        ret_str = _return_to_str(ret)
        if ret[0] == False:
            return False,ret_str
        return True,ret_str
    
    def create_target(self,dev_path,what_chip):
        ret_str = "\r\n------------------------------------\r\n"
        ret_str += "Operating "
        #traverse
        #if rpc server support the chip type
        if self.dfu_rpc_node != None: 
            arch_type = dfu_common.get_chip_arch_type_support(self.dfu_rpc_node)
            for arch_keys in arch_type.keys():
                chip_type = dfu_common.get_chip_type_support(self.dfu_rpc_node,arch_type[arch_keys]) 
                if what_chip in chip_type.keys():
                    if arch_keys == "stm32":
                        self.prog_instance = Stm32Prog(self.dfu_rpc_node)
                    elif arch_keys == "cortexm":
                         self.prog_instance = CortexMProg(self.dfu_rpc_node)
                    elif arch_keys == "psoc4":
                        self.prog_instance = Psoc4Prog(self.dfu_rpc_node)
                    elif arch_keys == "nrf5xble":
                        self.prog_instance = Nrf5XProg(self.dfu_rpc_node)
                    elif arch_keys == "spiflash":
                        self.arch_type = "spiflash"
                        self.prog_instance = SpiFlash(self.dfu_rpc_node)
                    elif arch_keys == "otp":
                        self.arch_type = "otp"
                        self.prog_instance = OtpProg(self.dfu_rpc_node)
                    break
        #
        #if other instance support the chip type
        if self.prog_instance == None:
            if what_chip == "hearst":
                if self.dfu_rpc_node != None: 
                    self.prog_instance = HearstProg(self.dfu_rpc_node)
                    arch_keys = "cortexm"
                    self.arch_type = "cortexm"
                else:
                    ret_str += arch_keys+":"+what_chip+"........the rpc node is not exist !\r\n"
                    return False,ret_str
            elif what_chip == "iktara":
                self.prog_instance = Iktara()
                arch_keys = "cortexm"
                self.arch_type = "cortexm"
            else:
                ret_str += "error ,do not support this device ."
                return False,ret_str
            ret_str += arch_keys+":"+what_chip+"........\r\n"

        #create instance
        ret_str += "create target.....\r\n"
        ret = self.prog_instance.create_instance(dev_path,what_chip)#[0] true/false,[1] type,[2] return
        # ret_str += _return_to_str(ret)
        if ret[0] == False:
            self.destroy_target()
            return False,ret_str

        return True,ret_str
    
    def target_driver_initial(self,frequency_hz):
        #instance initial
        ret_str = "driver initial \r\n"
        ret = self.prog_instance.instance_initial(frequency_hz)
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            self.destroy_target()
            return False,ret_str
        return True,ret_str

    def target_erase(self,target_address=None,size=None,target_file_name= None):
        ret_str = "erasing target ....\r\n"
        if (target_address !=None) and (size != None):
            ret_str += "erasing target address is 0x%08x"%(target_address)+".\r\n"
            ret_str += "erasing target size is 0x%08x"%(size)+".\r\n"
        elif (target_address !=None):
            ret_str += "erasing target address is 0x%08x"%(target_address)+".\r\n"

        ret = self.prog_instance.dut_storage_erase(0,target_address,size,target_file_name)
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        ret_str += "erasing target successfully\r\n"
        return True,ret_str
    
    def __target_programming_only(self,target_file_name,size,target_address ,file_offset = 0):        
        ret_str = "programming target .........\r\n"
        ret = self.prog_instance.dut_storage_infusing(target_file_name,target_address,file_offset,size)
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        ret_str += "programming target successfully\r\n"
        return True,ret_str
    
    def __target_checkout(self,target_file_name,size,target_address ,file_offset = 0):
        ret_str = "verify target .........\r\n"
        ret = self.prog_instance.dut_storage_checkout(target_file_name,target_address,file_offset,size)
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        ret_str += "verify target successfully\r\n"
        ret_str += "program ok\r\n"
        return True,ret_str
    
    def __target_initial(self):
        ret_str = "initial target ....\r\n"
        ret_str += "id:"
        ret = self.prog_instance.dut_initial()
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        return True,ret_str
    


    def target_initial(self):
        ret_str = ""
        ret = self.__target_initial()
        ret_str += ret[1]
        if ret[0] == False:
            return False,ret_str

        return True,ret_str
    
    # def target_erase(self,target_address=None,size=None):
    #     ret_str = ""
    #     # ret = self.__target_initial()
    #     # ret_str += ret[1]
    #     # if ret[0] == False:
    #         # return False,ret_str

    #     ret = self.__target_erase(target_address,size)
    #     ret_str += ret[1]
    #     if ret[0] == False:
    #         return False,ret_str
        
    #     return True,ret_str
        
    def target_programming(self,target_file_name,size,target_address,file_offset = 0,erase_match_file = 0):
        ret_str = "target file is "+target_file_name+".\r\n"
        ret_str += "target address is 0x%08x"%(target_address)+".\r\n"
        ret_str += "load file address is 0x%08x"%(int(file_offset))+".\r\n"
        ret_str += "load size is %d"%(size)+".\r\n"
        
        # ret = self.__target_initial()
        # ret_str += ret[1] 
        # if ret[0] == False:
            # return False,ret_str
        if erase_match_file != 0:
            ret = self.target_erase(target_address,size)
        else:
            ret = self.target_erase()# 
        ret_str += ret[1] 
        if ret[0] == False:
            return False,ret_str
        
        ret = self.__target_programming_only(target_file_name,size,target_address,file_offset)
        ret_str += ret[1] 
        if ret[0] == False:
            return False,ret_str
        if self.arch_type != "spiflash":
            ret = self.__target_checkout(target_file_name,size,target_address,file_offset)
            ret_str += ret[1] 
            if ret[0] == False:
                return False,ret_str
        else:
            ret_str += "verify target .........\r\n"
            ret_str += "verify target successfully\r\n"
            ret_str += "program ok\r\n"
        
        return True,ret_str
            
    def target_programming_only(self,target_file_name,size,target_address ,file_offset = 0):
        ret_str = "target file is "+target_file_name+".\r\n"
        ret_str += "target address is 0x%08x"%(int(target_address))+".\r\n"
        ret_str += "load file address is 0x%08x"%(int(file_offset))+".\r\n"
        ret_str += "load size is %d"%(size)+".\r\n"
        
        # ret = self.__target_initial()
        # ret_str += ret[1] 
        # if ret[0] == False:
            # return False,ret_str
        
        ret = self.__target_programming_only(target_file_name,size,target_address,file_offset)
        ret_str += ret[1] 
        if ret[0] == False:
            return False,ret_str
        
        if self.arch_type != "spiflash":
            ret = self.__target_checkout(target_file_name,size,target_address,file_offset)
            ret_str += ret[1] 
            if ret[0] == False:
                return False,ret_str
        else:
            ret_str += "verify target .........\r\n"
            ret_str += "verify target successfully\r\n"
            ret_str += "program ok\r\n"

        return True,ret_str
        

    def target_programming_auto(self,target_file_name,size,target_address ,file_offset = 0):
        ret_str = "target file is "+target_file_name+".\r\n"
        ret_str += "target address is 0x%08x"%(int(target_address))+".\r\n"
        ret_str += "load file address is 0x%08x"%(int(file_offset))+".\r\n"
        ret_str += "load size is %d"%(size)+".\r\n"
        
        # ret = self.__target_initial()
        # ret_str += ret[1] 
        # if ret[0] == False:
            # return False,ret_str

        ret_str += "programming target .........\r\n"
        ret = self.prog_instance.dut_storage_auto_infusing(target_file_name,target_address,file_offset,size)
        ret_str += _return_to_str(ret)
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        ret_str += "programming target successfully\r\n"
        
        # if self.arch_type != "spiflash":
        #     ret = self.__target_checkout(target_file_name,size,target_address,file_offset)
        #     ret_str += ret[1] 
        #     if ret[0] == False:
        #         return False,ret_str
        # else:
        ret_str += "verify target .........\r\n"
        ret_str += "verify target successfully\r\n"
        ret_str += "target file "+re.split(r'/',target_file_name)[-1] + " program ok\r\n"

        return True,ret_str


    def target_checkout(self,target_file_name,size,target_address,file_offset = 0):
        ret_str = "target file is "+target_file_name+".\r\n"
        ret_str += "target address is 0x%08x"%(int(target_address))+".\r\n"
        ret_str += "load file address is 0x%08x"%(int(file_offset))+".\r\n"
        ret_str += "load size is %d"%(size)+".\r\n"
                
        # ret = self.__target_initial()
        # ret_str += ret[1] 
        # if ret[0] == False:
            # return False,ret_str
        
        ret = self.__target_checkout(target_file_name,size,target_address,file_offset)
        ret_str += ret[1] 
        if ret[0] == False:

            return False,ret_str

        return True,ret_str
    
    def read_target_storage(self,target_file_name,read_size,target_address):
        
        ret_str = "target file is "+target_file_name+".\r\n"
        ret_str += "target address is 0x%08x"%(int(target_address))+".\r\n"
        ret_str += "load size is %d"%(read_size)+".\r\n"
        # ret = self.__target_initial()
        # ret_str += ret[1] 
        # if ret[0] == False:
            # return False,ret_str
        
        ret_str += "roading target .........\r\n"        
        ret = self.prog_instance.dut_storage_reading(target_file_name,target_address,read_size)
        ret_str += _return_to_str(ret) 
        if ret[0] == False:
            return False,ret_str
        ret_str += "road target done\r\n"
        return True,ret_str
        
    def release_target(self):
        # ret_str = "release target\r\n"
        ret_str =""
        ret = self.prog_instance.dut_exit()
        ret_str += _return_to_str(ret) 
        if ret[0] == False:
            # self.destroy_target()
            return False,ret_str
        # ret_str += "finish target release\r\n"
        return True,ret_str
    
    def destroy_target(self):
        # ret_str = "destruct ......\r\n"
        ret_str =""
        ret = self.prog_instance.destroy_instance()
        if ret[0] == False:
            ret_str += "target destroy error"
            return False,ret_str
        # ret_str = "instance destruct ."
        return True,ret_str #ret[1]










