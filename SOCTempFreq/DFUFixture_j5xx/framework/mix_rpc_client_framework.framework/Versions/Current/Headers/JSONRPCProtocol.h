//
//  JSONRPCProtocol.h
//  mix_rpc_client
//
//  Created by Shark Liu on 06/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "RPCProtocol.h"

@interface JSONRPCException : NSException
+(id)exceptionWithMsg: (NSString *)msg;
@end

@interface JSONRPCProtocol: NSObject <RPCProtocol>
@end

@interface JSONRPCRequest: NSObject <RPCRequest>
@end

@interface JSONRPCResponse: NSObject <RPCResponse>
@end

@interface JSONRPCErrorResponse: JSONRPCResponse
@end

@interface JSONRPCSuccessResponse: JSONRPCResponse
@end

/*
 * General RPC Errors:
 *    1. Exception in RPC service code
 *    2. RPC error at server side with "error" field in response.
 *    3. RPC error happens at client side, like sendFile failure.
 */

@interface RPCError: NSError
+(instancetype)errorWithCode:(NSInteger)code description:(NSString *)desc;
@end

@interface RPCTimeoutError: RPCError
+(instancetype)error;
@end
