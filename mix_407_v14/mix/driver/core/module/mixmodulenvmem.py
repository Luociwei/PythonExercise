import struct
from mixmodulehelper import BytesHelper


class NVMemFieldNames(object):
    STORAGE_SIZE = 0
    MODULE_SN = 1
    VENDOR = 2
    PRODUCTION_DATE = 3
    SEQUENCE_COUNT = 4
    QUADE = 5
    REVISION = 6
    ERS_VERSION = 7
    CONFIG = 8
    NUM_CALS = 9
    RO_CHKSUM = 10
    LAST_BASE_READ_ONLY = 11

    FIRST_BASE_CAL_FIELD = 101
    CAL_DATE = 101
    CAL_CHKSUM = 102
    LAST_BASE_CAL_FIELD = 103

    FIRST_MAP_SPECIFIC_FIELD = 201
    CAL_HEADER_SIZE = 201
    CAL_DATA_START_ADDR = 202
    USER_START_ADDR = 203
    CAL_DATA_SIZE = 204
    LAST_MAP_SPECIFIC_FIELD = 205


class NVMemContent(object):
    fn = NVMemFieldNames

    '''
    Keys shared across all versions should be stored in 'base'.
    Format of each key depends on its numeric value within NVMemFieldNames.
    See __getitem__ for how each set of keys is handled
    '''
    maps = {
        'base': {
            fn.STORAGE_SIZE: [0x01, 2, lambda d: struct.unpack('<H', d)[0]],
            fn.MODULE_SN: [0x03, 17, str],
            fn.VENDOR: [0x03, 3, str],
            fn.PRODUCTION_DATE: [0x06, 4, BytesHelper.sn_date_from_bytes],
            fn.SEQUENCE_COUNT: [0x0a, 4, BytesHelper.production_count_from_bytes],
            fn.QUADE: [0x0e, 4, str],
            fn.REVISION: [0x12, 1, str],
            fn.ERS_VERSION: [0x14, 1, lambda d: d[0]],
            fn.CONFIG: [0x15, 3, str],
            fn.NUM_CALS: [0x18, 1, lambda d: d[0]],
            fn.RO_CHKSUM: [0x2c, 20, lambda d: d],
            fn.CAL_DATE: [0x40, 9, BytesHelper.cal_date_from_bytes, BytesHelper.bytes_from_cal_date],
        },
        2: {
            fn.CAL_CHKSUM: [0x51, 20, lambda d: d, lambda d: d],
            fn.CAL_DATA_SIZE: lambda s: [BytesHelper.uint_from_bytes(s.reader.read_nvmem(x, 4)) for x in
                                         range(0x4D, 0x4D + s[s.fn.NUM_CALS] * s[s.fn.CAL_HEADER_SIZE],
                                         s[s.fn.CAL_HEADER_SIZE])],
            fn.CAL_HEADER_SIZE: lambda s: 0x25,
            fn.CAL_DATA_START_ADDR: lambda s: [BytesHelper.uint_from_bytes(s.reader.read_nvmem(x, 4)) for x in
                                               range(0x49, 0x49 + s[s.fn.NUM_CALS] * s[s.fn.CAL_HEADER_SIZE],
                                               s[s.fn.CAL_HEADER_SIZE])],
            fn.USER_START_ADDR: lambda s: max(s[s.fn.CAL_DATA_START_ADDR]) +
            s[s.fn.CAL_DATA_SIZE][s[s.fn.CAL_DATA_START_ADDR].index(max(s[s.fn.CAL_DATA_START_ADDR]))]
            if s[s.fn.NUM_CALS] > 0 else s.map[s.fn.FIRST_BASE_CAL_FIELD][0]
        },
        3: {
            fn.CAL_CHKSUM: [0x49, 20, lambda d: d, lambda d: d],
            fn.CAL_DATA_SIZE: lambda s: [BytesHelper.uint_from_bytes(s.reader.read_nvmem(0x19, 4))] * s[s.fn.NUM_CALS],
            fn.CAL_HEADER_SIZE: lambda s: 0x1D,
            fn.CAL_DATA_START_ADDR: lambda s: [s.map[s.fn.CAL_DATE][0] + (s[s.fn.NUM_CALS] * s[s.fn.CAL_HEADER_SIZE]) +
                                               (s[s.fn.CAL_DATA_SIZE][0] * i) for i in range(0, s[s.fn.NUM_CALS])] if
            s[s.fn.NUM_CALS] > 0 else [s.map[s.fn.CAL_DATE][0]],
            fn.USER_START_ADDR: lambda s: s[s.fn.CAL_DATA_START_ADDR][0] + s[s.fn.CAL_DATA_SIZE][0] * s[s.fn.NUM_CALS]
            if s[s.fn.NUM_CALS] > 0 else s.map[s.fn.FIRST_BASE_CAL_FIELD][0]
        }
    }

    class CalHeader(object):

        def __init__(self, field_name, nvmem_content):
            self.rw = nvmem_content.reader
            self.num_cals = nvmem_content.num_cals
            self.header_size = nvmem_content.cal_header_size
            self.first_address, self.size, self.rd_fun, self.wr_fun = nvmem_content.map[field_name]

        def __getitem__(self, cal_index):
            if cal_index >= self.num_cals:
                raise RuntimeError('cal index {0} is out of range for {1} cals'.format(cal_index, self.num_cals))
            address = self.first_address + cal_index * self.header_size
            return self.rd_fun(self.rw.read_nvmem(address, self.size))

        def __setitem__(self, cal_index, data):
            if cal_index >= self.num_cals:
                raise RuntimeError('cal index {0} is out of range for {1} cals'.format(cal_index, self.num_cals))
            address = self.first_address + cal_index * self.header_size
            self.rw.write_nvmem(address, self.wr_fun(data))

    def __init__(self, reader):
        version = reader.read_nvmem(0, 1)[0]
        if version not in self.maps.keys():
            raise RuntimeError('unrecognized EERPOM version {0} in the module'.format(version))
        self.version = version
        self.map = self.maps['base']
        self.map.update(self.maps[version])
        self.reader = reader
        self.check_ro_data()

        self.cal_header_size = self[self.fn.CAL_HEADER_SIZE]
        self.refresh_cal_header_info()

    def __getitem__(self, field_name):
        if field_name in range(0, self.fn.LAST_BASE_READ_ONLY):
            # this a simple RO sector read and manipulation of bytes
            # expected format of map key is [<nvmem offset>, <length>, <func to manipulate bytes>]
            addr, size, func = self.map[field_name]
            return func(self.reader.read_nvmem(addr, size))
        elif field_name in range(self.fn.FIRST_BASE_CAL_FIELD, self.fn.LAST_BASE_CAL_FIELD):
            # this is a base cal field that is R/W, could be different by map
            # expected format of map key is [<nvmem offset>, <length>, <read func>, <write_func>]
            return self.cal_map[field_name]
        elif field_name in range(self.fn.FIRST_MAP_SPECIFIC_FIELD, self.fn.LAST_MAP_SPECIFIC_FIELD):
            # this is a RO field whose implementation varies significantly by map version
            # expected format of map key is a lambda function handling any read and manipulation
            return self.map[field_name](self)
        else:
            raise RuntimeError('field id {0} is not valid'.format(field_name))

    def refresh_cal_header_info(self):
        self.num_cals = self[self.fn.NUM_CALS]
        if self.num_cals > 0:
            self.cal_map = {
                self.fn.CAL_DATE: self.CalHeader(self.fn.CAL_DATE, self),
                self.fn.CAL_CHKSUM: self.CalHeader(self.fn.CAL_CHKSUM, self)
            }

    def get_cal_header_bytes(self, cal_index):
        start_address = self.map[self.fn.FIRST_BASE_CAL_FIELD][0] + self.cal_header_size * cal_index
        size = self.cal_header_size - self.map[self.fn.CAL_CHKSUM][1]
        return self.reader.read_nvmem(start_address, size)

    def check_ro_data(self):
        ro_chksum = self[self.fn.RO_CHKSUM]
        # everything before the RO Chksum should be checked
        # so we are using the addresse of checksum as the size of
        # data to be checked
        ro_size = self.map[self.fn.RO_CHKSUM][0]
        ro_data = self.reader.read_nvmem(0x00, ro_size)
        ro_hash = BytesHelper.sha1_hash(ro_data)
        if ro_hash != ro_chksum:
            raise RuntimeError('nvmem read only area does not have valid chksum')
