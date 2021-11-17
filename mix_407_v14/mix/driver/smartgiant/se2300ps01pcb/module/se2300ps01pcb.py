# -*- coding: utf-8 -*-
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ipcore.mix_powersequence_sg import MIXPowerSequenceSG
from mix.driver.smartgiant.common.ic.ad56x9r import AD5629R
from mix.driver.smartgiant.common.ic.ad56x9r_emulator import AD5629REmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard

__author__ = 'ZiCheng.Huang@SmartGiant'
__version__ = '0.1'


class SE2300AD02PCADef:
    DAC_MAX_OUTPUT_VOL = 4990  # DAC default voltage, unit is mV
    DAC_MODE = "internal"
    PIN_OUTPUT_DIRECTION = "output"
    HIGH_LEVEL = 1
    LOW_LEVEL = 0
    ALL_CHANNEL = 0xFF
    ADS5231_OEA = 1
    POWER_SEQUNCE_IP_CTRL = 4
    DAC0_ADDR = 0x54
    DAC1_ADDR = 0x56
    DAC2_ADDR = 0x57
    DAC3_ADDR = 0x54
    DAC4_ADDR = 0x56
    CAT9555_ADDR = 0x20
    EEPROM_DEV_ADDR = 0x51
    SENSOR_DEV_ADDR = 0x49
    CHIP_SAMPLE_RATE = 40000000
    SWITCH_BASE_TIME = 1000000000
    SWITCH_TIME_GAIN = -75
    TRIGGER_SAMPLE_RATE = 125000000


class SE2300Exception(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class SE2300PS01PCB(MIXBoard):

    '''
    PS_MUX board is use for Power sequence test, Channel switch, Voltage compare.

    Note that if use ipcore ads5231_ctrl, upload_ctrl, i2c_bus_0, i2c_bus_1, power_sequence_ipcore,
    trigger_ipcore can not be None, i2c_bus_0, i2c_bus_1 can create the AD5629R instance.

    Args:
        ads5231_ctrl:          instance(GPIO)/None,  Class instance of Pin, which is used to
                                                     control ADS5231 disable/enable state
        upload_ctrl:           instance(GPIO)/None,  Class instance of Pin, which is used to
                                                     control power sequence IPcore upload disable/enable
        i2c_bus_0:             instance(I2C)/None,   I2C bus to three DAC (AD5629)
        i2c_bus_1:             instance(I2C)/None,   I2C bus to two DAC (AD5629)
        power_sequence_ipcore: instance(MIXSampleMultiplex)/string/None, Class instance of power_sequence_ipcore,
                                                     if not using this parameter, will create emulator.
        trigger_ipcore:        instance(MIXSampleMultiplex)/string/None, Class instance of trigger_ipcore,
                                                     if not using this parameter, will create emulator.

    Examples:
        # use IP
        gpio = PLGPIO(/dev/MIX_GPIO_0)
        ads5231_ctrl = Pin(gpio, 1)
        upload_ctrl = Pin(gpio, 4)
        i2c = I2C('/dev/i2c-1')
        # simulating case when i2c buses are from i2c-mux's 2 ports
        mux = TCA9548(0x75, i2c)
        i2c_ds_bus_0 = I2CDownstreamBus(mux, 0)
        i2c_ds_bus_1 = I2CDownstreamBus(mux, 1)
        power_sequence_device = MIXSampleMultiplex('/dev/MIX_Sample_Multiplex_1')
        trigger_device = MIXSampleMultiplex('/dev/MIX_Sample_Multiplex_2')
        power_sequence = SE2300PS01PCB(ads5231_ctrl, upload_ctrl, i2c_bus_0, i2c_bus_1,
                                       power_sequence_device, trigger_device)

    '''

    rpc_public_api = ['start_monitor', 'stop_monitor', 'set_trigger_ref_voltage', 'trigger_time_monitor_start',
                      'read_trigger_time', 'board_init'] + MIXBoard.rpc_public_api

    def __init__(self, ads5231_ctrl=None, upload_ctrl=None, i2c_bus_0=None, i2c_bus_1=None,
                 power_sequence_ipcore=None, trigger_ipcore=None):

        self.ads5231_ctrl = ads5231_ctrl or Pin(None, SE2300AD02PCADef.ADS5231_OEA)
        self.upload_ctrl = upload_ctrl or Pin(None, SE2300AD02PCADef.POWER_SEQUNCE_IP_CTRL)
        self.i2c_bus_0 = i2c_bus_0
        self.i2c_bus_1 = i2c_bus_1

        if isinstance(power_sequence_ipcore, basestring):
            self.power_sequence_ipcore = MIXPowerSequenceSG(power_sequence_ipcore)
        elif power_sequence_ipcore:
            self.power_sequence_ipcore = power_sequence_ipcore
        else:
            self.power_sequence_ipcore = MIXPowerSequenceSG()

        if isinstance(trigger_ipcore, basestring):
            self.trigger_ipcore = MIXPowerSequenceSG(trigger_ipcore)
        elif trigger_ipcore:
            self.trigger_ipcore = trigger_ipcore
        else:
            self.trigger_ipcore = MIXPowerSequenceSG()

    def start_monitor(self, sample_rate, attach_byte, channel_list):
        '''
        POWER_SEQUENCE start monitor to upload data

        Args:
            sample_rate:     int, [1000~400000], unit Hz, Set ADC measure sample rate.
            attach_byte:     int, [0x00-0xFF], upload raw data will attach this byte.
            channel_list:    list, ([x,x,...x]) x=(0-39), Need monitor channel list.

        Returns:
            string, "done", api execution successful.

        Examples:
            power_sequence.start_monitor(1000, 0x1, [0,1,2,3,4,5,6,7])

        '''
        assert isinstance(sample_rate, int)
        assert sample_rate in range(1000, 400001)  # range is 1000~400000Hz
        assert isinstance(attach_byte, int)
        assert attach_byte in range(0x00, 0x100)  # range is 0x00~0xFF
        assert isinstance(channel_list, list)
        assert len(channel_list) != 0

        self.ads5231_ctrl.set_level(SE2300AD02PCADef.LOW_LEVEL)
        self.upload_ctrl.set_level(SE2300AD02PCADef.HIGH_LEVEL)
        self.power_sequence_ipcore.close()
        self.power_sequence_ipcore.set_sample_channel(channel_list)
        attach_byte_list = [attach_byte] * len(channel_list)
        # Set extra information for each sample channel
        self.power_sequence_ipcore.set_channel_attached(attach_byte_list)
        switch_time = SE2300AD02PCADef.SWITCH_BASE_TIME / (sample_rate * (len(channel_list)))\
            + SE2300AD02PCADef.SWITCH_TIME_GAIN
        self.power_sequence_ipcore.set_sample_parameter(
            SE2300AD02PCADef.CHIP_SAMPLE_RATE, switch_time, 1)
        self.power_sequence_ipcore.open()
        self.power_sequence_ipcore.measure()

        return "done"

    def stop_monitor(self):
        '''
        POWER_SEQUENCE stop monitor to stop upload data

        Returns:
            string, "done", api execution successful.

        Examples:
            power_sequence.stop_monitor()

        '''
        self.ads5231_ctrl.set_level(SE2300AD02PCADef.HIGH_LEVEL)
        self.upload_ctrl.set_level(SE2300AD02PCADef.LOW_LEVEL)
        self.power_sequence_ipcore.close()

        return "done"

    def set_trigger_ref_voltage(self, channel, voltage, dac_num):
        '''
        POWER_SEQUENCE set trigger ref voltage

        channel 1-24 is control the dac0-2,channel 25~40 is control the dac3-4,
        'ALL' or 'all' control the dac0-2 or dac3-4.

        Args:
            channel:     int/string, [1~40] | ["ALL"], Select specify channel.
            voltage:     float, [0~5000], unit mV, Set specify channel output voltage.
            dac_num:     string, ['dac0-2', 'dac3-4'], Set the DAC channel voltage between the i2c.

        Returns:
            string, "done", api execution successful.

        Examples:
            power_sequence.set_trigger_ref_voltage(3, 2000, 'dac0-2')

        '''
        assert (isinstance(channel, int) and channel >= 1 and channel <= 40)\
            or (isinstance(channel, basestring) and channel.upper() == "ALL")
        assert isinstance(voltage, (float, int))
        assert voltage in range(0, 5001)  # range is 0~5000 mv
        assert dac_num in ['dac0-2', 'dac3-4']

        if str(channel).upper() == "ALL":
            if dac_num == 'dac0-2':
                self.ref_dac_0.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, voltage)
                self.ref_dac_1.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, voltage)
                self.ref_dac_2.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, voltage)
            else:
                self.ref_dac_3.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, voltage)
                self.ref_dac_4.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, voltage)
        else:
            channel_num = channel - 1
            channel_adc = channel_num & 0x07
            dac_object = None
            if (channel_num >> 3) == 0:
                dac_object = self.ref_dac_0
            elif (channel_num >> 3) == 1:
                dac_object = self.ref_dac_1
            elif (channel_num >> 3) == 2:
                dac_object = self.ref_dac_2
            elif (channel_num >> 3) == 3:
                dac_object = self.ref_dac_3
            elif (channel_num >> 3) == 4:
                dac_object = self.ref_dac_4

            if dac_object is None:
                raise SE2300Exception("Can find the DAC channel")
            dac_object.output_volt_dc(channel_adc, voltage)

        return "done"

    def trigger_time_monitor_start(self, measure_time):
        '''
        POWER_SEQUENCE start monitor trigger time

        Args:
            measure_time:    int, [1~30000], unit ms, Need monitor trigger time

        Returns:
            string, "done", api execution successful.

        Examples:
            power_sequence.trigger_time_monitor_start(20000)

        '''
        assert isinstance(measure_time, int)
        assert measure_time in range(1, 30001)  # range is 1~30000mS, measure time

        self.trigger_ipcore.close()
        self.trigger_ipcore.open()
        self.trigger_ipcore.measure_time(measure_time)
        self.trigger_ipcore.measure()

        return "done"

    def read_trigger_time(self, channel_list, mode):
        '''
        POWER_SEQUENCE get each channel trigger time

        Args:
            channel_list:    list, ([x,x,...x]) x=(1-40).
            mode:            string, ['rise', 'fall'].

        Returns:
            string, str, ("chX=Yns,....") X: 1-40; Y: trigger time value, unit is ns.

        Examples:
            result = power_sequence.read_trigger_time([1,2,3,4,40],'rise')

        '''
        mode_list = ["rise", "fall"]

        assert isinstance(channel_list, list)
        assert mode in mode_list

        result = ""
        for ch in channel_list:
            (pos_time, neg_time) = self.trigger_ipcore.get_interrupt_time(
                SE2300AD02PCADef.TRIGGER_SAMPLE_RATE, ch)
            result += "ch%d=" % ch
            if mode == "rise":
                result += str(pos_time)  # rise time
            else:
                result += str(neg_time)
            result += "ns,"

        self.trigger_ipcore.close()

        return result

    def board_init(self, dac_num):
        '''
        POWER_SEQUENCE initialize the board

        need to DAC 1~3 or 4~5 output 4990mV voltage to Comparators,set the pin output.

        Args:
            dac_num:       string, ['dac0-2', 'dac3-4'], choose initialize the dac chip.

        Returns:
            string, "done", api execution successful.

        Examples:
            result = power_sequence.board_init('dac0-2')

        '''
        assert dac_num in ['dac0-2', 'dac3-4']

        self.ads5231_ctrl.set_dir(SE2300AD02PCADef.PIN_OUTPUT_DIRECTION)
        self.upload_ctrl.set_dir(SE2300AD02PCADef.PIN_OUTPUT_DIRECTION)

        if dac_num == 'dac0-2':
            if self.i2c_bus_0:
                self.ref_dac_0 = AD5629R(SE2300AD02PCADef.DAC0_ADDR, self.i2c_bus_0, SE2300AD02PCADef.DAC_MODE)
                self.ref_dac_1 = AD5629R(SE2300AD02PCADef.DAC1_ADDR, self.i2c_bus_0, SE2300AD02PCADef.DAC_MODE)
                self.ref_dac_2 = AD5629R(SE2300AD02PCADef.DAC2_ADDR, self.i2c_bus_0, SE2300AD02PCADef.DAC_MODE)
            else:
                self.ref_dac_0 = AD5629REmulator("ad5629r_elulator_0")
                self.ref_dac_1 = AD5629REmulator("ad5629r_elulator_1")
                self.ref_dac_2 = AD5629REmulator("ad5629r_elulator_2")

            self.ref_dac_0.initialization()
            self.ref_dac_0.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, SE2300AD02PCADef.DAC_MAX_OUTPUT_VOL)

            self.ref_dac_1.initialization()
            self.ref_dac_1.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, SE2300AD02PCADef.DAC_MAX_OUTPUT_VOL)

            self.ref_dac_2.initialization()
            self.ref_dac_2.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, SE2300AD02PCADef.DAC_MAX_OUTPUT_VOL)
        else:
            if self.i2c_bus_1:
                self.ref_dac_3 = AD5629R(SE2300AD02PCADef.DAC3_ADDR, self.i2c_bus_1, SE2300AD02PCADef.DAC_MODE)
                self.ref_dac_4 = AD5629R(SE2300AD02PCADef.DAC4_ADDR, self.i2c_bus_1, SE2300AD02PCADef.DAC_MODE)
            else:
                self.ref_dac_3 = AD5629REmulator("ad5629r_elulator_3")
                self.ref_dac_4 = AD5629REmulator("ad5629r_elulator_4")

            self.ref_dac_3.initialization()
            self.ref_dac_3.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, SE2300AD02PCADef.DAC_MAX_OUTPUT_VOL)

            self.ref_dac_4.initialization()
            self.ref_dac_4.output_volt_dc(SE2300AD02PCADef.ALL_CHANNEL, SE2300AD02PCADef.DAC_MAX_OUTPUT_VOL)

        return "done"
