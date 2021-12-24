import re
import threading
import multiprocessing
import time

PASS_MASK = "ACK(DONE)"
FAIL_MASK = "ACK(ERR)"

PIN_CNT = 16


class IO(object):
    rpc_public_api = ['set', 'get','dir_set','dir_get']
    def __init__(self, xobjects):
        self.xobjects = xobjects
        self.io_lock = threading.Semaphore(1)
        self.io_table = xobjects['io_table']

        # self.start_key = xobjects['gpio_995']
        # self.reset_key = xobjects['gpio_996']

        self.first_flag = 0
        self.io_stop = False


    def get_io_device(self, io_num):
        pin_list = divmod(io_num - 1, 16)
        device_name = 'io_exp' + str(pin_list[0] + 1)
        pin_num = pin_list[1]
        device = self.xobjects[device_name]
        return (pin_num,device)

    def _read_back(self, chip_cnf, func):
        chip_list = chip_cnf.split(",")
        chip_state_dict = {}
        for chip_x in chip_list:
            result = re.match(r"cp(\w+)", chip_x)
            if result is None:
                raise Exception("parameter's format of port get is wrong")

            chip_num = int(result.group(1))

            self.io_lock.acquire()
            ports = eval("self.xobject['io_exp%s'].%s()" % (chip_num, func))
            self.io_lock.release()
            # ports contain with input register's low_8 & high_8
            chip_state_dict[chip_num] = (ports[0] | (ports[1] << 8)) & 0xFFFF

        return chip_state_dict

    def _config(self, chip_cnf, func):
        chip_list = chip_cnf.split(";")
        for chip_x in chip_list:
            result = re.match(r"cp(\w+)=(\w+)", chip_x)
            if result is None:
                raise Exception("parameter's format is wrong")

            chip_num = result.group(1)
            chip_val = int(result.group(2), 16)

            self.io_lock.acquire()
            # the order of writing data is low 8, high 8
            eval(
                "self.xobject['io_exp' + chip_num].%s([chip_val & 0xFF, (chip_val >> 8) & 0xFF])" %
                (func))
            self.io_lock.release()

        return PASS_MASK

    def _get(self, bit_cnf):
        try:
            bit_list = bit_cnf.split(";")
            bit_state = []
            chip_cnf_dict = {}
            for bit_x in bit_list:
                result = re.match(r"bit(\w+)", bit_x)
                if result is None:
                    raise Exception("parameter's format of bit set is wrong")

                bit_num = int(result.group(1))
                if bit_num <= 0:
                    return FAIL_MASK
                pin, io_exp = self.get_io_device(bit_num)
                ret = io_exp.get_pin(int(pin))
                bit_state.append("bit%s=%s" %(bit_num,ret))

            return "ACK("+",".join(bit_state)+")"
        except:
        	return FAIL_MASK

    def _get_dir(self, bit_cnf):
        try:
            bit_list = bit_cnf.split(";")
            bit_state = []
            chip_cnf_dict = {}
            for bit_x in bit_list:
                result = re.match(r"bit(\w+)", bit_x)
                if result is None:
                    raise Exception("parameter's format of bit set is wrong")

                bit_num = int(result.group(1))
                if bit_num <= 0:
                    return FAIL_MASK
                pin, io_exp = self.get_io_device(bit_num)
                ret = io_exp.get_pin_dir(int(pin))
                bit_state.append("bit%s=%s" %(bit_num,ret))

            return "ACK("+",".join(bit_state)+")"
        except:
        	return FAIL_MASK

    def _set(self, bit_cnf):
        try:
            bit_list = bit_cnf.split(";")
            for bit_x in bit_list:
                result = re.match(r"bit(\w+)=(\w+)", bit_x)
                if result is None:
                    raise Exception("parameter's format of bit set is wrong")

                bit_num = int(result.group(1))
                bit_val = int(result.group(2))

                pin, io_exp = self.get_io_device(bit_num)
                io_exp.set_pin(int(pin),bit_val)
            return PASS_MASK
        except Exception,e:
        	return FAIL_MASK
            
        return PASS_MASK
    def _set_dir(self, bit_cnf):
        bit_list = bit_cnf.split(";")
        for bit_x in bit_list:
            result = re.match(r"bit(\w+)=(\w+)", bit_x)
            if result is None:
                raise Exception("parameter's format of bit set is wrong")

            bit_num = int(result.group(1))
            bit_dir = int(result.group(2))
            pin, io_exp = self.get_io_device(bit_num)
            _dir = 'output'
            if bit_dir.find('intput'):
                _dir = 'input'
            io_exp.set_pin_dir(int(pin), _dir)
            
        return PASS_MASK

    def set(self, bit_cnf):
        """
        cat9555 bit set function
        Args:
            bit_cnf:     str,    a string like 'bitX=Y,...', X=1~160, Y=0/1, control cat9555 single pin output,
                                    if Y is 1, means bitX output high level
        Example:   
            io_set("bit56=1,bit57=0,bit58=1")
        """
    
        return self._set(bit_cnf)

    def get(self, bit_cnf):
        """
        get cat9555 bit input level function
        Args:
            param bit_cnf:     str,    a string like 'bitX,...', X=1~160, control cat9555 single pin output
        Example:   
            io.io_get("bit1,bit2")
        """
        return self._get(bit_cnf)

    def dir_set(self, dir_cnf):
        """
        ct9555 bit directory config function
            dir_cnf:     str,    a string like 'bitX=Y,...', X=1~160, Y=0/1, config cat9555 single pin direction
        Example:   
            io_dir_set("bit1=input,bit2=output")
        """
        return self._set_dir(dir_cnf)

    def dir_get(self, dir_cnf):
        """
        get cat9555 pin dir config function
        Args:
            dir_cnf:     str,    a string like 'bitX,...', X=1~160, get cat9555 single pin direction
        Example:   
            io_dir_set("bit1,bit2,bit3,bit4")
        """
        return self._get_dir(dir_cnf)