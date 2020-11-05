#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mock import Mock, MagicMock
import pytest
import inspect
import re

from tinyrpc.dispatch import RPCDispatcher, public
from tinyrpc import RPCRequest, RPCBatchRequest, RPCBatchResponse
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol, JSONRPCInvalidParamsError
from tinyrpc.exc import *

@pytest.fixture
def dispatch():
    return RPCDispatcher()


@pytest.fixture()
def subdispatch():
    return RPCDispatcher()


@pytest.fixture()
def mock_request(method='subtract', args=None, kwargs=None):
    mock_request = Mock(RPCRequest)
    mock_request.method = method
    mock_request.args = args or [4, 6]
    mock_request.kwargs = kwargs or {}

    return mock_request

def test_function_decorating_without_paramters(dispatch):
    @dispatch.public
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo

def test_function_decorating_with_empty_paramters(dispatch):
    @dispatch.public()
    def foo(bar):
        pass

    assert dispatch.get_method('foo') == foo

def test_function_decorating_with_paramters(dispatch):
    @dispatch.public(name='baz')
    def foo(bar):
        pass

    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')

    assert dispatch.get_method('baz') == foo

def test_subdispatchers(dispatch, subdispatch):
    @dispatch.public()
    def foo(bar):
        pass

    @subdispatch.public(name='foo')
    def subfoo(bar):
        pass

    dispatch.add_subdispatch(subdispatch, 'sub.')

    assert dispatch.get_method('foo') == foo
    assert dispatch.get_method('sub.foo') == subfoo

def test_object_method_marking():
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()

    assert not hasattr(f.foo1, '_rpc_public_name')
    assert f.foo2._rpc_public_name == 'foo2'
    assert f.foo3._rpc_public_name == 'baz'

def test_object_method_register(dispatch):
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f)

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    assert dispatch.get_method('foo2') == f.foo2
    assert dispatch.get_method('baz') == f.foo3

def test_object_method_register_whitelist(dispatch):
    class Foo(object):
        rpc_public_api = ['foo2', 'foo3']

        def foo1(self):
            pass

        def foo2(self):
            pass

        def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance(f)

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    assert dispatch.get_method('foo2') == f.foo2
    assert dispatch.get_method('foo3') == f.foo3

def test_object_method_register_whitelist_hasattr_fail(dispatch):
    class Foo(object):
        rpc_public_api = ['']

    f = Foo()

    with pytest.raises(RPCError) as e:
        dispatch.register_instance(f)
    msg = ('Failed to get RPC Public API from instance .+; '
           'Please contact author to confirm "rpc_public_api" '
           'matches method name')
    assert re.search(msg, str(e))

def test_object_method_register_whitelist_non_callable(dispatch):
    class Foo(object):
        rpc_public_api = ['foo']
        foo = 'a'

    f = Foo()

    with pytest.raises(AssertionError) as e:
        dispatch.register_instance(f)
    msg = 'method argument must be callable' in str(e)

def test_object_method_register_with_prefix(dispatch):
    class Foo(object):
        def foo1(self):
            pass

        @public
        def foo2(self):
            pass

        @public(name='baz')
        def foo3(self):
            pass

    f = Foo()
    dispatch.register_instance({'myprefix': f})

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo1')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('myprefix.foo1')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('wrongprefix.foo1')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo2')

    with pytest.raises(MethodNotFoundError):
        assert dispatch.get_method('foo3')

    assert dispatch.get_method('myprefix.foo2') == f.foo2
    assert dispatch.get_method('myprefix.baz') == f.foo3
    all_methods = dispatch.all_methods()
    assert '' in all_methods
    assert 'myprefix.' in all_methods
    found_foo1 = False
    found_foo2 = False
    found_foo3 = False
    found_baz = False
    for rpc in all_methods['myprefix.']:
        if rpc['name'] == 'foo1':
            found_foo1 = True
        elif rpc['name'] == 'foo2':
            found_foo2 = True
        elif rpc['name'] == 'foo3':
            found_foo3 = True
        elif rpc['name'] == 'baz':
            found_baz = True
    assert not found_foo1
    assert not found_foo1
    assert found_foo2
    assert not found_foo3
    assert found_baz

def test_dispatch_calls_method_and_responds(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    assert m.subtract.called

    mock_request.respond.assert_called_with(-2)

def test_dispatch_handles_in_function_exceptions(dispatch, mock_request):
    m = Mock()
    m.subtract = Mock(return_value=-2)

    class MockError(Exception):
        pass

    m.subtract.side_effect = MockError('mock error')

    dispatch.add_method(m.subtract, 'subtract')
    response = dispatch.dispatch(mock_request)

    assert m.subtract.called

    mock_request.error_respond.assert_called_with(m.subtract.side_effect)

def test_dispatch_raises_key_error(dispatch):
    with pytest.raises(MethodNotFoundError):
        dispatch.get_method('foo')

@pytest.fixture(params=[
    ('fn_a', [4, 6], {}, -2),
    ('fn_a', [4], {}, TypeError),
    ('fn_a', [], {'a': 4, 'b': 6}, -2),
    ('fn_a', [4], {'b': 6}, -2),
    ('fn_b', [4, 6], {}, -2),
    ('fn_b', [], {'a': 4, 'b': 6}, TypeError),
    ('fn_b', [4], {}, IndexError),
    # a[1] doesn't exist, can't be detected beforehand
    ('fn_c', [4, 6], {}, TypeError),
    ('fn_c', [], {'a': 4, 'b': 6}, -2),
    ('fn_c', [], {'a': 4}, KeyError)
    # a['b'] doesn't exist, can't be detected beforehand
])
def invoke_with(request):
    return request.param

def test_argument_error(dispatch, invoke_with):
    method, args, kwargs, result = invoke_with

    protocol = JSONRPCProtocol()

    @dispatch.public
    def fn_a(a, b):
        return a - b

    @dispatch.public
    def fn_b(*a):
        return a[0] - a[1]

    @dispatch.public
    def fn_c(**a):
        return a['a'] - a['b']

    mock_request = Mock(RPCRequest)
    mock_request.args = args
    mock_request.kwargs = kwargs
    mock_request.method = method
    # dispatch._dispatch(mock_request, getattr(protocol, '_caller', None))
    dispatch._dispatch(mock_request)
    if inspect.isclass(result) and issubclass(result, Exception):
        print 'mock args', mock_request.error_respond.call_args
        assert type(mock_request.error_respond.call_args[0][0]) == result
    else:
        mock_request.respond.assert_called_with(result)
