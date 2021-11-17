

class PLUTCEmulatorPlugin(object):

    def write_8bit_fix(self, addr, data):
        pass

    def write_16bit_fix(self, addr, data):
        pass

    def write_32bit_fix(self, addr, data):
        pass

    def read_16bit_fix(self, addr, rd_len):
        return [999]

    def read_32bit_fix(self, addr, rd_len):
        return [1538296130]
