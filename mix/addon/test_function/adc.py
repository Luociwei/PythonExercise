__author__ = 'Suncode_D@SunCode'
__version__ = '0.1'

import re
import time
import os

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class adc(object):

    rpc_public_api = ['read_volt']
    def __init__(self, xobjects):
        self.adc = xobjects['ltc2309']

    def read_volt(self,channel):
        '''
        example: read_volt(CH0)
        '''
        ret = self.adc.read_volt(channel)
        if int(ret) >= 0:
            return str(ret)+' mv '+PASS_MASK
        else:
            return str(ret)+' mv '+FAIL_MASK

