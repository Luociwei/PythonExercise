//
//  mix_rpc_client_framework.h
//  mix_rpc_client_framework
//
//  Created by Shark Liu on 15/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <Cocoa/Cocoa.h>
#import "mix_rpc_client_framework/mix_rpc_client.h"
#import <mix_rpc_client_framework/JSONRPCProtocol.h>
#import "mix_rpc_client_framework/rpc_error_code.h"

//! Project version number for mix_rpc_client_framework.
FOUNDATION_EXPORT double mix_rpc_client_frameworkVersionNumber;

//! Project version string for mix_rpc_client_framework.
FOUNDATION_EXPORT const unsigned char mix_rpc_client_frameworkVersionString[];

// In this header, you should import all the public headers of your framework using statements like #import <mix_rpc_client_framework/PublicHeader.h>

/*
 * interface provided:
 * -----------------------------------------------------------------------------------
 * + (id)initWithIP:(NSString *)ip withPort:(NSUInteger)port;
 * + (id)initWithIP:(NSString *)ip withPort:(NSUInteger)port withReceiverPort:(NSUInteger)receiverPort;

 * - (id)rpc:(NSString *)method args:(NSArray *)args kwargs:(NSDictionary *)kwargs error:(NSError **)error;
 * - (id)rpc:(NSString *)method args:(NSArray *)args error:(NSError **)error;
 * - (id)rpc:(NSString *)method kwargs:(NSDictionary *)kwargs error:(NSError **)error;
 * - (id)rpc:(NSString *)method error:(NSError **)error;
 * - (id)rpcWithDictionaryArgs:(NSDictionary *)dict_args error:(NSError **)error;

 * - (NSString *)isServerReady;
 * - (NSString *)getServerMode;

 * - (void)sendFile:(NSString *)srcFile intoFolder:(NSString *)dstFolder withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
 * - (NSData *)getFile:(NSString *)target withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
 * - (void)getAndWriteFile:(NSString *)target intoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;
 * - (void)getAndWriteAllLogsIntoDestFile:(NSString *)destFile withTimeoutInMS:(NSUInteger)timeout error:(NSError **)error;

 * - (void)enableLogging: (BOOL)enableProtocolLogging enableTransportLogging: (BOOL)enableTransportLogging;
 * -----------------------------------------------------------------------------------
 * please refer to sample test code in test_framework_arc.m in mix_rpc_client_framework.framework/Resources/ for usage reference.
 */
