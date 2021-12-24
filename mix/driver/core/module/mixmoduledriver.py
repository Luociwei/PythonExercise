from datetime import datetime
from mixmodulehelper import BytesHelper
from mixmodulenvmem import NVMemFieldNames, NVMemContent

'''
version number has three parts: major.minor.revision
If we release bug fixes or improvment, for instance, refactoring the __getitem__() algorithm,
we will update the revison number.
If we release backward compatible change, for instance, starting to support a new EEPROM map,
we will updatet the minor number
If we change the major number, that means there are changes that break the backward
compatiblility.
'''
__version__ = '1.0.0'


class MIXModuleDriver(object):
    '''
    MIXModuleDriver is the base class for MIX compatible modules.
    '''

    # --------------------------- MUST OVERRIDE ---------------------------
    # these functions and properties must be overriden by the child class

    compatible = []
    '''
    The compatible property is a list of compatible strings, which identify hardware
    supported by this driver. If a compatible string finds a match in two driver's lists,
    the launcher's behavior is undefined.
    '''

    rpc_public_api = []
    '''
    The rpc_public_api property is a list of function names to be exposed to RPC clients.
    Launcher will read this property when loading the class.
    '''

    def __init__(self):
        '''
        The constructor verifies we can access the nvmem and the read only content
        is not corrupted. The child class should override init to provide for inputs
        from profile, but must call the base init before attempting to call any base
        class functions that access the nvmem. Call the base init using
        super(<child_class>, self).__init__()
        '''
        self.nvmem = NVMemContent(self)

    def reset(self, timeout=0):
        '''
        After reset everything goes to a known state. A driver must implement this
        function. This function could be called anytime and should behave correctly.
        If timeout is 0, it means no timeout. Otherwise, the unit of time out is
        seconds
        '''
        raise NotImplementedError('reset is not implemeted')

    def read_nvmem(self, addr, count):
        '''
        Should implement the calls necessary to read the <count> number of bytes from
        nvmem starting from address <addr> and return the data as a bytearray object
        '''
        raise NotImplementedError('No concrete implementation for reading NVMEM in this driver')

    def write_nvmem(self, addr, data):
        '''
        Should implement the calls necessary to write <data> to nvmem starting from address <addr>.
        Should assume data is of the type bytearray
        '''
        raise NotImplementedError('No concrete implementation for writing NVMEM in this driver')

    def get_driver_version(self):
        '''
        Should return a string representing the version of the driver
        '''
        raise NotImplementedError('version is not specified in %s'
                                  % (self.__class__.__name__)
                                  )
    driver_version = property(fget=lambda self: self.get_driver_version())

    # ------------------------- OPTIONAL OVERRIDE -------------------------
    # these functions can be overriden if needed by the child class

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

    def pre_power_down(self, timeout=0):
        '''
        This function is called by the system before removing power to
        the module. After this function returns, it should be safe to
        physically unplug the module
        '''
        return

    # -------------------------- DO NOT OVERRIDE --------------------------
    # these functions are static base methods and should not be overriden

    def read_vendor(self):
        '''
        Returns a string representing the vendor code
        '''
        return self.nvmem[NVMemFieldNames.VENDOR]
    vendor = property(read_vendor)

    def read_EEEE_code(self):
        '''
        Returns a string representing the EEEE code. This is an Apple assigned string that
        uniquely identifies the module
        '''
        return self.nvmem[NVMemFieldNames.QUADE]
    EEEE_code = property(read_EEEE_code)

    def read_hardware_version(self):
        '''
        Returns a string representing the module revision
        '''
        return self.nvmem[NVMemFieldNames.REVISION]
    hardware_version = property(read_hardware_version)

    def read_number_supported_calibrations(self):
        '''
        Returns an integer representing the number of calibrations this module supports
        '''
        return self.nvmem[NVMemFieldNames.NUM_CALS]
    number_supported_calibrations = property(read_number_supported_calibrations)

    def read_ers_version(self):
        '''
        Returns an integer representing the ERS version the module was designed against
        '''
        return self.nvmem[NVMemFieldNames.ERS_VERSION]
    ers_version = property(read_ers_version)

    def read_hardware_config(self):
        '''
        Returns a string that represents the module config
        '''
        return self.nvmem[NVMemFieldNames.CONFIG]
    hardware_config = property(read_hardware_config)

    def read_serial_number(self):
        '''
        Returns a string that represents the module sn
        '''
        return self.nvmem[NVMemFieldNames.MODULE_SN]
    serial_number = property(read_serial_number)

    def read_nvmem_size(self):
        '''
        Returns an integer representing the size of the nvmem in Kbit
        '''
        return self.nvmem[NVMemFieldNames.STORAGE_SIZE]
    nvmem_size = property(read_nvmem_size)

    def read_production_date(self):
        '''
        Returns a python datetime object representing the date the module was manufactured.
        Resolution of timestamp is in days.
        '''
        return self.nvmem[NVMemFieldNames.PRODUCTION_DATE]
    production_date = property(read_production_date)

    def read_production_count(self):
        '''
        Returns an integer representing the production sequence count of the module
        '''
        return self.nvmem[NVMemFieldNames.SEQUENCE_COUNT]
    production_count = property(read_production_count)

    def read_latest_calibration_index(self):
        '''
        Returns the index of the "latest" calibration blob written to nvmem. Intended for use in
        class init when loading default calibration values. Multiple calibrations written within
        the same minute will return the cal in the higher index.
        '''
        date_list = []
        num_cals = self.number_supported_calibrations
        unused_date = datetime(1, 1, 1)  # earliest timestamp available
        if num_cals == 0:
            raise RuntimeError('cannot read latest cal index as module supports 0 calibrations')
        else:
            for i in range(num_cals):
                # if date hasn't been written, has been erased, or is invalid, read will return ValueError or TypeError
                try:
                    date = self.read_calibration_date(i)
                except (ValueError, TypeError):
                    date = unused_date
                date_list.append(date)
            latest_date = max(date_list)
            if latest_date == unused_date:
                raise RuntimeError('cannot read latest cal index as all indices are empty or invalid')
            else:
                date_list.reverse()  # to prioritize timestamps written in same minute in higher indices
                return num_cals - date_list.index(latest_date) - 1

    def write_calibration_cell(self, cal_index, data):
        '''
        Writes the <data> to the specified calibration index <cal_index>. <data> must be of type Bytearray
        '''
        if not isinstance(data, bytearray):
            raise RuntimeError('data passed to write_calibration_cell must be of type bytearray')
        data_size = len(data)
        cal_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][cal_index]
        if data_size != cal_size:
            details = 'cal data size should be {0:d}, data to write has size {1:d}'.format(cal_size, data_size)
            raise RuntimeError(details)
        start_address = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][cal_index]

        # write the data
        self.write_nvmem(start_address, data)
        # the cal time is automatically set by the software. Cal program can not cheat
        self.nvmem[NVMemFieldNames.CAL_DATE][cal_index] = datetime.now()
        # calculate and set the hash
        sha1_hash = BytesHelper.sha1_hash(self.nvmem.get_cal_header_bytes(cal_index) + data)
        self.nvmem[NVMemFieldNames.CAL_CHKSUM][cal_index] = sha1_hash

    def read_calibration_cell(self, cal_index):
        '''
        Reads the cal cell at index <cal_index>. Returns data of type Bytearray.
        '''
        try:
            cal_date = self.read_calibration_date(cal_index)
        except ValueError as e:
            raise RuntimeError('invalid cal date, probably cal block {0} is invalid'.format(cal_index))
        data_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][cal_index]
        start_address = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][cal_index]
        chk_sum = self.nvmem[NVMemFieldNames.CAL_CHKSUM][cal_index]

        data = self.read_nvmem(start_address, data_size)

        data_hash = BytesHelper.sha1_hash(self.nvmem.get_cal_header_bytes(cal_index) + data)
        if not data_hash == chk_sum:
            raise RuntimeError('cal data blob in index %d does not have valid chk sum' % (cal_index))
        else:
            return data

    def read_calibration_date(self, cal_index):
        '''
        Returns a python datetime object representing the date and time the calibration at index <cal_index>
        was written to nvmem. Resolution is in minutes.
        '''
        return self.nvmem[NVMemFieldNames.CAL_DATE][cal_index]

    def erase_calibration_cell(self, cal_index):
        '''
        Erases the datetime and checksum fields of the calibration at index <cal_index> by writting 0xff
        to those address ranges. Clearing these two fields invalidates the calibration and attempting
        to read this index afterwards will return an exception, even though the core cal cell data
        is still present within nvmem.
        '''
        date_addr, date_size = self.nvmem.map[NVMemFieldNames.CAL_DATE][:2]
        ed = [0xff] * date_size
        self.write_nvmem(date_addr + cal_index * self.nvmem.cal_header_size, bytearray(ed))
        chksum_addr, chksum_size = self.nvmem.map[NVMemFieldNames.CAL_CHKSUM][:2]
        ed = [0xff] * chksum_size
        self.write_nvmem(chksum_addr + cal_index * self.nvmem.cal_header_size, bytearray(ed))

    def read_user_area(self, offset, count):
        '''
        Returns data from the user area, which starts after the final calibration block. The data returned will
        be of length <count> and start from <offset>. Note, <offset> is relative to the start of the user area.
        '''
        return self.read_nvmem(self.nvmem[NVMemFieldNames.USER_START_ADDR] + offset, count)

    def write_user_area(self, offset, data):
        '''
        Writes <data> to the user area, starting from <offset>. Note, offset is relative to the start of the
        user area
        '''
        self.write_nvmem(self.nvmem[NVMemFieldNames.USER_START_ADDR] + offset, data)
