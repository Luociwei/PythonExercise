# -*- coding: utf-8 -*-
import ctypes
import struct
import mmap


class I2CException(Exception):
    def __init__(self, dev_name, err_code):
        reason = (128 * ctypes.c_char)()
        base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        base_lib.get_error_reason(err_code, reason, len(reason))
        self._err_reason = '[%s]: %s.' % (dev_name, ctypes.string_at(reason, -1).decode("utf-8"))

    def __str__(self):
        return self._err_reason


class XIICDef:
    CTRL_REG = 0x100
    CTRL_MODULE_ENABLE = 0x01


class I2CDef:
    XIIC_TYPE = 0

    # CDNS：Cadence i2c bus，bus for the cadence i2c controller.
    # CDNS is borrowed the written by the kernel driver of PS IIC.
    CDNS_I2C_TYPE = 1


class I2C(object):
    '''
    Singleton wrapper of Xilinx I2C driver

    ClassType = I2C

    This is to ensure only 1 instance is created for the same char device
    in /dev/i2c-x, even if instantiated multiple times.
    It is to solve the problem when profile define multiple i2c instance and
    use in different DUT which run in threadpool in parallel.

    Args:
        dev_name:   string, I2C device full path like '/dev/i2c-1'

    Examples:
        i2c_1 = I2C('/dev/i2c-1')
        i2c_2 = I2C('/dev/i2c-1')
        assert i2c_1 == i2c_2          # True

    '''
    # class variable to host all i2c bus instances created.
    instances = {}

    def __new__(cls, dev_name):
        if dev_name in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _I2C(dev_name)
            cls.instances[dev_name] = instance
        return cls.instances[dev_name]


class _I2C(object):
    '''
    I2C function class

    This driver support i2c mounted to ps.

    Args:
        dev_name:   string, I2C device name.

    Examples:
        i2c = I2C('/dev/i2c-0')

        # write data to address 0x50
        i2c.write(0x50, [0x00, 0x01, 0x02])

        # read 3 bytes from address 0x50
        rd_data = i2c.read(0x50, 3)
        print(rd_data) # rd_data is a list, each item is one byte

        # write [0x00, 0x01] to 0x50 and read 3 bytes
        rd_data = i2c.write_and_read(0x50, [0x00, 0x01], 3)
        print(rd_data) # rd_data is a list, each item is one byte

    '''
    rpc_public_api = ['read', 'write', 'write_and_read']

    def __init__(self, dev_name):
        self._dev_name = dev_name
        self.mm = None
        self.i2c_type = I2CDef.CDNS_I2C_TYPE
        self.base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')

        self.open()
        # the retry_times is temporary for fix i2c read/write failed.
        self.retry_times = 3

    def __del__(self):
        self.close()

    def open(self):
        '''
        I2C open device, has been called once when init.

        Examples:
            i2c.open()

        '''
        self._i2c = self.base_lib.i2c_open(self._dev_name)
        if self._i2c == 0:
            raise RuntimeError('Open I2C device {} failure.'.format(self._dev_name))

        i2c_name = self._dev_name.split("/")[-1]

        with open("/sys/class/i2c-dev/%s/device/of_node/compatible" % i2c_name) as cmp_fd:
            cmp_fd.seek(0)
            compatible = cmp_fd.read()

            if "xlnx,xps-iic" in compatible:
                with open("/sys/class/i2c-dev/%s/device/of_node/reg" % i2c_name) as reg_fd:
                    reg_fd.seek(0)
                    data = reg_fd.read(8)
                    reg = struct.unpack("8B", data)
                    i2c_addr = reg[0] << 24 | reg[1] << 16 | reg[2] << 8 | reg[3]
                    i2c_size = reg[4] << 24 | reg[5] << 16 | reg[6] << 8 | reg[7]

                    with open("/dev/mem", "wb+") as m_fd:
                        self.mm = mmap.mmap(m_fd.fileno(), length=i2c_size, offset=i2c_addr)
                        self.i2c_type = I2CDef.XIIC_TYPE

    def close(self):
        '''
        I2C close device

        Examples:
            i2c.close()

        '''
        if self.mm:
            self.mm.close()
            self.mm = None

        self.base_lib.i2c_close(self._i2c)

    def read(self, addr, data_len):
        '''
        I2C read specific length datas from address

        Args:
            addr:        heximal, [0x0000~0xFFFF], Read data from this address.
            data_len:   int, [0~1024], Length of data to be read.

        '''
        assert addr >= 0 and addr <= 0xFF
        assert data_len > 0

        rd_data = (ctypes.c_ubyte * data_len)()

        for x in range(self.retry_times):
            result = self.base_lib.i2c_read(self._i2c, addr, rd_data, data_len)
            if result == 0:
                break
            elif (result != 0) and (x == self.retry_times - 1):
                raise I2CException(self._dev_name, result)
            elif (result != 0) and (x == self.retry_times - 2):
                if self.i2c_type == I2CDef.XIIC_TYPE:
                    self._xiic_module_disable()
                    self._xiic_module_enable()
            else:
                continue

        return list(struct.unpack('%dB' % data_len, rd_data))

    def write(self, addr, data):
        '''
        I2C write data to address

        Args:
            addr:   hexmial, [0~0xFF],  Write datas to this address.
            data:   list,               Datas to be write.
        '''
        assert addr >= 0 and addr <= 0xFF
        assert len(data) > 0
        wr_data = (ctypes.c_ubyte * len(data))(*data)

        for x in range(self.retry_times):
            result = self.base_lib.i2c_write(self._i2c, addr, wr_data, len(data))
            if result == 0:
                break
            elif (result != 0) and (x == self.retry_times - 1):
                raise I2CException(self._dev_name, result)
            elif (result != 0) and (x == self.retry_times - 2):
                if self.i2c_type == I2CDef.XIIC_TYPE:
                    self._xiic_module_disable()
                    self._xiic_module_enable()
            else:
                continue

    def write_and_read(self, addr, wr_data, rd_len):
        '''
        I2C write datas to address and read specific length datas

        Args:
            addr:       heximial, [0~0xFF].
            wr_data:    list,               datas to be write.
            rd_len:     int, [0~1024],      Length of data to be read.
        '''
        assert addr >= 0 and addr <= 0xFF
        assert len(wr_data) > 0
        assert rd_len > 0

        wr_data = (ctypes.c_ubyte * len(wr_data))(*wr_data)
        rd_data = (ctypes.c_ubyte * rd_len)()

        for x in range(self.retry_times):
            result = self.base_lib.i2c_write_and_read(self._i2c, addr, wr_data, len(wr_data), rd_data, rd_len)
            if result == 0:
                break
            elif (result != 0) and (x == self.retry_times - 1):
                raise I2CException(self._dev_name, result)
            elif (result != 0) and (x == self.retry_times - 2):
                if self.i2c_type == I2CDef.XIIC_TYPE:
                    self._xiic_module_disable()
                    self._xiic_module_enable()
            else:
                continue

        return list(struct.unpack('%dB' % rd_len, rd_data))

    def _read_32bit_fix(self, reg_offset, rd_len):
        assert self.mm

        rd_buffer = list()
        for i in range(rd_len):
            self.mm.seek(reg_offset)
            data = struct.unpack("I", self.mm.read(4))
            rd_buffer.append(data[0])

        return rd_buffer

    def _write_32bit_fix(self, reg_offset, wr_datas):
        assert self.mm

        datas = struct.pack("%dI" % len(wr_datas), *wr_datas)
        for i in range(len(datas) / 4):
            self.mm.seek(reg_offset)
            self.mm.write(datas[4 * i: 4 * i + 4])

    def _xiic_module_enable(self):
        ctrl = self._read_32bit_fix(XIICDef.CTRL_REG, 1)[0]
        ctrl |= XIICDef.CTRL_MODULE_ENABLE
        self._write_32bit_fix(XIICDef.CTRL_REG, [ctrl])

    def _xiic_module_disable(self):
        ctrl = self._read_32bit_fix(XIICDef.CTRL_REG, 1)[0]
        ctrl &= (~XIICDef.CTRL_MODULE_ENABLE)
        self._write_32bit_fix(XIICDef.CTRL_REG, [ctrl])
