import os
import re
import zmq
import time
import uuid
import pstats
import ujson as json
import base64
import logging
import logging.handlers
import platform
import tarfile
import cProfile
import traceback
from logger import RPCLogger
from publisher import NoOpPublisher
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.zmq import ZmqServerTransport
from tinyrpc.server import RPCServer
from tinyrpc.dispatch import RPCDispatcher
from tinyrpc.config import ALLOWED_FOLDER_SEND_FILE
from tinyrpc.config import ALLOWED_FOLDER_GET_FILE
from tinyrpc.config import MIX_FW_VERSION_FILE
from tinyrpc.config import THREAD_POOL_WORKERS
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, FATAL


class RPCServerWrapper(object):
    '''
    RPC Server Wrapper to create a server in 1 line of code with given transport/endpoint and publisher.

    :param transport: 2 kind of input supported:
        1. dict describing server endpoint

        .. code-block:: python

            {'receiver':'tcp://127.0.0.1:5556', 'replier':'127.0.0.1:15556'}

        for backword compatibility, a single string is also accepted as receiver endpoint:

        .. code-block:: python

            'tcp://127.0.0.1:5556'

        In this case, replier endpoint will using same IP and given port + 10000; it is equal to the dictionary above.

        Supported endpoint format:

        .. code-block:: python

            'tcp://127.0.0.1:5556'
            '127.0.0.1:5556'
            '*:5556'

        Not supported:

        .. code-block:: python

            '5556'

        2. RPCTransport instance.

    :param ctx: ZMQ Context; used when multiple RPC server share same ZMQ Context.
    :param protocol: not used.
    :param dispatcher: not used.
    :param log_level: log level for log file; log below this will not be saved to log file.
    :param log_folder_path: log folder for rpc log.
                            If None, use log/ which is same level of logger/
    :param name: rpc server name; used in log file name.
                 If None, it will be 'ip_port' from rpc server IP and receiver port.

    :server services: Defined as selected functions in class "rpc_public_api" variable;
                       All functions in the list will be exposed as RPC service.
                       But only the selected will run in main dispatching thread
                       instead of run in threadpool.
                       This means they will run a little bit faster (threadpool cost 550us more),
                       and is able to run even when threadpool is full.
                       Guidelines to make RPC service a 'server service':

                           1. function that works at end of current server life cycle
                                reboot/reset
                           2. time-sensitive RPC service
                                'mode' that will be used before every RPC by PhoneQT.

                       Server services are in whitelist defined in config.py.
    '''
    rpc_public_api = ['reset', 'stop', 'all_methods', 'mode',
                      'get_log', 'reset_log', 'set_logging_level',
                      'profile_enable', 'clear_profile_stats', 'get_profile_stats']

    def __init__(self, transport, publisher=None, ctx=None, protocol=None,
                 dispatcher=None, log_level=INFO, log_folder_path=None, name=None, threadpool_size=None):

        self.ctx = ctx if ctx else zmq.Context().instance()
        self.protocol = protocol if protocol else JSONRPCProtocol()
        self.dispatcher = dispatcher if dispatcher else RPCDispatcher()
        self.publisher = publisher if publisher else NoOpPublisher()
        threadpool_size = threadpool_size or THREAD_POOL_WORKERS
        if isinstance(transport, dict):
            # dictionary:
            if 'receiver'in transport and 'replier' in transport:
                self.endpoints = transport
            else:
                msg = 'endpoint dictionary {} should contains receiver and replier'
                raise Exception(msg.format(transport))
            self.endpoint = self.endpoints['receiver']
        elif isinstance(transport, basestring):
            # only 1 endpoint is provided; create endpoint for replier by adding port by 10000
            pattern = '(tcp://)?((?P<ip>[0-9.*]+):)?(?P<port>[0-9]+)'
            re_groups = re.match(pattern, transport.strip())
            if not re_groups:
                raise Exception('Invalid transport format {}; '
                                'expecting tcp://IP:PORT or IP:PORT'.format(transport))
            replier_port = int(re_groups.group('port')) + 10000
            ip = re_groups.group('ip') if re_groups.group('ip') else '*'
            receiver_endpoint = 'tcp://{}:{}'.format(ip, replier_port)
            replier_endpoint = 'tcp://{}:{}'.format(ip, replier_port)
            self.endpoints = {'receiver': transport,
                              'replier': replier_endpoint}
            self.endpoint = self.endpoints['receiver']

        else:
            # existing transport instance
            self.endpoints = transport
            self.endpoint = transport.endpoint['receiver']

        if name:
            # name should be string.
            err_msg = 'RPC server name ({}) shall be string.'.format(name)
            assert isinstance(name, basestring), err_msg
            err_msg = 'RPC server name ({}) shall not contain .'.format(name)
            assert '.' not in name, err_msg
            err_msg = 'RPC server name ({}) shall not contain {}'.format(name, os.sep)
            assert os.sep not in name, err_msg
            logger_name = name
        else:
            # use port as name.
            pattern = 'tcp://(?P<ip>[0-9.*]+):(?P<port>[0-9]+)'
            re_groups = re.match(pattern, self.endpoint)
            logger_name = re_groups.group('port')
        self.logger = RPCLogger(name=logger_name, level=log_level, log_folder_path=log_folder_path)
        # logger for registered instance, like drivers and test functions
        self.service_logger = RPCLogger(logger_name + '_service', level=log_level, log_folder_path=log_folder_path)

        self.init_server(self.endpoints, threadpool_size)
        self.server_mode = 'normal'

    def init_server(self, transport, threadpool_size):
        '''
        Internal function that should not be called explicitly.
        :param transport: dict like {'receiver': transport, 'receiver': replier_endpoint}
        :param logger: RPCLogger instance
        '''
        if isinstance(transport, ZmqServerTransport):
            self.transport = transport
        else:
            # dict like {'receiver': transport, 'receiver': replier_endpoint}
            for key in transport:
                if 'tcp' not in str(transport[key]):
                    transport[key] = "tcp://" + str(transport[key])
            self.transport = ZmqServerTransport.create(self.ctx, transport)

        self.transport.publisher = self.publisher

        self.rpc_server = RPCServer(self.transport, self.protocol,
                                    self.dispatcher, threadpool_size)
        self.rpc_server.set_logger(self.logger)
        self.register_instance({'server': self})
        self.rpc_server.dispatcher.logger = self.service_logger
        self.rpc_server.start()
        self.logger.info('rpc server {} started.'.format(self.endpoint))

    def register_instance(self, obj={}):
        '''
        Register instance as RPC service provided to the RPC server.

        :param obj: a dictionary with the following format:

            value: instance that provide functions as RPC service

            key: a string as the prefix of all RPC services belongs to the instance in value.

        Example code for client to send "driver1_measure()" RPC to call driver1.measure()
        and driver2_measure() to call driver2.measure() on server:

        .. code-block:: python

            # Driver() class has a public function measure()
            driver1 = Driver()
            driver2 = Driver()
            server.register_instance({'driver1': driver1, 'driver2': driver2})

        '''
        self.rpc_server.dispatcher.register_instance(obj)

    def reset(self):
        self.rpc_server.shutdown()
        self.init_server(self.endpoints)
        return True

    def stop(self):
        self.rpc_server.shutdown()
        return True

    def all_methods(self):
        '''
        Wrapper for dispatcher.all_methods()
        '''
        return self.rpc_server.dispatcher.all_methods()

    def mode(self):
        '''
        Client will use this as
        1. server accessibility, like network disconnection
        2. server mode check; only continue testing in 'normal' mode;
        Server will put mode into 'dfu' during fwup in the future.
        '''
        return self.server_mode

    def reset_log(self):
        self.logger.reset()
        self.service_logger.reset()
        return '--PASS--'

    def get_log(self):
        '''
        get current rpc server log files in 1 tarball.

        Args:
            None

        Return:
            2-item tuple ('PASS', data) or (errmsg, '')
            errmsg should be a string about failure reason.
            data is encoded in base64; client will be responsible
            for decoding it into origin data.
        '''
        # handle trailing '/'
        # get all log files of current rpc server.
        # put them into a temp folder inside of log
        # pack into tgz and return back to client.
        log_folder = self.logger.log_folder
        # create a tmp folder for tgz
        print 'log_folder:', log_folder
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

        # restart server logger after removing log files.
        # without this there will be no log in log file after previous log file being removed.
        self.reset_log()

        # handle "~" in path
        tmp_folder = os.path.expanduser(tmp_folder)

        working_dir = os.path.dirname(tmp_folder)
        tmp_folder_name = os.path.basename(tmp_folder)

        # zip folder into tgz file: ~/aaa --> ~/aaa.tgz, /opt/seeing/log --> ~/log.tgz
        os.chdir(working_dir)
        tgz_fn = os.path.join('/tmp', '{}_{}.tgz'.format(tmp_folder_name, uuid.uuid4().hex))
        with tarfile.open(tgz_fn, 'w') as tgz:
            tgz.add(tmp_folder_name)

        with open(tgz_fn, 'rb') as f:
            data = f.read()

        # cleanup: remove tmp tgz file.
        os.remove(tgz_fn)

        # cleanup: remove tmp_folder for creating tgz.
        for f in os.listdir(tmp_folder):
            os.remove(os.path.join(tmp_folder, f))
        os.rmdir(tmp_folder)

        return 'PASS', base64.b64encode(data)

    def set_logging_level(self, level):
        '''
        Setting RPC server logging level;

        :param level: string in given list, string of level
                      case insensitive; must be one of
                      "NOTSET", "INFO", "DEBUG", "WARNING", "ERROR", "FATAL"
        '''
        level = level.lower()
        levels = {
            'notset': NOTSET,
            'debug': DEBUG,
            'info': INFO,
            'warning': WARNING,
            'error': ERROR,
            'fatal': FATAL}
        if level not in levels:
            msg = 'Unexpected level {}; should be in {}'.format(level, levels.keys())
            raise Exception(msg)

        # logging.seLevel accepts ints, not string.
        self.logger.setLevel(levels[level])
        self.service_logger.setLevel(levels[level])
        return 'done'

    def profile_enable(self, breakdown=True, rtt=True):
        '''
        Enable/disable server profiling;
        Both for total handle time and function breakdown

        :param breakdown: bool, default True; controls whether to profile server handle function
                          and generate breakdown data for each function call
        :param rtt: bool, default True; controls whether to calculate total server handle time;
        :example:
                 client.server_profile_enable()             # server profile will be enabled
                 client.server_profile_enable(False, False) # server profile will be disabled
        :return: 'done' for successfully setting. Do not explicitly return other value.
        '''
        self.rpc_server.set_profile(breakdown, rtt)
        return 'done'

    def clear_profile_stats(self):
        self.rpc_server.clear_profile_result()
        return 'done'

    def get_profile_stats(self):
        '''
        return profile statistics to client.

        :return: Tuple, (breakdown, profile_result)
            breakdown: dict; server main thread's cProfile stats; {} if not enabled.
            profile_result: dict; end-to-end time of each phase data
            format of breakdown dict:

                key: function name including file path, like /root/zmq.py:send
                value: dict{

                    'ncall': int, number of function call profiled,

                    'tot_avg': average time of the function, not including sub-func call

                    'cum_avg': average time of the function, including sub-func call

                    }

            format of profile_result: dict{

                'keys': list, keys in time sequence, like [start, step1, step2, step3]

                'start': [t_rpc1, t_rpc2, ...]      # t_rpc is float() from time.time()

                'step1': [t_rpc1, t_rpc2, ...]
                ...

                }

                User software could use this dict to do further calculation,
                like avg, rms, etc.
        '''
        stats_server = []
        breakdown = {}
        if self.rpc_server.profiler:
            try:
                stats_server = pstats.Stats(self.rpc_server.profiler).stats
                # profile breakdown
                breakdown = {
                    pstats.func_std_string(k): {
                        'ncall': v[1],
                        'tot_avg': float(v[2]) / v[1],
                        'cum_avg': float(v[3]) / v[0]}
                    for k, v in stats_server.items()}
            except:
                self.logger.info(traceback.format_exc())
                stats_server = []
                breakdown = {}

        profile_result = self.rpc_server.generate_profile_result()
        # overall server handling time
        return breakdown, profile_result

    def get_event(self):
        '''
        API for user software to get system event, like light curtain event and system hot.

        :return: a list of error code in string like this:

                    ret = client.server_get_event()

                    # ret == ['[Server 7801] Light curtain triggered', '[Server 7802] PROCHOT']

                 Empty list [] will returned if no event available.

        :notes:
            Event is global variable shared by all RPC server;
                Any server will return all events of all server.
            Event from each server will have identity in header like '[Server 7802]';
                This means this event is generated by Server with port 7802; normally DUT2.

            Events are cleared after got by client.
        '''
        pass


if __name__ == '__main__':
    from publisher import ZmqPublisher
    server = RPCServerWrapper("tcp://127.0.0.1:7777", ZmqPublisher(zmq.Context(), "tcp://127.0.0.1:6665", '101'))
    from drivers.driver import *
    service = driver()
    server.register_instance(service)
    raw_input()
