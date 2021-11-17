# -*- coding: utf-8 -*-
import os
import re
import copy


class IIOXADCDef:
    SYS_PATH_IIO = '/sys/bus/iio/devices'
    TEMPERATURE_FILENAME = 'in_temp0_raw'
    READ_SIZE = 200
    TEMPERATURE_REFERENCE_LEVEL = 503.975  # came from Xilinx official documentation <ug480_7Series_XADC.pdf>
    TEMPERATURE_OFFSET = 273.15  # came from Xilinx official documentation <ug480_7Series_XADC.pdf>
    REFERENCE_LEVEL = 1000.0
    ADC_RESOLUTION = 4096  # came from Xilinx official documentation <ug480_7Series_XADC.pdf>

    # The full name of following channels is like "in_temp0_raw, in_voltage8_vpvn_raw, in_voltage9_vaux4_raw".
    TEMPERATURE_CHANNEL = 'temp0'
    VPVN_CHANNEL = 'vpvn'
    VAUX0_CHANNEL = 'vaux0'
    VAUX1_CHANNEL = 'vaux1'
    VAUX2_CHANNEL = 'vaux2'
    VAUX3_CHANNEL = 'vaux3'
    VAUX4_CHANNEL = 'vaux4'
    VAUX5_CHANNEL = 'vaux5'
    VAUX6_CHANNEL = 'vaux6'
    VAUX7_CHANNEL = 'vaux7'
    VAUX8_CHANNEL = 'vaux8'
    VAUX9_CHANNEL = 'vaux9'
    VAUX10_CHANNEL = 'vaux10'
    VAUX11_CHANNEL = 'vaux11'
    VAUX12_CHANNEL = 'vaux12'
    VAUX13_CHANNEL = 'vaux13'
    VAUX14_CHANNEL = 'vaux14'
    VAUX15_CHANNEL = 'vaux15'
    ANALOG_IN_CHANNELS = [VPVN_CHANNEL, VAUX0_CHANNEL, VAUX1_CHANNEL, VAUX2_CHANNEL,
                          VAUX3_CHANNEL, VAUX4_CHANNEL, VAUX5_CHANNEL, VAUX6_CHANNEL,
                          VAUX7_CHANNEL, VAUX8_CHANNEL, VAUX9_CHANNEL, VAUX10_CHANNEL,
                          VAUX11_CHANNEL, VAUX12_CHANNEL, VAUX13_CHANNEL, VAUX14_CHANNEL,
                          VAUX15_CHANNEL]

    BIPOLAR = "bipolar"
    UNIPOLAR = "unipolar"
    CRITICAL_CODE = {BIPOLAR: [-2048, 2047], UNIPOLAR: [4095]}


class XADCChannel(object):
    '''
    The XADCChannel class record the xadc channel sysfs filename and conversion function

    Args:
        filename:          string, ['in_temp0_raw', 'in_voltage10_vaux8_raw'],   the channel sysfs interface filename.
        convert_function:  instance,   the xadc channel value conversion function.

    '''

    def __init__(self, filename, convert_function):
        self.filename = filename
        self.convert_function = convert_function


class IIOXADCException(Exception):
    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class IIOXADC(object):
    '''
    Singleton wrapper of Xilinx I2C driver

    ClassType = XADC

    This is to ensure only 1 instance is created for the same char device
    in /dev/, even if instantiated multiple times.

    Args:
        device:   string,    device full path.

    Examples:
        xadc_1 = IIOXADC('dev_path')
        xadc_2 = IIOXADC('dev_path')
        assert xadc_1 == xadc_2          # True

    '''
    # class variable to host all i2c bus instances created.
    instances = {}

    def __new__(cls, device):
        if device in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _IIOXADC(device)
            cls.instances[device] = instance
        return cls.instances[device]


class _IIOXADC(object):
    '''
    XADC IIO decive API, support 17 external analog input channels, need to use kernel driver

    Args:
        device:   string,    xadc device name.

    Examples:
        xadc = IIOXADC("iio:device0")

    '''
    rpc_public_api = ['read_value', 'read_temperature', 'read_voltage']

    def __init__(self, device):
        self.dev_name = device
        self._channels_instance = None
        self._init_channel_instance()
        self.channels = copy.deepcopy(self._channels_instance)
        if "temp0" in self.channels:
            self.channels.pop("temp0")

    def _init_channel_instance(self):
        '''
        This funtion is used to create the instance for each channel, it is an internal interface function.

        '''
        all_filename = os.listdir("%s/%s" % (IIOXADCDef.SYS_PATH_IIO, self.dev_name))
        raw_filename = [x for x in all_filename if '_raw' in x]

        self._channels_instance = dict()
        self._channels_instance[IIOXADCDef.TEMPERATURE_CHANNEL] = XADCChannel(
            IIOXADCDef.TEMPERATURE_FILENAME, self.convert_temperature)
        raw_filename.remove(IIOXADCDef.TEMPERATURE_FILENAME)

        for name in raw_filename:
            # The format of these file names is like "in_voltage8_vpvn_raw, in_voltage9_vaux4_raw".
            channel_str = re.match(r'in_(\w+)_(\w+)_raw', name)
            if channel_str is not None:
                channel_name = channel_str.group(2)
                if channel_name in IIOXADCDef.ANALOG_IN_CHANNELS:
                    self._channels_instance[channel_name] = XADCChannel(name, self.convert_voltage)
                    all_property = os.listdir("%s/%s/of_node/xlnx,channels/channel@%d" % (IIOXADCDef.SYS_PATH_IIO,
                                              self.dev_name, IIOXADCDef.ANALOG_IN_CHANNELS.index(channel_name)))
                    if "xlnx,bipolar" in all_property:
                        self._channels_instance[channel_name].polarity = "bipolar"
                    else:
                        self._channels_instance[channel_name].polarity = "unipolar"

    def convert_temperature(self, value):
        '''
        Convert the adc code to temperature value.

        Args:
            int, adc values.

        Returns:
            float, value, unit C, the real temperature, unit is degree C.

        Examples:
            temp = xadc.convert_temperature(2456)

        Raises:
            calc formula:
                Temp(C) = (12 bit ADC code) * 503.975 / 4096 - 273.15,
                it came from Xilinx official documentation <ug480_7Series_XADC.pdf>.

        '''
        result = value * IIOXADCDef.TEMPERATURE_REFERENCE_LEVEL / IIOXADCDef.ADC_RESOLUTION
        result = result - IIOXADCDef.TEMPERATURE_OFFSET
        return result

    def convert_voltage(self, value):
        '''
        Convert the adc code to voltage value.

        Args:
            value:    int, adc code values.

        Returns:
            float, value, unit mV, the real voltage after adc.

        Examples:
            voly = xadc.convert_voltage(2456)

        Raises:
            calc formula:
                Volt_value = (ADC code) * 1000.0 / 4096.0,
                it came from Xilinx official documentation <ug480_7Series_XADC.pdf>.

        '''
        return value * IIOXADCDef.REFERENCE_LEVEL / IIOXADCDef.ADC_RESOLUTION

    def read_value(self, channel, count=1):
        '''
        Read xadc temperature or voltage at single conversion mode.

        Args:
            channel:    string, ['temp', vpvn', 'vaux0'~'vaux15'], it depend on fpga open which ones.
            count:      int,    number of value to read.

        Returns:
            float, value, for voltage unit is mV, for temperature unit is degree C,
                          note that the result is averaged.

        Raises:
            AssertionError: channel is invalid.

        Examples:
            value = xadc.read_value("vpvn")

        '''
        assert channel in self._channels_instance.keys()

        channel_instance = self._channels_instance[channel]
        fd = open('%s/%s/%s' % (IIOXADCDef.SYS_PATH_IIO, self.dev_name, channel_instance.filename), 'r')

        values = []
        for x in range(count):
            value = fd.read(IIOXADCDef.READ_SIZE)
            if hasattr(channel_instance, "polarity"):
                if int(value) in IIOXADCDef.CRITICAL_CODE[channel_instance.polarity]:
                    fd.close()
                    raise IIOXADCException("Warning, the voltage value exceeds the range")
            values.append(float(value))
            fd.seek(0)
        fd.close()

        # The value obtained by reading the files are ADC code, need to be converted.
        values = list(map(channel_instance.convert_function, values))
        return sum(values) / count

    def read_temperature(self):
        '''
        Read xadc temperature.

        Returns:
            float, value, unit C, unit is degree C.

        Examples:
            temperature = xadc.read_temperature()

        '''
        return self.read_value(IIOXADCDef.TEMPERATURE_CHANNEL)

    def read_voltage(self, channel, count=1):
        '''
        Read voltage at single conversion mode.

        Args:
            channel:    string, ['vpvn', 'vaux0'~'vaux15'], it depend on fpga open which ones.
            count:      int,    number of voltage to read.

        Returns:
            float, value, unit mV, average voltage after conversion.

        Raises:
            AssertionError: channel is invalid.

        Examples:
            voltage = xadc.read_voltage("vpvn")

        '''
        assert channel in self.channels

        return self.read_value(channel, count)
