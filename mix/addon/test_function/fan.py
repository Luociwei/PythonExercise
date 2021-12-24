import re
import threading
import time

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"
GLOBAL_FAN_LOCK = threading.Lock()

class FAN(object):
    rpc_public_api = ['speed_set','disable','speed_get']
    def __init__(self, xobjects):
        self.xobject = xobjects
        self.fan_ctl = xobjects['fan_pwm_output']
        self.gpio992 = xobjects['gpio_992']
        self.gpio993 = xobjects['gpio_993']
        self.signal_meter = xobjects['fan_signal_meter']
        self.fan_ctl.close()
        self.gpio1005 = xobjects['gpio_1005']
        self.gpio1006 = xobjects['gpio_1006']
        self.gpio1007 = xobjects['gpio_1007']
        self.gpio1008 = xobjects['gpio_1008']
        time.sleep(0.5)
        self.gpio1005.set_level(1)
        self.gpio1006.set_level(1)
        self.gpio1007.set_level(1)
        self.gpio1008.set_level(1)

    def open(self):
        '''
        pwm output open
        Args:
            
        Example:
            open()
        '''
        self.fan_ctl.open()

        return PASS_MASK

    def close(self):
        '''
        pwm output close
        Args:
            
        Example:
            close():
        '''
        self.fan_ctl.close()

        return PASS_MASK

    def set(self, fre=100000, vpp_scale=0.5, square_duty=0.5, time_us = 0xffffff):
        '''
        pwm set
        Args:
            channel:   string,    channel1 ,channel2,...
            fre:       Hz,
            vpp_scale:      float
            square_duty:    float
            time_us:        0xffffff ,always on

        Example:
            set(100000, 0.5,0.5,1000)
        '''
        self.fan_ctl.set_swg_paramter(125000000, fre, vpp_scale, square_duty, 0)
        self.fan_ctl.set_signal_type('square')
        self.fan_ctl.set_signal_time(time_us)
        self.fan_ctl.output_signal()
        
        return PASS_MASK

    def speed_set(self,fre, duty):
        '''
        pwm output enable
        Args:
            fre:       Hz,
            Duty:      float
        Example:
            output_enable(1000,50)

        '''
        self.open()
        # speed = 100 - float(duty)
        square_duty = (100-float(duty))/100
        self.set(int(fre), 0.5, square_duty)
        

        return PASS_MASK

    def disable(self):
        '''
        pwm output disable
        Args:
            disable(self):
        Example:
            output_disable('')

        '''
        self.close()
        return PASS_MASK

    def speed_get(self, channel):
        '''
        speed_get
        Args:
            speed_get(self, channel):
        Example:
            speed_get(1):
        '''
        try:
            GLOBAL_FAN_LOCK.acquire()
            self.signal_meter.close()
            if int(channel) == 1 :
                self.gpio992.set_level(0)
                self.gpio993.set_level(0)
            elif int(channel) == 2 :
                self.gpio992.set_level(1)
                self.gpio993.set_level(0)
            elif int(channel) == 3 :
                self.gpio992.set_level(0)
                self.gpio993.set_level(1)
            elif int(channel) == 4 :
                self.gpio992.set_level(1)
                self.gpio993.set_level(1)
            self.signal_meter.open()
            self.signal_meter.start_measure(100, 125000000)
            freq = self.signal_meter.measure_frequency('LP')
            getd = self.signal_meter.duty()
            self.signal_meter.close()
            print('freq=',freq)
            print('getd=',getd)
            GLOBAL_FAN_LOCK.release()
            val = 0.0014 * freq * freq + 0.3266 * freq + 1.5984
            return str(int(val)) #'freq:'+str(freq)+'duty:'+ str(getd)
        except Exception as e:
            GLOBAL_FAN_LOCK.release()
            return '0'
            
            

    # def state(self):
    #     """
    #     :param ch: int, 1-4, channel
    #     :return: str, pass or fail 
    #     """

    #     pattern = re.compile(r'([0-9.]+)', re.I)
    #     pre_value = self.fan_speed_get(ch)
    #     pre_set_value = 0
    #     if pattern and len(pattern.findall(pre_value)) > 0:
    #         pre_set_value = float(pattern.findall(pre_value)[0])

    #     print 'pre_set_value:',pre_set_value
    #     self.fan_speed_set(ch, 90, 1000)
    #     set_val = self.fan_speed_get(ch)
        
    #     duty_v = 0
    #     ret_data = 'fail'

    #     if pattern and len(pattern.findall(set_val)) > 0:
    #         duty_v = float(pattern.findall(set_val)[0])
    #     if duty_v > 0:
    #         ret_data = 'pass'

    #     print 'duty_v:',duty_v
    #     self.fan_speed_set(ch, pre_set_value, 1000)

    #     return ret_data + '\n*_*'





