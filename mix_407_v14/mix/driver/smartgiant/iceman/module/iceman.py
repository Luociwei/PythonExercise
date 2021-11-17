# -*- coding: utf-8 -*-
import math
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.gpio_emulator import GPIOEmulator
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_sgt1_sg_r import MIXSGT1SGR


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


iceman_calibration = {
    'DC_1V': {
        'level1': {'unit_index': 0},
        'level2': {'unit_index': 1},
        'level3': {'unit_index': 2},
        'level4': {'unit_index': 3},
        'level5': {'unit_index': 4},
        'level6': {'unit_index': 5},
        'level7': {'unit_index': 6},
        'level8': {'unit_index': 7},
        'level9': {'unit_index': 8},
        'level10': {'unit_index': 9}
    },
    'DC_10V': {
        'level1': {'unit_index': 10},
        'level2': {'unit_index': 11},
        'level3': {'unit_index': 12},
        'level4': {'unit_index': 13},
        'level5': {'unit_index': 14},
        'level6': {'unit_index': 15},
        'level7': {'unit_index': 16},
        'level8': {'unit_index': 17},
        'level9': {'unit_index': 18},
        'level10': {'unit_index': 19}
    },
    'SINE_VPP_1V': {
        'level1': {'unit_index': 20},
        'level2': {'unit_index': 21},
        'level3': {'unit_index': 22},
        'level4': {'unit_index': 23},
        'level5': {'unit_index': 24},
        'level6': {'unit_index': 25},
        'level7': {'unit_index': 26},
        'level8': {'unit_index': 27},
        'level9': {'unit_index': 28},
        'level10': {'unit_index': 29}
    },
    'SINE_VPP_10V': {
        'level1': {'unit_index': 30},
        'level2': {'unit_index': 31},
        'level3': {'unit_index': 32},
        'level4': {'unit_index': 33},
        'level5': {'unit_index': 34},
        'level6': {'unit_index': 35},
        'level7': {'unit_index': 36},
        'level8': {'unit_index': 37},
        'level9': {'unit_index': 38},
        'level10': {'unit_index': 39}
    },
    'SQUARE_VPP_1V': {
        'level1': {'unit_index': 40},
        'level2': {'unit_index': 41},
        'level3': {'unit_index': 42},
        'level4': {'unit_index': 43},
        'level5': {'unit_index': 44},
        'level6': {'unit_index': 45},
        'level7': {'unit_index': 46},
        'level8': {'unit_index': 47},
        'level9': {'unit_index': 48},
        'level10': {'unit_index': 49}
    },
    'SQUARE_VPP_10V': {
        'level1': {'unit_index': 50},
        'level2': {'unit_index': 51},
        'level3': {'unit_index': 52},
        'level4': {'unit_index': 53},
        'level5': {'unit_index': 54},
        'level6': {'unit_index': 55},
        'level7': {'unit_index': 56},
        'level8': {'unit_index': 57},
        'level9': {'unit_index': 58},
        'level10': {'unit_index': 59}
    },
    'TRIANGLE_VPP_1V': {
        'level1': {'unit_index': 60},
        'level2': {'unit_index': 61},
        'level3': {'unit_index': 62},
        'level4': {'unit_index': 63},
        'level5': {'unit_index': 64},
        'level6': {'unit_index': 65},
        'level7': {'unit_index': 66},
        'level8': {'unit_index': 67},
        'level9': {'unit_index': 68},
        'level10': {'unit_index': 69}
    },
    'TRIANGLE_VPP_10V': {
        'level1': {'unit_index': 70},
        'level2': {'unit_index': 71},
        'level3': {'unit_index': 72},
        'level4': {'unit_index': 73},
        'level5': {'unit_index': 74},
        'level6': {'unit_index': 75},
        'level7': {'unit_index': 76},
        'level8': {'unit_index': 77},
        'level9': {'unit_index': 78},
        'level10': {'unit_index': 79}
    },
    'OFFSET_1V': {
        'level1': {'unit_index': 80},
        'level2': {'unit_index': 81},
        'level3': {'unit_index': 82},
        'level4': {'unit_index': 83},
        'level5': {'unit_index': 84},
        'level6': {'unit_index': 85},
        'level7': {'unit_index': 86},
        'level8': {'unit_index': 87},
        'level9': {'unit_index': 88},
        'level10': {'unit_index': 89}
    },
    'OFFSET_10V': {
        'level1': {'unit_index': 90},
        'level2': {'unit_index': 91},
        'level3': {'unit_index': 92},
        'level4': {'unit_index': 93},
        'level5': {'unit_index': 94},
        'level6': {'unit_index': 95},
        'level7': {'unit_index': 96},
        'level8': {'unit_index': 97},
        'level9': {'unit_index': 98},
        'level10': {'unit_index': 99}
    },
    'SAWTOOTH_VPP_1V': {
        'level1': {'unit_index': 100},
        'level2': {'unit_index': 101},
        'level3': {'unit_index': 102},
        'level4': {'unit_index': 103},
        'level5': {'unit_index': 104},
        'level6': {'unit_index': 105},
        'level7': {'unit_index': 106},
        'level8': {'unit_index': 107},
        'level9': {'unit_index': 108},
        'level10': {'unit_index': 109}
    },
    'SAWTOOTH_VPP_10V': {
        'level1': {'unit_index': 110},
        'level2': {'unit_index': 111},
        'level3': {'unit_index': 112},
        'level4': {'unit_index': 113},
        'level5': {'unit_index': 114},
        'level6': {'unit_index': 115},
        'level7': {'unit_index': 116},
        'level8': {'unit_index': 117},
        'level9': {'unit_index': 118},
        'level10': {'unit_index': 119}
    }
}

iceman_range_table = {
    'DC_1V': 0,
    'DC_10V': 1,
    'SINE_VPP_1V': 2,
    'SINE_VPP_10V': 3,
    'SQUARE_VPP_1V': 4,
    'SQUARE_VPP_10V': 5,
    'TRIANGLE_VPP_1V': 6,
    'TRIANGLE_VPP_10V': 7,
    'OFFSET_1V': 8,
    'OFFSET_10V': 9,
    'SAWTOOTH_VPP_1V': 10,
    'SAWTOOTH_VPP_10V': 11
}

iceman_config = {
    "1V": {
        "offset": {
            "max": 500.0,  # mV
            "min": -500.0  # mV
        },
        "vpp": {
            "max": 1000.0,  # mV
            "min": 0.0,  # mV
        },
        "rms": {
            "max": 366.1,  # mVrms
        }
    },
    "10V": {
        "offset": {
            "max": 5000.0,  # mV
            "min": -5000.0,  # mV
        },
        "vpp": {
            "max": 10000.0,  # mVrms
            "min": 0.0,  # mVrms
        },
        "rms": {
            "max": 3661,  # mVrms
        }
    }
}


class IcemanException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class IcemanDef:
    # the definition can be found in Driver ERS
    EEPROM_DEV_ADDR = 0x57
    SENSOR_DEV_ADDR = 0x4F
    RANGE_1V = '1V'
    RANGE_10V = '10V'
    RANGE_10V_GAIN = 10.09
    SAMPLE_RATE = 50000000
    MAX_MVPP = 1065.0  # mV
    FREQ_MIN = 1  # Hz
    FREQ_MAX = 4000000  # Hz
    SIGNAL_SOURCE_SCALE_MAX = 0.9999
    SIGNAL_SOURCE_SCALE_MIN = -0.9999
    SIGNAL_SOURCE_VPP_MAX = 1.0
    OUTPUT_DURATION = 0xffffffff
    RANGE_CTRL_PIN = 0
    AWG_DC_DURATION = 1000
    REG_SIZE = 256
    MIX_SGT1_REG_SIZE = 65536
    # FPGA can resolve the minimum processing time for AWG.
    AWG_MIN_TIME_RESOLUTION = 0.0001


class IcemanBase(MIXBoard):
    '''
    Base class of Iceman and IcemanCompatible,Providing common Iceman methods.

    Args:
        i2c:             instance(I2C)/None,            i2c bus which is used to access CAT24C32 and NCT75.
        signal_source:   instance(MIXSignalSourceSG)/None, MIXSignalSourceSG used to control DAC output.
        range_ctrl_pin:  instance(GPIO)/None,           GPIO or Pin, which is used to control output range.
        ipcore:          instance(MIXSGT1SGR)/None,        MIXSGT1SGR which include MIXSignalSource and PLGPIO IP.
        eeprom_dev_addr: int,                           Eeprom device address.
        sensor_dev_addr: int,                           NCT75 device address.
    '''

    rpc_public_api = ['module_init', 'get_range', 'set_sampling_rate', 'output_volt', 'output_sine',
                      'output_square', 'output_triangle', 'output_sawtooth', 'output_stop'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, signal_source, range_ctrl_pin, ipcore, eeprom_dev_addr, sensor_dev_addr):
        if not i2c and not signal_source and not range_ctrl_pin and not ipcore:
            self.signal_source = MIXSignalSourceSGEmulator('mix_signalsource_sg_emulator')
            self.range_ctrl_pin = GPIOEmulator('gpio_emulator')
        elif i2c and signal_source and range_ctrl_pin and not ipcore:
            if isinstance(signal_source, basestring):
                axi4_bus = AXI4LiteBus(signal_source, IcemanDef.REG_SIZE)
                self.signal_source = MIXSignalSourceSG(axi4_bus)
            else:
                self.signal_source = signal_source
            self.range_ctrl_pin = range_ctrl_pin
        elif i2c and not signal_source and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, IcemanDef.MIX_SGT1_REG_SIZE)
                use_gpio = False if range_ctrl_pin else True
                self.ipcore = MIXSGT1SGR(axi4_bus, use_gpio)
            else:
                self.ipcore = ipcore
            self.signal_source = self.ipcore.signal_source
            self.range_ctrl_pin = range_ctrl_pin or Pin(self.ipcore.gpio, IcemanDef.RANGE_CTRL_PIN)
        else:
            raise IcemanException("Please check init parameters.")
        if i2c:
            eeprom = CAT24C32(eeprom_dev_addr, i2c)
            nct75 = NCT75(sensor_dev_addr, i2c)
        else:
            eeprom = None
            nct75 = None
        super(IcemanBase, self).__init__(eeprom, nct75, cal_table=iceman_calibration, range_table=iceman_range_table)

    def module_init(self):
        '''
        init module, range ctrl pin will be set to output.

        Examples:
            iceman.module_init()

        '''
        self.load_calibration()
        self.range_ctrl_pin.set_dir('output')
        self._select_range('1V')
        self.set_sampling_rate()

    def _check_range(self, range):
        '''
        check signal range if is valid.

        Returns:
            string, convert range string to upper.

        Raise:
            IcemanException:  Parameter 'range' is invalid.

        '''
        if range.upper() == IcemanDef.RANGE_1V:
            return IcemanDef.RANGE_1V
        elif range.upper() == IcemanDef.RANGE_10V:
            return IcemanDef.RANGE_10V
        else:
            raise IcemanException("Parameter 'range' is invalid")

    def _select_range(self, range):
        '''
        Select output range.

        Args:
            range:      string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        if hasattr(self, 'range') and range == self.range:
            return "done"
        if range == IcemanDef.RANGE_1V:
            self.range_ctrl_pin.set_level(0)
        else:
            self.range_ctrl_pin.set_level(1)
        self.range = range
        return "done"

    def get_range(self):
        '''
        Get current range.

        Returns:
            string, ['1V', '10V'], current range.

        '''
        return self.range

    def set_sampling_rate(self, sampling_rate=IcemanDef.SAMPLE_RATE):
        '''
        Iceman set dac sample rate.

        Args:
            sampling_rate:    float,    [5~50000000], unit Hz, default value is 50000000Hz.
        Returns:
            strings, "done", api execution successful.

        '''
        assert 5 <= sampling_rate <= 50000000
        if hasattr(self, 'sampling_rate') and sampling_rate == self.sampling_rate:
            return "done"

        self.sampling_rate = sampling_rate
        return "done"

    def output_volt(self, mvolt, range=IcemanDef.RANGE_1V):
        '''
        Output DC voltage in mV.

        Args:
            mvolt:   float, if range is 1V, -500 mV <= mvolt <= 500 mV,
                            if range is 10V, -5000 mV <= mvolt <= 5000 mV.
            range:   string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        assert mvolt >= iceman_config[range]['offset']['min']
        assert mvolt <= iceman_config[range]['offset']['max']
        self.output_stop()
        self._select_range(range)
        self.signal_source.open()
        mvolt = self.calibrate('DC_{}'.format(self.range), mvolt)

        if self.range == IcemanDef.RANGE_10V:
            mvolt = mvolt * 1.0 / IcemanDef.RANGE_10V_GAIN

        # the volt should be reversed according to hardware
        mvolt = 0 - mvolt

        # get the offset scale
        mvolt = mvolt / (IcemanDef.MAX_MVPP / 2.0)

        if mvolt > IcemanDef.SIGNAL_SOURCE_SCALE_MAX:
            mvolt = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        elif mvolt < IcemanDef.SIGNAL_SOURCE_SCALE_MIN:
            mvolt = IcemanDef.SIGNAL_SOURCE_SCALE_MIN
        step = [[mvolt, mvolt, IcemanDef.AWG_DC_DURATION]]
        self.signal_source.set_signal_time(IcemanDef.OUTPUT_DURATION)
        self.signal_source.set_signal_type('AWG')
        self.signal_source.set_awg_parameter(self.sampling_rate, step)
        self.signal_source.output_signal()
        return "done"

    def output_sine(self, freq, rms, offset=0, range=IcemanDef.RANGE_1V):
        '''
        Output sine waveform with frequency, rms and offset. offset default is 0.

        Args:
            freq:    int, [1~4000000], unit Hz, output signal frequency in Hz.
            rms:     float, output signal rms. If range is 1V, 0 mVrms <= rms <= 366.1 mVrms.
                                               If range is 10V, 0 mVrms <= rms <= 3661 mVrms.
            offset:  float, signal offset voltage. If range is 1V, -500 mV <= offset <= 500 mV.
            range:   string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        assert IcemanDef.FREQ_MIN <= freq <= IcemanDef.FREQ_MAX
        assert 0 <= rms <= iceman_config[range]['rms']['max']
        assert offset >= iceman_config[range]['offset']['min']
        assert offset <= iceman_config[range]['offset']['max']
        self.output_stop()
        self._select_range(range)
        self.signal_source.open()
        rms = self.calibrate('SINE_VPP_{}'.format(self.range), rms)
        offset = self.calibrate('DC_{}'.format(self.range), offset)
        if self.range == IcemanDef.RANGE_10V:
            rms /= IcemanDef.RANGE_10V_GAIN
            offset /= IcemanDef.RANGE_10V_GAIN
        vpp = 2 * math.sqrt(2) * rms
        vpp = vpp / IcemanDef.MAX_MVPP
        offset = offset / (IcemanDef.MAX_MVPP / 2.0)
        offset = -offset
        if vpp > IcemanDef.SIGNAL_SOURCE_VPP_MAX:
            vpp = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        if vpp < 0:
            vpp = 0.0
        self.signal_source.set_signal_time(IcemanDef.OUTPUT_DURATION)
        self.signal_source.set_signal_type('sine')
        self.signal_source.set_swg_paramter(self.sampling_rate, freq, vpp, 0, offset)
        self.signal_source.output_signal()
        return "done"

    def output_square(self, freq, vpp, duty, offset=0, range=IcemanDef.RANGE_1V):
        '''
        Ouptut square waveform with frequency, vpp, duty and offset. default offset is 0

        Args:
            freq:     int, [1~4000000], unit Hz, square waveform output frquency in Hz.
            vpp:      float, square waveform output vpp. If range is 1V,
                                                         0 <= vpp <= 1000 mV. If range is 10V,
                                                         0 <= vpp <= 10000 mV.
            duty:     float, [0~100], square waveform output duty.
            offset:   float, default 0,  square waveform offset voltage. If range is 1V,
                                         -500 mV <= offset <= 500 mV. If range is 10V,
                                         -5000 mV <= offset <= 5000 mV.
            range:   string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        assert freq >= IcemanDef.FREQ_MIN and freq <= IcemanDef.FREQ_MAX
        assert vpp >= iceman_config[range]['vpp']['min']
        assert vpp <= iceman_config[range]['vpp']['max']
        assert offset >= iceman_config[range]['offset']['min']
        assert offset <= iceman_config[range]['offset']['max']
        assert duty >= 0 and duty <= 100

        self.output_stop()
        self._select_range(range)
        self.signal_source.open()
        vpp = self.calibrate('SQUARE_VPP_{}'.format(self.range), vpp)
        offset = self.calibrate('DC_{}'.format(self.range), offset)
        if self.range == IcemanDef.RANGE_10V:
            vpp /= IcemanDef.RANGE_10V_GAIN
            offset /= IcemanDef.RANGE_10V_GAIN

        vpp = vpp / IcemanDef.MAX_MVPP
        offset = offset / (IcemanDef.MAX_MVPP / 2.0)
        # the voltage should be reversed according to hardware
        offset = -offset
        if vpp > IcemanDef.SIGNAL_SOURCE_VPP_MAX:
            vpp = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        if vpp < 0:
            vpp = 0.0
        self.signal_source.set_signal_time(IcemanDef.OUTPUT_DURATION)
        self.signal_source.set_signal_type('square')
        self.signal_source.set_swg_paramter(self.sampling_rate, freq, vpp, 1 - duty / 100.0, offset)
        self.signal_source.output_signal()
        return "done"

    def output_triangle(self, freq, vpp, delay_ms=0, offset=0, range=IcemanDef.RANGE_1V):
        '''
        Output triangle waveform with frequency, vpp, delay_ms and offset.

        Args:
            freq:     int, [1~4000000], unit Hz, triangle waveform output frquency in Hz.
            vpp:      float, square waveform output vpp. If range is 1V,
                                                         0 <= vpp <= 1000 mV. If range is 10V,
                                                         0 <= vpp <= 10000 mV.
            delay_ms:    float, default 0, unit ms,  triangle waveform start delay time.
            offset:   float, default 0,  square waveform offset voltage. If range is 1V,
                                         -500 mV <= offset <= 500 mV. If range is 10V,
                                         -5000 mV <= offset <= 5000 mV.
            range:   string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        assert IcemanDef.FREQ_MIN <= freq <= IcemanDef.FREQ_MAX
        assert vpp >= iceman_config[range]['vpp']['min']
        assert vpp <= iceman_config[range]['vpp']['max']
        assert delay_ms >= 0
        assert offset >= iceman_config[range]['offset']['min']
        assert offset <= iceman_config[range]['offset']['max']

        self.output_stop()
        self._select_range(range)
        self.signal_source.open()
        vpp = self.calibrate('TRIANGLE_VPP_{}'.format(self.range), vpp)
        offset = self.calibrate('DC_{}'.format(self.range), offset)
        if self.range == IcemanDef.RANGE_10V:
            vpp /= IcemanDef.RANGE_10V_GAIN
            offset /= IcemanDef.RANGE_10V_GAIN
        # the voltage should be reversed according to hardware
        v1 = 0 - (vpp / 2.0 + offset)
        v2 = 0 - (offset - vpp / 2.0)
        # get the period in ms
        period = 1000.0 / freq - delay_ms
        if period <= 0:
            raise IcemanException('Iceman board parameter delay_ms out of range')

        v1 = v1 / (IcemanDef.MAX_MVPP / 2.0)
        v2 = v2 / (IcemanDef.MAX_MVPP / 2.0)
        if v1 > IcemanDef.SIGNAL_SOURCE_SCALE_MAX:
            v1 = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        elif v1 < IcemanDef.SIGNAL_SOURCE_SCALE_MIN:
            v1 = IcemanDef.SIGNAL_SOURCE_SCALE_MIN
        if v2 > IcemanDef.SIGNAL_SOURCE_SCALE_MAX:
            v2 = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        elif v2 < IcemanDef.SIGNAL_SOURCE_SCALE_MIN:
            v2 = IcemanDef.SIGNAL_SOURCE_SCALE_MIN
        self.signal_source.set_signal_time(IcemanDef.OUTPUT_DURATION)
        self.signal_source.set_signal_type('AWG')

        # FPGA can resolve the minimum processing time for AWG.
        if (period / 2.0) > IcemanDef.AWG_MIN_TIME_RESOLUTION:
            wave_data = [[v2, v1, period / 2.0], [v1, v2, period / 2.0]]
        if delay_ms > IcemanDef.AWG_MIN_TIME_RESOLUTION:
            wave_data.append([v2, v2, delay_ms])
        self.signal_source.set_awg_parameter(self.sampling_rate, wave_data)
        self.signal_source.output_signal()
        return "done"

    def output_sawtooth(self, freq, vpp, trise, delay_ms=0, offset=0, range=IcemanDef.RANGE_1V):
        '''
        Output sawtooth waveform with frequency, vpp, trise, delay_ms and offset.

        Args:
            freq:     float, [1~4000000], unit Hz, sawtooth waveform output frquency in Hz.
            vpp:      float, sawtooth waveform output vpp. If range is 1V,
                                                         0 <= vpp <= 1000 mV. If range is 10V,
                                                         0 <= vpp <= 10000 mV.
            trise:    float,   [0~1000], unit ms, sawtooth waveform rise time.
            delay_ms:    float, default 0, unit ms, sawtooth waveform start delay time.
            offset:   float, default 0,  sawtooth waveform offset voltage. If range is 1V,
                                         -500 mV <= offset <= 500 mV. If range is 10V,
                                         -5000 mV <= offset <= 5000 mV.
            range:   string, ['1V', '10V'], signal output range.

        Returns:
            string, "done", api execution successful.

        '''
        range = self._check_range(range)
        assert IcemanDef.FREQ_MIN <= freq <= IcemanDef.FREQ_MAX
        assert vpp >= iceman_config[range]['vpp']['min']
        assert vpp <= iceman_config[range]['vpp']['max']
        assert 0 <= (trise + delay_ms) <= (1000 / freq)
        assert offset >= iceman_config[range]['offset']['min']
        assert offset <= iceman_config[range]['offset']['max']

        self.output_stop()
        self._select_range(range)
        self.signal_source.open()
        vpp = self.calibrate('SAWTOOTH_VPP_{}'.format(self.range), vpp)
        offset = self.calibrate('DC_{}'.format(self.range), offset)
        if self.range == IcemanDef.RANGE_10V:
            vpp /= IcemanDef.RANGE_10V_GAIN
            offset /= IcemanDef.RANGE_10V_GAIN
        # the voltage should be reversed according to hardware
        v1 = 0 - (vpp / 2.0 + offset)
        v2 = 0 - (offset - vpp / 2.0)
        # get the period in ms
        period = 1000.0 / freq - delay_ms
        if period <= 0:
            raise IcemanException('Iceman board parameter delay_ms out of range')

        v1 = v1 / (IcemanDef.MAX_MVPP / 2.0)
        v2 = v2 / (IcemanDef.MAX_MVPP / 2.0)
        if v1 > IcemanDef.SIGNAL_SOURCE_SCALE_MAX:
            v1 = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        elif v1 < IcemanDef.SIGNAL_SOURCE_SCALE_MIN:
            v1 = IcemanDef.SIGNAL_SOURCE_SCALE_MIN
        if v2 > IcemanDef.SIGNAL_SOURCE_SCALE_MAX:
            v2 = IcemanDef.SIGNAL_SOURCE_SCALE_MAX
        elif v2 < IcemanDef.SIGNAL_SOURCE_SCALE_MIN:
            v2 = IcemanDef.SIGNAL_SOURCE_SCALE_MIN
        self.signal_source.set_signal_time(IcemanDef.OUTPUT_DURATION)
        self.signal_source.set_signal_type('AWG')

        wave_data = []
        fall_edge = round(period - trise, 6)
        # FPGA can resolve the minimum processing time for AWG.
        if trise > IcemanDef.AWG_MIN_TIME_RESOLUTION:
            wave_data.append([v2, v1, trise])
        if fall_edge > IcemanDef.AWG_MIN_TIME_RESOLUTION:
            wave_data.append([v1, v2, fall_edge])
        if delay_ms > IcemanDef.AWG_MIN_TIME_RESOLUTION:
            wave_data.append([v2, v2, delay_ms])
        self.signal_source.set_awg_parameter(self.sampling_rate, wave_data)
        self.signal_source.output_signal()
        return "done"

    def output_stop(self):
        '''
        Stop output signal.
        '''
        self.signal_source.close()
        return "done"


class Iceman(IcemanBase):
    '''
    Iceman is a high precision signal source module.

    compatible = ["GQQ-SG0001007-000"]

    The maximum refresh rate is 50Msps,
    the DAC resolution is 16 bits, and it has one channel output. It can output standard
    waveforms such as DC voltage, sine wave, square wave and triangle wave. This class is
    legacy driver for normal boot.

    Args:
        i2c:             instance(I2C)/None,            i2c bus which is used to access CAT24C32 and NCT75.
        signal_source:   instance(MIXSignalSourceSG)/None, MIXSignalSourceSG used to control DAC output.
        range_ctrl_pin:  instance(GPIO)/None,           GPIO or Pin, which is used to control output range.
        ip:              instance(MIXSGT1SGR)/None,        MIXSGT1SGR which include MIXSignalSource and PLGPIO IP.

    Examples:
        Example for using non-aggregate IP:
            i2c = I2C('/dev/i2c-0')
            axi4_bus = AXI4LiteBus('/dev/MIX_Signal_Source', 256)
            signal_source = MIXSignalSourceSG(axi4_bus)
            axi4_bus = AXI4LiteBus('/dev/MIX_GPIO', 256)
            pl_gpio = PLGPIO(axi4_bus)
            pin = Pin(pl_gpio, 0)
            iceman = Iceman(i2c, signal_source, range_ctrl_pin)

        Example for using aggregate IP:
            i2c = I2C('/dev/i2c-0')
            axi4_bus = AXI4LiteBus('/dev/MIX_SGT1')
            sgt1 = MIXSGT1SGR(axi4_bus)
            iceman = Iceman(i2c, ip=sgt1)

        Example for output signal:
            # init module
            iceman.module_init()

            # output dc 100 mV in 1V range
            iceman.output_volt(100, range='1V')

            # output sine 2000Hz, 1000 mVrms in 10V range
            iceman.output_sine(2000, 1000, range='10V')

            # output square 2000Hz, 1000 mVpp, duty 50% in 10V range
            iceman.output_square(2000, 1000, 50, range='10V')

            # output triangle 2000Hz, 1000 mVpp in 10V range.
            iceman.output_triangle(2000, 1000, range='10V')

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SG0001007-000"]

    def __init__(self, i2c, signal_source=None, range_ctrl_pin=None, ipcore=None):
        super(Iceman, self).__init__(i2c, signal_source, range_ctrl_pin, ipcore,
                                     IcemanDef.EEPROM_DEV_ADDR, IcemanDef.SENSOR_DEV_ADDR)
