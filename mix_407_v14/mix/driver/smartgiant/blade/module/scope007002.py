# -*- coding: utf-8 -*-
from blade import BladeBase


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.2'


class Scope007002Def:
    # CAT24C32 device address
    EEPROM_DEV_ADDR = 0x50


class SCOPE007002(BladeBase):

    '''
    This class is legacy driver for normal boot.

    compatible = ["GQQ-LWFV-5-020"]

    The Blade(SCOPE-007) module can perform simultaneously, continuously data recording;
    analog output; frequency conditioning;
    It includes eight ADC channels, four DAC channels, and AC signal measurement
    conditioning circuit.
    It can be used to recording DC voltage of power rail continuously and current
    sampling resistor’s voltage. And analog output signals to drive any device,
    such like PSU, reference level, etc..

    Args:
        i2c:                 instance(I2C), If not given, PLI2CBus emulator will be created.
        adc:                 instance(ADC), If not given, AD760X emulator will be created.
        xadc:                instance(XADC), if not given, PLXADC emulator will be created.
        adc_signal_meter:    instance(PLSignalMeter), if not given, PLSignalMeter emulator will be created.
        ac_signal_meter:     instance(PLSignalMeter), if not given, PLSignalMeter emulator will be created.
        fsk_signal_meter:    instance(PLSignalMeter), if not given, PLSignalMeter emulator will be created.
        ask_code:            instance(MIXQIASKLinkCode), if not given, MIXQIASKLinkCode emulator will be created.
        fsk_decode:          instance(MIXQIFSKLinkDecode), if not given, MIXQIFSKLinkDecode emulator will be created.
        adc_ctrl_pin_0:      instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        adc_ctrl_pin_1:      instance(GPIO), determine AD7608's data stream whether into AXI4_Signal_Meter_1 or DMA.
        fsk_ctrl_pin:        instance(GPIO), fsk enable/disable control pin.
        fsk_cic_ctrl_pin:    instance(GPIO), fsk enable/disable cic_filter control pin.
        adc_filter_pin_0:    instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_1:    instance(GPIO), determine which AD7608's channel to select.
        adc_filter_pin_2:    instance(GPIO), determine which AD7608's channel to select.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_I2C_0', 256)
        i2c_bus = PLI2CBus(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_AD760x_0', 8192)
        ad7608 = AD7608(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_XADC_0', 2048)
        xadc = PLXADC(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_0', 1024)
        adc_signal_meter= PLSignalMeter(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_1', 1024)
        ac_signal_meter = PLSignalMeter(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_Signal_Meter_2', 1024)
        fsk_signal_meter = PLSignalMeter(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_ASK_Encode_0', 2048)
        ask_code = MIXQIAskLinkCode(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/AXI4_FSK_Decode_0', 2048)
        fsk_decode = MIXQIFskLinkDecode(axi4_bus)

        axi4_bus = AXI4LiteBus('/dev/AXI4_GPIO_0', 256)
        gpio = PLGPIO(axi4_bus)
        adc_ctrl_pin_0 = Pin(gpio, 34)
        adc_ctrl_pin_1 = Pin(gpio, 33)
        fsk_ctrl_pin = Pin(gpio, 34)
        adc_filter_pin_0 = Pin(gpio, 35)
        adc_filter_pin_1 = Pin(gpio, 36)
        adc_filter_pin_2 = Pin(gpio, 37)

        blade = SCOPE007002(i2c=i2c_bus,
                            adc=ad7608,
                            xadc=xadc,
                            adc_signal_meter=adc_signal_meter,
                            ac_signal_meter=ac_signal_meter,
                            fsk_signal_meter=fsk_signal_meter,
                            ask_code=ask_code,
                            fsk_decode=fsk_decode,
                            adc_ctrl_pin_0=adc_ctrl_pin_0,
                            adc_ctrl_pin_1=adc_ctrl_pin_1,
                            fsk_ctrl_pin=fsk_ctrl_pin,
                            fsk_cic_ctrl_pin=fsk_cic_ctrl_pin,
                            adc_filter_pin_0=adc_filter_pin_0,
                            adc_filter_pin_1=adc_filter_pin_1,
                            adc_filter_pin_2=adc_filter_pin_2)

        Example for Analog input measurement:
            # Blade Analog input measurement, measure DC voltage with option `AVG` or `RMS`.
            adc_value = blade.adc_voltage_measure('AVG', 'ch0', '5V', 20000, 5, 100)
            print(adc_value)
            # Terminal shows "[xxx.xxx, 'mV']"

        Example for Analog output:
            # Blade dac output voltage, 0-5500 mV
            blade.dac_output('ch0', 1000)

        Example for AC signal measurement:
            # Signal: Square,100000Hz,2.5 VPP, 50%, High 1.25V

            # Blade measure ac signal with option 'f': freq
            result = blade.3.10 ac_signal_measure('f', 2500, 1000)
            print(result)
            # Terminal shows "{'freq': (xxx.x, 'Hz')}"

            # Blade measure ac signal with option 'v': vpp
            result = blade.3.10 ac_signal_measure('v', 2500, 1000)
            print(result)
            # Terminal shows "{'vpp': (xxx, 'mV')}"

            # Blade measure ac signal with option 'fwd': freq, width, duty
            result = blade.3.10 ac_signal_measure('fwd', 2500, 1000)
            print(result)
            # Terminal shows "{'duty': (xxx, '%%'), 'width': (xxx, 'us'), 'freq': (xxx, 'Hz')}"

        Example for ASK signal Encode:
            data = [1, 2, 3, 4, 5]
            blade.ask_write_encode_data(data)

        Example for FSK signal Decode:
            # Blade measure FSK signal frequency and receive data.
            freq = blade.fsk_frequency_measure(2000)
            print(freq)
            # FSK Decode State
            state = blade.fsk_decode_state()
            print(state)
            data = blade.fsk_read_decode_data()
            print(data)

        Example for data upload:
            dma = DMA("/dev/MIX_DMA_0")
            dma_channel = 0
            dma.config_channel(dma_channel, 0x1000000)
            dma.enable_channel(dma_channel)
            dma.reset_channel(dma_channel)
            blade.adc_measure_upload_enable('10V', 2000)
            time.sleep(1)
            result, data, data_num, overflow = dma.read_channel_all_data(dma_channel)
            dma.read_done(dma_channel, data_num)
            dma.disable_channel(dma_channel)
            blade.adc_measure_upload_disable()

            if result == 0:
                _len = 0
                    while data_num >= _len + 3:
                    code = data[_len + 0] | data[_len + 1] << 8 |
                            data[_len+2] << 16 | data[_len + 3] << 24
                    channel = code & 0x7
                    value = float((code>>14) & 0x3FFFF) / pow(2,17) * 10
                    print("chanel:%d, data:%f " % (channel, value))
                    _len = _len + 4
            else:
                print('error_code: %d' % (result))

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP007002-000"]

    def __init__(self, i2c=None, adc=None, xadc=None, adc_signal_meter=None,
                 ac_signal_meter=None, fsk_signal_meter=None,
                 ask_code=None, fsk_decode=None,
                 adc_ctrl_pin_0=None, adc_ctrl_pin_1=None,
                 fsk_ctrl_pin=None, fsk_cic_ctrl_pin=None,
                 adc_filter_pin_0=None, adc_filter_pin_1=None,
                 adc_filter_pin_2=None, ipcore=None):
        super(SCOPE007002, self).__init__(i2c, adc, xadc, adc_signal_meter,
                                          ac_signal_meter, fsk_signal_meter,
                                          ask_code, fsk_decode,
                                          adc_ctrl_pin_0, adc_ctrl_pin_1,
                                          fsk_ctrl_pin, fsk_cic_ctrl_pin,
                                          adc_filter_pin_0, adc_filter_pin_1,
                                          adc_filter_pin_2, ipcore,
                                          eeprom_devaddr=Scope007002Def.EEPROM_DEV_ADDR)
