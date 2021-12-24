'''
Get Zynq type (7007, 7010 and 7020) by reading SLCR PSS_IDCODE register.
The register is defined in UG585 Zynq-7000 SoC Technical Reference Manual, AppendixB Register Details section.
SLCR base address: 0xf800_0000
PSS_IDCODE offest: 0x530
Device bits: bit12-16
Value table (from ./include/zynqpl.h in uboot src):

#define XILINX_ZYNQ_7007S   0x3
#define XILINX_ZYNQ_7010    0x2
#define XILINX_ZYNQ_7012S   0x1c
#define XILINX_ZYNQ_7014S   0x8
#define XILINX_ZYNQ_7015    0x1b
#define XILINX_ZYNQ_7020    0x7
#define XILINX_ZYNQ_7030    0xc
#define XILINX_ZYNQ_7035    0x12
#define XILINX_ZYNQ_7045    0x11
#define XILINX_ZYNQ_7100    0x16
'''
import mmap

dict_mapping = {
    0x3: '7z007s',
    0x2: '7z010',
    0x7: '7z020'
}

slcr_base = 0xf8000000
pss_idcode_offset = 0x530
# 4 bytes
pss_idcode_width = 4

device_mask = 0x1f000
device_shift = 12

with open('/dev/mem', 'r+b') as f:
    # we need to read 4 bytes from 0x530, so only mmap 0x1000 bytes memory.
    idcode_map = mmap.mmap(f.fileno(), length=0x1000, offset=0xf8000000)
    idcode_map.seek(0x530)
    raw_data = bytearray(idcode_map.read(4))
# whole 32bit
pss_idcode = 0
for i in reversed(list(raw_data)):
    pss_idcode = pss_idcode << 8
    pss_idcode += i

device = (pss_idcode & device_mask) >> device_shift

print(dict_mapping[device])
