# -*- coding: utf-8 -*-
import struct
import time

LOCUST_HOST_B2P_TARGET_ADDR = 0x8
LOCUST_DEV_B2P_TARGET_ADDR = 0x9
LOCUST_I2C_SLAVE_ADDR = 0x33

routing_code = {
    "HostLocust": LOCUST_HOST_B2P_TARGET_ADDR,
    "DeviceLocust": LOCUST_DEV_B2P_TARGET_ADDR,
    "DeviceSOC": 0x0,
}

FunBusBaud_available = {
    0x0: 2,
    0x1: 1.92,
    0x2: 1.84615,
    0x3: 1.77778,
    0x4: 1,
    0x5: 0.97959,
    0x6: 0.96,
    0x7: 0.94118,
    0x8: 0.92308,
    0x9: 0.90566,
    0xA: 0.88889,
    0xB: 0.46154,
    0xC: 0.23077,
    0xD: 0.11679,
    0xE: 0.11511,
    0xF: 0.11348
}

Cmd = {
    "B2P_CMD_PING": 0x0,
    "B2P_CMD_RESET": 0x8,
    "B2P_CMD_I2C_WRITE": 0x14,
    "B2P_CMD_I2C_WRITE_REG8": 0x16,
    "B2P_CMD_I2C_WRITE_REG16": 0x18,
    "B2P_CMD_I2C_READ": 0x1A,
    "B2P_CMD_I2C_READ_REG8": 0x1C,
    "B2P_CMD_I2C_READ_REG16": 0x1E,
    "B2P_LOOPBACK": 0x100
}


class LocustException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class locust():
    '''
    locust is the encapsulation of the b2p_uart driver

    Args:
        b2p_uart:    instance(b2p),  uart device.
        debug:       True/False,  use debug.

    Examples:
        b2p_uart = b2p('/dev/ttyS2', 905600)
        locust = locust(b2p_uart)

    '''
    def __init__(self, b2p_uart, debug=False):
        self.b2p_uart = b2p_uart
        self.debug = debug
        self.logger = b2p_uart.logger

    def sendPing(self, destination="HostLocust"):
        '''
        B2P ping destination
        destination: enum<'HostLocust'|'DeviceLocust'>
        '''
        self.logger.info("GN host - locustb2p: send ping {0}".format(destination))
        payload = [0, 2]
        resp = self.b2p_uart.SendRead(rcode=routing_code[destination], cmd=Cmd["B2P_CMD_PING"],
                                      payload=payload, timeout=0.3, verb=True)
        if resp is False:
            self.logger.info("GN host - locustb2p: Error - b2p ping ", destination, " failed")
        else:
            protocol_ver = int(resp[2][0])
            mode = int(resp[2][1])
            self.logger.info("GN host - locustb2p: b2p protocol version = {ver}, mode = {m}".format(
                             ver=protocol_ver, m=mode))
        return True

    def sendReset(self, destination="HostLocust", reset_mode=0x01):
        '''
        B2P reset destination
        destination: enum<'HostLocust'|'DeviceLocust'>
        '''
        if reset_mode == 0x01:
            self.logger.info("GN host - locustb2p: send reset {0}".format(destination))
        if reset_mode == 0x00:
            self.logger.info("GN host - locustb2p: crab reset to pulse PMU reset")
        payload = [reset_mode, 255, 255]
        resp = self.b2p_uart.SendRead(rcode=routing_code[destination], cmd=Cmd["B2P_CMD_RESET"],
                                      payload=payload, timeout=0.3, verb=True)
        return resp

    def writeI2C(self, bus, slave_addr, data=0x00, wtype="reg8", register=0x00,
                 destination="HostLocust", timeout=0.3, get_resp=True, addDum=False, check_header_only=False):
        # header = SOP(2), length(2), SEQ(1), payload ([RCODE, OPCODE] + data)(N) , CRC(4)
        # I2C data = bus + {0,CHIPID} + real_data
        write_type = {
            "write": 0x14,
            "reg8": 0x16,
            "reg16": 0x18
        }
        write_type_tosend = write_type[wtype]
        data_to_write_tosend = data
        register_tosend = register
        slave_addr_tosend = slave_addr
        bus_tosend = bus
        if type(data_to_write_tosend) is list:
            if write_type_tosend == 0x14:
                complete_data_payload = [bus_tosend, slave_addr_tosend]
            elif write_type_tosend == 0x16:
                complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend]
            elif write_type_tosend == 0x18:
                complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend >> 8, register_tosend & 0x00FF]
            complete_data_payload.extend(data_to_write_tosend)
        else:
            if write_type_tosend == 0x14:
                complete_data_payload = [bus_tosend, slave_addr_tosend, data_to_write_tosend]
            elif write_type_tosend == 0x16:
                complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend, data_to_write_tosend]
            elif write_type_tosend == 0x18:
                complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend >> 8,
                                         register_tosend & 0x00FF, data_to_write_tosend]
        if self.debug:
            self.logger.info('GN host - locustb2p[debug]: data to send {0}'.format(complete_data_payload))
        resp = self.b2p_uart.SendRead(rcode=routing_code[destination], cmd=write_type_tosend,
                                      payload=complete_data_payload, timeout=timeout, verb=True,
                                      get_resp=get_resp, addDum=addDum, check_header_only=check_header_only)
        if self.debug:
            self.logger.info("GN host - locustb2p[debug]: write resp: {0}".format(resp))
        return True

    def writeLocustReg(self, register, data, target='host'):
        if target == 'host':
            destination = 'HostLocust'
        if target == 'device':
            destination = 'DeviceLocust'
        self.writeI2C(wtype="reg8", destination=destination, bus=0x00, slave_addr=0x33, register=register, data=data)
        return

    def writeLagunaReg(self, register, data, addDum=False):
        self.writeI2C(bus=0x01, slave_addr=0x11, data=data, wtype="reg16",
                      register=register, destination='DeviceLocust', addDum=addDum)
        return

    def readI2CRegs(self, bus, slave_addr, read_len, register=0x00, rtype="reg8",
                    destination="HostLocust", timeout=0.5):
        read_type = {
            "read": 0x1A,
            "reg8": 0x1C,
            "reg16": 0x1E
        }
        read_type_tosend = read_type[rtype]
        read_len_tosend = read_len
        register_tosend = register
        slave_addr_tosend = slave_addr
        bus_tosend = bus
        if read_type_tosend == 0x1A:
            complete_data_payload = [bus_tosend, slave_addr_tosend, read_len_tosend]
        elif read_type_tosend == 0x1C:
            complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend, read_len_tosend]
        elif read_type_tosend == 0x1E:
            complete_data_payload = [bus_tosend, slave_addr_tosend, register_tosend >> 8,
                                     register_tosend & 0x00FF, read_len_tosend]
        resp = self.b2p_uart.SendRead(rcode=routing_code[destination], cmd=read_type_tosend,
                                      payload=complete_data_payload, timeout=timeout, verb=True)
        if resp is False:
            if self.debug:
                self.logger.info("GN host - locustb2p[debug]: Error readI2cReg {0}".format(resp))
            return
        rdata = resp[2]
        try:
            rdata = list(struct.unpack('{}B'.format(read_len), rdata))
        except Exception as e:
            self.logger.info("Error MSG: Ret.PAYLOAD ERROR")
            raise LocustException("Error MSG: Ret.PAYLOAD ERROR")
        return rdata

    def readLocustReg(self, register, target='host', n=1):
        if target == 'host':
            destination = 'HostLocust'
        if target == 'device':
            destination = 'DeviceLocust'
        result = self.readI2CRegs(rtype="reg8", destination=destination, bus=0x00,
                                  slave_addr=0x33, register=register, read_len=n)
        return result

    def readLagunaReg(self, register, n=1):
        resp = self.readI2CRegs(bus=0x01, slave_addr=0x11, read_len=n, rtype="reg16",
                                register=register, destination='DeviceLocust')
        return resp

    def sendLoopback(self, data, destination="HostLocust", quiet=False):
        # data should be a list
        payload = data
        resp = self.b2p_uart.SendRead(rcode=routing_code[destination], cmd=Cmd["B2P_LOOPBACK"],
                                      payload=payload, timeout=0.1, verb=True)
        try:
            payload_tuple = struct.unpack('{}B'.format(len(resp[2])), resp[2])
            if list(payload_tuple) != data:
                if quiet is False:
                    self.logger.info("GN host - locustb2p: Error -  loopback data not equal!!!")
                return False
            if quiet is False:
                self.logger.info("GN host - locustb2p: loopback pass")
        except:
            self.logger.info("GN host - locustb2p: Error - resp incorrect, b2p path may not work")

        return resp

    def enablePowerPath(self, destination="HostLocust"):
        readback_reg4E_list = self.readI2CRegs(rtype="reg8", destination=destination,
                                               bus=0x00, slave_addr=0x33, register=0x4E, read_len=0x01)
        try:
            reg4E_val = readback_reg4E_list[0]
        except:
            self.logger.info("GN host - locustb2p: Error - , {0}, b2p no response".format(destination))
            return
        if (0x80 & reg4E_val) == 0x80:
            self.logger.info("GN host - locustb2p:, {0}, powerpath is already enabled.".format(destination))
            return
        else:
            masked_value = (reg4E_val & 0x7F) | 0x80
            if self.writeI2C(wtype="reg8", destination=destination, bus=0x00,
                             slave_addr=0x33, register=0x4E, data=masked_value):
                self.logger.info("GN host - locustb2p:, {0}, powerpath enabled.".format(destination))
        return

    def disablePowerPath(self, destination="HostLocust"):
        readback_reg4E_list = self.readI2CRegs(rtype="reg8", destination=destination, bus=0x00,
                                               slave_addr=0x33, register=0x4E, read_len=0x01)
        try:
            reg4E_val = readback_reg4E_list[0]
        except:
            self.logger.info("GN host - locustb2p: Error - ", destination, "b2p failed")
            return
        if (0x80 & reg4E_val) == 0x00:
            self.logger.info("GN host - locustb2p:, {0}, powerpath was disabled.".format(destination))
            return
        else:
            masked_value = (reg4E_val & 0x7F) | 0x00
            if self.writeI2C(wtype="reg8", destination=destination, bus=0x00,
                             slave_addr=0x33, register=0x4E, data=masked_value):
                self.logger.info("GN host - locustb2p:, {0}, powerpath disabled.".format(destination))
        return

    def pullup(self, on=True):
        if on:
            self.logger.info("GN host - locustb2p: HostLocust local pullup enabled.")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x01, wtype="reg8",
                          register=0x4f, destination="HostLocust")
        else:
            self.logger.info("GN host - locustb2p: HostLocust local pullup disabled.")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x00, wtype="reg8",
                          register=0x4f, destination="HostLocust")
        return

    def eUSBMode(self, on=False):
        if on:
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0xa4, wtype="reg8", register=0x5a, destination="HostLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0xa4, wtype="reg8", register=0x5a, destination="DeviceLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x01, wtype="reg8", register=0x51, destination="DeviceLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x00, wtype="reg8", register=0x51, destination="DeviceLocust")
            self.logger.info("GN host - locustb2p: enable both locust host and device eUSB mode")
        else:
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0xa0, wtype="reg8", register=0x5a, destination="HostLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0xa0, wtype="reg8", register=0x5a, destination="DeviceLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x01, wtype="reg8", register=0x51, destination="DeviceLocust")
            self.writeI2C(bus=0x00, slave_addr=0x33, data=0x00, wtype="reg8", register=0x51, destination="DeviceLocust")
            self.logger.info("GN host - locustb2p: disable both locust host and device eUSB mode")
        return

    def setFunBaud(self, baudrate, destination="DeviceLocust"):
        baud_tosend = baudrate
        readback_reg53_list = self.readI2CRegs(rtype="Reg8", destination=destination, bus=0x00,
                                               slave_addr=0x33, register=0x53, read_len=0x01)
        reg53_val = readback_reg53_list[0]
        if ((reg53_val & 0xF0) >> 4) != baud_tosend:
            value_to_send = ((baud_tosend << 4) | (reg53_val & 0x0F))
        if (reg53_val & 0x0F) != baud_tosend:
            value_to_send = reg53_val | (0x0F & baud_tosend)
        self.writeI2C(wtype="Reg8", destination=destination, bus=0x00,
                      slave_addr=0x33, register=0x53, data=value_to_send)
        self.writeI2C(wtype="Reg8", destination=destination, bus=0x00,
                      slave_addr=0x33, register=0x53, data=value_to_send)

    def funcConfigureCapDet(self, CAPDET_OPEN, CAPDET_DETECT):
        '''
        CAPDET_OPEN: int<0-65535>,ms, cap open timing threshold
        CAPDET_DETECT: int<0-65535>,ms, cap found timing threshold
        '''
        # reset value: CAPDET_OPEN = '600us', CAPDET_DETECT = '5000us'
        CAPDET_OPEN_values = {}
        for i in range(256):
            CAPDET_OPEN_text = str(50 + i * 50)
            CAPDET_OPEN_values.update({CAPDET_OPEN_text: i})
        CAPDET_OPEN_values.update({"None": None})

        CAPDET_DETECT_values = {}
        for i in range(256):
            CAPDET_DETECT_text = str(50 + i * 50)
            CAPDET_DETECT_values.update({CAPDET_DETECT_text: i})
        CAPDET_DETECT_values.update({"None": None})

        try:
            capdet_open_tosend = CAPDET_OPEN_values[CAPDET_OPEN]
        except:
            self.logger.info("GN host: Warning -  input CAPDET_OPEN wrong! \n Programmable from 50us to 12800 us in 50us \
                   intervals (8-bits). POR default to 600us")
            return
        try:
            capdet_detect_tosend = CAPDET_DETECT_values[CAPDET_DETECT]
        except:
            self.logger.info("GN host: Warning - input CAPDET_DETECT wrong! \n Programmable from 50us to 12800 us in 50us \
                   intervals (8-bits). POR default to 5,000 us")
            return
        if capdet_open_tosend is not None:
            ret_wr_capdet_open = self.writeI2C(bus=0x00, slave_addr=0x33, data=capdet_open_tosend,
                                               wtype="reg8", register=0x5F, destination="HostLocust")
        if capdet_detect_tosend is not None:
            ret_wr_capdet_detect = self.writeI2C(bus=0x00, slave_addr=0x33, data=capdet_detect_tosend,
                                                 wtype="reg8", register=0x60, destination="HostLocust")
        return (ret_wr_capdet_open & ret_wr_capdet_detect)

    def funcEnterCapDet(self):
        readback = self.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x4E,
                                    rtype="reg8", destination="HostLocust")
        try:
            reg4E_val = readback[0]
        except:
            self.logger.info("GN host - locustb2p: Error - readback none, b2p path may not work")
            return

        if (0x01 & reg4E_val) == 0x01:
            self.logger.info("GN host - locustb2p: HOST_CAPDET_EN already enabled.")
            return True
        else:
            masked_value = (reg4E_val & 0xFE) | 0x01
            retVal = self.writeI2C(bus=0x00, slave_addr=0x33, data=masked_value, wtype="reg8",
                                   register=0x4E, destination="HostLocust")
            return retVal

    def funcExitCapDet(self):
        readback = self.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x4E,
                                    rtype="reg8", destination="HostLocust")
        try:
            reg4E_val = readback[0]
        except:
            self.logger.info("GN host - locustb2p: Error - readback none, b2p path may not work")
            return

        if (0x01 & reg4E_val) == 0x00:
            # self.logger.info( "HOST_CAPDET_EN already disabled.")
            return True
        else:
            masked_value = (reg4E_val & 0xFE) | 0x00
            retVal = self.writeI2C(bus=0x00, slave_addr=0x33, data=masked_value, wtype="reg8",
                                   register=0x4E, destination="HostLocust")

        return retVal

    def funcReadCapDetStatus(self):
        CAP_DET_STATUS_values = {
            0: "CAP DET Not Active",
            1: "Open Detected",
            2: "Short Detected",
            3: "Connection Detected"
        }
        readback = self.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x41,
                                    rtype="reg8", destination="HostLocust")
        try:
            if self.debug:
                self.logger.info("GN host - locustb2p: readback {0}".format(hex(readback[0])))
            CAP_DET_STATUS = readback[0] & 0x03
        except:
            self.logger.info("GN host - locustb2p: Error - readback none, b2p path may not work")
            return
        self.logger.info(CAP_DET_STATUS_values[CAP_DET_STATUS])
        return CAP_DET_STATUS_values[CAP_DET_STATUS]

    def getState(self, destination="HostLocust"):
        rb_data = self.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x45,
                                   rtype="reg8", destination=destination)
        try:
            status_val = rb_data[0] >> 2
        except:
            RuntimeError("GN host - locustb2p: Error, b2p failed")

        MAIN_FSM_STATE__RO_values = {
            1: "HOST_CRC_ERROR",
            2: "HOST_IDLE_OFF",
            3: "HOST_IDLE_LCLB2P",
            4: "HOST_ASK_PPON",
            5: "HOST_DPM_PPON",
            6: "HOST_IDLE_25HZ",
            7: "HOST_IDLE_LCLB2P_25HZ",
            8: "HOST_ASK_RMTPU",
            9: "HOST_ASK_LCLPU",
            10: "HOST_DPM_RMTPU",
            11: "HOST_DPM_LCLPU",
            12: "HOST_FAULT",
            13: "HOST_CAPDET",
            14: "HOST_CAPDET_NONE",
            15: "N/A",
            16: "DEV_CRC_ERROR",
            17: "DEV_FAULT_OFF",
            18: "DEV_FAULT_LCLB2P",
            19: "DEV_IDLE_OFF",
            20: "DEV_IDLE_LCLB2P",
            21: "DEV_ASK_RMTONLY",
            22: "DEV_DPM_RMTONLY",
            23: "DEV_ASK_RMTPWR_PPON",
            24: "DEV_DPM_RMTPWR_PPON",
            25: "DEV_ASK_RMTPWR",
            26: "DEV_DPM_RMTPWR",
            27: "DEV_ASK_ALLON",
            28: "DEV_ASK_RMTONLY_PPON",
            29: "DEV_DPM_ALLON",
            30: "DEV_DPM_RMTONLY_PPON",
            31: "DEV_DEADHOSTDET",
            32: "DEV_DEADHOSTDET_DONE",
            33: "DEV_HOSTDET_OFF",
            34: "DEV_HOSTDET_LCLB2P"
        }
        msg = "GN host: %s current state %s" % (destination, MAIN_FSM_STATE__RO_values[status_val])
        self.logger.info(msg)

    def getFunVoltgStatus(self, destination="HostLocust"):
        FUN_VOLTG_STATUS_info = {
            0: "FUN bus is less than 1.2 (+/- 0.1) V",
            1: "FUN bus is between 1.2 (+/- 0.1) to 2.4 (+/- 0.1) V ",
            2: "FUN bus is between 2.4 (+/- 0.1) V to 3.1 (+/- 0.1) V ",
            3: "FUN bus is more than 3.1 (+/- 0.1) V"
        }
        readback = self.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                    register=0x42, rtype="reg8", destination=destination)
        try:
            if self.debug:
                self.logger.info("GN host - locustb2p[debug]: readback: {0}".format(hex(readback[0])))
            FUN_VOLTG_STATUS = readback[0] & 0x03
        except:
            self.logger.info("GN host - locustb2p: Error - readback none, b2p path may not work")
            return

        self.logger.info(FUN_VOLTG_STATUS_info[FUN_VOLTG_STATUS])
        return FUN_VOLTG_STATUS_info[FUN_VOLTG_STATUS]
