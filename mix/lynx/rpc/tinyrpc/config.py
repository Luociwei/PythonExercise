#!/usr/bin/env python
# -*- coding: utf-8 -*-

# some constants
HEARTBEAT_INTERVAL_S = 5
ZMQ_POLL_INTERVAL_MS = 5000
RUNNING = 'running'
DONE = 'done'
TIMEOUT = 'timeout'
ERROR = 'error'
DEBUG_ENABLE = False
CMD_CHANNEL = 'CMD'
DBG_CHANNEL = 'DBG'
THREAD_POOL_WORKERS = 15
DEFAULT_RPC_TIMEOUT_MS = 3000
DEFAULT_MSG_TRANSMIT_TIME_MS = 50
FCT_HEARTBEAT = "FCT_HEARTBEAT"
SERVER_SERVICES = ['server_reset', 'server_mode', 'server_stop', 'server_reboot']
DEBUGGER_REP_ENDPOINT = "tcp://*:9000"

# for server send_file and get_file
ALLOWED_FOLDER_SEND_FILE = ['~', '/opt/seeing/tftpboot', '/mix/upload']

# besides the dst_folders, rpc log folder is also one of the allowed folder;
# it is implied in get_file function dynamically.
ALLOWED_FOLDER_GET_FILE = ['~', '/tmp', '/var/log/rpc_log']

# mix fw version file
MIX_FW_VERSION_FILE = '/mix/version.json'

# initial setting for builtin profiling
PROFILE_RTT = False
PROFILE_CLIENT = False
PROFILE_SERVER = False
PROFILE_SERVER_RTT = False

# separate between instance name and method
NAME_METHOD_SEPARATOR = '.'
