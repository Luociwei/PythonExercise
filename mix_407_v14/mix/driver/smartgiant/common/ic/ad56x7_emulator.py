# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'qingzhen.zhu@SmartGiant'
__version__ = '0.2'


class AD56X7RDef:

    COMMAND_WRITE_TO_INPUT_REG = 0x00
    COMMAND_UPDATE_DAC_REG = 0x01
    COMMAND_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x02
    COMMAND_WRITE_AND_UPDATE_DAC_CHAN = 0x03
    COMMAND_POWER_UP_OR_DOWN = 0x04
    COMMAND_RESET = 0x05
    COMMAND_LDAC_SETUP = 0x06
    COMMAND_REFERENCE_SETUP = 0x07
    AD5667_RESLUTION = 16
    AD5647_RESLUTION = 14
    AD5627_RESLUTION = 12


class AD56X7RException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s' % (err_str)

    def __str__(self):
        return self.err_reason


class AD56X7REmulator(object):
    '''
    AD56X7R function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD56X7R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD56X7R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad56x7r = AD56X7R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        # 7-bit slave address. The two LSBs are variable
        self.dev_name = dev_name

        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._recorder.record("{}.__init__()".format(self.dev_name))

    def reset(self, mode="ALL_REG"):
        '''
        AD56X7R reset chip

        Args:
            mode:    string, ["DAC_AND_INPUT_SHIFT_REG", "ALL_REG"], default "ALL_REG".

        Examples:
            ad56x7r.reset("ALL_REG")

        '''
        assert mode in ["DAC_AND_INPUT_SHIFT_REG", "ALL_REG"]
        self._recorder.record("%s reset mode [%s]" % (self.dev_name, str(mode)))

    def select_work_mode(self, channel, mode="NORMAL"):
        '''
        AD56X7R select work mode

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel.
            mode:       string, ["NORMAL", "1KOHM_GND", "100KOHM_GND", "HIGH-Z"], default is "NORMAL".

        Examples:
            ad56x7r.select_work_mode(0,"NORMAL")

        '''
        assert channel in [0, 1, 2]
        assert mode in ["NORMAL", "1KOHM_GND", "100KOHM_GND", "HIGH-Z"]
        self._recorder.record(
            "%s select work mode [%s] for channel [%s]" % (
                self.dev_name, mode, str(channel)))

    def set_ldac_pin_enable(self, channel):
        '''
        AD56X7R configure ldac pin enable

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel.

        Examples:
            ad56x7r.set_ldac_pin_enable(0)

        '''
        assert channel in [0, 1, 2]
        self._recorder.record(
            "%s set_ldac_pin_enable for channel [%s]" % (
                self.dev_name, str(channel)))

    def set_ldac_pin_invalid(self, channel):
        '''
        AD56X7R configure ldac pin enable

        Args:
            channel:    int, [0, 1, 2], 2 mean both channel.

        Examples:
            ad56x7r.set_ldac_pin_enable(0)

        '''
        assert channel in [0, 1, 2]
        self._recorder.record(
            "%s set_ldac_pin_invalid for channel [%s]" % (
                self.dev_name, str(channel)))

    def output_volt_dc(self, channel, volt):
        '''
        AD56X9R output voltage

        Args:
            channel:  int, [0, 1, 2, 3, 4, 5, 6, 7, 8], 8 mean both channel.
            volt:     float/int, [0~reference voltage], unit mV.

        Examples:
            ad56x9r.output_volt_dc('A', 1000)

        '''
        self._recorder.record("%s set channel [%s] voltage [%s]" % (self.dev_name, str(channel), str(volt)))
        return True


class AD5667REmulator(AD56X7REmulator):
    '''
    AD5667R function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD5667R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        ref_mode:   string, ["EXTERN", "INTERNAL"], defualt "EXTERN", reference mode of AD5667R.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5667R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5667r = AD5667R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5667REmulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5667_RESLUTION
        self.ref_mode = "EXTERN"

    def get_reference(self):
        '''
        AD5667R get mode of reference voltage

        :example:  result = ad5667r.reference
        '''
        return self.ref_mode

    def set_reference(self, ref_mode):
        '''
        AD5667R set mode of reference voltage

        :param ref_mode:  str("INTERNAL,"EXTERN")  default is "EXTERN"
        :example:         ad5667r.reference = "EXTERN"
        '''
        assert ref_mode in ["EXTERN", "INTERNAL"]
        self.ref_mode = ref_mode
        self._recorder.record("%s set reference to [%s]" % (self.dev_name, self.ref_mode))


class AD5667Emulator(AD56X7REmulator):
    '''
    AD5667 function class

    Args:
        dev_addr:   hexmial,             I2C device address of AD5667.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5667.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5667 = AD5667(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5667Emulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5667_RESLUTION
        self.ref_mode = "EXTERN"


class AD5647REmulator(AD56X7REmulator):
    '''
    AD5647R function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD5647R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5647R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5647r = AD5647R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5647REmulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5647_RESLUTION
        self.ref_mode = "EXTERN"

    def get_reference(self):
        '''
        AD5647R get mode of reference voltage

        :example:  result = ad5647r.reference
        '''
        return self.ref_mode

    def set_reference(self, ref_mode):
        '''
        AD5647R set mode of reference voltage

        :param ref_mode: str("INTERNAL,"EXTERN"), default is "EXTERN"
        :example:        ad5647r.reference = "EXTERN"
        '''
        assert ref_mode in ["EXTERN", "INTERNAL"]
        self.ref_mode = ref_mode
        self._recorder.record("%s set reference to [%s]" % (self.dev_name, self.ref_mode))


class AD5647Emulator(AD56X7REmulator):
    '''
    AD5647 function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD5647.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5647.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5647 = AD5647(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5647Emulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5647_RESLUTION
        self.ref_mode = "EXTERN"


class AD5627Emulator(AD56X7REmulator):
    '''
    AD5627 function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             I2C device address of AD5627.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5627.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5627 = AD5627(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5627Emulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5627_RESLUTION
        self.ref_mode = "EXTERN"


class AD5627REmulator(AD56X7REmulator):
    '''
    AD5627R function class

    Args:
        dev_addr:   hexmial,             I2C device address of AD5627R.
        i2c_bus:    instance(I2C)/None,  Class instance of I2C bus,If not using this parameter,will create Emulator.
        mvref:      float, unit mV, default 2500.0, the reference voltage of AD5627R.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        ad5627r = AD5627R(0x50, i2c)

    '''

    def __init__(self, dev_name):
        super(AD5627REmulator, self).__init__(dev_name)
        self.resolution = AD56X7RDef.AD5627_RESLUTION
        self.ref_mode = "EXTERN"

    def get_reference(self):
        '''
        AD5627R get mode of reference voltage

        Returns:
            string, ['EXTERN', 'INTERNAL'], current reference mode

        Examples:
            result = ad5627r.reference
        '''
        return self.ref_mode

    def set_reference(self, ref_mode="EXTERN"):
        '''
        AD5627R set mode of reference voltage

        Args:
            param ref_mode: string, ["INTERNAL,"EXTERN"]  default is "EXTERN"

            Examples:
                ad5627r.reference = "EXTERN"
        '''
        assert ref_mode in ["EXTERN", "INTERNAL"]
        self.ref_mode = ref_mode
        self._recorder.record("%s set reference to [%s]" % (self.dev_name, self.ref_mode))
