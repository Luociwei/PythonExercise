# -*- coding: utf-8 -*-
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667
from mix.driver.smartgiant.common.module.mix_board import MIXBoard

__author__ = 'Hanyong.Huang@SmartGiant'
__version__ = '0.1'


class SG2238SP02PCADef:
    FAN_ON = "on"
    FAN_OFF = "off"
    DAC_OFFSET = 11388.9
    DAC_MAX_VOLTAGE = 8000
    DAC_MIN_VOLTAGE = -8000
    SIGNAL_TYPE = ["DC", "AC"]
    DAC_MAGNIFICATION_TIMES = 9.2
    IMPEDANCES = ["1Mohm", "50ohm"]
    DAC_CHANNEL = {"channel1": 0, "channel2": 1, "all": 2}
    AMPLIFICATION_LIST = ["gain1", "gain2", "gain3", "gain4"]
    CURRENT_RANGE = ["disable", "1500mA", "3000mA", "6000mA", "4500mA"]
    EEPROM_DEV_ADDR = 0x51
    AD5667_DEV_ADDR = 0x0E
    NCT75_DEV_ADDR = 0X49
    CAT9555_DEV_ADDR = 0x21
    AD5667_VREF_VOLTSGE = 2500


io_profile = {
    "on": [(4, 1)],
    "off": [(4, 0)],
    "DC": [(11, 0)],
    "AC": [(11, 1)],
    "1Mohm": [(8, 0)],
    "50ohm": [(8, 1)],
    "gain1": [(5, 1), (6, 0), (7, 0)],
    "gain2": [(5, 1), (6, 1), (7, 0)],
    "gain3": [(5, 1), (6, 0), (7, 1)],
    "gain4": [(5, 1), (6, 1), (7, 1)],
    "disable": [(0, 0), (1, 0), (9, 0), (10, 0)],
    "1500mA": [(0, 1), (1, 0), (9, 0), (10, 0)],
    "3000mA": [(0, 1), (1, 1), (9, 0), (10, 0)],
    "4500mA": [(0, 1), (1, 1), (9, 1), (10, 0)],
    "6000mA": [(0, 1), (1, 1), (9, 1), (10, 1)],
}

sg2238sp02pca_cal_info = {
    "128KHz": {
        'level1': {'unit_index': 0, 'limit': (141.4, 'mV')},
        'level2': {'unit_index': 1, 'limit': (282.8, 'mV')},
        'level3': {'unit_index': 2, 'limit': (1414, 'mV')},
        'level4': {'unit_index': 3, 'limit': (2828, 'mV')},
        'level5': {'unit_index': 4, 'limit': (5000, 'mV')},
        'level6': {'unit_index': 5, 'limit': (10000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (15000, 'mV')},
        'level8': {'unit_index': 7, 'limit': (20000, 'mV')}
    },
    "256KHz": {
        'level1': {'unit_index': 8, 'limit': (141.4, 'mV')},
        'level2': {'unit_index': 9, 'limit': (282.8, 'mV')},
        'level3': {'unit_index': 10, 'limit': (1414, 'mV')},
        'level4': {'unit_index': 11, 'limit': (2828, 'mV')},
        'level5': {'unit_index': 12, 'limit': (5000, 'mV')},
        'level6': {'unit_index': 13, 'limit': (10000, 'mV')},
        'level7': {'unit_index': 14, 'limit': (15000, 'mV')},
        'level8': {'unit_index': 15, 'limit': (20000, 'mV')}
    },
    "384KHz": {
        'level1': {'unit_index': 16, 'limit': (141.4, 'mV')},
        'level2': {'unit_index': 17, 'limit': (282.8, 'mV')},
        'level3': {'unit_index': 18, 'limit': (1414, 'mV')},
        'level4': {'unit_index': 19, 'limit': (2828, 'mV')},
        'level5': {'unit_index': 20, 'limit': (5000, 'mV')},
        'level6': {'unit_index': 21, 'limit': (10000, 'mV')},
        'level7': {'unit_index': 22, 'limit': (15000, 'mV')},
        'level8': {'unit_index': 23, 'limit': (20000, 'mV')}
    }
}


class SG2238SP02PCA(MIXBoard):
    '''
    The sg2238sp02pca module is a power amplifier.

    It has 4 levels of magnification
    for DC and AC signal, can control fan work, selecting impedance, setting offset value.
    In particular, this module only provides an interface for obtaining calibration values.
    Calibration is not provided The specific calibration needs to be implemented with the signal module.

    Args:
        i2c:     instance(I2C)/None,  if None, invoke emulator.

    Examples:
        if utility.is_pl_device(i2c1):
            axi4_bus = AXI4LiteBus(i2c1, 256)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(i2c1)
        sg2238sp02pca = SG2238SP02PCA(i2c_bus)

    '''

    rpc_public_api = ['module_init', 'fan_on', 'fan_off', 'select_voltage_gain',
                      'current_output', 'select_signal_type', 'select_impedance', 'set_offset',
                      'calibration_pipe'] + MIXBoard.rpc_public_api

    def __init__(self, i2c=None):
        self._cat9555 = CAT9555(SG2238SP02PCADef.CAT9555_DEV_ADDR, i2c)
        self._ad5667 = AD5667(SG2238SP02PCADef.AD5667_DEV_ADDR, i2c, SG2238SP02PCADef.AD5667_VREF_VOLTSGE)
        eeprom = CAT24C32(SG2238SP02PCADef.EEPROM_DEV_ADDR, i2c)
        nct75 = NCT75(SG2238SP02PCADef.NCT75_DEV_ADDR, i2c)

        super(SG2238SP02PCA, self).__init__(eeprom, nct75)

    def _io_set(self, key_name):
        '''
        Cat9555 io set

        Args:
            key_name:   string, (io_profile.keys()), Select control io list.

        Examples:
            self._io_set('DC')

        '''
        bits = io_profile[key_name]
        for bit in bits:
            self._cat9555.set_pin(bit[0], bit[1])

    def module_init(self):
        '''
        Module init

        Returns:
            string, "done", api execution successful.

        Examples:
            self.module_init()

        '''
        # init cat9555
        self._cat9555.set_pins_dir([0x00, 0x00])
        self._cat9555.set_ports([0x00, 0x00])

        # enable ad5667 all channel
        self._ad5667.reset()
        self._ad5667.select_work_mode(SG2238SP02PCADef.DAC_CHANNEL['all'])
        self._ad5667.set_ldac_pin_enable(SG2238SP02PCADef.DAC_CHANNEL['all'])

        # offset init
        self.set_offset('all', 0)

        # fan init
        self.fan_on()
        return "done"

    def fan_on(self):
        '''
        Open fan

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.fan_onfan_on()

        '''
        self._io_set(SG2238SP02PCADef.FAN_ON)
        return "Done"

    def fan_off(self):
        '''
        Close fan

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.fan_off()

        '''
        self._io_set(SG2238SP02PCADef.FAN_OFF)
        return "Done"

    def select_voltage_gain(self, gain):
        '''
        Select voltage amplification factor

        Args:
            gain:   string, ["gain1", "gian2", "gian3", gian4"], Voltage amplification factor.
                                                                 "gain1": the output voltage is amplified once times.
                                                                 "gain2": the output voltage is amplified twice.
                                                                 "gain3": the output voltage is tripled.
                                                                 "gain4": the output voltage is amplified four times.

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.current_output("3000mA")
            sg2238sp02pca.select_signal_type("DC")
            sg2238sp02pca.select_impedance("50ohm")
            sg2238sp02pca.select_voltage_gain("gain4")

        '''
        assert isinstance(gain, basestring)
        assert gain in SG2238SP02PCADef.AMPLIFICATION_LIST

        self._io_set(gain)
        return "Done"

    def current_output(self, current_range):
        '''
        Set the output current

        Args:
            current_range:     string, ["disable", "1500mA", "3000mA", "4500mA", "6000mA"],
                                        "disable": disable u13,u16,u15,u12; current is 0mA
                                        "1500mA": enable u13; current is 1500mA
                                        "3000mA": enable u13,u16;  current is 3000mA
                                        "4500mA": enable u13,u16,u15; current is 4500mA
                                        "6000mA": enable u13,u16,u15,u12; current is 6000mA

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.current_output('3000mA')

        '''
        assert isinstance(current_range, basestring)
        assert current_range in SG2238SP02PCADef.CURRENT_RANGE

        self._io_set(current_range)
        return "Done"

    def select_signal_type(self, signal_type='DC'):
        '''
        Select the input signal type

        Args:
            signal_type:     string, ["DC", "AC"], Input signal type.

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.select_signal_type('DC')

        '''
        assert isinstance(signal_type, basestring)
        assert signal_type in SG2238SP02PCADef.SIGNAL_TYPE

        self._io_set(signal_type)
        return "Done"

    def select_impedance(self, impedance='50ohm'):
        '''
        Select power amplifier board impedance

        Args:
            impedance:      string, ["1Mohm", "50ohm"], 1Mohm: High impedance state,
                                                        50ohm: Low impedance state.

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.select_impedance('50ohm')

        '''
        assert isinstance(impedance, basestring)
        assert impedance in SG2238SP02PCADef.IMPEDANCES

        self._io_set(impedance)
        return "Done"

    def set_offset(self, channel, offset):
        '''
        Set output signal offset

        Args:
            channel:     string, ['channel1', 'channel2', 'all'), 'all' mean both channel.
            offset:      float, [-8000~8000], unit mV, output voltage offset.

        Returns:
            string, "done", api execution successful.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.set_offset(channel1, 8000)

        '''
        assert isinstance(channel, basestring)
        assert isinstance(offset, (int, float))
        assert channel in SG2238SP02PCADef.DAC_CHANNEL.keys()
        assert offset >= SG2238SP02PCADef.DAC_MIN_VOLTAGE
        assert offset <= SG2238SP02PCADef.DAC_MAX_VOLTAGE

        """Op-amp formula: offset_voltage = (dac_voltage+11388.9)/9.2"""
        volt = (offset + SG2238SP02PCADef.DAC_OFFSET) / SG2238SP02PCADef.DAC_MAGNIFICATION_TIMES
        self._ad5667.output_volt_dc(SG2238SP02PCADef.DAC_CHANNEL[channel], volt)

        return "Done"

    def calibration_pipe(self, cal_item, raw_data):
        '''
        Get the calibrated results.This function is for external calibration call.

        Args:
            cal_item:    string, ["128kHz", "256KHz", "384KHz"], calibration unit index.
            raw_data:    float, data to be calibrated.

        Returns:
            list.

        Examples:
            sg2238sp02pca = SG2238SP02PCA(i2c)
            sg2238sp02pca.calibration_pipe('128KHz', 1000)

        '''
        return self.cal_pipe(sg2238sp02pca_cal_info[cal_item], raw_data)
