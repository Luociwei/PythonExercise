# -*- coding: utf-8 -*-
import re
import os
import ctypes
import shutil
import hashlib
import subprocess
from tinyrpc.client import XavierRpcClient
from smartgiant_fwdl_def import SmartGiantFWDLDef
from programmer.dfuapp.dfu_app import ProgApp
from mix.driver.core.bus.axi4_lite_def import PLSPIDef
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG


__author__ = 'jinkun.lin@SmartGiant'
__version__ = '0.3'


class FWDLException(Exception):
    def __init__(self, chip, err_str):
        self.reason = "[{}] {}".format(chip, err_str)

    def __str__(self):
        return self.reason


class SmartGiantFWDL():
    '''
    SmartGiantFWDL class provide function erase dut's flash and program.

    :param slot_id: int,            slot id<1, 2, 3, 4...>
    :param spi:     string,         spi device fullname.
    :param spi_freq:int,            spi frequency, unit Hz, default 10000000.
    :param spi_mode:string,         ['MODE0', 'MODE1', 'MODE2', 'MODE3'], CPOL and CPHA mode, default MODE0.
    :param swd:     string,         swd device fullname.
    :param swd_freq:int,            swd frequency, unit Hz, default 4000000.

    :example:
                    fwdl = SmartGiantFWDL(1, "/dev/MIX_QSPI_SG_0", 10000000, "MODE0")
    '''
    rpc_public_api = [
        'program_id', 'program', 'program_checkout', 'program_only',
        'program_readverify', 'program_erase',
        'program_firmware_check', 'program_firmware_erase', 'program_auto',
        'spi_mode_config', 'spi_prog_write_read', 'qpi_prog_write_read',
        'mcs2bin'
    ]

    def __init__(self, slot_id, spi=None, spi_freq=SmartGiantFWDLDef.SPI_DEFAULT_FREQ,
                 spi_mode='MODE0', swd=None, swd_freq=SmartGiantFWDLDef.SWD_DEFAULT_FREQ):
        assert isinstance(slot_id, int)
        assert spi is None or isinstance(spi, basestring)
        assert isinstance(spi_freq, int)
        assert spi_mode in ['MODE0', 'MODE1', 'MODE2', 'MODE3']
        assert swd is None or isinstance(swd, basestring)
        assert isinstance(swd_freq, int)
        assert swd or spi

        self._slot_id = slot_id
        self._spi = spi
        self._spi_clk_mode = spi_mode
        self._spi_clk_freq = spi_freq
        self._swd = swd
        self._swd_clk_freq = swd_freq
        self._port = SmartGiantFWDLDef.PORT + self._slot_id
        self._log_file_name = None

        # start fwdl process
        self._start_server_process()

    def _check_log_size(self):
        '''
        Check log file size
        If log file size out of MAX_SIZE, then clean
        '''
        if os.path.exists(self._log_file_name):
            size = os.path.getsize(self._log_file_name)
            if size >= SmartGiantFWDLDef.FWDL_LOG_MAX_SIZE:
                with open(self._log_file_name, 'r+') as file:
                    file.truncate()  # clean file

    def _start_server_process(self):
        # get library env
        env = os.getenv("LD_LIBRARY_PATH")
        if SmartGiantFWDLDef.FWDL_LIB_PATH not in env:
            # set legacy fwdl library env
            env += SmartGiantFWDLDef.FWDL_LIB_PATH
            os.environ["LD_LIBRARY_PATH"] = env

        process_name = "SmartGiantFWDL{}".format(self._slot_id)
        self._log_file_name = '{}/{}.log'.format(SmartGiantFWDLDef.FWDL_LOG_PATH, process_name)
        dfu_rpc_config = "{} {} {} >>{}".format(SmartGiantFWDLDef.RPC_IP, self._port, process_name, self._log_file_name)

        # then start the server
        os.system("mkdir -p {}".format(SmartGiantFWDLDef.FWDL_LOG_PATH))
        self._check_log_size()
        fwdl = subprocess.Popen("{} {}".format(SmartGiantFWDLDef.FWDL_PROCESS, dfu_rpc_config), shell=True)
        if fwdl.poll() is not None:
            strout, strerr = fwdl.communicate()
            if strerr:
                raise FWDLException(process_name, "{}".format(strerr))

    def _set_profile_path(self):
        '''
        Set profile path, path define by SmartGiantFWDLDef.CHIP_CONFIG_FULL_NAME.
        This function only use by self.

        :return:        None
        :example:
                        fwdl._set_profile_path()
        '''
        rpc_client = self._get_prog_rpc_node()
        params = {"config_file_name": SmartGiantFWDLDef.CHIP_CONFIG_FULL_NAME}
        rpc_client.call("SetChipConfigureFileName", **params)

    def _get_dev_path(self, chip):
        '''
        Get chip device path.
        This function only use by self.

        :param chip:    str,        chip name.
        :return:        str,        device path
        :raises FWDLException:      Raise exception when chip does not support or device does not exist.
        :example:
                        print fwdl._get_dev_path("stm32l4xx")
        '''

        if chip in SmartGiantFWDLDef.SWD_CHIPS:
            if not os.path.exists(self._swd):
                raise FWDLException(chip, "Device[%s] does not exist" % (self._swd))
            return self._swd, self._swd_clk_freq
        elif chip in SmartGiantFWDLDef.SPI_CHIPS or chip in SmartGiantFWDLDef.QPI_CHIPS:
            if not os.path.exists(self._spi):
                raise FWDLException(chip, "Device[%s] does not exist" % (self._spi))
            return self._spi, self._spi_clk_freq
        else:
            raise FWDLException(chip, "Does not support")

    def _get_prog_rpc_node(self):
        '''
        Get RPC Client instance.
        This function only use by self.

        :return:        instance<XavierRpcClient>,        rpc client instance.
        :raises FWDLException:      Raise exception when chip does not support or device does not exist.
        :example:
                        rpc = fwdl._get_prog_rpc_node()
                        rpc.call(method, args, kwargs)
        '''

        return XavierRpcClient(SmartGiantFWDLDef.RPC_IP, self._port, "tcp")

    def _fwdl_executing_process(self, chip, executing_config_list=None):
        '''
        Call fwdl server function by RPC.
        This function only use by self.

        :param chip:                    str,                    chip name.
        :param executing_config_list:   list,                   method's list.
        :return:                        tuple<(boll, str)>,     True/False and result message
        :raises FWDLException:          Raise exception when chip does not support or device does not exist.
        :example:
                        executing_config_list = [{'process_name':erase_chip,target_addr':0,'size':65535}]
                        print fwdl._fwdl_executing_process("stm32l4xx", executing_config_list)
        '''
        program_state = True
        ret_str = ""
        # get channel dev path
        dev_path, freq = self._get_dev_path(chip)
        if dev_path is False:
            raise FWDLException(chip, "channel dev path is not exist!")

        self._check_log_size()
        self._set_profile_path()

        # get prog rpc node
        prog_rpc_node = self._get_prog_rpc_node()

        # get dfu instance
        prog_instance = ProgApp(prog_rpc_node)
        # create target
        prog_state, prog_str = prog_instance.create_target(dev_path, chip)
        ret_str += prog_str
        if prog_state is False:
            raise FWDLException(chip, ret_str)

        for index in range(0, len(executing_config_list)):
            process_info = executing_config_list[index]
            # set frequency
            prog_state, prog_str = prog_instance.target_driver_initial(freq)
            ret_str += prog_str
            if prog_state is False:
                return False, ret_str

            # executing processs
            if (process_info['process_name'] == "read_id") or (index == 0):
                prog_state, prog_str = prog_instance.target_initial()
                ret_str += prog_str
                if prog_state is False:
                    program_state = False
                    break

            if process_info['process_name'] == "erase_chip":
                if "size" in process_info.keys():
                    target_addr = process_info["target_addr"]
                    size = process_info["size"]
                    prog_state, prog_str = prog_instance.target_erase(target_addr, size, None)
                elif "target_file" in process_info.keys():
                    target_addr = process_info["target_addr"]
                    firmware_path = process_info["target_file"]
                    prog_state, prog_str = prog_instance.target_erase(target_addr, None, firmware_path)
                else:
                    # erase all
                    prog_state, prog_str = prog_instance.target_erase()

                ret_str += prog_str
                if prog_state is False:
                    program_state = False
                    break

            process_name_list = ["program_only", "verify", "program", "readverify", "program_auto"]

            if process_info['process_name'] in process_name_list:
                firmware_path = process_info["target_file"]
                target_addr = None

                if "target_addr" not in process_info.keys():
                    target_addr_group = self.config_list["chip_process_configure"]["program_only"]['default_addr']
                    for addr_key in target_addr_group.keys():
                        for item_chip in target_addr_group[addr_key]:
                            if item_chip == chip:
                                target_addr = addr_key
                                break

                    if target_addr is None:
                        ret_str += "do not have target address"
                        program_state = False
                        break
                else:
                    target_addr = process_info["target_addr"]

                if process_info['process_name'] == "program_only":
                    # programming only
                    prog_state, prog_str = prog_instance.target_programming_only(
                        firmware_path, process_info["size"], target_addr, process_info["file_offset"])
                    ret_str += prog_str
                    if prog_state is False:
                        program_state = False
                        break

                elif process_info['process_name'] == "program":
                    # programming
                    prog_state, prog_str = prog_instance.target_programming(
                        firmware_path, process_info["size"], target_addr, process_info["file_offset"], 1)
                    ret_str += prog_str
                    if prog_state is False:
                        program_state = False
                        break

                elif process_info['process_name'] == "program_auto":
                    # programming
                    prog_state, prog_str = prog_instance.target_programming_auto(
                        firmware_path, process_info["size"], target_addr, process_info["file_offset"])
                    ret_str += prog_str
                    if prog_state is False:
                        program_state = False
                        break

                elif process_info['process_name'] == "verify":
                    # verify
                    prog_state, prog_str = prog_instance.target_checkout(
                        firmware_path, process_info["size"], target_addr, process_info["file_offset"])
                    ret_str += prog_str
                    if prog_state is False:
                        program_state = False
                        break

                elif process_info['process_name'] == "readverify":
                    # readverify to read the target log
                    # firmware_path+=".readback"
                    os.system("touch %s" % firmware_path)
                    prog_state, prog_str = prog_instance.read_target_storage(
                        firmware_path, process_info["size"], target_addr)
                    ret_str += prog_str
                    if prog_state is False:
                        program_state = False
                        break

        prog_state, prog_str = prog_instance.release_target()
        ret_str += prog_str
        if prog_state is False:
            return False, ret_str

        prog_state, prog_str = prog_instance.destroy_target()
        ret_str += prog_str
        if prog_state is False:
            return False, ret_str

        if program_state is False:
            return False, ret_str

        return True, ret_str

    def _check_md5_with_md5file(self, md5file, firmware, fwname, m5d):
        with open(md5file, "r") as f:
            line = f.readline()
            while line:
                result = re.match(r'(\w+)[ ].+?(\S+)', line)
                if None is result:
                    return False
                read_m5d = result.group(1)
                read_fwname = result.group(2)
                if read_m5d == m5d and (read_fwname == firmware or read_fwname == fwname):
                    return True
                line = f.readline()
        return False

    def _firmware_md5_check(self, firmware):
        path, fullname = os.path.split(firmware)
        firmware_md5_file = "{}/{}".format(path, SmartGiantFWDLDef.FIRMWARE_MD5_FILE)
        if not os.path.exists(firmware_md5_file):
            raise FWDLException(firmware_md5_file, "MD5 file does not exist!")

        md5 = self.program_firmware_check(firmware)
        if not self._check_md5_with_md5file(firmware_md5_file, firmware, fullname, md5):
            raise FWDLException(firmware, "md5 {} does not match with {}!".format(md5, firmware_md5_file))

    def program_id(self, chip):
        '''
        Read chip id.

        :param chip:    str,        chip name
        :return:        str,        result of read id
        :raises FWDLException:      Raise exception when read id failed.
        :example:
                        result = fwdl.program_id("stm32l4xx")
                        print(result)
        '''
        assert chip
        assert isinstance(chip, basestring)

        executing_config_list = []
        executing_config_dict = {}
        executing_config_dict["process_name"] = "read_id"
        executing_config_list.append(executing_config_dict)

        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)

        return prog_str

    def _get_firmware_info_list(self, firmware, target_addr):
        fw_infor_list = []
        if os.path.isdir(firmware):
            files = os.listdir(firmware)
            for file in files:
                if '.bin' not in file:
                    continue
                addr = target_addr + int(file.split(".bin")[0], 16)
                fw_infor_list.append({"firmware": "{}/{}".format(firmware, file), "target_addr": addr})
            if not fw_infor_list:
                raise FWDLException(firmware, "Have not any binary FW files!")
        else:
            fw_infor_list.append({"firmware": firmware, "target_addr": target_addr})

        return fw_infor_list

    def _create_program_process_list(self, type, firmware, target_addr):
        fw_infor_list = self._get_firmware_info_list(firmware, target_addr)
        executing_config_list = []
        for fw_infor in fw_infor_list:
            self._firmware_md5_check(fw_infor["firmware"])
            executing_config_dict = {}
            executing_config_dict["process_name"] = type
            executing_config_dict["target_addr"] = fw_infor["target_addr"]
            executing_config_dict["target_file"] = fw_infor["firmware"]
            executing_config_dict["file_offset"] = 0
            executing_config_dict["size"] = os.path.getsize(fw_infor["firmware"])
            executing_config_list.append(executing_config_dict)

        return executing_config_list

    def program(self, chip, firmware, target_addr):
        '''
        Program dut's flash, if flash not null, will erase it before program.

        :param chip:        str,        chip name
        :param firmware:    str,        Fullname with path and firmware name.
        :param target_addr: int,        Start position of Dut's flash which will be program
        :return:            str,        result of program
        :raises FWDLException:          Raise exception when firmware does not exist or program failed.
        :example:
                        print fwdl.program("stm32l4xx", "/mix/out.bin", 0x0)
        '''
        assert chip
        assert isinstance(chip, basestring)
        assert os.path.exists(firmware)
        assert target_addr >= 0

        executing_config_list = self._create_program_process_list("program", firmware, target_addr)
        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)

        # fwdl_executing_str idcode
        return prog_str

    def program_checkout(self, chip, firmware, target_addr):
        '''
        Checkout firmware data with dut's flash.

        :param chip:        str,        chip name
        :param firmware:    str,        Fullname with path and firmware name.
        :param target_addr: int,        Start position of Dut's flash which will be check
        :return:            str,        result of check
        :raises FWDLException:          Raise exception when firmware does not exist or check failed.
        :example:
                        print fwdl.program_checkout("stm32l4xx", "/mix/out.bin", 0x0)
        '''
        assert chip
        assert isinstance(chip, basestring)
        assert os.path.exists(firmware)
        assert target_addr >= 0

        executing_config_list = self._create_program_process_list("verify", firmware, target_addr)
        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)
        # fwdl_executing_str idcode
        return prog_str

    def program_only(self, chip, firmware, target_addr):
        '''
        Program dut's flash, use this function, must erase chip flash before.

        :param chip:        str,        chip name
        :param firmware:    str,        Fullname with path and firmware name.
        :param target_addr: int,        Start position of Dut's flash which will be program
        :return:            str,        result of program
        :raises FWDLException:          Raise exception when firmware does not exist or program failed.
        :example:
                        fwdl.program_erase("stm32l4xx")
                        print fwdl.program_only("stm32l4xx", "/mix/out.bin", 0x0)
        '''
        assert chip
        assert isinstance(chip, basestring)
        assert os.path.exists(firmware)
        assert target_addr >= 0

        executing_config_list = self._create_program_process_list("program_only", firmware, target_addr)
        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)
        # fwdl_executing_str idcode
        return prog_str

    def program_readverify(self, chip, firmware, target_addr, size):
        '''
        Read verify dut's flash data.

        :param chip:        str,        chip name
        :param firmware:    str,        Fullname with path and firmware name.
        :param target_addr: int,        Start position of Dut's flash which will be read verify
        :param size:        int,        Data length will be read verify.
        :return:            str,        result of read verify
        :raises FWDLException:          Raise exception when firmware does not exist or read verify failed.
        :example:
                        fwdl.program_erase("stm32l4xx")
                        print fwdl.program_only("stm32l4xx", "/mix/out.bin", 0x0)
        '''
        assert chip
        assert isinstance(chip, basestring)
        assert firmware
        assert target_addr >= 0
        assert size > 0

        executing_config_list = []
        executing_config_dict = {}
        executing_config_dict["process_name"] = "readverify"
        executing_config_dict["target_addr"] = target_addr
        executing_config_dict["target_file"] = "{}.readback".format(firmware)
        executing_config_dict["size"] = size
        executing_config_list.append(executing_config_dict)

        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)
        # fwdl_executing_str idcode
        return prog_str

    def program_erase(self, chip, target_addr=None, size=None):
        '''
        Erase dut's flash.

        :param chip:        str,        chip name
        :param target_addr: int,        Start position of Dut's flash which will be erase,
                                        if None, it will erase the whole flash.
        :param size:        int,        Data length will be erase.
        :return:            str,        result of erase
        :raises FWDLException:          Raise exception when erase failed.
        :example:
                        print fwdl.program_erase("stm32l4xx")
        '''
        assert chip
        assert isinstance(chip, basestring)

        executing_config_list = []
        executing_config_dict = {}
        executing_config_dict["process_name"] = "erase_chip"
        if target_addr is not None and size is not None:
            executing_config_dict["target_addr"] = target_addr
            executing_config_dict["size"] = size

        executing_config_list.append(executing_config_dict)

        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)
        # fwdl_executing_str idcode
        return prog_str

    def program_firmware_check(self, firmware):
        '''
        Read verify dut's flash data.

        :param firmware:    str,        Fullname with path and firmware name.
                                        if None, will get all file's md5 which in channel path
        :return:            str,        result of firmware md5
        :example:
                        print fwdl.program_firmware_check("/mix/out.bin")
        '''
        assert os.path.isfile(firmware)

        md5 = hashlib.md5()
        with open(firmware) as f:
            line = f.read(8192)
            while line:
                md5.update(line)
                line = f.read(8192)
        return md5.hexdigest()

    def program_firmware_erase(self, firmware):
        '''
        Delete channel path firmware.

        :param firmware:    str,        File of firmware name
        :return:            None
        :example:
                            fwdl.program_firmware_erase("out.bin")
        '''
        assert os.path.isfile(firmware)

        os.system("rm -f {}".format(firmware))

    def program_auto(self, chip, firmware=None, target_addr=None):
        '''
        If firmware is None, the function as same as program_id.
        Otherwise the function will program dut's flash after erase. And faster than program.

        :param chip:        str,        chip name
        :param firmware:    str,        Fullname with path and firmware name.
        :param target_addr: int,        Start position of Dut's flash which will be erase and program
        :param return:      str,        result of program_auto
        :raises FWDLException:          Raise exception when firmware does not exist or failed.
        :example:
                        print fwdl.program_auto("at25s128", "/mix/out.bin", 0x1000)
        '''
        assert chip
        assert isinstance(chip, basestring)

        if firmware:
            if not os.path.exists(firmware):
                raise FWDLException(chip, "target firmware file[%s] is not exist !" % (firmware))

            executing_config_list = self._create_program_process_list("program_auto", firmware, target_addr)
        else:
            executing_config_list = []
            executing_config_dict = {}
            executing_config_dict["process_name"] = "read_id"
            executing_config_list.append(executing_config_dict)

        prog_state, prog_str = self._fwdl_executing_process(chip, executing_config_list)
        if prog_state is False:
            raise FWDLException(chip, prog_str)
        return prog_str

    def spi_mode_config(self, spi_clk_mode, spi_clk_freq):
        '''
        spi mode config

        :param spi_clk_mode:       string,
                                            'MODE0': CPOL=0, CPHA=0
                                            'MODE1': CPOL=0, CPHA=1
                                            'MODE2': CPOL=1, CPHA=0
                                            'MODE3': CPOL=1, CPHA=1
        :param spi_clk_freq:       int,     range is 2000~20000000 Hz Hz
        '''
        assert spi_clk_mode in PLSPIDef.SPI_MODES
        assert isinstance(spi_clk_freq, int)
        assert spi_clk_freq >= 2000
        assert spi_clk_freq <= 20000000

        self._spi_clk_mode = spi_clk_mode
        self._spi_clk_freq = spi_clk_freq

    def spi_prog_write_read(self, wr_data_list):
        """
        spi programmer write and read

        :param wr_data_list:        list,           spi write data list(byte) , len 1~2048
        :param return:              list,           read data
        """
        assert isinstance(wr_data_list, list)

        spi_bus = self._spi_prog_open()

        mode = spi_bus.get_work_mode()
        spi_bus.set_work_mode(PLSPIDef.SPI_MODE)
        try:
            ret = spi_bus.sync_transfer(wr_data_list)
            return ret
        except Exception as e:
            raise e
        finally:
            spi_bus.set_work_mode(mode)

    def qpi_prog_write_read(self, wr_data_list, read_len):
        """
        qspi programmer write and read

        :param wr_data_list:        list,       spi write data list(byte)
        :param read_len:            int,        spi read byte length, range 1~2048
        :param return:              list,       read data
        """
        assert isinstance(wr_data_list, list)
        write_len = len(wr_data_list)
        assert write_len > 0
        assert read_len > 0

        spi_bus = self._spi_prog_open()

        mode = spi_bus.get_work_mode()
        spi_bus.set_work_mode(PLSPIDef.QPI_MODE)
        try:
            read_list = spi_bus.async_transfer(wr_data_list, read_len)
            return read_list
        except Exception as e:
            raise e
        finally:
            spi_bus.set_work_mode(mode)

    def _spi_prog_open(self):
        """
        spi module create and init
        """
        axi4_bus = AXI4LiteBus(self._spi, PLSPIDef.REG_SIZE)
        spi_bus = MIXQSPISG(axi4_bus)
        spi_bus.close()
        spi_bus.open()
        spi_bus.set_mode(self._spi_clk_mode)
        spi_bus.set_speed(self._spi_clk_freq)
        return spi_bus

    def _store_checksum(self, output):
        md5_fd = os.open("{}/{}".format(output, SmartGiantFWDLDef.FIRMWARE_MD5_FILE), os.O_WRONLY | os.O_CREAT)
        files = os.listdir(output)
        for _bin in files:
            if ".bin" not in _bin:
                continue
            md5 = hashlib.md5()
            with open("{}/{}".format(output, _bin), "r") as f:
                line = f.read(8192)
                while line:
                    md5.update(line)
                    line = f.read(8192)
            os.write(md5_fd, "{}  {}\n".format(md5.hexdigest(), _bin))
        os.close(md5_fd)

    def mcs2bin(self, input, output=None, pad_word=0xFF, swap=False):
        """
        Analysis the mcs file and generates multiple binary files and firmware.md5.

        :param input:               str,        Input mcs file.
        :param output:              str,        Output path.
        :param pad_word:            int,        Pad byte, while the mcs data is null. Range: 0~255.
        :param swap:                bool,       Swap wordwise.

        :raises FWDLException:          Raise exception when analysis mcs failed.
        :example:
                        fwdl.mcs2bin("/root/supernova_1_41_681.mcs")
        """
        assert input
        assert isinstance(input, basestring)
        assert os.path.isfile(input)
        assert isinstance(pad_word, int)
        assert 0 <= pad_word
        assert 256 > pad_word
        assert swap in [True, False]

        libmcs = ctypes.CDLL(SmartGiantFWDLDef.MCS_LIB)

        _input = ctypes.create_string_buffer(input)

        if output:
            _out = output
        else:
            path, file = os.path.split(input)
            if path:
                _out = "{}/output".format(path)
            else:
                _out = "output"
        _output = ctypes.create_string_buffer(_out)

        if swap:
            _swap = 1
        else:
            _swap = 0

        if os.path.isdir(_out):
            shutil.rmtree(_out)

        if libmcs.mcs2bins(_input, _output, pad_word, _swap) < 0:
            raise FWDLException(input, "decode error")

        self._store_checksum(_out)

        return "Done"
