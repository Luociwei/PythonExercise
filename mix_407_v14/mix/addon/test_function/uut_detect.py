import os
import time



PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class UUT_DETECT(object):

    rpc_public_api = ['read_Volt']
    def __init__(self, xobjects):
        self.adc128 = xobjects['io_exp2']
        
    def read_Volt(self):
    	'''
    	read_Volt()
    	
    	'''
        return self.adc128.get_pin(0)
