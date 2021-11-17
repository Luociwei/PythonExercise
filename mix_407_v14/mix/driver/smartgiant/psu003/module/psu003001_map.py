# -*- coding: utf-8 -*-
import bisect
import time
import math
import re

from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ic.ad5675 import AD5675


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = 'V0.0.3'

psu003001_range_table = {
    "POWER_VOLT_SET": 0,
    "POWER_CURR_SET_1A": 1,
    "POWER_CURR_SET_10A": 2,
    "POWER_VOLT_READ": 3,
    "POWER_CURR_READ_1A": 4,
    "POWER_CURR_READ_10A": 5,

}


class Psu003001Def:
    DAC_DEV_ADDR = 0x0C
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    IO_EXP_DEV_ADDR = 0x70

    RELAY_DELAY_MS = 50
    TIME_OUT = 6  # S
    DCDC_RAISE_DELAY_MS = 10
    DCDC_FALL_DELAY_MS = 5
    VI_DELAY_MS = 50

    DAC_REF_VOLT_mV = 2500
    DAC_MAX_OVERCURR_VOLT_mV = 4175

    SOURCE_TYPE = ["CVS", "CCS"]
    SWITCH_SELECT = ["on", "off"]
    SWITCH_ON = "on"
    SWITCH_OFF = "off"

    READBACK_STATE_MASK = 0x3 << 6
    READBACK_STATE = {0x00: "ERROR", 0x80: "SRC_CC", 0x40: "SINK_CC", 0xc0: "CV"}

    V_DCDC_CHAN = 0
    V_OUTPUT_CHAN = 1
    I_OUTPUT_CHAN = 2

    CURR_RANGE_SW_BIT = 0
    OUTPUT_EN_BIT = 1
    DCDC_EN_BIT = 2
    DIS_EN_BIT = 3
    AD5675R_RESET_L_BIT = 4
    AD5675R_LDAC_L_BIT = 5
    SRC_CC_L_BIT = 6
    SINK_CC_L_BIT = 7


# range defines
psu003001_line_info = {
    'curr_range_sw': {
        "10A": {
            "bits": [(Psu003001Def.CURR_RANGE_SW_BIT, 1)]
        },
        "1A": {
            "bits": [(Psu003001Def.CURR_RANGE_SW_BIT, 0)]
        }
    },
    'output_enable': {
        "on": {
            "bits": [(Psu003001Def.OUTPUT_EN_BIT, 1)],
        },
        "off": {
            "bits": [(Psu003001Def.OUTPUT_EN_BIT, 0)]
        }
    },
    'dcdc_enable': {
        "run": {
            "bits": [(Psu003001Def.DCDC_EN_BIT, 1)],
        },
        "shutdown": {
            "bits": [(Psu003001Def.DCDC_EN_BIT, 0)]
        }
    },
    'discharge_enable': {
        "enable": {
            "bits": [(Psu003001Def.DIS_EN_BIT, 1)]
        },
        "disable": {
            "bits": [(Psu003001Def.DIS_EN_BIT, 0)]
        }
    },
    'dac_load': {
        "high": {
            "bits": [(Psu003001Def.AD5675R_RESET_L_BIT, 1)]
        },
        "low": {
            "bits": [(Psu003001Def.AD5675R_RESET_L_BIT, 0)]
        }
    },
    'dac_reset': {
        "high": {
            "bits": [(Psu003001Def.AD5675R_RESET_L_BIT, 1)]
        },
        "low": {
            "bits": [(Psu003001Def.AD5675R_RESET_L_BIT, 0)]
        }
    }
}


formula = {
    # the formula Provided by hardware engineer
    # Vdcdc= 1.6129* Vdac+0.1797
    "Vdcdc2Vadc": lambda vdcdc: ((vdcdc - 179.7) / 1.6129),
    # Voutput= 1.1222*Vdac-0.0556
    "Vout2Vadc": lambda vout: ((vout + 55.6) / 1.1222),
    # Iout=0.2398*Vdac-0.0012
    "I1A2Vdac": lambda curr: ((curr + 1.2) / 0.2398),
    # Iout=2.3976*Vdac-0.01198
    "I10A2Vdac": lambda curr: ((curr + 11.98) / 2.3976),
    # Iout=0.2398*Vdac+0.0012
    "-I1A2Vdac": lambda curr: ((curr - 1.2) / 0.2398),
    # Iout=2.3976*Vdac+0.01198
    "-I10A2Vdac": lambda curr: ((curr - 11.98) / 2.3976),
    # Vvolt_meas= -0.9*Vout
    "Vadc2Vout": lambda vadc: (vadc / -0.9),
    # Vcurr_meas= -4.175*Iout
    "Vadc2I1A": lambda vadc: (vadc / -4.175),
    # Vcurr_meas= -0.4175*Iout
    "Vadc2I10A": lambda vadc: (vadc / -0.4175),
}


class Psu003001Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PSU003001(SGModuleDriver):
    '''
    PSU003001(PSU-003-001) is a power module with single channel and two quadrants,

    which is used for output voltage/current, the range of voltage is 0~5V,
    the range of current is -10~10A.

    Args:
        i2c:      instance(I2C), is used to create DAC, EEPROM, temperature sensor and IO expender.

    Examples:
        i2c_bus = I2C('/dev/i2c-1')
        psu003001 = PSU003001(i2c_bus)

        # PSU003001 output 2000mV with CVS mode
        psu003001.reset()
        psu003001.set_power_type('CVS')
        psu003001.power_output('1A', 2000, 1000)

    '''
    compatible = ["GQQ-PU03-5-020"]
    rpc_public_api = ['power_output', 'set_power_type', 'get_power_type', 'power_readback_voltage_calc',
                      'power_readback_current_calc', 'discharge_control', 'get_power_state',
                      'get_discharge_state', 'set_dac_voltage', 'set_voltage_difference',
                      'set_line_path', 'output_enable', 'power_output_debug'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c):

        if i2c:
            self.nct75 = NCT75(Psu003001Def.SENSOR_DEV_ADDR, i2c)
            self.dac = AD5675(Psu003001Def.DAC_DEV_ADDR, i2c, mvref=Psu003001Def.DAC_REF_VOLT_mV)
            self.eeprom = CAT24C32(Psu003001Def.EEPROM_DEV_ADDR, i2c)
            self.io_exp = TCA9538(Psu003001Def.IO_EXP_DEV_ADDR, i2c)
            super(PSU003001, self).__init__(self.eeprom, self.nct75,
                                            range_table=psu003001_range_table)
            self.line_path = dict()

        else:
            raise Psu003001Exception("Parameter error")

    def post_power_on_init(self, timeout=Psu003001Def.TIME_OUT):
        '''
        Init psu003001 module to a know harware state.

        This function will set tca9538 io direction to output and set DAC.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=Psu003001Def.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''

        start_time = time.time()
        while True:
            try:
                self.line_path.clear()
                self.source_type = "CVS"
                self.volt_diff = 2000

                self.dac.set_gain(2)
                [self.dac.set_mode(x, "normal") for x in xrange(3)]
                [self.dac.output_volt_dc(x, 0) for x in xrange(3)]

                self.set_line_path("dac_reset", "high")
                self.set_line_path("dac_load", "high")

                self.set_line_path("output_enable", "off")
                self.set_line_path("dcdc_enable", "shutdown")
                self.set_line_path("discharge_enable", "disable")
                self.set_line_path("curr_range_sw", "1A")
                self.io_exp.set_pins_dir([0xC0])

                self.output_state = "off"
                self.curr = None
                self.volt = None

                self.load_calibration()
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Psu003001Exception("Timeout: {}".format(e.message))

    def set_voltage_difference(self, volt):
        '''
        Set the voltage difference from Vdcdc to Vout, this is a debug function.

        Args:
            volt:    int/float, unit mV.

        Returns:
            string, "done", api execution successful.

        '''
        assert isinstance(volt, (int, float))
        self.volt_diff = volt
        return "done"

    def power_output_debug(self, curr_range, volt, curr):
        '''
        Set power output, this is a debug function.

        Args:
            curr_range:    string, ["10A", "1A"], the current range.
            volt:    int/float, unit mV.
            curr:    int/float, unit mA.

        Returns:
            string, "done", api execution successful.

        '''
        self.set_line_path("dcdc_enable", "run")
        self.set_line_path("output_enable", "on", Psu003001Def.RELAY_DELAY_MS)

        cal_volt = self.calibrate("POWER_VOLT_SET", volt)
        cal_curr = self.calibrate("POWER_CURR_SET_" + curr_range, curr)

        # the voltage of overcurrent protection set to max, for prevending spurious triggering from relay shaking.
        self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, Psu003001Def.DAC_MAX_OVERCURR_VOLT_mV)
        time.sleep(Psu003001Def.VI_DELAY_MS / 1000.0)
        self.set_line_path("curr_range_sw", curr_range, Psu003001Def.RELAY_DELAY_MS)

        if self.output_state == "off" or self.volt is None or self.volt < volt:
            self.dac.output_volt_dc(Psu003001Def.V_DCDC_CHAN, formula["Vdcdc2Vadc"](volt + self.volt_diff))
            time.sleep(Psu003001Def.DCDC_RAISE_DELAY_MS / 1000.0)

        if self.source_type == "CVS":
            if curr >= 0:
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, formula["I" + curr_range + "2Vdac"](cal_curr))
            else:
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, formula["-I" + curr_range + "2Vdac"](abs(cal_curr)))
            time.sleep(Psu003001Def.VI_DELAY_MS / 1000.0)
            self.dac.output_volt_dc(Psu003001Def.V_OUTPUT_CHAN, formula["Vout2Vadc"](cal_volt))
        else:
            self.dac.output_volt_dc(Psu003001Def.V_OUTPUT_CHAN, formula["Vout2Vadc"](cal_volt))
            time.sleep(Psu003001Def.VI_DELAY_MS / 1000.0)
            if curr >= 0:
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, formula["I" + curr_range + "2Vdac"](cal_curr))
            else:
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, formula["-I" + curr_range + "2Vdac"](abs(cal_curr)))
        if self.output_state == "on" and self.volt > volt:
            time.sleep(Psu003001Def.DCDC_FALL_DELAY_MS / 1000.0)
            self.dac.output_volt_dc(Psu003001Def.V_DCDC_CHAN, formula["Vdcdc2Vadc"](volt + self.volt_diff))

        self.curr = curr
        self.volt = volt
        self.output_state = "on"
        return "done"

    def power_output(self, curr_range, volt, curr):
        '''
        Set power output.

        Args:
            curr_range:    string, ["10A", "1A"], the current range.
            volt:    int/float, [0~5000], unit mV.
            curr:    int/float, unit mA.

        Returns:
            string, "done", api execution successful.

        '''
        assert curr_range in psu003001_line_info["curr_range_sw"]
        assert isinstance(volt, (int, float))
        assert isinstance(curr, (int, float))
        assert 0 <= volt <= 5000
        assert 0 <= abs(curr) <= int(curr_range[:-1]) * 1000

        self.power_output_debug(curr_range, volt, curr)

        return "done"

    def output_enable(self, state):
        '''
        Set power output.

        Args:
            state:   string, ["on", "off"], output the switch.

        Returns:
            string, "done", api execution successful.

        '''
        assert state in Psu003001Def.SWITCH_SELECT
        if state == Psu003001Def.SWITCH_ON:
            self.curr = self.curr if self.curr else 0
            self.volt = self.volt if self.volt else 0
            self.power_output_debug(self.line_path["curr_range_sw"], self.volt, self.curr)
        else:
            if self.source_type == "CVS":
                self.dac.output_volt_dc(Psu003001Def.V_OUTPUT_CHAN, 0)
                time.sleep(Psu003001Def.VI_DELAY_MS / 1000.0)
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, 0)
                time.sleep(Psu003001Def.DCDC_FALL_DELAY_MS / 1000.0)
                self.dac.output_volt_dc(Psu003001Def.V_DCDC_CHAN, 0)
            else:
                self.dac.output_volt_dc(Psu003001Def.I_OUTPUT_CHAN, 0)
                time.sleep(Psu003001Def.VI_DELAY_MS / 1000.0)
                self.dac.output_volt_dc(Psu003001Def.V_OUTPUT_CHAN, 0)
                time.sleep(Psu003001Def.DCDC_FALL_DELAY_MS / 1000.0)
                self.dac.output_volt_dc(Psu003001Def.V_DCDC_CHAN, 0)

            self.set_line_path("output_enable", "off")
            self.set_line_path("dcdc_enable", "shutdown")
            self.output_state = "off"
        return "done"

    def set_power_type(self, source_type):
        '''
        Set power type.

        Args:
            source_type: string, ["CVS", "CCS"], CVS means constant voltage source, CCS means constant current source.

        Returns:
            string, "done", api execution successful.

        '''
        assert source_type in Psu003001Def.SOURCE_TYPE
        self.source_type = source_type
        return "done"

    def get_power_type(self):
        '''
        Get power type.

        Returns:
            string, ["CVS", "CCS"].

        '''
        return self.source_type

    def power_readback_voltage_calc(self, volt):
        '''
        Calculate and calibrate read back power voltage.

        Args:
            volt:    float, ADC read back voltage, unit mV.

        Returns:
            float, unit mV, voltage value.

        Examples:
            volt = psu003001.power_readback_voltage_calc(1000)

        '''
        assert isinstance(volt, (int, float))
        volt = formula["Vadc2Vout"](volt)
        return self.calibrate("POWER_VOLT_READ", volt)

    def power_readback_current_calc(self, volt):
        '''
        Calculate and calibrate power current.

        Args:
            volt:    float, ADC read back voltage, unit mV.

        Returns:
            float, unit mA, current value.

        Examples:
            current = psu003001.power_readback_voltage_calc(100)

        '''
        assert isinstance(volt, (int, float))
        curr_range = self.line_path["curr_range_sw"]
        curr = formula["Vadc2I" + curr_range](volt)
        return self.calibrate("POWER_CURR_READ_" + curr_range, curr)

    def discharge_control(self, state):
        '''
        Control power discharge.

        Args:
            state:  string, ["enable", "disable"], state enable control.

        Returns:
            string, "done", execution successful.

        '''
        assert state in psu003001_line_info["discharge_enable"]
        self.set_line_path("discharge_enable", state)
        return "done"

    def get_discharge_state(self):
        '''
        control discharge.

        Returns:
            string, ["enable", "disable"].

        '''
        return self.line_path["discharge_enable"]

    def get_power_state(self):
        '''
        Get power state.

        Returns:
            string, ["ERROR","SRC_CC","SINK_CC","CV"].

        '''
        io_state = self.io_exp.get_ports()[0]
        curr_select = io_state & Psu003001Def.READBACK_STATE_MASK
        return Psu003001Def.READBACK_STATE[curr_select]

    def set_dac_voltage(self, channel, volt):
        '''
        Set dac voltage, this is a debug function.

        Args:
            channel:  int, [0-7].
            volt:     float/int, unit mV.

        Returns:
            string, "done", api execution successful.

        '''
        assert channel in xrange(7)
        assert isinstance(volt, (int, float))
        assert volt >= 0
        self.dac.output_volt_dc(channel, volt)
        return 'done'

    def _set_io(self, io_list):
        '''
        Psu003001 set io, this is a private function.

        Args:
            io_list:     list, [(bit, state),].

        Returns:
            string, "done", api execution successful.

        '''

        rd_data = self.io_exp.get_ports()
        cp_state = rd_data[0]

        for bit in io_list:
            cp_state &= ~(1 << (bit[0] & 0xf))
            if bit[1] == 1:
                cp_state |= (1 << (bit[0] & 0xf))
        self.io_exp.set_ports([cp_state & 0xFF, ])

        return 'done'

    def set_line_path(self, config, scope, delay_time_ms=0):
        '''
        psu003001 set line path, this is a private function.

        Args:
            config:        string, ["dcdc_enable", "output_enable", "discharge_enable",
                           "dac_reset", "curr_range_sw", "dac_load"].
            scope:         string, ["run", "shutdown", "on", "off", "enable", "disable",
                           "high", "low", "1A", "10A", "high", "low"], the scope is rely on config, eg:
                           dcdc_enable:["run", "shutdown"], output_enable:["on", "off"],
                           discharge_enable:["enable", "disable"], dac_reset:["high", "low"],
                           curr_range_sw:["1A", "10A"], dac_load:["high", "low"].
            delay_time_ms: float/int, unit ms, default 0,  delay time of excitation output.

        Returns:
            string, "done", api execution successful.

        Examples:
            psu003001.set_line_path('dcdc_enable', 'run')

        '''
        assert config in psu003001_line_info
        assert scope in psu003001_line_info[config]

        if config not in self.line_path or self.line_path[config] != scope:
            self._set_io(psu003001_line_info[config][scope]["bits"])
            time.sleep(delay_time_ms / 1000.0)

            self.line_path[config] = scope

        return 'done'

    def get_driver_version(self):
        '''
        Get psu003001 driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
