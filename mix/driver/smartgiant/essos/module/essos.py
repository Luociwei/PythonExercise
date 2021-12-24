# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.pcal6524 import PCAL6524
from mix.driver.core.ic.pcal6524_emulator import PCAL6524Emulator
from mix.driver.smartgiant.common.ic.ad506x import AD506x
from mix.driver.smartgiant.common.ic.tmp10x import TMP108
from mix.driver.core.ic.m24cxx import M24128
from mix.driver.core.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.smartgiant.common.ic.ad506x_emulator import AD5061Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

from mix.driver.smartgiant.common.ipcore.mix_sodium_sg_r import MIXSodiumSGR
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class EssosDef:

    # AD5061
    AD5061_OUTPUT_RANGE = [0, 4096]   # unit: mV
    AD5061_SAMPLE_RATE = 200000   # unit:SPS
    AD5061_SCK_SPEED = 10000000  # Hz
    AD5061_BIP_DIV_GAIN = 100
    AD5061_GAIN = 2.0
    AD5061_OFFSET = 2048.0

    # TMP108
    TMP108_DEV_ADDR = 0x49
    TMP108_ALERT_PIN = 8

    # M24128
    M24128_DEV_ADDR = 0x53

    # PCAL6524
    PCAL6524_CHIP_NUM = 2
    PCAL6524_DEV_ADDR = [0x22 + i for i in range(PCAL6524_CHIP_NUM)]
    PCAL6524_PIN_CNT = 24  # PCAL6524 has 24 IO

    DAC_REF = 13200  # mV
    DAC_GAIN = 3

    MIX_SODIUM_REG_SIZE = 65536
    PL_SPI_DAC_REG_SIZE = 256
    SIGNAL_SOURCE_REG_SIZE = 256


class EssosException(Exception):
    '''
    EssosException shows the exception of Essos
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Essos(MIXBoard):
    '''
    Essos is a digital instrument module

    ClassType: Essos

    The module will be used for output sine, pulse,
    triangle waveform and output dc voltage.

    Args:
        ipcore:           instance(MIXEssos)/None, instance of MIXEssos, which is integrated IPcore,
                                                   if not giving this parameter, will create emulator.
        signal_source_0:  instance(PLSignalSource)/None, instance of PLSignalSource, which is used to output signal,
                                                         if not giving this parameter, will create emulator.
        spi_dac_0:        instance(PLSPIDAC)/None, instance of PLSPIDAC, which is used to control DAC,
                                                   if not giving this parameter, will create emulator.
        i2c_0:            instance(I2C)/None, instance of PLI2CBus, if not giving this parameter, will create emulator.
        i2c_1:            instance(I2C)/None, instance of PLI2CBus, which is used to control TMP108 and M24128,
                                              if not giving this parameter, will create emulator.
        i2c_2:            instance(I2C)/None, instance of PLI2CBus, which is used to control PCAL6524,
                                              if not giving this parameter, will create emulator.

    Examples:
        # use non-aggregated IP
        signal_source_0 = PLSignalSource('/dev/MIX_SignalSource_0')

        spi_dac_0 = PLSPIDAC('/dev/MIX_SpiDac_0')

        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')

        essos = Essos(None, signal_source_0, spi_dac_0, i2c_0, i2c_1, i2c_2)

        # use MIXEssos aggregated IP
        ipcore = MIXEssos('/dev/MIX_ESSOS')

        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')

        essos = Essos(ipcore, None, None, i2c_0, i2c_1, i2c_2)

        # output sine waveform
        essos.sine(0, 1000, 2000, 100)

        # output dc voltage
        essos.dc(0, 1000)

        # output pulse waveform
        essos.pulse(0, 1000, 0, 100, 200, 2000)

        # output triangle waveform
        essos.triangle(0, 1000, 0, 100000, 200000)

    '''

    rpc_public_api = ['module_init', 'io_dir_set', 'io_dir_read', 'io_set', 'io_read',
                      'sine', 'dc', 'pulse', 'triangle', 'disable_waveform'] + MIXBoard.rpc_public_api

    def __init__(self, ipcore=None,
                 signal_source_0=None,
                 spi_dac_0=None,
                 i2c_0=None,
                 i2c_1=None,
                 i2c_2=None,
                 ):

        self.i2c_0 = i2c_0
        self.i2c_1 = i2c_1
        self.i2c_2 = i2c_2
        self.pcal6524 = list()

        if not ipcore and not signal_source_0 and not spi_dac_0 \
           and not i2c_0 and not i2c_1 and not i2c_2:
            self.i2c_0 = I2CBusEmulator("i2c_emulator", 256)
            self.i2c_1 = I2CBusEmulator("i2c_emulator", 256)
            self.i2c_2 = I2CBusEmulator("i2c_emulator", 256)

            self.eeprom = EepromEmulator('m24128_emulator')
            self.tmp108 = TMP108(EssosDef.TMP108_DEV_ADDR, self.i2c_1)
            self.ad5061_0 = AD5061Emulator("ad5061", EssosDef.AD5061_OUTPUT_RANGE[0], EssosDef.AD5061_OUTPUT_RANGE[1])
            for i in range(EssosDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524Emulator(EssosDef.PCAL6524_DEV_ADDR[i],
                                                      self.i2c_2))
        else:
            if ipcore and not signal_source_0 and not spi_dac_0 \
                    and i2c_0 and i2c_1 and i2c_2:
                if isinstance(ipcore, basestring):
                    axi4_bus = AXI4LiteBus(ipcore, EssosDef.MIX_SODIUM_REG_SIZE)
                    self.ipcore = MIXSodiumSGR(axi4_bus)
                else:
                    self.ipcore = ipcore
                self.signal_source_0 = self.ipcore.signal_source_0
                self.spi_dac_0 = self.ipcore.spi_dac_0

            elif not ipcore and signal_source_0 and spi_dac_0 and i2c_0 and i2c_1 and i2c_2:
                if isinstance(signal_source_0, basestring):
                    axi4_bus = AXI4LiteBus(signal_source_0, EssosDef.SIGNAL_SOURCE_REG_SIZE)
                    self.signal_source_0 = MIXSignalSourceSG(axi4_bus)
                else:
                    self.signal_source_0 = signal_source_0

                if isinstance(spi_dac_0, basestring):
                    axi4_bus = AXI4LiteBus(spi_dac_0, EssosDef.PL_SPI_DAC_REG_SIZE)
                    self.spi_dac_0 = PLSPIDAC(axi4_bus)
                else:
                    self.spi_dac_0 = spi_dac_0
            else:
                raise EssosException('Not allowed to use both aggregated IP and \
                 signal_source_0, spi_dac_0 at the same time')

            self.ad5061_0 = AD506x(EssosDef.AD5061_OUTPUT_RANGE[0],
                                   EssosDef.AD5061_OUTPUT_RANGE[1],
                                   EssosDef.AD5061_SAMPLE_RATE,
                                   EssosDef.AD5061_SCK_SPEED,
                                   self.signal_source_0,
                                   self.spi_dac_0)

            self.eeprom = M24128(EssosDef.M24128_DEV_ADDR, self.i2c_1)
            self.tmp108 = TMP108(EssosDef.TMP108_DEV_ADDR, self.i2c_1)
            for i in range(EssosDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524(EssosDef.PCAL6524_DEV_ADDR[i], self.i2c_2))

        self.waveforms = {0: self.ad5061_0}

        super(Essos, self).__init__(self.eeprom, self.tmp108)

    def module_init(self):
        '''
        Do module initialization.

        Returns:
            string, "done", when init finished, it will return done.
        '''
        # set these IO as input.
        self.io_dir_set([(EssosDef.TMP108_ALERT_PIN, 1)])
        return 'done'

    def io_dir_set(self, io_list):
        '''
        Essos set io direction state.

        Args:
            io_list: list, [(pinX, state),...], pinX  (int), 1 <= pinX <= 48
                                                state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.io_dir_set([(1,0),(2,0)])

        '''

        io_list = sorted(io_list)
        io_info = [[] for i in range(EssosDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // EssosDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % EssosDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_dir(io_list)
            chip_num += 1
        return 'done'

    def io_set(self, io_list):
        '''
        Essos set IO output state.

        Args:
            io_list: list, [(pinX, state),...], pinX  (int), 1 <= pinX <= 48
                                                state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.io_set([(1,0),(2,0)])

        '''

        io_list = sorted(io_list)
        io_info = [[] for i in range(EssosDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // EssosDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % EssosDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_state(io_list)
            chip_num += 1
        return 'done'

    def io_dir_read(self, io_list):
        '''
        Essos read IO direction.

        Args:
            io_list:    list, [pinX,...], pinX  (int), 1 <= pinX <= 48.

        Returns:
            list, [(pinX, level)...], eg: [(1,0), (2,1)].

        Examples:
            solaris.io_read_dir([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(EssosDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // EssosDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % EssosDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_dir(io)
                for num in ret:
                    num[0] += chip_num * EssosDef.PCAL6524_PIN_CNT + 1
                io_state += ret
            chip_num += 1

        return_list = []
        for io in io_list:
            for i in io_state:
                if io == i[0]:
                    return_list.append((i[0], i[1]))
                    io_state.remove(i)
                    break
        return return_list

    def io_read(self, io_list):
        '''
        Essos read IO output state.

        Args:
            io_list: list, [pinX,...], pinX  (int), 1 <= pinX <= 48.

        Returns:
            list, [(pinX, level),...], eg: [(1,0), (2,1)].

        Examples:
            essos.io_read([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(EssosDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // EssosDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % EssosDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_state(io)
                for num in ret:
                    num[0] += chip_num * EssosDef.PCAL6524_PIN_CNT + 1
                io_state += ret
            chip_num += 1

        return_list = []
        for io in io_list:
            for i in io_state:
                if io == i[0]:
                    return_list.append((i[0], i[1]))
                    io_state.remove(i)
                    break
        return return_list

    def _ad5061_output_calculation_formula(self, volt):
        '''
        The calculation formula about AD5061 in Essos board.
        Vout(mV) = 13200 - 3 * Vdac
        So Vdac = (13200 - Vout) / 3

        Args:
            volt: float, unit mV, Vout.

        Returns:
            float, value, unit mV, Vdac.

        '''
        return (EssosDef.DAC_REF - volt) / EssosDef.DAC_GAIN

    def sine(self, channel, vpp, offset, freq):
        '''
        Essos function to output sine waveform

        Args:
            channel: int, [0], The channel to output waveform.
            vpp:     float, [0~2048], unit mV, The waveform vpp voltage.
            offset:  float, [0~2048], unit mV, The waveform offset voltage.
            freq:    float, [0.01~500], unit Hz, The waveform frequency.

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.sine(0, 1000, 2000, 100)

        '''
        assert channel == 0

        vpp, offset = [self._ad5061_output_calculation_formula(v) for v in [vpp, offset]]

        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= offset <= EssosDef.AD5061_OUTPUT_RANGE[1]

        self.waveforms[channel].sine(vpp, offset, freq)
        return 'done'

    def dc(self, channel, volt):
        '''
        Essos output dc voltage

        Args:
            channel: int, [0,1], The channel to output voltage.
            volt:    float, [0~2048], unit mV, Output votlage value.

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.dc(0, 1000)

        '''
        assert channel == 0

        volt = self._ad5061_output_calculation_formula(volt)

        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= volt <= EssosDef.AD5061_OUTPUT_RANGE[1]

        # AD5061 has one channel, so the channel parameter is 0.
        self.waveforms[channel].output_volt_dc(0, volt)
        return 'done'

    def pulse(self, channel, v1, v2, edge, pulse, period):
        '''
        Essos output pulse waveform

        Args:
            channel:    int, [0, 1], The channel to output pulse.
            v1:         float, [0~2048], unit mV, start voltage of pulse.
            v2:         float, [0~2048], unit mV, end voltage of pulse.
            edge:       float, unit ms, Pulse edge width.
            pulse:      float, unit ms, Pulse width.
            period:     float, unit ms, Pulse period, include pulse width, edge width and DC width.

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.pulse(0, 1000, 0, 100, 200, 2000)

        '''
        assert channel == 0
        assert pulse > 0
        assert edge > 0
        assert pulse + edge * 2 < period

        v1, v2 = [self._ad5061_output_calculation_formula(v) for v in [v1, v2]]

        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= v1 <= EssosDef.AD5061_OUTPUT_RANGE[1]
        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= v2 <= EssosDef.AD5061_OUTPUT_RANGE[1]

        self.waveforms[channel].pulse(v1, v2, edge, pulse, period)
        return 'done'

    def triangle(self, channel, v1, v2, triangle, period):
        '''
        Essos output triangle waveform

        Args:
            channel:    int, [0, 1], The channel to output pulse.
            v1:         float, [0~2048], unit mV, start voltage of pulse.
            v2:         float, [0~2048], unit mV, end voltage of pulse.
            triangle:   float, unit ms, Triangle width.
            period:     float, unit ms, Triangle period, include triangle width and DC width.

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.triangle(0, 1000, 0, 100000, 200000)

        '''
        assert channel == 0
        assert triangle > 0
        assert triangle < period

        v1, v2 = [self._ad5061_output_calculation_formula(v) for v in [v1, v2]]

        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= v1 <= EssosDef.AD5061_OUTPUT_RANGE[1]
        assert EssosDef.AD5061_OUTPUT_RANGE[0] <= v2 <= EssosDef.AD5061_OUTPUT_RANGE[1]

        self.waveforms[channel].triangle(v1, v2, triangle, period)
        return 'done'

    def disable_waveform(self, channel=0):
        '''
        Essos disable waveform output

        Args:
            channel: int, default 0, The channel to disable waveform output.

        Returns:
            string, "done", api execution successful.

        Examples:
            essos.disable_waveform()

        '''
        assert channel == 0
        self.waveforms[channel].disable_output()
        return 'done'
