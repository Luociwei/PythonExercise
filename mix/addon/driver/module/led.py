import re
import threading
import multiprocessing
import time
from mix.driver.core.ic.cat9555 import CAT9555

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class LED(object):

    COLOR = {
        'off'    : [1, 1, 1],
        'red'    : [0, 1, 1],
        'green'  : [1, 0 ,1],
        'blue'   : [1, 1, 0]
    }
    SLOT = {
        'slot1'   :[3, 4, 5],
        'slot2'   :[6, 7, 8],
        'slot3'   :[0, 1, 2],
        'slot4'   :[3, 4, 5]
    }

    rpc_public_api = ['setled','startblink','stopblink']

    def __init__(self,ioexp,slot):
        self.exp = ioexp
        self.ledcontrol = False
        self.slot = slot
        self.led_thread = threading.Thread(target=self.run)
        self.led_thread.daemon = True
        self.led_thread.start()

    def _set(self,slot,color):
        for i in range(3):
            pin = self.SLOT[self.slot][i]
            val = self.COLOR[color][i]
            self.exp.set_pin(pin,val)

    def setled(self,color):
        self._set(self.slot,color)
        return PASS_MASK
    def startblink(self):
        self.ledcontrol = True
        return PASS_MASK
    def stopblink(self):
        self.ledcontrol = False
        time.sleep(0.5)
        self.setled('off')
        return PASS_MASK

    def run(self):
        while True:
            if self.ledcontrol:
                self.setled('red')
                time.sleep(0.02)
                self.setled('off')
                time.sleep(0.02)
                # self.setled(self.slot,'blue')
                # time.sleep(0.02)

