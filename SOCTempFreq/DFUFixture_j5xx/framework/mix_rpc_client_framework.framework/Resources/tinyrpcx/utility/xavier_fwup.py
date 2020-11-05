import os
import time
import base64
import argparse
import traceback
from rpc_client import RPCClientWrapper
from publisher import *

# 60s transfer timeout
TRANSFER_TIMEOUT = 60 * 1000.0

# 120s update timeout
UPDATE_TIMEOUT = 120 * 1000.0


def get_package_version(fn):
    '''
    extract version.txt from tgz package and parse into dictionary.
    change characters to lower.
    '''
    pass


def check_version(client, fn=None):
    '''
    Get current fw version from Xavier;
    If fn is provided, get version from given firmware package and compare with live one.
    Return (True/False, msg)
    msg should be string of versions of what ever have been checked.
    '''
    current_version = client.fw_version()
    msg = 'Current fw version: {}'.format(current_version)
    if fn:
        target_version = get_package_version(fn)
        msg += 'target firmware package version: {}'.format(target_version)
    print msg
    need_update = (target_version != current_version)
    return need_update, msg


def fwup(client, fn):
    '''
    send image to xavier, perform firmware update.
    '''
    ret = client.send_file(fn, '/mix/upload', timeout=TRANSFER_TIMEOUT)

    print 'File {} transfered with ret {}.'.format(fn, ret)

    print 'Starting Xavier Firmware Update with {:02f}ms timeout'.format(float(UPDATE_TIMEOUT) / 1000.0)
    uuid = client.server_fwup(timeout_ms=UPDATE_TIMEOUT, asynchronize=True)
    while True:
        # finally rpc will timeout so we don't need to check timeout here.
        status = client.get_status(uuid)[uuid][0]
        if status != 'running':
            print 'fwup started; break.'
            break
        print 'fwup in progress; '
        time.sleep(1)

    time.sleep(5)
    while True:
        # trying to check if server is up after reboot
        try:
            mode = client.server_mode()
            if mode == 'normal':
                print 'fwup finished; break.'
                break
        except:
            print 'fwup in progress;'
        time.sleep(1)

    return 'pass'


def main():
    usage = '''Usage:
        python xavier_fwup.py -i XAVIER_IP_ADDR -p XAVIER_PORT -f FILE_PATH
        '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--check_version', action='store_true',
                        help='check xavier version', default=False)
    parser.add_argument('-i', '--ip', help='xavier RPC server ip address', default="127.0.0.1")
    parser.add_argument('-p', '--port', help='xavier RPC server port', default=None)
    parser.add_argument('-f', '--file', help='file path to transfer', default=None)
    # parser.add_argument('-m', '--mode', help='update mode', default="all")
    args = parser.parse_args()
    ip = args.ip
    port = args.port
    fn = args.file
    check = args.check_version

    if check:
        print 'Checking Xavier version'
        check_version(client, fn)
        exit(0)

    if not port:
        print 'No xavier port is provided; existing.'
        print usage
        exit(-1)

    if not fn:
        print 'No file is provided; existing.'
        print usage
        exit(-1)

    endpoint = 'tcp://{}:{}'.format(ip, port)

    # start client
    ctx = zmq.Context()
    publisher = NoOpPublisher()

    client = RPCClientWrapper(endpoint, publisher)
    try:
        fwup(client, fn)
    except Exception as e:
        print 'Exception found during firmware update; traceback: ', traceback.format_exc()


if __name__ == '__main__':
    main()
