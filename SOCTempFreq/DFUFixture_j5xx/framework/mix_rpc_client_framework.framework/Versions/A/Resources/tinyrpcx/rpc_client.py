import re
import zmq
import logging
from publisher import NoOpPublisher
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.zmq import ZmqClientTransport
from tinyrpc import RPCClient

'''
# initializing logging.
logging.basicConfig(filename='log/rpc_server.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s',
                    )

# define a new Handler to log to console as well
console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
'''


class RPCClientWrapper(object):
    '''
    RPC Client class for user.

    RPCClient needs to connect to 2 sockets on server:
        one for sending request (requester);
        the other for receiving reply (receiver), defaults to requestor + 10000

    Typical usage:
        # most commonly used
        # this implies using server's 7801 and 17801 port;
        # work when server is created as RPCServer('tcp://169.254.1.32:7801')
        rpc_client = RPCClientWrapper('tcp://169.254.1.32:7801')
        # this implies using tcp.
        rpc_client = RPCClientWrapper(ip='169.254.1.32', port=7801)
    Supported as conner case:
        # when need to specify a non-default receiver_port:
        rpc_client = RPCClientWrapper(ip='169.254.1.32', port=7801, receiver_port=20000)

    Sending RPC:
        With rpc client instantiated, it can access any rpc server registered on server with syntax
            client.INSTANCE_NAME.RPC_FUNCTION_NAME
        Example:
            # server has "server" instances registered with "mode" rpc API:
            rpc_client.server.mode()
    '''
    def __init__(self, transport=None, publisher=None, ctx=None, protocol=None, ip=None, port=None, receiver_port=None):
        self.ctx = ctx if ctx else zmq.Context().instance()
        msg = 'ip and port should be used together.'
        assert ([ip, port] == [None, None]) or (ip is not None and port is not None), msg
        if ip is not None and port is not None:
            msg = 'port {} invalid; please choose from (0, 65536)'.format(port)
            assert 0 < port < 65536, msg
            # user provide ip and port, assuming using tcp.
            # endpoint generated as 'tcp'
            # user should not pass another transport in.
            msg = 'transport cannot be used along with ip&port'
            assert transport is None, msg
            assert isinstance(ip, basestring)
            msg = 'invalid tcp port: {}'.format(port)
            assert isinstance(port, int) and 0 < port < 65536, msg
            # generate zmq endpoint from ip and port
            if receiver_port is None:
                receiver_port = port + 10000
                # ensure receiver_port is valid
                msg = ('Failed to generate receiver_port by 10000 + port {}; '
                       'please use port < 55536')
                assert receiver_port < 65536, msg.format(port)
            else:
                msg = 'receiver_port {} invalid; please choose from (0, 65536)'.format(receiver_port)
                assert 0 < receiver_port < 65536, msg
            transport = {
                'requester': 'tcp://{}:{}'.format(ip, port),
                'receiver': 'tcp://{}:{}'.format(ip, receiver_port)
            }

        if isinstance(transport, ZmqClientTransport):
            self.transport = transport
        elif isinstance(transport, dict):
            # dictionary:
            if 'requester' in transport and 'receiver' in transport:
                self.transport = ZmqClientTransport.create(self.ctx, transport)
            else:
                msg = 'endpoint dictionary {} should contains requester and receiver'
                raise Exception(msg.format(transport))
        elif isinstance(transport, basestring):
            # only 1 endpoint is provided; create endpoint for receiver by adding port by 10000
            pattern = '(tcp://)?((?P<ip>[0-9.*]+):)?(?P<port>[0-9]+)'
            re_groups = re.match(pattern, transport.strip())
            if not re_groups:
                raise Exception('Invalid RPC client endpoint format {}; '
                                'expecting tcp://IP:PORT'.format(transport))
            requester_port = int(re_groups.group('port'))
            ip = re_groups.group('ip')
            endpoints = {
                'requester': 'tcp://{}:{}'.format(ip, requester_port),
                'receiver': 'tcp://{}:{}'.format(ip, requester_port + 10000)
            }
            self.transport = ZmqClientTransport.create(self.ctx, endpoints)
        else:
            msg = 'RPC client endpoint {} not supported; expecting dict or string or ip&port.'
            raise Exception(msg.format(transport))

        self.protocol = protocol if protocol else JSONRPCProtocol()
        self.publisher = publisher if publisher else NoOpPublisher()
        self.transport.publisher = self.publisher

        self.rpc_client = RPCClient(self.protocol, self.transport,
                                    self.publisher)
        self.proxy = self.rpc_client.get_proxy()

    def hijack(self, mock, func=None):
        self.rpc_client._send_and_handle_reply = mock

    def __getattr__(self, attr):
        '''
        Handle client_wrapper.attr

        Calling rpc_client method for some function
        Create proxy otherwise.
        This enables client.driver.func() which is previously not supported.

        Args:
            attr: attribute in string; could be function name or proxy name.

        Returns:
            self.rpc_client function for items in list;
            proxy otherwise.
        '''
        pass_through_apis = [
            'get_proxy',
            'set_profile',
            'set_profile',
            'clear_profile_stats',
            'send_file',
            'get_file',
            'get_log',
            'get_linux_boot_log',
            'get_and_write_file',
            'get_and_write_log',
            'get_and_write_all_log',
            'call',
        ]
        if attr in pass_through_apis:
            return getattr(self.rpc_client, attr)
        logging.info('Getting proxy: {}'.format(attr))
        return self.rpc_client.get_proxy(attr)

    def rpc(self, method, *args, **kwargs):
        '''
        interface for calling rpc using full rpc name as string like "driver.func"

        Args:
            method: string of rpc service name;
                    format:
                        instance.function for instance methods
                        function for standalone functions.
            *args: list of un-named arguments of given method
            **kwargs: dict of keyword arguments of given method
        '''
        return self.rpc_client.call(method, *args, **kwargs)
