import re
import threading
import multiprocessing
import time
from mix.driver.core.ic.cat9555 import CAT9555

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"



class FixtureStatus:

    ACTION = {
        'in'    : [1, 0, 0],
        'out'   : [0, 1, 0],
        'down'  : [1, 0 ,1],
        'up'    : [1, 0, 0],
        'idle'  : [0, 0, 0]
    }
    STATE = {
        '0101'  : 'in',
        '1001'  : 'out',
        '0110'  : 'down',
        '0111'  : 'idle',
        '1101'  : 'idleup',
        '1111'  : 'noaction'
    }

class FixtureActException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class FixtureAction(object):

    # rpc_public_api = ['get_status','In','Out','Up','Down','release','press','Idle','get_key_status']

    def __init__(self,start_left_key=None,start_right_key=None,reset_key=None,io_exp=None):
        self.start_left_key = start_left_key
        self.start_right_key = start_right_key
        self.reset_key = reset_key
        self.io_exp = io_exp
        # [133, 132, 131, 134]
        self.status_list = [0, 1, 2, 3]
        # [135,136,144]
        self.action_list = [5, 6, 4]
        self.control = True
        self.first_flag = 0


    def _get(self):
        state = ''
        for bit_num in self.status_list:
            ret = self.io_exp.get_pin(bit_num)
            state += str(ret)
        return state
    
    def _set(self,state):
        for i in range(3):
            pin = self.action_list[i]
            val = FixtureStatus.ACTION[state][i]
            if pin == 6 and val== 1:
                time.sleep(0.2)
            self.io_exp.set_pin(pin,val)
            time.sleep(0.05)
        return PASS_MASK

    def get_status(self):
        return FixtureStatus.STATE[self._get()]

    def get_key_status(self):
        left_ret = self.start_left_key.get_level()
        rigth_ret = self.start_right_key.get_level()
        retreset = self.reset_key.get_level()
        result = str(left_ret)+str(rigth_ret)+str(retreset)
        return result

    def get_start_left_key_status(self):
        ret = self.start_left_key.get_level()
        return ret

    def get_start_rigth_key_status(self):
        ret = self.start_right_key.get_level()
        return ret

    def get_reset_key_status(self):
        ret = self.reset_key.get_level()
        return ret

    def In(self,timeout=4000):
        self._set('in')
        # return PASS_MASK

    def Out(self,timeout=4000):
        self._set('out')
        # return PASS_MASK

    def Up(self,timeout=4000):
        status = self.get_status()
        self._set('up')
        # return PASS_MASK

    def Down(self,timeout=4000):
        status = self.get_status()
        self._set('down')
        # return PASS_MASK

    def Idle(self,timeout=4000):
        self._set('idle')
        return PASS_MASK

    def release(self,timeout=5000):
        status = self.get_status()
        if status == 'down':
            self.Idle(timeout)
        while True:
            time.sleep(0.08)
            status = self.get_status()          
            if status=='in':
                time.sleep(1)
                self.Out(timeout)
                break
            # time.sleep(0.3)
        return PASS_MASK

    def press(self,timeout=5000):
        status = self.get_status()
        if status == 'down':
            return PASS_MASK
        self.In(timeout)
        # time.sleep(0.5)
        while self.control:
            time.sleep(0.08)
            status = self.get_status()
            if status == 'in':
                time.sleep(0.8)
                break
        self.Down(timeout)

        start_time= time.time()
        while True:
            time.sleep(0.08)
            status = self.get_status()
            if time.time() - start_time >= 6:
                break

            if status == 'down':
                break
                
        return PASS_MASK
