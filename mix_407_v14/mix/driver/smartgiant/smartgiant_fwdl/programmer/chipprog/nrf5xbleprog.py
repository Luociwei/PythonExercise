#-*- coding: UTF-8 -*-
__author__ = 'jk'

import re
import time
from ..dfucommon import dfu_common
from chipprog import ChipProg



class Nrf5XProg(ChipProg):
    def __init__(self,rpc_client_node):
        ChipProg.__init__(self,rpc_client_node)

    def create_instance(self,dev_path,what_chip):
        "in :                    \
           dev_path:string"
        protocol_type = dfu_common.get_protocol_type_support(self.rpc_client_node)["swd"]
        arch_type = dfu_common.get_chip_arch_type_support(self.rpc_client_node)["nrf5xble"]
        chip_type = dfu_common.get_chip_type_support(self.rpc_client_node,arch_type)[what_chip]

        print(dfu_common.get_protocol_type_support(self.rpc_client_node))
        print(dfu_common.get_chip_arch_type_support(self.rpc_client_node))
        print(dfu_common.get_chip_type_support(self.rpc_client_node,arch_type))

        params = {}
        params["driver_name"] = dev_path
        params["protocol_type"] = protocol_type
        params["chip_arch_type"] = arch_type
        params["chip_type"] = chip_type

        response = self.rpc_client_node.call("DfuProgInstanceCreate",**params)
        if response["state"] < 0:
            return dfu_common.get_error_return_state(response)
        return dfu_common.get_correct_return_state(response)

