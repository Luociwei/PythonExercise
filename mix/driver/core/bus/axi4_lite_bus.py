# -*- coding: utf-8 -*-
import ctypes
import struct
from axi4_lite_def import AXI4Def
from axi4_lite_bus_lib_emulator import AXI4LiteBusLibEmulator


class AXI4LiteBusException(Exception):
    def __init__(self, dev_name, err_code):
        reason = (128 * ctypes.c_char)()
        base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        base_lib.get_error_reason(err_code, reason, len(reason))
        self._err_reason = '[%s]: %s.' % (dev_name, ctypes.string_at(reason, -1).decode('utf-8'))

    def __str__(self):
        return self._err_reason


class AXI4LiteBusRunTimeException(Exception):
    def __init__(self, err_str):
        self._err_str = err_str

    def __str__(self):
        return self._err_str


class AXI4LiteBusBase(object):
    '''
    Base class of AXI4LiteBus and AXI4LiteSubBus

    providing common axi4lite bus methods.

    Args:
        base_lib: library handler to call functions in libxavier-base.so
        _axi4_bus: file_descriptor returned by base_lib open function.
                      It could be returned by axi4_lite_open()
                      or axi4_lite_submodule_create()
    '''

    def __init__(self, base_lib, _axi4_bus):
        self.base_lib = base_lib
        self._axi4_bus = _axi4_bus

    def get_ipcore_id(self):
        '''
        AXI4LiteBus get ipcore id.

        Returns:
            int, [0~0xFF], the ipcore id.

        '''
        reg_value = self.read_32bit_inc(AXI4Def.IPCORE_INFO_ADDR, 1)[0]
        return (reg_value & 0xFF)

    def get_ipcore_version(self):
        '''
        AXI4LiteBus get ipcore version.

        Returns:
            int, [0~0xFF], the ipcore version.

        '''
        reg_value = self.read_32bit_inc(AXI4Def.IPCORE_INFO_ADDR, 1)[0]
        return (reg_value >> 16) & 0xFF

    def get_ipcore_board_id(self):
        '''
        AXI4LiteBus get ipcore board id.

        Returns:
            int, [0~0xFF], the board id in ipcore hold.

        '''
        reg_value = self.read_32bit_inc(AXI4Def.IPCORE_INFO_ADDR, 1)[0]
        return (reg_value >> 8) & 0xFF

    def check_ipcore_id(self, ipcore_id):
        '''
        AXI4LiteBus check ipcore id.

        Args:
            ipcore_id:    int, [0~0xFF], the ipcore id to be expected.

        '''
        value = self.get_ipcore_id()
        if ipcore_id != value:
            raise AXI4LiteBusException(self._dev_name,
                                       "Check ipcore ID failed. ipcore ID is 0x{:02x}\
                                       , expected ipcore ID is {:02x}".format(value, ipcore_id))

    def check_ipcore_version(self, min_version, max_version):
        '''
        AXI4LiteBus check ipcore version.

        Args:
            min_version:     int, [0~0xFF],    min ipcore version.
            max_version:     int, [0~0xFF],    max ipcore version.

        '''
        assert min_version >= 0 and min_version <= 0xFF
        assert max_version >= 0 and max_version <= 0xFF
        assert min_version < max_version
        value = self.get_ipcore_version()
        if (value < min_version) or (value > max_version):
            raise AXI4LiteBusException(self._dev_name,
                                       "Check ipcore version failed. ipcore version is 0x{:02x}.".format(value))

    def check_ipcore_board_id(self, board_id):
        '''
        AXI4LiteBus check ipcore board id failed.

        Args:
            board_id:     int, [0~0xFF],    the board id to be expected.

        '''
        assert board_id >= 0 and board_id <= 0xFF
        value = self.get_ipcore_board_id()
        if board_id != value:
            raise AXI4LiteBusException(self._dev_name,
                                       "Check board ID failed. Board ID is 0x{:02x}".format(value))

    def read_8bit_fix(self, addr, rd_len):
        '''
        AXI4LiteBus read 8bit width data from a fix address

        Args:
            addr:   hexmial, [0~0xFFFF], Read datas from this address.
            rd_len: int, [0~1024],       Length of datas to read.

        Examples:
            data = axi4_bus.read_8bit_fix(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and addr < self._reg_size
        assert rd_len > 0
        rd_data = (ctypes.c_ubyte * rd_len)()
        result = self.base_lib.axi4_lite_read_8bit_fix(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dB' % rd_len, rd_data))

    def write_8bit_fix(self, addr, data):
        '''
        AXI4LiteBus write 8bit width data to fix address

        Args:
            addr:   hexmial, [0~0xFFFF], Read datas from this address.
            data:   list, Datas to be write.

        Examples:
             axi4_bus.write_8bit_fix(0x00, [0x01, 0x02, 0x03])

        '''
        assert addr >= 0 and addr < self._reg_size
        assert len(data) > 0
        wr_data = (ctypes.c_ubyte * len(data))(*data)
        result = self.base_lib.axi4_lite_write_8bit_fix(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def read_16bit_fix(self, addr, rd_len):
        '''
        AXI4LiteBus read 16bit width data from a fix address

        Args:
            addr:   hexmial, [0~0xFFFF],  Read datas from this address.
            rd_len: int, [0~1024],        Length of datas to read.

        Examples:
            data = axi4_bus.read_16bit_fix(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and addr < self._reg_size
        assert rd_len > 0
        rd_data = (ctypes.c_ushort * rd_len)()
        result = self.base_lib.axi4_lite_read_16bit_fix(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dH' % rd_len, rd_data))

    def write_16bit_fix(self, addr, data):
        '''
        AXI4LiteBus write 16bit width data to fix address

        Args:
            addr:   hexmial, [0~0xFFFF],  Read datas from this address.
            data:   list,                 Datas to be write.

        Examples:
            axi4_bus.write_16bit_fix(0x00, [0x0001, 0x0002, 0x0003])

        '''
        assert addr >= 0 and addr < self._reg_size
        assert len(data) > 0
        wr_data = (ctypes.c_ushort * len(data))(*data)
        result = self.base_lib.axi4_lite_write_16bit_fix(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def read_32bit_fix(self, addr, rd_len):
        '''
        AXI4LiteBus read 32bit width data from a fix address

        Args:
            addr:   hexmial, [0~0xFFFF],  Read datas from this address.
            rd_len: int, [0~1024],        Length of datas to read.

        Examples:
            data = axi4_bus.read_32bit_fix(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and addr < self._reg_size
        assert rd_len > 0
        rd_data = (ctypes.c_uint * rd_len)()
        result = self.base_lib.axi4_lite_read_32bit_fix(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dI' % rd_len, rd_data))

    def write_32bit_fix(self, addr, data):
        '''
        AXI4LiteBus write 32bit width data to fix address

        Args:
            addr:   hexmial, [0~0xFFFF],  Read datas from this address.
            data:   list,                 Datas to be write.

        Examples:
            axi4_bus.write_32bit_fix(0x00, [0x00000001, 0x00000002, 0x00000003])

        '''
        assert addr >= 0 and addr < self._reg_size
        assert len(data) > 0
        wr_data = (ctypes.c_uint * len(data))(*data)
        result = self.base_lib.axi4_lite_write_32bit_fix(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def read_8bit_inc(self, addr, rd_len):
        '''
        AXI4LiteBus read 8bit width data from an increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            rd_len:  int, [0~1024],        Length of datas to read.

        Examples:
            data = axi4_bus.read_8bit_inc(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and (addr + rd_len <= self._reg_size)
        assert rd_len > 0
        rd_data = (ctypes.c_ubyte * rd_len)()
        result = self.base_lib.axi4_lite_read_8bit_inc(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dB' % rd_len, rd_data))

    def write_8bit_inc(self, addr, data):
        '''
        AXI4LiteBus write 8bit width data to increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            data:    list,                 Datas to be write.

        Examples:
            axi4_bus.write_8bit_inc(0x00, [0x01, 0x02, 0x03])

        '''
        assert addr >= 0 and (addr + len(data)) <= self._reg_size
        assert len(data) > 0
        wr_data = (ctypes.c_ubyte * len(data))(*data)
        result = self.base_lib.axi4_lite_write_8bit_inc(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def read_16bit_inc(self, addr, rd_len):
        '''
        AXI4LiteBus read 16bit width data from an increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            rd_len:  int, [0~1024],        Length of datas to read.

        Examples:
            data = axi4_bus.read_16bit_inc(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and (addr + rd_len * 2 <= self._reg_size)
        assert rd_len > 0
        rd_data = (ctypes.c_ushort * rd_len)()
        result = self.base_lib.axi4_lite_read_16bit_inc(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dH' % rd_len, rd_data))

    def write_16bit_inc(self, addr, data):
        '''
        AXI4LiteBus write 16bit width data to increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            data:    list,                 Datas to be write.

        Examples:
            axi4_bus.write_16bit_inc(0x00, [0x0001, 0x0002, 0x0003])

        '''
        assert addr >= 0 and (addr + len(data) * 2 <= self._reg_size)
        assert len(data) > 0
        wr_data = (ctypes.c_ushort * len(data))(*data)
        result = self.base_lib.axi4_lite_write_16bit_inc(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def read_32bit_inc(self, addr, rd_len):
        '''
        AXI4LiteBus read 32bit width data from an increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            rd_len:  int, [0~1024],        Length of datas to read.

        Examples:
            data = axi4_bus.read_32bit_inc(0x00, 3)
            print(data)

        '''
        assert addr >= 0 and (addr + rd_len * 4 <= self._reg_size)
        assert rd_len > 0
        rd_data = (ctypes.c_uint * rd_len)()
        result = self.base_lib.axi4_lite_read_32bit_inc(self._axi4_bus, addr, rd_data, rd_len)
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return list(struct.unpack('%dI' % rd_len, rd_data))

    def write_32bit_inc(self, addr, data):
        '''
        AXI4LiteBus write 32bit width data to increment address

        Args:
            addr:    hexmial, [0~0xFFFF],  Read datas from this address.
            data:    list,                 Datas to be write.

        Examples:
            axi4_bus.write_32bit_inc(0x00, [0x00000001, 0x00000002, 0x00000003])

        '''
        assert addr >= 0 and (addr + len(data) * 4) <= self._reg_size
        assert len(data) > 0
        wr_data = (ctypes.c_uint * len(data))(*data)
        result = self.base_lib.axi4_lite_write_32bit_inc(self._axi4_bus, addr, wr_data, len(data))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)

    def get_ipcore_ver(self):
        '''
        AXI4LiteBus get ipcore version

        Examples:
            version = axi4_bus.get_ipcore_ver()
            print(version)

        '''
        content = (ctypes.c_char * 128)()
        result = self.base_lib.axi4_lite_get_ipcore_version(self._axi4_bus, content, len(content))
        if result != 0:
            raise AXI4LiteBusException(self._dev_name, result)
        return content


class AXI4LiteBus(object):
    '''
    Singleton wrapper of AXILiteBus

    ClassType = AXI4LiteBus

    Judging from dev_name; return existing object if dev_name is already created
    because creating instance for same device with different reg_size
    is not expected, if reg_size is not the same as existing one,
    Exception will be raised.

    Args:
        dev_name: AXI4 lite bus device file name, like /dev/MIX_I2C_0
        reg_size: register size reserved for device, like 256

    '''
    # class variable to host all devices that has been created
    devices = {}

    def __new__(self, dev_name, reg_size):
        if dev_name in AXI4LiteBus.devices:
            existing_reg_size = AXI4LiteBus.devices[dev_name]['reg_size']
            if reg_size != existing_reg_size:
                msg = 'Trying to create {} instance with different reg_size {} & {}'
                raise Exception(msg.format(dev_name, reg_size, existing_reg_size))
            else:
                # use existing instance
                return AXI4LiteBus.devices[dev_name]['instance']
        else:
            # not created before; create a new instance
            instance = _AXI4LiteBus(dev_name, reg_size)
            AXI4LiteBus.devices[dev_name] = {
                'reg_size': reg_size,
                'instance': instance
            }
        return instance


class _AXI4LiteBus(AXI4LiteBusBase):
    '''
    AXILiteBus for loose IP core

    ClassType = AXI4LiteBus

    Created from char devices in /dev, like /dev/MIX_SysReg_0.

    Args:
        dev_name: string, full char device file path,
                             like '/dev/MIX_SysReg_0'
                             If None, will create emulator.
        reg_size: int, max bytes of IP Core memory map.
                          Could be get from IP Core spec.
    '''
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        if dev_name is not None:
            base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        else:
            base_lib = AXI4LiteBusLibEmulator()

        _axi4_bus = base_lib.axi4_lite_open(self._dev_name, self._reg_size)
        if _axi4_bus == 0:
            raise AXI4LiteBusRunTimeException('Open AXI4 lite device %s failue.' % (self._dev_name))
        super(_AXI4LiteBus, self).__init__(base_lib, _axi4_bus)

    def __del__(self):
        if hasattr(self, 'base_lib'):
            self.close()

    def close(self):
        '''
        AXI4LiteBus close device

        Examples:
            axi4_bus.close()

        '''
        self.base_lib.axi4_lite_close(self._axi4_bus)


class AXI4LiteSubBus(AXI4LiteBusBase):

    '''
    AXI4LiteSubBus Driver

    ClassType = AXI4LiteBus

    Args:
        axi4_bus: AXI4 lite bus
        offset_addr: AXI4 lite bus offset addr
        reg_size: register size reserved for device

    Examples:
        axi4_bus = AXI4LiteBus('/dev/AXI4_BUS_0')
        spi_axi4_bus = AXI4LiteSubBus(axi4_bus, 0x4000, 8192)

    '''
    def __init__(self, axi4_bus, offset_addr, reg_size):

        self.axi4_bus = axi4_bus
        self._dev_name = axi4_bus._dev_name
        self._offset_addr = offset_addr
        self._reg_size = reg_size
        base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')

        _axi4_bus = base_lib.axi4_lite_submodule_create(self.axi4_bus._axi4_bus,
                                                        self._offset_addr, self._reg_size)
        if _axi4_bus == 0:
            msg = 'Open AXI4 lite sub device %s failue.' % (self._axi4_bus)
            raise AXI4LiteBusRunTimeException(msg)

        super(AXI4LiteSubBus, self).__init__(base_lib, _axi4_bus)

    def __del__(self):
        if hasattr(self, 'base_lib'):
            self.close()

    def close(self):
        '''
        AXI4LiteSubBus close device

        Examples:
            axi4_sub_bus.close()

        '''
        self.base_lib.axi4_lite_submodule_destroy(self._axi4_bus)
