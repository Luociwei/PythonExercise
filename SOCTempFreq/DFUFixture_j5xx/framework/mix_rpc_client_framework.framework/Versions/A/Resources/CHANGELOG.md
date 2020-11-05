# mix_rpc_client release history

version 1.4.3:

    * Remove isServerUpToDate() api since we don't have version got from server
        from now.
        isServerReady() will only check if server mode is "normal".
    * Remove version info from client class.

version 1.4.2:

    * Change isLogging variable from hardcoded to be configurable in Info.plist
        This is to make isLogging variable to be configurable in Info.plist for enabling/disabling logging.
        There has two kinds of logging: Tranport logging and Protocol logging.
        Default setting is enabled, set to false in info.plist to disable logging.
    * Add enableLogging interface to allow user turning on/off logging at runtime

version 1.4.1:

    * Add 0.5s sleep after ZmqClientTransport connenct()
        This is to make sure connect() finish;
        Without this, if rpc is sent quickly after client instance is created,
        It is possbile client receive socket is not connected yet and lost
        the response.

version 1.4.0:

    * Enable ARC in project
        Remove all manual memory managing code;
        Memory usage does not increase during thread-safe 10000 RPC test.
    * Remove Proxy support which is not used.
        Proxy is desiged to support native-function-call user-experience;
        However in station SW scenario proxy does not have use case.

version 1.3.0:

    * Simplify client: remove async RPC support and client receiver.

    After internal discussion, async RPC is regarded of no use case;
    The designed use case of async RPC is single RPC command that returns
    immediately which does not exist actually.
    The real use case of parallel testing is a list of rpc/non-rpc actions
    running in parallel, while each list still executes sequentially.
    This scenario could be supported by multiple clients running in parallel
    which is supported already.
        * remove Client receiver
        * remove all async related code and test code
        * change client to send request and block wait for response
        * client support client timeout as usual
            * Poller now handle EINTR "interrupted system call" poll failure
                This is an error that is returned by zmq_poll();
                To handle it, retry polling with an adjusted timeout,
                like pyzmq does.
        * change the way to make client thread-safe;
            all function between send and recv (including these 2) are regarded
            as critical section and is locked by "synchronized".
    * remove unused interface and functions:
        client: rpcWithJSONArgs
        transport: sendMessage, recvMessage, recvData (blocking), send_and_recv


version 1.2.4:

    * Memory usage enhancement: clear RPC record after it is got by client.
        This could reduce memory usage when large data returned by server in a quick way.

version 1.2.3:

    * (backward compabitility) Support original endpoint format as NSString
        * Endpoint passed in when client initialization will be used as requester endpoint
        * receiver endpoint will use requester IP and requester port + 10000.
            Same as server rule.
        * add test case for RPC client init with single endpoint.

version 1.2.1:

    * Adding protocol logging at create_request and parse_reply.
    * Create switch in protocol and transport to enable and disable of logging.

version 1.2.0:

    * Solve thread-safe issue of client.
        * Using separate socket in main thread and receiver
            This is for working with 2-socket design of RPC server introduced in RPC server 1.2.0
        * Use different socket in different threads to avoid locking.
        * Update RPCServerTransport to accept a dictionary as endpoint including 2 endpoint information;
            One is for client main thread and the other is for receiver like this:
                ENDPOINT = @{@"requester":@"tcp://127.0.0.1:5556", @"receiver":@"tcp://127.0.0.1:15556"};
            NOTE: this will requires server >= 1.2.0 in which server also implements 2-socket solution;
            incompatible with old server.
        * add @synchronized to protect NSMutableDictionary "results" and "running".
        * adding thread-safe test case.
    * performance improvement
        * increase cycles of thread-safe from 5000 to 10000
        * reduce polling interval of receiver to 100us for better RPC round-trip time.
        * clean up logging; only send/recvData and create/parse request/reply now.
        * adding log profiling test case.

version 1.1.4:

    * limit "args" of rpc() to NSArray instead of id.

version 1.1.3:

    * build directly into .pkg.
    * update readme.

version 1.1.2:

    * add lock for uuid handling code.
    * sleep 5ms in waiting resul.
    * remove lock for uuid code, will dig more for the thread safe issue
    * Update README for client being non-thread-safe

version 1.1.1:

    * Change RPC timeout error message to begin with [RPCError] so it could be correctly captured by plugin calling it.
    * fix an logic error when logging for receiving an TIMEOUTed RPC response.

version 1.1.0:

    * distinguish milliseconds in timeout by adding MS/ms to varname.
    * requiring server 1.1.0 and above to work.

version 1.0.12:

    * remove sendFile api() with default destination folder since it is not supported by server any more.
    * Code clean up: remove commented code.
    * add more api to mix_rpc_client_framework.h for reference.
    * remove unused test_drivers/ from repo
    * move default file transfer time to a const instead of hard-code in function; change default time to 180 for both send and get file.
    * add test case in testJSONDataType for large int and large float

version 1.0.11:

    * add getFile() client api to get file from server to client.
        Mainly for getting xavier log.
    * update api: send_file() --> sendFile

version 1.0.10:

    * add send_file() client api to send file to server from client.
        Mainly for xavier firmware update.

version 1.0.9:

    * getServerMode() api is available to get server mode;
        Server mode is added in server 1.0.4; "normal" for normal testing status, "dfu" for non-testing status.
    * hello() server RPC service is removed and not called anymore.
    * isServerUpToDate() api is available to check server and client version matching.
        Calling server_rpc_version() server RPC service (previously server_is_ready() api).
        server_rpc_version() is availble in RPC server 1.0.4.
    * isServerReady: call server_hello() and server_is_ready();
        Always return NSString:
            "PASS" if server is network accessible, mode is "normal" and server client version match.
            error msg if any checking fail.
        This is the API that user could call after client init to check server status and version.
    * initWithEndpoint: do not check server status anymore, and will return an RPCClientWrapper instance.
        User software could run isServerReady() api if want to check server status.
    * Requiring RPC Server 1.0.4 or above.

version 1.0.8:

    * remove isReady() api;
    * change isServerReady() api to perform cross version check between server and client.
        cient and server now perform minimum allowed version check;
        If version does not meet minimum allowed version requirement, isServerReady() will return false.
        Maching TinyrpcX version is 1.0.1.

version 1.0.7:

    * isReady() api replaced by isServerReady() to be more accurate.
        isReady() is still working but will be removed in a future release.

version 1.0.6:

    * Increase dependency libzmq dylib file into Resouces folder;
        Need to be copied into /usr/local/lib/ for hosts that does not have zmq installed, like GH station

version 1.0.5:

    * client provide -(BOOL)isReady api to check server network connection.
    * client initialization includes network connection checking; if server is not reachable, an error message (NSString) will be returned instead of client instance.
    * fix receiver thread crash issue encounter by FCN

version 1.0.4:

    * Now the Framework support both MacOS 10.12 and 10.13.

version 1.0.3:

    * support asynchronous RPC.
            Adding "asynchronize":@YES as keyword arguments in any RPC request will make that RPC an async one.
            Async RPC will return immediately after the request is sent to server; it will not wait for server response.
            The return value will be the UUID (as NSString) of the rpc call, which could be used to query rpc request afterwards;
            The following API are provided by client for async RPC:
                - (void) waitForUUID(id)
                    wait until the given uuid(s) rpc has a non-running results; could be DONE or TIMEOUT.
                - (id) getResult(id)
                    get current result of the RPC; could be nil if RPC response has not arrived from server;
                    or actual ret returned from server if there is.
    * RPC timeout could be specified in rpc kwargs by "timeout" key now.

version 1.0.2:

    * handle client side timeout.
        Client has an default 3s timeout for RPC request;
        "timeout" keyword in rpc kwargs could override default timeout.
    * client will not crash now when read and write happened to the same socket at the same time.

version 1.0.1:

    * [internal] put RPC response receiving into a separate RPCReceiver thread; no behavior impact;
    * support multiple client in the same namespace sending request to the same server

version 1.0.0:

    * support synchronous RPC call; async call is coming soooooon.
    * with ARC enabled, support various rpc call:
        -rpc:method;
        -rpc:method args:args;
        -rpc:method args:args kwargs:kwargs;
        -rpcWithDictionaryArgs:dictArgs;
    * with ARC disabled, support RPC proxy call;
        [client rpc:@"driver_fun" args:args] is available throught the following code which is in native Objective-C function call:
        PRCProxy* driver = [client getProxy:@"driver"];
        [driver func:arg]
