"""@package docstring
bus/swd provides basic shims to SWD register access.
"""
from struct import *
import fcntl
import os
import time
import sys
import mmap

class SWD_OPS_Def:
    ENABLE_DBGFIFO        = 0x40045700
    READ_CHIPID           = 0x00005701
    CONNECT_DOCKCH        = 0x00005702
    DBGFIFO_READ          = 0x00005703
    DBGFIFO_WRITE         = 0x00005704
    DBGFIFO_GET_ACTIVE_CH = 0x80045705
    SWD_MODE              = 0x40045706
    SWD_CLK_FREQ          = 0x40045707
    SWD_RESET             = 0x40045708
    SWD_AP_READ           = 0xc00c5709
    SWD_AP_WRITE          = 0xc00c570a
    SWD_DP_READ           = 0xc008570b
    SWD_DP_WRITE          = 0xc008570c
    JTAG2SWD              = 0x0000570d
    SWD_MEMAP_READ        = 0xc014570e
    SWD_MEMAP_WRITE       = 0xc014570f
    SWD_MEMAP_BLK_READ    = 0xc0145710
    SWD_MEMAP_BLK_WRITE   = 0xc0145711
    SWD_LINE_RESET        = 0x00005712

class SWD(object):

    rpc_public_api = [
        'open', 'close', 'line_reset', 'reset_connected_device', 'dp_read', 'dp_write', 'ap_read', 'ap_write',
        'set_freq', 'get_freq',  # move as property?
        'jtag2swd',
        'memap_read', 'memap_write', 'memap_blk_read', 'memap_blk_write',
    ]

    def __init__(self, dev_name):
        assert dev_name != None 
        assert os.path.exists(dev_name)        
        self.dev_name = dev_name
        self.fd = None
        self.mm = None

    def open(self):
        """
        open file handle the SWD interface.  Access is exclusive, so other services
        such as Dock Channle, or SWDProgrammer, cannot simultaneously use the same
        interface.

        :param dev_name:    string.  /dev device path to SWD interface.
        """
        assert self.dev_name != None 
        assert os.path.exists(self.dev_name)        
        if (self.fd):
            self.close()
        
        # use os.open(), instead of open() so fd can be digested by fcntl.ioctl().
        self.fd = os.open(self.dev_name, os.O_RDWR|os.O_EXCL)

        # The current application uses max size of 256 words.  So double that for now.
        #
        # Kernel driver max possible space is DBGFIFO_BUFFER_SZ(2048)*4.  However,
        # we want to consider reducing that in the DockChannel2 Driver, where dockchannel
        # buffer will no longer pass through mmap, and this will become the only mmap usecase.
        self.mm = mmap.mmap(self.fd, 512*4)
        
    def close(self):
        """
        close file handle to SWD interface.  Call close() so other services may use
        the interface.
        """
        if (self.mm):
            self.mm.close()
        if (self.fd):
            os.close(self.fd)
        self.fd = None
        self.mm = None

    def reset_connected_device(self, value):
        """
        Control the RST line provided by the SWD IP.
        This is NOT the SWD Line Reset sequence as ARM spec 4.4.3.  This is a
        physical reset pin control, typically used by device programming.
        
        :param state:   int(0,1).   Assert(1) or Deassert(0) the reset line.        
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        return fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_RESET, pack('i',value))

    def line_reset(self):
        return fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_LINE_RESET)

    def jtag2swd(self):
        """
        Send the SWD JTAG2SWD sequence, per ARM spec 5.2.1.
            Send at least 50 SWCLKTCK cycles with SWDIOTMS HIGH.
            Send the 16-bit JTAG-to-SWD select sequence (0x79E7 MSB first) on SWDIOTMS
            Send at least 50 SWCLKTCK cycles with SWDIOTMS HIGH.
        """
        return fcntl.ioctl(self.fd, SWD_OPS_Def.JTAG2SWD)

    def dp_read(self, reg):
        """
        dp_read - DP register read.
        
        :param reg:     int         DP Register Address

        :return:        read value on success.  RAISE exception on SWD Error
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'

        r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_DP_READ, pack('II', reg, 0))
        return unpack('II', r)[1]

    def dp_write(self, reg, value):
        """
        dp_write - DP register write.

        :param reg:     int         DP Register address
        :param value:   uint        Value to write

        :return:        0 on success.  0xffffffff on error.
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'

        r = None
        try:
            r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_DP_WRITE, pack('II', reg, value))
        except:
            return 0xffffffff
            
        return 0

    def ap_read(self, apsel, address):
        """
        ap_read - AP register read.
        

        :param apsel:   int         APSEL.  AP to access
        :param address: int         address to read.

        :return:        read value on success.  RAISE exception on SWD Error
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_AP_READ, pack('III', apsel, address, 0))
        return unpack('III', r)[2]

    def ap_write(self, apsel, address, value):
        """
        ap_write - AP register write.

        :param apsel:   int         APSEL.  AP to access.
        :param address: int         address to read.
        :param value:   int         value to write.

        :return:        0 on success.  0xffffffff on error.
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'

        r = None
        try:
            r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_AP_WRITE, pack('III', apsel, address, value))
        except:
            return 0xffffffff

        return 0

    def memap_read(self, apsel, address, csw=None):
        """
        memap_read - MEM-AP Read access
        

        :param apsel:   int         APSEL.  AP to access
        :param address: int         memory address to read.
        :param csw:     int(optional) the AP's CSW register value.

        :return:        read value on success.  RAISE exception on SWD Error
        """

        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        use_csw = 0
        if (csw is not None):
            use_csw = 1
        _csw = csw if (csw is not None) else self.ap_read(apsel, 0)
        r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_MEMAP_READ, pack('IIIII', apsel, address, 0, _csw, use_csw))

        return unpack('IIIII', r)[2]

    def memap_write(self, apsel, address, value, csw=None):
        """
        memap_write - MEM-AP Write access

        :param apsel:   int         APSEL.  AP to access.
        :param address: int         memory address to read.
        :param value:   int         value to write.
        :param csw:     int(optional) the AP's CSW register value.

        :return:        0 on success.  0xffffffff on error.
        """

        # we can't call memap_blk_write(count=1) anymore since it's using hardcoded
        # CSW for different transaction

        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        use_csw = 0
        if (csw is not None):
            use_csw = 1
        _csw = csw if (csw is not None) else self.ap_read(apsel, 0)
        r = None
        try:
            r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_MEMAP_WRITE, pack('IIIII', apsel, address, value, _csw, use_csw))
        except:
            return 0xffffffff

        return 0

    def memap_blk_read(self, apsel, address, count, csw=None):
        """
        memap_blk_read - MEM-AP Block Read access
        

        :param apsel:   int         APSEL.  AP to access
        :param address: int         memory address to read.
        :param csw:     int(optional) the AP's CSW register value.

        :return:        read value on success.  RAISE exception on SWD Error
        """

        # Ideally this would be all done in kernel driver.  However copying arbitrary
        # large amount of buffer over to kernel seems to be a waste, and dangerous?
        # We'd need a proper method to handle memory transfer, since this driver
        # is soley using ioctl structure, which doesn't carry memory block well.

        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        
        if (csw == None):
            # force CSW's AddrInc and Size
            CSW_Size    = 0 << 0 
            CSW_AddrInc = 2 << 4
            csw = self.ap_read(apsel, 0)
            csw &= 0xffffffc8 
            csw |= (CSW_Size | CSW_AddrInc)

        self.ap_write(apsel, 0, csw)
        time.sleep(0.001)   # B298 hang patch per Peggy

        self.ap_write(apsel, 4, address)
        time.sleep(0.001)   # B298 hang patch per Peggy

        rv = []
        for i in range(count):
            rv.append(self.ap_read(apsel, 0xc))

        return rv

    def memap_blk_write(self, apsel, address, count, values, csw=None):
        """
        memap_blk_write - MEM-AP Block Write access

        Batch write a block of data to memeory, with starting address and auto-address-increment

        :param apsel:   int         APSEL.  AP to access.
        :param address: int         memory address to read.
        :param count:   int         number of 32bit words to write
        :param values:  int         a list of uint_32 words
        :param csw:     int(optional) the AP's CSW register value.
        :return:        0 on success.  0xffffffff on error.
        """

        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        assert len(values) > 0, '"values" list length is 0!'
        assert count > 0, 'count is zero?'

        assert count <= 512, 'count greater than 512 is not supported..'

        # Send data to shared memory 
        bytestring = ""
        for value in values:
            bytestring += pack("I", value)
        self.mm.seek(0)
        self.mm.write(bytestring)

        use_csw = 0
        if (csw is not None):
            use_csw = 1
        _csw = csw if (csw is not None) else self.ap_read(apsel, 0)

        r = None
        try:
            r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_MEMAP_BLK_WRITE, pack('IIIII',  apsel, address, _csw, use_csw, count))
        except:
           return 0xffffffff
        return 0

    def set_freq(self, value):
        """
        set_freq - Set SWD Clock Frequency.  Because of SWD IP uses clock divider
        internally, the actual clock set may not be exact as specified.
        
        :param value:   int         The frequency value, in hz.
        """
        assert self.fd != None, 'SWD not open.  Make sure to call open() before.'
        r = fcntl.ioctl(self.fd, SWD_OPS_Def.SWD_CLK_FREQ, pack('I', value))
        return unpack('I', r)   # not sure about this...

    def get_freq(self, value):
        """
        get_freq - NOT IMPLEMENTED YET...
        """
        assert False, 'SWD get_freq not implemented.'
        return -1

