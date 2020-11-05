//
//  RPCProtocol.h
//  mix_rpc_client
//
//  Created by Shark Liu on 06/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol RPCRequest <NSObject>
@property (retain) NSString* uuid;
@property (retain) NSString* method;
@property (retain) NSArray* args;
@property (retain) NSDictionary* kwargs;

- (NSData *) serialize;

@end


@protocol RPCResponse <NSObject>
@property (retain) NSString* uuid;
@property (retain) NSString* error;
@property (retain) id result;
@property (assign) NSInteger errorCode;

@end


@protocol RPCProtocol<NSObject>
@property (assign) BOOL isLogging;
- (id) createRequest:(NSString *)method withArgs:(NSArray *)args withKwargs:(NSDictionary *)kwargs;
- (id) parseReply:(id)data;
- (id) parseReply:(id)data error:(NSError **)error;
@end
