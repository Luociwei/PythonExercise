#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from mock import Mock
import time
import zmq

from tinyrpc.exc import RPCError
from tinyrpc.client import RPCClient, RPCProxy
from tinyrpc.protocols import RPCProtocol, RPCResponse, RPCRequest
from tinyrpc.transports.zmq import ZmqClientTransport
from publisher import NoOpPublisher

@pytest.fixture(params=['test_method1', 'method2', 'CamelCasedMethod'])
def method_name(request):
    return request.param


@pytest.fixture(params=[(), ('foo', None, 42), (1,)])
def method_args(request):
    return request.param


@pytest.fixture(params=[(), (('foo', 'bar'), ('x', None), ('y', 42)),
                        (('q', 1),)])
def method_kwargs(request):
    return dict(request.param or {})


@pytest.fixture(params=['', 'NoDot', 'dot.'])
def prefix(request):
    return request.param


@pytest.fixture
def mock_client():
    return Mock(RPCClient)


@pytest.fixture
def mock_protocol():
    mproto = Mock(RPCProtocol)

    foo = Mock(RPCResponse)
    foo.result = None
    foo.unique_id = '0'

    mproto.parse_reply = Mock(return_value=foo)
    return mproto


@pytest.fixture
def mock_transport():
    transport = Mock(ZmqClientTransport)
    transport.default_timeout_ms = 3000
    transport.socket = zmq.Context().socket(zmq.DEALER)
    transport.channel = 'mock'
    return transport


@pytest.fixture()
def client(mock_protocol, mock_transport, request):
    client = RPCClient(mock_protocol, mock_transport, NoOpPublisher())
    client.wait_for_task = Mock(return_value=None)
    response = Mock(RPCResponse)
    response.unicode = '0'
    response.result = 'result1'
    client.get_status = Mock(return_value={response.unicode: ('done', response, 'some time', 'timeout')})

    def fin():
        pass
    request.addfinalizer(fin)
    return client

@pytest.fixture
def m_proxy(mock_client, prefix):
    return RPCProxy(mock_client, prefix)

def test_proxy_calls_correct_method(m_proxy, mock_client,
                                    prefix, method_kwargs, method_args,
                                    method_name):
    getattr(m_proxy, method_name)(*method_args, **method_kwargs)

    mock_client.call.assert_called_with(
        prefix + method_name, *method_args, **method_kwargs)

def test_client_uses_correct_protocol(client, mock_protocol, method_name,
                                      method_args, method_kwargs):
    req = Mock(RPCRequest)
    req.unique_id = '0'
    req.method = 'test_method'
    req.args = method_args
    req.kwargs = method_kwargs
    mock_protocol.create_request = Mock(return_value=req)
    client.call(method_name, method_args, method_kwargs)

    assert mock_protocol.create_request.called

def test_client_uses_correct_transport(client, mock_protocol, method_name,
                                       method_args, method_kwargs, mock_transport):
    req = Mock(RPCRequest)
    req.unique_id = '0'
    req.method = 'test_method'
    req.args = method_args
    req.kwargs = method_kwargs
    mock_protocol.create_request = Mock(return_value=req)
    client.call(method_name, method_args, method_kwargs)
    assert mock_transport.send_message.called

def test_client_passes_correct_reply(client, mock_protocol, method_name,
                                     method_args, method_kwargs, mock_transport):
    req = Mock(RPCRequest)
    req.unique_id = '0'
    req.method = 'test_method'
    req.args = method_args
    req.kwargs = method_kwargs
    mock_protocol.create_request = Mock(return_value=req)
    transport_return = '023hoisdfh'
    client.transport.receive_reply = Mock(return_value=transport_return)
    time.sleep(0.1)
    client.call(method_name, method_args, method_kwargs)
    mock_protocol.parse_reply.assert_called_with(transport_return)

def test_client_raises_error_replies(client, mock_protocol, method_name,
                                     method_args, method_kwargs):
    error_response = RPCResponse()
    error_response.error = 'foo'
    client.send_and_handle_reply_blocking = Mock(return_value=error_response)

    with pytest.raises(RPCError):
        client.call(method_name, method_args, method_kwargs)
