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


QUESTION_MARK = 63
PRINTABLE_LOW_LIMIT = 32
PRINTABLE_HIGH_LIMIT = 126
VID_LENGTH = 3
HW_START_POSITION = 6
SN_START_POSITION = 15
MODULE_INFO_START_ADDR = 0x39
MODULE_INFO_LENGTH = 32


def process_eeprom_bytes(raw_data):
    '''
    Get vid, module type, sn info from data list in eeprom, replace non-printable value with '?'

    Examples:
        result = procee_eeprom_bytes(e2prom_bytes)

    '''
    data = [QUESTION_MARK if 0 < x < PRINTABLE_LOW_LIMIT or x > PRINTABLE_HIGH_LIMIT else x for x in raw_data]
    vid = ''.join(map(chr, list(takewhile(lambda x: x != 0, data[:VID_LENGTH]))))
    hw = ''.join(map(chr, list(takewhile(lambda x: x != 0, data[HW_START_POSITION:SN_START_POSITION]))))
    sn = ''.join(map(chr, list(takewhile(lambda x: x != 0, data[SN_START_POSITION:]))))
    return {"STATUS": "normal", "VID": vid, "MODULE_TYPE": hw, "SN": sn}


def is_pl_device(dev_name):
    '''
    Judge the device is or not pl device
    '''
    if 'MIX_' in dev_name:
        return True
    else:
        return False


def is_valid_host(host_name):
    '''
    Judge the host name valid or not
    '''
    if not host_name or '\x00' in host_name:
        return False
    try:
        res = socket.getaddrinfo(host_name, 0, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_NUMERICHOST)
        return bool(res)
    except socket.gaierror as e:
        if e.args[0] == socket.EAI_NONAME:
            return False
        raise
    return True


def cmdline(command):
    process = Popen(args=command, stdout=PIPE, shell=True)
    return process.communicate()[0]

