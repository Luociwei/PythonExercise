# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_axilitetostream_sg import MIXAxiLiteToStreamSG
from mix.driver.smartgiant.common.ipcore.mix_macfct_eepromprivate_sg import MIXMacFCTEepromPrivateSG


__author__ = 'shunreng.he@SmartGiant'
__version__ = '0.1'


class MIXMacFCTBusMonitorSGRDef:
    MIX_Monitor_IPCORE_ADDR = 0x2000
    MIX_I2C_Slave_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x6000
    REG_SIZE = 65536


class MIXMacFCTBusMonitorSGR(object):
    '''
    MIXMacFCTBusMonitorSGR aggregated IPcore has 3 child IP, MIXAxiLiteToStreamSG, MIXMacFCTEepromPrivateSG, MIXGPIOSG.

    ClassType = MIXMacFCTBusMonitorSGR

    Args:
        axi4_bus:            instance(AXI4LiteBus)/string, axi4lite instance or dev path.
        use_monitor:         boolean, i2c monitor use flag.
        use_i2c_slave:       boolean, i2c slave use flag.
        use_gpio:            boolean, gpio use flag.

    Examples:
        macfct_busmonitor = MIXMacFCTBusMonitorSGR('/dev/MIX_MacFCT_BusMonitor_SG_R_0')

    '''

    def __init__(self, axi4_bus, use_monitor=True, use_i2c_slave=True, use_gpio=True):
        if isinstance(axi4_bus, basestring):
            axi4_bus = AXI4LiteBus(axi4_bus, MIXMacFCTBusMonitorSGRDef.REG_SIZE)
        else:
            axi4_bus = axi4_bus

        if use_monitor:
            self.monitor_bus = AXI4LiteSubBus(axi4_bus, MIXMacFCTBusMonitorSGRDef.MIX_Monitor_IPCORE_ADDR,
                                              MIXMacFCTBusMonitorSGRDef.REG_SIZE)
            self.monitor_dev = MIXAxiLiteToStreamSG(self.monitor_bus)

        if use_i2c_slave:
            self.slave_bus = AXI4LiteSubBus(axi4_bus, MIXMacFCTBusMonitorSGRDef.MIX_I2C_Slave_IPCORE_ADDR,
                                            MIXMacFCTBusMonitorSGRDef.REG_SIZE)
            self.slave_dev = MIXMacFCTEepromPrivateSG(self.slave_bus)

        if use_gpio:
            self.gpio_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXMacFCTBusMonitorSGRDef.MIX_GPIO_IPCORE_ADDR,
                                                MIXMacFCTBusMonitorSGRDef.REG_SIZE)
            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)
