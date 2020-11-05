# -*- coding: utf-8 -*-
import os
import uuid
import json
import time
import base64
import ctypes
import socket
import tarfile
import platform
import traceback
from subprocess import PIPE, Popen
from threading import Thread
import re
from itertools import takewhile

MIX_FW_VERSION_FILE = '/mix/version.json'
# whitelist for get_file/send_file through RPC
# ~ is for debug; /tmp is ramdisk for temp file;
# /var/fw_update/upload is firmware update folder.
# /var/log/rpc_log is log folder.
ALLOWED_FOLDER_SEND_FILE = ['~', '/tmp', '/var/fw_update/upload']
ALLOWED_FOLDER_GET_FILE = ['~', '/tmp', '/var/log/rpc_log']


def _delayed_shutdown(delay):
    '''
    internal function run in a thread that shutdown linux in given seconds.
    '''
    time.sleep(delay)
    os.system('shutdown -P now')


def _delayed_reboot(delay):
    '''
    internal function run in a thread that reboot linux in given seconds.
    '''
    time.sleep(delay)
    os.system('reboot')


class Xavier(object):
    '''
    Xavier class providing APIs for xavier management like send file and set rtc.

    Args:
        log_folder: string, system log folder, for getting log RPC API.
        xobject: xobject instance, for power off module.

    Examples:
        xavier.Xaxier(xobject=xobject)
    '''
    rpc_public_api = ['get_rtc', 'set_rtc', 'get_ip', 'set_ip', 'fw_version',
                      'set_ntp_server', 'get_ntp_server', 'get_ntp_status',
                      'get_file', 'send_file', 'get_all_log', 'shutdown',
                      'reboot']

    ipaddr_path = '/boot/ip_addr'

    DEFAULT_IP_ADDR_PATH = "/boot/ip_addr.conf"
    DEFAULT_PROFILE_PATH = "/mix/config/profile.json"

    def __init__(self, log_folder='/var/log/rpc_log', xobject=None):
        # xobject: will use dut.power_control_modules and dut.instances
        # for powering off module.
        self.xobject = xobject

        self.log_folder = os.path.expanduser(log_folder)

    def set_ip(self, ip_addr):
        '''
        Xavier set ip address

        Args:
            ip_addr: string, ip address to be set.

        Examples:
            xavier.set_ip('169.254.1.32')

        '''
        assert isinstance(ip_addr, basestring)
        pattern = re.compile("([0-9]{1,3}\.){3}[0-9]{1,3}")
        result = pattern.match(ip_addr)
        if result is None:
            raise Exception("{} address not valid".format(ip_addr))

        ip_addr_file = open(self.get_ip_store_file(), "w+")
        ip_addr_file.write(ip_addr)
        ip_addr_file.close()
        print("ifconfig eth0 {}".format(ip_addr))
        os.popen("ifconfig eth0 {}".format(ip_addr))

    def get_ip(self):
        '''
        Xavier get ip address

        Examples:
            data = xaiver.get_ip()
            print(data)

        '''
        out = os.popen("ifconfig | grep 'inet addr:' | grep -v '127.0.0.1' "
                       "| cut -d: -f2 | awk '{print $1}' | head -1").read()
        pattern = re.compile("([0-9]{1,3}\.){3}[0-9]{1,3}")
        result = pattern.match(out)
        if result is None:
            return ""
        return result.group(0)

    def get_ip_store_file(self):
        try:
            with open(self.DEFAULT_PROFILE_PATH, "r") as f:
                profile = json.load(f)
                return profile.get("network").get("ip_addr_file")
        except Exception:
            return self.DEFAULT_IP_ADDR_PATH

    def fwup(self):
        '''
        Do the actual update job.

        Currently just reboot Xavier to let shell script work.
        Could update to do more in the future.
        '''
        self.reboot()

    def get_file(self, target, base64_encoding=True):
        '''
        target could be folder path or file path on xavier; '~' is allowed.
        folder of target (file folder or folder itself) should be in whitelist;
        any request outside of whitelist will be rejected.

        Specially:
            target '#log' mean to get all log files of current rpc
            server (in a tmp folder).
            target 'log' mean to get the whole rpc log folder

        Args:
            target:          string, file path on xavier.
            base64_encoding: boolean, whether returned data is encoded by base64.

        Returns:
            tuple, 2-item tuple ('PASS', data) or (errmsg, '')

        Raises:
            errmsg should be a string about failure reason.
            data is encoded in base64; client will be responsible
            for decoding it into origin data.

        '''
        # check whitelist
        log_folder = self.logger.log_folder
        if log_folder not in ALLOWED_FOLDER_GET_FILE:
            ALLOWED_FOLDER_GET_FILE.append(log_folder)

        if not target:
            return 'Invalid target {} to get from server'.format(target), ''

        # handle trailing '/'
        target = target.rstrip(os.path.sep)

        if target == 'log':
            # get the whole log folder.
            target = self.logger.log_folder

        tmp_folder = ''
        if target == '#log':
            # get all log files of current rpc server.
            # put them into a temp folder inside of log
            # pack into tgz and return back to client.
            log_folder = self.logger.log_folder
            tmp_folder = os.path.join(log_folder, 'rpc_server_log_{}_{}'.format(self.logger.name, uuid.uuid4().hex))
            os.mkdir(tmp_folder)
            for f in self.logger.files() + self.service_logger.files():
                dst = os.path.join(tmp_folder, os.path.basename(f))
                os.rename(f, dst)

            # for rpc_default.log which host non-rpc_server log
            other_log = os.path.join(log_folder, 'rpc_default.log')
            if os.path.exists(other_log):
                dst = os.path.join(tmp_folder, 'rpc_default.log')
                with open(other_log, 'rb') as f_in:
                    with open(dst, 'wb') as f_out:
                        f_out.write(f_in.read())
            target = tmp_folder

            # restart server logger after removing log files.
            # without this there will be no log in log file after previous log file being removed.
            self.reset_log()

        # handle "~" in target file/folder
        target = os.path.expanduser(target)

        folder = os.path.dirname(target)
        fn = os.path.basename(target)

        # handle "~" in white list.
        tgz_fn = ''
        allowed_folder = [os.path.expanduser(i) for i in ALLOWED_FOLDER_GET_FILE]
        if os.path.isfile(target):
            # for file, check if it is in allowed folder.
            if folder not in allowed_folder:
                msg = 'Invalid folder {} to get file from; supporting one in {}'
                return msg.format(folder, ALLOWED_FOLDER_GET_FILE), ''
        elif os.path.isdir(target):
            # for folder, check if it is one of the allowed folder.
            if target not in allowed_folder and os.path.dirname(target) not in allowed_folder:
                msg = 'Invalid folder {} to get file from; supporting one in {}'
                return msg.format(folder, ALLOWED_FOLDER_GET_FILE), ''
            # zip folder into tgz file: ~/aaa --> ~/aaa.tgz, /opt/seeing/log --> ~/log.tgz
            home = os.path.expanduser('~')
            os.chdir(folder)
            tgz_fn = os.path.join(home, '{}_{}.tgz'.format(fn, uuid.uuid4().hex))
            with tarfile.open(tgz_fn, 'w') as tgz:
                tgz.add(fn)
            # the actual file to transfer is the tgz file.
            target = tgz_fn
        elif not os.path.exists(target):
            return 'Target item to retrieve does not exist: {}'.format(target), ''
        else:
            return 'Target item to retrieve exists but is neither a folder nor a file: {}'.format(target), ''

        with open(target, 'rb') as f:
            data = f.read()

        # cleanup: remove tmp tgz file for folder.
        if tgz_fn:
            os.remove(tgz_fn)

        # cleanup: remove tmp_folder for creating tgz.
        if tmp_folder:
            for f in os.listdir(tmp_folder):
                os.remove(os.path.join(tmp_folder, f))
            os.rmdir(tmp_folder)

        if base64_encoding:
            data = base64.b64encode(data)

        return 'PASS', data

    def send_file(self, fn, data, folder):
        '''
        send file from RPC client to RPC server;

        fn should be filename in string;
        data should be base64 encoded raw binary file content.
        the function will write the file into file at predefined location with filename==fn.
        '''
        len_data = len(data)
        if not folder:
            raise Exception('Destination folder not provided.')
        if len_data > 1024 * 1024 * 500:
            # image larger than 500M is highly possible an mistake;
            # usually should be within 100MB wo fs and within 200MB with fs.
            raise Exception('Invalid file size {}; should be smaller than 500MB.'.format(len_data))

        # prevent fn like '../../root/xxx'
        if not fn == os.path.basename(fn):
            raise Exception('Invalid file name {}; should not include any path info.'.format(fn))

        # prevent arbitrary file write.
        folder = folder.rstrip(os.path.sep)
        if folder not in ALLOWED_FOLDER_SEND_FILE:
            msg = 'Invalid destination folder {}; supporting one in {}'
            msg = msg.format(folder, ALLOWED_FOLDER_SEND_FILE)
            raise Exception(msg)

        # expand to full path for ~
        folder = os.path.expanduser(folder)

        with open(os.path.join(folder, fn), 'wb') as f:
            data = base64.b64decode(data)
            # TODO: handle base64 decode error
            f.write(data)

        return 'PASS'

    def get_all_log(self, base64_encoding=True):
        '''
        For RPC log folder (default to /var/log/rpc_log), package the folder
        into .tgz, encode it with base64 if requested, and return to host.

        Args:
            target:          string, file path on xavier.
            base64_encoding: boolean, default True, whether returned data is encoded by base64.
                                      Use default True when getting log through RPC.

        Returns:
            tuple, ('PASS', data).

        '''
        return self.get_file('log')

    def get_rtc(self):
        return time.time()

    def set_rtc(self, timestamp):
        '''
        placeholder for the moment. Will be replaced with real set_rtc code later on.

        This function will set Xavier Linux system RTC to give value
        And set FPGA RTC to the same give value.

        Args:
            timestamp: float/int, should be seconds from 1970/1/1.

        Returns:
            string, 'PASS' when succeed; Error string in case of any error.

        Examples:
            # client.server_set_rtc(time.time()) will set xavier RTC to current time.
            timestamp = 1538296130  #2018-09-30 16:28:50 CST
            client.server_set_rtc(timestamp)

        '''
        self.logger.info('Setting RTC to {}'.format(timestamp))

        os_str = platform.platform().lower()
        # Xavier: Linux-4.0.0.02-xilinx-armv7l-with-Ubuntu-14.04-trusty

        if not ('xilinx' in os_str and 'linux' in os_str):
            self.logger.info('Skip Setting RTC to {} on host.'.format(timestamp))
            return '--PASS--'

        try:
            timestamp = float(timestamp)
        except:
            raise ValueError('timestamp value should be float or int!')

        assert timestamp >= 0

        if 0 != os.system('date -s @' + str(timestamp)):
            return '--FAIL--'

        return '--PASS--'

    def set_ntp_server(self, host_addr):
        '''
        Synchronizing date with host by NTP(Network Time Protocol) server

        Args:
            host_addr:    string, (<IP>), IPv4 address, as '64.236.96.53'

        Returns:
            string, '--PASS--' or Assert failure.

        Examples:
            host_addr = '210.72.145.44'
            xavier.set_ntp_server(host_addr)

        '''
        def set_server_ip(host_addr):
            ntp_conf_file = '/etc/ntp.conf'

            def is_addr_exist():
                with open(ntp_conf_file, 'r') as f:
                    datas = f.readlines()
                    for line in datas:
                        if line.startswith('server ' + str(host_addr) + ' '):
                            return True
                    return False

            def addr_append():
                with open(ntp_conf_file, 'a') as f:
                    f.writelines('\nserver ' + str(host_addr) + ' ')

            if not is_addr_exist():
                addr_append()

            return True

        assert (0 == os.system('service ntp stop')), 'ntp service stop fail'
        assert (0 == os.system('ntpdate ' + host_addr)), 'ntpdate get date fail'
        set_server_ip(host_addr)
        assert (0 == os.system('service ntp start')), 'ntp service start fail'

        return '--PASS--'

    def get_ntp_server(self):
        '''
        Get Xavier NTP server setting

        Returns:
            list, list of servers in /etc/ntp.conf.

        Examples:
            ret = xavier.get_ntp_server()
            # ret could be ['server 169.254.1.1']
        '''
        ntp_conf_file = '/etc/ntp.conf'
        with open(ntp_conf_file, 'rb') as f:
            lines = f.read().splitlines()
            # filter comments and empty lines
            return [line.strip() for line in lines if (not line.startswith('#') and line.strip())]

    def get_ntp_status(self):
        '''
        Get Xavier NTP server status; 'service ntp status'

        Returns:
            string, (stdout, stderr) of 'service ntp status'

        Examples:
            ret = xavier.get_ntp_status()

        '''
        cmd = 'service ntp status'
        ret = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True).communicate()
        return ret

    def fw_version(self):
        '''
        return dictionary of mix firmware;

        mix fw version is defined in a json file;
        Currently in /mix/version.json (MIX_FW_VERSION_FILE).

        Returns:
            dict, firmware version information.
        '''
        if not MIX_FW_VERSION_FILE:
            raise Exception('MIX_FW_VERSION_FILE not defined.')
        with open(MIX_FW_VERSION_FILE, 'rb') as f:
            data = f.read()
        return json.loads(data)

    def power_off_all_modules(self):
        '''
        power off all modules for this Xavier.

        Returns:
            string, 'done' when all power off succeed; report error msg of that module if it failed to power off.
        '''
        def power_off_shared_module(module_name):
            '''
            if obj has pre_power_down(), call it;
            if obj has power pin defined in 2-step-power-on, toggle it
            '''
            shared_devices_profile = self.xobject.get_object('profile').get('shared_devices', {})
            module_profile = shared_devices_profile[module_name]
            module_obj = self.xobject.shared_devices[module_name]
            module_power_pin = self.xobject._modules.get(module_obj, None)
            if hasattr(module_obj, 'pre_power_down'):
                pre_power_down_args = module_profile.get('pre_power_down_args', {})
                try:
                    module_obj.pre_power_down(**pre_power_down_args)
                    self.logger.info('Shared device {} pre_power_down().'.format(module_name))
                except:
                    msg = ('Exception found when calling shared module'
                           ' {}.pre_power_down(); trackback = {}')
                    msg = msg.format(module_name, traceback.format_exc())
                    self.logger.error(msg)
                    return msg
            else:
                # could be non-module driver intances.
                msg = ('Shared device {} does not have pre_power_down() API.')
                self.logger.info(msg.format(module_name))

            if module_power_pin:
                active_low = module_profile.get('2-step-power-on', {}).get('active_low', False)
                try:
                    power_off_level = 0 if not active_low else 1
                    module_power_pin.level = power_off_level
                    module_power_pin.direction = 'output'
                    msg = 'Shared device {} powered off; power pin = {}'
                    msg = msg.format(module_name, power_off_level)
                    self.logger.info(msg)
                except:
                    # ignore any error reported by gpio set; just log.
                    msg = 'Exception found when powering down shared module {}; trackback = {}'
                    msg = msg.format(module_name, traceback.format_exc())
                    self.logger.error(msg)
                    return msg
            else:
                msg = ('Shared device {} does not have power_control pin '
                       'defined in profile; skipping turning off power '
                       'for it.')
                self.logger.info(msg.format(module_name))

            return 'done'

        # power off shared modules
        profile = self.xobject.get_object('profile')
        profile_shared_devices = profile.get('shared_devices', {})
        result = [
            power_off_shared_module(device)
            for device, setting in profile_shared_devices.items()
            if 'class' in setting or 'allowed' in setting
        ]
        failed = ';'.join([ret for i in result if i != 'done'])

        # power off dut modules
        result = [
            [
                dut.power_off_module(module_name)
                for module_name in dut.instances
                if module_name in dut.profile and
                isinstance(dut.profile[module_name], dict) and
                ('class' in dut.profile[module_name] or 'allowed' in dut.profile[module_name])
            ] for dut in self.xobject.duts.values()
        ]
        failed += ''.join([';'.join([i for i in dut_ret if i is not 'done']) for dut_ret in result])
        return failed if failed else 'done'

    def turn_off_fpga_led(self):
        '''
        Internal function to turn off FPGA Blue LED by programming empty FPGA image; not exposed on RPC.
        '''
        os.system('cat /dev/null > /dev/xdevcfg')

    def shutdown(self):
        '''
        Power off all modules and shutdown Xavier linux in 3s.

        On non-Xavier, which means in test environment, just return done

        Returns:
            string, shutdown information
        '''
        ret = self.power_off_all_modules()
        if ret is not 'done':
            return ret

        # successfully power off all module; shutdown linux.
        os_str = platform.platform().lower()
        # Xavier: Linux-4.0.0.02-xilinx-armv7l-with-Ubuntu-14.04-trusty
        if 'xilinx' in os_str and 'linux' in os_str:
            self.turn_off_fpga_led()

            msg = 'shutting down in 3s!!!!!!!!'
            self.logger.info(msg)
            thread = Thread(name='delayed_shutdown', target=_delayed_shutdown, args=[3])
            thread.start()
        else:
            msg = 'done'

        return msg

    def reboot(self):
        '''
        power off all modules and reboot Xavier linux in 3s.

        On non-Xavier, which means in test environment, just return done

        Returns:
            string, shutdown information
        '''
        ret = self.power_off_all_modules()
        if ret is not 'done':
            return ret

        # successfully power off all module; shutdown linux.
        os_str = platform.platform().lower()
        # Xavier: Linux-4.0.0.02-xilinx-armv7l-with-Ubuntu-14.04-trusty
        if 'xilinx' in os_str and 'linux' in os_str:
            self.turn_off_fpga_led()

            msg = 'Xavier rebooting in 3s!!!!!!!!'
            self.logger.info(msg)
            thread = Thread(name='delayed_reboot', target=_delayed_reboot, args=[3])
            thread.start()
        else:
            msg = 'done'

        return msg

