EFI parsing definition file
===========================

Version Info
------------
AUGUST 22, 2015 ver01

[TOC]

Commands that can be parsed
===========================

version
--------
 - Command name: `version`
 - Command to send: `version`
```
{{ANYTHING}}
{{ANYTHING}}. Revision {{ANYTHING}}.
{{ANYTHING}}Built at {{ANYTHING}}
```

boardrev
--------
 - Command name: `boardrev`
 - Command to send: `boardrev`
```
Board Revision: {{ANYTHING}}
```

boardid
--------
 - Command name: `boardid`
 - Command to send: `boardid`
```
Board Id: {{boardid}}
```

soc -p
--------
 - Command name: `soc -p`
 - Command to send: `soc -p`
```
{{ANYTHING}}vendor: Apple
{{ANYTHING}}model: {{model}}
{{ANYTHING}}fuse-rev: {{fuse-re}} 
{{ANYTHING}}primary-cpu: {{ANYTHING}}
{{ANYTHING}}security-epoch: {{ANYTHING}}
{{ANYTHING}}security-domain: {{ANYTHING}}
{{ANYTHING}}production-mode: {{ANYTHING}}
{{ANYTHING}}board-id: {{ANYTHING}}
{{ANYTHING}}io-leakage-bin-fuse: {{io-leakage-bin-fuse}}
{{ANYTHING}}cpu-sram-io-leakage-bin-fuse: {{ANYTHING}}
{{ANYTHING}}gpu-sram-io-leakage-bin-fuse: {{ANYTHING}}
{{ANYTHING}}vdd-low-io-leakage-bin-fuse: {{ANYTHING}}
{{ANYTHING}}vdd-fixed-io-leakage-bin-fuse: {{vdd-fixed-io-leakage-bin-fuse}}
{{ANYTHING}}cpu-io-leakage-bin-fuse: {{cpu-io-leakage-bin-fuse}}
{{ANYTHING}}vdd-var-soc-io-leakage-bin-fuse: {{vdd-var-soc-io-leakage-bin-fuse}}
{{ANYTHING}}gpu-io-leakage-bin-fuse: {{gpu-io-leakage-bin-fuse}}
{{ANYTHING}}binning-revision: {{binning-revision}}
{{ANYTHING}}efi-memory-size: {{ANYTHING}}
{{ANYTHING}}revision: {{CPRV}}
{{ANYTHING}}prod-id:{{ANYTHING}}
{{ANYTHING}}secure-mode: {{ANYTHING}}
{{ANYTHING}}secure-storage: {{ANYTHING}}
{{ANYTHING}}package-id: {{ANYTHING}}
{{ANYTHING}}dram-memory-vendor: {{ANYTHING}}
{{ANYTHING}}dram-memory-type: {{ANYTHING}}
{{ANYTHING}}dram-memory-density: {{ANYTHING}}
{{ANYTHING}}dram-memory-io-width: {{ANYTHING}}
{{ANYTHING}}memctlr-cfg-channels: {{ANYTHING}}
{{ANYTHING}}memctlr-cfg-size: {{ANYTHING}}
```

sn
--------
 - Command name: `sn`
 - Command to send: `sn`
```
Serial: {{ANYTHING}}
```

syscfg print MLB#
--------
 - Command name: `syscfg print MLB#`
 - Command to send: `syscfg print MLB#`
```
{{MLB_CMD}}
{{MLB_Num}}
```

syscfg print CFG#
--------
 - Command name: `syscfg print CFG#`
 - Command to send: `syscfg print CFG#`
```
{{CFG_CMD}}
{{CFG}}
```

RTC__SET
--------
 - Command name: `RTC__SET`
 - Command to send: `RTC__SET`
```
:-)
```

cbwrite 0x02 incomplete
--------
 - Command name: `cbwrite 0x02 incomplete`
 - Command to send: `cbwrite 0x02 incomplete`
```
:-)
```

pmuadc --read all
--------
 - Command name: `pmuadc --read all`
 - Command to send: `pmuadc --read all`
```
{{ANYTHING}}
```

cb read 2
--------
 - Command name: `cb read 2`
 - Command to send: `cb read 2`
```
{{station}} {{state}} {{rel_fail_ct}} {{abs_fail_ct}} {{erase_ct}} {{test-time}} {{sw-version}}
```

enterDiags
--------
 - Command name: `enterDiags`
 - Command to send: `echo enterDiags`
```
enterDiags
```

enterrbm
--------
 - Command name: `enterrbm`
 - Command to send: `echo enterrbm`
```
{{ANYTHING}}
```

enterrtos
--------
 - Command name: `enterrtos`
 - Command to send: `echo enterrtos`
```
{{ANYTHING}}
```


Future commands to be parsed
----------------------------
