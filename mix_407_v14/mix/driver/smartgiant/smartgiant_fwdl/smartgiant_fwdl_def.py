
class SmartGiantFWDLDef():
    # path of smartgiant_fwdl_chip_config.json
    CHIP_CONFIG_FULL_NAME = "/mix/driver/smartgiant/smartgiant_fwdl/config/smartgiant_fwdl_chip_config.json"
    # smartgiant fwdl process full name
    FWDL_PROCESS = "/usr/local/bin/dfu_rpc_server"
    # log path of smartgiant fwdl
    FWDL_LOG_PATH = "/var/log/smartgiant_fwdl/"
    FWDL_LOG_MAX_SIZE = 10 * 1024 * 1024  # unit is Byte
    # smartgiant fwdl library path
    FWDL_LIB_PATH = "/usr/local/lib/smartgiant_fwdl/"
    # FW MD5 file
    FIRMWARE_MD5_FILE = "firmware.md5"

    # support chips.
    SPI_CHIPS = ["at25s128", "mx25u512", "w25q80", "w25q64", "w25q128", "w25q256", "w25x20", "mx25u", "mt25quxxx",
                 "s25l", "mx25u32", "mx25l400", "gd25le32", "mx25v16", "nandflash", "gd25lf255", "at25xxx",
                 "gd25xxx"]
    QPI_CHIPS = ["q_w25q128", "q_gd25l128", "q_at25s128", "q_w25q256", "q_mt25quxxx", "q_gd25le32"]
    SWD_CHIPS = ["psoc4000", "cypd5xxx", "cypd2xxx", "otp", "hearst", "cy8c4248", "stm32l4xx", "stm32l0xx",
                 "stm32l052", "stm32l0xxxB", "stm32f4xx", "stm32f0xx", "nrf51xxx", "nrf52xxx"]

    # default frequency
    SPI_DEFAULT_FREQ = 10000000
    SWD_DEFAULT_FREQ = 4000000

    # dfu server ip and port
    RPC_IP = "127.0.0.1"
    PORT = 6000

    # mcs lib 
    MCS_LIB = "/usr/local/lib/smartgiant_fwdl/libsmartgiant-fwdl-mcs.so"