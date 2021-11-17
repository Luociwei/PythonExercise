# -*- coding: utf-8 -*-
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.smartgiant.common.ic.ad9628 import AD9628
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ipcore.mix_daqt2_sg_r import MIXDAQT2SGR
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard

__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.2'


magik_calibration_info = {
    "ch0_dc_volt_average": {
        'level1': {'unit_index': 0, 'unit': 'mV'},
        'level2': {'unit_index': 1, 'unit': 'mV'},
        'level3': {'unit_index': 2, 'unit': 'mV'},
        'level4': {'unit_index': 3, 'unit': 'mV'},
        'level5': {'unit_index': 4, 'unit': 'mV'},
        'level6': {'unit_index': 5, 'unit': 'mV'},
        'level7': {'unit_index': 6, 'unit': 'mV'},
        'level8': {'unit_index': 7, 'unit': 'mV'}
    },
    "ch0_ac_volt_vpp": {
        'level1': {'unit_index': 8, 'unit': 'mV'},
        'level2': {'unit_index': 9, 'unit': 'mV'},
        'level3': {'unit_index': 10, 'unit': 'mV'},
        'level4': {'unit_index': 11, 'unit': 'mV'},
        'level5': {'unit_index': 12, 'unit': 'mV'},
        'level6': {'unit_index': 13, 'unit': 'mV'}
    },
    "ch1_dc_volt_average": {
        'level1': {'unit_index': 14, 'unit': 'mV'},
        'level2': {'unit_index': 15, 'unit': 'mV'},
        'level3': {'unit_index': 16, 'unit': 'mV'},
        'level4': {'unit_index': 17, 'unit': 'mV'},
        'level5': {'unit_index': 18, 'unit': 'mV'},
        'level6': {'unit_index': 19, 'unit': 'mV'},
        'level7': {'unit_index': 20, 'unit': 'mV'},
        'level8': {'unit_index': 21, 'unit': 'mV'}
    },
    "ch1_ac_volt_vpp": {
        'level1': {'unit_index': 22, 'unit': 'mV'},
        'level2': {'unit_index': 23, 'unit': 'mV'},
        'level3': {'unit_index': 24, 'unit': 'mV'},
        'level4': {'unit_index': 25, 'unit': 'mV'},
        'level5': {'unit_index': 26, 'unit': 'mV'},
        'level6': {'unit_index': 27, 'unit': 'mV'},
        'level7': {'unit_index': 28, 'unit': 'mV'}
    }

}

magik_range_table = {
    "ch0_dc_volt_average": 0,
    "ch0_ac_volt_vpp": 1,
    "ch1_dc_volt_average": 2,
    "ch1_ac_volt_vpp": 3
}


class MagikDef:
    CHANNEL_0 = 0
    CHANNEL_1 = 1
    OPA_PD1_PIN = 14
    OPA_PD2_PIN = 15
    AD9628_PDWN_PIN = 6
    AD9628_CS_CTRL_PIN = 12
    AD9517_CS_CTRL_PIN = 13
    RELAY1_CTR_PIN = 9
    RELAY2_CTR_PIN = 10
    IO_LOW_LEVEL = 0
    IO_HIGH_LEVEL = 1
    CAT9555_ADDR = 0x20
    EEPROM_DEV_ADDR = 0x51
    SENSOR_DEV_ADDR = 0x49
    COMPATIBLE_EEPROM_DEV_ADDR = 0x50
    COMPATIBLE_SENSOR_DEV_ADDR = 0x48
    AD9628_CHIP_ID = 0x89
    DC_MEASURE_MASK = 0x30
    PIN_OUTPUT_DIRECTION = 'output'
    AD9628_OUTPUT_TYPE = 'LVDS_ANSI'
    AD9628_OUTPUT_FORMAT = 'OFFSET_BIN'
    AD9628_SAMPLE_RATE = 125000000  # unit:SPS
    AD9628_RESOLUTION = 'WIDTH_12'
    AD9628_DCO_DELAY_DISABLE = 'DCO_DELAY_CLOSE'
    AD9628_DATA_DELAY_ENABLE = 'DATA_DELAY_OPEN'
    DATA_DELAY_LEVEL = '1_12_NS'  # output delay 1.12ns
    SPI_CLOCK_SPEED = 500000  # Hz
    SPI_BUS_MODE = 'MODE3'
    SIGNAL_METER_REG_SIZE = 256
    MIX_DAQT2_REG_SIZE = 65536

    # adc measure volt range, value unit is mV
    ADC_VOLT_RANGE = [-1000, 1000]
    SIGNAL_METER_SCALE_RANGE = [-1.0, 1.0]

    ADC_VPP_RANGE = [0, ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]]
    SIGNAL_METER_VPP_SCALE_RANGE = [0, 2.0]

    RMS_RANGE = [0, 1000]
    SIGNAL_METER_RMS_SCALE_RANGE = [0, 1.0]

    MAX_SCALE_GAIN = (ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]) / \
        (SIGNAL_METER_SCALE_RANGE[1] - SIGNAL_METER_SCALE_RANGE[0])
    MAX_SCALE_OFFSET = ADC_VOLT_RANGE[1] - MAX_SCALE_GAIN * SIGNAL_METER_SCALE_RANGE[1]

    MIN_SCALE_GAIN = (ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]) / \
        (SIGNAL_METER_SCALE_RANGE[1] - SIGNAL_METER_SCALE_RANGE[0])
    MIN_SCALE_OFFSET = ADC_VOLT_RANGE[1] - MIN_SCALE_GAIN * SIGNAL_METER_SCALE_RANGE[1]

    AVG_SCALE_GAIN = (ADC_VOLT_RANGE[1] - ADC_VOLT_RANGE[0]) / \
        (SIGNAL_METER_SCALE_RANGE[1] - SIGNAL_METER_SCALE_RANGE[0])
    AVG_SCALE_OFFSET = ADC_VOLT_RANGE[1] - AVG_SCALE_GAIN * SIGNAL_METER_SCALE_RANGE[1]

    VPP_SCALE_GAIN = (ADC_VPP_RANGE[1] - ADC_VPP_RANGE[0]) / \
        (SIGNAL_METER_VPP_SCALE_RANGE[1] - SIGNAL_METER_VPP_SCALE_RANGE[0])
    VPP_SCALE_OFFSET = ADC_VPP_RANGE[1] - VPP_SCALE_GAIN * SIGNAL_METER_VPP_SCALE_RANGE[1]

    RMS_SCALE_GAIN = (RMS_RANGE[1] - RMS_RANGE[0]) / (SIGNAL_METER_RMS_SCALE_RANGE[1] - SIGNAL_METER_RMS_SCALE_RANGE[0])
    RMS_SCALE_OFFSET = RMS_RANGE[1] - RMS_SCALE_GAIN * SIGNAL_METER_RMS_SCALE_RANGE[1]


class MagikException(Exception):
    '''
    MagikException shows the exception of Magik
    '''

    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class MagikBase(MIXBoard):
    '''
    Base class of Magik and MagikCompatible,Providing common Magik methods.

    Args:
        ipcore:          instance(MIXDAQT2SGR)/string/None, instance of MIXDAQT2, which is integrated IPcore,
                                                       if not giving this parameter, will create emulator.
        signal_meter_0:  instance(MIXSignalMeterSGR)/None, instance of PLSignalMeter, which is used to measure signal,
                                                       if not giving this parameter, will create emulator.
        signal_meter_1:  instance(MIXSignalMeterSG)/None, instance of PLSignalMeter, which is used to measure signal,
                                                       if not giving this parameter, will create emulator.
        spi:             instance(QSPI)/None, instance of PLSPIBus, which is used to control SPI Bus,
                                              if not giving this parameter, will create emulator.
        i2c:             instance(I2C)/None, instance of PLI2CBus, which is used to control cat9555, eeprom
                                             and nct75 sensor.
        eeprom_dev_addr: int,                Eeprom device address.
        sensor_dev_addr: int,                NCT75 device address.

    '''

    rpc_public_api = ['module_init', 'set_differential_amplifier_work_mode', 'enable_data_upload',
                      'disable_data_upload', 'measure_ac', 'measure_dc'] + MIXBoard.rpc_public_api

    def __init__(
            self, ipcore=None, signal_meter_0=None, signal_meter_1=None, spi=None, i2c=None,
            eeprom_dev_addr=MagikDef.EEPROM_DEV_ADDR, sensor_dev_addr=MagikDef.SENSOR_DEV_ADDR):
        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, MagikDef.MIX_DAQT2_REG_SIZE)
                self.mix_daqt2 = MIXDAQT2SGR(axi4_bus, use_signal_meter1=True, use_spi=True, use_gpio=False)
                self.signal_meter0 = self.mix_daqt2.signal_meter0
                self.signal_meter1 = self.mix_daqt2.signal_meter1
                self.spi = self.mix_daqt2.spi
            else:
                self.ipcore = ipcore
                self.signal_meter0 = ipcore.signal_meter0
                self.signal_meter1 = ipcore.signal_meter1
                self.spi = ipcore.spi
            if signal_meter_0 or signal_meter_1 or spi:
                raise MagikException('Not allowed to use both Integrated IP and Separated IP at the same time!')
        else:
            if signal_meter_0 and signal_meter_1:
                if isinstance(signal_meter_0, basestring):
                    axi4_bus = AXI4LiteBus(signal_meter_0, MagikDef.SIGNAL_METER_REG_SIZE)
                    self.signal_meter0 = MIXSignalMeterSG(axi4_bus)
                else:
                    self.signal_meter0 = signal_meter_0
                if isinstance(signal_meter_1, basestring):
                    axi4_bus = AXI4LiteBus(signal_meter_1, MagikDef.SIGNAL_METER_REG_SIZE)
                    self.signal_meter1 = MIXSignalMeterSG(axi4_bus)
                else:
                    self.signal_meter1 = signal_meter_1
            elif not signal_meter_0 and not signal_meter_1:
                self.signal_meter0 = MIXSignalMeterSGEmulator('mix_signalmeter_sg_emulator', 256)
                self.signal_meter1 = MIXSignalMeterSGEmulator('mix_signalmeter_sg_emulator', 256)
            else:
                raise MagikException('signal_meter_0 and signal_meter_1 IP need to exist or be empty at the same time!')
            self.spi = spi if spi else MIXQSPISGEmulator('mix_qspi_sg_emulator', 256)

        if i2c:
            self.cat9555 = CAT9555(MagikDef.CAT9555_ADDR, i2c)
            self.nct75 = NCT75(sensor_dev_addr, i2c)
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
        else:
            self.cat9555 = CAT9555Emulator(MagikDef.CAT9555_ADDR, None, None)
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.nct75 = NCT75Emulator('nct75_emulator')

        self.spi.open()
        self.spi.set_speed(MagikDef.SPI_CLOCK_SPEED)
        self.spi.set_mode(MagikDef.SPI_BUS_MODE)
        ad9628_pdwn = Pin(self.cat9555, 6)
        ad9628_oeb = Pin(self.cat9555, 7)
        ad9628_cs = Pin(self.cat9555, 12)
        self.ad9628 = AD9628(self.spi, ad9628_pdwn, ad9628_oeb, ad9628_cs)
        super(MagikBase, self).__init__(self.eeprom, self.nct75,
                                        cal_table=magik_calibration_info, range_table=magik_range_table)

    def module_init(self):
        '''
        Init module, config cat9555 and ad9628

        Returns:
            string, "done", api execution successful.

        Examples:
            magik.module_init()

        '''
        self.load_calibration()
        # init AD9628
        self.cat9555.set_pin_dir(MagikDef.AD9628_PDWN_PIN, MagikDef.PIN_OUTPUT_DIRECTION)
        self.cat9555.set_pin(MagikDef.AD9628_PDWN_PIN, MagikDef.IO_LOW_LEVEL)
        self.cat9555.set_pin_dir(MagikDef.AD9628_CS_CTRL_PIN, MagikDef.PIN_OUTPUT_DIRECTION)
        self.cat9555.set_pin(MagikDef.AD9628_CS_CTRL_PIN, MagikDef.IO_HIGH_LEVEL)

        if MagikDef.AD9628_CHIP_ID != self.ad9628.get_chip_id():
            raise MagikException('read AD9628 chip id error!')
        self.ad9628.data_output_delay(MagikDef.AD9628_DCO_DELAY_DISABLE,
                                      MagikDef.AD9628_DATA_DELAY_ENABLE,
                                      MagikDef.DATA_DELAY_LEVEL)
        self.ad9628.setup(MagikDef.AD9628_OUTPUT_TYPE, MagikDef.AD9628_OUTPUT_FORMAT,
                          MagikDef.AD9628_SAMPLE_RATE, MagikDef.AD9628_RESOLUTION)

        # init AD9517
        self.cat9555.set_pin_dir(MagikDef.AD9517_CS_CTRL_PIN,
                                 MagikDef.PIN_OUTPUT_DIRECTION)
        self.cat9555.set_pin(MagikDef.AD9517_CS_CTRL_PIN,
                             MagikDef.IO_HIGH_LEVEL)

        self.cat9555.set_pin_dir(MagikDef.RELAY1_CTR_PIN,
                                 MagikDef.PIN_OUTPUT_DIRECTION)
        self.cat9555.set_pin(MagikDef.RELAY1_CTR_PIN,
                             MagikDef.IO_HIGH_LEVEL)
        self.cat9555.set_pin_dir(MagikDef.RELAY2_CTR_PIN,
                                 MagikDef.PIN_OUTPUT_DIRECTION)
        self.cat9555.set_pin(MagikDef.RELAY2_CTR_PIN,
                             MagikDef.IO_HIGH_LEVEL)
        self.set_differential_amplifier_work_mode('open')

        return 'done'

    def set_differential_amplifier_work_mode(self, operation):
        '''
        control differential amplifier in low power or not

        you must select open mode if you want to measure the signal

        Args:
            operation:    string, ['open', 'close'].

        Returns:
            string, "done", api execution successful.

        Examples:
            magik.set_differential_amplifier_work_mode('open')

        '''
        assert operation in ('open', 'close')

        if 'open' == operation:
            self.cat9555.set_pin(MagikDef.OPA_PD1_PIN,
                                 MagikDef.IO_HIGH_LEVEL)
            self.cat9555.set_pin(MagikDef.OPA_PD2_PIN,
                                 MagikDef.IO_HIGH_LEVEL)
        elif 'close' == operation:
            self.cat9555.set_pin(MagikDef.OPA_PD1_PIN, MagikDef.IO_LOW_LEVEL)
            self.cat9555.set_pin(MagikDef.OPA_PD2_PIN, MagikDef.IO_LOW_LEVEL)

        return 'done'

    def enable_data_upload(self, channel, upframe_mode='DEBUG'):
        '''
        enable signal meter upload

        Args:
            channel:      int, [0, 1].
            upframe_mode: string, ['DEBUG', 'BYPASS'].

        Returns:
            string, "done", api execution successful.

        Examples:
            magik.enable_data_upload(1)

        '''
        assert channel in (MagikDef.CHANNEL_0, MagikDef.CHANNEL_1)

        signal_meter_dict = {0: self.signal_meter0, 1: self.signal_meter1}
        signal_meter = signal_meter_dict[channel]
        signal_meter.open()
        signal_meter.enable_upframe(upframe_mode)

        return 'done'

    def disable_data_upload(self, channel):
        '''
        disable signal meter upload

        Args:
            channel:      int, [0, 1].

        Returns:
            string, "done", api execution successful.

        Examples:
            magik.disable_data_upload(1)

        '''
        assert channel in (MagikDef.CHANNEL_0, MagikDef.CHANNEL_1)

        signal_meter_dict = {0: self.signal_meter0, 1: self.signal_meter1}
        signal_meter = signal_meter_dict[channel]
        signal_meter.disable_upframe()
        signal_meter.close()

        return 'done'

    def measure_ac(self, channel, measure_type='LP', measure_time=100, vpp_interval=1, freq_flag=True):
        '''
        Signal meter measure ac

        Args:
            channel:        int, [0 , 1].
            measure_type:   string, ['HP', 'LP'], default 'LP', type of measure.
            measure_time:   int, [1~2000], unit ms, default 100.
            vpp_interval:   int, [1-10000], unit ms, default 1, used to determine how often to.
                                           collect data during measurement time.
            freq_flag:      boolean, [True, False], default True, True means measuring frequency,
                                     False means not measuring frequency and the parameter measure_type has no effect.

        Returns:
            dict, {'freq': (freq, 'Hz'), 'vpp': (vpp, 'mV'),
                   'max': (max, 'mV'),   'min': (min, 'mV'),
                   'rms': (rms, 'mV'),   'avg': (avg, 'mV')}
                  or
                  {'vpp': (vpp, 'mV'),   'max': (max, 'mV'), 'min': (min, 'mV'),
                   'rms': (rms, 'mV'),   'avg': (avg, 'mV')}.

        Examples:
            result = magik.measure_ac(1, 'LP', 100, 10, True)
            print(result['max'][0])

        '''
        assert channel in (MagikDef.CHANNEL_0, MagikDef.CHANNEL_1)

        signal_meter_dict = {0: self.signal_meter0, 1: self.signal_meter1}
        signal_meter = signal_meter_dict[channel]
        signal_meter.open()
        signal_meter.set_vpp_interval(vpp_interval)
        if freq_flag is True:
            signal_meter.start_measure(measure_time, MagikDef.AD9628_SAMPLE_RATE)
            freq = signal_meter.measure_frequency(measure_type)
        else:
            signal_meter.start_measure(measure_time, MagikDef.AD9628_SAMPLE_RATE, MagikDef.DC_MEASURE_MASK)

        result = signal_meter.vpp()
        vpp = (result[2] * MagikDef.VPP_SCALE_GAIN + MagikDef.VPP_SCALE_OFFSET)
        max = (result[0] * MagikDef.MAX_SCALE_GAIN + MagikDef.MAX_SCALE_OFFSET)
        min = (result[1] * MagikDef.MIN_SCALE_GAIN + MagikDef.MIN_SCALE_OFFSET)

        result = signal_meter.rms()
        rms = (result[0] * MagikDef.RMS_SCALE_GAIN + MagikDef.RMS_SCALE_OFFSET)
        avg = (result[1] * MagikDef.AVG_SCALE_GAIN + MagikDef.AVG_SCALE_OFFSET)

        vpp = self.calibrate('ch%s_ac_volt_vpp' % channel, vpp)

        result = dict()
        if freq_flag is True:
            result['freq'] = (freq, 'Hz')
        result['vpp'] = (vpp, 'mV')
        result['max'] = (max, 'mV')
        result['min'] = (min, 'mV')
        result['rms'] = (rms, 'mV')
        result['avg'] = (avg, 'mV')
        signal_meter.close()

        return result

    def measure_dc(self, channel, measure_time=100, vpp_interval=1):
        '''
        Signal meter measure dc
        Args:
            channel:       int, [0 , 1].
            measure_time:  int, [1~2000], unit ms, default 100.
            vpp_interval:  int, [1-10000], unit ms, default 1, used to determine how often to.
                                           collect data during measurement time.

        Returns:
            dict, {'vpp': (vpp, 'mV'),
                   'max': (max, 'mV'), 'min': (min, 'mV'),
                   'rms': (rms, 'mV'), 'avg': (avg, 'mV')}.

        Examples:
            result = magik.measure_dc(1, 100, 1)
            print(result['max'][0])

        '''
        assert channel in (MagikDef.CHANNEL_0, MagikDef.CHANNEL_1)

        signal_meter_dict = {0: self.signal_meter0, 1: self.signal_meter1}
        signal_meter = signal_meter_dict[channel]
        signal_meter.open()
        signal_meter.set_vpp_interval(vpp_interval)
        signal_meter.start_measure(measure_time, MagikDef.AD9628_SAMPLE_RATE, MagikDef.DC_MEASURE_MASK)
        result = signal_meter.vpp()
        vpp = (result[2] * MagikDef.VPP_SCALE_GAIN + MagikDef.VPP_SCALE_OFFSET)
        max = (result[0] * MagikDef.MAX_SCALE_GAIN + MagikDef.MAX_SCALE_OFFSET)
        min = (result[1] * MagikDef.MIN_SCALE_GAIN + MagikDef.MIN_SCALE_OFFSET)

        result = signal_meter.rms()
        rms = (result[0] * MagikDef.RMS_SCALE_GAIN + MagikDef.RMS_SCALE_OFFSET)
        avg = (result[1] * MagikDef.AVG_SCALE_GAIN + MagikDef.AVG_SCALE_OFFSET)

        avg = self.calibrate('ch%s_dc_volt_average' % channel, avg)

        result = dict()
        result['vpp'] = (vpp, 'mV')
        result['max'] = (max, 'mV')
        result['min'] = (min, 'mV')
        result['rms'] = (rms, 'mV')
        result['avg'] = (avg, 'mV')
        signal_meter.close()

        return result


class Magik(MagikBase):
    '''
    Magik is a digital instrument module.

    compatible = ["GQQ-SCP005002-000"]

    Max sampling rate is 125Msps. ADC resolution is 12bit.
    The module has two channels, which are used to measure voltage. Max input voltage is +/-1V.

    Note:This class is legacy driver for normal boot.

    Args:
        ipcore:          instance(MIXDAQT2)/None, instance of MIXDAQT2, which is integrated IPcore,
                                                       if not giving this parameter, will create emulator.
        signal_meter_0:  instance(PLSignalMeter)/None, instance of PLSignalMeter, which is used to measure signal,
                                                       if not giving this parameter, will create emulator.
        signal_meter_1:  instance(PLSignalMeter)/None, instance of PLSignalMeter, which is used to measure signal,
                                                       if not giving this parameter, will create emulator.
        spi:             instance(QSPI)/None, instance of PLSPIBus, which is used to control SPI Bus,
                                              if not giving this parameter, will create emulator.
        i2c:             instance(I2C)/None, instance of PLI2CBus, which is used to control cat9555, eeprom
                                             and nct75 sensor.

    Examples:
        # use non-aggregated IP
        signal_meter_0 = PLSignalMeter('/dev/MIX_SignalMeter_0')
        signal_meter_1 = PLSignalMeter('/dev/MIX_SignalMeter_1')
        spi = PLSPIBus('/dev/MIX_SPI')
        i2c = I2C('/dev/i2c-1')
        magik = Magik(None, signal_meter_0, signal_meter_1, spi, i2c)

        # use MIXDAQT2 aggregated IP
        i2c = I2C('/dev/i2c-1')
        ip = MIXDAQT2('/dev/MIX_DAQT2_0')
        magik = Magik(ip, None, None, None, i2c)

        # measure ac voltage
        result = magik.measure_ac(1, 'LP', 100, 10)
        print("freq=%0.6f Hz, vpp=%0.6f mV, max=%0.6f mV, min=%0.6f mV, rms=%0.6f mV, avg=%0.6f mV"
           % (result['freq'][0], result['vpp'][0], result['max'][0], result['min'][0],
              result['rms'][0], result['avg'][0]))

        # measure dc voltage
        result = magik.measure_dc(1, 100, 1)
        print("vpp=%0.6f mV, max=%0.6f mV, min=%0.6f mV, rms=%0.6f mV, avg=%0.6f mV"
           % (result['vpp'][0], result['max'][0], result['min'][0],
              result['rms'][0], result['avg'][0]))

        # upload data through DMA
        magik.module_init()
        magik.disable_data_upload(1)
        magik.enable_data_upload(1)
        result = magik.measure_ac(1, 'LP', 100, 10)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP005002-000"]

    def __init__(self, ipcore=None, signal_meter_0=None, signal_meter_1=None, spi=None, i2c=None):
        super(Magik, self).__init__(ipcore, signal_meter_0, signal_meter_1, spi, i2c,
                                    MagikDef.EEPROM_DEV_ADDR, MagikDef.SENSOR_DEV_ADDR)
