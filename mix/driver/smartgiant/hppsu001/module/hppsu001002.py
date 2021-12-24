# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.core.ic.tca9538_emulator import TCA9538Emulator
from mix.driver.smartgiant.common.ic.ad56x7_emulator import AD5667Emulator
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator


__author__ = 'xuboyan@SmartGiant'
__version__ = '0.1'


hppsu001002_calibration_info = {
    "VOLTAGE_OUTPUT": {
        "level1": {"unit_index": 0},
        "level2": {"unit_index": 1},
        "level3": {"unit_index": 2},
        "level4": {"unit_index": 3}
    },
    "VOLTAGE_MEASURE": {
        "level1": {"unit_index": 4},
        "level2": {"unit_index": 5},
        "level3": {"unit_index": 6},
        "level4": {"unit_index": 7}
    },
    "CURRENT_MEASURE": {
        "level1": {"unit_index": 8},
        "level2": {"unit_index": 9},
        "level3": {"unit_index": 10},
        "level4": {"unit_index": 11},
        "level5": {"unit_index": 12},
        "level6": {"unit_index": 13},
        "level7": {"unit_index": 14},
        "level8": {"unit_index": 15},
        "level9": {"unit_index": 16},
        "level10": {"unit_index": 17},
        "level11": {"unit_index": 18},
        "level12": {"unit_index": 19}
    },
    "OCP": {
        "level1": {"unit_index": 20},
        "level2": {"unit_index": 21},
        "level3": {"unit_index": 22},
        "level4": {"unit_index": 23},
        "level5": {"unit_index": 24},
        "level6": {"unit_index": 25},
        "level7": {"unit_index": 26},
        "level8": {"unit_index": 27},
        "level9": {"unit_index": 28},
        "level10": {"unit_index": 29},
        "level11": {"unit_index": 30},
        "level12": {"unit_index": 31}
    },
    "OVP": {
        "level1": {"unit_index": 32},
        "level2": {"unit_index": 33},
        "level3": {"unit_index": 34},
        "level4": {"unit_index": 35}
    }
}

hppsu001002_range_table = {
    "VOLTAGE_OUTPUT": 0,
    "VOLTAGE_MEASURE": 1,
    "CURRENT_MEASURE": 2,
    "OCP": 3,
    "OVP": 4
}


class HPPSU001Def:
    TCA9538_DEV_ADDR = 0x73
    AD5667_DEV_1_ADDR = 0x0f
    AD5667_DEV_2_ADDR = 0x0c
    EEPROM_DEV_ADDR = 0x50
    NCT75_DEV_ADDR = 0x48

    AD5667_MVREF = 5000
    AD7175_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535
    AD7175_MVREF = 5000.0  # mv
    AD7175_CODE_POLAR = "bipolar"
    AD7175_BUFFER_FLAG = "enable"
    AD7175_REFERENCE_SOURCE = "extern"
    AD7175_CLOCK = "crystal"

    # default sampling rate is 5 Hz which is defined in Driver ERS
    DEFAULT_SAMPLE_RATE = 5

    tca9538_pins_dir_init = [0x78]
    tca9538_pins_init = [0x05]

    ad5667_ocp_init = 10000
    ad5667_ovp_init = 31500
    ad5667_output_0V = 0

    temp_alert = 100
    temp_hysteresis = 80

    ratio_less_than_10V = 1.1
    ratio_less_than_30V = 1.05

    VOLTAGE_OFFSET = 50
    ADC_CURRENT_ATTENUATION = 46
    ADC_CURRENT_GAIN = 0.01
    ADC_VOLTAGE_GAIN = 6.556
    ADC_VIN_ATTENUATION = 0.115
    ADC_NEAR_ATTENUATION = 0.138

    DAC_OUTPUT_VOLTAGE_GAIN = 6.556
    DAC_OCP_ATTENUATION = 46 * 0.01
    DAC_OVP_ATTENUATION = 0.1525

    calculation_formula = {
        # CURRENT_MEASURE: current =(Vadc-50)/46/0.01, unit = mV
        "CURRENT_MEASURE": lambda value: ((value - HPPSU001Def.VOLTAGE_OFFSET) / HPPSU001Def.ADC_CURRENT_ATTENUATION \
                                          / HPPSU001Def.ADC_CURRENT_GAIN),
        # VOLTAGE_MEASURE: voltage = Vadc * 6.556 - 50, unit = mV
        "VOLTAGE_MEASURE": lambda value: (value * HPPSU001Def.ADC_VOLTAGE_GAIN - HPPSU001Def.VOLTAGE_OFFSET),
        # VIN_MEASURE: vin = Vadc / 0.115, unit = mV
        "VIN_MEASURE": lambda value: (value / HPPSU001Def.ADC_VIN_ATTENUATION),
        # NEAR_MEASURE: near = Vadc / 0.138, unit = mV
        "NEAR_MEASURE": lambda value: (value / HPPSU001Def.ADC_NEAR_ATTENUATION),
        # VOLTAGE_OUTPUT: Vdac = (Vout + 50) / 6.556, unit = mV
        "VOLTAGE_OUTPUT": lambda value: ((value + HPPSU001Def.VOLTAGE_OFFSET) / HPPSU001Def.DAC_OUTPUT_VOLTAGE_GAIN),
        # OCP: Vdac = Iocp * 0.01 * 46 + 50, unit = mA
        "OCP": lambda value: (value * HPPSU001Def.DAC_OCP_ATTENUATION + HPPSU001Def.VOLTAGE_OFFSET),
        # OVP: Vdac = (Vovp - 50) * 0.1525, unit = mV
        "OVP": lambda value: ((value - HPPSU001Def.VOLTAGE_OFFSET) * HPPSU001Def.DAC_OVP_ATTENUATION)
    }

    FUNCTION_INFO = {
        "io_function_info": {
            "ctrl": {
                "power_ctrl": {
                    "mode": {"on": 0, "off": 1},
                    "pin_id": 0
                },
                "discharge_ctrl": {
                    "mode": {"on": 1, "off": 0},
                    "pin_id": 1
                },
                "protect_reset": {
                    "mode": {"on": 1, "off": 0},
                    "pin_id": 2
                }
            },
            "read_fault_state": {
                "pins_id": [3, 4, 5, 6]
            }
        },
        "io_function_ctrl_mode": ["on", "off"],
        "ovp_to_output_ratio": {
            "ratio_range": ["10V", "30V"],
            "value": lambda value: 0 <= value <= 2
        },
        "adc": {
            "CURRENT_MEASURE": {"channel": 0},
            "VOLTAGE_MEASURE": {"channel": 1},
            "VIN_MEASURE": {"channel": 2},
            "NEAR_MEASURE": {"channel": 3}
        },
        "dac": {
            "VOLTAGE_OUTPUT": {
                "range": lambda value: 0 <= value <= 30000,
                "device": "self.ad5667_1",
                "channel": 0
            },
            "OCP": {
                "range": lambda value: 0 <= value <= 10000,
                "device": "self.ad5667_2",
                "channel": 0
            },
            "OVP": {
                "range": lambda value: 0 <= value <= 31500,
                "device": "self.ad5667_2",
                "channel": 1
            }
        },
        "power_output_voltage": {
            "normal": lambda output: 4000 <= output <= 30000,
            "debug": lambda output: 0 <= output <= 30000
        },
        "power_ouput_mode": {
            "debug": "31500",
            "normal": "output * self.ovp_to_output_ratio[self.ratio_range]"
        },
        "adc_register": {
            "register": lambda register: 0x00 <= register <= 0x3f,
            "value": lambda value: 0x00 <= value <= 0xffffffff,
            "sampling_rate": lambda sampling_rate: 5 <= sampling_rate <= 250000,
        }
    }


class HPPSU001Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class HPPSU001001Base(MIXBoard):
    '''
    Base class of HPPSU001001 and HPPSU001001Compatible.

    Providing common HPPSU001001 methods.

    Args:
        i2c:                    instance(I2C)/None,         which is used to control nct75 and cat24c32. If not given,
                                                        emulator will be created.
        ad7175:                 instance(ADC)/None,         Class instance of AD7175, if not using this parameter,
                                                        will create emulator.
        fault_pin:              instance(GPIO),             This can be Pin or xilinx gpio, used to read module status.
        ipcore:                 instance(MIXDAQT1SGR)/string, MIXDAQT1SGR ipcore driver instance or device name string,
                                                        if given, user should not use ad7175.
        cal_info:               dictionary,                 Module calibration information.
        range_table:            dictionary,                 Module calibration gear.

    Raise:
        HPPSU001Exception:  Not allowed to use both aggregated IP and AD717X.

    '''

    rpc_public_api = ['module_init', 'io_function_ctrl', 'read_fault_state', 'get_fault_pin_level',
                      'ovp_to_output_ratio_set', 'ovp_to_output_ratio_get', 'set_output_value', 'power_output_voltage',
                      'adc_register_read', 'adc_register_write', 'set_sampling_rate', 'get_sampling_rate',
                      'measure'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, ad7175=None, fault_pin=None, ipcore=None, cal_info=None, range_table=None):

        if ipcore and ad7175:
            raise HPPSU001Exception("Not allowed to use both aggregated IP and AD717X")

        if i2c:
            self.tca9538 = TCA9538(HPPSU001Def.TCA9538_DEV_ADDR, i2c)
            self.ad5667_1 = AD5667(HPPSU001Def.AD5667_DEV_1_ADDR, i2c, HPPSU001Def.AD5667_MVREF)
            self.ad5667_2 = AD5667(HPPSU001Def.AD5667_DEV_2_ADDR, i2c, HPPSU001Def.AD5667_MVREF)
            self.eeprom = CAT24C32(HPPSU001Def.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(HPPSU001Def.NCT75_DEV_ADDR, i2c)
        else:
            self.tca9538 = TCA9538Emulator(HPPSU001Def.TCA9538_DEV_ADDR)
            self.ad5667_1 = AD5667Emulator("ad5667_emulator_1")
            self.ad5667_2 = AD5667Emulator("ad5667_emulator_2")
            self.eeprom = EepromEmulator("eeprom_emulator")
            self.sensor = NCT75Emulator("nct75_emulator")

        if fault_pin:
            self.fault_pin = fault_pin
        else:
            self.fault_pin = GPIOEmulator('gpio_emulator')

        if ipcore:
            self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
        elif ad7175:
            self.ad7175 = ad7175
        else:
            raise HPPSU001Exception("Use one of aggregated IP or AD717X")

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN4"},
            "ch1": {"P": "AIN1", "N": "AIN4"},
            "ch2": {"P": "AIN2", "N": "AIN4"},
            "ch3": {"P": "AIN3", "N": "AIN4"}
        }

        super(HPPSU001001Base, self).__init__(self.eeprom, self.sensor, cal_table=cal_info,
                                              range_table=range_table)

    def module_init(self):
        '''
        HPPSU001001 module init.

        This function will set bit1, bit2, bit3, bit8 io direction of tca9538 as output
        and set to high level, low level, high level and low level respectively.
        The io direction of the remaining bits of tca9538 is input.
        Set OCP value to 10A, OVP value to 31.5V, output voltage to 0V.
        Init ad7175 chip: samplerate, work mode.
        Configure nct75 to one-shot mode.

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.module_init()

        '''
        self.load_calibration()
        # TCA9538 chip initial
        self.tca9538.set_pins_dir(HPPSU001Def.tca9538_pins_dir_init)
        self.tca9538.set_ports(HPPSU001Def.tca9538_pins_init)
        # DAC chip initial, ocp: 10A, ovp: 31.5V
        self.ad5667_1.reset("ALL_REG")
        self.ad5667_1.select_work_mode(2, "NORMAL")
        self.ad5667_2.reset("ALL_REG")
        self.ad5667_2.select_work_mode(2, "NORMAL")
        self.set_output_value("OCP", HPPSU001Def.ad5667_ocp_init)
        self.set_output_value("OVP", HPPSU001Def.ad5667_ovp_init)
        # ADC chip initial
        self.ad7175.is_communication_ok()
        self.ad7175.channel_init()
        for channel in [0, 1, 2, 3]:
            self.ad7175.set_sampling_rate(channel, HPPSU001Def.DEFAULT_SAMPLE_RATE)
            self.ad7175.read_volt(channel)
            self.ad7175.set_channel_state(channel, "disable")
        # NCT75 chip initial, Tos set 100C, Thyst set 80C
        self._temperature_device.config_overtemperature(HPPSU001Def.temp_alert, HPPSU001Def.temp_hysteresis)

        self.ocp_set_flag = 0
        self.ovp_set_flag = 0
        self.last_output_voltage_record = 0
        self.ovp_to_output_ratio = {
            "10V": HPPSU001Def.ratio_less_than_10V,
            "30V": HPPSU001Def.ratio_less_than_30V
        }
        self.ratio_range = "30V"
        return "done"

    def io_function_ctrl(self, function, mode):
        '''
        Assign different functions to different io pins

        Args:
            function:       string, ["power_ctrl", "discharge_ctrl", "protect_reset"], io function select.
            mode:           string, ["on", "off"], the mode to set work state.

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.io_function_ctrl("power_ctrl", "on")

        '''
        assert function in HPPSU001Def.FUNCTION_INFO["io_function_info"]["ctrl"]
        assert mode in HPPSU001Def.FUNCTION_INFO["io_function_ctrl_mode"]

        pin_id = HPPSU001Def.FUNCTION_INFO["io_function_info"]["ctrl"][function]["pin_id"]
        pin_status = HPPSU001Def.FUNCTION_INFO["io_function_info"]["ctrl"][function]["mode"][mode]

        if function in ["power_ctrl", "discharge_ctrl"]:
            self.tca9538.set_pin(pin_id, pin_status)
            if function == "power_ctrl":
                time.sleep(0.03)
                if mode == "off":
                    self.set_output_value("VOLTAGE_OUTPUT", HPPSU001Def.ad5667_output_0V)
        elif function == "protect_reset":
            if pin_status:
                self.tca9538.set_pin(pin_id, 1)
                self.tca9538.set_pin(pin_id, 0)
                time.sleep(0.001)
                self.tca9538.set_pin(pin_id, 1)

        return "done"

    def read_fault_state(self):
        '''
        Read fault state

        Returns:
            string, ["No problem", "OCP", "OVP", "RSFP", "OTP", "OCP, OTP", "OVP, OTP", "RSFP, OTP"],
                    get the fault state.

        Examples:
            result = hppsu001001.read_fault_state()
            print(result)

        '''
        ret = ""
        result = self.tca9538.get_ports()[0]
        pins = HPPSU001Def.FUNCTION_INFO["io_function_info"]["read_fault_state"]["pins_id"]
        for index in range(pins[0], pins[3]):
            if ((1 << index) & result):
                if int(pins[0]) == index:
                    ret = "OCP,"
                elif int(pins[1]) == index:
                    ret = "OVP,"
                elif int(pins[2]) == index:
                    ret = "RSFP,"

        if ((1 << (int(pins[3]) - 1)) & result):
            ret += "OTP,"

        if "" == ret:
            ret = "No problem,"
        ret = ret[:-1]
        return ret

    def get_fault_pin_level(self):
        '''
        Get fault pin level

        Returns:
            int, [0, 1], 0 for nomal state, 1 for fault state.

        Examples:
            result = hppsu001001.get_fault_pin_level()
            print(result)

        '''
        return self.fault_pin.get_level()

    def ovp_to_output_ratio_set(self, ratio_range, value):
        '''
        Set ratio of ovp set value to output set value

        Args:
            ratio_range:    string, ["10V", "30V"], "10V" is [0~10]V, "30V" is [10~30]V
            value:          float, [0~2]

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.ovp_to_output_ratio_set("30V", 1.05)

        '''
        assert ratio_range in HPPSU001Def.FUNCTION_INFO["ovp_to_output_ratio"]["ratio_range"]
        assert HPPSU001Def.FUNCTION_INFO["ovp_to_output_ratio"]["value"](value)
        self.ovp_to_output_ratio[ratio_range] = value
        return "done"

    def ovp_to_output_ratio_get(self, ratio_range):
        '''
        Get ratio of ovp set value to output set value

        Args:
            ratio_range:    string, ["10V", "30V"], "10V" is [0~10]V, "30V" is [10~30]V

        Returns:
            float, [0~2]

        Examples:
            result = hppsu001001.ovp_to_output_ratio_get("30V")
            print(result)

        '''
        assert ratio_range in HPPSU001Def.FUNCTION_INFO["ovp_to_output_ratio"]["ratio_range"]
        return self.ovp_to_output_ratio[ratio_range]

    def set_output_value(self, channel, value):
        '''
        HPPSU001001 set the output value via the AD5667 DAC with I2C interface.

        Args:
            channel:        string, ["VOLTAGE_OUTPUT", "OCP", "OVP"], the channel to set output value.
            value:          float, [0~31500], unit mV, VOLTAGE_OUTPUT is [0~30000]mV, OCP is [0~10000]mA and
                                                       OVP is [0~31500]mV.

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.set_output_value("VOLTAGE_OUTPUT", 5000)

        '''
        assert isinstance(value, (int, float))
        assert channel in HPPSU001Def.FUNCTION_INFO["dac"]
        assert HPPSU001Def.FUNCTION_INFO["dac"][channel]["range"](value)

        value = self.calibrate(channel, value)

        vdac = HPPSU001Def.calculation_formula[channel](value)

        eval(HPPSU001Def.FUNCTION_INFO["dac"][channel]["device"]).output_volt_dc(
            HPPSU001Def.FUNCTION_INFO["dac"][channel]["channel"], vdac)

        if channel == "OCP":
            self.ocp_set_flag = 1
        elif channel == "OVP":
            self.ovp_set_flag = 1

        return "done"

    def power_output_voltage(self, output=0, mode="normal"):
        '''
        Set the power output voltage

        Args:
            output:         float, default 0, if the mode is "debug", the range is 0~30000;
                                              if mode is normal, 4000~30000.
            mode:           string, ["debug", "normal"], default "normal", the mode to set work state, in debug mode,
                                                         the overvoltage protection value is set to a maximum of 31500.

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.power_output_voltage(5000)

        '''
        assert HPPSU001Def.FUNCTION_INFO["power_output_voltage"][mode](output)
        assert mode in HPPSU001Def.FUNCTION_INFO["power_ouput_mode"]

        self.io_function_ctrl("power_ctrl", "on")

        if self.ocp_set_flag != 1:
            self.set_output_value("OCP", 10000)

        if output <= 10000:
            self.ratio_range = "10V"
        else:
            self.ratio_range = "30V"

        if mode == "normal" and output < self.last_output_voltage_record:
            self.set_output_value("VOLTAGE_OUTPUT", output)
            time.sleep(1)
            self.set_output_value("OVP", eval(HPPSU001Def.FUNCTION_INFO["power_ouput_mode"][mode]))
        elif mode == "debug" or (mode == "normal" and output >= self.last_output_voltage_record):
            self.set_output_value("OVP", eval(HPPSU001Def.FUNCTION_INFO["power_ouput_mode"][mode]))
            self.set_output_value("VOLTAGE_OUTPUT", output)

        self.io_function_ctrl("protect_reset", "on")
        self.last_output_voltage_record = output

        return "done"

    def adc_register_read(self, register):
        '''
        Read data from AD7175 adc register

        Args:
            registor:       hex, [0x00~0x3f]

        Returns:
            hex, [0x00~0xffffffff]

        Examples:
            result = hppsu001001.adc_register_read(0x00)
            print(result)

        '''
        assert HPPSU001Def.FUNCTION_INFO["adc_register"]["register"](register)
        return self.ad7175.read_register(register)

    def adc_register_write(self, register, value):
        '''
        Write data to AD7175 adc register

        Args:
            registor:       hex, [0x00~0x3f]
            value:          hex, [0x00~0xffffffff]

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.adc_register_write(0x10, 30)

        '''
        assert HPPSU001Def.FUNCTION_INFO["adc_register"]["register"](register)
        assert HPPSU001Def.FUNCTION_INFO["adc_register"]["value"](value)
        self.ad7175.write_register(register, value)
        return "done"

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        HPPSU001001 set sampling rate of adc.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad7175 datasheet.

        Args:
            channel:        string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"],
                                    the channel to change sampling rate.
            sampling_rate:  float, [5~250000], unit Hz, adc measure sampling rate, which is not continuous,
                                               please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
            hppsu001001.set_sampling_rate("VOLTAGE_MEASURE", 5)

        '''
        assert HPPSU001Def.FUNCTION_INFO["adc_register"]["sampling_rate"](sampling_rate)
        assert channel in HPPSU001Def.FUNCTION_INFO["adc"]

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(HPPSU001Def.FUNCTION_INFO["adc"][channel]["channel"],
                                          sampling_rate)

        return "done"

    def get_sampling_rate(self, channel):
        '''
        HPPSU001001 get sampling rate of adc.

        Args:
            channel:        string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"],
                                    the channel to get sampling rate.

        Returns:
            tuple, [ret, unit], unit Hz

        Examples:
            result = hppsu001001.get_sampling_rate("VOLTAGE_MEASURE")
            print(result)

        '''
        assert channel in HPPSU001Def.FUNCTION_INFO["adc"]
        return (self.ad7175.get_sampling_rate(HPPSU001Def.FUNCTION_INFO["adc"][channel]["channel"]), "Hz")

    def measure(self, channel):
        '''
        Do one time sample from adc, return the measurement result.

        Args:
            channel:        string, ["CURRENT_MEASURE", "VOLTAGE_MEASURE", "VIN_MEASURE", "NEAR_MEASURE"],
                                    the channel to measure current or voltage.

        Returns:
            tuple, [ret, unit], unit mV, the unit of CURRENT_MEASURE is mA.

        Examples:
            result = hppsu001001.measure("VOLTAGE_MEASURE")
            print(result)

        '''
        assert channel in HPPSU001Def.FUNCTION_INFO["adc"]
        value = self.ad7175.read_volt(HPPSU001Def.FUNCTION_INFO["adc"][channel]["channel"])
        ret = HPPSU001Def.calculation_formula[channel](value)

        if channel in ["CURRENT_MEASURE", "VOLTAGE_MEASURE"]:
            ret = self.calibrate(channel, ret)

        if channel == "CURRENT_MEASURE":
            return (ret, "mA")
        else:
            return (ret, "mV")


class HPPSU001002(HPPSU001001Base):
    '''
    HPPSU001002 module is used for output the voltage.

    compatible = ["GQQ-HPU001002-000"]

    HPPSU-001-002 is a single-channel high-performance programmable power module,
    16-bit DAC resolution, voltage output range: 4V ~ 30V, rated maximum output current 5A,
    maximum output power 150W; on-board 24-bit ADC to measures output voltage and current, OCP, OVP , OTP can be set.

    Args:
        i2c:        instance(I2C), If not given, emulator will be created.
        ad7175:     instance(ADC),   If not given, emulator will be created.
        fault_pin:  instance(GPIO),  This can be Pin or xilinx gpio, used to read module status.
        ipcore:     instance(MIXDAQT1SGR), If daqt1 given, then use MIXDAQT1SGR's AD7175.

    Examples:
        If the params `ipcore` is valid, then use MIXDAQT1SGR aggregated IP;
        Otherwise, if the params `ad7175`, use non-aggregated IP.

        # use MIXDAQT1SGR aggregated IP
        i2c = I2C('/dev/MIX_I2C_0')
        fault_pin = GPIO(86)
        ip_daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=False, use_gpio=False)
        hppsu001002 = HPPSU001002(i2c=i2c,
                                  ad7175=None,
                                  fault_pin,
                                  ipcore=ip_daqt1)
        # use non-aggregated IP
        ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
        i2c = I2C('/dev/MIX_I2C_1')
        fault_pin = GPIO(86)
        hppsu001002 = HPPSU001002(i2c=i2c,
                                  ad7175=ad7175,
                                  fault_pin,
                                  ipcore=None)

        # HPPSU001002 output voltage 5000 mV
        hppsu001002.power_output_voltage(5000)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-HPU001002-000"]

    def __init__(self, i2c, ad7175=None, fault_pin=None, ipcore=None):
        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, HPPSU001Def.MIX_DAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=HPPSU001Def.AD7175_MVREF,
                                     code_polar=HPPSU001Def.AD7175_CODE_POLAR,
                                     reference=HPPSU001Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=HPPSU001Def.AD7175_BUFFER_FLAG,
                                     clock=HPPSU001Def.AD7175_CLOCK,
                                     use_spi=False, use_gpio=False)
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, HPPSU001Def.AD7175_REG_SIZE)
                ad7175 = MIXAd7175SG(axi4_bus, mvref=HPPSU001Def.AD7175_MVREF,
                                     code_polar=HPPSU001Def.AD7175_CODE_POLAR,
                                     reference=HPPSU001Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=HPPSU001Def.AD7175_BUFFER_FLAG,
                                     clock=HPPSU001Def.AD7175_CLOCK)
        else:
            ad7175 = MIXAd7175SGEmulator('mix_ad7175_sg_emulator', HPPSU001Def.AD7175_MVREF)

        super(HPPSU001002, self).__init__(i2c, ad7175, fault_pin, ipcore,
                                          hppsu001002_calibration_info,
                                          hppsu001002_range_table)
