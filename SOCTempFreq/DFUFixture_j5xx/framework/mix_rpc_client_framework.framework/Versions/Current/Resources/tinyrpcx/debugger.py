#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import zmq
import cmd
import pdb
import sys
import time
import thread
import argparse
import traceback
from functools import wraps
from tinyrpc.exc import RPCError
from rpc_client import RPCClientWrapper
from tinyrpc.config import DEBUGGER_REP_ENDPOINT, DBG_CHANNEL


class RedirectStd(object):
    def __init__(self):
        ctx = zmq.Context()
        self.socket = ctx.socket(zmq.ROUTER)
        self.socket.bind(DEBUGGER_REP_ENDPOINT)
        self.context = 'DBG'

    def readline(self):
        context, msg = self.socket.recv_multipart()
        self.context = context
        return msg

    def write(self, s):
        self.socket.send_multipart([self.context, s])

    def flush(self):
        pass

    def shutdown(self):
        self.socket.setsockopt(zmq.LINGER, 0)
        self.socket.close()


class rpdb(pdb.Pdb):

    def __init__(self, stdin, stdout, user_rawinput):
        pdb.Pdb.__init__(self, stdin=stdin, stdout=stdout)
        self.user_rawinput = user_rawinput

    def cmdloop(self, intro=None):
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = raw_input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        print 'pdb recv:', line
                        self.stdout.write(line)
                        while not len(line):
                            line = self.stdin.readline()
                        else:
                            line = line.rstrip('\r\n')
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass


def handle_response(afunc):

    @wraps(afunc)
    def _(*args, **kwargs):
        try:
            reply = afunc(*args, **kwargs)
            if reply:
                if hasattr(reply, 'result'):
                    print reply.result
                else:
                    print str(reply)
        except RPCError as e:
            print e.message, os.linesep, traceback.format_exc()
    return _


class Debugger(cmd.Cmd):

    prompt = 'MIX Debugger>'
    intro = 'MIX FW Debugger'
    remote = None
    break_points = []
    this_run = None
    stat = ''
    ss_pdb = None

    def emptyline(self):
        pass

    def do_quit(self, cmd):
        exit()

    @handle_response
    def do_exe(self, cmd):
        input_list = cmd.split(' ')
        method = input_list[0]
        input_list.pop(0)
        args = []
        kwargs = {}
        for item in input_list:
            if '=' not in item:
                args.append(item)
            else:
                k, v = item.split('=')
                kwargs[k] = v
        print method, args, kwargs
        getattr(self.client, method)(*args, **kwargs)
        self.prompt = 'PDB Debugger>'

    @handle_response
    def do_pdb(self, cmd):
        self.ss_pdb.send_multipart([cmd])


def monitorSub(socket, stdout):
    serving = True
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    while serving:
        socks = dict(poller.poll(1000))
        if socket in socks and socks[socket] == zmq.POLLIN:
            msg = socket.recv(zmq.NOBLOCK)
            stdout.write(msg)
            time.sleep(0.2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dbg', help='pdb communication port', default="tcp://127.0.0.1:9000")
    parser.add_argument('-p', '--pub', help='transport publisher', default="tcp://127.0.0.1:9999")
    parser.add_argument('-r', '--rpc', help='rpc server communication port', default="tcp://127.0.0.1:7777")
    args = parser.parse_args()
    dbg = args.dbg
    pub = args.pub
    rs = args.rpc
    ctx = zmq.Context()
    if pdb is "None":
        from publisher import NoOpPublisher
        publisher = NoOpPublisher()
    else:
        from publisher import ZmqPublisher
        publisher = ZmqPublisher(ctx, pub, '101')
    ss = ctx.socket(zmq.DEALER)
    ss.setsockopt(zmq.IDENTITY, 'DBG')
    ss.connect(dbg)
    thread.start_new_thread(monitorSub, (ss, sys.stdout))
    rpc_client = RPCClientWrapper(rs, publisher)
    socket = ctx.socket(zmq.DEALER)
    socket.setsockopt(zmq.IDENTITY, DBG_CHANNEL)
    socket.connect(rs)
    to_deprecated = rpc_client.rpc_client.transport.socket
    rpc_client.rpc_client.transport.socket = socket
    rpc_client.rpc_client.reset()
    to_deprecated.close()
    debugger = Debugger()
    debugger.client = rpc_client
    debugger.ss_pdb = ss
    debugger.cmdloop()
