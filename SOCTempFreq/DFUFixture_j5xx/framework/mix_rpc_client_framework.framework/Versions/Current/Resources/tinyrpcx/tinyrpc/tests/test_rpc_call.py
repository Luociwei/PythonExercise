import time
import pytest
import ujson as json
import ctypes
import re
import os
import uuid
import zmq
import logging
from threading import Thread
from threading import Event
from publisher import *
from tinyrpc.config import THREAD_POOL_WORKERS
from tinyrpc.exc import RPCError
from tinyrpc.dispatch import public
from rpc_client import RPCClientWrapper
from rpc_server import RPCServerWrapper
from DummyRPCService import DummyRPCService
from DummyRPCService import driver
from xavier import Xavier
from tinyrpc import RUNNING, DONE, TIMEOUT, ERROR
from tinyrpc.protocols.jsonrpc import JSONRPCRequest
from tinyrpc.protocols.jsonrpc import JSONRPCMethodNotFoundError
from mock import patch
from mock import mock_open
from tinyrpc.transports.zmq import ZmqServerTransport
import mock


ENDPOINT_SERVER = {'receiver': 'tcp://127.0.0.1:8889', 'replier': 'tcp://127.0.0.1:18889'}
ENDPOINT_CLIENT = {'requester': 'tcp://127.0.0.1:8889', 'receiver': 'tcp://127.0.0.1:18889'}
ENDPOINT_CLIENT_STR = 'tcp://127.0.0.1:8889'
ENDPOINT_CLIENT_IP = '127.0.0.1'
ENDPOINT_CLIENT_PORT = 8889

ENDPOINT_MGMT_SERVER = {'receiver': 'tcp://127.0.0.1:7800', 'replier': 'tcp://127.0.0.1:17800'}
ENDPOINT_MGMT_CLIENT = {'requester': 'tcp://127.0.0.1:7800', 'receiver': 'tcp://127.0.0.1:17800'}

ENDPOINT_NO = {'requester': 'tcp://127.0.1.1:7777', 'receiver': 'tcp://127.0.1.1:17777'}

ENDPOINT_CLIENT_SHUTDOWN = {'requester': 'tcp://127.0.0.1:7778', 'receiver': 'tcp://127.0.0.1:17778'}
ENDPOINT_SERVER_SHUTDOWN = {'receiver': 'tcp://127.0.0.1:7778', 'replier': 'tcp://127.0.0.1:17778'}
msg_list = []
publisher = TestPublisher('TestPublisher', msg_list)


@pytest.fixture
def loop_request():
    request = JSONRPCRequest()
    request.method = 'loop'
    request.args = []
    request.sync = True
    request.kwargs = {'timeout_ms': 3000}
    return request

@pytest.fixture
def sleep_request():
    request = JSONRPCRequest()
    request.method = 'sleep'
    request.args = [3]
    request.sync = True
    request.kwargs = {'timeout_ms': 6000}
    return request

@pytest.fixture(params=[
    ('measure', 1, 1),
    ('dummy.measure', 1, 1),
])
def rpc_to_test(request):
    return request.param

@pytest.fixture(params=[[1], [1.0], ['1.2'], [[1, 1.0, '1.2']], [{'test1': 1, 'test2': 1.0, 'test3': '1.2'}]])
def method_args(request):
    return request.param

@pytest.fixture(params=[{'test1': 1, 'test2': 1.0, 'test3': '1.2'}])
def method_kwargs(request):
    return request.param

@pytest.fixture(params=[-1, 0, 55536, 65536, 70000])
def wrong_port(request):
    return request.param

@pytest.fixture(params=[-1, 0, 65536, 70000])
def wrong_receiver_port(request):
    return request.param

@pytest.fixture(params=[(logging.DEBUG, './'),
                        (logging.INFO, './var/log/rpc_log'),
                        (logging.CRITICAL, '/tmp'),
                        (logging.FATAL, '~'),
                        (logging.WARNING, './var/log/'),
                        (logging.NOTSET, './var/log/rpc_log'),
                        (logging.ERROR, './var/log/rpc_log')])
def logging_params(request):
    return request.param


@pytest.fixture(scope='module')
def log_test_transport(request):
    transport = ZmqServerTransport.create(zmq.Context(), {'replier': 'tcp://127.0.0.1:7890', 'receiver': 'tcp://127.0.0.1:17890'})

    def fin():
        transport.shutdown()
    request.addfinalizer(fin)
    return transport

@pytest.fixture(scope='module')
def rpc_service_single():
    rs = DummyRPCService()
    return rs


@pytest.fixture(scope='module')
def rpc_service_list():
    ss_dict = {'dummy': DummyRPCService(), 'driver': driver()}
    return ss_dict


@pytest.fixture(scope='module')
def rpc_client_wrapper(request):
    wrapper = RPCClientWrapper(ENDPOINT_CLIENT, publisher)

    def fin():
        wrapper.rpc_client.stop()
    time.sleep(0.5)
    request.addfinalizer(fin)
    return wrapper

@pytest.fixture(scope='module')
def mgmt_client(request):
    wrapper = RPCClientWrapper(ENDPOINT_MGMT_CLIENT)

    def fin():
        wrapper.rpc_client.stop()
    time.sleep(0.5)
    request.addfinalizer(fin)
    return wrapper

@pytest.fixture(scope='module')
def mgmt_server(request):
    wrapper = RPCServerWrapper(ENDPOINT_MGMT_SERVER, name='mgmt',
                               log_folder_path='./log')
    wrapper.register_instance({'xavier': Xavier()})

    def fin():
        wrapper.rpc_server.serving = False
        del wrapper.rpc_server
        # time.sleep(2)
    time.sleep(0.5)
    request.addfinalizer(fin)
    return wrapper

@pytest.fixture(scope='module')
def rpc_server_wrapper(rpc_service_single, request, rpc_service_list):
    wrapper = RPCServerWrapper(ENDPOINT_SERVER, publisher,
                               log_folder_path='/tmp/rpc_log')
    wrapper.register_instance(rpc_service_single)
    wrapper.register_instance(rpc_service_list)
    # wrapper.rpc_server.redir.shutdown()

    def fin():
        wrapper.rpc_server.serving = False
        del wrapper.rpc_server
        # time.sleep(2)
    time.sleep(0.5)
    request.addfinalizer(fin)
    return wrapper

@pytest.fixture(scope='function')
def mock_file(tmpdir):
    '''
    Create a temp file for testing send/get file.
    '''
    p = tmpdir.join('dummy_file')
    p.write('aaaa')
    yield p.strpath


def exception_handle(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as e:
        pytest.fail(e.message)

def set_rpc_default_timeout(client, timeout_ms):
    client.rpc_client.transport.default_timeout_ms = timeout_ms

def get_rpc_default_timeout(client):
    return client.rpc_client.transport.default_timeout_ms

def test_sync_rpc(rpc_client_wrapper, rpc_server_wrapper):
    client = rpc_client_wrapper.get_proxy()
    now = time.time()
    ret = exception_handle(client.sleep, 1, timeout_ms=2000)
    assert 'server time cost for 1 second sleep:' in ret
    time_cost = time.time() - now
    assert 0.8 < time_cost < 1.5

def test_client_timeout(rpc_client_wrapper, rpc_server_wrapper):
    client = rpc_client_wrapper.get_proxy()
    t = get_rpc_default_timeout(rpc_client_wrapper)
    set_rpc_default_timeout(rpc_client_wrapper, 500)
    now = time.time()
    with pytest.raises(Exception) as e:
        client.sleep(1)
    assert e.typename == 'RPCError' and '[RPCError] Timeout waiting for response from server' in str(e)
    time_cost = time.time() - now
    assert 0.5 < time_cost < 1

    with pytest.raises(Exception) as e:
        client.exception_test()
    assert e.typename == 'RPCError' and '[RPCError] Timeout waiting for response from server' in str(e)
    # restore default timeout
    set_rpc_default_timeout(rpc_client_wrapper, t)
    time.sleep(2)


def test_register_rpc_service(rpc_client_wrapper, rpc_server_wrapper, rpc_service_list):
    dispatcher = rpc_server_wrapper.rpc_server.dispatcher

    assert 'sleep' in dispatcher.subdispatchers[''][0].__dict__['method_map']
    assert 'measure' in dispatcher.subdispatchers[''][0].__dict__['method_map']

    # rpc_server_wrapper.register_instance(rpc_service_list)

    client = rpc_client_wrapper.get_proxy()
    client_driver = rpc_client_wrapper.get_proxy('driver')
    client_dummy = rpc_client_wrapper.get_proxy('dummy')
    assert exception_handle(rpc_client_wrapper.rpc, 'driver.fun') == 'calling driver.fun()'

    # with args
    assert exception_handle(client_driver.fun, 1, 2) == 'calling driver.fun(1, 2)'

    # with kwargs
    assert exception_handle(client_driver.fun_kwargs, a=1, b=2) == 'calling driver.fun_kwargs(a=1, b=2)'

    # with kwargs and timeout
    assert exception_handle(client_driver.fun_kwargs, a=1, b=2, timeout_ms=10000) == 'calling driver.fun_kwargs(a=1, b=2)'
    assert exception_handle(client_dummy.sleep, 0.1).startswith('server time cost for 0.1 second sleep: ')

    # test dispatch invalid method
    with pytest.raises(RPCError) as e:
        client_driver.invalid_method()
    assert '[RPCError] Method not found: driver.invalid_method' in str(e)

    # test calling invalid service
    with pytest.raises(RPCError) as e:
        client_service = client_driver = rpc_client_wrapper.get_proxy('invalid_service')
        client_service.sleep()
    assert e.typename == 'RPCError'

    # test exception if double registering same driver w/ same prefix
    with pytest.raises(RPCError) as e:
        rpc_server_wrapper.register_instance({'dummy': DummyRPCService()})
    assert "Name set(['exception_test', 'args_test', 'sleep', 'non_utf8_str', 'measure']) already registered in subdispather dummy" in str(e)
    with pytest.raises(RPCError) as e:
        rpc_server_wrapper.register_instance(DummyRPCService())
    assert "Name set(['exception_test', 'args_test', 'sleep', 'non_utf8_str', 'measure']) already registered in subdispather" in str(e)

def test_server_worker_unavailble(rpc_client_wrapper, rpc_server_wrapper):
    def thread_worker():
        no_publisher = NoOpPublisher()
        client = RPCClientWrapper(ENDPOINT_CLIENT, no_publisher).get_proxy()
        client.sleep(3)
        client.rpc_client.stop()

    threads = []
    for i in range(THREAD_POOL_WORKERS):
        thread = Thread(target=thread_worker)
        threads.append(thread)
    for thread in threads:
        thread.start()

    # sleep to make sure all threadpool jobs are actually running;
    # without the sleep it is possible that measure run before sleep() in thread

    time.sleep(1)
    with pytest.raises(RPCError) as e:
        print rpc_client_wrapper.proxy.measure(1)
    assert e.typename == 'RPCError' and 'No available worker in thread pool' in str(e)
    # wait for all threads to finish for next test.
    for thread in threads:
        thread.join()

def test_rpc_service_exception(rpc_client_wrapper, rpc_server_wrapper):
    client_dummy = rpc_client_wrapper.get_proxy('dummy')
    with pytest.raises(Exception) as e:
        client_dummy.exception_test()
    assert 'Test Exception, raises exception on purpose' in str(e)

def test_rpc_rpc_test(rpc_client_wrapper, rpc_server_wrapper, method_args, method_kwargs):
    client_dummy = rpc_client_wrapper.get_proxy('')
    assert client_dummy.args_test(*method_args, **method_kwargs) == [method_args] + [method_kwargs]

def test_server_is_ready(rpc_client_wrapper, rpc_server_wrapper):
    server = rpc_client_wrapper.get_proxy('server')
    client = rpc_client_wrapper
    print 'testing accessible server'
    assert 'normal' == server.mode()

def test_multiple_client(rpc_client_wrapper, rpc_server_wrapper):
    print 'testing non-accessible server'
    no_publisher = NoOpPublisher()
    clients = []
    uuids = []

    # sync RPC
    for i in range(5):
        client = RPCClientWrapper(ENDPOINT_CLIENT, no_publisher)
        clients.append(client)

    start = time.time()
    for client in clients:
        ret = client.proxy.sleep(1)
        # assert(ret.startswith('server time cost for 1 second sleep: 1'))

    time_cost = time.time() - start
    print 'sync time_cost: ', time_cost
    for client in clients:
        client.rpc_client.stop()

    # sync RPC, time cost should be within about N*1s sleep + 0.08 estimated max overhead
    assert (4 < time_cost < 7)


def test_log_file(rpc_client_wrapper, rpc_server_wrapper):
    client = rpc_client_wrapper.get_proxy('')
    server = rpc_client_wrapper.get_proxy('server')
    # send msg to server and server will send it back
    msg = 'log to test log'
    ret = client.measure(msg)
    assert msg == ret
    # sleep to ensure log are flushed to file
    time.sleep(1)
    log_file = rpc_server_wrapper.logger.file_path

    # check file name format: rpc_server_port_timestamp.log
    file_name = os.path.basename(log_file)
    # rpc_server_port_date_time.log
    pattern = 'rpc_server_[0-9]+_[0-9]+_[0-9]+.log'
    err_msg = 'rpc log file name format unexpected: {}; expecting {}'.format(file_name, pattern)
    assert re.match(pattern, file_name), err_msg

    with open(log_file, 'rb') as f:
        log = f.read()
        assert ret in log

        # make sure there are received event log for the 'measure' rpc like the one below
        # 2018-09-07 11:53:08,228:INFO:[1536292388.23] received: cf65bc7281b84c4a9a9fd5be674d0124 {"args": ["log to test log"], "jsonrpc": "2.0", "method": "measure", "id": "883821b3b25111e889c4784f4367a8fb"}
        pattern_uuid = r'[0-9A-Za-z]{32}'
        pattern_received = r'INFO:.*:received: '
        pattern_received += pattern_uuid
        pattern_received += r' {"args":\["log to test log"\],"jsonrpc":"2.0",'
        pattern_received += r'"method":"measure","id":"'
        pattern_received += pattern_uuid
        pattern_received += r'"}'
        assert re.search(pattern_received, log)

        # check for sent event
        # 2018-09-07 11:53:08,229:INFO:[1536292388.23] sent: cf65bc7281b84c4a9a9fd5be674d0124 {"jsonrpc": "2.0", "id": "883821b3b25111e889c4784f4367a8fb", "result": "log to test log"}
        pattern_sent = r'INFO:.*:sent: '
        pattern_sent += pattern_uuid
        pattern_sent += r' {"jsonrpc":"2.0","id":"'
        pattern_sent += pattern_uuid
        pattern_sent += r'","result":"log to test log"}'
        assert re.search(pattern_sent, log)

    # setting logging level to ERROR and verify no INFO log in file
    server.set_logging_level('error')
    msg = 'log to test no log'
    ret = client.measure(msg)
    with open(log_file, 'rb') as f:
        log = f.read()
        assert ret not in log

    # enable the log again
    server.set_logging_level('debug')
    msg = 'log to test enable log again'
    ret = client.measure(msg)
    # sleep to ensure log are flushed to file
    time.sleep(1)
    with open(log_file, 'rb') as f:
        log = f.read()
        assert ret in log

        # make sure there are received event log for the 'measure' rpc like the one below
        # 2018-09-07 11:53:08,228:INFO:[1536292388.23] received: cf65bc7281b84c4a9a9fd5be674d0124 {"args": ["log to test enable log again"], "jsonrpc": "2.0", "method": "measure", "id": "883821b3b25111e889c4784f4367a8fb"}
        pattern_uuid = r'[0-9A-Za-z]{32}'
        pattern_received = r'INFO:.*:received: '
        pattern_received += pattern_uuid
        pattern_received += r' {"args":\["log to test enable log again"\],"jsonrpc":"2.0",'
        pattern_received += r'"method":"measure","id":"'
        pattern_received += pattern_uuid
        pattern_received += r'"}'
        assert re.search(pattern_received, log)

        # check for sent event
        # 2018-09-07 11:53:08,229:INFO:[1536292388.23] sent: cf65bc7281b84c4a9a9fd5be674d0124 {"jsonrpc": "2.0", "id": "883821b3b25111e889c4784f4367a8fb", "result": "log to test enable log again"}
        pattern_sent = r'INFO:.*:sent: '
        pattern_sent += pattern_uuid
        pattern_sent += r' {"jsonrpc":"2.0","id":"'
        pattern_sent += pattern_uuid
        pattern_sent += r'","result":"log to test enable log again"}'
        assert re.search(pattern_sent, log)

    # test server_reset_log() will remove old log file and create a new log file
    server.reset_log()
    assert not os.path.exists(log_file)
    # current log file should be updated
    assert log_file != rpc_server_wrapper.logger.file_path

    ret = client.measure(msg)
    log_file = rpc_server_wrapper.logger.file_path
    assert os.path.exists(log_file)
    with open(log_file, 'rb') as f:
        log = f.read()
        assert ret in log

def test_send_file(mgmt_client, mgmt_server, mock_file):
    '''
    test for send_image and fwup api.
    '''
    client = mgmt_client.get_proxy()
    server = mgmt_client.get_proxy('xavier')

    # None destination folder
    with pytest.raises(Exception) as e:
        mgmt_client.send_file(mock_file, None)
    assert 'Destination folder not provided' in str(e)

    # invalid destination folder
    with pytest.raises(Exception) as e:
        mgmt_client.send_file(mock_file, '/alksjdfl')
    assert 'RPCError: [RPCError] Invalid destination folder' in str(e)

    # invalid filename (including path)
    with pytest.raises(Exception) as e:
        server.send_file('../dummy_file_name', 'aaaa', '/opt/seeing/tftpboot')
    assert 'RPCError: [RPCError] Invalid file name ../dummy_file_name; should not include any path info.' in str(e)

    binary = '\x1f\x8b\x08\x00\xe5\x25\x1e\x5b'
    text = 'abcdefg'
    file_data = [binary, text]
    for data in file_data:
        fn = 'test_{}'.format(uuid.uuid4().hex)
        with open(fn, 'wb') as f:
            f.write(data)

        # write to '~' which is writeable on either xavier or mac.
        ret = mgmt_client.send_file(fn, '/tmp')
        os.remove(fn)

        new_file_path = os.path.join(os.path.expanduser('/tmp'), fn)
        assert ret == 'PASS'
        assert os.path.isfile(new_file_path)

        with open(new_file_path, 'rb') as f:
            read_data = f.read()
        os.remove(new_file_path)

        assert read_data == data

    # None file name
    with pytest.raises(Exception) as e:
        mgmt_client.send_file(None, '/tmp')
    assert 'Source file None invalid' in str(e)

    # file does not exist
    fn = 'DONOTEXIST'
    with pytest.raises(Exception) as e:
        mgmt_client.send_file(fn, '~')
    assert 'Source file DONOTEXIST is not accessible as a file' in str(e)

def test_get_log(mgmt_client, mgmt_server):
    '''
    test for get_log api.
    '''
    # get log folder
    print '------------'
    ret, data = mgmt_client.get_log(timeout_ms=5000)
    assert ret == 'PASS'
    assert data

    print '------------'
    # get log folder and write to local file as tgz
    fn = 'rpc_server_log_{}.tgz'.format(uuid.uuid4().hex)
    new_file_path = os.path.join('/tmp', fn)
    ret = mgmt_client.get_and_write_log(new_file_path, timeout_ms=3000)
    assert ret == 'PASS'
    assert os.path.isfile(new_file_path)
    os.remove(new_file_path)


def test_get_file(mgmt_client, mgmt_server):
    '''
    test for get_file api.
    '''
    client = mgmt_client.get_proxy()

    # None file
    ret, data = mgmt_client.get_file(None)
    assert 'Invalid target None to get from server' == ret
    assert data == ''

    # non-existing file
    # remove first to make sure the file does not exist;
    non_existing_fn = '~/NONEXISTINGFILE'
    try:
        os.remove(non_existing_fn)
    except:
        pass
    ret, data = mgmt_client.get_file(non_existing_fn)
    assert 'Target item to retrieve does not exist:' in ret
    assert data == ''

    binary = '\x1f\x8b\x08\x00\xe5\x25\x1e\x5b'
    text = 'abcdefg'
    file_data = [binary, text]
    for data in file_data:
        # create temp file to get
        fn = 'test_{}'.format(uuid.uuid4().hex)
        new_file_path = os.path.join(os.path.expanduser('~'), fn)
        with open(new_file_path, 'wb') as f:
            f.write(data)

        # write to '~' which is writeable on either xavier or mac.
        ret, file_data = mgmt_client.get_file('~/{}'.format(fn))
        assert ret == 'PASS'
        assert file_data == data
        os.remove(new_file_path)

    # get log folder
    ret, data = mgmt_client.get_file('log')
    assert ret == 'PASS'
    assert data

    # get from invalid folder
    ret, data = mgmt_client.get_file('/etc/passwd')
    assert 'Invalid folder /etc to get file from' in ret
    assert data == ''

    # get log folder and write to local file as tgz
    fn = 'rpc_log_{}.tgz'.format(uuid.uuid4().hex)
    new_file_path = os.path.join(os.path.expanduser('~'), fn)
    ret = mgmt_client.get_and_write_file('log', new_file_path)
    assert ret == 'PASS'
    assert os.path.isfile(new_file_path)
    os.remove(new_file_path)

    ret = mgmt_client.get_and_write_all_log(new_file_path)
    assert ret == 'PASS'
    assert os.path.isfile(new_file_path)
    os.remove(new_file_path)

def test_fw_version(mgmt_client, mgmt_server):
    '''
    test for fw_version() api.
    Check if fw_version() could return the correct version dict().
    '''
    server = mgmt_client.get_proxy('xavier')

    mock_fw_version_file = mock_open(read_data='{"fw_component": "0.0.0"}')
    with patch('__builtin__.open', mock_fw_version_file) as p:
        # patch open() so server.fw_version is actually use the mocked file content
        ver_dict = server.fw_version()
        expect = {'fw_component': '0.0.0'}
        assert ver_dict == expect

def test_server_shutdown():
    '''
    shutdown server through server(func) and client (rpc)
    '''
    server = RPCServerWrapper(ENDPOINT_SERVER_SHUTDOWN, publisher)
    client = RPCClientWrapper(ENDPOINT_CLIENT_SHUTDOWN, publisher)
    server_proxy = client.get_proxy('server')
    set_rpc_default_timeout(client, 500)
    # rpc server work
    ret = server_proxy.mode()
    assert ret == 'normal'
    assert server.stop() is True

    # server does not work after shutdown
    with pytest.raises(Exception) as e:
        server_proxy.mode()
    assert e.typename == 'RPCError' and '[RPCError] Timeout waiting for response from server' in str(e)
    client.rpc_client.stop()

    server = RPCServerWrapper(ENDPOINT_SERVER_SHUTDOWN, publisher)
    client = RPCClientWrapper(ENDPOINT_CLIENT_SHUTDOWN, publisher)
    server_proxy = client.get_proxy('server')
    set_rpc_default_timeout(client, 500)
    # rpc server work
    ret = server_proxy.mode()
    assert ret == 'normal'
    with pytest.raises(Exception) as e:
        server_proxy.stop()
    assert e.typename == 'RPCError' and '[RPCError] Timeout waiting for response from server' in str(e)

    # rpc server will actually stop current zmq poll cycle, which is at most 5s.
    # if sending rpc within 5s, still possible to get response because server happens to handle this last request.
    # taking rpc client timeout 0.5s set above, sleep 5s should make sure it is > 5s after
    # server start to shudown, which ensure shutdown done.
    time.sleep(5)
    # server does not work after shutdown
    with pytest.raises(Exception) as e:
        server_proxy.mode()
    assert e.typename == 'RPCError' and '[RPCError] Timeout waiting for response from server' in str(e)


@pytest.mark.skip(reason='Disabled due to random failure; tracked in radar 50241246')
def test_feature_profile(rpc_client_wrapper, rpc_server_wrapper):
    '''
    Test client and server profile function itself
    not to profile rpc performance
    '''
    num_rpc = 20

    client = rpc_client_wrapper
    server = client.get_proxy('xavier')
    # all profile should be disabled by default:
    # send 20 rpc to generate profile data
    for i in range(num_rpc):
        client.measure(1)

    assert not client.rpc_client.profile_result
    assert not client.rpc_client.profiler.getstats()
    breakdown, profile_result = client.server.get_profile_stats()
    assert not breakdown
    assert not profile_result

    # enable client and server profiling
    # enable both cProfile breakdown and rtt measurment
    assert 'done' == client.rpc_client.set_profile(True, True)
    assert 'done' == client.server.profile_enable()

    for i in range(num_rpc):
        client.measure(1)

    assert client.rpc_client.profile_result
    # valid list of data in client profiler stats
    assert client.rpc_client.profiler.getstats()
    breakdown, profile_result = server.get_profile_stats()
    # valid list of data in server profiler stats
    assert breakdown
    assert profile_result
    # profile_result should be a dict of {'keys': [sorted list of keys], 'step1':[lst of time]...}
    assert 'keys' in profile_result
    for key in profile_result['keys']:
        assert key in profile_result
        # each should have 20 data for 20 rpc.
        assert len(profile_result[key]) == num_rpc

    # disable profiling, clear client and server stats
    assert 'done' == server.profile_enable(False, False)
    assert 'done' == server.clear_profile_stats()
    assert 'done' == client.rpc_client.set_profile(False, False)
    assert 'done' == client.rpc_client.clear_profile_stats()

    # server stats should be empty again
    breakdown, profile_result = server.get_profile_stats()
    assert not breakdown
    assert not profile_result

    # enable rtt measuring, disable cProfile breakdown
    client.rpc_client.set_profile(False, True)
    assert 'done' == server.profile_enable(False, True)
    # get rid of impact of server.get_profile_stats and server.profile_enable
    assert 'done' == client.rpc_client.clear_profile_stats()

    for i in range(num_rpc):
        client.measure(1)

    assert client.rpc_client.profile_result
    profile_result_client = client.rpc_client.generate_profile_result()
    # valid list of data in client profiler stats
    assert not client.rpc_client.profiler.getstats()
    breakdown, profile_result = server.get_profile_stats()
    # valid list of data in server profiler stats
    assert not breakdown
    assert profile_result
    # profile_result should be a dict of {'keys': [sorted list of keys], 'step1':[lst of time]...}
    assert 'keys' in profile_result
    keys = profile_result.pop('keys')
    assert [u'parse_request', u'dispatch', u'serialize'] == keys
    for key in keys:
        assert key in profile_result
        # each should have 20 data for 20 rpc.
        assert len(profile_result[key]) == num_rpc

    # verify profile statistics at client side. The format is same as client:
    #    {
    #        'keys': [SORTED_POINT1, SORTED_POINT2, ...],
    #        'POINT1': [DATA1, DATA2, ...],
    #        'POINT2': [DATA1, DATA2, ...],
    #    }
    assert 'keys' in profile_result_client
    keys = profile_result_client.pop('keys')
    assert ['create_request', 'serialize', 'reply_got', 'parse_reply', 'return'] == keys
    assert 'create_request' in profile_result_client
    assert 'serialize' in profile_result_client
    assert 'reply_got' in profile_result_client
    assert 'parse_reply' in profile_result_client
    assert 'return' in profile_result_client
    # 20 valid data point
    for v in profile_result_client.values():
        assert len(v) == num_rpc

    # disable server profiling
    assert 'done' == server.profile_enable(False, False)
    # new rpc should not generate any profile data in server
    assert 1 == client.measure(1)
    assert 'normal' == server.mode()

    breakdown, profile_result = server.get_profile_stats()
    # valid list of data in server profiler stats
    assert not breakdown
    # previous data not cleared, still valid
    assert profile_result

    # data should increase by 1 because server.get_profile_stats();
    # should not increase due to the measure() rpc.
    assert 'keys' in profile_result
    for key in profile_result['keys']:
        assert key in profile_result
        assert len(profile_result[key]) == num_rpc + 1

    assert 'done' == server.clear_profile_stats()
    client.rpc_client.clear_profile_stats()

def test_logging_param(logging_params, log_test_transport):
    server = RPCServerWrapper(log_test_transport, log_level=logging_params[0], log_folder_path=logging_params[1])
    assert server.logger.level == logging_params[0]
    assert server.logger.log_folder == os.path.abspath(os.path.expanduser(logging_params[1]))

def test_serialize_failure(rpc_client_wrapper, rpc_server_wrapper):
    '''
    make RPC return un-serialized return value and ensure the rpc will have response to client.
    If server not handling serialize() failure, the rpc could stuck in threadpool.
    '''
    client = rpc_client_wrapper.get_proxy()
    with pytest.raises(Exception) as e:
        ret = client.non_utf8_str()
        raise Exception('Exception exception of serialize() failure not raised.')
    assert 'Unsupported UTF-8 sequence length when encoding string' in str(e)
    # threadpool tasks number shall be zero after a short period of time
    time.sleep(0.1)
    assert len(rpc_server_wrapper.rpc_server.tasks) == 0

def test_client_wrapper_rpc(rpc_client_wrapper, rpc_server_wrapper, rpc_to_test):
    '''
    Verify rpc client wrapper "rpc" api
    '''
    client = rpc_client_wrapper

    now = time.time()

    method = rpc_to_test[0]
    args = rpc_to_test[1]
    expected = rpc_to_test[2]
    ret = exception_handle(client.rpc, method, args, timeout_ms=2000)
    assert ret == expected, 'Unexpected ret for {}({}): {}; expecting {}'.format(method, args, ret, expected)

def test_client_wrapper_getattr(rpc_client_wrapper, rpc_server_wrapper):
    '''
    client wrapper getattr shall return proxy to support syntax like client.driver.fun()
    '''
    now = time.time()

    ret = exception_handle(rpc_client_wrapper.dummy.measure, 1, timeout_ms=2000)
    assert ret == 1, 'Unexpected ret for client.dummy.measure(1test_client_wrapper_getattr): {}; expecting 1'.format(ret)

def test_client_endpoint_str(rpc_server_wrapper):
    '''
    ensure user can use syntax below to create rpc client:
    client = RPCClientWrapper('tcp://127.0.0.1:8889')
    '''
    client = RPCClientWrapper(ENDPOINT_CLIENT_STR)
    assert client.server.mode() == 'normal'

def test_client_endpoint_ip_port(rpc_server_wrapper):
    '''
    ensure user can use syntax below to create rpc client:
    client = RPCClientWrapper(ip='127.0.0.1', port=8889)
    '''
    client = RPCClientWrapper(ip=ENDPOINT_CLIENT_IP, port=ENDPOINT_CLIENT_PORT)
    assert client.server.mode() == 'normal'

def test_client_endpoint_ip_ports(rpc_server_wrapper):
    '''
    ensure user can use syntax below to create rpc client:
    client = RPCClientWrapper(ip='127.0.0.1', port=8889, receiver_port=18889)
    '''
    client = RPCClientWrapper(ip=ENDPOINT_CLIENT_IP,
                              port=ENDPOINT_CLIENT_PORT,
                              receiver_port=ENDPOINT_CLIENT_PORT + 10000)
    assert client.server.mode() == 'normal'

def test_client_endpoint_ip_port_error(rpc_server_wrapper, wrong_port):
    '''
    Test error reporting when creating rpc client with ip and port
    '''
    with pytest.raises(AssertionError) as e:
        client = RPCClientWrapper(ip='127.0.0.1', port=wrong_port)
    if 55536 <= wrong_port < 65536:
        expected_msg = 'Failed to generate receiver_port by 10000 + port {}; please use port < 55536'.format(wrong_port)
    else:
        expected_msg = 'port {} invalid; please choose from (0, 65536)'.format(wrong_port)
    assert expected_msg in str(e)

def test_client_endpoint_ip_ports_error(rpc_server_wrapper, wrong_receiver_port):
    '''
    Test error reporting when creating rpc client with ip and 2 ports
    '''
    with pytest.raises(AssertionError) as e:
        client = RPCClientWrapper(ip='127.0.0.1', port=7800,
                                  receiver_port=wrong_receiver_port)
    if 55536 <= wrong_receiver_port < 65536:
        expected_msg = 'Failed to generate receiver_port by 10000 + port {}; please use port < 55536'.format(wrong_receiver_port)
    else:
        expected_msg = 'port {} invalid; please choose from (0, 65536)'.format(wrong_receiver_port)
    assert expected_msg in str(e)


def test_get_linux_boot_log(mgmt_client):
    import os
    import base64
    from tinyrpc.client import RPCClient
    mock_file = os.path.join(os.path.dirname(__file__), 'syslog')
    with mock.patch.object(RPCClient, 'get_proxy') as mock_proxy:
        mock_proxy('xavier').get_linux_boot_log = mock.Mock(return_value=('PASS', base64.b64encode('This is linux boot log for test')))
        mock_return_value = mgmt_client.get_linux_boot_log(mock_file)
    assert mock_return_value == 'PASS'
    with open(mock_file, 'rb') as f:
        mock_log_content = f.read()
    assert mock_log_content == 'This is linux boot log for test'
