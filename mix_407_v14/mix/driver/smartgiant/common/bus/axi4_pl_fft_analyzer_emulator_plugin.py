from mix.driver.smartgiant.common.bus.axi4_bus_emulator_plugin import AXI4BusEmulatorPlugin

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AXI4MIXFftAnalyzerSGEmulatorPlugin(AXI4BusEmulatorPlugin):
    def __init__(self):
        super(AXI4MIXFftAnalyzerSGEmulatorPlugin, self).__init__()
        self.ram_index = 0
        self.ram_data = [
            [0, 2, 0, 0],
            [0, 0, 0, 0],

            [0, 6, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 0, 0],
            [0, 0, 0, 0],

            [0, 3, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 5, 0],
            [0, 0, 0, 0],

            [0, 0, 9, 0],
            [0, 0, 0, 0],

            [0, 0, 1, 0],
            [0, 0, 0, 0],

            [0, 10, 0, 0],
            [0, 0, 0, 0],

            [0, 2, 0, 0],
            [0, 0, 0, 0],

            [0, 6, 6, 0],
            [0, 0, 0, 0],

            [0, 0, 10, 0],
            [0, 0, 0, 0],

            [0, 0, 9, 0],
            [0, 0, 0, 0],

            [0, 3, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 0, 0],
            [0, 0, 0, 0],

            [0, 0, 1, 0],
            [0, 0, 0, 0],

            [0, 0, 1, 0],
            [0, 0, 0, 0],

            [0, 0, 1, 0],
            [0, 0, 0, 0],

            [0, 10, 0, 0],
            [0, 0, 0, 0],
        ]

    def read_8bit_inc(self, addr, rd_len):
        if addr == 0x10:
            return [0x01]
        elif addr == 0x16:
            return [1]
        elif addr == 0x14:
            return [1]
        elif addr == 0x80:
            index = self.ram_index
            self.ram_index += 1
            if self.ram_index >= len(self.ram_data):
                self.ram_index = 0
            return self.ram_data[index]
        else:
            return super(AXI4MIXFftAnalyzerSGEmulatorPlugin, self).read_8bit_inc(addr, rd_len)

    def read_32bit_inc(self, addr, rd_len):
        if addr == 0x84:
            return [20]
        else:
            return super(AXI4MIXFftAnalyzerSGEmulatorPlugin, self).read_32bit_inc(addr, rd_len)

