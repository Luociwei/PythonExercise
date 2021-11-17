# -*- coding: utf-8 -*-
from mix.driver.smartgiant.beast.module.beast import BeastBase

__author__ = 'Shunreng.He@SmartGiant'
__version__ = '1.0'


class Scope001002Def:
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48


class Scope001002(BeastBase):
    '''
    Scope001002 is a general medium-speed digital instrument module.

    compatible = ["GQQ-SCP001002-000"]

    Scope001002 will be used for voltage,
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
        range_ctrl:       instance(GPIO),                used to control Scope001002 range.
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
            scope001002 = Scope001002(i2c,range_ctrl, dcac_ctrl, output_ctrl, pl_signal_meter)

        # use MIXDAQT2 aggregated IP, not use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            # use cat9555 to control range, DC/AC and AD5231 enable state.
            cat9555 = CAT9555(0x20, i2c_bus)
            range_ctrl = Pin(cat9555, 5)
            dcac_ctrl = Pin(cat9555, 6)
            output_ctrl = Pin(cat9555, 4)
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, False)
            scope001002 = Scope001002(i2c,range_ctrl, dcac_ctrl, output_ctrl, None, mix_daqt2)

        # use MIXDAQT2 aggregated IP, use MIXDAQT2 inside gpio
            i2c = I2CBus('/dev/MIX_I2C_0')
            mix_daqt2 = MIXDAQT2('/dev/MIX_DAQT2_0', False, False, True)
            scope001002 = Scope001002(i2c, None, None, None, None, mix_daqt2)

        # if GPIO expander is behind a i2c-mux, set i2c-mux channel then call
            scope001002.board_init()
          to set default gpio direction before using the module to measure.

        # suppose input signal is 1000 Hz, vpp 1000 mV square waveform
        scope001002.select_ragne('AC_VOLT', 2, 'V')

        # frequncy meaurement
        result = scope001002.frequency_measure(100) # measure 100 ms
        print("freq={}Hz, duty={}%".format(result.[0], result[1]))
        # terminal show "freq=xxxHz, duty=xx%"

        # VPP measurement
        result = scope001002.vpp_measure(100) # measure 100 ms
        print("vpp={}mV, max={}mV, min={}mV".format(result[0], result[1], result{2}))
        # terminal show "vpp=xxxmV, max=xxxmV, min=xxxmV"

        # rms measurement
        result = scope001002.rms_measure(100) # measure 100 ms
        print("rms={}mV, average={}mV".format(result[0], result[1]))
        # terminal show "rms=xxxmV, average=xxxmV"

        # upload data in 100ms through dma
        scope001002.enable_continuous_measure()
        time.sleep(100)
        scope001002.disable_continuous_measure()

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP001002-000"]

    def __init__(self, i2c, range_ctrl=None, dcac_ctrl=None, output_ctrl=None, pl_signal_meter=None, ipcore=None):
        super(Scope001002, self).__init__(i2c, range_ctrl, dcac_ctrl, output_ctrl, pl_signal_meter, ipcore,
                                          Scope001002Def.EEPROM_DEV_ADDR, Scope001002Def.SENSOR_DEV_ADDR)
