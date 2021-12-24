# -*- coding: utf-8 -*-
import time
from mix.driver.core.ic.m24cxx import M24128
from mix.driver.core.ic.pcal6524 import PCAL6524
from mix.driver.core.ic.pcal6524_emulator import PCAL6524Emulator
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.smartgiant.common.ic.ad5272_emulator import AD5272Emulator
from mix.driver.smartgiant.common.ic.ad527x import AD5272
from mix.driver.smartgiant.common.ic.ad57x1r import AD5761, AD57X1RDef
from mix.driver.smartgiant.common.ic.ad5761_emulator import AD5761Emulator
from mix.driver.smartgiant.common.ic.adg2128 import ADG2128
from mix.driver.smartgiant.common.ic.adg2128_emulator import ADG2128Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ic.ltc2378_emulator import LTC2378Emulator
from mix.driver.smartgiant.common.ic.ltc2378 import LTC2378, LTC2378Def
from mix.driver.smartgiant.common.ic.tmp10x import TMP108
from mix.driver.smartgiant.common.ipcore.mix_dma_sg_emulator import MIXDMASGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_dac_emulator import PLSPIDACEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.pl_spi_adc import PLSPIADC
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.smartgiant.common.ipcore.mix_solaris_sg_r import MIXSolarisSGR
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.utility.data_operate import DataOperate


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = '0.1'


class SolarisDef:
    # DMA
    DMA_SIZE = 16 * 1024 * 1024  # 16Mbytes
    DMA_READ_SIZE = 2048     # read 2048 bytes once
    DMA_TIMEOUT_MS = 3000

    SWITCH_DELAY_S = 0.001

    # AD5761
    # AD5761 and ADATE304 share one SPI bus,
    # bit16: switch spi bus for AD5761 or ADATE304,
    # bit16=0:AD5761; bit16=1:ADATE304
    # bit17: switch control AD5761 register or control AD5761 output waveform
    # bit17=0: control AD5761 register, bit17=1: control AD5761 output waveform

    AD5761_REG_CONTROL = [[17, 0], [16, 0]]
    AD5761_WAVEFORM_CONTROL = [[17, 1], [16, 0]]

    AD5761_SPI_DAC_SCK = 10000000  # unit: Hz
    AD5761_SPI_SCK = 10000000  # unit: Hz
    AD5761_SAMPLE_RATE = 200000  # unit: SPS
    AD5761_SPI_MODE = 0x3
    AD5761_RST_PIN = 21
    AD5761_CLEAR_PIN = 22
    AD5761_LDAC_PIN = 23
    AD5761_ALERT_PIN = 24
    # range: -2500~7500 mV, Power-up voltage: midscale
    AD5761_CTRL_REG_DEF_VAL = 0x16C
    ALWAYS_OUTPUT = 0xFFFFFF
    AWG_VALUE_MAX = 0.9999
    AWG_VALUE_MIN = -0.9999
    SINE_VALUE_MAX = 0.9999
    SINE_VALUE_MIN = 0.0
    SINE_OFFSET_MAX = 0.9999
    SINE_OFFSET_MIN = -0.9999

    # LTC2378
    LTC2378_VOLT_RANGE = [-5000, 5000]  # unit: mV
    LTC2378_VREF = 5000.0  # unit: mV
    RMS_SAMPLE_RATE = 256000  # unit: SPS
    THDN_SAMPLE_RATE = 192000  # unit: SPS
    LTC2378_IPCORE_GPIO = 11
    LTC2378_RMS = 0
    LTC2378_THDN = 1
    LTC2378_THDN_MAX_BANDWIDTH = 200000
    LTC2378_MAX_DECIMATION = 0xFF

    # AD5272
    AD5272_RESET_PIN = 17
    AD5272_DEV_ADDR = 0x2E
    AD5272_WRITE_CTRL_REG_CMD = 0x7
    AD5272_EANBLE_RDAC = 0x2
    AD5272_MAX_RESISTOR_VAL = 100000.0

    # M24128
    M24128_DEV_ADDR = 0x50
    M24128_WR_EN_PIN = 5

    # TMP108
    TMP108_DEV_ADDR = 0x49
    TMP108_ALERT_PIN = 89

    # ADG2128
    ADG2128_NUM = 18
    ADG2128_RESET_PIN = 1
    ADG2128_DEV_ADDR = [0x70 + i for i in range(8)]

    # PCAL6524
    # Solaris has 4 pieces of PCAL6524, the device addresses are 0x20, 0x21, 0x22, 0x23.
    PCAL6524_CHIP_NUM = 4
    PCAL6524_DEV_ADDR = [0x20 + i for i in range(PCAL6524_CHIP_NUM)]
    PCAL6524_PIN_CNT = 24

    # signal meter
    PL_SIGNAL_METER_MODULE_ENABLE_ADDR = 0x10
    PL_SIGNAL_METER_MEASURE_TIME_LOW_ADDR = 0x11
    PL_SIGNAL_METER_MEASURE_CTRL_ADDR = 0x13
    PL_SIGNAL_METER_MEASURE_TIME_HIGH_ADDR = 0x1A
    PL_SIGNAL_METER_MEASURE_MAX_ADDR = 0x1C
    PL_SIGNAL_METER_MEASURE_MIN_ADDR = 0x0C


class SolarisException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Solaris(MIXBoard):
    '''
    Solaris function class

    Args:
        i2c_0:            instance(I2C)/None, instance of PLI2CBus, which is used to control (pcal6524,
                                              adg2128, m24128).
        i2c_1:            instance(I2C)/None, instance of PLI2CBus, which is used to control adg2128.
        i2c_2:            instance(I2C)/None, instance of PLI2CBus, which is used to control (tmp108,
                                              adg2128 and ad5272).
        dma:              instance(DMA)/None, Class instance of DMA.
        thdn_dma_channel: int, channel of Dma, which is used to determine thdn upload channel.
        rms_dma_channel:  int, channel of Dma, which is used to determine rms upload channel.
        ipcore:               instance(MIXDAQT1)/None, instance of MIX_DAQT1, which is used to control {PLSignalMeter,
                                                   PLGPIO,PLSignalSource,PLFFTAnalyzer,PLSPIAdc,PLSPIDAC,PLSPIBus).
        meter:            instance(PLSignalMeter)/string/None, Class instance of PLSignalMeter.
        spi_adc:          instance(QSPI)/string/None, Class instance of PLSPIAdc.
        audio:            instance(PLFFTAnalyzer)/string/None, Class instance of PLFFTAnalyzer.
        spi_bus:          instance(QSPI)/None, Class instance of PLSPIBus.
        source:           instance(PLSignalSource)/string/None, Class instance of PLSignalSource.
        gpio:             instance(GPIO)/None, Class instance of PLGPIO.
        spi_dac:          instance(QSPI)/string/None, Class instance of PLSPIDAC.
        ad5761_mvref:     int,                 the reference voltage of ad5761.

    Examples:
        # use non-aggregated IP
        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')
        dma = DMA('/dev/MIX_DMA_0')
        thdn_dma_channel = 2
        rms_dma_channel = 1

        ipcore = None

        meter = PLSignalMeter('/dev/MIX_SignalMeter_0')
        spi_adc = PLSPIAdc('/dev/MIX_SPIADC_0')
        audio = PLFFTAnalyzer('/dev/MIX_FFT_Analyzer_0')
        spi_bus = PLSPIBus('/dev/MIX_SPI_0')
        source = PLSignalSource('/dev/MIX_Signal_Source_0')
        gpio = PLGPIO('/dev/MIX_GPIO')
        spi_dac = PLSPIDAC('/dev/MIX_SPIDAC_0')
        solaris = Solaris(i2c_0, i2c_1, i2c_2, dma, thdn_dma_channel, rms_dma_channel, ipcore,
                          meter, spi_adc, audio, spi_bus, source, gpio, spi_dac)

        # use MIXSolaris aggregated IP
        i2c_0 = I2C('/dev/i2c-0')
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-2')
        dma = Dma('/dev/MIX_DMA_0')
        thdn_dma_channel = 2
        rms_dma_channel = 1

        ipcore = MIXSolaris('/dev/MIX_Solaris')
        solaris = Solaris(i2c_0, i2c_1, i2c_2, dma, thdn_dma_channel, rms_dma_channel, ipcore)

    '''

    rpc_public_api = ['module_init', 'io_dir_set', 'io_dir_read', 'io_set', 'io_read',
                      'adg2128_set_xy_state', 'adg2128_get_xy_state', 'ltc2378_get_raw_data',
                      'ltc2378_get_raw_data_by_len', 'adg2128_reset', 'voltage_measure', 'voltage_output',
                      'rms_measure', 'ad5761_readback_voltage', 'enable_ad5272', 'set_resistor_value',
                      'read_resistor', 'set_resistor_mode', 'measure_thdn', 'ad5761_set_control_register',
                      'triangle', 'pulse', 'disable_waveform', 'dc',
                      'sine', 'get_adc_max_min', 'enable_upload', 'disable_upload'] + MIXBoard.rpc_public_api

    def __init__(self,
                 i2c_0=None,
                 i2c_1=None,
                 i2c_2=None,
                 dma=None,
                 thdn_dma_channel=2,
                 rms_dma_channel=1,
                 ipcore=None,
                 meter=None,
                 spi_adc=None,
                 audio=None,
                 spi_bus=None,
                 source=None,
                 gpio=None,
                 spi_dac=None,
                 ad5761_mvref=2500):
        self.ipcore = ipcore
        self.pcal6524 = list()
        self.adg2128 = list()
        self.i2c_0 = i2c_0
        self.i2c_1 = i2c_1
        self.i2c_2 = i2c_2
        self.dma_inited = False
        self.dma_channel = {"rms": rms_dma_channel, "thdn": thdn_dma_channel}

        if not ipcore and not i2c_0 and not i2c_1 and not i2c_2 and not dma \
           and not meter and not spi_adc and not audio and not spi_bus \
           and not source and not gpio and not spi_dac:
            self.i2c_0 = I2CBusEmulator("i2c_emulator", 256)
            self.i2c_1 = I2CBusEmulator("i2c_emulator", 256)
            self.i2c_2 = I2CBusEmulator("i2c_emulator", 256)
            self.eeprom = EepromEmulator('m24128_emulator')
            self.ltc2378 = LTC2378Emulator("ltc2378")
            self.ad5761 = AD5761Emulator("ad5761")
            self.gpio = MIXGPIOSGEmulator("gpio", 256)
            self.signal_source = MIXSignalSourceSGEmulator("pl_signal_source_emulator")
            self.spi_dac = PLSPIDACEmulator("pl_spi_dac_emulator")
            self.dma = MIXDMASGEmulator('dma')
            self.eeprom = EepromEmulator('m24128_emulator')
            for i in range(SolarisDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524Emulator(SolarisDef.PCAL6524_DEV_ADDR[i],
                                                      self.i2c_0))
            for i in range(8):
                self.adg2128.append(ADG2128Emulator(SolarisDef.ADG2128_DEV_ADDR[i]))
            for i in range(8):
                self.adg2128.append(ADG2128Emulator(SolarisDef.ADG2128_DEV_ADDR[i]))
            self.tmp108 = TMP108(SolarisDef.TMP108_DEV_ADDR, self.i2c_2)
            self.ad5272 = AD5272Emulator("ad5272")
            for i in range(2):
                self.adg2128.append(ADG2128Emulator(SolarisDef.ADG2128_DEV_ADDR[i]))

        else:
            if ipcore and i2c_0 and i2c_1 and i2c_2 and dma \
               and not meter and not spi_adc and not audio and not spi_bus \
               and not source and not gpio and not spi_dac:
                if isinstance(ipcore, basestring):
                    self.ipcore = MIXSolarisSGR(ipcore)
                self.ltc2378 = LTC2378(self.ipcore.meter, self.ipcore.spi_adc,
                                       self.ipcore.audio, SolarisDef.LTC2378_VOLT_RANGE)
                self.ad5761 = AD5761(ad5761_mvref, self.ipcore.spi_bus)
                self.gpio = self.ipcore.gpio
                self.signal_source = self.ipcore.source
                self.spi_dac = self.ipcore.spi_dac
            elif not ipcore and i2c_0 and i2c_1 and i2c_2 and dma and \
                meter and spi_adc and audio and spi_bus \
                    and source and gpio and spi_dac:
                if isinstance(meter, basestring):
                    meter = MIXSignalMeterSG(meter)
                if isinstance(spi_adc, basestring):
                    spi_adc = PLSPIADC(spi_adc)
                if isinstance(audio, basestring):
                    audio = MIXFftAnalyzerSG(audio)
                if isinstance(source, basestring):
                    source = MIXSignalSourceSG(source)
                if isinstance(spi_dac, basestring):
                    spi_dac = PLSPIDAC(spi_dac)

                self.ltc2378 = LTC2378(meter, spi_adc, audio, SolarisDef.LTC2378_VOLT_RANGE)
                self.ad5761 = AD5761(ad5761_mvref, spi_bus)
                self.gpio = gpio
                self.signal_source = source
                self.spi_dac = spi_dac
            else:
                raise SolarisException('Not allowed to use both aggregated IP and\
                      meter,spi_adc,audio,spi_bus,source,gpio,spi_dac at the same time')
            self.dma = dma

            self.eeprom = M24128(SolarisDef.M24128_DEV_ADDR, self.i2c_0)

            for i in range(SolarisDef.PCAL6524_CHIP_NUM):
                self.pcal6524.append(PCAL6524(SolarisDef.PCAL6524_DEV_ADDR[i],
                                              self.i2c_0))
            for i in range(8):
                self.adg2128.append(ADG2128(SolarisDef.ADG2128_DEV_ADDR[i],
                                            self.i2c_0))

            for i in range(8):
                self.adg2128.append(ADG2128(SolarisDef.ADG2128_DEV_ADDR[i],
                                            self.i2c_1))

            self.tmp108 = TMP108(SolarisDef.TMP108_DEV_ADDR, self.i2c_2)
            self.ad5272 = AD5272(SolarisDef.AD5272_DEV_ADDR, self.i2c_2)
            for i in range(2):
                self.adg2128.append(ADG2128(SolarisDef.ADG2128_DEV_ADDR[i],
                                            self.i2c_2))

        super(Solaris, self).__init__(self.eeprom, self.tmp108)

    def module_init(self):
        '''
        Solaris module initialization

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.module_init()

        '''

        # set these IO as output.
        self.io_dir_set([(SolarisDef.ADG2128_RESET_PIN, 0)])
        self.io_set([(SolarisDef.ADG2128_RESET_PIN, 1)])

        self.io_dir_set([(SolarisDef.AD5272_RESET_PIN, 0)])
        self.io_set([(SolarisDef.AD5272_RESET_PIN, 1)])

        self.io_dir_set([(SolarisDef.M24128_WR_EN_PIN, 0)])
        self.io_set([(SolarisDef.M24128_WR_EN_PIN, 0)])

        self.io_dir_set([(SolarisDef.AD5761_RST_PIN, 0)])
        self.io_set([(SolarisDef.AD5761_RST_PIN, 1)])
        self.io_dir_set([(SolarisDef.AD5761_CLEAR_PIN, 0)])
        self.io_set([(SolarisDef.AD5761_CLEAR_PIN, 1)])
        self.io_dir_set([(SolarisDef.AD5761_LDAC_PIN, 0)])
        self.io_set([(SolarisDef.AD5761_LDAC_PIN, 0)])

        # set these IO as input.
        self.io_dir_set([(SolarisDef.AD5761_ALERT_PIN, 1)])
        self.io_dir_set([(SolarisDef.TMP108_ALERT_PIN, 1)])

        self.spi_dac.open()
        self.spi_dac.dac_mode_set(SolarisDef.AD5761_SPI_MODE)
        self.spi_dac.spi_sclk_frequency_set(SolarisDef.AD5761_SPI_DAC_SCK)
        self.spi_dac.sample_data_set(SolarisDef.AD5761_SAMPLE_RATE)

        self.ad5761.spi_bus.set_mode("MODE2")
        self.ad5761.spi_bus.set_speed(SolarisDef.AD5761_SPI_SCK)
        self.ad5761_set_control_register(SolarisDef.AD5761_CTRL_REG_DEF_VAL)

        if not self.dma_inited:
            self.dma.reset_channel(self.dma_channel["rms"])
            self.dma.disable_channel(self.dma_channel["rms"])
            self.dma.config_channel(self.dma_channel["rms"], SolarisDef.DMA_SIZE)

            self.dma.reset_channel(self.dma_channel["thdn"])
            self.dma.disable_channel(self.dma_channel["thdn"])
            self.dma.config_channel(self.dma_channel["thdn"], SolarisDef.DMA_SIZE)
            self.dma_inited = True

        return 'done'

    def io_dir_set(self, io_list):
        '''
        Solaris set io direction state.

        Args:
            io_list: list, [(pinX, state),(pinX, state),...], pinX  (int), 1 <= pinX <= 96
                                                              state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.io_dir_set([(1,0),(2,0)])

        '''
        assert isinstance(io_list, list)
        io_list = sorted(io_list)
        io_info = [[] for i in range(SolarisDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // SolarisDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % SolarisDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_dir(io_list)
            chip_num += 1
        return "done"

    def io_dir_read(self, io_list):
        '''
        Solaris read IO direction.

        Args:
            io_list:    list, [pinX,...], pinX  (int), 1 <= pinX <= 48.

        Returns:
            list, [(pinX, level)...], eg: [(1,0), (2,1)].

        Examples:
            solaris.io_read_dir([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(SolarisDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // SolarisDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % SolarisDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_dir(io)
                for num in ret:
                    num[0] += chip_num * SolarisDef.PCAL6524_PIN_CNT + 1
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

    def io_set(self, io_list):
        '''
        Solaris set IO output state.

        Args:
            io_list: list, [(pinX, state),...], pinX  (int), 1 <= pinX <= 96
                                                state (int), 0(output) or 1(input).

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.io_set([(1,0),(2,0)])

        '''
        assert isinstance(io_list, list)
        io_list = sorted(io_list)
        io_info = [[] for i in range(SolarisDef.PCAL6524_CHIP_NUM)]
        for io in io_list:
            chip_num = (io[0] - 1) // SolarisDef.PCAL6524_PIN_CNT
            io_num = (io[0] - 1) % SolarisDef.PCAL6524_PIN_CNT
            io_info[chip_num].append((io_num, io[1]))
        chip_num = 0
        for io_list in io_info:
            if io_list:
                self.pcal6524[chip_num].set_pins_state(io_list)
            chip_num += 1
        return 'done'

    def io_read(self, io_list):
        '''
        Solaris read IO output state.

        Args:
            io_list:    list, [pinX,...], pinX  (int), 1 <= pinX <= 96.

        Returns:
            list, [(pinX, level)...], eg: [(1,0), (2,1)].

        Examples:
            sodium.io_read([1,2])

        '''

        io_list_tmp = sorted(io_list)
        io_info = [[] for i in range(SolarisDef.PCAL6524_CHIP_NUM)]
        for io in io_list_tmp:
            chip_num = (io - 1) // SolarisDef.PCAL6524_PIN_CNT
            io_num = (io - 1) % SolarisDef.PCAL6524_PIN_CNT
            io_info[chip_num].append(io_num)

        chip_num = 0
        io_state = []
        for io in io_info:
            if io:
                ret = self.pcal6524[chip_num].get_pins_state(io)
                for num in ret:
                    num[0] += chip_num * SolarisDef.PCAL6524_PIN_CNT + 1
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

    def adg2128_set_xy_state(self, chip, switch_val):
        '''
        Solaris ADG2128 get the xy state

        Args:
            chip:            int, [0~18].
            switch_val:      list, eg: [[1,2], [3,4]] means witch X1Y2 and switch X3Y4.

        Raise:
            keyError: ADG2128Exception

        Returns:
            list, eg: [[1,2,1], [3,4,0]] means X1Y2=1, X3Y4=0.

        Examples:
            rd_data = solaris.adg2128_set_xy_state(0,[[1,2], [3,4]])

        '''
        assert chip in range(0, SolarisDef.ADG2128_NUM)
        self.adg2128[chip].set_xy_state(switch_val)
        return 'done'

    def adg2128_get_xy_state(self, chip, switch_val):
        '''
        Solaris ADG2128 get the xy state

        Args:
            chip:            int, [0~18].
            switch_val:      list, eg: [[1,2], [3,4]] means witch X1Y2 and switch X3Y4.

        Raise:
            keyError: ADG2128Exception

        Returns:
            list, eg: [[1,2,1], [3,4,0]] means X1Y2=1, X3Y4=0.

        Examples:
            rd_data = solaris.adg2128_get_xy_state(0,[[1,2], [3,4]])

        '''
        assert chip in range(0, SolarisDef.ADG2128_NUM)
        return self.adg2128[chip].get_xy_state(switch_val)

    def ltc2378_get_raw_data(self, channel):
        '''
        Solaris read ltc2378 data with dma channel

        Args:
            channel: string, ["rms", "thdn"], THDN DMA channel or RMS DMA channel.

        Returns:
            list/string, if success return a list else return string, eg:[1, 2, 3] or 'error'.

        Examples:
            def data_2_volt(raw_data):
                adc_resolution = 20 # LTC2378 resolution
                vref = 5000.0  # mV, change the reference according the vref pin of LTC2378
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
        assert channel in self.dma_channel.keys()
        result, data, data_num, overflow = self.dma.read_channel_all_data(self.dma_channel[channel])
        self.dma.read_done(self.dma_channel[channel], data_num)
        if result != 0 or overflow == 1:
            return 'error'
        else:
            return data[:data_num]

    def ltc2378_get_raw_data_by_len(self, channel, read_len=1024, time_out=100):
        '''
        Solaris read ltc2378 data with dma channel

        Args:
            channel:   string, ["rms", "thdn"], THDN DMA channel or RMS DMA channel.
            read_len:  int, default 1024, read the data from the dma.
            time_out:  int, default 100, unit ms, read the data time.

        Returns:
            list/string, if success return a list else return string, eg:[1, 2, 3] or 'error'.

        Examples:
            def data_2_volt(raw_data):
                adc_resolution = 20 # LTC2378 resolution
                vref = 5000.0  # mV, change the reference according the vref pin of LTC2378
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
        assert channel in self.dma_channel.keys()
        result, data, data_num, overflow = self.dma.read_channel_data(self.dma_channel[channel], read_len, time_out)
        self.dma.read_done(self.dma_channel[channel], data_num)
        if result != 0 or overflow == 1:
            return 'error'
        else:
            return data[:data_num]

    def adg2128_reset(self):
        '''
        Solaris board reset adg2128

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.adg2128_reset()

        '''
        # set io diction as output
        self.io_set([(SolarisDef.ADG2128_RESET_PIN, 0)])
        time.sleep(SolarisDef.SWITCH_DELAY_S)
        self.io_set([(SolarisDef.ADG2128_RESET_PIN, 1)])
        return 'done'

    def voltage_measure(self):
        '''
        Solaris board ltc2378 measure voltage

        Returns:
            float, value, unit mV.

        Examples:
            solaris.voltage_measure()

        '''

        return self.ltc2378.read_volt()

    def voltage_output(self, channel, volt):
        '''
        Solaris board AD5761 output DC voltage, SPI bus refresh the AD5761 data register once.

        Args:
            channel: int, [0], The channel to output voltage.
            volt: float, unit mV.

        Returns:
            string, ['done', "error"].

        Examples:
            volt = 1000
            solaris.voltage_output(volt)

        '''
        assert channel == 0
        assert self.ad5761.min_output_volt <= volt <= self.ad5761.max_output_volt

        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_REG_CONTROL]
        self.ad5761.output_volt_dc(0, volt)
        return 'done'

    def rms_measure(self, measure_time, vpp_interval,
                    sample_rate=SolarisDef.RMS_SAMPLE_RATE, upload_state="off"):
        '''
        Solaris board measure rms,vpp,max,min,average

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
            solaris.rms_measure(time_ms, interval_ms, upload_state)

        '''
        assert isinstance(measure_time, int) or measure_time > 0
        assert isinstance(vpp_interval, int) and vpp_interval <= measure_time
        assert upload_state in ("on", "off")

        self.gpio.set_pin(SolarisDef.LTC2378_IPCORE_GPIO, SolarisDef.LTC2378_RMS)

        self.dma.reset_channel(self.dma_channel["rms"])
        self.dma.disable_channel(self.dma_channel["rms"])
        if upload_state == 'on':
            self.dma.enable_channel(self.dma_channel["rms"])
        result = self.ltc2378.measure_rms_average_amplitude_max_min(
            sample_rate, measure_time, upload_state, vpp_interval, 'DEBUG')

        return "average: %0.4f mV,max: %0.4f mV, min: %0.4f mV, vpp: %0.4f mV, rms: %0.4f mV"\
            % (result["avg"], result['max'], result["min"], result["vpp"], result["rms"])

    def ad5761_readback_voltage(self):
        '''
        Solaris board read back voltage

        Returns:
            float, value, unit mV.

        Examples:
            solaris.ad5761_readback_voltage()

        '''
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_REG_CONTROL]
        volt = self.ad5761.readback_output_voltage()
        return volt

    def enable_ad5272(self):
        '''
        Solaris board enable AD5272, allow update of wiper position through a digital interface.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.enable_ad5272()

        '''
        self.ad5272.write_command(SolarisDef.AD5272_WRITE_CTRL_REG_CMD,
                                  SolarisDef.AD5272_EANBLE_RDAC)
        return 'done'

    def set_resistor_value(self, resistor_value):
        '''
        Set the resistor of the solaris

        Args:
            resistor_value:  float, [0~100K], unit ohm, the value of the resistor set.

        Returns:
            string, ["done", "error"].

        Examples:
            resistor_value = 100.0
            solaris.set_resistor_value(resistor_value)

        '''
        assert isinstance(resistor_value, (int, float))
        assert 0 <= resistor_value <= SolarisDef.AD5272_MAX_RESISTOR_VAL
        self.ad5272.set_resistor(resistor_value)
        return 'done'

    def read_resistor(self):
        '''
        Read the resistor of the solaris

        Returns:
            float, value, unit ohm.

        Examples:
            solaris.read_resistor()

        '''

        return self.ad5272.get_resistor()

    def set_resistor_mode(self, mode):
        '''
        Set the mode of the resistor

        Args:
            mode:       string, ['normal', 'shutdown'], the mode set.

        Returns:
            string, ["done", "error"].

        Examples:
            mode = 'shutdown'
            solaris.set_resistor_mode(mode)

        '''
        assert mode in ['normal', 'shutdown']

        self.ad5272.set_work_mode(mode)
        return 'done'

    def measure_thdn(self, decimation_type=0xFF, band=20000, harmonic_count=5, flag="off"):
        '''
        THDN function to measure thdn Vpp frequency thd

        Args:
            decimation_type:  int, 0xFF: IPCORE set the decimation automatic.
            band:             int, unit Hz, default:20000, the max frequency of signal.
            harmonic_count:   int, [1~10], default 5, harmonic count.
            flag:             string, ['on', 'off'], default 'off', upload ADC raw data.

        Returns:
            string, str, if success return "frequency: 1000.0000 Hz,
                         amp: 500.0000 mV, thd: -40.0000 dB, thdn: -45.0000 dB" else  return "error".

        Examples:
            solaris.measure_thdn(0xFF, 20000, 5, 'on')

        '''
        assert band in range(1, SolarisDef.LTC2378_THDN_MAX_BANDWIDTH + 1) or band == "auto"
        assert decimation_type in range(1, SolarisDef.LTC2378_MAX_DECIMATION + 1)

        self.gpio.set_pin(SolarisDef.LTC2378_IPCORE_GPIO, SolarisDef.LTC2378_THDN)

        self.dma.reset_channel(self.dma_channel["thdn"])
        self.dma.disable_channel(self.dma_channel["thdn"])
        if flag == 'on':
            self.dma.enable_channel(self.dma_channel["thdn"])
        ret = self.ltc2378.measure_thdn(band, SolarisDef.THDN_SAMPLE_RATE, decimation_type,
                                        flag, harmonic_count)

        ret_str = ''
        ret_str += "{}{:.4f}{},{}{:.4f}{},".format('frequency: ', ret["freq"],
                                                   ' Hz', 'vpp: ', ret["vpp"], ' mV')
        ret_str += "{}{:.4f}{},".format('thd: ', ret["thd"], ' dB')
        ret_str += "{}{:.4f}{}".format('thdn: ', ret["thdn"], ' dB')
        return ret_str

    def ad5761_set_control_register(self, reg_val):
        '''
        Set AD5761 control register and update waveform parameter of AD5761.

        Args:
            reg_val: int, (2 bytes)The control register value.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.ad5761_set_control_register(0x16C)

        '''
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_REG_CONTROL]
        self.ad5761.write_register(AD57X1RDef.CONTROL_REGISTER, reg_val)
        # if AD5761 output range change, must update waveform parameters.
        self._set_waveform_param([self.ad5761.min_output_volt, self.ad5761.max_output_volt])
        return 'done'

    def _set_waveform_param(self, dac_volt_range):
        '''
        Update the k and b of waveform in solaris.

        Args:
            dac_volt_range: list, The output range of DAC,unit:mV

        Examples:
            self._set_waveform_param([-2500,7500])

        '''
        # k and b values of pulse, dc_voltage and triangular wave
        self.k = (SolarisDef.AWG_VALUE_MAX - SolarisDef.AWG_VALUE_MIN) / (dac_volt_range[1] - dac_volt_range[0])
        self.b = SolarisDef.AWG_VALUE_MAX - self.k * dac_volt_range[1]

        # k and b values of sine wave reference vpp
        self.vpp_k = (SolarisDef.SINE_VALUE_MAX - SolarisDef.SINE_VALUE_MIN) / (dac_volt_range[1] - dac_volt_range[0])
        self.vpp_b = SolarisDef.SINE_VALUE_MAX - self.vpp_k * (dac_volt_range[1] - dac_volt_range[0])

        # k and b values of sine wave offset
        self.offset_k = (SolarisDef.SINE_OFFSET_MAX - SolarisDef.SINE_OFFSET_MIN) / \
                        (dac_volt_range[1] - dac_volt_range[0])
        self.offset_b = SolarisDef.SINE_OFFSET_MAX - self.offset_k * dac_volt_range[1]

    def triangle(self, channel, v1, v2, triangle, period,
                 output_time=SolarisDef.ALWAYS_OUTPUT):
        '''
        Output triangle wave

        Args:
            channel:        int, [0],        The channel to output voltage.
            v1:             float, unit mV,  start voltage of triangle,
            v2:             float, unit mV,  end voltage of triangle ,
            triangle:       float, unit ms,  Triangle width.
            period:         float, unit ms,  Triangle period, include triangle width and DC width.
            output_time:    int, unit us, default 0xFFFFFF.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.triangle(0, 1000, 0, 100000, 200000)

        '''
        assert channel == 0
        assert self.ad5761.min_output_volt <= v1 <= self.ad5761.max_output_volt
        assert self.ad5761.min_output_volt <= v2 <= self.ad5761.max_output_volt
        self.spi_dac.close()
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_WAVEFORM_CONTROL]
        assert triangle > 0
        assert triangle < period
        v1 = self.k * v1 + self.b
        v2 = self.k * v2 + self.b
        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        if v1 > v2:
            self.signal_source.set_awg_parameter(
                SolarisDef.AD5761_SAMPLE_RATE, [(v1, v2, triangle / 2),
                                                (v2, v2, period - triangle),
                                                (v2, v1, triangle / 2)])
        else:
            self.signal_source.set_awg_parameter(
                SolarisDef.AD5761_SAMPLE_RATE, [(v1, v2, triangle / 2),
                                                (v2, v1, triangle / 2),
                                                (v1, v1, period - triangle)])

        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()
        self.spi_dac.open()
        return 'done'

    def pulse(self, channel, v1, v2, edge_width, pulse_width, period,
              output_time=SolarisDef.ALWAYS_OUTPUT):
        '''
        Output pulse wave

        Args:
            channel:        int, [0], The channel to output voltage.
            v1:             float, unit mV,  Max voltage or min voltage ,
                                             if v1>v2, the wave starts at v1 to v2.
            v2:             float, unit mV,  Max voltage or min voltage ,
                                             if v2>v1, the wave starts at v2 to v1.
            edge_width:     float, unit ms, Edge width of pulse wave.
            pulse_width:    float, unit ms, Pulse width of pulse wave.
            period:         float, unit ms, Period of pulse wave.
            output_time:    int, unit us, default 0xFFFFFF, Output_time of pulse wave.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.pulse(0, 1000, 0, 100, 200, 2000)

        '''
        assert channel == 0
        assert self.ad5761.min_output_volt <= v1 <= self.ad5761.max_output_volt
        assert self.ad5761.min_output_volt <= v2 <= self.ad5761.max_output_volt

        self.spi_dac.close()
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_WAVEFORM_CONTROL]
        assert pulse_width > 0
        assert edge_width > 0
        assert pulse_width + edge_width * 2 < period
        v1 = self.k * v1 + self.b
        v2 = self.k * v2 + self.b

        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        if v1 > v2:
            self.signal_source.set_awg_parameter(
                SolarisDef.AD5761_SAMPLE_RATE, [(v1, v1, pulse_width),
                                                (v1, v2, edge_width),
                                                (v2, v2, period -
                                                 pulse_width - 2 * edge_width),
                                                (v2, v1, edge_width)])
        else:
            self.signal_source.set_awg_parameter(
                SolarisDef.AD5761_SAMPLE_RATE, [(v1, v1, period - pulse_width -
                                                 2 * edge_width),
                                                (v1, v2, edge_width),
                                                (v2, v2, pulse_width),
                                                (v2, v1, edge_width)])

        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()
        self.spi_dac.open()
        return 'done'

    def disable_waveform(self, channel):
        '''
        :param channel: int(0), The channel to disable waveform output

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.disable_waveform(0)

        '''
        assert channel == 0
        self.spi_dac.close()
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_WAVEFORM_CONTROL]
        self.signal_source.close()
        return 'done'

    def dc(self, channel, volt, output_time=SolarisDef.ALWAYS_OUTPUT):
        '''
        AD5761 Output DC voltage, SPI bus would always refresh the AD5761 data register.

        Args:
            channel:        int, [0], The channel to output voltage.
            volt:           float, unit mV, DC voltage.
            output_time:    int, unit us, default 0xFFFFFF, Output_time of dc voltage.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.dc(0, 2000)

        '''
        assert channel == 0
        assert self.ad5761.min_output_volt <= volt <= self.ad5761.max_output_volt

        start_volt = self.k * volt + self.b
        stop_volt = start_volt

        self.spi_dac.close()
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_WAVEFORM_CONTROL]
        self.signal_source.close()
        self.signal_source.set_signal_type('AWG')
        # 0.5 is duration time
        self.signal_source.set_awg_parameter(SolarisDef.AD5761_SAMPLE_RATE,
                                             [(start_volt, stop_volt,
                                               0.5)])
        self.signal_source.set_signal_time(output_time)
        self.signal_source.open()
        self.signal_source.output_signal()
        self.spi_dac.open()

        return 'done'

    def sine(self, channel, vpp, offset, frequency,
             output_time=SolarisDef.ALWAYS_OUTPUT):
        '''
        Output sine wave

        Args:
            channel:      int, [0], The channel to output voltage.
            vpp:          float, unit mV,  Vpp voltage to config sine wave.
            offset:       float, unit mV, Offset to config sine wave.
            frequency:    float, unit mV, Frequency to config sine wave.
            output_time:  int, unit us, default 0xFFFFFF.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.sine(0, 2000, 500, 1000)

        '''
        assert channel == 0
        assert 0 <= vpp <= self.ad5761.max_output_volt - self.ad5761.min_output_volt
        assert self.ad5761.min_output_volt <= offset <= self.ad5761.max_output_volt

        self.spi_dac.close()
        [self.gpio.set_pin(x[0], x[1]) for x in SolarisDef.AD5761_WAVEFORM_CONTROL]

        vpp = vpp * self.vpp_k + self.vpp_b
        offset = offset * self.offset_k + self.offset_b

        self.signal_source.close()
        self.signal_source.set_signal_time(output_time)
        self.signal_source.set_signal_type('sine')
        # set duty as 0.5, for sine,it's a fix value 0.5 .
        self.signal_source.set_swg_paramter(
            SolarisDef.AD5761_SAMPLE_RATE, frequency, vpp, 0.5, offset)
        self.signal_source.open()
        self.signal_source.output_signal()
        self.spi_dac.open()

        return 'done'

    def adc_data_2_voltage(self, raw_data, adc_resolution=20, vref=SolarisDef.LTC2378_VREF):
        if (raw_data >> (adc_resolution - 1)) & 0x1:
            raw_data -= 1 << adc_resolution
        voltage = raw_data * vref / (1 << (adc_resolution - 1))
        return voltage  # mV

    def get_adc_max_min(self):
        '''
        Get the adc max value and min value

        Examples:
            solaris.get_adc_max_min()
        '''
        # self.ipcore.meter.axi4_bus.write_8bit_inc(0x13, [0x01])
        rd_data = self.ipcore.meter.axi4_bus.read_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_MAX_ADDR, 4)
        vpp_max = self.adc_data_2_voltage((rd_data[1] >> 4) | (rd_data[2] << 4) | (rd_data[3] << 12), 20)
        rd_data = self.ipcore.meter.axi4_bus.read_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_MIN_ADDR, 4)
        vpp_min = self.adc_data_2_voltage((rd_data[1] >> 4) | (rd_data[2] << 4) | (rd_data[3] << 12), 20)
        return vpp_max, vpp_min

    def enable_upload(self, sample_rate=192000, upload_state="off", measure_time=0xFFFFFFFF):
        '''
        enable the solaris adc upload

        Args:
            sample_rate:    int, unit Hz, default 192000, set the sample rate for adcHz.
            upload_state:   string, ["on", "off"], default "off".
            measure_time:   int, default 0xFFFFFFFF.

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.enable_upload()
        '''

        assert upload_state in ("on", "off")
        self.gpio.set_pin(SolarisDef.LTC2378_IPCORE_GPIO, SolarisDef.LTC2378_RMS)
        self.dma.reset_channel(self.dma_channel["rms"])
        self.dma.disable_channel(self.dma_channel["rms"])
        if upload_state == 'on':
            self.dma.enable_channel(self.dma_channel["rms"])

        wr_data = DataOperate.int_2_list(measure_time & 0xFFFF, 2)
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_TIME_LOW_ADDR, wr_data)
        wr_data = DataOperate.int_2_list((measure_time >> 16) & 0xFFFF, 2)
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_TIME_HIGH_ADDR, wr_data)
        self.ipcore.spi_adc.open()
        self.ipcore.spi_adc.set_sample_rate(sample_rate)
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MODULE_ENABLE_ADDR, [0xFE])
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MODULE_ENABLE_ADDR, [0xFF])
        # enable the [0]: 1—Generate a Signal measure start signal, active-1, automatic reset.
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_CTRL_ADDR, [0x01])
        return 'done'

    def disable_upload(self):
        '''
        disable the solaris adc data upload

        Returns:
            string, "done", api execution successful.

        Examples:
            solaris.disable_upload()

        '''

        # disable signal meter and clear the output time
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MODULE_ENABLE_ADDR, [0x01])
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_TIME_HIGH_ADDR, [0x00, 0x00])
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_TIME_LOW_ADDR, [0x00, 0x00])
        # [1]: active-1, automatic reset.
        self.ipcore.meter.axi4_bus.write_8bit_inc(SolarisDef.PL_SIGNAL_METER_MEASURE_CTRL_ADDR, [0x02])

        self.dma.reset_channel(self.dma_channel["rms"])
        self.dma.disable_channel(self.dma_channel["rms"])

        return 'done'
