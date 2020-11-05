.. tinyrpcx documentation master file, created by
   sphinx-quickstart on Fri Jul 27 22:59:01 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to tinyrpcX's documentation!
====================================
tinyrpcx is python module designed for supporting remote process control with customized protocol. Powered by zmq router-dealer socket, 
tinrpcX can support both synchronization and asynchronization application. 

Quick Start
--------------
Tinyrpx provides simple entrance for set up a RPCClient or RPCServer. All you need to do is to import the RPCClient/RPCServer wrapper, 
and initialize a RPCClientWrapper/RPCServerWrapper instance.

A Client working on localhost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python
        
        import zmq
        from tinyrpc.rpc_client import RPCClientWrapper
        from publisher import ZmqPublisher

        publisher = ZmqPublisher(zmq.Context(), "tcp://127.0.0.1:6050")
        client = RPCClientWrapper({"requester": "tcp://127.0.0.1:6000", "receiver": "tcp://127.0.0.1:16000"}, publisher)

        # get rpc service proxy & make a call
        client_dummy = client.get_proxy('DummyRPCService', prefix = 'dummy')
        # a sleep function is registered at server side in DummyRPCService class
        ret = client_dummy.sleep(1)

A Server working on localhost
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

        import zmq
        from tinyrpc.rpc_server import RPCServerWrapper
        from publisher import ZmqPublisher
        from DummyRPCService import DummyRPCService

        publisher = ZmqPublisher(zmq.Context(), "tcp://127.0.0.1:7050")
        server = RPCServerWrapper({"receiver": "tcp://127.0.0.1:6000", "replier": "tcp://127.0.0.1:16000"}, publisher)

        # register some rpc service
        service = DummyRPCService()
        server.register(service)

Sub modules working in tinyrpcx
-----------------------------------
Looking into the wrapper, tinyrpcx can be devided to serveral function modules: client, server, protocols, dispatch, transports.

:doc:`client` is the main class for the rpc client. It provides the high-level API for users to make rpc call and get the results.
All the rpc service can be encapsulated into a `RPCProxy`, and working just like a local call in the client applciations.
To support asynchronization, a `ClientReceiver` is indenpently working in a daemon thread and keeplistening to the msg from server. 

:doc:`server` is the main entrance for a rpc server. RPCServer will start to work as soon as it is initialized through the `RPCServerWrapper`. 
Any msg received from client will be parsed to find out if it is complied to the protocol and if there's avaiable services can be dispatched for the msg.
API `register_instance` is designed to register the service instance into the server dispatching service.

.. code-block:: python

        # register service with prefix
        server.register(driver, 'driver')
        # register a group of services by a dictionary
        server.register({driver: 'driver1', driver: 'driver2'})


tinyrpcx uses :doc:`protocols` as default messgage protocol. Jsonrpc protocol uses json key-value pairs to define the required paramters for a rpc call. 
The protocol defines the structure for JSONRPCRequest, JSONRPCResponse and JSONRPCError. 

tinyrpcx uses :doc:`transports` to do the socket management for data transmission. To support both both synchronization and asynchronization applicaiton,
the sockets is set as zmq.ROUTER for server, and zmq.DEALER for client. 

API Reference for modules
====================================
.. toctree::
   :maxdepth: 2
   
   rpc_server
   protocols
   transports
   client
   server
   dispatch
