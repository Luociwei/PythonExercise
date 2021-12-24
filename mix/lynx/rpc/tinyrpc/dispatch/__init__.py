#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import logging

from ..exc import *
from ..protocols.jsonrpc import JSONRPCServerError, JSONRPCMethodNotFoundError
from ..config import NAME_METHOD_SEPARATOR
import os
import traceback


def public(name=None):
    """Set RPC name on function.

    This function decorator will set the ``_rpc_public_name`` attribute on a
    function, causing it to be picked up if an instance of its parent class is
    registered using
    :py:func:`~tinyrpc.dispatch.RPCDispatcher.register_instance`.

    ``@public`` is a shortcut for ``@public()``.

    :param name: The name to register the function with.
    """
    # called directly with function
    if callable(name):
        f = name
        f._rpc_public_name = f.__name__
        return f

    def _(f):
        f._rpc_public_name = name or f.__name__
        return f

    return _


class RPCDispatcher(object):
    """Stores name-to-method mappings."""

    def __init__(self):
        self.method_map = {}
        self.subdispatchers = {}
        self.logger = logging.getLogger()

    def add_subdispatch(self, dispatcher, prefix=''):
        """Adds a subdispatcher, possibly in its own namespace.
        It raises Error if the method under registering already exists in
        current subdispatcher w/ the same prefix

        :param dispatcher: The dispatcher to add as a subdispatcher.
        :param prefix: A prefix. All of the new subdispatchers methods will be
                       available as prefix + their original name.
        """
        if prefix in self.subdispatchers:
            exist_objs = self.subdispatchers[prefix]
            new_methods = set(dispatcher.method_map.keys())
            for obj in exist_objs:
                exist_methods = set(obj.method_map.keys())
                if len(new_methods & exist_methods) is not 0:
                    raise RPCError('Name %s already registered in subdispather %s' %
                                   (new_methods & exist_methods, prefix))
        self.subdispatchers.setdefault(prefix, []).append(dispatcher)

    def add_method(self, f, name=None):
        """Add a method to the dispatcher.

        :param f: Callable to be added.
        :param name: Name to register it with. If ``None``, ``f.__name__`` will
                     be used.
        """
        assert callable(f), "method argument must be callable"
        # catches a few programming errors that are
        # commonly silently swallowed otherwise
        if not name:
            name = f.__name__

        if name in self.method_map:
            raise RPCError('Name %s already registered' % name)  # pragma: no cover

        self.method_map[name] = f

    def dispatch(self, request):
        """Fully handle request.

        The dispatch method determines which method to call, calls it and
        returns a response containing a result.

        No exceptions will be thrown, rather, every exception will be turned
        into a response using :py:func:`~tinyrpc.RPCRequest.error_respond`.

        If a method isn't found, a :py:exc:`~tinyrpc.exc.MethodNotFoundError`
        response will be returned. If any error occurs outside of the requested
        method, a :py:exc:`~tinyrpc.exc.ServerError` without any error
        information will be returend.

        If the method is found and called but throws an exception, the
        exception thrown is used as a response instead. This is the only case
        in which information from the exception is possibly propagated back to
        the client, as the exception is part of the requested method.

        :py:class:`~tinyrpc.RPCBatchRequest` instances are handled by handling
        all its children in order and collecting the results, then returning an
        :py:class:`~tinyrpc.RPCBatchResponse` with the results.

        :param request: An :py:func:`~tinyrpc.RPCRequest`.
        :return: An :py:func:`~tinyrpc.RPCResponse`.
        """
        return self._dispatch(request)

    def _dispatch(self, request):
        try:
            try:
                method = self.get_method(request.method)
            except JSONRPCMethodNotFoundError as e:
                return request.error_respond(e)

            # we found the method
            try:
                result = method(*request.args, **request.kwargs)
            except Exception as e:
                # an error occurred within the method, return it
                e.message = '{}: {}'.format(str(e), traceback.format_exc())
                return request.error_respond(e)

            # respond with result
            return request.respond(result)
        except Exception as e:  # pragma: no cover
            # unexpected error, do not let client know what happened
            msg = '{}: {}'.format(e.message, traceback.format_exc())
            return request.error_respond(JSONRPCServerError(msg))

    def get_method(self, name):
        """Retrieve a previously registered method.

        Checks if a method matching ``name`` has been registered.

        If :py:func:`get_method` cannot find a method, every subdispatcher
        with a prefix matching the method name is checked as well.

        If a method isn't found, a :py:class:`KeyError` is thrown.

        :param name: Callable to find.
        """
        if name in self.method_map:
            return self.method_map[name]
        for prefix, subdispatchers in self.subdispatchers.iteritems():
            if name.startswith(prefix):
                for sd in subdispatchers:
                    try:
                        return sd.get_method(name[len(prefix):])
                    except KeyError:  # pragma: no cover
                        pass
                    except JSONRPCMethodNotFoundError:
                        pass

        raise JSONRPCMethodNotFoundError('Method not found: ' + name)

    def public(self, name=None):
        """Convenient decorator.

        Allows easy registering of functions to this dispatcher. Example:

        .. code-block:: python

            dispatch = RPCDispatcher()

            @dispatch.public
            def foo(bar):
                # ...

            class Baz(object):
                def not_exposed(self):
                    # ...

                @dispatch.public(name='do_something')
                def visible_method(arg1)
                    # ...

        :param name: Name to register callable with
        """
        if callable(name):
            self.add_method(name)
            return name

        def _(f):
            self.add_method(f, name=name)
            return f

        return _

    def register_instance(self, obj):
        """Create new subdispatcher and register all public object methods on
        it.

        To be used in conjunction with the :py:func:`tinyrpc.dispatch.public`
        decorator (*not* :py:func:`tinyrpc.dispatch.RPCDispatcher.public`).

        :param obj: The object whose public methods should be made available.
        :param prefix: A prefix for the new subdispatcher.
        """
        # support single instance and list of instances
        if not isinstance(obj, dict):
            obj = {'': obj}
        for prefix, instance in obj.iteritems():
            dispatch = self.__class__()
            instance.logger = self.logger
            for name, f in self.get_public(instance).items():
                dispatch.add_method(f, name)

            # add to dispatchers
            if prefix:
                prefix += NAME_METHOD_SEPARATOR
            self.add_subdispatch(dispatch, prefix)

    def get_public(self, obj):
        '''
        get function name and pointer of functions marked with @public decorator
        Will search recersively into member variables.
        a.b.fun() --> 'b_fun'
        a.fun() --> 'fun'
        '''
        rpc = {}
        if hasattr(obj, 'rpc_public_api'):
            try:
                rpc = {k: getattr(obj, k) for k in obj.rpc_public_api}
                return rpc
            except Exception as e:
                msg = ('Failed to get RPC Public API from instance {}; '
                       'Please contact author to confirm "rpc_public_api" '
                       'matches method name; traceback: {}')
                raise RPCError(msg.format(obj, traceback.format_exc()))
        for name, attr in inspect.getmembers(obj):
            if callable(attr) and hasattr(attr, '_rpc_public_name'):
                prefixed_name = attr._rpc_public_name
                rpc[prefixed_name] = attr
        return rpc

    def all_methods(self):
        '''
        return all registered methods in dictionary with proxy being key.

        :sample return:
            {"": ["sleep", "measure"], "driver": ["fun", "echo"]}
        '''
        ret = {"": [{'name': k, 'doc': v.__doc__} for k, v in self.method_map.items()]}
        for prefix, sd in self.subdispatchers.items():
            ret[prefix] = []
            for i in sd:
                ret[prefix] += [{'name': k, 'doc': v.__doc__} for k, v in i.method_map.items()]

        return ret
