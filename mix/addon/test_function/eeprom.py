import re
import time
import os

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class eeprom(object):

    rpc_public_api = ['read_string','write_string']
    def __init__(self, xobjects):
        self.eeprom_device = xobjects['sib_eeprom']
        # self.dac.set_reference('INTERNAL')
        # self.dac.reset()
        # self.dac.select_work_mode("NORMAL")

    def read_string(self, addr,length):
        """
        :param address: int(0-1024),   Write datas from this address
        :param length: int,   Read datas length

        :return: str, Return Data
        """
        addr  = str(addr)
        addr = int(addr,16) if addr.find('0x') or addr.find('0X') else int(addr)
        result = self.eeprom_device.read(int(addr),int(length))
        new_string = []
        for c in result:
            if c !=255:
                new_string.append(str(chr(c)))
        if new_string:
            s=''.join(new_string)
            return "ACK(\"" + str(s)+"\""+";DONE)"
        else:
            return FAIL_MASK
    def write_string(self,addr,datastring):
        addr  = str(addr)
        addr = int(addr,16) if addr.find('0x') or addr.find('0X') else int(addr)
        data_list = []
        for c in datastring:
            data_list.append(int(str(ord(c))))
        self.eeprom_device.write(int(addr), data_list)
        return PASS_MASK 

