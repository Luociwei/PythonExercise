import time
import cProfile
from rpc_client import RPCClientWrapper
from rpc_server import RPCServerWrapper
from publisher import *
from threading import Thread
import ujson as json
import pstats
RUNNING = 'running'
DONE = 'done'


# test driver class; only for demo & testing
class driver(object):
    rpc_public_api = ['fun', 'fun_kwargs']

    def __init__(self):
        self.bus = bus()
        self.axi = axi()

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
    rpc_public_api = ['measure', 'sleep']

    def __init__(self, name='utility'):
        self.name = name

    def measure(self, value):
        return value

    def sleep(self, second, timeout_ms=None):
        now = time.time()
        msg = '[{}] worker: start to sleep for {} second'.format(time.time(), second)
        print msg

        time.sleep(float(second))
        print '[{}] worker: end sleep for {} second'.format(time.time(), second)
        return 'server time cost for {} second sleep: {}'.format(second, time.time() - now)


def set_rpc_default_timeout(client, timeout_ms):
    client.rpc_client.transport.default_timeout_ms = timeout_ms


def get_rpc_default_timeout(client):
    return client.rpc_client.transport.default_timeout_ms


def sample_sync_rpc(client):
    print '-' * 80
    print 'sample1: synchronous call to sleep 1s'
    set_rpc_default_timeout(client, 10000)
    now = time.time()
    ret = client.sleep(1, timeout_ms=1500)
    print 'ret of sleep1: ', ret
    time_cost = time.time() - now
    print 'time cost: {}'.format(time_cost)
    assert 1 < time_cost < 1.08


def sample_rpc_service_discovery(client):
    client_driver = client.get_proxy('driver')
    client_util = client.get_proxy('util')
    print '-' * 80
    print 'sample0: rpc service discovery'
    ret = client.driver_fun()
    print 'ret of client.driver_fun(): ', ret
    assert ret == 'calling driver.fun()'

    ret = client_driver.fun()
    print 'ret of client_driver.fun(): ', ret
    assert ret == 'calling driver.fun()'

    # args
    ret = client_driver.fun(1, 2)
    print 'ret of client_driver.fun(1, 2): ', ret
    assert ret == 'calling driver.fun(1, 2)'

    # kwargs
    ret = client_driver.fun_kwargs(a=1, b=2)
    print 'ret of client_driver.fun_kwargs(a=1, b=2): ', ret
    assert ret == 'calling driver.fun_kwargs(a=1, b=2)'

    # kwargs + specified timeout
    ret = client_driver.fun_kwargs(a=1, b=2, timeout_ms=10000)
    print 'ret of client_driver.fun_kwargs(a=1, b=2): ', ret
    assert ret == 'calling driver.fun_kwargs(a=1, b=2)'

    ret = client_util.sleep(0.1)
    print 'ret of client_util.sleep(0.1): ', ret
    assert ret.startswith('server time cost for 0.1 second sleep: ')

def sample_client_timeout(client):
    print '-' * 80
    print 'sample6: synchronous rpc timeout at client side'
    t = get_rpc_default_timeout(client)
    set_rpc_default_timeout(client, 1000)

    now = time.time()
    try:
        ret = client.sleep(5)
        raise Exception('Client timeout not triggered correctly')
    except Exception as e:
        assert e.message == '[RPCError] Timeout waiting for response from server'

    time_cost = time.time() - now
    print 'total time cost: {}'.format(time_cost)
    assert 1 < time_cost < 1.08

    # timeout handle
    set_rpc_default_timeout(client, 200)
    for i in range(10):
        try:
            ret = client.sleep(0.35)
            raise Exception('Client timeout not triggered correctly')
        except Exception as e:
            assert e.message == '[RPCError] Timeout waiting for response from server'

    # restore default timeout
    set_rpc_default_timeout(client, t)

def sample_check_server_accessibility(client_yes):
    print '-' * 80
    print 'scenario 13: check if server is accessible by calling server_rpc_version rpc service'
    endpoint_no = {'requester': 'tcp://127.0.1.1:5556', 'receiver': 'tcp://127.0.1.1:15556'}
    client_no = RPCClientWrapper(endpoint_no)

    try:
        ret = client_no.server_mode()
    except Exception, e:
        assert '[RPCError] Timeout waiting for response from server' in e.message

def sample_multiple_client_thread(endpoint):
    print '-' * 80
    print 'scenario 14: creating multiple RPC client in threads'
    no_publisher = NoOpPublisher()
    clients = []
    uuids = []

    # sync RPC
    for i in range(10):
        client = RPCClientWrapper(endpoint, no_publisher)
        clients.append(client)

    now = time.time()
    for i in range(10):
        ret = client.sleep(1)
        assert(ret.startswith('server time cost for 1 second sleep: 1'))

    print 'sync timecost: ', time.time() - now
    for client in clients:
        client.rpc_client.stop()


if __name__ == '__main__':
    endpoint_server = {'receiver': 'tcp://127.0.0.1:5556', 'replier': 'tcp://127.0.0.1:15556'}
    endpoint_client = {'requester': 'tcp://127.0.0.1:5556', 'receiver': 'tcp://127.0.0.1:15556'}
    client = RPCClientWrapper(endpoint_client)

    # 2 driver instances
    util = utility()
    driver = driver()

    server = RPCServerWrapper(endpoint_server)
    server.register_instance(util)
    server.register_instance({'driver': driver, 'util': util})

    # initial work that will take 150ms; put it here to avoid adding 150ms to the 1st rpc call.
    from uuid import uuid4
    uuid4().hex

    # for socket connect
    time.sleep(0.5)

    sample_rpc_service_discovery(client)
    sample_sync_rpc(client)
    sample_client_timeout(client)
    sample_check_server_accessibility(client)
    sample_multiple_client_thread(endpoint_client)
