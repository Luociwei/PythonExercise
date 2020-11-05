import time


class DummyRPCService(object):
    rpc_public_api = ['measure', 'non_utf8_str', 'args_test', 'sleep',
                      'exception_test']

    def __init__(self, name='utility'):
        self.name = name

    def measure(self, value):
        return value

    def non_utf8_str(self):
        '''
        cause serialize() error
        '''
        return '\xf8\xf2\x02\xf2'

    def args_test(self, *args, **kwargs):
        print 'measure: ', args, kwargs
        return args, kwargs

    def sleep(self, second):
        now = time.time()
        msg = '[{}] worker: start to sleep for {} second'.format(time.time(), second)
        print msg

        time.sleep(float(second))
        print '[{}] worker: end sleep for {} second'.format(time.time(), second)
        return 'server time cost for {} second sleep: {}'.format(second, time.time() - now)

    def exception_test(self):
        time.sleep(1)
        print 'raises exception on purpose'
        raise Exception('Test Exception, raises exception on purpose')


# test driver class; only for demo & testing
class driver(object):
    rpc_public_api = ['echo', 'fun', 'fun_kwargs']

    def echo(self, a):
        if len(a) > 128:
            msg = a[:125] + '...'
        else:
            msg = a
        print('Echoing {} back to client.'.format(msg))
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

