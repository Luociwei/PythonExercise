from ..ic.i2c_mux_emulator import I2CMUXEmulator
from threading import Lock

'''
I2C Downstream bus driver.
'''


def lock_i2c_mux(f):
    '''
    decorator to add lock and i2c-mux switch around wrapped function
    '''
    def wrapper(self, *args, **kwargs):
        with self.mux.mux_lock:
            self.mux.set_channel_state([[self.channel, 1]])
            try:
                ret = f(self, *args, **kwargs)
            finally:
                self.mux.set_channel_state([[self.channel, 0]])
        return ret

    return wrapper


class I2CDownstreamBus(object):
    '''
    I2C Downstream bus driverz

    ClassType = I2C

    I2C Downstream bus is the i2c bus coming from a i2c_mux's downstream channel.
    I2C master/root cannot directly talk to devices connecting to i2c downstream bus;
    A i2c mux switch is required to enable the bus beforehands.

    This driver is intended to work as a i2c bus driver but wrap mux switching action inside.
    For example, if we have a cat9555 connecting to channel 0 of i2c-mux (tca9548) on i2c bus 0,
    To read from cat9555, user software needs to do this:
        0. Create instance:
            i2c = I2C('/dev/i2c-0')
            mux = TCA9548(mux_addr, i2c)
            io_exp = CAT9555(i2c, io_exp_addr)

        1. tca9548 channel 0 enable:
            mux.enable_channel(0)
        2. read cat9555 pin:
            io_exp.get_pin(0)
        3. tca9548 channel 0 disable
            mux.disable_channel(0)
    Step 3 is required for avoid address conflict on different i2c-mux channels.

    With this driver, this could be done by less steps:
        0. Create instance:
            i2c = I2C('/dev/i2c-0')
            mux = TCA9548(mux_addr, i2c)
            i2c_ds = I2CDownStreamBus(mux, 0)
            io_exp = CAT9555(i2c_ds, io_exp_addr)
        1. read cat9555 pin:
            io_exp.get_pin(0)

    i2c-mux cascading is supported by passing a i2c-ds-bus as 1st argument of __init__().

    Args:
        mux: instance/None, a i2c mux instance that has a lock and set channel action.
                               Could be a I2CDownstreamBus instance if it is a cascading
                               i2c-mux: mux connecting to another i2c-mux's downstream channel.
        channel: int, (>0), channel number of i2c mux that this bus is coming from.

    Examples:
        # creating instance
        i2c = I2C('/dev/i2c-0')
        mux = TCA9548(mux_addr, i2c)
        i2c_ds = I2CDownStreamBus(mux, 0)

        # use i2c_ds to initiate devices
        io_exp = CAT9555(i2c_ds, io_exp_addr)

        # read cat9555 pin:
        io_exp.get_pin(0)

    '''
    rpc_public_api = ['read', 'write', 'write_and_read']
    # class lock to control lock creating action for i2c_mux;
    LOCK = Lock()

    def __init__(self, mux, channel):
        # channel must be specified int and >= 0.
        assert type(channel) is int
        assert channel >= 0

        if mux:
            self.mux = mux
        else:
            self.mux = I2CMUXEmulator(0x70, 8)

        # existing tca9548 has _i2c_bus instance.
        self.i2c = self.mux._i2c_bus
        self._dev_name = self.i2c._dev_name
        self.channel = channel

        # mux instance may not have a lock; create one if not.
        # use LOCK here to ensure only 1 lock created for the same mux.
        with I2CDownstreamBus.LOCK:
            if not hasattr(mux, 'mux_lock'):
                self.mux.mux_lock = Lock()
            else:
                # already has a lock; just use it.
                pass

    # no open() because open() is called once during i2c init.
    def close(self):
        '''
        I2C bus close; will close the root bus device.
        '''
        self.i2c.close()

    @lock_i2c_mux
    def read(self, addr, data_len):
        '''
        I2C bus read with i2c mux switching.

        Args:
            addr:        heximal, Read data from this address.
            data_len:   int, Length of data to be read.

        Returns:
            list, data of i2c bus read.

        '''
        return self.i2c.read(addr, data_len)

    @lock_i2c_mux
    def write(self, addr, data):
        '''
        I2C bus write with i2c mux switching.

        Args:
            addr:   hexmial, Write datas to this address.
            data:   list, Datas to be write.

        Returns:
            None.
        '''
        return self.i2c.write(addr, data)

    @lock_i2c_mux
    def write_and_read(self, addr, wr_data, rd_len):
        '''
        I2C bus write and read with i2c mux switching.

        Args:
            addr:       heximial.
            wr_data:    list,   datas to be write.
            rd_len:     int,    Length of data to be read.

        Returns:
            list, data of i2c bus read.
        '''
        return self.i2c.write_and_read(addr, wr_data, rd_len)
