from datetime import datetime
import hashlib
from collections import OrderedDict


class WriteCalibrationError(RuntimeError):
    def __init__(self, msg, old_header=None, old_data=None):
        super(WriteCalibrationError, self).__init__(msg)
        self.old_header = old_header
        self.old_data = old_data


class MIXModuleDriver(object):
    # this is a list of the compatible string, the driver
    # should support an instrument if it matches any string in the compatible
    # string list. If a compatile string finds a match in two driver's list,
    # the launcher's behavior is undefined
    compatible = []
    # this is the list of names of public functions that are exposed to RPC clients
    rpc_public_api = []

    # the adddress for the number of cal data blocks
    NUMBER_OF_CAL_ADDR = 0x18

    FIRST_CAL_DATETIME_ADDR = 0x40
    FIRST_CAL_START_ADDR_ADDR = 0x49
    FIRST_CAL_SIZE_ADDR = 0x4d
    FIRST_CAL_CHKSUM_ADDR = 0x51
    # todo: update HEADER_CHKSUM_ADDR = 0xAF
    CAL_DATETIME_SIZE = 9
    CAL_ADDR_SIZE = 4
    CAL_SIZE_SIZE = 4
    CHKSUM_SIZE = 20
    CAL_HEADER_SIZE = CAL_DATETIME_SIZE + CAL_ADDR_SIZE + CAL_SIZE_SIZE + CHKSUM_SIZE

    def pre_power_on_init(self, timeout=0):
        '''
        This is where the driver sets up all the IO pins to make sure nothing
        gets damaged when power is applied.
        '''
        return

    def post_power_on_init(self, timeout=0):
        '''
        This is where you initialized the hardware after power on.
        '''
        return

    def reset(self, timeout=0):
        '''
        after reset everything goes to a known state. A driver must
        implement this function.
        This function could be called anytime and should behave correctly.
        if timeout is 0, it means no timeout. Otherwise, the unit of time
        out is seconds
        '''
        raise NotImplementedError("reset is not implemeted")

    def pre_power_down(self, timeout=0):
        '''
        This function is called by the system before removing power to
        the module. After this functionreturns, it should be safe to
        physically unplug the module
        '''
        return

    def get_driver_version(self):
        raise NotImplementedError("version is not specified in %s"
                                  % (self.__class__.__name__)
                                  )
        # really the pythonic way is to make version a read-only property.
        # However that doesn't travel well across the wire in RPC.
        # Also this seems to be the only way for property to pick up
        # functions defined in derived classes.
    driver_version = property(fget=lambda self: self.get_driver_version())

    def read_nvram(self, addr, count):
        '''
        this should return a bytearray object representing the data
        '''
        raise NotImplementedError("No concrete implmenetation for reading NVRAM in this driver")  # noqa

    def write_nvram(self, address, data):
        '''
        data should be a byte array object
        '''
        raise NotImplementedError("No concerte implmenetation for writing NVRAM in this driver")  # noqa

    def read_vendor(self):
        '''
        returns the vendor code
        '''
        return str(self.read_nvram(0x03, 3))
    vendor = property(fget=lambda self: self.read_vendor())

    def read_EEEE_code(self):
        '''
        returns the EEEE code. This is an Apple assigned number that uniquely identifies
        this type of modules
        '''
        return str(self.read_nvram(0x0e, 4))
    EEEE_code = property(fget=lambda self: self.read_EEEE_code())

    def read_hardware_version(self):
        '''
        returns an integer represneting the hardware version
        '''
        return self.read_nvram(0x12, 1)[0] - 0x30
    hardware_version = property(fget=lambda self: self.read_hardware_version())

    def read_hardware_config(self):
        '''
        returns a string that represents the config
        '''
        # TODO: wait for final decision on ICI spec
        return "".join([chr(c) for c in self.read_nvram(0x0a, 3)])
    # I have to use a Lambda here so the the child class will pick up the
    # child class's read_nvram implementation
    hardware_config = property(fget=lambda self: self.read_hardware_config())

    def read_serial_number(self):
        return "".join([chr(c) for c in self.read_nvram(0x03, 17)])
    serial_number = property(fget=lambda self: self.read_serial_number())

    def read_temperature(self):
        return -99999.0

    # ===============some helper functions====================
    def _uint_from_bytes(self, data_bytes):
        '''
        convert a little endean two bytes bytearray to uint
        '''
        return data_bytes[0] + 256 * data_bytes[1]

    def _bytes_from_uint(self, data):
        '''
        converts an uint to a two byte bytearray in the little endean format
        '''
        assert data < 65536
        b = bytearray(2)
        b[0] = data % 256
        b[1] = data / 256
        return b

    def _cal_hash(self, data):
        # is this necessary? it could be bytes in python3.
        assert isinstance(data, bytearray)
        s = hashlib.sha1()
        s.update(data)
        return bytearray(s.digest())

    def _bytes_from_date(self, d):
        date_string = d.strftime("%Y%W%w%H%M")
        date_array = bytearray(date_string[2:])
        return date_array

    def _date_from_bytes(self, date_array):
        date_string = "20" + str(date_array)
        return datetime.strptime(date_string, "%Y%W%w%H%M")

    def _get_cal_address(self, index):
        # I am not checkin if the index is valid here. it should be check against
        # the cal number in address 0x18 in the implmenation of a child class
        # check the test class ShadowModule for an example
        return self._uint_from_bytes(self.read_nvram(self.FIRST_CAL_START_ADDR_ADDR + index * self.CAL_HEADER_SIZE, self.CAL_ADDR_SIZE))

    def _get_cal_size(self, index):
        # I am not checkin if the index is valid here. it should be check against
        # the cal number in address 0x18 in the implmenation of a child class
        return self._uint_from_bytes(self.read_nvram(self.FIRST_CAL_SIZE_ADDR + index * self.CAL_HEADER_SIZE, self.CAL_SIZE_SIZE))

    def _get_cal_header_bytes(self, index):
        hbytes = self.read_nvram(self.FIRST_CAL_DATETIME_ADDR + index * self.CAL_HEADER_SIZE, self.CAL_HEADER_SIZE)
        return hbytes[:-self.CHKSUM_SIZE]

    # ====================end helper functions===================================

    def write_calibration_cell(self, cal_index, data):
        assert isinstance(data, bytearray)
        data_size = len(data)
        cal_size = self._get_cal_size(cal_index)
        if data_size != cal_size:
            raise WriteCalibrationError("cal data size should be {0:d}, data to write has size {1:d}".format(cal_size, data_size))
        start_address = self._get_cal_address(cal_index)

        try:
            # first write the data
            self.write_nvram(start_address, data)
            # then write the header
            cal_date = datetime.now()  # the cal time is auotmatically set by the software. Cal program can not cheat
            date_bytes = self._bytes_from_date(cal_date)
            self.write_nvram(self.FIRST_CAL_DATETIME_ADDR + cal_index * self.CAL_HEADER_SIZE, date_bytes)
            sha1_hash = self._cal_hash(self._get_cal_header_bytes(cal_index) + data)
            self.write_nvram(self.FIRST_CAL_CHKSUM_ADDR + cal_index * self.CAL_HEADER_SIZE, sha1_hash)
        except RuntimeError as e:
            # Now if we  have trouble writing to nvram, it doesn't make sense to
            # try to write the old data back to nvram again.
            # we will just put the old data in the exception we throw
            raise WriteCalibrationError("error writing cal cell {0:d}: {1}".format(cal_index, str(e)))

        # todo: some kind of error handling if anything goes wrong

    def read_calibration_cell(self, cal_index):
        # try:
        #     cal_date = self.read_calibration_date(cal_index)
        # except ValueError as e:
        #     raise RuntimeError("invalid cal date, probably cal block {0} is invalid".format(cal_index))
        start_address = self._get_cal_address(cal_index)
        data_size = self._get_cal_size(cal_index)
        chk_sum = self.read_nvram(self.FIRST_CAL_CHKSUM_ADDR + cal_index * self.CAL_HEADER_SIZE, self.CHKSUM_SIZE)

        data = self.read_nvram(start_address, data_size)

        data_hash = self._cal_hash(self._get_cal_header_bytes(cal_index) + data)
        if not data_hash == chk_sum:
            raise RuntimeError("cal data blob in index %d does not have valid chk sum" % (cal_index))
        else:
            return data

    def read_calibration_date(self, cal_index):
        return self._date_from_bytes(self.read_nvram(self.FIRST_CAL_DATETIME_ADDR + cal_index * self.CAL_HEADER_SIZE, self.CAL_DATETIME_SIZE))

    def erase_calibration_cell(self, cal_index):
        '''
        here we only erase the datetime and checksum
        start address and data size do not chagne in the field
        '''
        ed = [0xff] * self.CAL_DATETIME_SIZE  # only erase the datetime and checksum
        self.write_nvram(self.FIRST_CAL_DATETIME_ADDR + cal_index * self.CAL_HEADER_SIZE, bytearray(ed))
        ed = [0xff] * self.CHKSUM_SIZE
        self.write_nvram(self.FIRST_CAL_CHKSUM_ADDR + cal_index * self.CAL_HEADER_SIZE, bytearray(ed))

