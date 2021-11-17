# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_daqt2_sg_r import MIXDAQT2SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.pin import Pin


__author__ = 'Chujie.Lan@SmartGiant'
__version__ = '1.2'


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
    TIME_OUT = 0

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


class BeastBaseException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class BeastBase(SGModuleDriver):
    '''
    Base class of Beast and BeastCompatible.
    Providing common Beast methods.

    Args:
        i2c:              instance(I2C),              used to control eeprom and nct75 sensor.
        range_ctrl_pin:   instance(GPIO),             used to control Beast range.
        dcac_ctrl_pin:    instance(GPIO),             used to control DC/AC mode.
        output_ctrl_pin:  instance(GPIO),             used to control AD5231 disable/enable state.
        pl_signal_meter:  instance(PLSignalMeter),    used to access PLSignalMeter ipcore.
        ipcore:           instance(MIXDAQT2SGR),      used to access PLGPIO, PLSignalMeter ipcore.
        eeprom_dev_addr:  int,                        eeprom device address.
        sensor_dev_addr:  int,                        NCT75 device address.

    '''

    rpc_public_api = ['select_range', 'enable_continuous_measure', 'disable_continuous_measure',
                      'set_measure_mask', 'frequency_measure', 'vpp_measure', 'rms_measure',
                      'level', 'adc_enable', 'adc_disable'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, range_ctrl_pin=None, dcac_ctrl_pin=None, output_ctrl_pin=None, pl_signal_meter=None,
                 ipcore=None, eeprom_dev_addr=BeastDef.EEPROM_DEV_ADDR, sensor_dev_addr=BeastDef.SENSOR_DEV_ADDR):

        if i2c is None:
            super(BeastBase, self).__init__(None, None, range_table=beast_range_table)
        else:
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.nct75 = NCT75(sensor_dev_addr, i2c)
            super(BeastBase, self).__init__(self.eeprom, self.nct75, range_table=beast_range_table)

        if i2c and range_ctrl_pin and dcac_ctrl_pin and output_ctrl_pin and pl_signal_meter and not ipcore:
            self.range_ctrl_pin = range_ctrl_pin
            self.dcac_ctrl_pin = dcac_ctrl_pin
            self.output_ctrl_pin = output_ctrl_pin
            if isinstance(pl_signal_meter, basestring):
                axi4_bus = AXI4LiteBus(pl_signal_meter, BeastDef.SIGNAL_METER_REG_SIZE)
                self.pl_signal_meter_device = MIXSignalMeterSG(axi4_bus)
            else:
                self.pl_signal_meter_device = pl_signal_meter
        elif i2c and not range_ctrl_pin and not dcac_ctrl_pin and not output_ctrl_pin and not pl_signal_meter \
                and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, BeastDef.MIX_DAQT2_REG_SIZE)
                self.mix_daqt2 = MIXDAQT2SGR(axi4_bus, use_signal_meter1=False, use_spi=False, use_gpio=True)
            else:
                self.mix_daqt2 = ipcore
            self.pl_signal_meter_device = self.mix_daqt2.signal_meter0
            self.range_ctrl_pin = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_RANGE_CTRL_PIN)
            self.dcac_ctrl_pin = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_DCAC_CTRL_PIN)
            self.output_ctrl_pin = Pin(self.mix_daqt2.gpio, BeastDef.BEAST_OUTPUT_CTRL_PIN)
        elif i2c and range_ctrl_pin and dcac_ctrl_pin and output_ctrl_pin and not pl_signal_meter and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, BeastDef.MIX_DAQT2_REG_SIZE)
                self.mix_daqt2 = MIXDAQT2SGR(axi4_bus, use_signal_meter1=False, use_spi=False, use_gpio=False)
            else:
                self.mix_daqt2 = ipcore
            self.pl_signal_meter_device = self.mix_daqt2.signal_meter0
            self.range_ctrl_pin = range_ctrl_pin
            self.dcac_ctrl_pin = dcac_ctrl_pin
            self.output_ctrl_pin = output_ctrl_pin
        else:
            raise BeastBaseException("Invalid parameter, please check")

        self._mask = 0

    def post_power_on_init(self, timeout=BeastDef.TIME_OUT):
        '''
        Init Beast module to a know harware state.

        This function will set gpio pin io direction to output and set default range to '20Vpp'

        Args:
            timeout:      float, unit Second, execute timeout

        '''
        self.reset(timeout)

    def pre_power_down(self, timeout=BeastDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set gpio pin io direction to output.

        Args:
            timeout:      float, unit Second, execute timeout

        '''
        self.range_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.dcac_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.output_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)

    def reset(self, timeout=BeastDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, unit Second, execute timeout.

        '''
        self.range_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.dcac_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        self.output_ctrl_pin.set_dir(BeastDef.PIN_OUTPUT_DIRECTION)
        # Use max range is 20 Vpp as initial range
        self.select_range('AC_VOLT', 20)

    def get_driver_version(self):
        '''
        Get beast driver version.

        Returns:
            string, current driver version.

        '''
        return __version__

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
            self.dcac_ctrl_pin.set_level(BeastDef.IO_LOW_LEVEL)
        else:
            self.dcac_ctrl_pin.set_level(BeastDef.IO_HIGH_LEVEL)

        if value == BeastDef.RANGE_VALUE_LIST[0]:
            self.board_gain = BeastDef.GAIN1
            self.range_ctrl_pin.set_level(BeastDef.IO_LOW_LEVEL)
        else:
            self.board_gain = BeastDef.GAIN10
            self.range_ctrl_pin.set_level(BeastDef.IO_HIGH_LEVEL)
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
        self.output_ctrl_pin.set_level(BeastDef.IO_LOW_LEVEL)
        return "done"

    def adc_disable(self):
        '''
        This function is used for disable adc output, it is an internal interface function.

        Returns:
            string, "done", api execution successful.

        '''
        self.output_ctrl_pin.set_level(BeastDef.IO_HIGH_LEVEL)
        return "done"


class Beast(BeastBase):
    '''
    Beast is a general medium-speed digital instrument module.

    compatible = ["GQQ-L2CL-5-020"]

    Beast will be used for voltage,
    frequency measurement and waveform acquisition. Note that if use legacy ipcore pl_signal_meter,
    range_ctrl_pin, dcac_ctrl_pin and output_ctrl_pin can not be None; If use lynx ipcore MIXDAQT2 and use
    MIXDAQT2 inside gpio, range_ctrl_pin, dcac_ctrl_pin or output_ctrl_pin can be None,otherwise, none of them
    can be None. The lynx ipcore MIXDAQT2 ipcore which include GPIO, spi, SignalMeter0 and SignalMeter1,
    and their register address have offset compared with the legacy ipcore: PLGPIO, PLSPIBus and PLSignalMeter.
    This driver is compatible with both legacy and lynx ipcore.
    This class is driver for normal boot.
    Note that default calibration function is enabled, default range is AC 20V.

    Args:
        i2c:              instance(I2C),             used to control eeprom and nct75 sensor.
        range_ctrl_pin:       instance(GPIO),                used to control Beast range.
        dcac_ctrl_pin:        instance(GPIO),                used to control DC/AC mode.
        output_ctrl_pin:      instance(GPIO),                used to control AD5231 disable/enable state.
        pl_signal_meter:  instance(PLSignalMeter),      used to access PLSignalMeter ipcore.
        mix_daqt2:        instance(MIXDAQT2),          used to access PLGPIO, PLSignalMeter ipcore.

    Examples:
        # use non-aggregated IP
            i2c = I2CBus('/dev/MIX_I2C_0')
            # use cat9555 to control range, DC/AC and AD5231 enable state.
            cat9555 = CAT9555(0x20, i2c_bus)
            range_ctrl_pin = Pin(cat9555, 5)
            dcac_ctrl_pin = Pin(cat9555, 6)
            output_ctrl_pin = Pin(cat9555, 4)
            pl_signal_meter = PLSignalMeter('/dev/MIX_Signal_Meter_0')
            beast = Beast(i2c, range_ctrl_pin, dcac_ctrl_pin, output_ctrl_pin, pl_signal_meter)

        # use MIXDAQT2 aggregated IP, not use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            # use cat9555 to control range, DC/AC and AD5231 enable state.
            cat9555 = CAT9555(0x20, i2c_bus)
            range_ctrl_pin = Pin(cat9555, 5)
            dcac_ctrl_pin = Pin(cat9555, 6)
            output_ctrl_pin = Pin(cat9555, 4)
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, False)
            beast = Beast(i2c, range_ctrl_pin, dcac_ctrl_pin, output_ctrl_pin, None, mix_daqt2)

        # use MIXDAQT2 aggregated IP, use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, True)
            beast = Beast(i2c, None, None, None, None, mix_daqt2)

        # if GPIO expander is behind a i2c-mux, set i2c-mux channel then call
            beast.post_power_on_init()
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
    compatible = ["GQQ-L2CL-5-010"]

    def __init__(self, i2c, range_ctrl_pin=None, dcac_ctrl_pin=None, output_ctrl_pin=None, pl_signal_meter=None,
                 ipcore=None):
        super(Beast, self).__init__(i2c, range_ctrl_pin, dcac_ctrl_pin, output_ctrl_pin, pl_signal_meter, ipcore,
                                    BeastDef.EEPROM_DEV_ADDR, BeastDef.SENSOR_DEV_ADDR)
