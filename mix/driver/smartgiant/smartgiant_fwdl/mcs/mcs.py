import os
import time
import shutil
import struct
import hashlib
import argparse

class MCS2BINDef:
    # address type
    NONE_TYPE_ADDRESS = 0
    SEGMENT_ADDRESS = 1
    LINEAR_ADDRESS = 2

    # type of mcs record
    TYPE_DATA_RECORD = 0
    TYPE_FILE_END_RECORD = 1
    TYPE_SEGMENT_ADDRESS_RECORD = 2
    TYPE_SEGMENT_START_RECORD = 3
    TYPE_LINEAR_ADDRESS_RECORD = 4
    TYPE_LINEAR_START_RECORD = 5

    # File control flag
    FILE_WRONLY = os.O_WRONLY | os.O_CREAT
    FILE_RW = os.O_WRONLY | os.O_CREAT

    # checksum file name
    CHECKSUM_FILE = "firmware.md5"
    OUTPUT_PATH = "output"

class MCS2BINException(Exception): pass

class MCS2BIN():
    def __init__(self, mcs, output=None, pad=0xFF, swap=False):
        assert mcs
        assert isinstance(mcs, basestring)
        assert isinstance(pad, int)
        assert 0 <= pad <= 0xFF
        assert os.path.isfile(mcs)

        self._mcs = mcs
        if output:
            self._output = output
        else:
            path, file = os.path.split(self._mcs)
            if not path:
                self._output =  "{}".format(MCS2BINDef.OUTPUT_PATH)
            else:
                self._output =  "{}/{}".format(path, MCS2BINDef.OUTPUT_PATH)
        if os.path.isdir(self._output):
            shutil.rmtree(self._output)
        os.makedirs(self._output)
        self._pad = pad
        self._swap = swap
        self._seg_lin_select = MCS2BINDef.NONE_TYPE_ADDRESS
        self._high_address = None
        self._bin_line = None
        self._bin_fd = None
        self._address_list = []
        self._last_address = 0

    def _write_bin_line(self, line):
        if not line:
            return

        if self._bin_fd is None:
            raise MCS2BINException("File number is invalid!!")

        os.write(self._bin_fd, line)

    def _split_bin(self, high_address):
        # If the linear address is not continuous, split the bin file
        if self._high_address is None or high_address - self._high_address > 1:
            if self._bin_fd:
                '''
                # pad data to fix 256 page size.
                rest = (self._last_address + 1) % 256
                if rest:
                    remaind = 256 - rest
                    print("last: {}, remaind: {}".format(self._last_address, remaind))
                    line = ""
                    for i in range(0, remaind):
                        line += struct.pack('B', self._pad)
                    self._write_bin_line(line)
                '''
                os.close(self._bin_fd)
                self._bin_fd = None
            self._bin_fd = os.open("{}/{}.bin".format(self._output, hex(high_address << 16)), MCS2BINDef.FILE_WRONLY)
            self._last_address = (high_address << 16)
            self._address_list.append(self._last_address)
            print("bin file: {}/{}.bin, start address: {}".format(self._output, hex(high_address << 16), hex(self._last_address)))

    def _decode_line(self, line):
        '''
        mcs line format: 
        |-----|-----|-------|------|-----------|--------|
        |  :  |  BC |  AAAA |  TT  | HHHH...HH |   CC   |
        |-----|-----|-------|------|-----------|--------|
        |Start|Byte |Hex    |Record|HH = 1 data|Checksum|
        |Char |Count|Address|Type  |byte       |        |
        |-----|-----|-------|------|-----------|--------|
        |1    |2    |       |2     |2 up to 32 |        |
        |char |chars|4 chars|chars |chars      |2 chars |
        |-----|-----|-------|------|-----------|--------|
        '''
        assert len(line) > 10
        assert line[0:1] == ":"

        data_cnt = int(line[1:3], 16)
        first_word = int(line[3:7], 16)
        data_type = int(line[7:9], 16)
        datas = line[9:].strip()

        # get checksum
        checksum = data_cnt + (first_word >> 8) + (first_word & 0xFF) + data_type

        if data_type == MCS2BINDef.TYPE_DATA_RECORD:
            if self._seg_lin_select == MCS2BINDef.NONE_TYPE_ADDRESS:
                self._seg_lin_select = MCS2BINDef.LINEAR_ADDRESS

            if self._seg_lin_select == MCS2BINDef.LINEAR_ADDRESS:
                address = (self._high_address << 16 & 0xFFFF0000) | first_word
            else:
                address = (self._high_address << 4 & 0xFF00) | first_word
            # pad empty data.
            pad_cnt = address - (self._last_address + 1)
            for i in range(0, pad_cnt):
                if not self._bin_line:
                    self._bin_line = struct.pack('B', self._pad)
                else:
                    self._bin_line += struct.pack('B', self._pad)

            # encode data to hex.
            data_len = data_cnt * 2
            for i in range(data_cnt):
                byte = int(datas[i*2:(i+1)*2], 16)
                if not self._bin_line:
                    self._bin_line = struct.pack('B', byte)
                else:
                    self._bin_line += struct.pack('B', byte)
                checksum = (checksum + byte) & 0xFF

            # checksum.
            _crc = int(datas[data_len:], 16)
            checksum = (checksum + _crc) & 0xFF

            # record last data address.
            self._last_address += (pad_cnt + data_cnt)
        elif data_type == MCS2BINDef.TYPE_FILE_END_RECORD:
            # nothing to do
            return True
        elif data_type == MCS2BINDef.TYPE_SEGMENT_ADDRESS_RECORD:
            if self._seg_lin_select == MCS2BINDef.NONE_TYPE_ADDRESS:
                self._seg_lin_select = MCS2BINDef.SEGMENT_ADDRESS

            if self._seg_lin_select == MCS2BINDef.SEGMENT_ADDRESS:
                self._split_bin(int(datas[0:4], 16))
                self._high_address = int(datas[0:4], 16)
                _crc = int(datas[4:6], 16)
                checksum = (checksum + (self._high_address >> 8) + (self._high_address & 0xFF) + _crc & 0xFF)
        elif data_type == MCS2BINDef.TYPE_SEGMENT_START_RECORD:
            # nothing to do
            return True
        elif data_type == MCS2BINDef.TYPE_LINEAR_ADDRESS_RECORD:
            if self._seg_lin_select == MCS2BINDef.NONE_TYPE_ADDRESS:
                self._seg_lin_select = MCS2BINDef.LINEAR_ADDRESS

            if self._seg_lin_select == MCS2BINDef.LINEAR_ADDRESS:
                self._split_bin(int(datas[0:4], 16))
                self._high_address = int(datas[0:4], 16)
                _crc = int(datas[4:6], 16)
                checksum = (checksum + (self._high_address >> 8) + (self._high_address & 0xFF) + _crc & 0xFF)
        elif data_type == MCS2BINDef.TYPE_LINEAR_START_RECORD:
            # nothing to do
            return True
        else:
            print("unknow type record: {}".format(data_type))
            return False

        if checksum != 0:
            raise MCS2BINException("Checksum error. line data: {}".format(line))

        if data_cnt * 2 != (len(datas) - 2):
            print("{}, {}".format(data_cnt, len(datas) - 2))

        return True

    def _update_checksum(self):
        fd = os.open("{}/{}".format(self._output, MCS2BINDef.CHECKSUM_FILE), MCS2BINDef.FILE_WRITE)

    def _store_checksum(self):
        md5_fd = os.open("{}/{}".format(self._output, MCS2BINDef.CHECKSUM_FILE), MCS2BINDef.FILE_WRONLY)
        for _address in self._address_list:
            md5 = hashlib.md5()
            with open("{}/{}.bin".format(self._output, hex(_address)), "r") as f:
                line = f.read(8192)
                while line:
                    md5.update(line)
                    line = f.read(8192)
            os.write(md5_fd, "{}  {}.bin\n".format(md5.hexdigest(), hex(_address)))
        os.close(md5_fd)

    def mcs2bin(self):
        print("Decode mcs file to mutil binary file!")
        with open(self._mcs, 'r') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                self._decode_line(line)
                self._write_bin_line(self._bin_line)
                self._bin_line = None
        print("Store checksum to {}!".format(MCS2BINDef.CHECKSUM_FILE))
        self._store_checksum()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='Output path', type=str, default=None)
    parser.add_argument('-i', '--input', help='Input source mcs file', type=str)
    parser.add_argument('-p', '--pad', help='pad byte', type=str, default="0xFF")
    parser.add_argument('-w', '--swap', help='Swap wordwise', type=bool, default=False)

    args = parser.parse_args()
    output = args.output
    mcs = args.input
    pad = int(args.pad, 16)
    swap = args.swap

    mcs2bin = MCS2BIN(mcs, output, pad, swap)
    start = time.time()
    mcs2bin.mcs2bin()
    print("Successful, used {} S!".format(time.time() - start))
