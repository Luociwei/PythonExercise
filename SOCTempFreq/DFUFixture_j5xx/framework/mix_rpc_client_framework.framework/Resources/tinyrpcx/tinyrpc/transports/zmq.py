#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import  # needed for zmq import
import zmq
import time
import uuid
import logging
from threading import Thread
from threading import Lock
from .. import HEARTBEAT_INTERVAL_S
from .. import ZMQ_POLL_INTERVAL_MS
from .. import FCT_HEARTBEAT
from .. import DONE
from .. import ERROR
from .. import DBG_CHANNEL
from .. import DEFAULT_RPC_TIMEOUT_MS
from . import ServerTransport, ClientTransport


class ZmqServerTransport(ServerTransport):
    """Server transport based on a :py:const:`zmq.ROUTER` socket.

    :param recv_ocket: A :py:const:`zmq.ROUTER` socket instance, bound to an
                   endpoint for receiving request.
    :param reply_socket: A :py:const:`zmq.ROUTER` socket instance, bound to an

                   endpoint for sending reply;

    Reason to have 2 separate sockets is ZMQ sockets are non-thread-safe;
        If we are to separate sending and receving in 2 threads, each thread
        must have its own socket or zmq could crash.
    """

    def __init__(self, recv_socket, reply_socket, endpoint, poll_time_ms=ZMQ_POLL_INTERVAL_MS):
        self.publisher = None
        self.lock = Lock()
        self.recv_socket = recv_socket
        self.reply_socket = reply_socket
        self.poller = zmq.Poller()
        self.poller.register(self.recv_socket, zmq.POLLIN)
        self.poll_time_ms = poll_time_ms
        self.heartbeat_at = time.time()
        # use global default logger as default; will be overrided when creating server
        self.logger = logging.getLogger()
        # to control whether to do transport level server logging
        self.is_logging = True
        self.endpoint = endpoint

    def broadcast(self, msg):
        self.publisher.publish(msg)
        self.heartbeat_at = time.time() + HEARTBEAT_INTERVAL_S
        # TODO: HB shall be out per 5sec or only needed as NOP when PUB idle?

    def check_heartbeat(self):
        t_now = time.time()
        if t_now >= self.heartbeat_at:
            self.broadcast(FCT_HEARTBEAT)

    def receive_message(self, poll_time_ms=None):
        """Asynchronous poll socket"""
        if poll_time_ms is None:
            poll_time_ms = self.poll_time_ms
        socks = dict(self.poller.poll(poll_time_ms))
        if socks.get(self.recv_socket) == zmq.POLLIN:
            context, message = self.recv_socket.recv_multipart()
            if self.is_logging:
                if len(message) > 2048:
                    b_message = message[:2045] + '...'
                else:
                    b_message = message
                msg = 'received: {} {}, tasks in threadpool: {}'
                msg = msg.format(context, b_message, len(self.tasks))
                self.logger.info(msg)
        else:
            context, message = None, None
        return context, message

    def send_reply_with_lock(self, context, reply):
        with self.lock:
            self.send_reply(context, reply)

    def send_reply(self, context, reply):
        self.reply_socket.send_multipart([context, reply])
        # send reply first then log;
        # this could cost minor delay of logging timestamp but it reduce rpc rtt.
        if self.is_logging:
            if len(reply) > 2048:
                b_message = reply[:2045] + '...'
            else:
                b_message = reply
            msg = 'sent: {} {}, tasks in threadpool: {}'
            msg = msg.format(context, b_message, len(self.tasks))
            self.logger.info(msg)

    @classmethod
    def create(cls, zmq_context, endpoint, poll_time_ms=ZMQ_POLL_INTERVAL_MS):
        """Create new server transport.

        Instead of creating the socket yourself, you can call this function and
        merely pass the :py:class:`zmq.core.context.Context` instance.

        By passing a context imported from :py:mod:`zmq.green`, you can use
        green (gevent) 0mq sockets as well.

        :param zmq_context: A 0mq context.
        :param endpoint: The endpoint clients will connect to.
        """
        recv_socket = zmq_context.socket(zmq.ROUTER)
        reply_socket = zmq_context.socket(zmq.ROUTER)
        recv_socket.bind(endpoint['receiver'])
        reply_socket.bind(endpoint['replier'])
        return cls(recv_socket, reply_socket, endpoint, poll_time_ms)

    def shutdown(self):
        if not self.recv_socket.closed:
            self.recv_socket.setsockopt(zmq.LINGER, 0)
            self.recv_socket.close()
        if not self.reply_socket.closed:
            self.reply_socket.setsockopt(zmq.LINGER, 0)
            self.reply_socket.close()


class ZmqClientTransport(ClientTransport):
    """Client transport based on a :py:const:`zmq.REQ` socket.

    :param send_socket: A :py:const:`zmq.REQ` socket instance, connected to the
                   server socket for sending request.
    :param recv_socket: A :py:const:`zmq.ROUTER` socket instance, bound to an
                   endpoint for receiving response;
    :param zmq_context: A 0mq context.
    :param endpoint: The endpoint the server is bound to.

    Reason to have 2 separate sockets is ZMQ sockets are non-thread-safe;
        If we are to separate sending and receving in 2 threads, each thread
        must have its own socket or zmq could crash.
    """

    def __init__(self, send_socket, recv_socket, context, endpoint, channel=None, timeout_ms=DEFAULT_RPC_TIMEOUT_MS):
        self.publisher = None
        self.send_socket = send_socket
        self.recv_socket = recv_socket
        self.context = context
        self.endpoint = endpoint
        self.channel = channel
        self.default_timeout_ms = timeout_ms

    def reconnect(self):
        self.send_socket.setsockopt(zmq.LINGER, 0)
        self.recv_socket.setsockopt(zmq.LINGER, 0)
        self.send_socket.close()
        self.recv_socket.close()
        time.sleep(0.1)
        self.send_socket = self.context.socket(zmq.DEALER)
        self.recv_socket = self.context.socket(zmq.DEALER)
        self.send_socket.setsockopt(zmq.IDENTITY, self.channel)
        self.recv_socket.setsockopt(zmq.IDENTITY, self.channel)
        self.send_socket.connect(endpoint['requester'])
        self.recv_socket.connect(endpoint['receiver'])
        # sleep 0.5s to make sure socket connection finish
        time.sleep(0.5)

    def send_message(self, message):
        self.send_socket.send(message)

    def receive_reply(self, poll_time_ms=10):
        poll = zmq.Poller()
        poll.register(self.recv_socket, zmq.POLLIN)
        socks = dict(poll.poll(poll_time_ms))

        if socks.get(self.recv_socket) == zmq.POLLIN:
            reply = self.recv_socket.recv()
        else:
            reply = None
            '''
            # potential risk; keep for the moment.
            poll.unregister(self.socket)
            # reconnect socket otherwise ZMQ socket stuck in unusable state
            self.reconnect()
            poll.register(self.socket, zmq.POLLIN)
            '''

        return reply

    def shutdown(self):
        if not self.send_socket.closed:
            self.send_socket.setsockopt(zmq.LINGER, 0)
            self.send_socket.close()
        if not self.recv_socket.closed:
            self.recv_socket.setsockopt(zmq.LINGER, 0)
            self.recv_socket.close()

    @classmethod
    def create(cls, zmq_context, endpoint):
        """Create new client transport.

        Instead of creating the socket yourself, you can call this function and
        merely pass the :py:class:`zmq.core.context.Context` instance.

        By passing a context imported from :py:mod:`zmq.green`, you can use
        green (gevent) 0mq sockets as well.

        :param zmq_context: A 0mq context.
        :param endpoint: The endpoints the server is bound to.
        """
        send_socket = zmq_context.socket(zmq.DEALER)
        recv_socket = zmq_context.socket(zmq.DEALER)
        channel = uuid.uuid4().hex
        send_socket.setsockopt(zmq.IDENTITY, channel)
        recv_socket.setsockopt(zmq.IDENTITY, channel)
        send_socket.connect(endpoint['requester'])
        recv_socket.connect(endpoint['receiver'])
        # sleep 0.5s to make sure socket connection finish
        time.sleep(0.5)
        obj = cls(send_socket, recv_socket, zmq_context, endpoint, channel)
        return obj
