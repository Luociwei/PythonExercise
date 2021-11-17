# -*- coding: utf-8 -*-
import os
import ctypes
import time
from ctypes import string_at

__author__ = 'qinxiaojun@SmartGiant'
__version__ = '0.1'


class MIXDMASGError(Exception):
    def __init__(self, dev_name, err_code):
        reason = (128 * ctypes.c_char)()
        base_lib = ctypes.cdll.LoadLibrary('libmix-dma-sg-driver.so')
        reason = base_lib.sg_axis_get_err_reason(err_code)
        self._err_reason = '[%s]: %s.' % \
            (dev_name, string_at(reason, -1).decode("utf-8"))

    def __str__(self):
        return self._err_reason


class MIXDMASG(object):
    '''
    Singleton wrapper of SmartGiant MIX_DMA_SG driver.

    ClassType = DMA

    This is to ensure only 1 instance is created for the same char device
    in /dev/MIX_MIXDMASG, even if instantiated multiple times.

    Args:
        dev_name:      string, MIXDMASG device full path like '/dev/MIX_MIXDMASG'.
        dma_size_mb:   int, default 128, MIXDMASG max memory size.

    Examples:
        dma_1 = MIXDMASG('/dev/MIX_MIXDMASG')
        dma_2 = MIXDMASG('/dev/MIX_MIXDMASG')
        assert dma_1 == dma_2          # True

    '''
    # class variable to host all i2c bus instances created.
    instances = {}

    def __new__(cls, dev_name, **kwarg):
        if dev_name in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _MIXDMASG(dev_name, **kwarg)
            cls.instances[dev_name] = instance
        return cls.instances[dev_name]


class _MIXDMASG(object):
    '''
    MIX_DMA_SG function class

    Args:
        dev_name:      string,             MIXDMASG device full path like '/dev/MIX_MIXDMASG'.
        dma_size_mb:   int, default 128,   MIXDMASG max memory size.

    Examples:
        dma = MIXDMASG('/dev/MIX_MIXDMASG_0', 64)
        # create MIXDMASG instance and reserve 64MB memory for MIXDMASG.

    '''

    rpc_public_api = ['config_channel', 'enable_channel', 'disable_channel', 'reset_channel',
                      'read_channel_data', 'read_channel_all_data', 'read_done']

    KERNEL_MODULE = os.path.join(os.path.dirname(__file__), 'axi4stream.ko')

    def __init__(self, dev_name, dma_size_mb=128):
        self._dev_name = dev_name
        self.dma_size_byte = dma_size_mb * 1024 * 1024
        self.reload_dma_kernel_driver()
        self.base_lib = ctypes.cdll.LoadLibrary('libmix-dma-sg-driver.so')
        self.base_lib.sg_axis_init.restype = ctypes.c_void_p
        dma_dev = self.base_lib.sg_axis_init(self._dev_name)
        if not dma_dev:
            return None
        self._dma_dev = dma_dev
        self._mem_offset = 0

    def __del__(self):
        self.base_lib.sg_axis_exit(self._dma_dev)
        self.unload_dma_kernel_driver()

    def load_dma_kernel_driver(self):
        cmd = 'insmod {} CMA_SIZE={:#}'.format(_MIXDMASG.KERNEL_MODULE, self.dma_size_byte)
        assert 0 == os.system(cmd), 'MIXDMASG kernel driver axi4stream.ko load failed.'
        # ensure /dev/ device is successfully generated.
        now = time.time()
        # usually this should finish in < 1s.
        timeout = 5
        while (time.time() - now < timeout):
            if os.path.exists(self._dev_name):
                break
        else:
            msg = 'MIXDMASG device {} did not appear in /dev/ in {}s after kernel module loaded'
            raise Exception(msg.format(self._dev_name, timeout))

    def unload_dma_kernel_driver(self):
        '''
        Ensure not loaded.
        '''
        cmd = 'rmmod axi4stream'
        os.system(cmd)

    def reload_dma_kernel_driver(self):
        self.unload_dma_kernel_driver()
        self.load_dma_kernel_driver()

    def config_channel(self, id, size):
        '''
        Config dma channel

        Args:
            id:      int, [0~15], Id of the channel to be configured.
            size:    hexmial, [0~MIXDMASG_MEM_SIZE], unit byte, MIX_DMA_SG channel size, must align to 256.

        Examples:
            dma = MIXDMASG("/dev/MIX_DMA_SG_0")
            dma.config_channel(0, 0x1000000)

        '''
        assert id < 16
        result = self.base_lib.sg_axis_config_channel(self._dma_dev,
                                                      id, self._mem_offset,
                                                      size)
        if result != 0:
            raise MIXDMASGError(self._dev_name, result)
        self._mem_offset += size

        return True

    def enable_channel(self, id):
        '''
        Enable dma channel

        Args:
            id:      int, [0~15], Id of the channel to be enable.

        Examples:
            dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
            dma.config_channel(0, 0x0, 0x1000000)
            dma.enable_chanel(0)

        '''
        assert id < 16
        result = self.base_lib.sg_axis_enable_channel(self._dma_dev, id)
        if result != 0:
            raise MIXDMASGError(self._dev_name, result)

        return True

    def disable_channel(self, id):
        '''
        Disable dma channel

        Args:
            id:      int, [0~15], Id of the channel to be enable.

        Examples:
            dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
            dma.config_channel(0, 0x1000000)
            dma.disable_chanel(0)

        '''
        assert id < 16
        self.base_lib.sg_axis_disable_channel(self._dma_dev, id)

    def reset_channel(self, id):
        '''
        Reset dma channel

        Args:
            id:      int, [0~15], Id of the channel to be reset.

        Examples:
                dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
                dma.config_channel(0, 0x1000000)
                dma.reset_chanel(0)

        '''
        assert id < 16
        result = self.base_lib.sg_axis_reset_channel(self._dma_dev, id)
        if result != 0:
            raise MIXDMASGError(self._dev_name, result)

        return True

    def read_channel_data(self, id, length, timeout):
        '''
        Read data from dma channel

        Args:
            id:         int, [0~15], Id of the channel to be read.
            length:     hexmial, [0~MIXDMASG_CHANNEL_SIZE], Length of data to read.
            timeout:    int, [0~MAX], unit ms, The timeout of reading data.

        Examples:
            dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
            dma.config_channel(0, 0x1000000)
            dma.enable_chanel(0)
            result, data, len, overflow = dma.read_channel_data(0, 0x200, 100)
            if result == 0:
                print data

        '''
        assert id < 16
        buf = ctypes.POINTER(ctypes.c_ubyte * length)()
        actual_len = ctypes.c_uint(0)
        overflow = ctypes.c_uint(0)
        result = self.base_lib.sg_axis_read_data(self._dma_dev, id, length,
                                                 ctypes.byref(buf),
                                                 ctypes.byref(actual_len),
                                                 ctypes.byref(overflow),
                                                 timeout)

        return result, buf.contents, actual_len.value, overflow.value

    def read_channel_all_data(self, id):
        '''
        Read all data from dma channel

        Args:
            id:      int, [0~15], Id of the channel to be read.

        Examples:
            dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
            dma.config_channel(0, 0x1000000)
            dma.enable_chanel(0)
            result, data, len, overflow = dma.read_channel_all_data(0)
            if result == 0:
                print data
            elif result == -6:
                print data
                dma.read_done(0, len)
                result, data, len, overflow = dma.read_channel_all_data(0)
                print data

        '''
        assert id < 16
        max_len = 0x20000000
        buf = ctypes.POINTER(ctypes.c_ubyte * max_len)()
        actual_len = ctypes.c_uint(0)
        overflow = ctypes.c_uint(0)
        result = self.base_lib.sg_axis_read_all_data(self._dma_dev, id,
                                                     ctypes.byref(buf),
                                                     ctypes.byref(actual_len),
                                                     ctypes.byref(overflow))

        return result, buf.contents, actual_len.value, overflow.value

    def read_done(self, id, length):
        '''
        Notify how many data have been read

        Args:
            id:         int, [0~15], Id of the channel to be notify.
            length:     hexmial, [0-MIXDMASG_CHANNEL_SIZE], Length of data been read.

        Examples:
            dma = MIXDMASG("/dev/MIX_MIXDMASG_0")
            dma.config_channel(0, 0x1000000)
            dma.enable_chanel(0)
            result, data, len, overflow = dma.read_channel_data(0, 0x200, 100)
            if result == 0:
                print data
                dma.read_done(0, len)

        '''
        assert id < 16
        self.base_lib.sg_axis_read_done(self._dma_dev, id, length)
