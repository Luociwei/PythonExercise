# -*- coding: utf-8 -*-
from mix.driver.core.ic.m24cxx import M24128
from mix.driver.core.ic.pcal6524 import PCAL6524
from mix.driver.core.ic.pcal6524_emulator import PCAL6524Emulator
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.smartgiant.common.ic.ad506x import AD506x
from mix.driver.smartgiant.common.ic.ad506x_emulator import AD5061Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ic.ltc2378 import LTC2378
from mix.driver.smartgiant.common.ic.ltc2378_emulator import LTC2378Emulator
from mix.driver.smartgiant.common.ic.tmp10x import TMP108
from mix.driver.smartgiant.common.ipcore.mix_dma_sg_emulator import MIXDMASGEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.pl_spi_adc import PLSPIADC
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.smartgiant.common.ipcore.mix_sodium_sg_r import MIXSodiumSGR
from mix.driver.smartgiant.common.module.mix_board import MIXBoard


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class SodiumDef:
    # DMA
    DMA_SIZE = 16 * 1024 * 1024  # 16Mbytes
    DMA_READ_SIZE = 2048     # read 2048 bytes once
    DMA_TIMEOUT_MS = 3000

    # AD5061
    AD5061_OUTPUT_RANGE = [0, 2048]   # unit: mV
    AD5061_SAMPLE_RATE = 200000   # unit:SPS
    AD5061_SCK_SPEED = 10000000  # Hz
    AD5061_BIP_DIV_GAIN = 100
    AD5061_GAIN = 2.0
    AD5061_OFFSET = 2048.0

    # LTC2378
    RMS_SAMPLE_RATE = 256000  # unit: SPS
    LTC2378_VOLT_RANGE = [-4096, 4096]  # unit:mV, ADC measure range
    ADC_GAIN = 1 / 2.0
    DAC_OUTPUT_OPTIONS = ['raw', 'bip', 'bip_div']
    LTC2378_MAX_MEASURE_TIME = 65535

    # TMP108
    TMP108_DEV_ADDR = 0x48
    TMP108_ALERT_PIN = 41

    # M24128
    M24128_DEV_ADDR = 0x50
    M24128_WR_EN_PIN = 42

    # PCAL6524
    PCAL6524_CHIP_NUM = 2
    PCAL6524_DEV_ADDR = [0x22 + i for i in range(PCAL6524_CHIP_NUM)]
    PCAL6524_PIN_CNT = 24  # PCAL6524 has 24 IO


class SodiumException(Exception):
    '''
    SodiumException shows the exception of Sodium
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Sodium(MIXBoard):
    '''
    ClassType is Sodium

    Sodium is a digital instrument module, which will be used for voltage measurement, output sine, pulse,
    triangle waveform and output dc voltage.

    Args:
        ipcore:          instance(MIXSodiumSGR)/string/None,       instance of MIXSodium, which is integrated IPcore,
                                                                if not giving this parameter, will create emulator.
        spi_adc:         instance(QSPI)/None,                   instance of PLSPIAdc, which is used to control ADC,
                                                                if not giving this parameter, will create emulator.
        audio_analyzer:  instance(MIXFftAnalyzerSG)/string/None, instance of PLSignalSource, which is used to measure,
                                                                if not giving this parameter, will create emulator.
        signal_meter:    instance(MIXSignalMeterSG)/string/None,   instance of PLSignalMeter, which is used to measure,
                                                                if not giving this parameter, will create emulator.
        signal_source_0: instance(MIXSignalSourceSG)/string/None,  instance of PLSignalSource, which is used to output,
                                                                if not giving this parameter, will create emulator.
        signal_source_1: instance(MIXSignalSourceSG)/string/None,  instance of PLSignalSource, which is used to output,
                                                                if not giving this parameter, will create emulator.
        spi_dac_0:       instance(QSPI)/string/None,            instance of PLSPIDAC, which is used to control DAC,
                                                                if not giving this parameter, will create emulator.
        spi_dac_1:       instance(QSPI)/string/None,            instance of PLSPIDAC, which is used to control DAC,
                                                                if not giving this parameter, will create emulator.
        i2c_0:           instance(I2C)/None,                    instance of PLI2CBus, if not giving this parameter,
                                                                will create emulator.
        i2c_1:           instance(I2C)/None,                    instance of PLI2CBus, which is used to
                                                                control PCAL6524 and M24128,
                                                                if not giving this parameter, will create emulator.
        i2c_2:           instance(I2C)/None,                    instance of PLI2CBus, which is used to control sensor,
                                                                if not giving this parameter, will create emulator.
        dma:             instance(DMA)/None,                    instance of Dma, which is used for data transmission,
                                                                if not giving this parameter, will create emulator.
        rms_dma_channel: int, channel of Dma,                   which is used to determine DMA upload channel.

    Examples:
        # use non-aggregated IP
        spi_adc = PLSPIAdc('/dev/MIX_SpiAdc_0')

        audio_analyzer = MIXFftAnalyzerSG('/dev/MIX_AUDIO_ANALYZER')

        signal_meter = MIXSignalMeterSG('/dev/MIX_SignalMeter_0')

        signal_source_0 = PLSignalSource('/dev/MIX_SignalSource_0')
        signal_source_1 = PLSignalSource('/dev/MIX_SignalSource_1')

        spi_dac_0 = PLSPIDAC('/dev/MIX_SpiDac_0')
        spi_dac_1 = PLSPIDAC('/dev/MIX_SpiDac_1')

        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')

        dma = Dma('/dev/MIX_DMA_0')
        rms_dma_channel = 1

        sodium = Sodium(None, spi_adc, audio_analyzer, signal_meter,
                        signal_source_0, signal_source_1, spi_dac_0,
                        spi_dac_1, i2c_0, i2c_1, i2c_2, dma, rms_dma_channel)

        # use MIXSodium aggregated IP
        ipcore = MIXSodiumSGR('/dev/MIX_SODIUM')

        spi_adc = None
        signal_meter = None
        signal_source_0 = None
        signal_source_1 = None
        spi_dac_0 = None
        spi_dac_1 = None

        audio_axi4_bus = AXI4LiteBus('/dev/MIX_AUDIO_ANALYZER', 65536)
        audio_analyzer = MIXFftAnalyzerSG(audio_axi4_bus)
        i2c0_axi4_bus = AXI4LiteBus('/dev/MIX_I2C_0', 256)

        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')

        dma = Dma('/dev/MIX_DMA_0')
        rms_dma_channel = 1

        sodium = Sodium(ipcore, None, audio_analyzer, None, None, None, None,
                        None, i2c_0, i2c_1, i2c_2, dma, rms_dma_channel)

        # rms measure
        result = sodium.rms_measure(1000, 500, 256000, 'on')
        print(result)

        # voltage measure
        voltage = sodium.voltage_measure()
        print(voltage)

        # output sine waveform
        sodium.sine(0, 1000, 2000, 100)

        # output dc voltage
        sodium.dc(0, 1000)

        # output pulse waveform
        sodium.pulse(0, 1000, 0, 100, 200, 2000)

        # output triangle waveform
        sodium.triangle(0, 1000, 0, 100000, 200000)

    '''

    rpc_public_api = ['module_init', 'io_dir_set', 'io_dir_read', 'io_set', 'io_read',
                      'ltc2378_get_raw_data', 'sine', 'dc', 'pulse',
                      'triangle', 'rms_measure', 'voltage_measure', 'disable_waveform'] + MIXBoard.rpc_public_api

    def __init__(self, ipcore=None,
                 spi_adc=None,
                 audio_analyzer=None,
                 signal_meter=None,
                 signal_source_0=None,
                 signal_source_1=None,
                 spi_dac_0=None,
                 spi_dac_1=None,
                 i2c_0=None,
                 i2c_1=None,
                 i2c_2=None,
                 dma=None,
                 rms_dma_channel=1
                 ):

        self.dma_channel = {"rms": rms_dma_channel}
        self.i2c_1 = i2c_1
        self.i2c_2 = i2c_2
        self.pcal6524 = list()

        if not ipcore and not spi_adc and not audio_analyzer and not signal_meter \
           and not signal_source_0 and not signal_source_1 and not spi_dac_0 \
           and not spi_dac_1 and not i2c_0 and not i2c_1 and not i2c_2 and not dma:
            self.dma = MIXDMASGEmulator('dma')
            self.i2c_1 = I2CBusEmulator("i2c_emulator", 256)
            self.i2c_2 = I2CBusEmulator("i2c_emulator", 256)
            self.ltc2378 = LTC2378Emulator("ltc2378")
            self.ad5061_0 = AD5061Emulator("ad5061")
            self.ad5061_1 = AD5061Emulator("ad5061")
            self.eeprom = EepromEmulator('m24128_emulator')
            self.tmp108 = TMP108(SodiumDef.TMP108_DEV_ADDR, self.i2c_1)

            for i in range(SodiumDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524Emulator(SodiumDef.PCAL6524_DEV_ADDR[i], self.i2c_1))
        else:
            if ipcore and i2c_0 and i2c_1 and i2c_2 and dma and not spi_adc and not audio_analyzer \
               and not signal_meter and not signal_source_0 and not signal_source_1 \
               and not spi_dac_0 and not spi_dac_1:
                if isinstance(ipcore, basestring):
                    self.ipcore = MIXSodiumSGR(ipcore)
                else:
                    self.ipcore = ipcore
                self.spi_adc = self.ipcore.spi_adc
                self.signal_meter = self.ipcore.signal_meter
                self.signal_source_0 = self.ipcore.signal_source_0
                self.signal_source_1 = self.ipcore.signal_source_1
                self.spi_dac_0 = self.ipcore.spi_dac_0
                self.spi_dac_1 = self.ipcore.spi_dac_1
            elif not ipcore and i2c_0 and i2c_1 and i2c_2 and dma and spi_adc and audio_analyzer \
                    and signal_source_0 and signal_source_1 and spi_dac_0 and spi_dac_1:
                if isinstance(signal_meter, basestring):
                    self.signal_meter = MIXSignalMeterSG(signal_meter)
                else:
                    self.signal_meter = signal_meter

                if isinstance(spi_adc, basestring):
                    self.spi_adc = PLSPIADC(spi_adc)
                else:
                    self.spi_adc = spi_adc

                if isinstance(audio_analyzer, basestring):
                    self.audio_analyzer = MIXFftAnalyzerSG(audio_analyzer)
                else:
                    self.audio_analyzer = audio_analyzer

                if isinstance(signal_source_0, basestring):
                    self.signal_source_0 = MIXSignalSourceSG(signal_source_0)
                else:
                    self.signal_source_0 = signal_source_0

                if isinstance(signal_source_1, basestring):
                    self.signal_source_1 = MIXSignalSourceSG(signal_source_1)
                else:
                    self.signal_source_1 = signal_source_1

                if isinstance(spi_dac_0, basestring):
                    self.spi_dac_0 = PLSPIDAC(spi_dac_0)
                else:
                    self.spi_dac_0 = spi_dac_0
                if isinstance(spi_dac_1, basestring):
                    self.spi_dac_1 = PLSPIDAC(spi_dac_1)
                else:
                    self.spi_dac_1 = spi_dac_1

            else:
                raise SodiumException("Not allowed to use both aggregated IP and "
                                      "spi_adc,audio_analyzer,signal_meter,"
                                      "signal_source_0,signal_source_1,spi_dac_0,spi_dac_1 at the same time")
            self.dma = dma
            self.ad5061_0 = AD506x(SodiumDef.AD5061_OUTPUT_RANGE[0],
                                   SodiumDef.AD5061_OUTPUT_RANGE[1],
                                   SodiumDef.AD5061_SAMPLE_RATE,
                                   SodiumDef.AD5061_SCK_SPEED,
                                   self.signal_source_0,
                                   self.spi_dac_0)
            self.ad5061_1 = AD506x(SodiumDef.AD5061_OUTPUT_RANGE[0],
                                   SodiumDef.AD5061_OUTPUT_RANGE[1],
                                   SodiumDef.AD5061_SAMPLE_RATE,
                                   SodiumDef.AD5061_SCK_SPEED,
                                   self.signal_source_1,
                                   self.spi_dac_1)
            self.ltc2378 = LTC2378(self.signal_meter,
                                   self.spi_adc,
                                   None,
                                   SodiumDef.LTC2378_VOLT_RANGE)
            self.eeprom = M24128(SodiumDef.M24128_DEV_ADDR, self.i2c_1)
            self.pcal6524 = list()
            for i in range(SodiumDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524(SodiumDef.PCAL6524_DEV_ADDR[i], self.i2c_1))
            self.tmp108 = TMP108(SodiumDef.TMP108_DEV_ADDR, self.i2c_2)

        self.waveforms = {0: self.ad5061_0, 1: self.ad5061_1}

        super(Sodium, self).__init__(self.eeprom, self.tmp108)

    def module_init(self):
        '''
        Module init

        Returns:
            string, "done", api execution successful.

        Examples:
            sodium.module_init()

        '''
        # set these IO as output.
        self.io_dir_set([(SodiumDef.M24128_WR_EN_PIN, 0)])
        self.io_set([(SodiumDef.M24128_WR_EN_PIN, 0)])

        # set these IO as input.
        self.io_dir_set([(SodiumDef.TMP108_ALERT_PIN, 1)])

        # configure DMA
        self.dma.config_channel(self.dma_channel['rms'], SodiumDef.DMA_SIZE)
        return 'done'

    def io_dir_set(self, io_list):
        '''
        Sodium set io direction state.

        Args:
            io_list: list, [(pinX, state),...], pinX  (int), 1 <= pinX <= 48
                                                state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            sodium.io_dir_set([(1,0),(2,0)])

        '''

        io_list = sorted(io_list)
        io_info = [[] for i in range(SodiumDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // SodiumDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % SodiumDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_dir(io_list)
            chip_num += 1
        return 'done'

    def io_set(self, io_list):
        '''
        Sodium set IO output state.

        Args:
            io_list: list, [(pinX, state),...], pinX  (int), 1 <= pinX <= 48
                                                state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            sodium.io_set([(1,0),(2,0)])

        '''
        io_list = sorted(io_list)
        io_info = [[] for i in range(SodiumDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // SodiumDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % SodiumDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_state(io_list)
            chip_num += 1
        return 'done'

    def io_read(self, io_list):
        '''
        Sodium read IO output state.

        Args:
            io_list:    list, [pinX,...], pinX  (int), 1 <= pinX <= 48.

        Returns:
            list, [(pinX, level)...], eg: [(1,0), (2,1)].

        Examples:
            sodium.io_read([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(SodiumDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // SodiumDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % SodiumDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_state(io)
                for num in ret:
                    num[0] += chip_num * SodiumDef.PCAL6524_PIN_CNT + 1
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

    def io_dir_read(self, io_list):
        '''
        Sodium read IO direction.

        Args:
            io_list:    list, [pinX,...], pinX  (int), 1 <= pinX <= 48.

        Returns:
            list, [(pinX, level)...], eg: [(1,0), (2,1)].

        Examples:
            sodium.io_read_dir([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(SodiumDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // SodiumDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % SodiumDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_dir(io)
                for num in ret:
                    num[0] += chip_num * SodiumDef.PCAL6524_PIN_CNT + 1
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

    def ltc2378_get_raw_data(self, channel):
        '''
        read ltc2378 data with dma channel

        Args:
            channel:    string, ["rms"], RMS DMA channel.

        Returns:
            list/string, if success return a list else return string
                 eg:
                    def data_2_volt(raw_data):
                        adc_resolution = 20 # LTC2378 resolution
                        vref = 4096.0  # mV, change the reference according the vref pin of LTC2378
                        if (raw_data >> (adc_resolution - 1)) & 0x1:
                            raw_data -= 1 << adc_resolution
                        voltage = raw_data * vref / (1 << (adc_resolution - 1))
                        return voltage  # mV
                    raw_data = solaris.ltc2378_get_raw_data("rms")
                    if raw_data = [0x00, 0x10, 0x34, 0x56, 0x00,...]
                    # every 4 bytes consist of one ADC data, only 20 bit effective
                    code = (raw_data[1] >> 4) | raw_data[2] << 4 | raw_data[3] << 12
                    volt = data_2_volt(code) # get the voltage
                    handle next 4 byte in raw_data
        '''
        assert channel == 'rms'
        result, data, data_num, overflow = self.dma.read_channel_all_data(self.dma_channel[channel])
        self.dma.read_done(self.dma_channel[channel], data_num)
        if result != 0 or overflow == 1:
            return 'error'
        else:
            return data[:data_num]

    def _ad5061_output_type(self, volt_list, output_type):
        '''
        Internal funciton. This Function to calculate voltage

        Args:
            volt_list:      list, raw voltage list
            output_type:    string, ['bip', 'bip_div', 'raw'].

        Returns:
            list/string,  eg: [-2048, 2048] or 'error'.

        '''
        if output_type == 'bip':
            return [(volt + SodiumDef.AD5061_OFFSET) / SodiumDef.AD5061_GAIN for volt in volt_list]
        elif output_type == 'bip_div':
            return [(volt * SodiumDef.AD5061_BIP_DIV_GAIN + SodiumDef.AD5061_OFFSET) /
                    SodiumDef.AD5061_GAIN for volt in volt_list]
        elif output_type == 'raw':
            return volt_list
        else:
            return 'error'

    def sine(self, channel, vpp, offset, freq, output_type='bip'):
        '''
        Sodium function to output sine waveform

        Args:
            channel:      int, [0, 1], The channel to output waveform.
            vpp:          float, [0~4096], unit mV, The waveform vpp voltage.
            offset:       float, [-2048~2048], unit mV, The waveform offset voltage.
            freq:         float, [0.01~500], unit Hz, The waveform frequency.
            output_type:  string, ['bip', 'bip_div', 'raw'], default 'bip', Select output type.

        Returns:
            string, ["done", "error"].

        Examples:
            sodium.sine(0, 1000, 2000, 100)

        '''
        assert channel in [0, 1]
        assert 0 <= vpp <= SodiumDef.AD5061_OUTPUT_RANGE[1] * 2
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= offset <= SodiumDef.AD5061_OUTPUT_RANGE[1]

        if output_type == 'bip':
            vpp = vpp / SodiumDef.AD5061_GAIN
            offset = self._ad5061_output_type([offset], output_type)[0]
        elif output_type == 'bip_div':
            vpp = vpp * SodiumDef.AD5061_BIP_DIV_GAIN / SodiumDef.AD5061_GAIN
            offset = self._ad5061_output_type([offset], output_type)[0]
        elif output_type == 'raw':
            vpp = vpp
            offset = self._ad5061_output_type([offset], output_type)[0]

        self.waveforms[channel].sine(vpp, offset, freq)
        return 'done'

    def dc(self, channel, volt, output_type='bip'):
        '''
        Sodium output dc voltage

        Args:
            channel:      int, [0, 1], The channel to output waveform.
            volt:         float, [-2048~2048], unit mV, Output votlage value.
            output_type:  string, ['bip', 'bip_div', 'raw'], default 'bip', Select output type.

        Returns:
            string, ["done", "error"].

        Examples:
            sodium.dc(0, 1000)

        '''
        assert channel in [0, 1]
        assert output_type in SodiumDef.DAC_OUTPUT_OPTIONS
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= volt <= SodiumDef.AD5061_OUTPUT_RANGE[1]

        volt = self._ad5061_output_type([volt], output_type)[0]
        # AD5061 has one channel, so the channel parameter is 0.
        self.waveforms[channel].output_volt_dc(0, volt)
        return 'done'

    def pulse(self, channel, v1, v2, edge, pulse, period, output_type='bip'):
        '''
        Sodium output pulse waveform

        Args:
            channel:       int, [0, 1], The channel to output pulse.
            v1:            float, [-2048~2048], unit mV, start voltage of pulse.
            v2:            float, [-2048~2048], unit mV, end voltage of pulse.
            edge:          float, unit ms, Pulse edge width.
            pulse:         float, unit ms, Pulse width.
            period:        float, unit ms, Pulse period, include pulse width, edge width and DC width.
            output_type:   string, ['bip', 'bip_div', 'raw'], default 'bip', Voltage output type.

        Returns:
            string, ["done", "error"].

        Examples:
            sodium.pulse(0, 1000, 0, 100, 200, 2000)

        '''
        assert channel in [0, 1]
        assert output_type in SodiumDef.DAC_OUTPUT_OPTIONS
        assert pulse > 0
        assert edge > 0
        assert pulse + edge * 2 < period
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= v1 <= SodiumDef.AD5061_OUTPUT_RANGE[1]
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= v2 <= SodiumDef.AD5061_OUTPUT_RANGE[1]

        v1, v2 = self._ad5061_output_type([v1, v2], output_type)
        self.waveforms[channel].pulse(v1, v2, edge, pulse, period)
        return 'done'

    def triangle(self, channel, v1, v2, triangle, period, output_type='bip'):
        '''
        Sodium output triangle waveform

        Args:
            channel:       int, [0, 1], The channel to output pulse.
            v1:            float, [-2048~2048], unit mV, start voltage of pulse.
            v2:            float, [-2048~2048], unit mV, end voltage of pulse.
            triangle:      float, unit ms, Triangle width.
            period:        float, unit ms, Pulse period, include pulse width, edge width and DC width.
            output_type:   string, ['bip', 'bip_div', 'raw'], default 'bip', Voltage output type.

        Returns:
            string, ["done", "error"].

        Examples:
            sodium.triangle(0, 1000, 0, 100000, 200000)
        '''
        assert channel in [0, 1]
        assert output_type in SodiumDef.DAC_OUTPUT_OPTIONS
        assert triangle > 0
        assert triangle < period
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= v1 <= SodiumDef.AD5061_OUTPUT_RANGE[1]
        assert -SodiumDef.AD5061_OUTPUT_RANGE[1] <= v2 <= SodiumDef.AD5061_OUTPUT_RANGE[1]

        v1, v2 = self._ad5061_output_type([v1, v2], output_type)
        self.waveforms[channel].triangle(v1, v2, triangle, period)
        return 'done'

    def rms_measure(self, measure_time, vpp_interval,
                    sample_rate=SodiumDef.RMS_SAMPLE_RATE, upload_state="off"):
        '''
        Sodium board measure rms,vpp,max,min,average

        Args:
            measure_time:     int, [1~65535], unit ms.
            vpp_interval:     int, [1~65535], unit ms, the interval time of VPP measurement.
            sample_rate:      int, default 256000, Measure sample rate.
            upload_state:     string, ["on", "off"], default "off", "on": enable upload ADC raw data,
                                                                    "off": disable upload ADC raw data.

        Returns:
            string, str, if success, return "average: 320.2312 mV, max: 604.3001 mV,
                         min: 102.3100 mV,vpp: 321.31 mV, rms: 234.2100 mV", else return "error"

        Examples:
            upload_state = 'on'
            time_ms = 1000
            interval_ms = 500
            sodium.rms_measure(time_ms, interval_ms, upload_state)

        '''
        assert 0 < measure_time < SodiumDef.LTC2378_MAX_MEASURE_TIME
        assert 0 < vpp_interval <= measure_time
        assert upload_state in ("on", "off")

        self.dma.reset_channel(self.dma_channel['rms'])
        self.dma.disable_channel(self.dma_channel['rms'])
        if upload_state == 'on':
            self.dma.enable_channel(self.dma_channel['rms'])
        result = self.ltc2378.measure_rms_average_amplitude_max_min(
            sample_rate, measure_time, upload_state, vpp_interval, 'DEBUG')

        return "average: %0.4f mV,max: %0.4f mV, min: %0.4f mV, vpp: %0.4f mV, rms: %0.4f mV"\
            % (result['avg'] * SodiumDef.ADC_GAIN, result['max'] * SodiumDef.ADC_GAIN,
               result['min'] * SodiumDef.ADC_GAIN, result['vpp'] * SodiumDef.ADC_GAIN,
               result['rms'] * SodiumDef.ADC_GAIN)

    def voltage_measure(self):
        '''
        Sodium measure voltage

        Returns:
            string, str, unit mV, eg: "1000.0000 mV".

        Examples:
            sodium.voltage_measure()

        '''
        ret = self.ltc2378.read_volt() * SodiumDef.ADC_GAIN
        return "%0.4f mV" % ret

    def disable_waveform(self, channel=0xFF):
        '''
        Sodium disable waveform output

        Args:
            channel: int, default 0xFF, The channel to disable waveform output.

        Returns:
            string, "done", api execution successful.

        Examples:
            sodium.disable_waveform(0xFF)

        '''
        if channel == 0xFF:
            self.waveforms[0].disable_output()
            self.waveforms[1].disable_output()
        else:
            self.waveforms[channel].disable_output()
        return 'done'
