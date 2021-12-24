#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import zmq
import json
import socket
import traceback
from protocols.jsonrpc import JSONRPCProtocol
from transports.zmq import ZmqClientTransport
from proxy.eeproxy import EEProxy
from exc import RPCError

class RPCClient(object):
    """Client for making RPC calls to connected servers.

    :param protocol: An :py:class:`~tinyrpc.RPCProtocol` instance.
    :param transport: A :py:class:`~tinyrpc.transports.ClientTransport`
                      instance.
    """

    def __init__(self, protocol, transport):
        self.protocol = protocol
        self.transport = transport

    def _send_and_handle_reply(self, req):
        # sends and waits for reply
        reply = self.transport.send_message(req.serialize())
        response = self.protocol.parse_reply(reply)
#         logger.info("receive reply recevie response:" + response.__dict__)
        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response

    def call(self, method, args, kwargs, one_way=False):
        """Calls the requested method and returns the result.

        If an error occured, an :py:class:`~tinyrpc.exc.RPCError` instance
        is raised.

        :param method: Name of the method to call.
        :param args: Arguments to pass to the method.
        :param kwargs: Keyword arguments to pass to the method.
        :param one_way: Whether or not a reply is desired.
        """
#         logger.info("client call:%s .args :%s. kwargs:%s. protocol:%s"%(method, str(args), str(kwargs), str(self.protocol)))
        req = self.protocol.create_request(method, args, kwargs, one_way)
#         logger.info("request args:%s .request kwargs:%s. request:%s. "%(str(req.args), str(req.kwargs), str(req.serialize())))
        return self._send_and_handle_reply(req).result

    def get_proxy(self, prefix='', one_way=False):
        """Convenience method for creating a proxy.

        :param prefix: Passed on to :py:class:`~tinyrpc.client.RPCProxy`.
        :param one_way: Passed on to :py:class:`~tinyrpc.client.RPCProxy`.
        :return: :py:class:`~tinyrpc.client.RPCProxy` instance."""
        return RPCProxy(self, prefix, one_way)

    def batch_call(self, calls):
        """Experimental, use at your own peril."""
        req = self.protocol.create_batch_request()

        for call_args in calls:
            req.append(self.protocol.create_request(*call_args))

        return self._send_and_handle_reply(req)


class RPCProxy(object):
    """Create a new remote proxy object.

    Proxies allow calling of methods through a simpler interface. See the
    documentation for an example.

    :param client: An :py:class:`~tinyrpc.client.RPCClient` instance.
    :param prefix: Prefix to prepend to every method name.
    :param one_way: Passed to every call of
                    :py:func:`~tinyrpc.client.call`.
    """

    def __init__(self, client, prefix='', one_way=False):
        self.client = client
        self.prefix = prefix
        self.one_way = one_way

    def __getattr__(self, name):
        """Returns a proxy function that, when called, will call a function
        name ``name`` on the client associated with the proxy.
        """
        proxy_func = lambda *args, **kwargs: self.client.call(
                         self.prefix + name,
                         args,
                         kwargs,
                         one_way=self.one_way
                     )
        return proxy_func


class XavierRpcClient():
    def __init__(self, ip, port, mode="zmq"):
        self._ip = ip
        self._port = int(port)
        self._mode = mode
        self._protocol = JSONRPCProtocol()
        self.sock = None

    def call(self, handle, *args, **kwargs):
        if None == self.sock:
            self.sock = self._create_conn()
        req = self._protocol.create_request(handle, args, kwargs, False)
        protocol = req.serialize()
        if self._mode == "tcp":
            protocol = protocol + "\n"
        self.sock.send(protocol)
        reply = self.sock.recv(40960)
        if self._mode == "tcp":
            self.sock.close()
            self.sock = None

        return self._result_protocol(reply)

    def __create_req_conn(self):
        HOST = self._ip
        PORT = self._port
        context = zmq.Context()
        sock = context.socket(zmq.REQ)
        sock.connect("tcp://%s:%d"%(HOST, PORT))
        return sock

    def __create_tcp_conn(self):
        HOST = self._ip
        PORT = self._port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.connect((HOST, PORT))
        except Exception as e:
            print("connect %s exception : %s"%(str((HOST, PORT)), traceback.format_exc()))
        return sock

    def _create_conn(self):
        if self._mode == "tcp":
            return self.__create_tcp_conn()
        elif self._mode == "zmq":
            return self.__create_req_conn()
        else:
            print("no support mode:%s"%(msg_json["mode"]))
        return None

    def _result_protocol(self, reply):
        response = self._protocol.parse_reply(reply)
        if hasattr(response, 'error'):
            raise RPCError('Error calling remote procedure: %s' %\
                           response.error)

        return response.result
