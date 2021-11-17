# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_widthmeasure_sg import MIXWidthMeasureSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG

__author__ = 'Kun.Yang@SmartGiant'
__version__ = '0.1'


class MIXBMUWidthSwitcherSGRDef:
    MIX_GPIO_IPCORE_ADDR = 0x2000
    MIX_WM_IPCORE_ADDR = 0x4000
    MIX_BMUWIDTHSWITCHER_IPCORE_VERSION = 0x00
    GPIO_REG_SIZE = 256
    WM_REG_SIZE = 8192
    REG_SIZE = 65536
    CHANNEL_SELECT_BIT0 = 0
    CHANNEL_SELECT_BIT1 = 1
    CHANNEL_SELECT_BIT2 = 2


class MIXBMUWidthSwitcherSGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXBMUWidthSwitcherSGR(object):
    '''
    MIXBMUWidthSwitcherSGR function class to measure the time difference between edge signals

    ClassType = MIXBMUWidthSwitcherSGR

    Args:
        axi4_bus: instance(AXI4LiteBus)/string,   Class instance or dev path of AXI4 bus.

    Examples:
        width_measure = MIXBMUWidthSwitcherSGR('/dev/MIX_Signal_Meter_0')

    '''

    rpc_public_api = ['start_measure', 'stop_measure', 'open', 'close']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXBMUWidthSwitcherSGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        axi4_gpio = AXI4LiteSubBus(self.axi4_bus, MIXBMUWidthSwitcherSGRDef.MIX_GPIO_IPCORE_ADDR,
                                   MIXBMUWidthSwitcherSGRDef.GPIO_REG_SIZE)
        axi4_widthmeasure = AXI4LiteSubBus(self.axi4_bus, MIXBMUWidthSwitcherSGRDef.MIX_WM_IPCORE_ADDR,
                                           MIXBMUWidthSwitcherSGRDef.WM_REG_SIZE)

        self.gpio = MIXGPIOSG(axi4_gpio)
        self.widthmeasure = MIXWidthMeasureSG(axi4_widthmeasure)
        self.gpio.set_pin_dir(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT0, 'output')
        self.gpio.set_pin_dir(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT1, 'output')
        self.gpio.set_pin_dir(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT2, 'output')

    def close(self):
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT0, 0)
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT1, 0)
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT2, 0)
        self.widthmeasure.stop_measure()

    def open(self):
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT0, 0)
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT1, 0)
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT2, 0)

    def start_measure(self, channel_select, start_status, stop_status):
        '''
        MIXBMUWidthSwitcherSGR module enable the corresponding register, then can get result

        Args:
            channel_select: int,  select the channel to measure.
            start_status:   int,  start trigger signal, details in class TriggarSignalDef.
            stop_status:    int,  stop trigger signal, details in class TriggarSignalDef.

        Returns:
            "done"

        '''
        assert isinstance(channel_select, int)

        a = bin(channel_select)
        a = a[2:]
        a = list(a)
        a.reverse()
        if 3 - len(a) == 0:
            a = a
        else:
            for i in range(3 - len(a)):
                a.append('0')
        a.reverse()
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT0, int(a[2]))
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT1, int(a[1]))
        self.gpio.set_pin(MIXBMUWidthSwitcherSGRDef.CHANNEL_SELECT_BIT2, int(a[0]))

        self.widthmeasure.config(start_triggar_signal=start_status, stop_triggar_signal=stop_status)
        self.widthmeasure.start_measure()
        return "done"

    def stop_measure(self, time_out):
        '''
        MIXWidthMeasureSG module disable the corresponding register, and then get time measure result.

        Args:
            time_out: int,  overtime of measure, unit:ms.

        Returns:
            list,  list of width values.

        '''
        self.time_out = time_out * 1000

        start_time = time.time() * 1000
        while 1:
            try:
                wid = self.widthmeasure.get_width()
                result = []
                for i in range(len(wid)):
                    result.append(wid[i].width)
                return result
            except Exception as e:
                if time.time() * 1000 - start_time > self.time_out:
                    raise MIXBMUWidthSwitcherSGRException("Timeout: {}".format(e.message))
            finally:
                self.widthmeasure.stop_measure()
