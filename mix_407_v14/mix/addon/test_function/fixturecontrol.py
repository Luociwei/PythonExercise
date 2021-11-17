import re
import threading
import multiprocessing
import time

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

class FixtureControl(object):

    rpc_public_api = ['get_fixture_status','In','Out','Up','Down','Idle','release','press','get_key_status','get_reset_key_status','get_start_right_key_status','get_start_left_key_status']

    def __init__(self, xobjects):
        self.fixturecontrol = xobjects['fixture']
        self.first_flag = 0
        self.control = True
        # if str(self.get_fixture_status())!="1111":
        #     self.Up()
        #     time.sleep(2)
        #     self.Out()
        #     time.sleep(2)
        self.io_thread = multiprocessing.Process(target=self.run)
        self.io_thread.daemon = True
        self.io_thread.start()
        print('fixturecontrol class')

    def get_fixture_status(self):
        return self.fixturecontrol.get_status()

    def get_key_status(self):
        return self.fixturecontrol.get_key_status()

    def get_start_right_key_status(self):
        return self.fixturecontrol.get_start_right_key_status()

    def get_start_left_key_status(self):
        return self.fixturecontrol.get_start_left_key_status()
    
    def get_reset_key_status(self):
        return self.fixturecontrol.get_reset_key_status()

    def In(self):
        self.fixturecontrol.In()
        return PASS_MASK

    def Out(self):
        self.fixturecontrol.Out()
        return PASS_MASK

    def Up(self):
        self.fixturecontrol.Up()
        return PASS_MASK

    def Down(self):
        self.fixturecontrol.Down()
        return PASS_MASK

    def Idle(self):
        self.fixturecontrol.Idle()
        return PASS_MASK

    def release(self):
        if self.get_fixture_status()!='down':
            self.Out()
        else:
            self.fixturecontrol.release()
        return PASS_MASK

    def press(self):
        self.fixturecontrol.press()
        return PASS_MASK

    def run(self):
        while self.control:
            try:
                ret_start_left = self.get_start_left_key_status()
                ret_start_rigth = self.get_start_rigth_key_status()
                ret_reset = self.get_reset_key_status()
                time.sleep(1)
                key = self.get_key_status()
                # if int(ret_reset)==0 and int(ret_start) ==0:
                if str(key)=='000':
                    self.release()
                    while True:
                        if self.get_fixture_status()=='out':

                            while True:
                                time.sleep(0.3)
                                self.In()
                                if self.get_fixture_status()=='in':
                                    time.sleep(1)
                                    break
                            # elif self.get_fixture_status()=='in':
                            #     time.sleep(2)
                            #     break
                        time.sleep(0.3)
                        if self.get_fixture_status()=='in':
                            while True:
                                time.sleep(0.3)
                                self.Down()
                                if self.get_fixture_status()=='down':
                                    time.sleep(1)
                                    break
               
                        time.sleep(0.3)

                        if self.get_fixture_status()=='down':
                            while True:
                                time.sleep(0.3)
                                self.Idle()
                                if self.get_fixture_status()=='in':
                                    time.sleep(1)
                                    break
                        time.sleep(0.3)

                        if self.get_fixture_status()=='in':

                            while True:
                                time.sleep(0.3)
                                self.Out()
                                if self.get_fixture_status()=='out':
                                    time.sleep(1)
                                    break
                        time.sleep(0.3)

                # if int(ret_start)==0 and int(ret_reset)!=0:
                #     while int(ret_start)==0 and self.get_fixture_status()!='in' and self.get_fixture_status()!='down':
                #         time.sleep(0.05)
                #         self.In()
                #         ret_start = self.get_start_key_status()
                #         if int(ret_start)!=0 and self.get_fixture_status()!='in':
                #             # time.sleep(0.1)
                #             self.Idle()
                #             break
                #         elif self.get_fixture_status()=='in':
                #             time.sleep(0.8)
                #             break
                #     while int(ret_start)==0 and self.get_fixture_status()!='down':
                #         time.sleep(0.05)
                #         self.Down()
                #         ret_start = self.get_start_key_status()
                #         if int(ret_start)!=0 and self.get_fixture_status()!='down':
                #             self.Idle()
                #             break
                #         elif self.get_fixture_status()=='down':
                #             break
                if int(ret_reset)==0 and int(ret_start_left)!=0 and int(ret_start_rigth)!=0:
                    while int(ret_reset)==0 and self.get_fixture_status()!='in' and self.get_fixture_status()!='out' and self.get_fixture_status()!='idleup':
                        time.sleep(0.05)
                        self.Idle()
                        ret_reset = self.get_reset_key_status()
                        if int(ret_reset)!=0 and self.get_fixture_status()!='in':
                            time.sleep(0.05)
                            self.Idle()
                            break
                        elif int(ret_reset)!=0 and self.get_fixture_status()=='in':
                            time.sleep(0.8)
                            break
                    while int(ret_reset)==0 and self.get_fixture_status()!='out':
                        time.sleep(0.05)
                        self.Out()
                        ret_reset = self.get_reset_key_status()
                        if int(ret_reset)!=0 and self.get_fixture_status()!='out':
                            break
                        elif self.get_fixture_status()=='out':
                            break
            except Exception as e:
                pass
