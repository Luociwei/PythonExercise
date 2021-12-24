# -*- coding: utf-8 -*-
import math
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class DaggerDef:
    EEPROM_DEV_ADDR = 0x51
    NCT75_DEV_ADDR = 0x49

    DEFAULT_SAMPLING_RATE = 1000

    CHANNELS = [0, 1, 'all']
    AD7175_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535
    AD7175_MVREF = 5000.0  # mv
    AD7175_CODE_POLAR = "bipolar"
    AD7175_BUFFER_FLAG = "enable"
    AD7175_REFERENCE_SOURCE = "extern"
    AD7175_CLOCK = "crystal"


dagger_calibration_info = {

    'RMS_CH0': {
        'level1': {'unit_index': 0, 'unit': 'mV'},
        'level2': {'unit_index': 1, 'unit': 'mV'},
        'level3': {'unit_index': 2, 'unit': 'mV'},
        'level4': {'unit_index': 3, 'unit': 'mV'},
        'level5': {'unit_index': 4, 'unit': 'mV'},
        'level6': {'unit_index': 5, 'unit': 'mV'},
        'level7': {'unit_index': 6, 'unit': 'mV'},
        'level8': {'unit_index': 7, 'unit': 'mV'},
        'level9': {'unit_index': 8, 'unit': 'mV'},
        'level10': {'unit_index': 9, 'unit': 'mV'},
        'level11': {'unit_index': 10, 'unit': 'mV'},
        'level12': {'unit_index': 11, 'unit': 'mV'},
        'level13': {'unit_index': 12, 'unit': 'mV'},
        'level14': {'unit_index': 13, 'unit': 'mV'}
    },
    'VOLT_CH0': {
        'level1': {'unit_index': 14, 'unit': 'mV'},
        'level2': {'unit_index': 15, 'unit': 'mV'},
        'level3': {'unit_index': 16, 'unit': 'mV'},
        'level4': {'unit_index': 17, 'unit': 'mV'},
        'level5': {'unit_index': 18, 'unit': 'mV'},
        'level6': {'unit_index': 19, 'unit': 'mV'},
        'level7': {'unit_index': 20, 'unit': 'mV'},
        'level8': {'unit_index': 21, 'unit': 'mV'},
        'level9': {'unit_index': 22, 'unit': 'mV'},
        'level10': {'unit_index': 23, 'unit': 'mV'},
        'level11': {'unit_index': 24, 'unit': 'mV'},
        'level12': {'unit_index': 25, 'unit': 'mV'},
        'level13': {'unit_index': 26, 'unit': 'mV'},
        'level14': {'unit_index': 27, 'unit': 'mV'}
    },

    'RMS_CH1': {
        'level1': {'unit_index': 28, 'unit': 'mV'},
        'level2': {'unit_index': 29, 'unit': 'mV'},
        'level3': {'unit_index': 30, 'unit': 'mV'},
        'level4': {'unit_index': 31, 'unit': 'mV'},
        'level5': {'unit_index': 32, 'unit': 'mV'},
        'level6': {'unit_index': 33, 'unit': 'mV'},
        'level7': {'unit_index': 34, 'unit': 'mV'},
        'level8': {'unit_index': 35, 'unit': 'mV'},
        'level9': {'unit_index': 36, 'unit': 'mV'},
        'level10': {'unit_index': 37, 'unit': 'mV'},
        'level11': {'unit_index': 38, 'unit': 'mV'},
        'level12': {'unit_index': 39, 'unit': 'mV'},
        'level13': {'unit_index': 40, 'unit': 'mV'},
        'level14': {'unit_index': 41, 'unit': 'mV'}
    },
    'VOLT_CH1': {
        'level1': {'unit_index': 42, 'unit': 'mV'},
        'level2': {'unit_index': 43, 'unit': 'mV'},
        'level3': {'unit_index': 44, 'unit': 'mV'},
        'level4': {'unit_index': 45, 'unit': 'mV'},
        'level5': {'unit_index': 46, 'unit': 'mV'},
        'level6': {'unit_index': 47, 'unit': 'mV'},
        'level7': {'unit_index': 48, 'unit': 'mV'},
        'level8': {'unit_index': 49, 'unit': 'mV'},
        'level9': {'unit_index': 50, 'unit': 'mV'},
        'level10': {'unit_index': 51, 'unit': 'mV'},
        'level11': {'unit_index': 52, 'unit': 'mV'},
        'level12': {'unit_index': 53, 'unit': 'mV'},
        'level13': {'unit_index': 54, 'unit': 'mV'},
        'level14': {'unit_index': 55, 'unit': 'mV'}
    }

}

dagger_range_table = {
    "RMS_CH0": 0,
    "VOLT_CH0": 1,
    "RMS_CH1": 2,
    "VOLT_CH1": 3,

}


class DaggerException(Exception):
    pass


class DaggerBase(MIXBoard):
    '''
    Base class of Dagger and DaggerCompatible.

    Providing common Dagger methods.

    Args:
        i2c:                 instance(I2C), the i2c bus is used to control eeprom and nct75 on the module.
        ad7175:              instance(ADC)/None, default None, the adc used to measure voltage.
        ipcore:                  instance(MIXDAQT1SGR)/None, default None, if daqt1 given, then use MIXDAQT1's AD7175.
        eeprom_dev_addr:     int, Eeprom device address.
        sensor_dev_addr:     int, NCT75 device address.

    '''

    rpc_public_api = ['module_init', 'get_sampling_rate', 'multi_points_measure_enable',
                      'multi_points_measure_disable', 'multi_points_voltage_measure'] + MIXBoard.rpc_public_api

    def __init__(
            self, i2c, ad7175=None, ipcore=None,
            eeprom_dev_addr=DaggerDef.EEPROM_DEV_ADDR,
            sensor_dev_addr=DaggerDef.NCT75_DEV_ADDR):

        if ipcore and ad7175:
            raise DaggerException('ipcore and ad7175 can not be existed at the same time')

        self.ipcore = ipcore
        if ipcore is not None:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, DaggerDef.MIX_DAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=DaggerDef.AD7175_MVREF,
                                          code_polar=DaggerDef.AD7175_CODE_POLAR,
                                          reference=DaggerDef.AD7175_REFERENCE_SOURCE,
                                          buffer_flag=DaggerDef.AD7175_BUFFER_FLAG,
                                          clock=DaggerDef.AD7175_CLOCK,
                                          use_spi=False, use_gpio=False)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, DaggerDef.AD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4_bus, mvref=DaggerDef.AD7175_MVREF,
                                          code_polar=DaggerDef.AD7175_CODE_POLAR,
                                          reference=DaggerDef.AD7175_REFERENCE_SOURCE,
                                          buffer_flag=DaggerDef.AD7175_BUFFER_FLAG,
                                          clock=DaggerDef.AD7175_CLOCK)
            else:
                self.ad7175 = ad7175
        else:
            self.ad7175 = MIXAd7175SGEmulator('AD7175')

        if i2c:
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.nct75 = NCT75(sensor_dev_addr, i2c)
            super(DaggerBase, self).__init__(self.eeprom, self.nct75,
                                             cal_table=dagger_calibration_info, range_table=dagger_range_table)
        else:
            super(DaggerBase, self).__init__(None, None, cal_table=dagger_calibration_info,
                                             range_table=dagger_range_table)

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }

    def module_init(self):
        '''
        Init dagger module. This method will set the board at a default state.

        Returns:
            string, "done", api execution successful.

        '''
        self.ad7175.channel_init()
        self.load_calibration()
        return 'done'

    def get_sampling_rate(self, channel):
        '''
        Get specific channel sampling rate.

        Args:
            channel:    int, [0, 1], 0 for current channel, 1 for voltage channel.

        Returns:
            float, value, AD7175 current sampling rate.

        '''
        assert channel in [0, 1]
        sampling_rate = self.ad7175.get_sampling_rate(channel)
        return sampling_rate

    def multi_points_measure_enable(self, channel, sampling_rate):
        '''
        Dagger enable continuous measure mode.

        When continuous measure mode enabled, no function except
        continuous_measure_current shall be called. This function will start data upload through dma.

        Args:
            channel:         int/string, [0, 1, 'all'],  the specific channel to enable continuous measure mode.
            sampling_rate:   float, [5~250000], please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        '''
        assert channel in DaggerDef.CHANNELS

        self.ad7175.enable_continuous_sampling(channel, sampling_rate)
        return "done"

    def multi_points_measure_disable(self, channel):
        '''
        Dagger disable continuous measure mode. This function will disable data upload through dma.

        Args:
            channel:         int/string, [0, 1, 'all'],   the specific channel to disable continuous measure mode.

        Returns:
            string, "done", api execution successful.

        '''
        assert channel in DaggerDef.CHANNELS
        self.ad7175.disable_continuous_sampling(channel)
        return "done"

    def multi_points_voltage_measure(self, channel, count=1):
        '''
        Do measure voltage in continuous mode.

        Note that when call this function, AD7175 shall have entered continuous
        mode by calling 'enable_continuous_measure'.

        Args:
            channel:     int, [0, 1], the specific channel to measure voltage.
            count:       int, [1~512], default 1, number of voltage to measure, max value is 512.

        Returns:
            dict, {"min": (value, 'mV'), "max": (value, 'mV'), "sum": (value, 'mV'),
                   "average": (value, 'mV'), "rms": (value, 'mVrms')},
                  min, max, sum, average and rms with unit.

        '''
        assert channel in [0, 1]

        adc_volts = self.ad7175.get_continuous_sampling_voltage(channel, count)
        min_volt = min(adc_volts)
        max_volt = max(adc_volts)
        sum_volt = sum(adc_volts)
        average_volt = sum_volt / len(adc_volts)
        suqare_sum_volt = sum([x**2 for x in adc_volts])
        rms_volt = math.sqrt(suqare_sum_volt / len(adc_volts))

        average_volt = self.calibrate("VOLT_CH" + str(channel), average_volt)
        rms_volt = self.calibrate("RMS_CH" + str(channel), rms_volt)

        result = dict()
        result['min'] = [min_volt, "mV"]
        result['max'] = [max_volt, "mV"]
        result['sum'] = [sum_volt, "mV"]
        result['average'] = [average_volt, "mV"]
        result['rms'] = [rms_volt, "mVrms"]
        return result


class Dagger(DaggerBase):
    '''
    Dagger is a high resolution digital module.

    compatible = ["GQQ-SCP006004-000"]

    Max sampling rate is 250Ksps. ADC resolution is 24bit.
    The module has two input module. The two channels are both used to measure voltage.
    Max input voltage is +/-5V. Note that if ad7175 cs not controlled by software, ad717x_cs should be None.
    This class is legacy driver for normal boot.

    Args:
        i2c:        instance(I2C), the i2c bus is used to control eeprom and nct75 on the module.
        ad7175:     instance(ADC), the adc used to measure voltage.

    Examples:
        i2c = I2C('/dev/i2c-0')
        ad7175 = PLAD7175('/dev/MIX_AD717X_0', 5000)
        dagger = Dagger(i2c, ad7175=ad7175)

        Example for using aggregate ipcore:
            i2c = I2C(/dev/i2c-0)
            ipcore = MIX_DAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7175',
                           use_ad717x=True, use_spi=False, use_gpio=False)
            dagger = Dagger(i2c, ipcore=ipcore)

        Example for measure voltage in 1000 sps sampling rate:
            dagger.enable_continuous_measure(0, 1000)
            result = dagger.continuous_measure_voltage(0, 10)
            print(result)
            dagger.disable_continuous_measure(0)

        Example for single channel upload:
            dma = Dma('/dev/MIX_DMA')
            dma.config_channel(0, 1024 * 1024)
            dma.enable_channel(0)
            dagger.enable_continuous_measure(0, 1000)
            time.sleep(1)
            dagger.disable_continuous_measure(0)
            dma.disable_channel(0)
            data = dma.read_channel_all_data(0)
            # parse example, data[0] is invalid
            adc_value = data[1] | (data[2] << 8) | (data[3] << 16)

        Example for dual channel upload:
            dma = Dma('/dev/MIX_DMA')
            dma.config_channel(0, 1024 * 1024)
            dma.enable_channel(0)
            dagger.enable_continuous_measure('all', 1000)
            time.sleep(1)
            dagger.disable_continuous_measure('all')
            # parse example, data[0] is channel index
            channel = data[0]
            adc_value = data[1] | (data[2] << 8) | (data[3] << 16)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP006004-000"]

    def __init__(self, i2c, ad7175=None, ipcore=None):
        super(Dagger, self).__init__(i2c, ad7175, ipcore, DaggerDef.EEPROM_DEV_ADDR, DaggerDef.NCT75_DEV_ADDR)
