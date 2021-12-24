# -*- coding: utf-8 -*-

import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate
from mix.driver.core.bus.axi4_lite_def import AXI4Def

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXAd760xSGDef:
    # 0x10 [0]: Enable [4]:continues mode
    ENABLE_BIT = 0
    CONTINUOUS_MODE_BIT = 4
    ENABLE_REG = 0x10
    # 0x11 [2:0]: OS pin control [4]: range pin control [7]: reset pin control
    PIN_RESET_BIT = 7
    PIN_CTRL_REG = 0x11
    # 0x12
    SAMPLE_START_REG = 0x12
    # 0x13
    BUSY_STAT_REG = 0x13
    # 0x14
    SAMPLE_RATE_REG = 0x14
    # ch(x) = 0x20 + 4 * x
    CHANNEL_VOLTAGE_BASE_REG = 0x20
    VOLTAGE_REG_OFFSET = 4
    VOLT_2_MILLIVOLT = 1000
    # RANGE '5V' / '10'
    RANGE_CONFIG = {'5V': 0, '10V': (1 << 3)}
    # Delay define
    DEFAULT_TIMEOUT = 1
    DELAY_1MS = 0.001

    FULL_SCALE = pow(2, 32)
    CONVERT_RATIO_10V = 20
    CONVERT_RATIO_5V = 10

    # AD7608 channels
    AD7608_CHANNEL_NUM = 8
    # AD7607 channels
    AD7607_CHANNEL_NUM = 8
    # AD7606 channels
    AD7606_CHANNEL_NUM = 8
    # AD7606-6 channels
    AD7606_6_CHANNEL_NUM = 6
    # AD7606-4 channels
    AD7606_4_CHANNEL_NUM = 4
    # AD7605 channels
    AD7605_CHANNEL_NUM = 4
    REG_SIZE = 8192


class MIXAd760xSGException(Exception):

    '''
    MIXAd760xSGException shows the exception of AD760X
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXAd760xSG(object):
    '''
    MIXAd760xSG ADC Driver:
        The AD7605, AD7606, AD7607, and AD7608 are 16-bit, 8-/6-/4-channel,
        simultaneous sampling successive approximation ADCs.
        The devices operate from a single 2.7 V to 5.25 V power supply and feature
        throughput rates of up to 200 kSPS.
        The devices have on-board 1 MΩ input buffers for direct connection from the
        user sensor outputs to the ADC.
        The AD7608 contains an optional digital first-order sinc filter that should
        be used in applications where slower throughput rates are used or where higher
        signal-to-noise ratio or dynamic range is desirable.

    ClassType = ADC

    Args:
        axi4_bus: instance(AXI4LiteBus)/string; instance of AXI4 bus or device path
                                                If None, will create Emulator.
        channel_num: int, [4, 6, 8],            channel number supported.

    Examples:
        ad760x = MIXAd760xSG('/dev/AXI4_AD7608_0', MIXAd760xSGDef.AD7608_CHANNEL_NUM)

        # sampling once, unit is 'mV'
        sample_data_list = ad760x.single_sampling(0, '5V')
        print(sample_data_list)
        Terminal shows "[xx, xx, xx, xx, xx, xx, xx, xx]"

        # enable continuous sampling
        ad760x.enable_continuous_sampling(0, '10V', 2000)

        # disable continuous sampling
        ad760x.disable_continuous_sampling()

    '''

    rpc_public_api = ['reset', 'single_sampling', 'enable_continuous_sampling', 'disable_continuous_sampling']

    def __init__(self, axi4_bus=None, channel_num=None):
        if axi4_bus:
            if isinstance(axi4_bus, basestring):
                # device path; create axi4lite bus here
                self.axi4_bus = AXI4LiteBus(axi4_bus, 8192)
            else:
                self.axi4_bus = axi4_bus
            if channel_num not in [4, 6, 8]:
                raise MIXAd760xSGException('MIXAd760xSG channel number invalid')
            self.channel_num = channel_num
        else:
            self.axi4_bus = AXI4LiteBusEmulator("mix_ad760x_sg_emulator", 8192)
            self.channel_num = MIXAd760xSGDef.AD7608_CHANNEL_NUM

        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
        AD760X enable, set ENABLE register ENABLE_BIT

        Examples:
            ad760x._enable()

        '''
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.ENABLE_REG, [0x01])

    def _disable(self):
        '''
        AD760X disable, clear ENABLE register

        Examples:
            ad760x._disable()

        '''
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.ENABLE_REG, [0x00])

    def reset(self):
        '''
        AD760X reset chip,
        The RESET high pulse should be minimum 50 ns wide.

        Examples:
            ad760x.reset()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXAd760xSGDef.PIN_CTRL_REG, 1)
        rd_data[0] |= (0x1 << MIXAd760xSGDef.PIN_RESET_BIT)
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.PIN_CTRL_REG, rd_data)
        time.sleep(MIXAd760xSGDef.DELAY_1MS)
        rd_data[0] &= ~(0x1 << MIXAd760xSGDef.PIN_RESET_BIT)
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.PIN_CTRL_REG, rd_data)

    def single_sampling(self, over_sampling, adc_range):
        '''
        AD760X measure single voltage, there is an improvement in SNR as
        over_sampling increases. Refer to AD7608 Datasheet Table 8(Page26).
        Conversion Control:
            Simultaneous Sampling on All Analog Input Channels

        +-------------------+-------------------+------+
        | over_sampling     |sampling_rate limit| unit |
        +===================+===================+======+
        |  0 (No OS)        |  2000~200000      | 'Hz' |
        +-------------------+-------------------+------+
        |  1                |  2000~100000      | 'Hz' |
        +-------------------+-------------------+------+
        |  2                |  2000~50000       | 'Hz' |
        +-------------------+-------------------+------+
        |  3                |  2000~25000       | 'Hz' |
        +-------------------+-------------------+------+
        |  4                |  2000~12500       | 'Hz' |
        +-------------------+-------------------+------+
        |  5                |  2000~6250        | 'Hz' |
        +-------------------+-------------------+------+
        |  6                |  2000~3125        | 'Hz' |
        +-------------------+-------------------+------+
        |  7 (Invalid)      |  /                |  /   |
        +-------------------+-------------------+------+

        Args:
            over_sampling:  int, [0~7], OS[2:0] oversample bit value.
            adc_range:      string, ['10V', '5V'], adc reference voltage range.

        Examples:
            ad760x.single_sampling(0, '10V')

        '''
        assert 0 <= over_sampling < 8
        assert adc_range in ['10V', '5V']

        # Enable and Clear Continuous mode, Set OS bit, select range
        rd_data = self.axi4_bus.read_8bit_inc(MIXAd760xSGDef.ENABLE_REG, 2)
        rd_data[0] = (0x1 << MIXAd760xSGDef.ENABLE_BIT)
        rd_data[0] &= ~(0x1 << MIXAd760xSGDef.CONTINUOUS_MODE_BIT)
        rd_data[1] = (rd_data[1] & 0xF0) | (
            MIXAd760xSGDef.RANGE_CONFIG[adc_range] | over_sampling)
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.ENABLE_REG, rd_data)

        # start sample
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.SAMPLE_START_REG, [0x01])
        reg_data = 0
        last_time = time.time()
        while(reg_data & 0x01 == 0x00) and \
                (time.time() - last_time < MIXAd760xSGDef.DEFAULT_TIMEOUT):
            time.sleep(MIXAd760xSGDef.DELAY_1MS)
            reg_data = self.axi4_bus.read_8bit_inc(MIXAd760xSGDef.BUSY_STAT_REG, 1)[0]
        if time.time() - last_time >= MIXAd760xSGDef.DEFAULT_TIMEOUT:
            raise MIXAd760xSGException('AD706X read register wait timeout')

        # read channel voltage
        voltages = []
        volt_reg_addr = MIXAd760xSGDef.CHANNEL_VOLTAGE_BASE_REG
        for i in range(self.channel_num):
            rd_data = self.axi4_bus.read_8bit_inc(volt_reg_addr, 4)
            volt_temp = DataOperate.list_2_int(rd_data)
            if(adc_range == '10V'):
                volt_temp = float(volt_temp) / MIXAd760xSGDef.FULL_SCALE * MIXAd760xSGDef.CONVERT_RATIO_10V
            else:
                volt_temp = float(volt_temp) / MIXAd760xSGDef.FULL_SCALE * MIXAd760xSGDef.CONVERT_RATIO_5V
            volt_reg_addr += MIXAd760xSGDef.VOLTAGE_REG_OFFSET
            # Convert result unit 'V' to 'mV'
            volt_temp *= MIXAd760xSGDef.VOLT_2_MILLIVOLT
            voltages.append(volt_temp)

        return voltages

    def enable_continuous_sampling(self, over_sampling, adc_range, sampling_rate):
        '''
        AD760X enable continuous measure, there is an improvement in SNR as
        over_sampling increases. Refer to AD7608 Datasheet Table 8(Page26).

        Args:
            over_sampling:  int, [0~7], OS[2:0] oversample bit value.
            adc_range:      string, ['10V', '5V'], reference voltage range.
            sampling_rate:  int, [2000~200000], sampling_rate.

        Examples:
            ad760x.enable_continuous_sampling(0, '10V', 2000)

        '''
        assert 0 <= over_sampling < 8
        assert adc_range in ['10V', '5V']
        assert isinstance(sampling_rate, int) and 2000 <= sampling_rate <= 200000

        # Set continuos mode, set OS bit, select range
        rd_data = self.axi4_bus.read_8bit_inc(MIXAd760xSGDef.ENABLE_REG, 2)
        rd_data[0] = (0x1 << MIXAd760xSGDef.ENABLE_BIT)
        rd_data[0] |= (0x1 << MIXAd760xSGDef.CONTINUOUS_MODE_BIT)
        rd_data[1] = (rd_data[1] & 0xF0) | (
            MIXAd760xSGDef.RANGE_CONFIG[adc_range] | over_sampling)
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.ENABLE_REG, rd_data)

        # configure sample rate
        wr_data = DataOperate.int_2_list(int((AXI4Def.AXI4_CLOCK / sampling_rate) - 2), 2)
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.SAMPLE_RATE_REG, wr_data)

        # start sample
        self.axi4_bus.write_8bit_inc(MIXAd760xSGDef.SAMPLE_START_REG, [0x01])

    def disable_continuous_sampling(self):
        '''
        AD760X disable continuous measure

        Examples:
            ad760x.disable_continuous_sampling()

        '''
        self._disable()


class MIXAd7608SG(MIXAd760xSG):
    '''
    AD7608 ADC Driver:
        The AD7608 is an 18-bit, 8 channel, simultaneous sampling Analog-to-Digital Data Acquisition
        system (DAS). The part contains analog input clamp protection, 2nd order anti-alias filter,
        track and hold amplifier, 18-bit charge redistribution successive approximation ADC,
        flexible digital filter, 2.5V reference and reference buffer and high speed serial and
        parallel interfaces.

    ClassType = ADC

    Args:
        axi4_bus: instance(AXI4LiteBus)/string; instance of AXI4 bus or device path
                                                If None, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_AD7608_0', 8192)
        ad7608 = AD7608(axi)

        # sampling once, unit is 'mV'
        sample_data_list = ad760x.single_sampling(0, '5V')
        print(sample_data_list)
        Terminal shows "[xx, xx, xx, xx, xx, xx, xx, xx]"

        # enable continuous sampling
        ad760x.enable_continuous_sampling(0, '10V', 2000)

        # disable continuous sampling
        ad760x.disable_continuous_sampling()

    '''

    def __init__(self, axi4_bus=None):
        super(MIXAd7608SG, self).__init__(axi4_bus, MIXAd760xSGDef.AD7608_CHANNEL_NUM)
