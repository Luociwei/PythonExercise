# -*- coding: utf-8 -*-
import time
import struct
from magma import Magma

__author__ = 'weiping.xuan@SmartGiant'
__version__ = '0.1'


class Wct001002AException(Exception):
    def __init__(self, err_str):
        self._err_reason = err_str

    def __str__(self):
        return self._err_reason


wct001002a_range_table = {
    'VOLTOUTPUT': 0,
    'READ_VOLTAGE': 1,
    "READ_CURRENT": 2,
    "READ_CURRENT_5V_20V": 3,
    "READ_VOLTAGE_0A_4A": 4
}


class Wct001002ADef:
    TIME_OUT = 6
    BIT_STATUS_LEN = 10
    CAP_P_CTL_L_MASK = 0x7f
    CAP_P_CTL_H_MASK = 0x07
    CAP_P_CTL_L_OFFSET = 1
    CAP_P_CTL_H_OFFSET = 4
    VOLTAGE_OUTPUT_MIN = 0
    VOLTAGE_OUTPUT_MAX = 20470
    MP8859_VOLTAGE_CHANNEL = 0
    MP8859_CURRENT_CHANNEL = 0
    VOLT_CHANNEL = 3
    CURRENT_CHANNEL = 5
    I_VRAIL_CURRENT_GAIN = 50 * 0.01
    PPVAIL_VOLTAGE_GAIN = 0.0991
    SENSER_CURRENT_GAIN = 50
    VOLT_ORIGIN = 5010
    MAXIMUM_POWER = 30000000
    CURRENT_OUTPUT_MAX = 6350
    INDUCTOR_CALIBRATION_COUNT = 6
    INDUCTOR_CALIBRATION_ADDRESS = {"Lmin": 0xAF, "Lnom": 0xB5, "Lmax": 0xbb}


class WCT001002A(Magma):
    '''
    The WCT001002A is based on Magma(WCT001001), it has set_cap_io function and it's calibration segments
    different from Magma, so it has different calibration methods.

    Args:
        i2c:              instance(I2C)/None,  If not given, I2CBus emulator will be created.
        ipcore:           instance(MIXWCT001), MIXWCT001 IP driver instance, provide signalsource, signalmeter_p
                                                 and signalmeter_n function.

    Examples:
        i2c = I2C('/dev/i2c-0')
        axi4_bus = AXI4LiteBus('dev/MIX_WCT001_001_SG_R_0', 65536)
        ipcore = MIXWCT001001SGR(axi4_bus, use_signalmeter_p=True, use_signalmeter_n=True, use_signalsource=True)
        wct001002a = WCT001002A(i2c,ipcore)
    '''
    compatible = ['GQQ-03X7-5-02A']

    rpc_public_api = ['set_cap_io'] + Magma.rpc_public_api

    def __init__(self, i2c=None, ipcore=None):
        super(WCT001002A, self).__init__(i2c, ipcore, wct001002a_range_table)

    def post_power_on_init(self, timeout=Wct001002ADef.TIME_OUT):
        '''
        Init Magma module to a know harware state.

        This function will set cat9555 io direction to output and set ADC and DAC.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=Wct001002ADef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        Returns:
            string, "done", api execution successful.
        '''
        start_time = time.time()
        while True:
            try:
                self.signalsource.close()
                self.cat9555.set_ports([0x00, 0x80])
                self.cat9555.set_pins_dir([0, 0x0A])
                self._adc_init()
                self.mp8859_init()
                self.load_calibration()
                return 'done'
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Wct001002AException("Timeout: {}".format(e.message))

    def set_cap_io(self, inductance_gears):
        '''
        set capacitance io based on the state stored in the eeprom.

        Args:
        inductance_gears:     string,["Lmin", "Lnom", "Lmax"].

        Examples:
            set_cap_io("Lmin")
        '''
        assert inductance_gears in Wct001002ADef.INDUCTOR_CALIBRATION_ADDRESS.keys()

        bit_status = self.inductor_calibration_read(inductance_gears)['bit_status']
        bit_status = '0' + bit_status.split('0b')[1]
        len_a = len(bit_status)
        data = 0
        for i in range(len_a):
            data = data | int(bit_status[i]) << (Wct001002ADef.BIT_STATUS_LEN - i)
        pins_level = self.cat9555.get_ports()
        pins_level_L = pins_level[0]
        pins_level_L &= ~(Wct001002ADef.CAP_P_CTL_L_MASK << Wct001002ADef.CAP_P_CTL_L_OFFSET)
        pins_level_L |= ((data & 0x7f) << Wct001002ADef.CAP_P_CTL_L_OFFSET)
        pins_level_H = pins_level[1]
        pins_level_H &= ~(Wct001002ADef.CAP_P_CTL_H_MASK << Wct001002ADef.CAP_P_CTL_H_OFFSET)
        pins_level_H |= (((data >> 7) & Wct001002ADef.CAP_P_CTL_H_MASK) << Wct001002ADef.CAP_P_CTL_H_OFFSET)
        self.cat9555.set_ports([pins_level_L, pins_level_H])
        return "done"

    def set_vrail_output_voltage(self, voltage):
        '''
        mp8859 output voltage, range 0 V ~ 20.47 V.

        Args:
            voltage:    int, [0~20470], unit mV.

        Examples:
            set_vrail_output_voltage(5000)

        '''
        assert isinstance(voltage, (int, float))
        assert Wct001002ADef.VOLTAGE_OUTPUT_MIN <= voltage and voltage <= Wct001002ADef.VOLTAGE_OUTPUT_MAX

        voltage = self.calibrate('VOLTOUTPUT', voltage)
        voltage_rem = voltage % 10
        if voltage_rem != 0:
            voltage = round(voltage, -1)
        if voltage > Wct001002ADef.VOLTAGE_OUTPUT_MAX:
            voltage = Wct001002ADef.VOLTAGE_OUTPUT_MAX
        self.mp8859.output_volt_dc(Wct001002ADef.MP8859_VOLTAGE_CHANNEL, voltage)
        current = Wct001002ADef.MAXIMUM_POWER / voltage
        if current > Wct001002ADef.CURRENT_OUTPUT_MAX:
            current = Wct001002ADef.CURRENT_OUTPUT_MAX
        self.mp8859.output_current_dc(Wct001002ADef.MP8859_CURRENT_CHANNEL, current)
        return "done"

    def read_vrail_voltage(self, mode='ppvrail'):
        '''
        read voltage function.

        Args:
            mode:   string, ['ppvrail','adc'],'ppvrail':read the vlotage from ppvrail.
                                              'adc':read the vlotage from ads1119.

        Returns:
            float, voltage, unit is mV.

        Examples:
            voltage = read_vrail_voltage('ppvrail')
        '''
        assert mode in ['ppvrail', 'adc']

        voltage = self.ads1119.read_volt(Wct001002ADef.VOLT_CHANNEL)
        if mode == 'ppvrail':
            voltage = float(voltage / Wct001002ADef.PPVAIL_VOLTAGE_GAIN)
        if self.is_use_cal_data():
            voltage = self.calibrate('READ_VOLTAGE', voltage)
            self.set_calibration_mode('raw')
            current = self.read_vrail_current("i_vrail")
            self.set_calibration_mode('cal')
            volt_offset = self.calibrate('READ_VOLTAGE_0A_4A', current)
            voltage = voltage + volt_offset
        return voltage

    def read_vrail_current(self, mode='senseR'):
        '''
        read current function.

        Args:
            mode:   string, ['senseR','adc','i_vrail'].'senseR':read the vlotage from senseR.
                                             'adc':read the vlotage from ads1119.

        Returns:
            float, current, unit is mA.

        Examples:
            current = read_vrail_current('ppvrail')
        '''
        assert mode in ['senseR', 'adc', 'i_vrail']

        current = self.ads1119.read_volt(Wct001002ADef.CURRENT_CHANNEL)
        if mode == 'senseR':
            current = float(current / Wct001002ADef.SENSER_CURRENT_GAIN)
        if mode == 'i_vrail':
            current = float(current / Wct001002ADef.I_VRAIL_CURRENT_GAIN)
        if self.is_use_cal_data():
            current = self.calibrate('READ_CURRENT', current)
            self.set_calibration_mode('raw')
            volt = self.read_vrail_voltage("ppvrail") - Wct001002ADef.VOLT_ORIGIN
            self.set_calibration_mode('cal')
            current_offset = self.calibrate('READ_CURRENT_5V_20V', volt)
            current = current + current_offset
        return current

    def inductor_calibration_read(self, inductance_gears):
        '''
        read the inductor and CAP_P_CTL bits status and the inductance value in the eeprom.

        Args:
            inductance_gears:     string,["Lmin", "Lnom", "Lmax"].

        Returns:
            dict,{'bit_status':0b0000101100,'L':26.4}
        bit_status meaning CAP_P_CTL10-CAP_P_CTL1 level.

        Examples:
            data = inductor_calibration_read()
            print(data)
        '''
        assert inductance_gears in Wct001002ADef.INDUCTOR_CALIBRATION_ADDRESS.keys()

        data = self.eeprom.read(Wct001002ADef.INDUCTOR_CALIBRATION_ADDRESS[inductance_gears],
                                Wct001002ADef.INDUCTOR_CALIBRATION_COUNT)
        s = struct.Struct('6B')
        pack_data = s.pack(*data)
        s = struct.Struct('1f2B')
        result = s.unpack(pack_data)
        return {'bit_status': '0b' + bin(result[2])[2:].zfill(2) + bin(result[1])[2:].zfill(8), 'L': result[0]}
