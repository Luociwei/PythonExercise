//
//  RPCTransport.h
//  mix_rpc_client
//
//  Created by Shark Liu on 14/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol RPCTransport <NSObject>
@property (assign) BOOL isLogging;
// UUID: used in multi-client scenario.
@property (retain) NSString* uuid;
+ (id)createWithZMQContext:(id)ctx withEndpoint:(id)endpoint;
- (void)sendData:(NSData *)data;
- (NSData *)recvDataNonBlocking:(NSUInteger)pollTimeMS;
- (void)shutdown;
- (NSUInteger)defaultTimeoutMS;

@end
