import time
import os
import base64
import pstats
from rpc_client import RPCClientWrapper
from rpc_server import RPCServerWrapper
from publisher import *
from threading import Thread
import logging
RUNNING = 'running'
DONE = 'done'


def f8(x):
    return "%.3fus" % (x * 1000000)

pstats.f8 = f8


class UART(object):
    rpc_public_api = ['open', 'close', 'config', 'read_hex', 'write_hex']

    def __init__(self):
        pass

    def open(self, *arg, **kwargs):
        return 'done'

    def close(self, *arg, **kwargs):
        return 'done'

    def config(self, *arg, **kwargs):
        return 'done'

    def read_hex(self, *arg, **kwargs):
        print 'reading hex'
        return [30, 31, 32, 33]

    def write_hex(self, *arg, **kwargs):
        return 'done'


# test driver class; only for demo & testing
class driver(object):
    rpc_public_api = ['echo', 'float10', 'float11', 'int1', 'strshark',
                      'list_0_1_a_float15_false', 'dict_a_0',
                      'fun', 'fun_kwargs']

    def __init__(self):
        self.bus = bus()
        self.axi = axi()

    def echo(self, a):
        if len(a) > 128:
            msg = a[:125] + '...'
        else:
            msg = a
        print('Echoing {} back to client.'.format(msg))
        return a

    def float10(self, a):
        print('Checking if input is float 1.0', a)
        if a != 1.0:
            return 'input {} is not 1.0 as expected'.format(a)
        return a

    def float11(self, a):
        print('Checking if input is float 1.1', a)
        if a != 1.1:
            return 'input {} is not 1.1 as expected'.format(a)
        return a

    def int1(self, a):
        # print('Checking if input is int 1', a)
        # if a != 1:
        #     return 'input {} is not 1 as expected'.format(a)
        return a

    def strshark(self, a):
        print('Checking if input is string "shark"', a)
        if a != 'shark':
            return 'input {} is not "shark" as expected'.format(a)
        return a

    def list_0_1_a_float15_false(self, a):
        print('Checking if input is list [0, 1, "a", 1.5, False]')
        expected = [0, 1, 'a', 1.5, False]
        if a != expected:
            return 'input {} is not [0, 1, "a", 1.5, False] as expected'.format(a)
        return a

    def dict_a_0(self, a):
        print('Checking if input is dictionary {"a": 0}')
        expected = {"a": 0}
        if a != {"a": 0}:
            return 'input {} is not {"a": 0} as expected'.format(a)
        return a

    def fun(self, a=None, b=None):
        if not a and not b:
            ret = 'calling driver.fun()'
        elif a and b:
            ret = 'calling driver.fun({}, {})'.format(a, b)
        return ret

    def fun_kwargs(self, a, b):
        ret = 'calling driver.fun_kwargs(a={}, b={})'.format(a, b)
        return ret

    def driver_private_fun(self):
        ret = 'driver private fun'
        return ret


class bus(object):
    rpc_public_api = ['fun']

    def __init__(self):
        self.axi = axi()

    def fun(self):
        ret = 'calling driver.bus.fun()'
        return ret

    def bus_private_fun(self):
        ret = 'bus private fun'
        return ret


class axi(object):
    rpc_public_api = ['fun']

    def __init__(self):
        pass

    def fun(self):
        ret = 'calling axi.fun()'
        return ret

    def axi_private_fun(self):
        ret = 'axi private fun'
        return ret


class utility(object):
    rpc_public_api = ['measure', 'dummy', 'dummy_fail', 'dummy_other', 'invalid',
                      'exception', 'sleep', 'sleep_timeout']

    def __init__(self, name='utility'):
        self.name = name

    def measure(self, value):
        return value

    def dummy(self, a=1, b=2):
        print 'dummy: {}, {} '.format(a, b)
        return '--PASS--'

    def dummy_fail(self, a=1, b=2):
        print 'dummy: {}, {} '.format(a, b)
        return '--FAIL--'

    def dummy_other(self, a=1, b=2):
        print 'dummy: {}, {} '.format(a, b)
        return 'Shark does not bite.'

    def invalid(self):
        ret = '\xff0\r\n'
        print 'returning {}'.format(ret)
        return ret

    def exception(self, msg='Hello'):
        msg = 'Raising Exception: {}'.format(msg)
        raise Exception(msg)

    def sleep(self, second):
        now = time.time()
        self.logger.info('[{}] worker: start to sleep for {} second'.format(time.time(), second))
        time.sleep(second)
        self.logger.info('[{}] worker: end sleep for {} second'.format(time.time(), second))
        return 'server time cost for {} second sleep: {}'.format(second, time.time() - now)

    def sleep_timeout(self, second):
        '''
        sleep 1s more than given second to generate a server side timeout.
        '''
        now = time.time()
        logging.info('[{}] worker: start to sleep for {}+1 second'.format(time.time(), second))

        time.sleep(second + 1)
        logging.info('[{}] worker: end sleep for {}+1 second'.format(time.time(), second))
        return 'server time cost for {}+1 second sleep: {}'.format(second, time.time() - now)


class MockedXavier(object):
    rpc_public_api = ['get_linux_boot_log', 'get_file', 'send_file', 'get_all_log']

    def __init__(self, name='xavier'):
        self.name = name

    def get_linux_boot_log(self):
        return 'PASS', base64.b64encode('This is linux boot log for test')

    def send_file(self, fn, data, folder):
        '''
        mock for send_file: write file to given path with given data.
        '''
        folder = os.path.expanduser(folder)
        with open(os.path.join(folder, fn), 'wb') as f:
            data = base64.b64decode(data)
            f.write(data)

        return 'PASS'

    def get_file(self, target, base64_encoding=True):
        '''
        mock for get_file: get file from given path
        '''
        with open(target, 'rb') as f:
            data = f.read()
        return 'PASS', base64.b64encode(data)

    def get_all_log(self, base64_encoding=True):
        return 'PASS', base64.b64encode('simulating all server log.')


if __name__ == '__main__':
    import sys
    args = sys.argv[1:]
    argc = len(args)
    if argc == 0:
        n_server = 1
    elif argc == 1:
        n_server = int(args[0])
    else:
        raise Exception('Usage: python start_python_rpc_server.py [N_SERVER]')
    endpoints = []
    for port in range(5556, 5556 + n_server):
        endpoint = 'tcp://*:{}'.format(port)
        endpoints.append(endpoint)

    # driver instances
    util = utility()
    driver = driver()
    uart = UART()

    servers = []
    for endpoint in endpoints:
        print 'starting server {}'.format(endpoint)
        server = RPCServerWrapper(endpoint)
        server.register_instance(util)
        server.register_instance({'util': util})
        server.register_instance({'driver': driver})
        server.register_instance({'xavier': MockedXavier()})
        servers.append(server)

    # initial work that will take 150ms; put it here to avoid adding 150ms to the 1st rpc call.
    from uuid import uuid1
    uuid1().hex

    # for socket connect
    time.sleep(0.5)

    while True:
        time.sleep(1)


