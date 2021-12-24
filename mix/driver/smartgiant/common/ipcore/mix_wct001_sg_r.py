# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG


__author__ = 'Weiping.Xuan@SmartGiant'
__version__ = '0.1'


class MIXWCT001001SGRDef:
    SM_P_OFFSET_ADDR = 0x2000
    SM_N_OFFSET_ADDR = 0x4000
    SS_OFFSET_ADDR = 0x6000

    SM_P_REG_SIZE = 1024
    SM_N_REG_SIZE = 1024
    SS_REG_SIZE = 1024
    REG_SIZE = 65536


class MIXWCT001001SGRException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class MIXWCT001001SGR(object):
    def __init__(self, axi4_bus=None, use_signalmeter_p=True, use_signalmeter_n=True, use_signalsource=True):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXWCT001001SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.signalmeter_p = None
        self.signalmeter_n = None
        self.signalsource = None
        self.open(use_signalmeter_p, use_signalmeter_n, use_signalsource)

    def open(self, use_signalmeter_p=True, use_signalmeter_n=True, use_signalsource=True):

        if use_signalmeter_p is True:
            self.signalmeter_p_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXWCT001001SGRDef.SM_P_OFFSET_ADDR,
                                                         MIXWCT001001SGRDef.SM_P_REG_SIZE)
            self.signalmeter_p = MIXSignalMeterSG(self.signalmeter_p_axi4_bus)

        if use_signalmeter_n is True:
            self.signalmeter_n_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                         MIXWCT001001SGRDef.SM_N_OFFSET_ADDR,
                                                         MIXWCT001001SGRDef.SM_N_REG_SIZE)
            self.signalmeter_n = MIXSignalMeterSG(self.signalmeter_n_axi4_bus)

        if use_signalsource is True:
            self.signalsource_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                        MIXWCT001001SGRDef.SS_OFFSET_ADDR,
                                                        MIXWCT001001SGRDef.SS_REG_SIZE)
            self.signalsource = MIXSignalSourceSG(self.signalsource_axi4_bus)
