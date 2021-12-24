from datetime import datetime
import hashlib
import struct
import string


class BytesHelper(object):

    @staticmethod
    def dump_bytes(ba_data, name='dump_ba', folder='/tmp'):
        import os
        f = open(os.path.join(folder, name + '.csv'), 'w+')
        for i, b in enumerate(ba_data):
            f.write('{0}, 0x{1:x}\n'.format(i, b))
        f.close()

    @staticmethod
    def ushort_from_bytes(data_bytes):
        if len(data_bytes) != 2:
            raise RuntimeError('cannot convert {0} bytes to ushort, must be 2 bytes'.format(len(data_bytes)))
        return struct.unpack('<H', data_bytes)[0]

    @staticmethod
    def uint_from_bytes(data_bytes):
        if len(data_bytes) != 4:
            raise RuntimeError('cannot convert {0} bytes to uint, must be 4 bytes'.format(len(data_bytes)))
        return struct.unpack('<I', data_bytes)[0]

    @staticmethod
    def bytes_from_uint(data):
        return struct.pack('<I', data)

    @staticmethod
    def bytes_from_ushort(data):
        return struct.pack('<H', data)

    @staticmethod
    def sha1_hash(data):
        s = hashlib.sha1()
        s.update(data)
        return bytearray(s.digest())

    @staticmethod
    def bytes_from_cal_date(d):
        # in compliance with 081-2110-C section 5, Sun-Sat is defined as 1-7 instead of 0-6 for day
        # and week code starts from 1 instead of 0 so we increment the day and week bytes to convert
        # from python datetime to byte array of YYWWDHHMM
        date_string = d.strftime('%Y%U%w%H%M')[2:]
        ww = '{0:02d}'.format(int(date_string[2:4]) + 1)
        d = str(int(date_string[4]) + 1)
        date_array = bytearray(date_string[:2] + ww + d + date_string[5:])
        return date_array

    @staticmethod
    def cal_date_from_bytes(date_array):
        # expecting YYWWDHHMM
        # in compliance with 081-2110-C section 5, Sun-Sat is defined as 1-7 instead of 0-6 for day
        # and week code starts from 1 instead of 0 so we decrement the day and week bytes to be
        # compliant with python datetime prior to conversion
        date_string = str(date_array)
        ww = int(date_string[2:4])
        d = int(date_string[4])
        date_string = '20' + date_string[:2] + '{0:02d}{1}'.format(ww - 1, d - 1) + date_string[5:]
        return datetime.strptime(date_string, '%Y%U%w%H%M')

    @staticmethod
    def production_count_from_bytes(data_bytes):
        # using base 34 as described in Appendix G of 081-2110-C
        # acceptable digits are 1-9, A-Z, skipping I and O
        digits = [str(i) for i in range(0, 10)] + [e for e in string.ascii_uppercase if e not in ('I', 'O')]
        prod_count = 0
        base = 34
        for i, c in enumerate(str(data_bytes[::-1])):
            if c not in digits:
                raise RuntimeError('production count string is not valid')
            prod_count += digits.index(c) * base ** i
        return prod_count

    @staticmethod
    def sn_date_from_bytes(date_array):
        # expecting YWWD
        # in compliance with 081-2110-C section 5, Sun-Sat is defined as 1-7 instead of 0-6 for day
        # and week code starts from 1 instead of 0 so we decrement the day and week bytes to be
        # compliant with python datetime prior to conversion
        ww = int(str(date_array)[1:3])
        d = int(str(date_array)[3])
        date_string = str(date_array)[0] + '{0:02d}{1}'.format(ww - 1, d - 1)
        year = datetime.now().year
        timestamp = datetime.strptime(str(year)[:3] + date_string, '%Y%U%w')
        if timestamp > datetime.now():
            timestamp = datetime.strptime(str(year - 10)[:3] + date_string, '%Y%U%w')
        return timestamp
