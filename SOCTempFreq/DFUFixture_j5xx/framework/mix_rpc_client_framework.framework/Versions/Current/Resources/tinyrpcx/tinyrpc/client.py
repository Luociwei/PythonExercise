#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import zmq
import time
import ujson as json
import base64
import logging
from threading import Thread
import traceback
import cProfile
from concurrent.futures import ThreadPoolExecutor
from .exc import RPCError
from config import DONE
from config import ERROR
from config import RUNNING
from config import TIMEOUT
from config import DEFAULT_MSG_TRANSMIT_TIME_MS
from config import PROFILE_RTT
from config import PROFILE_CLIENT
from config import NAME_METHOD_SEPARATOR
from protocols.jsonrpc import JSONRPCTimeoutError


def rpc_profile(f):
    def wrapper(self, *args, **kwargs):
        if self.profile:
            self.profiler.enable()
            ret = f(self, *args, **kwargs)
            self.profiler.disable()
            return ret
        else:
            return f(self, *args, **kwargs)

    return wrapper


def rpc_profile_rtt(f):
    '''
    Wrapper function to do builtin profiling used on "call" api.
    RPC RTT time without proxy cost is recorded here, in call() function.
    Time in sequence below is not counted:
    RPC --> RPCClientWrapper.__getattr__ --> RPCProxy.__getattr__ --> --> lambda
    Typical cost in proxy is 10ms if enabled logginging in RPCClientWrapper.__getattr__;
    7ms if commented out the info() line in RPCClientWrapper.__getattr__.

    wrapper will check client's profile attr to determine if do profile;
    wrapper will put cost data into client's profile_rtt_result list.
    RPC profile overhead comparasion:

        using if inside call: 0.2us overhead\n
        using wrapper below when profile is disabled: 0.2us overhead\n
        using wrapper below when profile is enabled: 0.7us overhead\n
    '''
    def wrapper(self, *args, **kwargs):
        if self.profile_rtt:
            start = time.time()
            ret = f(self, *args, **kwargs)
            end = time.time()
            self.profile_rtt_result.append(end - start)
            return ret
        else:
            return f(self, *args, **kwargs)

    return wrapper


class RPCClient(object):
    """Client for making RPC calls to connected servers.

    :param protocol: An :py:class:`~tinyrpc.RPCProtocol` instance.
    :param transport: A :py:class:`~tinyrpc.transports.ClientTransport`
                      instance.
    """

    def __init__(self, protocol, transport, publisher):
        self.protocol = protocol
        self.transport = transport
        self.publisher = publisher
        self.proxy = {}
        self.profile_rtt = PROFILE_RTT
        self.profile = PROFILE_CLIENT
        self.profile_rtt_result = []
        self.profile_result = {}
        self.profiler = cProfile.Profile()
        self.profiler.disable()

        logging.info('Client started')

    def stop(self):
        '''
        stop and will not start again.
        shutdown transport.
        '''
        self.transport.shutdown()

    def send_and_handle_reply_blocking(self, req):
        uid = req.unique_id
        if self.transport.channel == 'dbg':
            # not timeout for debug
            timeout = sys.maxint
        else:
            # use specified timeout; if not specified, use default transport timeout (3s)
            if 'timeout_ms' not in req.kwargs:
                timeout = self.transport.default_timeout_ms / 1000.0
            else:
                timeout = req.kwargs['timeout_ms'] / 1000.0
                req.kwargs.pop('timeout_ms')

        s_req = req.serialize()
        if self.profile_rtt and uid in self.profile_result:
            self.profile_result[uid]['serialize'] = time.time()
        self.transport.send_message(s_req)

        # block wait for response; drop previous timed-out response.
        # handle timeout when there are unmatching respose comes from a previous client-timeout.
        # rpc like sleep(5) will trigger client timeout;
        # server does not get timeout restriction so it will send response,
        # and client will get it in following rpc's recv.
        wait_total_ms = timeout * 1000 + DEFAULT_MSG_TRANSMIT_TIME_MS
        start = time.time()
        while (time.time() - start) * 1000 < wait_total_ms:
            wait = wait_total_ms - (time.time() - start) * 1000
            reply = self.transport.receive_reply(wait)
            if self.profile_rtt and uid in self.profile_result:
                self.profile_result[uid]['reply_got'] = time.time()
            if reply is None:
                msg_timeout = 'Timeout waiting for response from server'
                response = self.protocol.error_respond(JSONRPCTimeoutError(msg_timeout), req)
                return response
            response = self.protocol.parse_reply(reply)
            if self.profile_rtt and uid in self.profile_result:
                self.profile_result[uid]['parse_reply'] = time.time()
            resp_uid = response.unique_id
            if resp_uid != uid:
                # TODO: add logging for client.
                print '[RPCInfo] got previous timed-out response: {}; dropped.'.format(response.__dict__)
            else:
                # expected response
                break
        return response

    @rpc_profile
    @rpc_profile_rtt
    def call(self, method, *args, **kwargs):
        """Calls the requested method and returns the result.

        If an error occured, an :py:class:`~tinyrpc.exc.RPCError` instance
        is raised.

        :param method: Name of the method to call.
        :param args: Arguments to pass to the method.
        :param kwargs: Keyword arguments to pass to the method.
        """
        if self.profile_rtt:
            start = time.time()
        req = self.protocol.create_request(method, *args, **kwargs)
        if self.profile_rtt:
            create_request = time.time()
            # start, create_request, serialize, get_reply, parse_reply
            self.profile_result[req.unique_id] = {}
            self.profile_result[req.unique_id]['start'] = start
            self.profile_result[req.unique_id]['create_request'] = create_request

        response = self.send_and_handle_reply_blocking(req)

        if hasattr(response, 'error'):
            raise RPCError(response.error)

        # get response from server
        ret = response.result
        if self.profile_rtt and req.unique_id in self.profile_result:
            self.profile_result[req.unique_id]['return'] = time.time()
        return ret

    def get_proxy(self, prefix=''):
        """Convenience method for creating a proxy.

        :param prefix: Passed on to :py:class:`~tinyrpc.client.RPCProxy`.
        :return: :py:class:`~tinyrpc.client.RPCProxy` instance."""
        if prefix not in self.proxy:
            if prefix:
                prefix += NAME_METHOD_SEPARATOR
            self.proxy[prefix] = RPCProxy(self, prefix)
        return self.proxy[prefix]

    def send_file(self, src_file, dst_folder, timeout_ms=60 * 1000.0):
        '''
        this function will read file content from src_file, encode it with base64encode,
        and send to server using xavier.send_file api.

        server is supposed to decode the received data,
        and write to dst_folder/dst_fn after validating the dst folder and fn (supported in server 1.0.6).

        :param dst_folder: should be valid folder in xavier file system;
            server has an allowed list of dst folder; this folder should be in the list or be rejected.

        :param timeout_ms: transfer timeout in milliseconds; int or float.

        :return: string 'PASS' or error string/exception.
        '''
        if not src_file:
            raise Exception('Source file {} invalid'.format(src_file))
        if not os.path.isfile(src_file):
            raise Exception('Source file {} is not accessible as a file'.format(src_file))

        print 'Transfer file {} to xavier with {:02f}s timeout'.format(src_file, timeout_ms / 1000.0)
        dst_fn = os.path.basename(src_file)

        with open(src_file, 'rb') as f:
            data = f.read()

        data = base64.b64encode(data)

        return self.get_proxy('xavier').send_file(dst_fn, data, dst_folder, timeout_ms=timeout_ms)

    def get_file(self, target, timeout_ms=60 * 1000.0):
        '''
        get_file content from server and return to caller.
        Perform base64 decoding for data retrieve since it has been encoded at server.

        :param target: string, path to file/folder on xavier to get.
        :param timeout_ms: int or float, network transfer timeout in milliseconds, by default 60*1000ms
        :return: tuple as below:
                ('PASS', data) when succeed; 'PASS' is string; data is string.
                (err_msg, '') when fail; errmsg is string; '' is empty string.
        '''
        print 'Getting file/folder {} from xavier with {:02f}s timeout'.format(target, timeout_ms / 1000.0)

        ret, data = self.get_proxy('xavier').get_file(target, timeout_ms=timeout_ms)
        return ret, base64.b64decode(data)

    def get_log(self, timeout_ms=60 * 1000.0):
        '''
        get log files in a tarball for current rpc server;
        Perform base64 decoding for data retrieve since it has been encoded at server.

        :param target: string, path to file/folder on xavier to get.
        :param timeout_ms: int or float, network transfer timeout in milliseconds, by default 60*1000ms
        :return: tuple as below:
                ('PASS', data) when succeed; 'PASS' is string; data is string.
                (err_msg, '') when fail; errmsg is string; '' is empty string.
        '''
        print 'Getting log files for current rpc server with {:02f}s timeout'.format(timeout_ms / 1000.0)

        ret, data = self.get_proxy('server').get_log(timeout_ms=timeout_ms)
        return ret, base64.b64decode(data)

    def get_and_write_log(self, filename='rpc_server_log.tgz', timeout_ms=60 * 1000.0):
        '''
        get all log files through RPC, and store in rpc_log.tgz.
        Perform base64 decoding for data retrieve since it has been encoded at server.

        :param filename: string, filename to be written to
        :param timeout_ms: int or float, network transfer timeout in milliseconds, by default 60*1000ms
        :return: string: 'PASS' when succeed; err_msg when fail.
        '''
        print 'Get and write log files for current rpc server with {:02f}s timeout'.format(timeout_ms / 1000.0)

        ret, data = self.get_log(timeout_ms=timeout_ms)
        if ret != 'PASS':
            return ret

        with open(filename, 'wb') as f:
            f.write(data)

        return 'PASS'

    def get_and_write_all_log(self, filename='rpc_server_log.tgz', timeout_ms=60 * 1000.0):
        '''
        get all log files through RPC, and store in given file name.
        Perform base64 decoding for data retrieve since it has been encoded at server.

        :param filename: string, filename to be written to
        :param timeout_ms: int or float, network transfer timeout in milliseconds, by default 60*1000ms
        :return: string: 'PASS' when succeed; err_msg when fail.
        '''
        print 'Getting log files for all DUTs with {:02f}s timeout'.format(timeout_ms / 1000.0)

        ret, data = self.get_proxy('xavier').get_all_log(timeout_ms=timeout_ms)
        if ret != 'PASS':
            return ret

        with open(filename, 'wb') as f:
            f.write(base64.b64decode(data))
        return 'PASS'

    def get_and_write_file(self, target, dst_file, timeout_ms=60 * 1000.0):
        '''
        get file content from server and write to dst_file.

        :param target: string, path to file/folder on xavier to get.
        :param dst_file: string, file path to write to after getting from server.
        :param timeout_ms: int or float, network transfer timeout in milliseconds, by default 60*1000ms
        :return: string 'PASS' when successfully get and write;
                 string error message when failure found, like get_file fail or write fail.
        '''
        ret, data = self.get_file(target, timeout_ms)
        if ret != 'PASS':
            return ret

        with open(dst_file, 'wb') as f:
            f.write(data)

        return 'PASS'

    def get_linux_boot_log(self, dst_file):
        '''
        get linux boot log from server and write to dst_file
        :param dst_file: string, file path to write to after getting
            from server. file type should be .tar.gz or .tgz
        return: string 'PASS' when successfully get and write;
                string error message weh failure found, like get_file fail or write fail
        '''
        dst_folder = os.path.dirname(dst_file)
        if not os.path.exists(dst_folder):
            os.mkdir(dst_folder)
        ret, data = self.get_proxy('xavier').get_linux_boot_log()
        if ret != 'PASS':
            return ret

        with open(dst_file, 'wb') as f:
            f.write(base64.b64decode(data))

        return 'PASS'

    def set_profile(self, breakdown=False, rtt=True):
        '''
        Change profile setting;
        breakdown: whether to profile each func call using cProfile
        rtt: whether record start and end of server handling time.
        :param breakdown: bool, True to use cProfile to get function cost breakdown
        :param rtt: bool, whether to measure end to end time of each phase
        '''
        self.profile = breakdown
        self.profile_rtt = rtt
        if breakdown:
            self.profiler.enable()
        else:
            self.profiler.disable()
        return 'done'

    def clear_profile_stats(self):
        '''
        clear profile result.
        '''
        self.profile_result = {}
        self.profile_rtt_result = []
        self.profiler = cProfile.Profile()
        self.profiler.disable()
        return 'done'

    def generate_profile_result(self):
        '''
        Generate a dict of profile result including RTT and each phase data

        input: self.profile_result
        ::

              format: {
                           'uid1': {'start': time1, 'create_request', time2, ...},
                           'uid2': {'start': time1, 'create_request', time2, ...},
                       }

        process: get list of sorted key by sorting the time to determine sequence, like
                 ::

                     [start, create_request, serialize, transport, parse_reply]

                 Then calculate each stage time by minus action:
                 ::

                    t_create_request = result['create_request'] - result['start']
                    t_serialize = result['serialize'] - result['create_request']

        :return: dict as follow so user could calculate avg/rms/other statistics.

        ::

                {
                    'keys': [start, SORTED_POINT, ...],
                    'POINT1': [DATA1, DATA2, ...],
                    'POINT2': [DATA1, DATA2, ...],
                }

        '''
        # filter valid profile results; skip those incomplete ones from profile_enable.
        full_key = []
        for v in self.profile_result.values():
            if len(full_key) < len(v):
                full_key = v.keys()
        valid_profile_result = [v for v in self.profile_result.values() if v.keys() == full_key]
        ret = {}
        first_data = valid_profile_result[0]
        # sorted key by value so key is in time sequence
        key_list = sorted(first_data.keys(), key=lambda k: first_data[k])
        # 1st is start time, no need to report.
        ret['keys'] = key_list[1:]
        for key in ret['keys']:
            ret[key] = []
        for data in valid_profile_result:
            for i, key in enumerate(key_list):
                # 'start'
                if i == 0:
                    continue
                # us as unit.
                ret[key].append((data[key_list[i]] - data[key_list[i - 1]]) * 1000 * 1000)
        return ret


class RPCProxy(object):
    """Create a new remote proxy object.

    Proxies allow calling of methods through a simpler interface. See the
    documentation for an example.

    :param client: An :py:class:`~tinyrpc.client.RPCClient` instance.
    :param prefix: Prefix to prepend to every method name.
                    :py:func:`~tinyrpc.client.call`.
    """

    def __init__(self, client, prefix=''):
        self.client = client
        self.prefix = prefix

    def __getattr__(self, name):
        """Returns a proxy function that, when called, will call a function
        name ``name`` on the client associated with the proxy.
        """
        proxy_func = lambda *args, **kwargs: self.client.call(
                        self.prefix + name,
                        *args,
                        **kwargs)
        return proxy_func
