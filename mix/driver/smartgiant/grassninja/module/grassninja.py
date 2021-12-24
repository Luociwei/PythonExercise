# -*- coding: utf-8 -*-
import time
import struct
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.grassninja.module.sub import I2CBus
from mix.driver.smartgiant.grassninja.module.sub import cd2e22
from mix.driver.smartgiant.grassninja.module.sub import tca9555
from mix.driver.smartgiant.grassninja.module.sub import locustI2C
from mix.driver.smartgiant.grassninja.module.sub import b2puart
from mix.driver.smartgiant.grassninja.module.sub import init_logger
from mix.driver.smartgiant.grassninja.module.locust import locust
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.0.1'


LAGUNA_I2C_7BIT_ADDR = 0x11
EEPROM_I2C_ADDR = 0x50


class GrassNinjaHostException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class grassNinjaHost(SGModuleDriver):
    '''
    GrassNinja drive class.

    Args:
        i2c:        instance(I2C),   Class instance of I2C bus.
        uart:       instance(UART),  Class instance of UART bus.
        debug:      boolean,         Whether to print the data log.
        file:       string,          log file name.
    Examples:
        i2c = I2C('/dev/i2c-0')
        uart = UART('/dev/ttyS2', 905600)
        grassninja = grassNinjaHost(i2c, uart)

    '''
    rpc_public_api = ["reset_all", "idle_mode", "cap_detect", "enable_powerpath", "ping_device",
                      "reset_laguna", "force_dfu", "reset_host", "ping_soc", "get_device_info",
                      "enter_laguna_testmode", "pp7v5_passthrough", "amux_select", "amux_rtc",
                      "set_powerstate", "get_powerstate", "run_ping", "run_loopback", "enable_kis",
                      "enable_analog_power", "sys_reset", "set_b2p_timeouts", "uart_open",
                      "uart_close", "parrot2Locust", "setDPMCommsMode", "disableParrotPower",
                      "enableParrotPower", "force_dfu_mode", "writeLagunaReg"] + SGModuleDriver.rpc_public_api

    compatible = ["GQQ-1G11-5-010"]

    def __init__(self, i2c, uart, debug=False, file='grassninja'):
        self.debug = debug
        self._logger = init_logger(file)
        self.eeprom = CAT24C32(EEPROM_I2C_ADDR, i2c)
        self.i2c = I2CBus(i2c, self.debug)
        self.i2c.logger = self._logger

        self.ioexp = tca9555(self.i2c)
        self.ioexp.logger = self._logger

        self.parrot = cd2e22(self.i2c)
        self.parrot.logger = self._logger

        self.locustI2C = locustI2C(self.i2c)
        self.locustI2C.logger = self._logger

        uart.logger = self._logger
        self.b2pUart = b2puart(uart, None, self.debug)
        self.locustB2P = locust(self.b2pUart, debug=debug)

        super(grassNinjaHost, self).__init__(self.eeprom)

    def post_power_on_init(self, timeout=1.0):
        '''
        Init grassninja module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=1.0):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.reset_all()
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise GrassNinjaHostException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get grassninja driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def reset_all(self):
        '''
        Initialize the GrassNinjaHost board, including Parrot, Locust host and IOExpander
        Use this function only once for the whole test.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== reset_all ========")
        self.b2pUart.flush()
        self.ioexp.reset()
        self.parrot.reset()
        self.locustB2P.sendReset("HostLocust", 0x01)
        # Bug fix: Move locust host configuration below host reset; Otherwise TX settings can't be enabled
        self.locustI2C.reset()
        self.locustB2P.sendPing("HostLocust")
        self.parrot2Locust()
        return "done"

    def idle_mode(self, on=True):
        '''
        Switch to idle mode.

        Args:
            on:      boolean, [True, False], Whether to Switch to idle mode.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== idle_mode ========")
        resp = self.locustI2C.idleMode(on)
        return "done"

    def cap_detect(self, open_threshold='600', detect_threshold='5000'):
        '''
        Cap detection.

        Args:
            open_threshold:       string, cap detection open timer threshold in micro-seconds.
            detect_threshold:     string, cap detection detect timer threshold in micro-seconds.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== cap_detect ========")
        capExist = self.locustI2C.capDetection(open_threshold, detect_threshold)
        if capExist:
            self._logger.info("GN host: cap detection successful")
            dmesg = 'cap detected successfully'
        else:
            self._logger.info("GN host: cap failed to detect")
            dmesg = 'cap failed to detect'
        return 'done: ' + dmesg

    def enable_powerpath(self, on=True):
        '''
        enable power path.
        Args:
            on:      boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== enable_powerpath ========")
        if on:
            self.locustB2P.enablePowerPath("HostLocust")
            self.locustB2P.pullup(False)
            dmesg = 'power path enabled'
            # self.locustB2P.getState()

        else:
            self.locustB2P.pullup(True)
            self.locustB2P.disablePowerPath("HostLocust")
            dmesg = 'power path disabled'
            # self.locustB2P.getState()
        return "done: " + dmesg

    def ping_device(self, timeout=3):
        '''
        ping the device.
        Args:
            timeout:    int,   ping timeout in seconds.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== ping_device ========")
        TimeBegin = time.time()
        while ((time.time() - TimeBegin) < timeout):
            # reset has to be done before ping to setup linkstate; Otherwise b2p path to device doesn't work
            self.locustB2P.sendReset("DeviceLocust", 0x01)
            if self.locustB2P.sendPing("DeviceLocust"):
                return 'done: locust device ping successfully'
        else:
            return 'done: locust device ping failed'

    def reset_laguna(self):
        '''
        Pulse PMU reset.

        Locust A0 bug -- after crabs reset, locust host has to be reset,
                         and link again if a 2nd crabs reset is required.

        After PMUReset, gn.resetAll() and gn.enableLink() is required to establish connections to DUT
        WE ARE DOING CRABS RESETS, THIS SHOULD BE A LAST RESORT ONLY

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== reset_laguna ========")
        self.enable_powerpath(False)
        self.locustB2P.sendReset("HostLocust", reset_mode=0x00)
        return "done: laguna reset successfully"

    def force_dfu(self, on=True):
        '''
        Change force_dfu pin status by using 0x1868 (0x0804) register
        Args:
            on:      boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== force_dfu ========")
        regVal = self.locustB2P.readLagunaReg(0x0804)[0]

        if on:
            regTarget = regVal | 0b00100000
            dmesg = 'Force DFU on'
        else:
            regTarget = regVal & 0b11011111
            dmesg = 'Force DFU off'

        self.locustB2P.writeLagunaReg(0x0804, regTarget)
        self._logger.info("GN host:" + dmesg)

        return "done, " + dmesg

    def force_dfu_gpio(self, on=True):
        '''
        Change forceDFU pin of Laguna to on or off, laguna gpio17.

        Args:
            on:      boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== force_dfu_gpio ========")
        if on:
            self.locustB2P.writeLagunaReg(0x1825, 0x41, addDum=False)
            self._logger.info("GN host: Force DFU on")

        else:
            self.locustB2P.writeLagunaReg(0x1825, 0x62, addDum=False)
            self._logger.info("GN host: Force DFU off")

        return "done"

    def force_dfu_mode(self):
        '''
        Force DUT to enter DFU mode
        '''
        self._logger.info("======== Force SoC into DFU mode ========")
        REG_DFU_CANCEL = 0x240b
        self.forceLagunaPowerState(state="RESTART_DFU")
        time.sleep(0.3)
        self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=0x1, wtype="reg16",
                                register=REG_DFU_CANCEL, destination="DeviceLocust")
        self._logger.info("GN host: Force DUT into DFU mode")
        return "done"

    def reset_host(self, on=True):
        '''
        Toggle host reset pin of Durant.

        Args:
            on:      boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== reset_host ========")
        if on:
            # self.locustB2P.writeLagunaReg(0x24bb,0x00, addDum=False)
            self.locustB2P.writeLagunaReg(0x080c, 0x00, addDum=False)
            dmesg = 'host reset on'
        else:
            # self.locustB2P.writeLagunaReg(0x24bb,0x03, addDum=True)
            self.locustB2P.writeLagunaReg(0x080c, 0x03, addDum=True)
            dmesg = 'host reset off'

        self._logger.info("GN host: " + dmesg)

        return "done: " + dmesg

    def ping_soc(self):
        '''
        B2p ping SoC in DFU mode.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== ping_soc ========")
        rsp = self.locustB2P.b2p_uart.SendRead(rcode=0x0, cmd=0x0, payload=[0, 2], timeout=0.2)
        dmesg = "{0}".format(list(rsp))
        self._logger.info("GN host: {0}".format(list(rsp)))
        if (rsp[0] == 2):
            self._logger.info("GN host: B2P device found")
        return "done: b2p response " + dmesg

    def get_device_info(self):
        '''
        get device info, DFU mode is required.

        Returns:
            string, device info.
        '''
        self._logger.info("======== get_device_info ========")
        RSP = self.locustB2P.b2p_uart.SendRead(rcode=0x0, cmd=0x02, payload=[0], timeout=0.2)
        [stat, chipidLow, chipidHigh, boardidLow, boardidHigh, securityEpoch,
         prodStatus, securityMode, securityDomain, ecid, nonce1, nonce2,
         nonce3, nonce4, chipRev] = struct.unpack('>BBBBBBBBBQ4QB', RSP)
        chipid = (chipidHigh << 8 | chipidLow)
        boardid = (boardidHigh << 8 | boardidLow)
        temp = 0
        while ecid != 0:
            temp = (temp << 8) + (ecid & 0xFF)
            ecid = ecid >> 8
        ecid = temp
        msg = "GN host: ChipId = 0x%x, BoardID = 0x%x, Epoch = %d, Prod = %s, SecMode = %s, SecDom = %d,\
               ECID = 0x%x, Nonce1 = 0x%x, Nonce2 = 0x%x, Nonce3 = 0x%x, Nonce4 = 0x%x, CRev = %d" % (
              chipid, boardid, securityEpoch, prodStatus, securityMode, securityDomain, ecid, nonce1,
              nonce2, nonce3, nonce4, chipRev)
        self._logger.info(msg)
        return msg

    def enter_laguna_testmode(self):
        '''
        Enable test mode of laguna.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== enter_laguna_testmode ========")
        TEST_REG_EN = [0x3100, 0x3101, 0x3102, 0x3103]
        TEST_EN_STATUS = 0x3105
        data = [0x61, 0x45, 0x72, 0x4f]
        for i in range(4):
            self.locustB2P.writeLagunaReg(TEST_REG_EN[i], data[i])
        resp = self.locustB2P.readLagunaReg(TEST_EN_STATUS)
        if resp[0] == 1:
            dmesg = "enter Laguna test mode succesfully, status = {0}".format(resp)
        else:
            dmesg = "Error - enter Laguna test mode failed, status = {0}".format(resp)

        self._logger.info("GN host: " + dmesg)

        return 'done: ' + dmesg

    def pp7v5_passthrough(self, on=True):
        '''
        Laguna test mode is required, Enable PP7V5 passthrough to SoC PP5V3.

        Args:
            on:      boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== pp7v5_passthrough ========")
        if on:
            self.locustB2P.writeLagunaReg(0x2f1c, 0x01)
            dmesg = "PP7V5 to SoC 5V3 pass through enabled"
        else:
            self.locustB2P.writeLagunaReg(0x2f1c, 0x00)
            dmesg = "PP7V5 to SoC 5V3 pass through disabled"

        self._logger.info("GN host: " + dmesg)

        return "done: " + dmesg

    def amux_select(self, src='AMUX0', target='ax'):
        '''
        Laguna test mode is required.

        Args:
            src: string, ['disabled', 'AMUX0', 'AMUX1', 'AMUX2', 'AMUX3', 'AMUX4', 'AMUX5', 'AMUX6','AMUX7',
                          'VDD_MAIN_SNS', 'VBAT_SNS_CHG', 'BUCK0_FB', 'BUCK1_FB', 'BUCK2_FB', 'BUCK3_FB',
                          'BUCK4'_FB, 'BUCK5_FB', 'LDO1_VOUT', 'LDO2_VOUT', 'LDO3_VOUT', 'LSC_VOUT01', 'LSC_VOUT02'].
            target: string, ['ax', 'ay'].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== amux_select ========")
        # CHANNEL TABLE 'Name':[acore_domain,reg_value]
        CHTable = {
            'disabled': [0, 0x00, 1],
            'AMUX0': [1, 0x01, 2],  # 200 RON
            'AMUX1': [1, 0x02, 3],  # 200 RON
            'AMUX2': [1, 0x03, 4],  # 200 RON
            'AMUX3': [1, 0x04, 5],  # 200 RON
            'AMUX4': [0, 0x05, 6],  # 200 RON
            'AMUX5': [0, 0x02, 7],  # 5k RON
            'AMUX6': [0, 0x03, 8],  # 5k RON
            'AMUX7': [0, 0x04, 9],  # 5k RON
            'VDD_MAIN_SNS': [0, 0x01, 10],
            'VBAT_SNS_CHG': [0, 0x02, 11],
            'NTC_BAT_P': [0, 0x03, 12],
            'BUCK0_FB': [0, 0x04, 13],
            'BUCK1_FB': [0, 0x05, 14],
            'BUCK2_FB': [0, 0x06, 15],
            'BUCK3_FB': [0, 0x07, 16],
            'BUCK4_FB': [0, 0x08, 17],
            'BUCK5_FB': [0, 0x09, 18],
            'PMU_1V5': [0, 0x0A, 19],
            'LDO1_VOUT': [0, 0x0B, 20],
            'LDO2_VOUT': [0, 0x0C, 21],
            'LDO3_VOUT': [0, 0x0D, 22],
            'LSA_VOUT0': [0, 0x0E, 23],
            'LSB_VOUT0': [0, 0x0F, 24],
            'LSB_VOUT1': [0, 0x10, 25],
            'LSC_VOUT0': [0, 0x11, 26],
            'LSC_VOUT1': [0, 0x12, 27],
            'LSC_VOUT2': [0, 0x13, 28],
            'LS_HPA_VOUT': [0, 0x14, 29],
            'VSS_REF': [0, 0x15, 30],
            'GPADC_LVMUX': [0, 0x16, 31],
            'GPADC_HVMUX': [0, 0x17, 32],
            'VSS': [0, 0x18, 33]
        }

        amuxSelect = CHTable[src][1]
        index = CHTable[src][2]

        if target in ['ax', 'ay']:
            if target == 'ax':
                gpio_cfg1_reg = 0x1822  # LAGUNA GPIO14 CFG1
                gpio_cfg2_reg = 0x1839  # LAGUNA GPIO14 CFG2
                if index in [1, 2, 3, 4, 5]:
                    REG_SOURCE = 0x2f6c
                    amuxSelect = amuxSelect << 1
                if index in [6, 7, 8, 9]:
                    REG_SOURCE = 0x7d12
                    amuxSelect = amuxSelect << 1
                if index in range(10, 34, 1):
                    REG_SOURCE0 = 0x7d12
                    amuxSelect0 = 0x05 << 1
                    REG_SOURCE = 0x7d10
                    amuxSelect = amuxSelect << 1
            else:  # target == ay
                gpio_cfg1_reg = 0x1823  # LAGUNA GPIO15 CFG1
                gpio_cfg2_reg = 0x183A  # LAGUNA GPIO15 CFG2
                if index in [1, 2, 3, 4, 5]:
                    REG_SOURCE = 0x2f6d
                    amuxSelect = amuxSelect << 1
                if index in [6, 7, 8, 9]:
                    REG_SOURCE = 0x7d12
                    amuxSelect = amuxSelect << 5
                if index in range(10, 34, 1):
                    REG_SOURCE0 = 0x7d12
                    amuxSelect0 = 0x05 << 5
                    REG_SOURCE = 0x7d11
                    amuxSelect = amuxSelect << 1

            # value = self.locustB2P.readLagunaReg(gpio_cfg2_reg)
            # newValue = value[0] & (0b11111100) | 0x00 #disable pull down
            newValue = 0x00  # disable pull down, select highest voltage range
            self.locustB2P.writeLagunaReg(gpio_cfg2_reg, newValue)
            newValue = 0xc0  # disable gpio
            self.locustB2P.writeLagunaReg(gpio_cfg1_reg, newValue)  # disable gpio, configure as analog pin

            self.locustB2P.writeLagunaReg(0x7d12, 0x00)  # disable 5k MUX
            self.locustB2P.writeLagunaReg(0x2f6c, 0x00)  # disable 200OHM MUX X
            self.locustB2P.writeLagunaReg(0x2f6d, 0x00)  # disable 200OHM MUX Y

            if index <= 5:
                self.locustB2P.writeLagunaReg(REG_SOURCE, amuxSelect)
            else:
                if index > 9:
                    # configure 2nd stage AMUX
                    self.locustB2P.writeLagunaReg(REG_SOURCE, amuxSelect)
                    # configure 1st stage AMUX to select 2nd stage AMUX
                    self.locustB2P.writeLagunaReg(REG_SOURCE0, amuxSelect0)
                else:
                    self.locustB2P.writeLagunaReg(REG_SOURCE, amuxSelect)
            dmesg = "Laguna AMUX output %s on pin AMUXOUT_%s" % (src, target)
        else:
            dmesg = "Error, target is not ax or ay"

        self._logger.info("GN host: " + dmesg)
        return "done: " + dmesg

    def amux_rtc(self, pin='ax', on=True):
        '''
        Enable or disable the 32k RTC clock on AMUXOUT_AX or AMUXOUT_AY pin.

        Args:
            pin:    string,  ['ax', 'ay'].
            on:     boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== amux_rtc ========")
        if on:
            CFG1 = 0x60  # Output 32k RTC
            CFG2 = 0x38  # 1.8V LSC, no pull, 10mA driving
        else:
            CFG1 = 0x00
            CFG2 = 0xc0

        CFG = (CFG1 << 8) + CFG2

        gpio = 14

        if pin == 'ax':
            gpio = 14
        if pin == 'ay':
            gpio = 15

        self.lagunaGpioConfig(gpio, CFG)

        dmesg = "AMUXOUT_%s outputs RTC now" % pin
        self._logger.info("GN host: AMUXOUT_%s outputs RTC now" % pin)

        return "done: " + dmesg

    def enable_kis(self, on=True, forceDFU=False):
        '''
        USB micro to Parrot to Locust host to Locust device to SoC
        Use this function in pairs: first 'on', and once test done use 'off';
        Parrot is easy to cause hang on Mac, if the function is not used in pair

        Args:
            on:           boolean, [True, False].
            forceDFU:     boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== {}_kis ========".format("enabled" if on else "disabled"))
        if on:
            self.ioexp.usbMuxOE(on)
            self.setDPMCommsMode()
            self.locustB2P.eUSBMode(on)
            time.sleep(0.1)
            self.eUSBDurant(on, forceDFU)
        else:
            self.ioexp.usbMuxOE(on)
            self.eUSBDurant(on, forceDFU)

        self._logger.info("GN host: KIS from USB micro to SoC, passthrough Locusts, is {}".format(
                          "enabled" if on else "disabled"))
        return "done: KIS path is {}".format("enabled" if on else "disabled")

    def set_powerstate(self, state):
        '''
        set power state.

        Args:
            state:      string, ['AWAKE', 'SLP', 'OFF', 'ULP'].

        Returns:
            string, "done", api execution successfully.
        '''
        self._logger.info("======== set_powerstate ========")
        destination = "DeviceLocust"
        REG_POWER_STATE = 0x2407
        REG_SHDN_CMD_CFG = 0x2409
        stateVal = {
            "AWAKE": 0x0,
            "SLP": 0x1,  # works
            "OFF": 0x4,
            "ULP": 0x5,
            # "UVP": 0x5  # Do we need UVP
        }
        if stateVal[state] is None:
            self._logger.info("GN host: power state invalid")
            return False
        if stateVal[state] == 0x5:
            self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=0x02,
                                    wtype="reg16", register=REG_SHDN_CMD_CFG, destination=destination)

        self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=stateVal[state],
                                wtype="reg16", register=REG_POWER_STATE, destination=destination)
        dmesg = "powerstate set to {0}".format(stateVal[state])
        self._logger.info("GN host: powerstate set to {0}".format(stateVal[state]))
        return "done: " + dmesg

    def get_powerstate(self):
        '''
        Read back Laguna's current power state.

        Returns:
            string, "done", api execution successfully.
        '''
        self._logger.info("======== get_powerstate ========")
        stateVal = {
            0x0: "AWAKE",
            0x1: "SLP",  # works
            0x4: "OFF",
            0x5: "Error",
            0x6: "Reset"
        }
        destination = "DeviceLocust"
        REG_POWER_STATUS = 0x2406
        readback = self.locustB2P.readI2CRegs(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, read_len=0x1,
                                              register=REG_POWER_STATUS, rtype="reg16", destination=destination)
        CURState = readback[0] & 0b111
        PREState = (readback[0] >> 3) & 0b111

        dmesg = "previous power state, {0}, current power state, {1}".format(stateVal[PREState], stateVal[CURState])
        self._logger.info("GN host: " + dmesg)
        return "done: " + dmesg

    def enable_analog_power(self, on=True):
        '''
        enable analog power.

        Args:
            on:           boolean, [True, False].

        Returns:
            string, "done", api execution successfully.
        '''
        self._logger.info("======== enable_analog_power ========")
        if on:
            dmesg = 'switch to MIX analog input'
            self.ioexp.pp4v5Control(0)
        else:
            dmesg = 'switch to internal 4.5V'
            self.ioexp.pp4v5Control(1)

        return "done: " + dmesg

    def run_ping(self, comms_mode="DPM", num=5000):
        '''
        run ping.

        Args:
            comms_mode:   string, ['DPM', 'ASK'], comms mode.
            num:          int, number of loops.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== run_ping ========")
        if comms_mode == "DPM":
            self.setDPMCommsMode()
        else:
            self.setCommsMode(mode="ASK")
        for i in range(num):
            self.locustB2P.sendPing(destination="DeviceLocust")
        return "done"

    def run_loopback(self, comms_mode="DPM", num=5000):
        '''
        run loopback.

        Args:
            comms_mode:   string, ['DPM', 'ASK'], comms mode.
            num:          int, number of loops.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== run_loopback ========")
        test_len = num
        self._logger.info("====== Enabling DPM between Loocust's and doing {} loopback commands\
                         with max checkerboard payload ======".format(test_len))
        if comms_mode == "DPM":
            self.setDPMCommsMode()
        else:
            self.setCommsMode(mode="ASK")
        P = 0
        F = 0
        self._logger.info("Running Loopback Test...")

        for i in range(test_len):
            if i == (.25 * test_len):
                self._logger.info("25% complete...")
            elif i == (.5 * test_len):
                self._logger.info("50% complete...")
            elif i == (.75 * test_len):
                self._logger.info("75% complete...")
            elif i == (1 * (test_len - 1)):
                self._logger.info("100% complete...")
            resp = self.locustB2P.sendLoopback(quiet=True, destination="DeviceLocust",
                                               data=[0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55, 0xaa, 0x55,
                                                     0xaa, 0x55, 0xaa, 0x55])
            # self._logger.info(resp)
            if resp is not False:
                P = P + 1
            else:
                F = F + 1

        dmesg = "Pass: {}, Fail: {}, % Success: {}%".format(P, F, 100 * (P / (P + F)))
        self._logger.info("GN host: " + dmesg)
        return "done: " + dmesg

    def set_b2p_timeouts(self):
        '''
        Setting mid-remote-packet and total-remote-packet timeouts to higher values.

        Default values are ~10mS.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== set_b2p_timeouts ========")
        REG_CONFIRM_COMMS = 0x51
        REG_CONFIRM_COMMS_TIMEOUT = 0x59

        # Set GN timeout to max
        reg59_dev = self.locustB2P.readLocustReg(REG_CONFIRM_COMMS_TIMEOUT, target='host', n=1)[0]
        if reg59_dev >> 5 != 0x7:
            value_to_send = (reg59_dev & 0x1F | 0xE0)
            self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS_TIMEOUT, value_to_send, target='host')

        # Set DUT timeout to max
        reg59_dev = self.locustB2P.readLocustReg(REG_CONFIRM_COMMS_TIMEOUT, target='device', n=1)[0]
        if reg59_dev >> 5 != 0x7:
            value_to_send = (reg59_dev & 0x1F | 0xE0)
            self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS_TIMEOUT, value_to_send, target='device')

        hostCFG5 = self.locustB2P.readLocustReg(0x55, target='host', n=1)[0]  # 4:0,10ms to 320ms,mid_remote_timeout
        devCFG5 = self.locustB2P.readLocustReg(0x55, target='device', n=1)[0]  # 4:0,10ms to 320ms,mid_remote_timeout
        hostCFG6 = self.locustB2P.readLocustReg(0x56, target='host', n=1)[0]  # 4:0,10ms to 320ms,total_remote_timeout
        devCFG6 = self.locustB2P.readLocustReg(0x56, target='device', n=1)[0]  # 4:0,10ms to 320ms,total_remote_timeout
        self._logger.info('GN host: Default [MIDPACK_REMOTE_TIMEOUT], GN - %s, DUT - %s' % (
                          hex(hostCFG5 & 0b11111), hex(devCFG5 & 0b11111)))
        self._logger.info('GN host: Default [TOTAL_REMOTE_TIMEOUT], GN - %s, DUT - %s' % (
                          hex(hostCFG6 & 0b11111), hex(devCFG6 & 0b11111)))

        hostcfg5 = hostCFG5 | 0b11100
        devcfg5 = devCFG5 | 0b11111
        hostcfg6 = hostCFG6 | 0b11100
        devcfg6 = devCFG6 | 0b11111

        self.locustB2P.writeLocustReg(0x55, hostcfg5, target='host')  # 4:0, 10ms to 320ms, mid_remote_timeout
        self.locustB2P.writeLocustReg(0x56, hostcfg6, target='host')  # 4:0, 10ms to 320ms, mid_remote_timeout
        self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS, 0x01, target='host')
        self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS, 0x0, target='host')

        self.locustB2P.writeLocustReg(0x55, devcfg5, target='device')  # 4:0, 10ms to 320ms, mid_remote_timeout
        self.locustB2P.writeLocustReg(0x56, devcfg6, target='device')  # 4:0, 10ms to 320ms, mid_remote_timeout
        self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS, 0x01, target='device')
        self.locustB2P.writeLocustReg(REG_CONFIRM_COMMS, 0x0, target='device')

        hostCFG5 = self.locustB2P.readLocustReg(0x55, target='host', n=1)[0]  # 4:0,10ms to 320ms,mid_remote_timeout
        devCFG5 = self.locustB2P.readLocustReg(0x55, target='device', n=1)[0]  # 4:0,10ms to 320ms,mid_remote_timeout
        hostCFG6 = self.locustB2P.readLocustReg(0x56, target='host', n=1)[0]  # 4:0,10ms to 320ms,total_remote_timeout
        devCFG6 = self.locustB2P.readLocustReg(0x56, target='device', n=1)[0]  # 4:0,10ms to 320ms,total_remote_timeout

        self._logger.info('GN host: New [MIDPACK_REMOTE_TIMEOUT], GN - %s, DUT - %s' % (
                          hex(hostCFG5 & 0b11111), hex(devCFG5 & 0b11111)))
        self._logger.info('GN host: New [TOTAL_REMOTE_TIMEOUT], GN - %s, DUT - %s' % (
                          hex(hostCFG6 & 0b11111), hex(devCFG6 & 0b11111)))

        return "done"

    def lagunaGpioConfig(self, gpio=0, val=0x0000):
        '''
        configure laguna gpio

        Args:
            gpio:   int, [0~22], gpio number.
            val:    int, (configure1<<8) + configure2.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== lagunaGpioConfig ========")
        REG_GPIO_CFG1 = 0x1814
        REG_GPIO_CFG2 = 0x182b
        val1 = (val >> 8) & 0xff
        val2 = val & 0xff
        self.locustB2P.writeLagunaReg(REG_GPIO_CFG1 + gpio, val1)
        self.locustB2P.writeLagunaReg(REG_GPIO_CFG2 + gpio, val2)

        return "done"

    def forceLagunaPowerState(self, state):
        '''
        Force laguna power state.

        Args:
            state:   string, ['AWAKE', 'SLP', 'RESTART', 'RESTART_DFU', 'OFF', 'SHUTDOWN'].

        Returns:
            boolean, [True, False].
        '''
        self._logger.info("======== forceLagunaPowerState ========")
        destination = "DeviceLocust"
        REG_POWER_STATE_FORCE = 0x2408
        REG_POWER_STATE = 0x2406
        REG_FROCE_DFU = 0x2407
        state_val = {
            "AWAKE": 0x0,
            "SLP": 0x1,
            "RESTART": 0x2,
            "RESTART_DFU": 0x3,
            "OFF": 0x4,
            "SHUTDOWN": 0x5
        }
        if state_val[state] is None:
            self._logger.info("GN host: power state invalid")
            return False
        readback = self.locustB2P.readI2CRegs(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, read_len=0x1,
                                              register=REG_FROCE_DFU, rtype="reg16", destination=destination)
        if readback is None:
            self._logger.info("GN host: Error, b2p not able to readback data, check funbus connection")
            return False
        value_to_write = readback[0] & 0xF8 | state_val[state]
        self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=value_to_write,
                                wtype="reg16", register=REG_FROCE_DFU, destination=destination)
        return True

    def lagunaIsink(self, current=0x05, target='amuxout_ax'):
        '''
        Laguna Isink control.

        Args:
            current:    int,  greater than 0x11 means disable,
                              0x00-12.8mA, 0x01-6.4mA, 0x02-1.6mA, 0x03-0.8mA.
            target:     string, ['buck0', 'buck1', 'buck2', 'buck3', 'buck5',
                                 'ldo0', 'ldo1', 'ldo2', 'ldo3', 'ls_hpa', 'amuxout_ax']

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== lagunaIsink ========")
        REG_CTRL = 0x7d00
        REG_CONF = 0X7d06
        targetList = {
            'buck0': 0x00,
            'buck1': 0x01,
            'buck2': 0x02,
            'buck3': 0x03,
            'buck4': 0x04,
            'buck5': 0x05,
            'ldo0': 0x06,
            'ldo1': 0x07,
            'ldo2': 0x08,
            'ldo3': 0x09,
            'ls_hpa': 0x0a,
            'amuxout_ax': 0x0b
        }
        if current < 0b100:
            reg_ctrl_val = (targetList[target] << 2) + 0b01
        else:
            reg_ctrl_val = 0x00

        # The order of the operation needs to be followed
        self.locustB2P.writeLagunaReg(REG_CTRL, 0x00)  # disable isink enable first
        self.locustB2P.writeLagunaReg(REG_CONF, current)  # set sink current
        self.locustB2P.writeLagunaReg(REG_CTRL, reg_ctrl_val & 0xfe)  # select target
        self.locustB2P.writeLagunaReg(REG_CTRL, reg_ctrl_val)  # enable isink

        resp1 = self.locustB2P.readLagunaReg(REG_CTRL)
        resp2 = self.locustB2P.readLagunaReg(REG_CONF)
        self._logger.info("GN host: Laguna Isink control register:", resp1[0], "configure register:", resp2[0])
        return "done"

    def parrot2Locust(self):
        '''
        eUSB to Locust host path.

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== parrot2Locust ========")
        self.parrot.port(on=False)
        self.ioexp.parrotCross(1)
        self.ioexp.parrotReset(0)
        time.sleep(0.01)
        self.ioexp.parrotReset(1)
        time.sleep(0.01)
        self.parrot.port(on=True)
        self._logger.info("GN host: eUSB to Locust host path complete")
        return "done"

    def eUSBDurant(self, on=False, forceDFU=False):
        '''
        eUSB durant.

        Args:
            on:           boolean, [True, False].
            forceDFU:     boolean, [True, False].

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== eUSBDurant ========")
        if forceDFU:
            data = 0xf0
        else:
            data = 0xd0

        if on:
            # self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR,
            #                         data=data, wtype="reg16", register=0x1868, destination="DeviceLocust")
            self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=data,
                                    wtype="reg16", register=0x0804, destination="DeviceLocust")
        else:
            # self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR,
            #                         data=0x00, wtype="reg16", register=0x1868, destination="DeviceLocust")
            self.locustB2P.writeI2C(bus=0x01, slave_addr=LAGUNA_I2C_7BIT_ADDR, data=0x00,
                                    wtype="reg16", register=0x0804, destination="DeviceLocust")
        return "done"

    def setCommsMode(self, mode="DPM"):
        '''
        set Comms mode.

        Args:
            mode:    string, ['DPM', 'ASK'].

        Returns:
            boolean, [True, False], whether set Comms mode success.
        '''
        self._logger.info("======== setCommsMode ========")
        REG_COMMS_Mode = 0x52
        REG_CONFIRM_COMMS = 0x51
        REG_CONFIRM_COMMS_TIMEOUT = 0x59

        mode_val = {
            "ASK": 0x00,
            "DPM": 0x80
        }
        if mode_val[mode] is None:
            self._logger.info("GN host: Error - wrong input mode")
            return False

        self.locustB2P.b2p_uart.sequence = 0
        self._logger.info("GN host: COMMS timeout check")
        readback_reg59_dev = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                                        register=REG_CONFIRM_COMMS_TIMEOUT, rtype="reg8",
                                                        destination="DeviceLocust")
        reg59_dev = readback_reg59_dev[0]
        if reg59_dev >> 5 != 0x7:
            value_to_send = (reg59_dev & 0x1F | 0xE0)
            self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_send, wtype="reg8",
                                    register=REG_CONFIRM_COMMS_TIMEOUT, destination="DeviceLocust")

        self._logger.info("GN host: Set COMMS mode bit")
        readback_reg52_dev = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                                        register=REG_COMMS_Mode, rtype="reg8",
                                                        destination="DeviceLocust")
        value_to_send_dev = (readback_reg52_dev[0] & 0x7F) | mode_val[mode]

        readback_reg52_host = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                                         register=REG_COMMS_Mode, rtype="reg8",
                                                         destination="HostLocust")
        value_to_send_host = (readback_reg52_host[0] & 0x7F) | mode_val[mode]

        self.locustB2P.getState("DeviceLocust")
        start_time = time.time()
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_send_dev,
                                wtype="reg8", register=REG_COMMS_Mode, destination="DeviceLocust",
                                get_resp=False)
        self._logger.info('-1--writeI2C time: {0}'.format(time.time() - start_time))
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_send_host,
                                wtype="reg8", register=REG_COMMS_Mode, destination="HostLocust", check_header_only=True)
        self._logger.info('-2--writeI2C time: {0}'.format(time.time() - start_time))

        self._logger.info("GN host: Set confirm COMMS bit of device")
        # time.sleep(1)
        self.locustB2P.getState("DeviceLocust")
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=0x1, wtype="reg8",
                                register=REG_CONFIRM_COMMS, destination="DeviceLocust", timeout=0.2)
        self._logger.info('-3--writeI2C time: {0}'.format(time.time() - start_time))
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=0x0, wtype="reg8",
                                register=REG_CONFIRM_COMMS, destination="DeviceLocust", timeout=0.2)
        self._logger.info('-4--writeI2C time: {0}'.format(time.time() - start_time))

        self._logger.info("GN host: ASK/DPM bit written in Host and Device")
        return True

    def setDPMCommsMode(self, DPM_TX_THSEL=5, DPM_RX_THSEL=8, DPM_SEL_ROUT=2,
                        DPM_SR=0, DPM_CFUN_SEL=2, destination="HostLocust"):
        '''
        set DPM Comms mode.

        Args:
            DPM_TX_THSEL:    int, [0x01~0x07].
            DPM_RX_THSEL:    int, [0x01~0x0F].
            DPM_SEL_ROUT:    int, [0x01~0x03].
            DPM_SR:          int, [0x01, 0x02].
            DPM_CFUN_SEL:    int, [0x01~0x03].
            destination:     string, ['HostLocust', 'DeviceLocust', 'DeviceSOC'].

        Exception:
            RuntimeWarning() if DPM parameters input wrong.
            RuntimeError() if DPM_TX_THSEL readback wrong.

        Returns:
            boolean, [True, False], whether set DPM Comms mode success.
        '''
        self._logger.info("======== setDPMCommsMode ========")
        # DPM_TX_THSEL = "800mV", DPM_RX_THSEL = "250mV", DPM_SEL_ROUT = "4 Ohm",
        # DPM_SR = "100mV/nS", DPM_CFUN_SEL = "45pF to 85pF"
        DPM_TX_THSEL_values = {
            0x0: "200mV",
            0x1: "300mV",
            0x2: "400mV",
            0x3: "500mV",
            0x4: "600mV",
            0x5: "800mV",
            0x6: "1000mV",
            0x7: "1200mV"
        }

        DPM_RX_THSEL_values = {
            0x0: "25mV",
            0x1: "37.5mV",
            0x2: "50mV",
            0x3: "62.5mV",
            0x4: "75mV",
            0x5: "87.5mV",
            0x6: "100mV",
            0x7: "112.5mV",
            0x8: "125mV",
            0x9: "150mV",
            0xA: "175mV",
            0xB: "200mV",
            0xC: "250mV",
            0xD: "300mV",
            0xE: "350mV",
            0xF: "400mV"
        }

        DPM_SEL_ROUT_values = {
            0x0: "3 Ohm",
            0x1: "4 Ohm",
            0x2: "5.8 Ohm",
            0x3: "7.6 Ohm"
        }

        DPM_SR_values = {
            0x1: "100mV/nS",
            0x0: "200mV/nS"
        }

        DPM_CFUN_SEL_values = {
            0x0: "80pF to 135pF",
            0x1: "130pF to 200pF",
            0x2: "45pF to 85pF",
            0x3: "10pF to 50pF"
        }

        try:
            self._logger.info("GN host: set DPM_TX_THSEL = {0}".format(DPM_TX_THSEL_values[DPM_TX_THSEL]))
            self._logger.info("GN host: set DPM_RX_THSEL = {0}".format(DPM_RX_THSEL_values[DPM_RX_THSEL]))
            self._logger.info("GN host: set DPM_SEL_ROUT = {0}".format(DPM_SEL_ROUT_values[DPM_SEL_ROUT]))
            self._logger.info("GN host: set DPM_SR = {0}".format(DPM_SR_values[DPM_SR]))
            self._logger.info("GN host: set DPM_CFUN_SEL = {0}".format(DPM_CFUN_SEL_values[DPM_CFUN_SEL]))
        except:
            raise GrassNinjaHostException("GN host: DPM parameters input wrong!!!!")

        rb_data = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                             register=0x52, rtype="reg8", destination=destination)
        if self.debug:
            # TX bit[2:0] -> 101 ->800mV, RX bit[6:3] -> 1000 -> 125mV
            self._logger.info("GN host: DPM_TX_THSEL, DPM_RX_THSEL {0}".format(hex(rb_data[0])))

        value_to_write_RX_th = (rb_data[0] & 0x87) | (DPM_RX_THSEL << 3)  # set RX threshold to 175mV -> 0x48
        value_to_write_TX_th = (value_to_write_RX_th & 0xF8) | DPM_TX_THSEL

        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_write_TX_th,
                                wtype="reg8", register=0x52, destination=destination)
        rb_data = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x52,
                                             rtype="reg8", destination=destination)
        if rb_data[0] != value_to_write_TX_th:
            raise GrassNinjaHostException("GN host: DPM_TX_THSEL readback wrong")
            return False

        rb_data = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                             register=0x57, rtype="reg8", destination=destination)
        if self.debug:
            self._logger.info("GN host: DPM_SEL_ROUT {0}".format(hex(rb_data[0])))  # bit[5:4] -> 0x10 -> 5.8 ohm
        value_to_write_rout = (rb_data[0] & 0xCF) | (DPM_SEL_ROUT << 4)
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_write_rout,
                                wtype="reg8", register=0x57, destination=destination)

        rb_data = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1,
                                             register=0x58, rtype="reg8", destination=destination)
        if self.debug:
            self._logger.info("GN host: DPM_SR {0}".format(hex(rb_data[0])))  # bit[4] -> 0 ->200mV/ns
        value_to_write_sr = (rb_data[0] & 0xFF) | (DPM_SR << 4)
        # Writing register 0x58 can disable PP to DUT
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_write_sr,
                                wtype="reg8", register=0x58, destination=destination)

        rb_data = self.locustB2P.readI2CRegs(bus=0x00, slave_addr=0x33, read_len=0x1, register=0x5B,
                                             rtype="reg8", destination=destination)
        if self.debug:
            self._logger.info("GN host: DPM_CFUN_SEL {0}".format(hex(rb_data[0])))  # bit[3:2] ->0x10 -> 45pF to 85pF
        value_to_write_cfun = (rb_data[0] & 0xF3) | (DPM_SEL_ROUT << 2)
        self.locustB2P.writeI2C(bus=0x00, slave_addr=0x33, data=value_to_write_cfun,
                                wtype="reg8", register=0x5B, destination=destination)

        ret = self.setCommsMode(mode="DPM")
        return ret

    def resetDeviceLocust(self):
        '''
        b2p reset device Locust

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== resetDeviceLocust ========")
        self.locustB2P.sendReset("DeviceLocust", reset_mode=0x01)
        self.locustB2P.sendPing(destination="DeviceLocust")
        self.locustB2P.enablePowerPath(destination="DeviceLocust")
        return "done"

    def disconnectUSB(self):
        '''
        USE THE FUNCTION WITH CAUTION:
        ONCE USB MUX IS OFF, ALL GRASSNINJA PORT WILL DISAPPEAR IMDEDIATELY
        THIS CAN'T BE RECOVERED UNTIL GRASSNINJA IS POWER CYCLED

        Returns:
            string, "done", api execution successful.
        '''
        self._logger.info("======== disconnectUSB ========")
        self.ioexp.usbMuxOE(False)
        return "done"

    def sys_reset(self):
        '''
        This will power cycle the board
        '''
        self._logger.info("======== sys_reset ========")
        self.ioexp.sysReset()
        return "done: GN is power cycled, please wait 1s for board to recover"

    def uart_open(self):
        '''
        Open uart port and reset input/output buffer.

        Returns:
            string, "done", api execution successful

        '''
        self._logger.info("======== uart_open ========")
        self.b2pUart.open()
        return 'done'

    def uart_close(self):
        '''
        Uart close port immediately

        Returns:
            string, "done", api execution successful

        '''
        self._logger.info("======== uart_close ========")
        self.b2pUart.close()
        return 'done'

    def disableParrotPower(self):
        '''
        '''
        self._logger.info("======== disableParrotPower ========")
        self.ioexp.pp3V3(0)
        return 'done'

    def enableParrotPower(self):
        '''
        '''
        self._logger.info("======== enableParrotPower ========")
        self.ioexp.pp3V3(1)
        return 'done'

    def writeLagunaReg(self, register, data, addDum=False):
        '''
        '''
        self.locustB2P.writeLagunaReg(register, data, addDum)
        return "done"


