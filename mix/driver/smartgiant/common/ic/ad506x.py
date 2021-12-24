# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_dac_emulator import PLSPIDACEmulator

__author__ = 'jingyong.xiao@gzseeing.com'
__version__ = '0.1'


class PLAD506xDef:
    AWG_VALUE_MAX = 0.9999
    AWG_VALUE_MIN = -0.9999
    SINE_VALUE_MAX = 0.9999
    SINE_VALUE_MIN = 0.0
    SINE_OFFSET_MAX = 0.9999
    SINE_OFFSET_MIN = -0.9999

    ALWAYS_OUTPUT = 0xFFFFFF


class AD506xException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class AD506x(object):
    '''
    AD506x chip function class.

    ClassType = DAC

    Args:
        dac_volt_min:     int, default 0, Dac min voltage of AD506X.
        dac_volt_max:     int, default 2048, Dac max voltage of AD506X.
        sample_rate:      int, default 200000, Sample_rate of AD506X.
        sck_speed:        int, default 10000000, Sck_speed of AD506X.
        signal_source:    instance(MIXSignalSourceSG)/string/None, dev_name of mix_signalsource_sg device,
                                                                or Class instance of mix_signalsource_sg.
        pl_spi_dac:       instance(PLSPIDAC)/string/None, dev_name of pl_spi_dac device,
                                                          Class instance of pl_spi_dac.

    Examples:
        signal_source = '/dev/MIX_Signal_Source_0'
        pl_spi_dac = '/dev/MIX_Spi_Dac_0'
        ad506x = AD506X(0, 2048, 200000, 10000000, signal_source, pl_spi_dac)

    '''

    def __init__(self, dac_volt_min=0, dac_volt_max=2048, sample_rate=200000,
                 sck_speed=10000000, signal_source=None,
                 pl_spi_dac=None):

        if signal_source is None:
            self.signal_source = MIXSignalSourceSGEmulator(
                "mix_signalsource_sg_emulator")
        elif isinstance(signal_source, basestring):
            # device path; create singla_source instance here.
            self.signal_source = MIXSignalSourceSG(signal_source)
        else:
            self.signal_source = signal_source

        if pl_spi_dac is None:
            self.pl_spi_dac = PLSPIDACEmulator(
                'pl_spi_dac_emulator')
        elif isinstance(pl_spi_dac, basestring):
            # device path; create singla_source instance here.
            self.pl_spi_dac = PLSPIDAC(pl_spi_dac)
        else:
            self.pl_spi_dac = pl_spi_dac

        self.sample_rate = sample_rate
        self.dac_volt_min = dac_volt_min
        self.dac_volt_max = dac_volt_max
        self.resolution = None

        self.sck_speed = sck_speed
        self.pl_spi_dac.open()
        self.pl_spi_dac.dac_mode_set(0x0)
        self.pl_spi_dac.spi_sclk_frequency_set(
            self.sck_speed)
        self.pl_spi_dac.sample_data_set(self.sample_rate)

        # k and b values of pulse, dc_voltage and triangular wave
        self.k = (PLAD506xDef.AWG_VALUE_MAX - PLAD506xDef.AWG_VALUE_MIN) / (dac_volt_max - dac_volt_min)
        self.b = PLAD506xDef.AWG_VALUE_MAX - self.k * dac_volt_max

        # k and b values of sine wave reference vpp
        self.vpp_k = (PLAD506xDef.SINE_VALUE_MAX - PLAD506xDef.SINE_VALUE_MIN) / (dac_volt_max - dac_volt_min)
        self.vpp_b = PLAD506xDef.SINE_VALUE_MAX - self.vpp_k * (dac_volt_max - dac_volt_min)

        # k and b values of sine wave offset
        self.offset_k = (PLAD506xDef.SINE_OFFSET_MAX - PLAD506xDef.SINE_OFFSET_MIN) / (dac_volt_max - dac_volt_min)
        self.offset_b = PLAD506xDef.SINE_OFFSET_MAX - self.offset_k * dac_volt_max

    def disable_output(self):
        '''
        Disable the current waveform output function, not disable the chip

        Examples:
            ad506x.disable_output()

        '''
        self.signal_source.close()

    def sine(self, vpp, offset, frequency,
             output_time=PLAD506xDef.ALWAYS_OUTPUT):
        '''
        Output sine wave

        Args:
            vpp:          float, [dac_volt_min-dac_volt_max], unit mV, vpp voltage to config sine wave.
            offset:       float, offset to config sine wave.
            frequency:    float, frequency to config sine wave.
            output_time:  int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
            ad506x.sine(2000, 1, 1000, 10000)

        '''
        assert self.dac_volt_min <= vpp <= self.dac_volt_max
        vpp_scale = self.vpp_k * vpp + self.vpp_b
        offset_volt = self.offset_k * offset + self.offset_b

        self.signal_source.close()
        self.signal_source.set_signal_time(output_time)
        self.signal_source.set_signal_type('sine')
        # 0.5 is square_duty(float): duty of square
        self.signal_source.set_swg_paramter(
            self.sample_rate, frequency, vpp_scale, 0.5, offset_volt)
        self.signal_source.open()
        self.signal_source.output_signal()

    def output_volt_dc(self, channel, volt):
        '''
        Output dc_voltage wave

        Args:
            channel:   int, [0], channel must be 0.
            volt:      float, voltage reference to config dc_voltage wave.

        Examples:
            ad506x.output_volt_dc(0, 2000)

        '''
        assert channel == 0
        output_time = PLAD506xDef.ALWAYS_OUTPUT
        start_volt = self.k * volt + self.b
        stop_volt = start_volt
        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        # 0.5 is duration time
        self.signal_source.set_awg_parameter(self.sample_rate,
                                             [(start_volt, stop_volt,
                                               0.5)])
        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()

    def triangle(self, v1, v2, triangle_width, period,
                 output_time=PLAD506xDef.ALWAYS_OUTPUT):
        '''
        Output triangle wave

        Args:
            v1:             float, Max voltage or min voltage, if v1>v2, the wave starts at v1 to v2.
            v2:             float, Max voltage or min voltage, if v2>v1, the wave starts at v2 to v1.
            triangle_width: float, Triangle_width to triangle wave.
            period:         float, Triangle_width to triangle wave.
            output_time:    int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
                   ad506x.triangle(1000, 2000, 100, 100, 10000)

        '''

        v1 = self.k * v1 + self.b
        v2 = self.k * v2 + self.b
        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        if v1 > v2:
            self.signal_source.set_awg_parameter(
                self.sample_rate, [(v1, v2, triangle_width / 2),
                                   (v2, v2, period - triangle_width),
                                   (v2, v1, triangle_width / 2)])
        else:
            self.signal_source.set_awg_parameter(
                self.sample_rate, [(v1, v2, triangle_width / 2),
                                   (v2, v1, triangle_width / 2),
                                   (v1, v1, period - triangle_width)])

        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()

    def pulse(self, v1, v2, edge_width, pulse_width, period,
              output_time=PLAD506xDef.ALWAYS_OUTPUT):
        '''
        Output pulse wave

        Args:
            v1:             float, Max voltage or min voltage, if v1>v2, the wave starts at v1 to v2.
            v2:             float, Max voltage or min voltage, if v2>v1, the wave starts at v2 to v1.
            edge_width:     float, Edge width of pulse wave.
            pulse_width:    float, Pulse width of pulse wave.
            period:         float, Period of pulse wave.
            output_time:    int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
                   ad506x.pulse(1000, 2000, 1, 10, 100, 10000)

        '''

        v1 = self.k * v1 + self.b
        v2 = self.k * v2 + self.b

        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        if v1 > v2:
            self.signal_source.set_awg_parameter(
                self.sample_rate, [(v1, v1, pulse_width),
                                   (v1, v2, edge_width),
                                   (v2, v2, period -
                                    pulse_width - 2 * edge_width),
                                   (v2, v1, edge_width)])
        else:
            self.signal_source.set_awg_parameter(
                self.sample_rate, [(v1, v1, period - pulse_width -
                                    2 * edge_width),
                                   (v1, v2, edge_width),
                                   (v2, v2, pulse_width),
                                   (v2, v1, edge_width)])

        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()
