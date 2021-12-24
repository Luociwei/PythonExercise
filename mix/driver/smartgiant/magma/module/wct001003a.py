# -*- coding: utf-8 -*-
import time
from wct001002a import WCT001002A

__author__ = 'weiping.xuan@SmartGiant'
__version__ = '0.1'


class Wct001003AException(Exception):
    def __init__(self, err_str):
        self._err_reason = err_str

    def __str__(self):
        return self._err_reason


class Wct001003ADef:
    TIME_OUT = 6
    SENSOR_HIGH_LIMIT = 120
    MAX6642_CHANNEL = ['local', 'remote']


class WCT001003A(WCT001002A):
    '''
    The WCT001003A is based on WCT001002A, Its reset function is different from wct001002a.
    WCT001003A needs to set CAP_P_CTL_0 to low level, set the trigger temperature of max6642 to 120℃,
    and read the status bit to make ALERT return to high level.

    Args:
        i2c:              instance(I2C)/None,  If not given, I2CBus emulator will be created.
        ipcore:           instance(MIXWCT001), MIXWCT001 IP driver instance, provide signalsource, signalmeter_p
                                                 and signalmeter_n function.

    Examples:
        i2c = I2C('/dev/i2c-0')
        axi4_bus = AXI4LiteBus('dev/MIX_WCT001_001_SG_R_0', 65536)
        ipcore = MIXWCT001001SGR(axi4_bus, use_signalmeter_p=True, use_signalmeter_n=True, use_signalsource=True)
        wct001003a = WCT001003A(i2c,ipcore)
    '''
    compatible = ['GQQ-03X7-5-03A', 'GQQ-03X7-5-03B']

    rpc_public_api = WCT001002A.rpc_public_api

    def __init__(self, i2c=None, ipcore=None):
        super(WCT001003A, self).__init__(i2c, ipcore)

    def post_power_on_init(self, timeout=Wct001003ADef.TIME_OUT):
        '''
        Init Magma module to a know harware state.

        This function will set cat9555 io direction to output and set ADC and DAC.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=Wct001003ADef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        Returns:
            string, "done", api execution successful.
        '''
        start_time = time.time()
        while True:
            try:
                self.signalsource.close()
                self.cat9555.set_ports([0x00, 0x00])
                self.cat9555.set_pins_dir([0, 0x0A])
                self._adc_init()
                self.mp8859_init()
                self.max6642_write_high_limit(Wct001003ADef.MAX6642_CHANNEL[0], Wct001003ADef.SENSOR_HIGH_LIMIT)
                self.max6642_read_state()
                self.load_calibration()
                return 'done'
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Wct001003AException("Timeout: {}".format(e.message))
