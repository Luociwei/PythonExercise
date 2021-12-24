import re
import time
import os

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class BATT(object):

    rpc_public_api = ['volt_set']
    def __init__(self, xobjects):
        self.dac = xobjects['batt_dac']
        # self.dac.set_reference('INTERNAL')
        # self.dac.reset()
        # self.dac.select_work_mode("NORMAL")

    def volt_set(self, volt):
        '''
        example: volt_output()
        '''
        assert int(volt) < 4500
        #assert isinstance(volt, (int, float)) and volt >= 0
        self.dac.output_volt_dc(int(volt))
        return PASS_MASK
