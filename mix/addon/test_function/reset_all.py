import re
import time
import os

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class RESET_ALL(object):

    rpc_public_api = ['reset_all','reset']
    def __init__(self, xobjects):
    	self.xobjects = xobjects
        self.io_table = xobjects['io_table']
        self.reset_seq = self.io_table.get_by_netname("IO_Config", table="HWIO_RESET")
        self.reset_all()

    def get_io_device(self, io_num):
        pin_list = divmod(io_num - 1, 16)
        device_name = 'io_exp' + str(pin_list[0] + 1)
        pin_num = pin_list[1]
        device = self.xobjects[device_name]
        return (pin_num,device)

    def reset_all(self):
        '''
        example: reset_reset()
        '''
        if self.reset_seq:
            dir_config_list = self.reset_seq['DIR']
            pin_config_list = self.reset_seq['IO']

            i = 0
            bitdir = []
            for bit, _dir in dir_config_list:
                pin_list = divmod(bit - 1, 16)
                device_name = 'io_exp' + str(pin_list[0] + 1)
                bitdir.append(str(_dir))

                if i%16==15:
                    strBit = ''.join(bitdir[::-1])
                    strBit_H = strBit[:8]
                    strBit_L = strBit[8:]
                    hexBit_H=int(strBit_H,2)
                    hexBit_L=int(strBit_L,2)
                    dev = self.xobjects[device_name]

                    dev.set_pins_dir([hexBit_L,hexBit_H])
                    del bitdir[-16:]
                i +=1

            i = 0
            bitValue = []
            for bit, level in pin_config_list:
                pin_list = divmod(bit - 1, 16)
                device_name = 'io_exp' + str(pin_list[0] + 1)
                bitValue.append(str(level))

                if i%16==15:
                    strBit = ''.join(bitValue[::-1])
                    strBit_H = strBit[:8]
                    strBit_L = strBit[8:]
                    hexBit_H=int(strBit_H,2)
                    hexBit_L=int(strBit_L,2)
                    dev = self.xobjects[device_name]

                    dev.set_ports([hexBit_L,hexBit_H])
                    del bitValue[-16:]
                i +=1
        
    def reset(self):
        i = 0
        bitValue = []
        pin_config_list = self.reset_seq['IO']
        for bit, level in pin_config_list:
            # if int(bit) > 7 and  int(bit) <17:
            #     pin_list = divmod(bit - 1, 16)
            #     device_name = 'io_exp' + str(pin_list[0] + 1)
            #     dev = self.xobjects[device_name]
            #     dev.set_pin(int(bit)-1,0)

            # elif int(bit) >16 and int(bit) <49:
            if int(bit) >=1 and int(bit) <=48:    
                # if int(bit) == 41 or int(bit) == 27 or int(bit) == 28:
                #     level = 1
                pin_list = divmod(bit - 1, 16)
                device_name = 'io_exp' + str(pin_list[0] + 1)
                bitValue.append(str(level))

                if i%16==15:
                    strBit = ''.join(bitValue[::-1])
                    strBit_H = strBit[:8]
                    strBit_L = strBit[8:]
                    hexBit_H=int(strBit_H,2)
                    hexBit_L=int(strBit_L,2)
                    dev = self.xobjects[device_name]

                    dev.set_ports([hexBit_L,hexBit_H])
                    del bitValue[-16:]
            i +=1

 
        return PASS_MASK

