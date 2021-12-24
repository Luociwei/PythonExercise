# -*- coding: utf-8 -*-
import time
from compiler.ast import flatten
from threading import Lock
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLI2CDef, AXI4Def

__author__ = 'liliang@SmartGiant'
__version__ = '0.1'


class MIXI2CSGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


def lock(f):
    '''
    decorator to add lock around wrapped function
    '''
    def wrapper(self, *args, **kwargs):
        self.lock.acquire()
        try:
            ret = f(self, *args, **kwargs)
        finally:
            self.lock.release()
        return ret

    return wrapper


class MIXI2CSG(object):
    '''
    Singleton wrapper of MIXI2CSG.

    ClassType = I2C

    This is to ensure only 1 instance will be created for the same
    char device in /dev, even when instantiated multiple times.
    It is to solve problem when profile define multiple instance
    for the same /dev/MIX_I2C_x and use them in prallel in threadpool (multi-dut),
    there will be i2c _transfer() failure reporting "receive buffer not empty".
    Singleton in AXI4LiteBus ensure the same '/dev/MIX_I2C_0' will
    have singleton axi4litebus instance;
    Here we ensure the same axi4_bus instance will have singleton i2c bus instance.

    Args:
        axi4_bus:  instance(AXI4LiteBus)/None, Class instance of axi4 bus,
                                               if not using this parameter, will create emulator.
        speed_hz:  int, [1~400000], unit Hz, default 400000, pl i2c bus speed.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_I2C', 256)
        i2c = MIXI2CSG(axi4_bus)

    '''
    # class variable to host all i2c bus instances created
    instances = {}

    def __new__(cls, axi4_bus, speed_hz=PLI2CDef.DEFAULT_RATE):
        if axi4_bus in cls.instances:
            # use existing instance
            return cls.instances[axi4_bus]
        else:
            # not created before; create a new instance
            instance = _MIXI2CSG(axi4_bus, speed_hz)
            cls.instances[axi4_bus] = instance
        return instance


class _MIXI2CSG(object):
    '''
    MIXI2CSG function class

    Args:
        axi4_bus:  instance(AXI4LiteBus)/None, Class instance of axi4 bus,
                                               if not using this parameter, will create emulator.
        speed_hz:  int,[1~400000], unit Hz, default 400000, pl i2c bus speed.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_I2C', 256)
        i2c = MIXI2CSG(axi4_bus)

    '''

    rpc_public_api = ['get_speed', 'set_speed', 'read', 'write', 'write_and_read', 'get_cache_size']

    def __init__(self, axi4_bus=None, speed_hz=PLI2CDef.DEFAULT_RATE):
        if axi4_bus is None:
            self._axi4_bus = AXI4LiteBusEmulator("mix_i2c_sg_emulator", PLI2CDef.REG_SIZE)
        else:
            self._axi4_bus = axi4_bus

        self._dev_name = self._axi4_bus._dev_name
        self.lock = Lock()
        self._speed_hz = speed_hz

        self.open()

    def open(self):
        '''
        PLI2CBus open device, init has called once.

        Examples:
            i2c.open()

        '''
        self.set_speed(self._speed_hz)
        self._cache_size = self._axi4_bus.read_16bit_inc(PLI2CDef.BUF_SIZE_REGISTER, 1)[0]

    def enable(self):
        '''
        MIXI2CSG enable bus

        Examples:
            i2c.enable()

        '''
        self._axi4_bus.write_8bit_inc(PLI2CDef.CONFIG_REGISTER, [PLI2CDef.RESET_CMD])
        self._axi4_bus.write_8bit_inc(PLI2CDef.CONFIG_REGISTER, [PLI2CDef.ENABLE_CMD])

    def disable(self):
        '''
        MIXI2CSG disable bus

        Examples:
            i2c.disable()

        '''
        self._axi4_bus.write_8bit_inc(PLI2CDef.CONFIG_REGISTER, [PLI2CDef.RESET_CMD])

    @lock
    def _transfer(self, tf_data):
        '''
        To write datas into AXI4 lite bus and then read datas from it

        Args:
            tf_data:    list, Data to be transfered.

        Examples:
            i2c.transfer([0x01,0x02])

        '''
        assert len(tf_data) <= self._cache_size * 2

        tx_remain = self._axi4_bus.read_8bit_inc(PLI2CDef.TX_COUNT_REGISTER, 1)[0]
        if tx_remain > 0:
            self.enable()
            msg = 'Transfer failure because send buffer is not empty ({})!'.format(tx_remain)
            raise MIXI2CSGException(self._dev_name, msg)

        rx_remain = self._axi4_bus.read_8bit_inc(PLI2CDef.RX_COUNT_REGISTER, 1)[0]
        if rx_remain > 0:
            self.enable()
            msg = 'Transfer failure because receive buffer is not empty ({})!'.format(rx_remain)
            raise MIXI2CSGException(self._dev_name, msg)

        wr_data = [tf_data[i] | (tf_data[i + 1] << 8) for i in range(0, len(tf_data), 2)]

        self._axi4_bus.write_16bit_fix(PLI2CDef.TX_BUF_REGISTER, wr_data)

        now = time.time()
        while time.time() < now + AXI4Def.AXI4_TIMEOUT:
            recv_len = self._axi4_bus.read_8bit_inc(PLI2CDef.RX_COUNT_REGISTER, 1)[0]
            if recv_len == len(tf_data) / 2:
                break
            time.sleep(AXI4Def.AXI4_DELAY)
        if time.time() >= now + AXI4Def.AXI4_TIMEOUT:
            self.enable()
            raise MIXI2CSGException(self._dev_name, 'Wait for response timeout in transfer process!')

        rd_data = self._axi4_bus.read_16bit_fix(PLI2CDef.RX_BUF_REGISTER, recv_len)

        return flatten([(rd_data[i] & 0xff, (rd_data[i] >> 8) & 0xff) for i in range(recv_len)])

    def get_speed(self):
        '''
        PLI2C get transmit baudrate

        Returns:
            int, value, transmit baudrate.

        Examples:
            rate = i2c.get_speed()
            print(rate)

        '''
        config_data = self._axi4_bus.read_32bit_inc(PLI2CDef.FREQ_REGISTER, 1)[0]
        return int(config_data * AXI4Def.AXI4_CLOCK / (8 * pow(2, 32)))

    def set_speed(self, freq):
        '''
        MIXI2CSG set transmition baudrate

        Args:
            freq:   float, [0~2000000], I2C bus baudrate.

        Examples:
            i2c.set_speed(100000)

        '''
        assert freq > 0 and (freq <= PLI2CDef.DEFAULT_MAX_RATE)
        self.disable()
        bit_rate_ctrl = freq * 8 * pow(2, 32) / AXI4Def.AXI4_CLOCK
        self._axi4_bus.write_32bit_inc(PLI2CDef.FREQ_REGISTER, [int(bit_rate_ctrl)])
        self.enable()

    def read(self, addr, data_len):
        '''
        MIXI2CSG read specific length datas

        Args:
            addr:       hexmical, [0~0xFF], read data from this address.
            data_len:   int, [0~1024], length of datas to read.

        Returns:
            list, [value], specific length datas.

        Examples:
            datas = i2c.read(0x00, 3)
            print(datas)

        '''
        assert addr >= 0 and addr <= 0xFF
        assert data_len > 0 and data_len <= self._cache_size

        send_data = [(addr << 1) | PLI2CDef.READ_FLAG, PLI2CDef.SEND_START_CMD]

        for i in range(data_len - 1):
            send_data.append(PLI2CDef.DUMMY_DATA)
            send_data.append(PLI2CDef.SEND_ACK_CMD)
        send_data.append(PLI2CDef.DUMMY_DATA)
        send_data.append(PLI2CDef.SEND_NACK_STOP_CMD)
        recv_data = self._transfer(send_data)

        for ack in recv_data[0:(len(recv_data) - 2)][1::2]:
            if ack & PLI2CDef.IS_NACK_FLAG == PLI2CDef.IS_NACK_FLAG:
                msg = 'Read address %x failue, with NACK flag in response data.' % addr
                raise MIXI2CSGException(self._dev_name, msg)

        result_data = recv_data[2:len(recv_data)][::2]

        return result_data

    def write(self, addr, data):
        '''
        MIXI2CSG write datas to address

        Args:
            address:    hexmial, [0~0xFF], write datas to this address.
            data:       list, datas to be write.

        Examples:
            i2c.write(0x00, [0x01, 0x02, 0x03])

        '''
        assert addr >= 0 and addr <= 0xFF
        assert len(data) > 0

        send_list = [addr << 1, PLI2CDef.SEND_START_CMD]
        for i in range(len(data) - 1):
            send_list.append(data[i])
            send_list.append(PLI2CDef.WAIT_ACK_CMD)
        send_list.append(data[-1])
        send_list.append(PLI2CDef.WAIT_ACK_STOP_CMD)

        recv_data = self._transfer(send_list)

        for ack in recv_data[0:(len(recv_data) - 2)][1::2]:
            if ack & PLI2CDef.IS_NACK_FLAG == PLI2CDef.IS_NACK_FLAG:
                msg = 'Write address %x failue, with NACK flag in response data.' % addr
                raise MIXI2CSGException(self._dev_name, msg)

    def write_and_read(self, addr, wr_data, rd_len):
        '''
        MIXI2CSG write datas and then read specific length datas

        Args:
            addr:       hexmial, [0-0xFF], write to and read from this address.
            wr_data:    list, datas to be write.
            rd_len:     int, [0-1024], length of datas to be read.

        Returns:
            list, [value], specific length datas.

        Examples:
            datas = i2c.write_and_read(0x00, [0x01, 0x02, 0x03], 2)
            print(datas)

        '''
        assert addr >= 0 and addr <= 0xFF
        assert rd_len > 0 and rd_len <= self._cache_size

        send_list = [addr << 1, PLI2CDef.SEND_START_CMD]
        [send_list.extend([wr_data[i], PLI2CDef.WAIT_ACK_CMD]) for i in range(len(wr_data))]

        send_list.extend([(addr << 1) | PLI2CDef.READ_FLAG, PLI2CDef.SEND_START_CMD])
        [send_list.extend([PLI2CDef.DUMMY_DATA, PLI2CDef.SEND_ACK_CMD]) for i in range(rd_len - 1)]
        send_list.append(PLI2CDef.DUMMY_DATA)
        send_list.append(PLI2CDef.SEND_NACK_STOP_CMD)

        recv_data = self._transfer(send_list)

        for ack in recv_data[0:(len(recv_data) - 2)][1::2]:
            if ack & PLI2CDef.IS_NACK_FLAG == PLI2CDef.IS_NACK_FLAG:
                msg = 'Write and read address %x failue, with NACK flag in response data.' % addr
                raise MIXI2CSGException(self._dev_name, msg)

        result_data = recv_data[::2][(len(wr_data) + 2):len(recv_data)]

        return result_data

    def get_cache_size(self):
        '''
        MIXI2CSG get cache size

        Returns:
            int, value, get cache size.

        Examples:
            cache_size = i2c.cache_size
            print(cache_size)

        '''
        return self._cache_size
