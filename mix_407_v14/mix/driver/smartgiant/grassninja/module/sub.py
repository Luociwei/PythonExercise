# -*- coding: utf-8 -*-
import os
import time
import logging
import logging.handlers
from mix.driver.smartgiant.grassninja.module.b2p import MessageLayer


def init_logger(logname):
    dirs = '/var/log/grassninja/'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    logfile = dirs + logname + '.log'
    max_size = 5 * 1000 * 1000  # ~5MB
    logger = logging.getLogger(logname)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(logfile, mode='a', maxBytes=max_size, backupCount=5)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class B2PUartException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class LocustI2CException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


CAP_DET_STATUS_values = {
    0: "CAP DET Not Active",
    1: "Open Detected",
    2: "Short Detected",
    3: "Connection Detected"
}


class locustI2C():  # i2c is not necessary as b2p uart i2c is more efficient 100k vs 1M
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x33 << 1

    def reset(self):
        self.masterCheck()
        self.setASKTXParameter(rout=8, timeout=30e-3, amplitude=2)  # enable maximum ASK TX amplitude
        return

    def crabsResetTime(self, duration=100):  # 100ms by default
        val = int(duration / 50) << 3
        self.i2c.write(self.addr, 0x2c, val)
        return

    def masterCheck(self):
        deviceID = self.i2c.read(self.addr, 0x00, 2)
        deviceREV = self.i2c.read(self.addr, 0x02, 1)
        traceID = self.i2c.read(self.addr, 0x03, 4)
        ASK_TX_DRV_BW = self.i2c.read(self.addr, 0x1a, 1)
        Control7Reg = self.i2c.read(self.addr, 0x55, 1)
        Control8Reg = self.i2c.read(self.addr, 0x56, 1)
        Control9Reg = self.i2c.read(self.addr, 0x57, 1)
        Control11Reg = self.i2c.read(self.addr, 0x59, 1)
        Trim19Reg = self.i2c.read(self.addr, 0x1A, 1)
        val = self.i2c.read(self.addr, 0x21, 1)
        if ((val & 0x80) is True):
            self.logger.info("GN host: error, locust host not found")
        else:
            self.logger.info("GN host: locust host found, deviceID %s, device revison %s, traceID %s, Trim19Reg %s" % (
                             hex(deviceID), hex(deviceREV), hex(traceID), hex(Trim19Reg)))
            self.logger.info("GN host: default ASK TX setting: 0x55 = %s,0x56 = %s, 0x57 = %s, 0x59 = %s" % (
                             hex(Control7Reg), hex(Control8Reg), hex(Control9Reg), hex(Control11Reg)))

    def powerPath(self, switch='on'):
        if (switch == 'on'):
            self.i2c.write(self.addr, 0x4E, 0x80)
            self.logger.info("GN host: Power path enabled")
        if (switch == 'off'):
            self.i2c.write(self.addr, 0x4E, 0x00)
            self.logger.info("GN host: Power path disabled")

    def setASKTXParameter(self, rout=10, timeout=30e-3, amplitude=1):

        if rout <= 5.3:
            ASK_SEL_ROUT = 0x5
        if 5.3 < rout <= 6.2:
            ASK_SEL_ROUT = 0x4
        if 6.2 < rout <= 7.3:
            ASK_SEL_ROUT = 0x7
        if 7.3 < rout <= 9:
            ASK_SEL_ROUT = 0x6
        if 9 < rout <= 11.7:
            ASK_SEL_ROUT = 0x1
        if 11.7 < rout <= 17:
            ASK_SEL_ROUT = 0x0
        if 17 < rout <= 30:
            ASK_SEL_ROUT = 0x3
        if rout > 30:
            ASK_SEL_ROUT = 0x2

        B2PTIMEOUT = int(abs((timeout - 10e-3) / 10e-3)) & 0x1F
        Reg8 = (ASK_SEL_ROUT << 5) + B2PTIMEOUT
        self.i2c.write(self.addr, 0x56, Reg8)
        self.i2c.write(self.addr, 0x59, 0xc4)  # SS is causing a modulation on the waveform, disable SS could improve SI

        if amplitude < 1.25:
            ASK_TX_GAIN_TUNE = 0x2
        else:
            ASK_TX_GAIN_TUNE = 0x0

        Reg9 = self.i2c.read(self.addr, 0x57, 1)
        Reg9 = (Reg9 & 0xFC) | ASK_TX_GAIN_TUNE
        self.i2c.write(self.addr, 0x55, 0x60)
        self.i2c.write(self.addr, 0x56, 0x81)
        self.i2c.write(self.addr, 0x57, 0xa8)

        Reg7 = self.i2c.read(self.addr, 0x55, 1)
        Reg8 = self.i2c.read(self.addr, 0x56, 1)
        Reg9 = self.i2c.read(self.addr, 0x57, 1)
        Reg11 = self.i2c.read(self.addr, 0x59, 1)

        self.logger.info("GN host: ASK TX setting change to 0x55 = %s, 0x56 = %s, 0x57 = %s" % (
                         hex(Reg7), hex(Reg8), hex(Reg9)))
        self.logger.info("GN host: default SS setting 0x59 update to %s (0xc4)" % (hex(Reg11)))
        return

    def idleMode(self, on=True):
        val = self.i2c.read(self.addr, 0x4e, 1)
        if on:
            val = val | 0x4
        else:
            val = val & 0b11111011
        resp = self.i2c.write(self.addr, 0x4e, val)
        self.logger.info("GN host: idle mode is %d" % ((val >> 2) & 0b1))
        return resp

    def dumpStatus(self):
        val = self.i2c.read(self.addr, 0x40, 14)
        self.logger.info("GN host: status", hex(val))

    def powerStatus(self):
        val = self.i2c.read(self.addr, 0x41, 1)
        if (val != 0xf0):
            self.logger.info("GN host: Error, locust power connection failed -- status 0x%x" % val)
        else:
            self.logger.info("GN host: Locust power good.")

    def capDetection(self, open_threshold='600', detect_threshold='5000'):
        '''
        open_threshold: string, cap detection open timer threshold in micro-seconds
        detect_threshold: string, cap detection detect timer threshold in micro-seconds
        '''
        self.funcConfigureCapDet(CAPDET_OPEN=open_threshold, CAPDET_DETECT=detect_threshold)
        self.funcEnterCapDet()
        time.sleep(0.02)
        resp = self.funcReadCapDetStatus()
        self.funcExitCapDet()
        if resp == 3:
            return True
        else:
            return False

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
            raise LocustI2CException("GN host: input CAPDET_OPEN time from 50us to 12800 us in 50us \
                                     intervals (8-bits). POR default to 600us")
        try:
            capdet_detect_tosend = CAPDET_DETECT_values[CAPDET_DETECT]
        except:
            raise LocustI2CException("Warning: input CAPDET_DETECT time from 50us to 12800 us in 50us \
                                     intervals (8-bits). POR default to 5,000 us")

        if capdet_open_tosend is not None:
            self.i2c.write(self.addr, 0x5F, capdet_open_tosend)
        if capdet_detect_tosend is not None:
            self.i2c.write(self.addr, 0x60, capdet_detect_tosend)

        msg = "GN host: configure cap detection with open time', %s, 'ms', 'detect time', %s, 'ms'" % (
              CAPDET_OPEN, CAPDET_DETECT)
        self.logger.info(msg)
        return

    def funcEnterCapDet(self):
        val = self.i2c.read(self.addr, 0x4E, 1)
        if (0x01 & val) == 0x01:
            self.logger.info("GN host: HOST_CAPDET_EN already enabled.")
        else:
            masked_value = (val & 0xFE) | 0x01
            self.i2c.write(self.addr, 0x4E, masked_value)
            self.logger.info("GN host: cap detection enabled")

    def funcExitCapDet(self):
        val = self.i2c.read(self.addr, 0x4E, 1)
        if (0x01 & val) == 0x00:
            self.logger.info("GN host: HOST_CAPDET_EN already disabled.")
        else:
            masked_value = (val & 0xFE) | 0x00
            self.i2c.write(self.addr, 0x4E, masked_value)
            self.logger.info("GN host: cap detection disabled")

    def funcReadCapDetStatus(self):
        val = self.i2c.read(self.addr, 0x41, 1)
        CAP_DET_STATUS = val & 0x03

        msg = "GN host: %s" % (CAP_DET_STATUS_values[CAP_DET_STATUS])
        self.logger.info(msg)
        return CAP_DET_STATUS


class cd2e22():  # Parrot functions
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x42

    def reset(self):
        self.i2c.write(self.addr, 0x82, 0b10001000)  # configure INT polarity
        self.i2c.write(self.addr, 0x83, 0x0f)  # configure INT enables
        self.i2c.write(self.addr, 0x84, 0x0f)  # configure INT enables
        revID = self.i2c.read(self.addr, 0x80, 1)
        gpio0 = self.i2c.read(self.addr, 0x30, 1)
        gpio1 = self.i2c.read(self.addr, 0x70, 1)
        intConf = self.i2c.read(self.addr, 0x83, 2)
        self.logger.info("GN host: Parrot ID 0x%x, gpio0 0x%x, gpio1 0x%x, intConf 0x%x" % (
                         revID, gpio0, gpio1, intConf))
        self.logger.info("GN host: Parrot reset complete")

    def port(self, on=True):
        if on:
            self.i2c.write(self.addr, 0x82, 0x00)
        else:
            self.i2c.write(self.addr, 0x82, 0x20)

    def softReset(self):
        self.i2c.write(self.addr, 0x82, 0x80)

    def interrupt(self):
        val = self.i2c.read(self.addr, 0x93, 1)
        val = (val << 8) + self.i2c.read(self.addr, 0x94, 1)
        if (val > 0):
            self.logger.info("Interrupt 0x%x" % val)
        else:
            self.logger.info("No eUSB interrupt found")

    def readReg(self, register):
        value = self.i2c.read(self.addr, register, 1)
        return value

    def writeReg(self, register, data):
        self.i2c.write(self.addr, register, data)
        return


class tca9555():
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = 0x40

    def reset(self):
        self.i2c.write(self.addr, 0x02, 0b11001111)  # enable all LEDs, reset Parrot
        self.i2c.write(self.addr, 0x06, 0x00)
        self.i2c.write(self.addr, 0x03, 0b00001000)
        self.i2c.write(self.addr, 0x07, 0b11100110)  # reset Locust
        time.sleep(0.5)
        self.i2c.write(self.addr, 0x02, 0b11010000)  # disable all LEDs, enable Parrot
        self.i2c.write(self.addr, 0x07, 0b11100111)  # enable Locust
        self.write(1, 4, 1)  # enable USB MUX
        self.config(1, 4, 0)

    def readAll(self):
        val = self.i2c.read(self.addr, 0x0, 1)
        self.logger.info("Port 0 %s" % (hex(val)))
        val = self.i2c.read(self.addr, 0x1, 1)
        self.logger.info("Port 1 %s" % (hex(val)))

    def read(self, port, io):
        '''
        port: enum 0|1
        io: enum 0..7
        '''
        val = self.i2c.read(self.addr, port, 1)
        val = (val >> io) & 0x01
        return val

    def write(self, port, io, val):
        '''
        port: enum 0|1
        io: enum 0..7
        '''
        reg = port + 2
        data = self.i2c.read(self.addr, reg, 1)
        if (val == 0):
            data = data & (0xff - (1 << io))
        else:
            data = data | (1 << io)

        self.i2c.write(self.addr, reg, data)
        return

    def config(self, port, io, config):
        '''
        port: enum 0|1
        io: enum 0..7
        config: enum 0|1, 0--output, 1--input
        '''
        reg = port + 6
        data = self.i2c.read(self.addr, reg, 1)
        if (config == 0):  # output
            data = data & (0xff - (1 << io))
        else:  # input
            data = data | (1 << io)

        self.i2c.write(self.addr, reg, data)
        return

    def parrotCross(self, value):
        '''
        value: enum<0|1>
        '''
        self.write(0, 5, value)
        return

    def parrotReset(self, value):
        '''
        value: enum<0|1>
        '''
        self.write(0, 4, value)
        return

    def pp4v5Control(self, value):
        '''
        value: enum<0|1>
        '''
        self.write(0, 7, value)
        self.config(0, 7, 0)

    def sysReset(self):
        '''
        WARNING: this will power cycle the module
        '''
        self.write(1, 5, 1)
        self.config(1, 5, 0)

    def usbMuxOE(self, on=True):
        '''
        on: bool <True|False>, True- outptut enable, False- output disable
        CAUTION: DON'T TOUCH THIS FUNCTION IF YOU DON'T KNOW WHAT IT DOES
        '''
        self.logger.info("GN host: USB connection will be broken if on=False")
        if on:
            self.write(1, 4, 0)
        else:
            self.write(1, 4, 1)

    def pp3V3(self, value):
        '''
        value: enum<0|1>, default==1 (on)
        '''
        self.write(0, 6, value)
        self.config(0, 6, 0)
        return


class I2CBus():
    def __init__(self, i2c, debug=False):
        self.i2c_bus = i2c
        self.debug = debug

    def read(self, addr, reg, N):
        '''
        read register from address
        addr: int8<0-255>, i2c slave 8bit address
        reg: int8<0-255>, register
        N: int8<0-255>, number of registers to read
        '''
        addr = addr >> 1
        list_in = self.i2c_bus.write_and_read(addr, [reg], N)
        uint_data = 0
        for i, data in enumerate(list_in):
            uint_data |= data << (8 * i)

        if self.debug:
            self.logger.info("GN host i2c: Read from i2c addr 0x%x, reg 0x%x, data 0x%x" % (addr, reg, uint_data))
        return uint_data

    def write(self, addr, reg, data):
        '''
        write register with data
        addr: int8<0-255>, i2c slave 8bit address
        reg: int8<0-255>, register
        data: int8<0-255>, data to be written
        '''
        addr = addr >> 1

        wr_data = []
        wr_data.append(reg)
        wr_data.append(data)
        self.i2c_bus.write(addr, wr_data)

        if self.debug:
            self.logger.info("GN host i2c: Write to i2c addr 0x%x, reg 0x%x, data 0x%x" % (addr, reg, data))


class uartport(object):
    def __init__(self, uart, debug=False):
        self.uart = uart._serial
        self.debug = debug
        self.uart.flush()
        self.logger = uart.logger

    def sendCommand(self, data):  # payload is an array []
        """
        uart send
        :param data: bytearray,
        :return: None
        """
        if self.uart.isOpen():
            if self.debug:
                self.logger.info('   Send: {0}'.format([hex(no) for no in data]))
            self.uart.write(list(data))
        else:
            raise B2PUartException("Open serial port error")

    def send(self, data):  # payload is an array []
        """
        remove debuglog
        uart send
        :param data: bytearray,
        :return: None
        """
        if self.uart.isOpen():
            self.uart.write(data)
        else:
            raise B2PUartException("Open serial port error")

    def readResponse(self, timeout, package=1):  # timeout in seconds
        """
        uart read
        :param timeout: float
        :return: bytearray
        """
        if self.uart.isOpen():
            rx = bytearray(b'')
            _package = 0
            total_length = 0
            TimeBegin = time.time()
            rxdata_Length = 65535
            while ((time.time() - TimeBegin) < timeout):
                data = self.uart.read(self.uart.inWaiting())
                if data:
                    if (len(rx) >= rxdata_Length):
                        break
                    else:
                        rx += bytearray(data)
                    # Check first package
                    while (len(rx) > total_length + 4):
                        rxHeader = bytearray(rx)[total_length:total_length + 4]
                        if ((rxHeader[0] == 0xFF) and (rxHeader[1] == 0xB2)):
                            total_length += ((rxHeader[3] << 8) & 0xFF00) + rxHeader[2] & 0xFF
                            _package += 1
                        else:
                            rx.pop(0)
                            break
                if (len(rx) == total_length) and _package == package:
                    break
                time.sleep(0.001)
            if self.debug:
                self.logger.info('Receive: {0}'.format([hex(no) for no in list(rx)]))
            return rx

    def SendRead(self, data, timeout, get_resp=True, check_header_only=False):
        self.sendCommand(data)  # payload is an array []
        package = 1
        if get_resp:
            if check_header_only:
                package = 2
            return self.readResponse(timeout, package)
        else:
            return None

    def SendReadWithDummyBytes(self, data, timeout, get_resp=True, check_header_only=False):
        self.send(data)  # payload is an array []
        package = 1
        if get_resp:
            if check_header_only:
                package = 2
            return self.readResponse(timeout, package)
        else:
            return None

    def flush(self):
        self.uart.flush()

    def close(self):
        self.uart.flush()
        self.uart.close()

    def open(self):
        '''
        Open uart port and reset input/output buffer.
        '''
        if not self.uart.isOpen():
            self.uart.open()


class b2puart():
    def __init__(self, uart, b2p=None, debug=True):
        self.uart = uartport(uart, debug=debug)
        self.logger = uart.logger
        if b2p:
            self.MSGL = b2p
        else:
            self.MSGL = MessageLayer()

    def send_read_with_no_retry(self, rcode, cmd, payload, timeout, get_resp=True, addDum=False,
                                send_again=False, check_header_only=False):
        """
        :param rcode: int, 0x09/9
        :param cmd: int, 0x16/22
        :param payload: list, [0, 51, 0x52, 0xc5]
        :param timeout: float, timeout is in second
        :param get_resp:  bool, True/False
        :param addDum: bool, True/False
        :param send_again: bool. True/False
        :return: dict, {"RESULT": True, "ERROR_MSG": None, "PAYLOAD": [0, 51, 0x52, 0xc5]}
        """
        dumBytes = [0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe, 0xfe]
        if send_again:
            b2pCmd = self.MSGL.getLastCmd()
        else:
            b2pCmd = self.MSGL.createB2PCmd(rcode, cmd, payload)
        # self.logger.info ("send b2pCmd: {}".format(b2pCmd))
        if addDum:
            self.uart.send(bytearray(dumBytes))
            # TODO: 100 times dummy instruction about 25~28us in 7020;
            for i in xrange(100):
                continue
            response = self.uart.SendReadWithDummyBytes(b2pCmd, timeout, get_resp, check_header_only)
        else:
            response = self.uart.SendRead(b2pCmd, timeout, get_resp, check_header_only)
        if not get_resp:
            return None
        elif get_resp and response:
            return self.MSGL.decodeResponse(response, cmd + 1, check_header_only=check_header_only)
        else:
            return {}

    def SendRead(self, rcode, cmd, payload, timeout, get_resp=True, verb=False,
                 addDum=False, retry=3, check_header_only=False):
        # self.flush()
        send_again = False
        for i in range(retry):
            ret = self.send_read_with_no_retry(rcode, cmd, payload, timeout, get_resp,
                                               addDum=addDum, send_again=send_again,
                                               check_header_only=check_header_only)
            if ret is None:
                return ret
            else:
                result = ret.get("RESULT")
                if result is True:
                    if verb:
                        return ret.get("OPCODE"), ret.get("STATUS"), ret.get("PAYLOAD")
                    return ret.get("PAYLOAD")
                else:
                    if ret == {} and i <= (retry - 1):
                        send_again = True
                        time.sleep(0.0001)
                        continue
                    else:
                        self.logger.info("Error MSG: {}".format(ret.get("ERROR_MSG")))
                        raise B2PUartException("Error MSG: {}".format(ret.get("ERROR_MSG")))
        self.logger.info("Error MSG: Retry {0} times and return nothing".format(retry))
        raise B2PUartException("Error MSG: Retry {0} times and return nothing".format(retry))

    def TunnelOpen(self, timeout):
        response = self.SendRead(0x0, 0x10, [0, 1], timeout)
        return response

    def TunnelClose(self, timeout):
        response = self.SendRead(0x0, 0x10, [0, 0], timeout)
        return response

    def TunnelCmd(self, cmd, timeout):
        full_response = ""
        payload = [0, 1] + list(cmd.encode('utf-8')) + [0x0d, 0x0a]
        response = self.SendRead(0x0, 0x12, payload, timeout)
        full_response = response.decode('utf-8')
        EOF = False
        while not EOF:
            payload = [0, 1]
            response = self.SendRead(0x0, 0x12, payload, timeout)
            if response[-26:] == bytearray(b'passthrough exited;DONE)\r\n'):
                self.logger.info("passthrough timed out")
                break
            full_response += response.decode('utf-8')
            if 'exited' in response.decode('utf-8'):
                self.logger.info("pass through timed out")
                break
            EOF = (response[-1] == 0x20) and (response[-2] == 0x5d)
        self.logger.info(full_response)
        return full_response

    def flush(self):
        self.uart.flush()

    def close(self):
        self.uart.close()

    def open(self):
        self.uart.open()
