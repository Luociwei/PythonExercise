import os
import time
import uuid
import base64
import argparse
import traceback
from rpc_client import RPCClientWrapper
from publisher import *

# 60s transfer timeout
TRANSFER_TIMEOUT = 60 * 1000.0


def main():
    usage = '''Usage:
        python get_file.py -i XAVIER_IP_ADDR -p XAVIER_PORT -f FILE_PATH
        '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--check_version', action='store_true',
                        help='check xavier version', default=False)
    parser.add_argument('-i', '--ip', help='xavier RPC server ip address', default="127.0.0.1")
    parser.add_argument('-p', '--port', help='xavier RPC server port', default=5556)
    parser.add_argument('-f', '--file', help='file path on xavier to retrive', default='log')
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
        '''
        client.get_and_write_file(None, 'tmp/none.dst')
        client.get_and_write_file('~/ssh_qsmc.h', 'tmp/dst_ssh_qsmc.h')
        client.get_and_write_file('~/ssh_qsmc.sh', 'tmp/dst_ssh_qsmc.sh')
        client.get_and_write_file('log', 'tmp/log.tgz')
        '''
        client.server_mode()
        time.sleep(2)
        client.get_and_write_file('#log', 'tmp/log_before.tgz')
        client.server_reset_log()
        client.get_and_write_file('#log', 'tmp/log_after.tgz')
        client.get_and_write_file('log', 'tmp/log_full.tgz')
    except Exception as e:
        print 'Exception found during firmware update; traceback: ', traceback.format_exc()


if __name__ == '__main__':
    main()
