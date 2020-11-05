#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from mock import Mock, call

from tinyrpc.server import RPCServer, ThreadPoolExecutor
from tinyrpc.transports.zmq import ZmqServerTransport as ServerTransport
from tinyrpc.protocols import RPCProtocol, RPCResponse, RPCRequest
from tinyrpc.dispatch import RPCDispatcher


CONTEXT = 'sapperdeflap'
RECMSG = 'out of receive_message'
REQ = RPCRequest()
REQ.method = 'test'

DISPATCH_REQ = RPCRequest()
DISPATCH_REQ.method = 'server_mode'

SERMSG = 'out of serialize'


@pytest.fixture
def transport():
    transport = Mock(ServerTransport)
    transport.receive_message = Mock(return_value=(CONTEXT, RECMSG))
    return transport


@pytest.fixture
def protocol():
    protocol = Mock(RPCProtocol)
    protocol.parse_request = Mock(return_value=REQ)
    protocol.error_respond = Mock(return_value=None)
    return protocol

@pytest.fixture
def protocol_dispatch():
    '''
    return a method dispatched in server main thread.
    '''
    protocol = Mock(RPCProtocol)
    protocol.parse_request = Mock(return_value=DISPATCH_REQ)
    protocol.error_respond = Mock(return_value=None)
    return protocol

@pytest.fixture()
def response():
    response = Mock(RPCResponse)
    response.serialize = Mock(return_value=SERMSG)
    return response


@pytest.fixture
def dispatcher(response):
    dispatcher = Mock(RPCDispatcher)
    dispatcher.dispatch = Mock(return_value=response)
    return dispatcher

def test_handle_message_dispatch_in_main_thread(transport, protocol_dispatch, dispatcher):
    '''
    Specific rpc will dispatch in server main thread instead of in threadpool
    '''
    server = RPCServer(transport, protocol_dispatch, dispatcher)
    server.process_one_message()

    transport.receive_message.assert_called()
    protocol_dispatch.parse_request.assert_called_with(RECMSG)
    dispatcher._dispatch.assert_called_with(DISPATCH_REQ)

def test_handle_message(transport, protocol, dispatcher):
    '''
    with threadpool, no receiver; dispatch and send reply in threadpool.
    '''
    server = RPCServer(transport, protocol, dispatcher)
    server.process_one_message()

    transport.receive_message.assert_called()
    protocol.parse_request.assert_called_with(RECMSG)

