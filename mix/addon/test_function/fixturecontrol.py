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


        self.io_start_thread = multiprocessing.Process(target=self.start_detect_run)
        self.io_start_thread.daemon = True
        self.io_start_thread.start()

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
        # if self.get_fixture_status()!='down':
        self.fixturecontrol.Out()
        return PASS_MASK

    def Up(self):
        # if self.get_fixture_status()=='down':
        self.fixturecontrol.Up()
        return PASS_MASK

    def Down(self):
        # if self.get_fixture_status()=='in':
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

    def start_to_press(self):
        timeout=6000
        status = self.get_fixture_status()
        if status == 'down':
            return PASS_MASK
        elif status == 'idle' or status == 'in': 
            self.Down()
            time.sleep(0.2)   
        elif status == 'idleup' or status == 'out':
            self.In()
            time.sleep(0.2)

        start_time= time.time()
        while True:
            is_start = int(self.get_start_left_key_status())==0 and int(self.get_start_right_key_status())==0
            if int(is_start)==False:
                            # time.sleep(0.1)
                self.Idle()
                break
            
            status = self.get_fixture_status()
            if status == 'down':
                time.sleep(0.8)
                break
            elif self.get_fixture_status() =='in':
                time.sleep(0.8)
                self.Down()
                
                # break
            if time.time() - start_time >= 12:
                return FAIL_MASK

            time.sleep(0.2)
        return PASS_MASK        

              
    # def start_to_press1(self):

    #     while self.get_fixture_status()!='in' and self.get_fixture_status()!='down':
    #         time.sleep(0.1)
    #         self.In()
    #         is_start = int(self.get_start_left_key_status())==0 and int(self.get_start_right_key_status())==0
    #         if int(is_start)==False and self.get_fixture_status()!='in':
    #                         # time.sleep(0.1)
    #             self.Idle()
    #             time.sleep(0.5)
    #             break
    #         elif self.get_fixture_status()=='in':
    #             time.sleep(0.8)
    #             break
    #     while self.get_fixture_status()!='down':
    #         time.sleep(0.2)
    #         self.Down()
    #         is_start = int(self.get_start_left_key_status())==0 and int(self.get_start_right_key_status())==0

    #         if int(is_start)==False and self.get_fixture_status()!='down':
    #             self.Idle()
    #             time.sleep(0.5)
    #             break
    #         elif self.get_fixture_status()=='down':
    #             break


    def start_detect_run(self):
        while self.control:
            time.sleep(0.1)
            try:
                ret_start_left = self.get_start_left_key_status()
                left_start_time= time.time()
                ret_start_right = self.get_start_right_key_status()
                right_start_time= time.time()
                if int(ret_start_left)==0 and int(ret_start_right)!=0:
                    is_stop = True
                    while True:
                        
                        if time.time() - left_start_time > 0.5:
                            break
                        # start_right = self.get_start_right_key_status()    
                        if int(self.get_start_right_key_status()) == 0:
                            self.start_to_press()
                            is_stop = False
                            break
                        time.sleep(0.03)
                    if is_stop == True:
                        while True:
                            if int(self.get_start_left_key_status())==1 and int(self.get_start_right_key_status())==1:
                                break
                            else:
                                time.sleep(0.1)


                        
                elif int(ret_start_left)!=0 and int(ret_start_right)==0:
                    is_stop = True
                    while True:
                        
                        if time.time() - right_start_time >= 0.5:
                            break
                        # start_right = self.get_start_right_key_status()    
                        if int(self.get_start_left_key_status()) == 0:
                            self.start_to_press()
                            is_stop = False
                            break
                        time.sleep(0.03)
                    if is_stop == True:
                        while True:
                            if int(self.get_start_left_key_status())==1 and int(self.get_start_right_key_status())==1:
                                break
                            else:
                                time.sleep(0.1)



                elif int(ret_start_left)==0 and int(ret_start_right)==0:
                    time.sleep(0.05)
                    self.start_to_press()
                else: # int(get_start_left_key_status)==1 and int(get_start_right_key_status)==1
                    time.sleep(0.2)

            except Exception as e:
                pass


    def run(self):
        while self.control:
            try:
                # ret_start_left = self.get_start_left_key_status()
                # ret_start_rigth = self.get_start_right_key_status()
                # ret_reset = self.get_reset_key_status()
                key = self.get_key_status()
                # if int(ret_reset)==0 and int(ret_start) ==0:
                if str(key)=='000':
                    self.release()
                    while True:
                        if self.get_fixture_status()=='out' or self.get_fixture_status()=='idleup':
                            self.In()
                            while True:
                                time.sleep(0.3)
                                if self.get_fixture_status()=='in':
                                    time.sleep(1.5)
                                    break
                            # elif self.get_fixture_status()=='in':
                            #     time.sleep(2)
                            #     break
                        time.sleep(0.3)
                        if self.get_fixture_status()=='in' or self.get_fixture_status()=='idle':
                            self.Down()
                            while True:
                                time.sleep(0.3)
                                
                                if self.get_fixture_status()=='down':
                                    time.sleep(1.5)
                                    break
               
                        time.sleep(0.3)

                        if self.get_fixture_status()=='down':
                            self.Idle()
                            while True:
                                time.sleep(0.3)
                                
                                if self.get_fixture_status()=='in':
                                    time.sleep(1.5)
                                    break
                        time.sleep(0.3)

                        if self.get_fixture_status()=='in' or self.get_fixture_status()=='idleup':
                            self.Out()
                            while True:
                                time.sleep(0.3)
                                
                                if self.get_fixture_status()=='out':
                                    time.sleep(1.5)
                                    break
                        time.sleep(0.3)

                        if int(ret_reset)==0:
                            self.Idle()
                            time.sleep(5)
                            break

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
                elif str(key)=='110':
                    if self.get_fixture_status()=='down' or self.get_fixture_status()=='idle':
                        time.sleep(0.05)
                        self.Idle()
                        start_time= time.time()
                        while True:
                            time.sleep(0.08)
                            if str(key)=='000' or int(ret_reset)==1:
                                # self.Idle()
                                break
                            status = self.get_fixture_status()          
                            if status=='in':
                                time.sleep(0.2)
                                break
                            else:
                                if time.time() - start_time >= 10:
                                    break
                    elif self.get_fixture_status()=='in' or self.get_fixture_status()=='idleup':
                        time.sleep(0.05)
                        self.Out()
                        start_time= time.time()
                        while True:
                            time.sleep(0.08)
                            if str(key)=='000' or int(ret_reset)==1:
                                self.Idle()
                                break
                            status = self.get_fixture_status()          
                            if status=='out':
                                time.sleep(0.3)
                                break
                            else:
                                if time.time() - start_time >= 10:
                                    break

                    time.sleep(0.2)
            # time.sleep(0.3)
                # if int(ret_reset)==0 and int(ret_start_left)!=0 and int(ret_start_rigth)!=0:
                #     while int(ret_reset)==0 and self.get_fixture_status()!='in' and self.get_fixture_status()!='out' and self.get_fixture_status()!='idleup':
                #         time.sleep(0.05)
                #         self.Idle()
                #         ret_reset = self.get_reset_key_status()
                #         if int(ret_reset)!=0 and self.get_fixture_status()!='in':
                #             time.sleep(0.05)
                #             self.Idle()
                #             break
                #         elif int(ret_reset)!=0 and self.get_fixture_status()=='in':
                #             time.sleep(0.8)
                #             break
                #     while int(ret_reset)==0 and self.get_fixture_status()!='out':
                #         time.sleep(0.05)
                #         self.Out()
                #         ret_reset = self.get_reset_key_status()
                #         if int(ret_reset)!=0 and self.get_fixture_status()!='out':
                #             break
                #         elif self.get_fixture_status()=='out':
                #             break
            except Exception as e:
                pass
