import time
from rpc_client import RPCClientWrapper


def f8(x):
    return "%6dus" % (x * 1000000)


def profile_sync_rpc(client):
    print '-' * 80
    print 'profiling sync RPC RTT'
    cycle = 10000
    results = []
    # get rid of additional overhead of first few rpcs
    # introduced by threadpool init
    for i in range(20):
        client.driver_int1(1)

    for i in range(cycle):
        now = time.time()
        ret = client.driver_int1(1)
        assert ret == 1
        cost = time.time() - now
        results.append(cost * 1000 * 1000)

    import pstats
    pstats.f8 = f8
    import cProfile
    for i in range(5):
        cProfile.run('client.driver_int1(1)')

    result_file = '/vault/mix_rpc_python_client_profile.csv'
    with open(result_file, 'wb') as f:
        f.write('index, rtt(us)\n')
        for i, rtt in enumerate(results):
            f.write('{}, {:06f}\n'.format(i, rtt))

if __name__ == '__main__':

    print 'Please make sure server is started separately.'
    endpoint_client = {'requester': 'tcp://127.0.0.1:5556', 'receiver': 'tcp://127.0.0.1:15556'}
    client = RPCClientWrapper(endpoint_client)

    # initial work that will take 150ms; put it here to avoid adding 150ms to the 1st rpc call.
    from uuid import uuid4
    uuid4().hex

    # for socket connect
    time.sleep(0.5)

    profile_sync_rpc(client)
