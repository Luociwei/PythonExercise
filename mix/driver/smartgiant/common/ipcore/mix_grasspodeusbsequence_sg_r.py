# -*- coding: utf-8 -*-
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'Weiping.Xuan@SmartGiant'
__version__ = '0.1'


class MIXGrassPodeUSBSequenceSGRDef:
    MODULE_EN_REG = 0x10
    REG_SIZE = 256
    FS_REG = 0x11
    LS_REG = 0x12
    FS_START = 0x01
    LS_START = 0x01
    PASS_MASK = 0x01
    MODULE_DISABLE = 0x00
    MODULE_ENABLE = 0x01
    SLEEP_TIME = 0.4


class MIXGrassPodeUSBSequenceSGRException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class MIXGrassPodeUSBSequenceSGR(object):
    '''
    MIXGrassPodeUSBSequenceSGR  class Used for EUSB testing

    ClassType = MIXGrassPodeUSBSequenceSGR

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or device path of AXI4LiteBus.

    Examples:
        grasspod = MIXGrassPodeUSBSequenceSGR('/dev/MIX_GrassPodeUSBSequence_SG_0')

    '''

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXGrassPodeUSBSequenceSGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.reset()

    def reset(self):
        '''
        Reset device, device must be reset and that can testing.

        Examples:
            grasspod.reset()
        '''

        self.axi4_bus.write_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.MODULE_EN_REG,
                                     [MIXGrassPodeUSBSequenceSGRDef.MODULE_DISABLE])
        self.axi4_bus.write_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.MODULE_EN_REG,
                                     [MIXGrassPodeUSBSequenceSGRDef.MODULE_ENABLE])
        return 'done'

    def fs_connect_test(self):
        '''
        FS connect test function, when the return is Ture, the test is passes.

        Examples:
            result = grasspod.fs_connect_test()
            print(result)
        '''

        self.axi4_bus.write_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.FS_REG, [MIXGrassPodeUSBSequenceSGRDef.FS_START])
        time.sleep(MIXGrassPodeUSBSequenceSGRDef.SLEEP_TIME)
        if(self.axi4_bus.read_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.FS_REG,
                                       1)[0] & MIXGrassPodeUSBSequenceSGRDef.PASS_MASK):
            return True
        return False

    def ls_connect_test(self):
        '''
        LS connect test function, when the return is Ture, the test is passes.

        Examples:
            result = grasspod.ls_connect_test()
            print(result)
        '''
        self.axi4_bus.write_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.LS_REG, [MIXGrassPodeUSBSequenceSGRDef.LS_START])
        time.sleep(MIXGrassPodeUSBSequenceSGRDef.SLEEP_TIME)
        if(self.axi4_bus.read_8bit_fix(MIXGrassPodeUSBSequenceSGRDef.LS_REG,
                                       1)[0] & MIXGrassPodeUSBSequenceSGRDef.PASS_MASK):
            return True
        return False
