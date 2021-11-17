# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_daqt2_sg_r import MIXDAQT2SGR
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator


__author__ = 'Chujie.Lan@SmartGiant'
__version__ = '1.2'


beast_calibration_info = {
    "VPP_2V": {
        'level1': {'unit_index': 0, 'unit': 'mV'},
        'level2': {'unit_index': 1, 'unit': 'mV'},
        'level3': {'unit_index': 2, 'unit': 'mV'},
        'level4': {'unit_index': 3, 'unit': 'mV'},
        'level5': {'unit_index': 4, 'unit': 'mV'},
        'level6': {'unit_index': 5, 'unit': 'mV'},
        'level7': {'unit_index': 6, 'unit': 'mV'},
        'level8': {'unit_index': 7, 'unit': 'mV'},
        'level9': {'unit_index': 8, 'unit': 'mV'},
        'level10': {'unit_index': 9, 'unit': 'mV'}
    },
    "LOW_FREQ_VPP_20V": {
        'level1': {'unit_index': 10, 'unit': 'mV'},
        'level2': {'unit_index': 11, 'unit': 'mV'},
        'level3': {'unit_index': 12, 'unit': 'mV'},
        'level4': {'unit_index': 13, 'unit': 'mV'},
        'level5': {'unit_index': 14, 'unit': 'mV'},
        'level6': {'unit_index': 15, 'unit': 'mV'},
        'level7': {'unit_index': 16, 'unit': 'mV'},
        'level8': {'unit_index': 17, 'unit': 'mV'},
        'level9': {'unit_index': 18, 'unit': 'mV'},
        'level10': {'unit_index': 19, 'unit': 'mV'}

    },
    "HIGH_FREQ_VPP_20V": {
        'level1': {'unit_index': 40, 'unit': 'mV'},
        'level2': {'unit_index': 41, 'unit': 'mV'},
        'level3': {'unit_index': 42, 'unit': 'mV'},
        'level4': {'unit_index': 43, 'unit': 'mV'},
        'level5': {'unit_index': 44, 'unit': 'mV'},
        'level6': {'unit_index': 45, 'unit': 'mV'},
        'level7': {'unit_index': 46, 'unit': 'mV'},
        'level8': {'unit_index': 47, 'unit': 'mV'},
        'level9': {'unit_index': 48, 'unit': 'mV'},
        'level10': {'unit_index': 49, 'unit': 'mV'}
    },
    "RMS_2V": {
        'level1': {'unit_index': 20, 'unit': 'mV'},
        'level2': {'unit_index': 21, 'unit': 'mV'},
        'level3': {'unit_index': 22, 'unit': 'mV'},
        'level4': {'unit_index': 23, 'unit': 'mV'},
        'level5': {'unit_index': 24, 'unit': 'mV'},
        'level6': {'unit_index': 25, 'unit': 'mV'},
        'level7': {'unit_index': 26, 'unit': 'mV'},
        'level8': {'unit_index': 27, 'unit': 'mV'},
        'level9': {'unit_index': 28, 'unit': 'mV'},
        'level10': {'unit_index': 29, 'unit': 'mV'}
    },
    "LOW_FREQ_RMS_20V": {
        'level1': {'unit_index': 30, 'unit': 'mV'},
        'level2': {'unit_index': 31, 'unit': 'mV'},
        'level3': {'unit_index': 32, 'unit': 'mV'},
        'level4': {'unit_index': 33, 'unit': 'mV'},
        'level5': {'unit_index': 34, 'unit': 'mV'},
        'level6': {'unit_index': 35, 'unit': 'mV'},
        'level7': {'unit_index': 36, 'unit': 'mV'},
        'level8': {'unit_index': 37, 'unit': 'mV'},
        'level9': {'unit_index': 38, 'unit': 'mV'},
        'level10': {'unit_index': 39, 'unit': 'mV'}
    },
    "HIGH_FREQ_RMS_20V": {
        'level1': {'unit_index': 50, 'unit': 'mV'},
        'level2': {'unit_index': 51, 'unit': 'mV'},
        'level3': {'unit_index': 52, 'unit': 'mV'},
        'level4': {'unit_index': 53, 'unit': 'mV'},
        'level5': {'unit_index': 54, 'unit': 'mV'},
        'level6': {'unit_index': 55, 'unit': 'mV'},
        'level7': {'unit_index': 56, 'unit': 'mV'},
        'level8': {'unit_index': 57, 'unit': 'mV'},
        'level9': {'unit_index': 58, 'unit': 'mV'},
        'level10': {'unit_index': 59, 'unit': 'mV'}
    }
}

beast_range_table = {
    "VPP_2V": 0,
    "LOW_FREQ_VPP_20V": 1,
    "HIGH_FREQ_VPP_20V": 2,
    "RMS_2V": 3,
    "LOW_FREQ_RMS_20V": 4,
    "HIGH_FREQ_RMS_20V": 5
}


class BeastDef:
    EEPROM_DEV_ADDR = 0x51
    SENSOR_DEV_ADDR = 0x49
    SIGNAL_METER_REG_SIZE = 256
    MIX_DAQT2_REG_SIZE = 65536
    IO_LOW_LEVEL = 0
    IO_HIGH_LEVEL = 1
    PIN_OUTPUT_DIRECTION = "output"
    BEAST_VPP_DURATION = 10
    BEAST_SAMPLE_RATE = 40000000
    BEAST_HIGH_FREQ_THRESHOLD = 100000
    GAIN1 = 1
    GAIN10 = 10
    DURATION = 100
    RANGE_VALUE_LIST = [2, 20]
    UPFRAME_MODE = "BYPASS"

    # adc measure volt range value unit is mV
    ADC_VOLT_RANGE = [-1010, 1010]
    SIGNAL_METER_SCALE_RANGE = [-0.99999, 0.99999]
    VPP_RANGE = [0, ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]]
    SIGNAL_METER_VPP_SCALE_RANGE = [0, 1.99999]
    RMS_RANGE = [0, 1010]
    SIGNAL_METER_RMS_SCALE_RANGE = [0, 0.99999]

    SCALE_GAIN = (ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]) / (SIGNAL_METER_SCALE_RANGE[1] - SIGNAL_METER_SCALE_RANGE[0])
    SCALE_OFFSET = ADC_VOLT_RANGE[1] - SCALE_GAIN * SIGNAL_METER_SCALE_RANGE[1]

    VPP_SCALE_GAIN = (VPP_RANGE[1] - VPP_RANGE[0]) / (SIGNAL_METER_VPP_SCALE_RANGE[1] - SIGNAL_METER_VPP_SCALE_RANGE[0])
    VPP_SCALE_OFFSET = VPP_RANGE[1] - VPP_SCALE_GAIN * SIGNAL_METER_VPP_SCALE_RANGE[1]

    RMS_SCALE_GAIN = (RMS_RANGE[1] - RMS_RANGE[0]) / (SIGNAL_METER_RMS_SCALE_RANGE[1] - SIGNAL_METER_RMS_SCALE_RANGE[0])
    RMS_SCALE_OFFSET = RMS_RANGE[1] - RMS_SCALE_GAIN * SIGNAL_METER_RMS_SCALE_RANGE[1]

    # These bit are provided by the fpga
    BEAST_RANGE_CTRL_PIN = 1
    BEAST_DCAC_CTRL_PIN = 2
    BEAST_OUTPUT_CTRL_PIN = 0


class BeastBase(MIXBoard):
    '''
    Base class of Beast and BeastCompatible.
    Providing common Beast methods.

    Args:
        i2c:              instance(I2C),              used to control eeprom and nct75 sensor.
        range_ctrl:       instance(GPIO),             used to control Beast range.
        dcac_ctrl:        instance(GPIO),             used to control DC/AC mode.
        output_ctrl:      instance(GPIO),             used to control AD5231 disable/enable state.
        pl_signal_meter:  instance(PLSignalMeter),    used to access PLSignalMeter ipcore.
        ipcore:        instance(MIXDAQT2SGR),         used to access PLGPIO, PLSignalMeter ipcore.
        eeprom_dev_addr:  int,                        eeprom device address.
        sensor_dev_addr:  int,                        NCT75 device address.

    '''

    rpc_public_api = ['module_init', 'select_range', 'enable_continuous_measure',
                      'disable_continuous_measure', 'set_measure_mask', 'frequency_measure',
                      'vpp_measure', 'rms_measure', 'level', 'adc_enable', 'adc_disable'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, range_ctrl=None, dcac_ctrl=None, output_ctrl=None, pl_signal_meter=None, ipcore=None,
                 eeprom_dev_addr=BeastDef.EEPROM_DEV_ADDR, sensor_dev_addr=BeastDef.SENSOR_DEV_ADDR):

        if i2c is None:
            super(BeastBase, self).__init__(None, None, cal_table=beast_calibration_info,
                                            range_table=beast_range_table)
        else:
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.nct75 = NCT75(sensor_dev_addr, i2c)
            super(BeastBase, self).__init__(self.eeprom, self.nct75,
                                            cal_table=beast_calibration_info, range_table=beast_range_table)

        if i2c and range_ctrl and dcac_ctrl and output_ctrl and pl_signal_meter and not ipcore:
            self.range_ctrl = range_ctrl
            self.dcac_ctrl = dcac_ctrl
            self.output_ctrl = output_ctrl
            if isinstance(pl_signal_meter, basestring):
                axi4_bus = AXI4LiteBus(pl_signal_meter, BeastDef.SIGNAL_METER_REG_SIZE)
                self.pl_signal_meter_device = MIXSignalMeterSG(axi4_bus)
            else:
                self.pl_signal_meter_device = pl_signal_meter
        elif i2c and not range_ctrl and not dcac_ctrl and not output_ctrl and not pl_signal_meter and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, BeastDef.MIX_DAQT2_REG_SIZE)
                self.mix_daqt2 = MIXDAQT2SGR(axi4_bus, use_signal_meter1=False, use_spi=False, use_gpio=True)
            else:
                self.mix_daqt2 = ipcore
            self.pl_signal_meter_device = self.mix_daqt2.signal_meter0
            self.range_ctrl = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_RANGE_CTRL_PIN)
            self.dcac_ctrl = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_DCAC_CTRL_PIN)
            self.output_ctrl = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_OUTPUT_CTRL_PIN)
        elif i2c and range_ctrl and dcac_ctrl and output_ctrl and not pl_signal_meter and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, BeastDef.MIX_DAQT2_REG_SIZE)
                self.mix_daqt2 = MIXDAQT2SGR(axi4_bus, use_signal_meter1=False, use_spi=False, use_gpio=False)
            else:
                self.mix_daqt2 = ipcore
            self.pl_signal_meter_device = self.mix_daqt2.signal_meter0
            self.range_ctrl = range_ctrl
            self.dcac_ctrl = dcac_ctrl
            self.output_ctrl = output_ctrl
        elif not i2c and not range_ctrl and not dcac_ctrl and not output_ctrl and not pl_signal_meter and not ipcore:
            self.range_ctrl = Pin(None, BeastDef.BEAST_RANGE_CTRL_PIN)
            self.dcac_ctrl = Pin(None, BeastDef.BEAST_DCAC_CTRL_PIN)
            self.output_ctrl = Pin(None, BeastDef.BEAST_OUTPUT_CTRL_PIN)
            self.pl_signal_meter_device = MIXSignalMeterSGEmulator(
                "mix_signalmeter_sg_emulator", BeastDef.SIGNAL_METER_REG_SIZE)

        self._mask = 0

    def module_init(self):
        '''
        Configure GPIO pin default direction.

        This needs to be outside of __init__();
        Because when GPIO expander is behind an i2c-mux, set_dir() will fail unless
        i2c-mux channel is set, and setting channel is an external action beyond module.
        See example below for usage.

        Returns:
            string, "done", api execution successful.

        Examples:
            # GPIO expander directly connected to xavier, not behind i2c-mux:
            beast = Beast(...)
            beast.board_init()

            # GPIO expander is connected to downstream port of i2c-mux:
            beast = Beast(...)
            # some i2c_mux action
            ...
            beast.board_init()

        '''
        self.range_ctrl.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.dcac_ctrl.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.output_ctrl.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)

        # Use max range is 20 Vpp as initial range
        self.select_range('AC_VOLT', 20)

        self.load_calibration()
        return "done"

    def select_range(self, signal_type, value):
        '''
        Select Beast measurement range. All support range shown as below.

        Args:
            signal_type:    string, ['DC_VOLT', 'AC_VOLT'], Range signal_type string.
            value:          int, [2, 20], Range value.

        Returns:
            string, "done", api execution successful.

        '''
        assert signal_type in ["DC_VOLT", "AC_VOLT"]
        assert value in BeastDef.RANGE_VALUE_LIST

        if signal_type == "DC_VOLT":
            self.dcac_ctrl.set_level(BeastDef.IO_LOW_LEVEL)
        else:
            self.dcac_ctrl.set_level(BeastDef.IO_HIGH_LEVEL)

        if value == BeastDef.RANGE_VALUE_LIST[0]:
            self.board_gain = BeastDef.GAIN1
            self.range_ctrl.set_level(BeastDef.IO_LOW_LEVEL)
        else:
            self.board_gain = BeastDef.GAIN10
            self.range_ctrl.set_level(BeastDef.IO_HIGH_LEVEL)
        self.signal_type = signal_type
        return 'done'

    def enable_continuous_measure(self):
        '''
        Beast enable_continuous_measure function. board data will be copyed to dma when this function called.

        Returns:
            string, "done", api execution successful.

        '''
        self.adc_enable()
        self.pl_signal_meter_device.open()
        self.pl_signal_meter_device.enable_upframe(BeastDef.UPFRAME_MODE)

        return 'done'

    def disable_continuous_measure(self):
        '''
        Beast disable_continuous_measure function. Data will disable upload, when this function called.

        Returns:
            string, "done", api execution successful.

        '''
        self.adc_disable()
        self.pl_signal_meter_device.disable_upframe()
        self.pl_signal_meter_device.close()

        return 'done'

    def set_measure_mask(self, mask=0):
        '''
        Beast set signal meter measure mask.

        Args:
            mask:    int, default 0, mask bit value shown as below.

            +---------------+-------------------+
            |   mask        |       function    |
            +===============+===================+
            | bit[0:3]      | Reserved          |
            +---------------+-------------------+
            | bit[4]        | Frequency mask    |
            +---------------+-------------------+
            | bit[5]        | Duty mask         |
            +---------------+-------------------+
            | bit[6]        | Vpp mask          |
            +---------------+-------------------+
            | bit[7]        | rms mask          |
            +---------------+-------------------+

        Returns:
            string, "done", api execution successful.

        '''
        self._mask = mask
        return "done"

    def frequency_measure(self, duration, measure_type="LP"):
        '''
        Measure input signal frequncy and duty in a defined duration.

        Args:
            duration:      int, [1~2000], millisecond time to measure frequncy.
            measure_type:  string, ["HP", "LP"], default "LP", type of measure.

        Returns:
            list, [value, value], result value contain freq and duty, units are Hz, %.

        Examples:
            # adc_enable() and adc_disable() will operate on Pin
            # which might belongs to another i2c Mux port from on-board eeprom so put outside.
            beast.adc_enable()
            ret = beast.frequency_measure(10)
            beast.adc_disable()
            # ret will be list: [freq, duty]

        '''
        assert isinstance(duration, int) and duration > 0 and duration <= 2000
        assert measure_type in ["HP", "LP"]

        self.pl_signal_meter_device.open()
        self.pl_signal_meter_device.set_vpp_interval(BeastDef.BEAST_VPP_DURATION)
        self.pl_signal_meter_device.start_measure(duration, BeastDef.BEAST_SAMPLE_RATE, self._mask)
        freq = self.pl_signal_meter_device.measure_frequency(measure_type)
        duty = self.pl_signal_meter_device.duty()
        self.pl_signal_meter_device.close()

        return [freq, duty]

    def vpp_measure(self, duration):
        '''
        Measure input signal vpp, max and min voltage in a defined duration.

        Args:
            duration:   int, [1~2000], millisecond time to measure vpp.

        Returns:
            list, [value, value, value], result value contain vpp, max and min voltage, unit is mV.

        Examples:
            # adc_enable() and adc_disable() will operate on Pin
            # which might belongs to another i2c Mux port from on-board eeprom so put outside.
            beast.adc_enable()
            ret = beast.vpp_measure(10)
            beast.adc_disable()
            # ret will be list: [vpp, max, min]

        '''
        assert isinstance(duration, int) and duration > 0 and duration <= 2000

        self.pl_signal_meter_device.open()
        self.pl_signal_meter_device.set_vpp_interval(BeastDef.BEAST_VPP_DURATION)
        self.pl_signal_meter_device.start_measure(duration, BeastDef.BEAST_SAMPLE_RATE, self._mask)
        result = self.pl_signal_meter_device.vpp()
        vpp = (result[2] * BeastDef.VPP_SCALE_GAIN + BeastDef.VPP_SCALE_OFFSET) * self.board_gain
        max_data = (result[0] * BeastDef.SCALE_GAIN + BeastDef.SCALE_OFFSET) * self.board_gain
        min_data = (result[1] * BeastDef.SCALE_GAIN + BeastDef.SCALE_OFFSET) * self.board_gain

        if self.is_use_cal_data():
            if self.board_gain == BeastDef.GAIN1:
                vpp = self.calibrate('VPP_2V', vpp)
            else:
                if self.frequency_measure(BeastDef.DURATION)[0] <= BeastDef.BEAST_HIGH_FREQ_THRESHOLD:
                    vpp = self.calibrate('LOW_FREQ_VPP_20V', vpp)
                else:
                    vpp = self.calibrate('HIGH_FREQ_VPP_20V', vpp)

        self.pl_signal_meter_device.close()

        return [vpp, max_data, min_data]

    def rms_measure(self, duration):
        '''
        Measure input signal rms and average voltage in a defined duration.

        Args:
            duration:   int, [1~2000], millisecond time to measure rms.

        Returns:
            list, [value, value], result value contain rms and average voltage, unit is mV.

        Examples:
            # adc_enable() and adc_disable() will operate on Pin
            # which might belongs to another i2c Mux port from on-board eeprom so put outside.
            beast.adc_enable()
            ret = beast.rms_measure(10)
            beast.adc_disable()
            # ret will be list: [rms, average]

        '''
        assert isinstance(duration, int) and duration > 0 and duration <= 2000

        self.pl_signal_meter_device.open()
        self.pl_signal_meter_device.set_vpp_interval(BeastDef.BEAST_VPP_DURATION)
        self.pl_signal_meter_device.start_measure(duration, BeastDef.BEAST_SAMPLE_RATE, self._mask)
        result = self.pl_signal_meter_device.rms()
        rms = (result[0] * BeastDef.RMS_SCALE_GAIN + BeastDef.RMS_SCALE_OFFSET) * self.board_gain
        average = (result[1] * BeastDef.SCALE_GAIN + BeastDef.SCALE_OFFSET) * self.board_gain

        if self.is_use_cal_data() and self.signal_type == "AC_VOLT":
            if self.board_gain == BeastDef.GAIN1:
                rms = self.calibrate('RMS_2V', rms)
            else:
                if self.frequency_measure(BeastDef.DURATION)[0] <= BeastDef.BEAST_HIGH_FREQ_THRESHOLD:
                    rms = self.calibrate('LOW_FREQ_RMS_20V', rms)
                else:
                    rms = self.calibrate('HIGH_FREQ_RMS_20V', rms)

        self.pl_signal_meter_device.close()

        return [rms, average]

    def level(self):
        '''
        Get current voltage level.

        Returns:
            int, [0, 1], 0 for low level, 1 for high level.

        '''
        return self.pl_signal_meter_device.level()

    def adc_enable(self):
        '''
        This function is used for enable adc output, it is an internal interface function.

        Returns:
            string, "done", api execution successful.

        '''
        self.output_ctrl.set_level(BeastDef.IO_LOW_LEVEL)
        return "done"

    def adc_disable(self):
        '''
        This function is used for disable adc output, it is an internal interface function.

        Returns:
            string, "done", api execution successful.

        '''
        self.output_ctrl.set_level(BeastDef.IO_HIGH_LEVEL)
        return "done"


class Beast(BeastBase):
    '''
    Beast is a general medium-speed digital instrument module.

    compatible = ["GQQ-SCP001001-000"]

    Beast will be used for voltage,
    frequency measurement and waveform acquisition. Note that if use legacy ipcore pl_signal_meter,
    range_ctrl, dcac_ctrl and output_ctrl can not be None; If use lynx ipcore MIXDAQT2 and use
    MIXDAQT2 inside gpio, range_ctrl, dcac_ctrl or output_ctrl can be None,otherwise, none of them
    can be None. The lynx ipcore MIXDAQT2 ipcore which include GPIO, spi, SignalMeter0 and SignalMeter1,
    and their register address have offset compared with the legacy ipcore: PLGPIO, PLSPIBus and PLSignalMeter.
    This driver is compatible with both legacy and lynx ipcore.
    This class is driver for normal boot.
    Note that default calibration function is enabled, default range is AC 20V.

    Args:
        i2c:              instance(I2C),             used to control eeprom and nct75 sensor.
        range_ctrl:       instance(GPIO),                used to control Beast range.
        dcac_ctrl:        instance(GPIO),                used to control DC/AC mode.
        output_ctrl:      instance(GPIO),                used to control AD5231 disable/enable state.
        pl_signal_meter:  instance(PLSignalMeter),      used to access PLSignalMeter ipcore.
        mix_daqt2:        instance(MIXDAQT2),          used to access PLGPIO, PLSignalMeter ipcore.

    Examples:
        # use non-aggregated IP
            i2c = I2CBus('/dev/MIX_I2C_0')
            # use cat9555 to control range, DC/AC and AD5231 enable state.
            cat9555 = CAT9555(0x20, i2c_bus)
            range_ctrl = Pin(cat9555, 5)
            dcac_ctrl = Pin(cat9555, 6)
            output_ctrl = Pin(cat9555, 4)
            pl_signal_meter = PLSignalMeter('/dev/MIX_Signal_Meter_0')
            beast = Beast(i2c,range_ctrl, dcac_ctrl, output_ctrl, pl_signal_meter)

        # use MIXDAQT2 aggregated IP, not use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            # use cat9555 to control range, DC/AC and AD5231 enable state.
            cat9555 = CAT9555(0x20, i2c_bus)
            range_ctrl = Pin(cat9555, 5)
            dcac_ctrl = Pin(cat9555, 6)
            output_ctrl = Pin(cat9555, 4)
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, False)
            beast = Beast(i2c,range_ctrl, dcac_ctrl, output_ctrl, None, mix_daqt2)

        # use MIXDAQT2 aggregated IP, use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, True)
            beast = Beast(i2c, None, None, None, None, mix_daqt2)

        # if GPIO expander is behind a i2c-mux, set i2c-mux channel then call
            beast.board_init()
          to set default gpio direction before using the module to measure.

        # suppose input signal is 1000 Hz, vpp 1000 mV square waveform
        beast.select_ragne('AC_VOLT', 2, 'V')

        # frequncy meaurement
        result = beast.frequency_measure(100) # measure 100 ms
        print("freq={}Hz, duty={}%".format(result.[0], result[1]))
        # terminal show "freq=xxxHz, duty=xx%"

        # VPP measurement
        result = beast.vpp_measure(100) # measure 100 ms
        print("vpp={}mV, max={}mV, min={}mV".format(result[0], result[1], result{2}))
        # terminal show "vpp=xxxmV, max=xxxmV, min=xxxmV"

        # rms measurement
        result = beast.rms_measure(100) # measure 100 ms
        print("rms={}mV, average={}mV".format(result[0], result[1]))
        # terminal show "rms=xxxmV, average=xxxmV"

        # upload data in 100ms through dma
        beast.enable_continuous_measure()
        time.sleep(100)
        beast.disable_continuous_measure()

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP001001-000"]

    def __init__(self, i2c, range_ctrl=None, dcac_ctrl=None, output_ctrl=None, pl_signal_meter=None, ipcore=None):
        super(Beast, self).__init__(i2c, range_ctrl, dcac_ctrl, output_ctrl, pl_signal_meter, ipcore,
                                    BeastDef.EEPROM_DEV_ADDR, BeastDef.SENSOR_DEV_ADDR)
