//
//  mix_rpc_client.h
//  mix_rpc_client
//
//  Created by Shark Liu on 03/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "RPCProtocol.h"
#import "RPCTransport.h"

static NSUInteger const DEFAULT_MSG_TRANSMIT_TIME_MS = 100;

/*
 * Main RPC Client wrapper class;
 * instancelize to send rpc command.
 */
@interface RPCClientWrapper : NSObject

@property (retain) id <RPCTransport> transport;
@property (retain) id <RPCProtocol> protocol;

/*
 * endpoint could be a dictionary with 2 keys which match server's 2 endpoint:
 *     ENDPOINT = @{@"requester":@"tcp://127.0.0.1:5556", @"receiver":@"tcp://127.0.0.1:15556"};
 * correponding server endpoint:
 *     endpoint_server = {'receiver': 'tcp://127.0.0.1:7777', 'replier': 'tcp://127.0.0.1:17777'}
 * Or, endpoint could be just a NSString for receiver endpoint;
 * replier endpoint will use the same IP address; port will be 10000+receiver's ports.
 *     endpoint_server = @"tcp://127.0.0.1:7777'
 *   this is equal to
 *     endpoint_server = {'receiver': 'tcp://127.0.0.1:7777', 'replier': 'tcp://127.0.0.1:17777'}
 *
 */
+ (id)initWithEndpoint:(NSDictionary *)endpoint __attribute__((deprecated));
+ (id)initWithStringEndpoint:(NSString *)endpoint;

+ (id)initWithIP:(NSString *)ip withPort:(NSUInteger)port;
+ (id)initWithIP:(NSString *)ip withPort:(NSUInteger)port withReceiverPort:(NSUInteger)receiverPort;
/*
* RPCClient wrapper support an instance method that support to be used as
* RPCClientWrapper* client = [[RPCClientWrapper alloc] initializeWithIP:IP withPort:PORT];
* currently this is for Atlas2 plugin that requests an instance init method.
*/
- (id)initializeWithIP:(NSString *)ip withPort:(NSNumber *)port error:(NSError **)error;

/*
 * Check server mode.
 * return "PASS" if server is valid: network accessible, in "normal" mode
 * return error msg in NSString for any checking fail; please print/log the response when handling.
 */
- (NSString *)isServerReady;

/*
 * getServerMode: return "normal" when xavier is ready for testing.
 * Other possible status includes "dfu" which means xavier is in firmware update
 * and should not be regarded as valid status for testing.
 */
- (NSString *)getServerMode;

/*
 * RPC api: return whatever returned from RPC server; data type is preserved
 * For example, if server returns an python int, return value here will be NSNumber;
 * if server returns an python string, return value here will be NSString.
 * error: user should create an nil NSError* and pass in as &error to receive potential RPCError.
 * Sample:
 *     NSError* error = nil;
 *     id ret = [client rpc:@"server.mode" error:&error];
 *     if (error)
 *     {
 *         // handle RPC error like timeout or exception in RPC service.
 *     }
 *     else
 *     {
 *         // use ret as valid rpc return value.
 *     }
 */
- (id)rpc:(NSString *)method args:(NSArray *)args kwargs:(NSDictionary *)kwargs error:(NSError **)error;
- (id)rpc:(NSString *)method args:(NSArray *)args error:(NSError **)error;
- (id)rpc:(NSString *)method kwargs:(NSDictionary *)kwargs error:(NSError **)error;
- (id)rpc:(NSString *)method error:(NSError **)error;
- (id)rpcWithDictionaryArgs:(NSDictionary *)dict_args error:(NSError **)error;

// old API that does not support error; to be deprecated.
- (id)rpc:(NSString *)method args:(NSArray *)args kwargs:(NSDictionary *)kwargs __attribute__((deprecated));
- (id)rpc:(NSString *)method kwargs:(NSDictionary *)kwargs __attribute__((deprecated));
- (id)rpc:(NSString *)method args:(NSArray *)args __attribute__((deprecated));
- (id)rpc:(NSString *)method __attribute__((deprecated));
- (id)rpcWithDictionaryArgs:(NSDictionary *)dict_args __attribute__((deprecated));

/*
 * send file to xavier; encode file content with base64 as jsonrpc does not support binary data.
 * Send file specified by srcFile to xavier through RPC, as intoFolder/filename.
 * filename is the file name without path info of srcFile.
 * dst_folder should be valid folder in xavier file system;
 * server has an allowed list of dst folder; this folder should be in the list or be rejected.
 * this function will read file content from srcFile, encode it with base64encode,
 * and send to server using server_send_file api.
 * server will decode and write to dst_folder/dst_fn after validating the dst folder and fn.
 * return True on successful send; return False on failure and error message can be found in non-nil error.
 */
- (void)sendFile:(NSString *)srcFile intoFolder:(NSString *)dstFolder withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
// Legacy API that returns error in ret
- (id)sendFile:(NSString *)srcFile intoFolder:(NSString *)dstFolder withTimeoutInMS:(NSUInteger)timeout __attribute__((deprecated));

/*
 * Get file/folder from xavier; folder will be packed into tgz file before uploading.
 * Server has an allowed list of white list folder for getting files from;
 * Only file/folders directly located in whitelist folder is allowed; currently rpc log folder and ~ is supported.
 * Requesting files in other folders is considered illegal and will be rejected.
 * Specially, use "log" as target will get the whole rpc "log" folder, which contains log file of all RPC server.
 *    No log is removed in this scenario.
 * Specially, use "#log" as target will get all rpc server log of the current rpc server.
 *    note that after "#log", the log file got will be removed on server side.
 *    This is the designed way for client to retrive server log.
 * On failure, error msg is available in non-nil error; otherwise error will remains as passed in.
 */
- (NSData *)getFile:(NSString *)target withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
// calls getFile above and write to file on client side.
- (void)getAndWriteFile:(NSString *)target intoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;

// Legacy APIs that return error in ret
- (NSData *)getFile:(NSString *)target withTimeoutInMS:(NSUInteger)timeout __attribute__((deprecated));
- (NSString *)getAndWriteFile:(NSString *)target intoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout __attribute__((deprecated));

// get all log files for current xavier.
- (void)getAndWriteAllLogsIntoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
// Legacy APIs that return error in ret
- (NSString *)getAndWriteAllLogsIntoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout __attribute__((deprecated));

// get all log files for current RPC server
- (void)getAndWriteLogToFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;

// get linux boot log for current xavier
- (void)getAndWriteLinuxBootLogToFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;

/*
 * Turn on/off logging for the protocol and transport modules
 * Accept BOOL type paramter, YES turns on the logging, NO turns off the logging
 */
- (void)enableLogging: (BOOL)enableProtocolLogging enableTransportLogging: (BOOL)enableTransportLogging;

/*
 * cleanup: shutdown clien transport; current close 2 zmq sockets, send and recv.
 */
- (void)shutdown;
@end
