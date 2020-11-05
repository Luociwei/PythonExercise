//
//  rpc_error_code.h
//  mix_rpc_client_framework
//
//  Created by Shark Liu on 2020/4/16.
//  Copyright © 2020 HWTE. All rights reserved.
//

/*
 * RPC Error code definition used by RPC Objective-C client.
 */
#ifndef rpc_error_code_h
#define rpc_error_code_h

// shared error codes between python and OC client

#define RPC_SERVER_SIDE_EXCEPTION -32000
#define RPC_INVALID_REQUEST -32600
#define RPC_METHOD_NOT_FOUND -32601
#define RPC_INVALID_PARAMETER -32602
#define RPC_SERVER_THREADPOOL_FULL -32605

#define RPC_TIMEOUT -32610

#define JSON_PARSE_RPC_RESPONSE_FAIL -32700

#define UNEXPECTED_STRING_RETURNED -33000
#define UNKNOWN_RETURN_TYPE_FROM_SERVER -33001
#define FAIL_RESULT -33002
#define FILE_INACCESSIBLE -33003

// OC specific error codes
#define RPC_RESPONSE_MISSING_JSONRPC_VERSION -34001
#define RPC_RESPONSE_WRONG_JSONRPC_VERSION -34002
#define RPC_RESPONSE_MISSING_ID -34003
#define RPC_RESPONSE_NO_RESULT_OR_ERROR -34004
#define RPC_RESPONSE_BOTH_RESULT_AND_ERROR -34005


#endif /* rpc_error_code_h */
