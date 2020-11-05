PERTOS parsing definition file
==============================

Version Info
------------
13/12/2016 PeRtosFactoryTests-2237.1.1 (RELEASE)

[TOC]

Commands that can be parsed
===========================

smb 0 0xEA 0x0443
---------
 - Command name : `smb 0 0xEA 0x0443`
 - Command to send: `smb 0 0xEA 0x0443`
```
{{ANYTHING}} 0x0443 {{ANYTHING}}={{ANYTHING}} 0x10
{{isPass}} smb 0 0xEA 0x0443
```
                                                                                                                                                               
smb 0 0xEA 0x044E 0xF0
---------
 - Command name : `smb 0 0xEA 0x044E 0xF0`
 - Command to send: `smb 0 0xEA 0x044E 0xF0`
```
{{ANYTHING}} 0x044e {{ANYTHING}}={{ANYTHING}} 0xf0
{{isPass}} smb 0 0xEA 0x044E 0xF0
```

fs mount 0x816d00000
---------
 - Command name : `fs mount 0x816d00000`
 - Command to send: `fs mount 0x816d00000`
```
{{isPass}} fs mount 0x816d00000
```

slave up cc0
---------
- Command name : `slave up cc0`
- Command to send: `slave up cc0`
```
{{isPass}} slave up cc0
```

slave up cc1
---------
- Command name : `slave up cc1`
- Command to send: `slave up cc1`
```
{{isPass}} slave up cc1
```

slave up cc2
---------
- Command name : `slave up cc2`
- Command to send: `slave up cc2`
```
{{isPass}} slave up cc2
```

slave up sio kf_sram.shr 0x0 200000
---------
- Command name : `slave up sio kf_sram.shr 0x0 200000`
- Command to send: `slave up sio kf_sram.shr 0x0 200000`
```
{{isPass}} slave up sio kf_sram.shr 0x0 200000
```

slave up sio kf_dram.shr 0x0 500000
---------
- Command name : `slave up sio kf_dram.shr 0x0 500000`
- Command to send: `slave up sio kf_dram.shr 0x0 500000`
```
{{isPass}} slave up sio kf_dram.shr 0x0 500000
```

slave up aop kf_dram.shr 0x0 200000
---------
- Command name : `slave up aop kf_dram.shr 0x0 200000`
- Command to send: `slave up aop kf_dram.shr 0x0 200000`
```
{{isPass}} slave up aop kf_dram.shr 0x0 200000
```

slave up pms kf_dram.shr 0x0 200000
---------
- Command name : `slave up pms kf_dram.shr 0x0 200000`
- Command to send: `slave up pms kf_dram.shr 0x0 200000`
```
{{isPass}} slave up pms kf_dram.shr 0x0 200000
```

slave up gfx kf_dram.shr 0x0 200000
---------
- Command name : `slave up gfx kf_dram.shr 0x0 200000`
- Command to send: `slave up gfx kf_dram.shr 0x0 200000`
```
{{isPass}} slave up gfx kf_dram.shr 0x0 200000
```


slave up isp kf_dram.shr 0x0 200000
---------
- Command name : `slave up isp kf_dram.shr 0x0 200000`
- Command to send: `slave up isp kf_dram.shr 0x0 200000`
```
{{isPass}} slave up isp kf_dram.shr 0x0 200000
```


slave up sve kf_dram.shr 0x0 200000
---------
- Command name : `slave up sve kf_dram.shr 0x0 200000`
- Command to send: `slave up sve kf_dram.shr 0x0 200000`
```
{{isPass}} slave up sve kf_dram.shr 0x0 200000
```

slave up sep kf_dram.sep 0x0 500000
---------
- Command name : `slave up sep kf_dram.sep 0x0 500000`
- Command to send: `slave up sep kf_dram.sep 0x0 500000`
```
{{isPass}} slave up sep kf_dram.sep 0x0 500000
```

bbq config fg 0 0 4 1 0 0 G
---------
- Command name : `bbq config fg 0 0 4 1 0 0 G`
- Command to send: `bbq config fg 0 0 4 1 0 0 G`
```
{{isPass}} bbq config fg 0 0 4 1 0 0 G
```

bbq config 7 500 150 5 100 24 6 G
---------
- Command name : `bbq config 7 500 150 5 100 24 6 G`
- Command to send: `bbq config 7 500 150 5 100 24 6 G`
```
{{isPass}} bbq config 7 500 150 5 100 24 6 G
```

bbq config fg 0 0 4 1 0 0 C
---------
- Command name : `bbq config fg 0 0 4 1 0 0 C`
- Command to send: `bbq config fg 0 0 4 1 0 0 C`
```
{{isPass}} bbq config fg 0 0 4 1 0 0 C
```


bbq config 7 500 150 5 100 24 6 C
---------
- Command name : `bbq config 7 500 150 5 100 24 6 C`
- Command to send: `bbq config 7 500 150 5 100 24 6 C`
```
{{isPass}} bbq config 7 500 150 5 100 24 6 C
```

bbq config 3 500 150 5 100 24 6 2
---------
- Command name : `bbq config 3 500 150 5 100 24 6 2`
- Command to send: `bbq config 3 500 150 5 100 24 6 2`
```
{{isPass}} bbq config 3 500 150 5 100 24 6 2
```

bbq on
---------
- Command name : `bbq on`
- Command to send: `bbq on`
```
{{isPass}} bbq on
```
bbq off
---------
- Command name : `bbq off`
- Command to send: `bbq off`
```
{{isPass}} bbq off
```

hammer 0x1777 40 5 -s 0x4b1ddecafc0ffee -m 300
---------
 - Command name : `hammer 0x1777 40 5 -s 0x4b1ddecafc0ffee -m 300`
 - Command to send: `hammer 0x1777 40 5 -s 0x4b1ddecafc0ffee -m 300`
```
{{ANYTHING}}TEST_RESULT{{ANYTHING}} {{Result}}
{{isPass}} hammer 0x1777 40 5 -s 0x4b1ddecafc0ffee -m 300
```

clksw config 0 200 -j 20
---------
- Command name : `clksw config 0 200 -j 20`
- Command to send: `clksw config 0 200 -j 20`
```
{{isPass}} clksw config 0 200 -j 20
```

clksw config 0 500 -j 20
---------
- Command name : `clksw config 0 500 -j 20`
- Command to send: `clksw config 0 500 -j 20`
```
{{isPass}} clksw config 0 500 -j 20
```

clksw config 4 500 -j 10 601 602 603 604 605
---------
- Command name : `clksw config 4 500 -j 10 601 602 603 604 605`
- Command to send: `clksw config 4 500 -j 10 601 602 603 604 605`
```
{{isPass}} clksw config 4 500 -j 10 601 602 603 604 605
```

clksw on
---------
- Command name : `clksw on`
- Command to send: `clksw on`
```
{{isPass}} clksw on
```
clksw off
---------
- Command name : `clksw off`
- Command to send: `clksw off`
```
{{isPass}} clksw off
```

mmu ddr-linear
--------------
- Command name : `mmu ddr-linear`
- Command to send : `mmu ddr-linear`
```
{{ANYTHING}}ddr mapped linearly
{{isPass}} mmu ddr-linear
```

mmu ddr-protect fs
--------------
- Command name : `mmu ddr-protect fs`
- Command to send : `mmu ddr-protect fs`
```
{{isPass}} mmu ddr-protect fs
```

mmu ddr-protect acc
--------------
- Command name : `mmu ddr-protect acc`
- Command to send : `mmu ddr-protect acc`
```
{{isPass}} mmu ddr-protect acc
```

mmu ddr-protect 1024
--------------
- Command name : `mmu ddr-protect 1024`
- Command to send : `mmu ddr-protect 1024`
```
{{isPass}} mmu ddr-protect 1024
```

mmu ddr-protect 128
--------------
- Command name : `mmu ddr-protect 128`
- Command to send : `mmu ddr-protect 128`
```
{{isPass}} mmu ddr-protect 128
```

fuse all
--------------
- Command name : `fuse all`
- Command to send : `fuse all`
``` 
{{ANYTHING}} ECID Fuse : {{ECID}}
```
```
{{isPass}} fuse all
```

fuse config
---------
- Command name : `fuse config`
- Command to send: `fuse config`
``` 
{{ANYTHING}} Configuration fuse assignment
{{ANYTHING}}   {{Fuse_Config}}
```
``` 
{{ANYTHING}}   Fuse Rev     : {{Fuse_Revision}}
```
```
{{ANYTHING}}   Product ID : {{Product_ID}}
```
```
{{ANYTHING}}  PCPU IDS      : {{ANYTHING}},  {{PCPU_IDS_Voltage}} uA 
{{ANYTHING}}  ECPU IDS      : {{ANYTHING}},  {{ECPU_IDS_Voltage}} uA 
{{ANYTHING}}  GPU7 IDS      : {{ANYTHING}},  {{GCPU_IDS_Voltage}} uA 
{{ANYTHING}}  GPU8 IDS      : {{ANYTHING}},  {{GPUB_IDS_Voltage}} uA 
{{ANYTHING}}  GPU BIN IDS   : {{ANYTHING}},  {{GPU_BIN_IDS_Voltage}} uA 
{{ANYTHING}}  SOC IDS       : {{ANYTHING}},  {{SOC_IDS_Voltage}} uA 
{{ANYTHING}}  SOC SRAM IDS  : {{ANYTHING}},  {{SOC_SRAM_IDS_Voltage}} uA 
{{ANYTHING}}  CPU SRAM IDS  : {{ANYTHING}},  {{CPU_SRAM_IDS_Voltage}} uA 
{{ANYTHING}}  GPU7 SRAM IDS : {{ANYTHING}},  {{GPU7_SRAM_IDS_Voltage}} uA 
{{ANYTHING}}  GPU8 SRAM IDS : {{ANYTHING}},  {{GPU8_SRAM_IDS_Voltage}} uA 
{{ANYTHING}}  DISP IDS      : {{ANYTHING}},  {{DISP_IDS_Voltage}} uA 
{{ANYTHING}}  FIXED IDS     : {{ANYTHING}},  {{FIXED_IDS_Voltage}} uA 
{{ANYTHING}}  LOW IDS       : {{ANYTHING}},  {{LOW_IDS_Voltage}} uA 
{{ANYTHING}}  DCS IDS       : {{ANYTHING}},  {{DCS_IDS_Voltage}} uA 
```
```
{{ANYTHING}}  SOC IDS 105C       : {{ANYTHING}},   {{SOC_IDS_105C_Voltage}} uA
{{ANYTHING}}  PCPU IDS 105C      : {{ANYTHING}},   {{PCPU_IDS_105C_Voltage}} uA
{{ANYTHING}}  ECPU IDS 105C      : {{ANYTHING}},   {{ECPU_IDS_105C_Voltage}} uA
{{ANYTHING}}  GPU7 IDS 105C      : {{ANYTHING}},   {{GPU7_IDS_105C_Voltage}} uA
{{ANYTHING}}  GPU8 IDS 105C      : {{ANYTHING}},   {{GPU8_IDS_105C_Voltage}} uA
{{ANYTHING}}  GPU7 SRAM IDS 105C : {{ANYTHING}},   {{GPU7_SRAM_IDS_105C_Voltage}} uA
{{ANYTHING}}  GPU8 SRAM IDS 105C : {{ANYTHING}},   {{GPU8_SRAM_IDS_105C_Voltage}} uA
```
```
{{ANYTHING}} DVFM fuse settings
{{ANYTHING}}   Rev   : {{DVFM_Rev}}
{{ANYTHING}}   Base  : {{ANYTHING}}, {{Low_Limit}} uV
```
```
{{ANYTHING}} PCPU fuse settings
{{ANYTHING}}   MP001|P1 : {{ANYTHING}}, {{MP001_Voltage}} uV
{{ANYTHING}}   MP101|P2 : {{ANYTHING}}, {{MP101_Voltage}} uV
{{ANYTHING}}   MP102|P3 : {{ANYTHING}}, {{MP102_Voltage}} uV
{{ANYTHING}}   MP002|P4 : {{ANYTHING}}, {{MP002_Voltage}} uV
{{ANYTHING}}   MP103|P5 : {{ANYTHING}}, {{MP203_Voltage}} uV
{{ANYTHING}}   MP003|P6 : {{ANYTHING}}, {{MP003_Voltage}} uV
{{ANYTHING}}   MP104|P7 : {{ANYTHING}}, {{MP104_Voltage}} uV
{{ANYTHING}}   MP004|P8 : {{ANYTHING}}, {{MP004_Voltage}} uV
{{ANYTHING}}   MP005|P9 : {{ANYTHING}}, {{MP005_Voltage}} uV
{{ANYTHING}}   MP006|P10 : {{ANYTHING}}, {{MP006_Voltage}} uV
{{ANYTHING}}   MP007|P11 : {{ANYTHING}}, {{MP007_Voltage}} uV
{{ANYTHING}}   MP008|P12 : {{ANYTHING}}, {{MP008_Voltage}} uV
{{ANYTHING}}   MP009|P13 : {{ANYTHING}}, {{MP009_Voltage}} uV
{{ANYTHING}}   MP00A|P14 : {{ANYTHING}}, {{MP00A_Voltage}} uV
{{ANYTHING}}   MP105|P15 : {{ANYTHING}}, {{MP105_Voltage}} uV
```
```
{{ANYTHING}} ECPU fuse settings
{{ANYTHING}}   ME001|E1 : {{ANYTHING}}, {{ME001_Voltage}} uV
{{ANYTHING}}   ME002|E2 : {{ANYTHING}}, {{ME002_Voltage}} uV
{{ANYTHING}}   ME003|E3 : {{ANYTHING}}, {{ME003_Voltage}} uV
{{ANYTHING}}   ME004|E4 : {{ANYTHING}}, {{ME004_Voltage}} uV
{{ANYTHING}}   ME005|E5 : {{ANYTHING}}, {{ME005_Voltage}} uV

```
```
{{ANYTHING}} GPU fuse settings
{{ANYTHING}}   MG001|G1: {{ANYTHING}}, {{MG001_Voltage}} uV
{{ANYTHING}}   MG002|G2: {{ANYTHING}}, {{MG002_Voltage}} uV
{{ANYTHING}}   MG003|G3: {{ANYTHING}}, {{MG003_Voltage}} uV
{{ANYTHING}}   MG004|G4: {{ANYTHING}}, {{MG004_Voltage}} uV
{{ANYTHING}}   MG005|G5: {{ANYTHING}}, {{MG005_Voltage}} uV
{{ANYTHING}}   MG006|G6: {{ANYTHING}}, {{MG006_Voltage}} uV
{{ANYTHING}}   MG007|G7: {{ANYTHING}}, {{MG007_Voltage}} uV
```
```
{{ANYTHING}} SOC fuse settings
{{ANYTHING}}   MS001|S3 : {{ANYTHING}}, {{MS001_Voltage}} uV
{{ANYTHING}}   MS002|S4 : {{ANYTHING}}, {{MS002_Voltage}} uV
{{ANYTHING}}   MS003|S5 : {{ANYTHING}}, {{MS003_Voltage}} uV
```
```
{{ANYTHING}} DISP fuse settings
{{ANYTHING}}   MI001|I2 : {{ANYTHING}}, {{MI001_Voltage}} uV
{{ANYTHING}}   MI002|I3 : {{ANYTHING}}, {{MI002_Voltage}} uV
{{ANYTHING}}   MI003|I4 : {{ANYTHING}}, {{MI003_Voltage}} uV
{{ANYTHING}}   MI001|I5 : {{ANYTHING}}, {{MI004_Voltage}} uV
{{ANYTHING}}   MI002|I6 : {{ANYTHING}}, {{MI005_Voltage}} uV
{{ANYTHING}}   MI003|I7 : {{ANYTHING}}, {{MI006_Voltage}} uV
```
```
{{ANYTHING}} DCS fuse settings
{{ANYTHING}}   MD001|D4 : {{ANYTHING}}, {{MD001_Voltage}} uV
{{ANYTHING}}   MD002|D5 : {{ANYTHING}}, {{MD002_Voltage}} uV
{{ANYTHING}}   MD003|D6 : {{ANYTHING}}, {{MD003_Voltage}} uV
```
``` 
{{isPass}} fuse config
```

ddr print info
---------
 - Command name : `ddr print info`
 - Command to send: `ddr print info`
```
DDR Info Struct
{{ANYTHING}}  channels: {{channels}}
{{ANYTHING}}  ch width: {{ch width}}
{{ANYTHING}}  ranks:    {{ranks}}
{{ANYTHING}}  vendor:   {{vendor}}  mfg: {{ANYTHING}}
{{ANYTHING}}  rev1:     {{rev1}}
{{ANYTHING}}  rev2:     {{rev2}}
{{ANYTHING}}  density:  {{density}}
{{ANYTHING}}  width:    {{width}}
{{ANYTHING}}  banks:    {{banks}}
{{ANYTHING}}  type:     {{type}}
{{ANYTHING}}  initd:    {{initd}}
{{ANYTHING}}  ca_cal:   {{ca_cal}}
{{ANYTHING}}  rd_cal:   {{rd_cal}}
{{ANYTHING}}  wr_cal:   {{wr_cal}}
{{ANYTHING}}  CA0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD0.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD0.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR0.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR0.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ0.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ0.1: {{ANYTHING}}
{{ANYTHING}}  CA1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD1.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD1.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR1.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR1.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA1: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ1.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ1.1: {{ANYTHING}}
{{ANYTHING}}  CA2: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS2: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK2: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD2.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD2.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR2.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR2.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA2: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ2.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ2.1: {{ANYTHING}}
{{ANYTHING}}  CA3: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS3: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK3: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD3.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD3.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR3.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR3.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA3:{{ANYTHING}}
{{ANYTHING}}  WRLVL DQ3.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ3.1: {{ANYTHING}}
{{ANYTHING}}  CA4: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS4: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK4: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD4.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD4.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR4.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR4.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA4:{{ANYTHING}}
{{ANYTHING}}  WRLVL DQ4.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ4.1: {{ANYTHING}}
{{ANYTHING}}  CA5: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS5: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK5: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD5.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD5.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR5.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR5.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA5:{{ANYTHING}}
{{ANYTHING}}  WRLVL DQ5.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ5.1: {{ANYTHING}}
{{ANYTHING}}  CA6: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS6: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK6: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD6.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD6.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR6.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR6.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA6:{{ANYTHING}}
{{ANYTHING}}  WRLVL DQ6.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ6.1: {{ANYTHING}}
{{ANYTHING}}  CA7: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CS7: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  CK7: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD7.0: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  RD7.1: {{ANYTHING}} { {{ANYTHING}}
{{ANYTHING}}  WR7.0: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WR7.1: {{ANYTHING}} /  {{ANYTHING}}
{{ANYTHING}}  WRLVL CA7:{{ANYTHING}}
{{ANYTHING}}  WRLVL DQ7.0: {{ANYTHING}}
{{ANYTHING}}  WRLVL DQ7.1: {{ANYTHING}}
{{ANYTHING}}  MBytes:     {{MBytes}}
{{ANYTHING}}  cal panic   {{cal panic}}
{{ANYTHING}}  odts en     {{odts en}}
{{ANYTHING}}  dyn cal en  {{dyn cal en}}
{{ANYTHING}}  vref cal en {{vref cal en}}
{{ANYTHING}}  refcnt en   {{refcnt en}}
{{ANYTHING}}  rd/wr cal en {{rd/wr cal en}}
{{isPass}} ddr print info
```

ddr calw nocheck
---------
 - Command name : `ddr calw nocheck`
 - Command to send: `ddr calw nocheck`
```
{{isPass}} ddr calw nocheck
{{ANYTHING}}
```

ddr cal
---------
 - Command name : `ddr cal`
 - Command to send: `ddr cal`
```
{{ANYTHING}} ch0: {{ANYTHING}}
{{ANYTHING}} ch1: {{ANYTHING}}
{{ANYTHING}} ch2: {{ANYTHING}}
{{ANYTHING}} ch3: {{ANYTHING}}
{{ANYTHING}} ch4: {{ANYTHING}}
{{ANYTHING}} ch5: {{ANYTHING}}
{{ANYTHING}} ch6: {{ANYTHING}}
{{ANYTHING}} ch7: {{ANYTHING}}
{{isPass}} ddr cal
```

pmu rails
---------
 - Command name : `pmu rails`
 - Command to send: `pmu rails`
```
{{ANYTHING}}  LDO4|vlow       =   {{VLOW_Voltage}} uV [  {{VLOW_LOW}}.. {{VLOW_HIGH}}] uV
```
```
{{isPass}} pmu rails
```

pmgr mode 701
---------
 - Command name : `pmgr mode 701`
 - Command to send: `pmgr mode 701`
```
{{isPass}} pmgr mode 701
```

pmgr mode 702
---------
- Command name : `pmgr mode 702`
- Command to send: `pmgr mode 702`
```
{{isPass}} pmgr mode 702
```

pmgr mode 703
---------
 - Command name : `pmgr mode 703`
 - Command to send: `pmgr mode 703`
```
{{isPass}} pmgr mode 703
```

pmgr mode 601
---------
 - Command name : `pmgr mode 601`
 - Command to send: `pmgr mode 601`
```
{{isPass}} pmgr mode 601
```

pmgr mode 602
---------
 - Command name : `pmgr mode 602`
 - Command to send: `pmgr mode 602`
```
{{isPass}} pmgr mode 602
```

pmgr mode 603
---------
 - Command name : `pmgr mode 603`
 - Command to send: `pmgr mode 603`
```
{{isPass}} pmgr mode 603
```

pmgr mode 604
---------
- Command name : `pmgr mode 604`
- Command to send: `pmgr mode 604`
```
{{isPass}} pmgr mode 604
```

pmgr mode 605
---------
- Command name : `pmgr mode 605`
- Command to send: `pmgr mode 605`
```
{{isPass}} pmgr mode 605
```

pmgr vmode bin
---------
 - Command name : `pmgr vmode bin`
 - Command to send: `pmgr vmode bin`
```
{{ANYTHING}} pmgr vmode bin
{{isPass}} pmgr vmode bin
```

pmgr show-clk
---------
 - Command name : `pmgr show-clk`
 - Command to send: `pmgr show-clk`
```
{{ANYTHING}}PU_CLK        :{{ANYTHING}} {{CPU_CLK}} Mhz
{{ANYTHING}}GFX_CLK        :{{ANYTHING}} {{GFX_CLK}} Mhz
{{ANYTHING}}
{{ANYTHING}}GFX_FENDER_CLK :{{ANYTHING}} {{GFX_CLK}} Mhz
{{ANYTHING}}FAST_AF_CLK    :{{ANYTHING}} {{FAST_AF_CLK}} Mhz
{{ANYTHING}}SLOW_AF_CLK    :{{ANYTHING}} {{SLOW_AF_CLK}} Mhz
{{ANYTHING}}amcc_cfg_sel:{{ANYTHING}} {{amcc_cfg_sel}}
{{ANYTHING}}MCU_CLK_FREQ   :{{ANYTHING}} {{MCU_CLK_FREQ}} Mhz
{{ANYTHING}}MCU_REF_CLK    :{{ANYTHING}} {{MCU_CLK_FREQ}} Mhz
{{ANYTHING}}mcu_ref_src_sel:{{ANYTHING}} {{mcu_ref_src_sel}}
{{ANYTHING}}mcu_ref_cfg_sel:{{ANYTHING}} {{mcu_ref_cfg_sel}}
{{ANYTHING}}PLL 0:{{ANYTHING}} {{PLL 0}} Mhz
{{ANYTHING}}PLL 1:{{ANYTHING}} {{PLL 1}} Mhz
{{ANYTHING}}PLL 2:{{ANYTHING}} {{PLL 2}} Mhz
{{ANYTHING}}PLL 3:{{ANYTHING}} {{PLL 3}} Mhz
{{ANYTHING}}PLL 4:{{ANYTHING}} {{PLL 4}} Mhz
{{ANYTHING}}PCIE PLL:{{ANYTHING}} {{PCIE PLL}} Mhz
{{isPass}} pmgr show-clk
```

mem wr 32 0x2002003bc 0x0017006B
---------
- Command name : `mem wr 32 0x2002003bc 0x0017006B`
- Command to send: `mem wr 32 0x2002003bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2002003bc 0x0017006B
```

mem wr 32 0x2002403bc 0x0017006B
---------
- Command name : `mem wr 32 0x2002403bc 0x0017006B`
- Command to send: `mem wr 32 0x2002403bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2002403bc 0x0017006B
```

mem wr 32 0x2002803bc 0x0017006B
---------
- Command name : `mem wr 32 0x2002803bc 0x0017006B`
- Command to send: `mem wr 32 0x2002803bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2002803bc 0x0017006B
```

mem wr 32 0x2002c03bc 0x0017006B
---------
- Command name : `mem wr 32 0x2002c03bc 0x0017006B`
- Command to send: `mem wr 32 0x2002c03bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2002c03bc 0x0017006B
```

mem wr 32 0x2003003bc 0x0017006B
---------
- Command name : `mem wr 32 0x2003003bc 0x0017006B`
- Command to send: `mem wr 32 0x2003003bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2003003bc 0x0017006B
```

mem wr 32 0x2003403bc 0x0017006B
---------
- Command name : `mem wr 32 0x2003403bc 0x0017006B`
- Command to send: `mem wr 32 0x2003403bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2003403bc 0x0017006B
```

mem wr 32 0x2003803bc 0x0017006B
---------
- Command name : `mem wr 32 0x2003803bc 0x0017006B`
- Command to send: `mem wr 32 0x2003803bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2003803bc 0x0017006B
```

mem wr 32 0x2003c03bc 0x0017006B
---------
- Command name : `mem wr 32 0x2003c03bc 0x0017006B`
- Command to send: `mem wr 32 0x2003c03bc 0x0017006B`
```
{{isPass}} mem wr 32 0x2003c03bc 0x0017006B
```

mem wr 32 0x200220f38 0x0
---------
- Command name : `mem wr 32 0x200220f38 0x0`
- Command to send: `mem wr 32 0x200220f38 0x0`
```
{{isPass}} mem wr 32 0x200220f38 0x0
```

mem wr 32 0x200260f38 0x0
---------
- Command name : `mem wr 32 0x200260f38 0x0`
- Command to send: `mem wr 32 0x200260f38 0x0`
```
{{isPass}} mem wr 32 0x200260f38 0x0
```

mem wr 32 0x2002a0f38 0x0
---------
- Command name : `mem wr 32 0x2002a0f38 0x0`
- Command to send: `mem wr 32 0x2002a0f38 0x0`
```
{{isPass}} mem wr 32 0x2002a0f38 0x0
```

mem wr 32 0x2002e0f38 0x0
---------
- Command name : `mem wr 32 0x2002e0f38 0x0`
- Command to send: `mem wr 32 0x2002e0f38 0x0`
```
{{isPass}} mem wr 32 0x2002e0f38 0x0
```

mem wr 32 0x200320f38 0x0
---------
- Command name : `mem wr 32 0x200320f38 0x0`
- Command to send: `mem wr 32 0x200320f38 0x0`
```
{{isPass}} mem wr 32 0x200320f38 0x0
```

mem wr 32 0x200360f38 0x0
---------
- Command name : `mem wr 32 0x200360f38 0x0`
- Command to send: `mem wr 32 0x200360f38 0x0`
```
{{isPass}} mem wr 32 0x200360f38 0x0
```

mem wr 32 0x2003a0f38 0x0
---------
- Command name : `mem wr 32 0x2003a0f38 0x0`
- Command to send: `mem wr 32 0x2003a0f38 0x0`
```
{{isPass}} mem wr 32 0x2003a0f38 0x0
```

mem wr 32 0x2003e0f38 0x0
---------
- Command name : `mem wr 32 0x2003e0f38 0x0`
- Command to send: `mem wr 32 0x2003e0f38 0x0`
```
{{isPass}} mem wr 32 0x2003e0f38 0x0
```

fuse ecid
---------
 - Command name : `fuse ecid`
 - Command to send: `fuse ecid`
```
{{ANYTHING}}ECID Fuse : {{ANYTHING}}
{{ANYTHING}}  Lot ID  : {{ANYTHING}}
{{ANYTHING}}  Wafer   : {{ANYTHING}}
{{ANYTHING}}  X Pos   : {{ANYTHING}}
{{ANYTHING}}  Y Pos   : {{ANYTHING}}
{{isPass}} fuse ecid
```

fuse raw
---------
- Command name : `fuse raw`
- Command to send: `fuse raw`
```
{{ANYTHING}}cfg 0: {{cfg 0}}
{{ANYTHING}}cfg 1: {{cfg 1}}
{{ANYTHING}}cfg 2: {{cfg 2}}
{{ANYTHING}}cfg 3: {{cfg 3}}
{{ANYTHING}}cfg 4: {{cfg 4}}
{{ANYTHING}}cfg 5: {{cfg 5}}
{{ANYTHING}}cfg 6: {{cfg 6}}
{{ANYTHING}}cfg 7: {{cfg 7}}
{{ANYTHING}}cfg 8: {{cfg 8}}
{{ANYTHING}}cfg 9: {{cfg 9}}
{{ANYTHING}}cfg10: {{cfg10}}
{{ANYTHING}}cfg11: {{cfg11}}
{{ANYTHING}}cfg12: {{cfg12}}
{{ANYTHING}}cfg13: {{cfg13}}
{{ANYTHING}}cfg14: {{cfg14}}
{{ANYTHING}}cfg15: {{cfg15}}
{{ANYTHING}}
{{ANYTHING}}ecid 0: {{ecid 0}}
{{ANYTHING}}ecid 1: {{ecid 1}}
{{ANYTHING}}ecid 2: {{ecid 2}}
{{ANYTHING}}ecid 3: {{ecid 3}}
{{ANYTHING}}ecid 4: {{ecid 4}}
{{ANYTHING}}ecid 5: {{ecid 5}}
{{ANYTHING}}ecid 6: {{ecid 6}}
{{ANYTHING}}ecid 7: {{ecid 7}}
{{ANYTHING}}
{{ANYTHING}}dvfm 0: {{dvfm 0}}
{{ANYTHING}}dvfm 1: {{dvfm 1}}
{{ANYTHING}}dvfm 2: {{dvfm 2}}
{{ANYTHING}}dvfm 3: {{dvfm 3}}
{{ANYTHING}}dvfm 4: {{dvfm 4}}
{{ANYTHING}}dvfm 5: {{dvfm 5}}
{{ANYTHING}}dvfm 6: {{dvfm 6}}
{{ANYTHING}}dvfm 7: {{dvfm 7}}
{{ANYTHING}}dvfm 8: {{dvfm 8}}
{{ANYTHING}}dvfm 9: {{dvfm 9}}
{{ANYTHING}}dvfm10: {{dvfm10}}
{{ANYTHING}}dvfm11: {{dvfm11}}
{{ANYTHING}}dvfm12: {{dvfm12}}
{{ANYTHING}}dvfm13: {{dvfm13}}
{{ANYTHING}}dvfm14: {{dvfm14}}
{{ANYTHING}}dvfm15: {{dvfm15}}
{{ANYTHING}}
{{ANYTHING}}
{{isPass}} fuse raw
```


sense rd
---------
 - Command name : `sense rd`
 - Command to send: `sense rd`
```
{{ANYTHING}}T0{{ANYTHING}} cur {{ANYTHING}} max {{T0}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T1{{ANYTHING}} cur {{ANYTHING}} max {{T1}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T2{{ANYTHING}} cur {{ANYTHING}} max {{ANYTHING}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T3{{ANYTHING}} cur {{ANYTHING}} max {{T3}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T4{{ANYTHING}} cur {{ANYTHING}} max {{T4}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T5{{ANYTHING}} cur {{ANYTHING}} max {{T5}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T6{{ANYTHING}} cur {{ANYTHING}} max {{T6}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T7{{ANYTHING}} cur {{ANYTHING}} max {{T7}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T8{{ANYTHING}} cur {{ANYTHING}} max {{T8}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T9{{ANYTHING}} cur {{ANYTHING}} max {{T9}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T10{{ANYTHING}} cur {{ANYTHING}} max {{T10}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T11{{ANYTHING}} cur {{ANYTHING}} max {{T11}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T12{{ANYTHING}} cur {{ANYTHING}} max {{T12}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}T13{{ANYTHING}} cur {{ANYTHING}} max {{T13}} {{ANYTHING}}oC{{ANYTHING}}
{{ANYTHING}}DDR: cur {{ANYTHING}}=<{{DDR}} oC
{{isPass}} sense rd
```

sense reset
---------
 - Command name : `sense reset`
 - Command to send: `sense reset`
```
{{isPass}} sense reset
```


sc run 5
---------
 - Command name : `sc run 5`
 - Command to send: `sc run 5`
```
{{ANYTHING}}Scenario 5 {{Result}} 1
{{isPass}} sc run 5
```

sc run 58
---------
 - Command name : `sc run 58`
 - Command to send: `sc run 58`
```
{{ANYTHING}}Scenario 58 {{Result}} 1
{{isPass}} sc run 58
```

sc run 13 50
---------
 - Command name : `sc run 13 50`
 - Command to send: `sc run 13 50`
```
{{ANYTHING}}Scenario 13 {{Result}} 50
{{isPass}} sc run 13 50
```

sc run 49
---------
 - Command name : `sc run 49`
 - Command to send: `sc run 49`
```
{{ANYTHING}}Scenario 49 {{Result}} 1
{{isPass}} sc run 49
```

sc run 30
---------
 - Command name : `sc run 30`
 - Command to send: `sc run 30`
```
{{ANYTHING}}Scenario 30 {{Result}} 1
{{isPass}} sc run 30
```

sc run 35
---------
 - Command name : `sc run 35`
 - Command to send: `sc run 35`
```
{{ANYTHING}}Scenario 35 {{Result}} 1
{{isPass}} sc run 35
```

sc run 19 10
---------
 - Command name : `sc run 19 10`
 - Command to send: `sc run 19 10`
```
{{ANYTHING}}Scenario 19 {{Result}} 10
{{isPass}} sc run 19 10
```

sc run 19 100
---------
 - Command name : `sc run 19 100`
 - Command to send: `sc run 19 100`
```
{{ANYTHING}}Scenario 19 {{Result}} 100
{{isPass}} sc run 19 100
```

sc run 54
---------
 - Command name : `sc run 54`
 - Command to send: `sc run 54`
```
{{ANYTHING}}Scenario 54 {{Result}} 1
{{isPass}} sc run 54
```

sc run 46
---------
 - Command name : `sc run 46`
 - Command to send: `sc run 46`
```
{{ANYTHING}}Scenario 46 {{Result}} 1
{{isPass}} sc run 46
```

sc run 55
---------
 - Command name : `sc run 55`
 - Command to send: `sc run 55`
```
{{ANYTHING}}Scenario 55 {{Result}} 1
{{isPass}} sc run 55
```

sc run 56
---------
 - Command name : `sc run 56`
 - Command to send: `sc run 56`
```
{{ANYTHING}}Scenario 56 {{Result}} 1
{{isPass}} sc run 56
```

sc run 6 10
---------
 - Command name : `sc run 6 10`
 - Command to send: `sc run 6 10`
```
{{ANYTHING}}Scenario 6 {{Result}} 10
{{isPass}} sc run 6 10
```

sc run 6 50
---------
 - Command name : `sc run 6 50`
 - Command to send: `sc run 6 50`
```
{{ANYTHING}}Scenario 6 {{Result}} 50
{{isPass}} sc run 6 50
```

sc run 61
---------
 - Command name : `sc run 61`
 - Command to send: `sc run 61`
```  
{{ANYTHING}}Scenario 61 {{Result}} 1
{{isPass}} sc run 61
```

sc run 603
---------
 - Command name : `sc run 603`
 - Command to send: `sc run 603`
```
{{ANYTHING}}Scenario 603 {{Result}} 1
{{isPass}} sc run 603
```

sc run 700
---------
 - Command name : `sc run 700`
 - Command to send: `sc run 700`
```
{{ANYTHING}}Scenario 700 {{Result}} 1
{{isPass}} sc run 700
```

fs mount 0x813e00000
--------------
 - Command name : `fs mount 0x813e00000`
 - Command to send : `fs mount 0x813e00000`
```
{{isPass}} fs mount 0x813e00000
```

fs mount ddr
--------------
 - Command name : `fs mount ddr`
 - Command to send : `fs mount ddr`
```
{{isPass}} fs mount ddr
```

fs volumes
--------------
 - Command name : `fs volumes`
 - Command to send : `fs volumes`
```
{{isPass}} fs volumes
```

os jitter 10
--------------
 - Command name : `os jitter 10`
 - Command to send : `os jitter 10`
```
{{isPass}} os jitter 10
```

sense thread resume
--------------
 - Command name : `sense thread resume`
 - Command to send : `sense thread resume`
```
{{isPass}} sense thread resume
```

xfer drm
--------------
 - Command name : `xfer drm`
 - Command to send : `xfer drm`
```
{{ANYTHING}}{{isPass}} xfer drm
```

xfer con
--------------
 - Command name : `xfer con`
 - Command to send : `xfer con`
```
{{isPass}} xfer con
```

ddr margin test 0x303 50
---------
 - Command name : `ddr margin test 0x303 50`
 - Command to send: `ddr margin test 0x303 50`
```
{{ANYTHING}} 60 {{ANYTHING}} {{output time}}msec 1:1 {{Result}}
{{isPass}} ddr margin test 0x303 50
```

mem rd 64 0x202f200b0
---------
 - Command name : `mem rd 64 0x202f200b0`
 - Command to send: `mem rd 64 0x202f200b0`
```
{{ANYTHING}} 0000000202F200B0: {{ANYTHING}}{{bin_number/[\w]{2}/}}{{ANYTHING/[\w]{4}/}}{{ANYTHING/[\W]*/}}
```

sc coremask 0x06
---------
 - Command name : `sc coremask 0x06`
 - Command to send: `sc coremask 0x06`
```
{{isPass}} sc coremask 0x06
```

sc coremask 0x04
---------
 - Command name : `sc coremask 0x04`
 - Command to send: `sc coremask 0x04`
```
{{isPass}} sc coremask 0x04
```

sc coremask 0x02
---------
 - Command name : `sc coremask 0x02`
 - Command to send: `sc coremask 0x02`
```
{{isPass}} sc coremask 0x02
```

sc coremask 0x0800
---------
 - Command name : `sc coremask 0x0800`
 - Command to send: `sc coremask 0x0800`
```
{{isPass}} sc coremask 0x0800
```

find bin
---------
 - Command name : `find bin`
 - Command to send: `mem rd 64 0x202f200b0`
```
{{ANYTHING}} 0000000202F200B0: {{ANYTHING}}{{bin_number/[\w]{2}/}}{{ANYTHING/[\w]{4}/}}{{ANYTHING/[\W]*/}}
{{isPass}} mem rd 64 0x202f200b0
```

sense sochot
---------
 - Command name : `sense sochot`
 - Command to send: `sense sochot`
```
{{isPass}} sense sochot
```

sense sochot on
---------
 - Command name : `sense sochot on`
 - Command to send: `sense sochot on`
```
{{isPass}} sense sochot on
```

sense sochot 110
---------
 - Command name : `sense sochot 110`
 - Command to send: `sense sochot 110`
```
{{isPass}} sense sochot 110
```

sense sochot 115
---------
 - Command name : `sense sochot 115`
 - Command to send: `sense sochot 115`
```
{{isPass}} sense sochot 115
```

sense toohot 105 105 6
---------
 - Command name : `sense toohot 105 105 6`
 - Command to send: `sense toohot 105 105 6`
```
{{isPass}} sense toohot 105 105 6
```

sense toohot 100 100 6
---------
 - Command name : `sense toohot 100 100 6`
 - Command to send: `sense toohot 100 100 6`
```
{{isPass}} sense toohot 100 100 6
```

sense thread
---------
 - Command name : `sense thread`
 - Command to send: `sense thread`
```
{{isPass}} sense thread
```

sc run 83
---------
 - Command name : `sc run 83`
 - Command to send: `sc run 83`
```
{{ANYTHING}}Scenario 83 {{Result}} 1
{{isPass}} sc run 83
```

tc run 129 1 0 3 500
---------
 - Command name : `tc run 129 1 0 3 500`
 - Command to send: `tc run 129 1 0 3 500`
```
{{ANYTHING}}Scenario 0 {{Result}} 1
{{isPass}} tc run 129 1 0 3 500
```

tc run 129 1 0 2 500
---------
 - Command name : `tc run 129 1 0 2 500`
 - Command to send: `tc run 129 1 0 2 500`
```
{{ANYTHING}}Scenario 0 {{Result}} 1
{{isPass}} tc run 129 1 0 2 500
```

tc run 129 1 0 1 500
---------
 - Command name : `tc run 129 1 0 1 500`
 - Command to send: `tc run 129 1 0 1 500`
```
{{ANYTHING}}Scenario 0 {{Result}} 1
{{isPass}} tc run 129 1 0 1 500
```

slave down gfx
---------
 - Command name : `slave down gfx`
 - Command to send: `slave down gfx`
```
{{isPass}} slave down gfx
```

hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee -u
---------
 - Command name : `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee -u`
 - Command to send: `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee -u`
```
{{ANYTHING}}TEST_RESULT{{ANYTHING}} {{Result}}
{{isPass}} hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee -u
```

hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee
---------
- Command name : `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee`
- Command to send: `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee`
```
{{ANYTHING}}TEST_RESULT{{ANYTHING}} {{Result}}
{{isPass}} hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 40 -t 5 -s 0x4b1ddecafc0ffee
```

ddr dcal off
---------
- Command name : `ddr dcal off`
- Command to send: `ddr dcal off`
```
{{isPass}} ddr dcal off
```

ddr vdcal off
---------
- Command name : `ddr vdcal off`
- Command to send: `ddr vdcal off`
```
{{isPass}} ddr vdcal off
```


mem wr 32 0x200220e58 0x10
---------
- Command name : `mem wr 32 0x200220e58 0x10`
- Command to send: `mem wr 32 0x200220e58 0x10`
```
{{isPass}} mem wr 32 0x200220e58 0x10
```

mem wr 32 0x200220e60 0x10
---------
- Command name : `mem wr 32 0x200220e60 0x10`
- Command to send: `mem wr 32 0x200220e60 0x10`
```
{{isPass}} mem wr 32 0x200220e60 0x10
```


mem wr 32 0x200260e58 0x10
---------
- Command name : `mem wr 32 0x200260e58 0x10`
- Command to send: `mem wr 32 0x200260e58 0x10`
```
{{isPass}} mem wr 32 0x200260e58 0x10
```

mem wr 32 0x200260e60 0x10
---------
- Command name : `mem wr 32 0x200260e60 0x10`
- Command to send: `mem wr 32 0x200260e60 0x10`
```
{{isPass}} mem wr 32 0x200260e60 0x10
```


mem wr 32 0x2002a0e58 0x10
---------
- Command name : `mem wr 32 0x2002a0e58 0x10`
- Command to send: `mem wr 32 0x2002a0e58 0x10`
```
{{isPass}} mem wr 32 0x2002a0e58 0x10
```

mem wr 32 0x2002a0e60 0x10
---------
- Command name : `mem wr 32 0x2002a0e60 0x10`
- Command to send: `mem wr 32 0x2002a0e60 0x10`
```
{{isPass}} mem wr 32 0x2002a0e60 0x10
```


mem wr 32 0x2002e0e58 0x10
---------
- Command name : `mem wr 32 0x2002e0e58 0x10`
- Command to send: `mem wr 32 0x2002e0e58 0x10`
```
{{isPass}} mem wr 32 0x2002e0e58 0x10
```

mem wr 32 0x2002e0e60 0x10
---------
- Command name : `mem wr 32 0x2002e0e60 0x10`
- Command to send: `mem wr 32 0x2002e0e60 0x10`
```
{{isPass}} mem wr 32 0x2002e0e60 0x10
```


mem wr 32 0x200320e58 0x10
---------
- Command name : `mem wr 32 0x200320e58 0x10`
- Command to send: `mem wr 32 0x200320e58 0x10`
```
{{isPass}} mem wr 32 0x200320e58 0x10
```

mem wr 32 0x200320e60 0x10
---------
- Command name : `mem wr 32 0x200320e60 0x10`
- Command to send: `mem wr 32 0x200320e60 0x10`
```
{{isPass}} mem wr 32 0x200320e60 0x10
```


mem wr 32 0x200360e58 0x10
---------
- Command name : `mem wr 32 0x200360e58 0x10`
- Command to send: `mem wr 32 0x200360e58 0x10`
```
{{isPass}} mem wr 32 0x200360e58 0x10
```

mem wr 32 0x200360e60 0x10
---------
- Command name : `mem wr 32 0x200360e60 0x10`
- Command to send: `mem wr 32 0x200360e60 0x10`
```
{{isPass}} mem wr 32 0x200360e60 0x10
```


mem wr 32 0x2003a0e58 0x10
---------
- Command name : `mem wr 32 0x2003a0e58 0x10`
- Command to send: `mem wr 32 0x2003a0e58 0x10`
```
{{isPass}} mem wr 32 0x2003a0e58 0x10
```

mem wr 32 0x2003a0e60 0x10
---------
- Command name : `mem wr 32 0x2003a0e60 0x10`
- Command to send: `mem wr 32 0x2003a0e60 0x10`
```
{{isPass}} mem wr 32 0x2003a0e60 0x10
```

mem wr 32 0x2003e0e58 0x10
---------
- Command name : `mem wr 32 0x2003e0e58 0x10`
- Command to send: `mem wr 32 0x2003e0e58 0x10`
```
{{isPass}} mem wr 32 0x2003e0e58 0x10
```

mem wr 32 0x2003e0e60 0x10
---------
- Command name : `mem wr 32 0x2003e0e60 0x10`
- Command to send: `mem wr 32 0x2003e0e60 0x10`
```
{{isPass}} mem wr 32 0x2003e0e60 0x10
```

mem test 0x303
---------
- Command name : `mem test 0x303`
- Command to send: `mem test 0x303`
```
{{ANYTHING}}Scenario 60 {{Result}} 1
{{isPass}} mem test 0x303
```

ddr vref reset
---------
- Command name : `ddr vref reset`
- Command to send: `ddr vref reset`
```
{{isPass}} ddr vref reset
```


ddr dcal on
---------
- Command name : `ddr dcal on`
- Command to send: `ddr dcal on`
```
{{isPass}} ddr dcal on
```

ddr vdcal on
---------
- Command name : `ddr vdcal on`
- Command to send: `ddr vdcal on`
```
{{isPass}} ddr vdcal on
```

ddr vref
---------
- Command name : `ddr vref`
- Command to send: `ddr vref`
```
{{isPass}} ddr vref
```

mem test -m 0x424F36D9F
---------
- Command name : `mem test -m 0x424F36D9F`
- Command to send: `mem test -m 0x424F36D9F`
```
{{ANYTHING}}Scenario 60 {{Result}} 1
{{isPass}} mem test -m 0x424F36D9F
```

mem test -m 0x424F32D9F
---------
- Command name : `mem test -m 0x424F32D9F`
- Command to send: `mem test -m 0x424F32D9F`
```
{{ANYTHING}}Scenario 60 {{Result}} 1
{{isPass}} mem test -m 0x424F32D9F
```

hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 20 -t 5 -s 0x4b1ddecafc0ffee
---------
- Command name : `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 20 -t 5 -s 0x4b1ddecafc0ffee`
- Command to send: `hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 20 -t 5 -s 0x4b1ddecafc0ffee`
```
{{ANYTHING}}TEST_RESULT{{ANYTHING}} {{Result}}
{{isPass}} hammer -fmc 0x7 -urbm 0x7 -bonfire 0x7 -msr -l 20 -t 5 -s 0x4b1ddecafc0ffee
```
switcher off -reset
---------
- Command name : `switcher off -reset`
- Command to send: `switcher off -reset`
```
{{isPass}} switcher off -reset
```
