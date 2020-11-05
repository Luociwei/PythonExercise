import time
import cProfile
from rpc_client import RPCClientWrapper
from rpc_server import RPCServerWrapper
from publisher import *
from tinyrpc.dispatch import public
from threading import Thread
import multiprocessing
import pstats

# this script is to run on client side, mostly Mac-mini.
# not necessary on the same machine as server.


def f8(x):
    return "%6.3fus" % (x * 1000000)

pstats.f8 = f8


def profile_rpc(endpoint):
    print '-' * 80
    print 'profiling rpc'
    client = RPCClientWrapper(endpoint)
    cycle = 10000
    results = []

    # get rid of additional overhead of first few rpcs
    # introduced by threadpool init
    for i in range(20):
        client.measure(1)
    # only enable rtt profile for regresion test.
    client.server_profile_enable(False, True)
    client.set_profile(False, True)
    for i in xrange(cycle):
        start = time.time()
        ret = client.measure(1)
        assert ret == 1
        results.append(time.time() - start)
        # sleep 10ms to simulate actual command channel use case
        # time.sleep(0.01)
    print '-----client profile result-----'
    print 'avg of {} measure(1) rpc: \t\t {:.3f}us'.format(cycle, 1000 * 1000 * sum(results) / cycle)
    client.set_profile(False, False)
    client.server_profile_enable(False, False)
    # client.rpc_client.profiler.print_stats()

    result = client.rpc_client.profile_rtt_result
    num = len(result)
    avg_rtt_call_us = 1000 * 1000 * sum(result) / num
    print 'Average RTT of {} profiled RPC (call(), no proxy): {:.3f}us'.format(num, avg_rtt_call_us)

    breakdown, server_profile_result = client.server_get_profile_stats(timeout_ms=10000)
    print 'ncall'.rjust(10), 'total time', 'cumulative time', 'func'
    for k, v in sorted(breakdown.items(), key=lambda (k, v): v['cum_avg'], reverse=True):
        print str(v['ncall']).rjust(10), pstats.f8(v['tot_avg']), pstats.f8(v['cum_avg']), k

    # print breakdown of different point
    profile_result = client.rpc_client.generate_profile_result()
    avg_list = [sum(profile_result[key]) / len(profile_result[key]) for key in profile_result['keys']]
    print ''.join(key.rjust(15) for key in profile_result['keys']) + 'sub-total'.rjust(15)
    print ''.join(['{:.3f}us'.format(data).rjust(15) for data in avg_list]) + '{:.3f}us'.format(sum(avg_list)).rjust(15)

    print '-----server profile result-----'
    any_key = server_profile_result['keys'][0]
    num = len(server_profile_result[any_key])
    avg_list = [sum(server_profile_result[key]) / len(server_profile_result[key])
                for key in server_profile_result['keys']]
    print ''.join(key.rjust(15) for key in server_profile_result['keys']) + 'sub-total'.rjust(15)
    print ''.join(['{:.3f}us'.format(data).rjust(15) for data in avg_list]) + '{:.3f}us'.format(sum(avg_list)).rjust(15)
    # reply_got is transport + server handle time;
    avg_reply_got = sum(profile_result['reply_got']) / len(profile_result['reply_got'])
    print 'avg transport time for {} rpc: {:.3f}us'.format(num, avg_reply_got - sum(avg_list))
    client.server_clear_profile_stats()
    client.clear_profile_stats()


def profile_multiple_client_process(endpoints, cycle, num_clients):
    '''
    Multiple clients run in different process (not thread)
    to simulate real station use case.
    endpoint could be string for single server or list for multiple server;
    num_clients will be created for every server in separate process.
    '''
    print '-' * 80
    print 'scenario 15: creating multiple RPC client in processes'

    def worker(endpoint, cycle, index, return_dict):
        # need to use different zmq context in different process so explicitly create here;
        # by default, all RPCClientWrapper instance use the same zmq Context() which is expected.
        client = RPCClientWrapper(endpoint, None, zmq.Context())
        results = []
        for i in xrange(cycle):
            start = time.time()
            ret = client.measure(1)
            results.append(time.time() - start)
            assert ret == 1
            # sleep 10ms to simulate actual command channel use case
            # time.sleep(0.01)

        client.rpc_client.stop()
        return_dict[index] = results

    manager = multiprocessing.Manager()
    processes = []
    results = {}
    if type(endpoints) is str:
        endpoints = [endpoints]
    elif type(endpoints) is list:
        # expected
        pass
    else:
        raise Exception('Unexpected endpoint {}; should be endpoint in string or list of string')

    for endpoint in endpoints:
        return_dict = manager.dict()
        results[endpoint['requester']] = return_dict
        for i in range(num_clients):
            process = multiprocessing.Process(target=worker, args=(endpoint, cycle, i, return_dict),
                                              name='{}-{}'.format(endpoint, i))
            processes.append(process)

    for p in processes:
        p.start()

    for p in processes:
        p.join()
    avg_rtt_processes = []
    for endpoint, data in results.items():
        for i, v in data.items():
            avg_rtt_processes.append(float(sum(v)) / len(v) * 1000 * 1000)
    print 'avg RTT of {} RPC: {}us'.format(cycle, float(sum(avg_rtt_processes)) / len(avg_rtt_processes))

if __name__ == '__main__':
    usage = 'usage: python profile_cilent.py [endpoint] [n_server clients_per_server] [cycle]'

    import sys
    args = sys.argv[1:]
    argc = len(args)

    # defaults:
    ip = '127.0.0.1'
    n_server = 1
    cycle = 1000
    clients_per_server = 1

    if argc == 0:
        # all default
        pass
    elif argc == 1:
        ip = args[0]
    elif argc == 3:
        ip = args[0]
        n_server = int(args[1])
        clients_per_server = int(args[2])
    elif argc == 4:
        ip = args[0]
        n_server = int(args[1])
        clients_per_server = int(args[2])
        cycle = int(args[3])
    else:
        raise Exception(usage)

    # profile multi-client-multi-server rpc rtt.

    endpoints = []
    endpoint = {'requester': 'tcp://{}:5556'.format(ip),
                'receiver': 'tcp://{}:15556'.format(ip)}
    for port in range(5556, 5556 + n_server):
        endpoint = {'requester': 'tcp://{}:{}'.format(ip, port),
                    'receiver': 'tcp://{}:{}'.format(ip, port + 10000)}
        endpoints.append(endpoint)

    # profile for phase breakdown, only use 1 client
    profile_rpc(endpoint)

    profile_multiple_client_process(endpoints, cycle, clients_per_server)

