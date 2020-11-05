//
//  test_framework_arc.m
//  test_framework_arc
//
//  Created by Shark Liu on 22/08/2018.
//  Copyright © 2018 HWTE. All rights reserved.
//

#import <XCTest/XCTest.h>
#import <mix_rpc_client_framework/mix_rpc_client_framework.h>
#import <mix_rpc_client_framework/rpc_error_code.h>

@interface test_framework_arc : XCTestCase
@property (retain) NSString* IP;
@property (assign) NSUInteger PORT;
@property (assign) NSUInteger NON_EXISTING_PORT;

@end

@implementation test_framework_arc
@synthesize IP;
@synthesize PORT;
@synthesize NON_EXISTING_PORT;

- (void)setUp {
    [super setUp];
    IP = @"127.0.0.1";
    PORT = 5556;
    NON_EXISTING_PORT = 5555;
}

- (void)tearDown {
    [super tearDown];
}

/*
 * test function for memory usage/leak checking.
 * Memory usage should not noticably increase when running this test.
 */
- (void)__testRPCMemory{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    for (int i = 0; i < 1000; i++)
    {
        @autoreleasepool {
            [client rpc:@"measure" args:@[@1] error:nil];
        }
    }
}

- (void)testProtocolRespNoID{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // response without "jsonrpc" key
    NSDictionary* dictResp= @{
        @"result": @1,
        @"jsonrpc": @"2.0"
    };

    NSData* data = [NSJSONSerialization dataWithJSONObject:dictResp options:0 error:nil];
    NSError* error = nil;
    id ret = [client.protocol parseReply:data error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSInteger expectedCode = RPC_RESPONSE_MISSING_ID;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:@"No 'id' key in parsed response"]);
    // test for nil error; ret should be nil.
    ret = [client.protocol parseReply:data error:nil];
    XCTAssertNil(ret);
}

- (void)testProtocolRespNoJSONRPCVersionLegacy{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // response without "jsonrpc" key
    NSDictionary* dictResp= @{
        @"result": @1,
        @"id": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",
    };

    NSData* data = [NSJSONSerialization dataWithJSONObject:dictResp options:0 error:nil];
    XCTAssertThrowsSpecificNamed([client.protocol parseReply:data],
                                 JSONRPCException,
                                 @"JSONRPCException",
                                 @"JSONRPCException not raised when no \"jsonrpc\" key in response dict.");

}

- (void)testProtocolRespNoJSONRPCVersion{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // response without "jsonrpc" key
    NSDictionary* dictResp= @{
        @"result": @1,
        @"id": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",
    };

    NSData* data = [NSJSONSerialization dataWithJSONObject:dictResp options:0 error:nil];
    NSError* error = nil;
    id ret = [client.protocol parseReply:data error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSInteger expectedCode = RPC_RESPONSE_MISSING_JSONRPC_VERSION;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:@"No 'jsonrpc' key in parsed response"]);
    // test for nil error; ret should be nil.
    ret = [client.protocol parseReply:data error:nil];
    XCTAssertNil(ret);
}

- (void)testProtocolRespWrongJSONRPCVersion{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // response without "jsonrpc" key
    NSDictionary* dictResp= @{
        @"jsonrpc": @"1.0",
        @"result": @1,
        @"id": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",

    };

    NSData* data = [NSJSONSerialization dataWithJSONObject:dictResp options:0 error:nil];
    NSError* error = nil;
    id ret = [client.protocol parseReply:data error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSInteger expectedCode = RPC_RESPONSE_WRONG_JSONRPC_VERSION;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:@"Unexpected JSONRPC version 1.0; expecting 2.0"]);
    // test for nil error; ret should be nil.
    ret = [client.protocol parseReply:data error:nil];
    XCTAssertNil(ret);
}

- (void)testProtocolRespNoResultNoError{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // response without "jsonrpc" key
    NSDictionary* dictResp= @{
        @"jsonrpc": @"2.0",
        @"id": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",

    };

    NSData* data = [NSJSONSerialization dataWithJSONObject:dictResp options:0 error:nil];
    NSError* error = nil;
    id ret = [client.protocol parseReply:data error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSInteger expectedCode = RPC_RESPONSE_NO_RESULT_OR_ERROR;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:@"Neither 'error' nor 'result' is found in resp dict"]);
    // test for nil error; ret should be nil.
    ret = [client.protocol parseReply:data error:nil];
    XCTAssertNil(ret);
}

- (void)testRespInvalidDataLegacy{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    XCTAssertThrowsSpecificNamed([client rpc:@"invalid"],
                                 JSONRPCException,
                                 @"JSONRPCException",
                                 @"JSONRPCException not raised when no rpc response contains non-utf8 string");
}

- (void)testRespInvalidData{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    NSError *error = nil;
    id ret = [client rpc:@"invalid" error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSString *expected = @"Unable to convert data to string";
    NSInteger expectedCode = JSON_PARSE_RPC_RESPONSE_FAIL;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:expected], @"Expected string %@ not found in error %@", expected, error);
}

/*
 * error handling when rpc service raise exception; expected to be catch in "error".
 */
- (void)testRPCServiceException{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    NSError *error = nil;
    id ret = [client rpc:@"exception" error:&error];
    XCTAssertNil(ret);
    XCTAssertNotNil(error);
    NSString *expected = @"Raising Exception: Hello: Traceback";
    NSInteger expectedCode = RPC_SERVER_SIDE_EXCEPTION;
    XCTAssertEqual(error.code, expectedCode, @"Error code is not %ld as expected: %ld", expectedCode, error.code);
    XCTAssertTrue([error.localizedDescription containsString:expected], @"Expected string %@ not found in error %@", expected, error);
}

/*
 * RPC API support passing "nil" to error, when error details are not important.
 * this test ensure RPC will return nil without crash when error happens.
 */
- (void)testRPCWithNilError{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    id ret = [client rpc:@"dummy" error:nil];
    XCTAssertTrue([ret isEqualToString:@"--PASS--"]);
    ret = [client rpc:@"measure" args:@[@1] error:nil];
    XCTAssertTrue([ret isEqualTo:@1]);

    ret = [client rpc:@"measure" kwargs:@{@"value": @1} error:nil];
    XCTAssertTrue([ret isEqualTo:@1]);

    ret = [client rpc:@"dummy" args:@[@1] kwargs:@{@"b": @2} error:nil];
    XCTAssertTrue([ret isEqualToString:@"--PASS--"]);
    ret = [client rpc:@"measure" args:@[@1] error:nil];

    // rpc that will have method not found error;
    ret = [client rpc:@"meow" error:nil];
    XCTAssertNil(ret);

    ret = [client rpc:@"meow" args:nil error:nil];
    XCTAssertNil(ret);

    ret = [client rpc:@"meow" kwargs:nil error:nil];
    XCTAssertNil(ret);

    ret = [client rpc:@"meow" args:nil kwargs:nil error:nil];
    XCTAssertNil(ret);
    // rpc that cause JSONRPC parse error; should not crash.
    ret = [client rpc:@"invalid" error:nil];
    XCTAssertNil(ret);
}

- (void)testDispatch{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // valid call :sleep(1, timeout_ms=20000)
    NSString* testMsg = @"server time cost for 1 second sleep: 1";
    NSError* error = nil;
    NSString* ret = [client rpc:@"sleep" args:@[@1] kwargs:@{@"timeout_ms": @20000} error:&error];
    NSLog(@"rpc received:%@, error=%@", ret, error);
    XCTAssertNil(error);
    XCTAssertTrue([ret containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    //full string is like the following line with a different id:
    testMsg = @"Method not found: meowww";
    NSError *err = nil;
    ret = [client rpc:@"meowww" args:@[] kwargs:@{@"timeout_ms":@20000, @"key":@NO} error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww 1 received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    //empty args
    testMsg = @"Method not found: meowww";
    err = nil;
    ret = [client rpc:@"meowww" args:nil kwargs:@{@"timeout_ms":@20000, @"key":@NO} error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // nil args nil kwargs
    testMsg = @"Method not found: meow";
    err = nil;
    ret = [client rpc:@"meowww" args:nil kwargs:nil error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // no args no kwargs
    err = nil;
    ret = [client rpc:@"meowww" error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // no kwargs
    err = nil;
    ret = [client rpc:@"meowww" args:@[@1] error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // no args
    err = nil;
    ret = [client rpc:@"meowww" kwargs:@{@"key": @"value"} error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // empty kwargs
    testMsg = @"Method not found: meowww";
    err = nil;
    ret = [client rpc:@"meowww" args:nil kwargs:@{} error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"meowww received error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);

    // list args
    testMsg = @"Method not found: woof";
    err = nil;
    ret = [client rpc:@"woof" args:@[@1, @2] kwargs:@{@"timeout_ms":@10000, @"key":@YES} error:&err];
    XCTAssertNil(ret);
    XCTAssertNotNil(err);
    NSLog(@"woof(1, 2, timeout_ms=10000, key=True) returns error:%@", err);
    XCTAssertTrue([[err localizedDescription] containsString:testMsg], @"server response unexpected: %@, expecting to contain %@", ret, testMsg);
}

/*
 * try to call valid rpc with the following data type:
 *   int
 *   float
 *   string
 *   list
 *   dict
 */
- (void)testJOSNDataType{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    // int
    id ret = [client rpc:@"driver.int1" args:@[@1] error:nil];
    NSLog(@"driver.int1(1) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from driver.int1;");
    XCTAssertTrue([ret isEqual:@1], @"Expecting 1 from driver.int1 but actually got: %@", ret);

    // float 1.0; will be converted into 1.
    ret = [client rpc:@"driver.float10" args:@[@1.0] error:nil];
    NSLog(@"driver.float10(1.0) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from driver.float10;");
    XCTAssertTrue([ret isEqual:@1.0], @"Expecting 1 from driver.float10 but actually got: %@", ret);

    // float 1.1
    ret = [client rpc:@"driver.float11" args:@[@1.1] error:nil];
    NSLog(@"driver.float11(1.1) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from driver.float11;");
    XCTAssertTrue([ret isEqual:@1.1], @"Expecting 1.1 from driver.float11 but actually got: %@", ret);

    // big int
    ret = [client rpc:@"measure" args:@[@1000000] error:nil];
    NSLog(@"measure(1000000) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from measure(1000000);");
    XCTAssertTrue([ret isEqual:@1000000], @"Expecting 1000000 from measure(1000000) but actually got: %@", ret);

    // big float
    ret = [client rpc:@"measure" args:@[@1000000.11] error:nil];
    NSLog(@"measure(1000000.11) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from measure(1000000.11);");
    XCTAssertTrue([ret isEqual:@1000000.11], @"Expecting 1000000 from measure(1000000.11) but actually got: %@", ret);

    // str
    ret = [client rpc:@"driver.strshark" args:@[@"shark"] error:nil];
    NSLog(@"driver.strshark('shark') received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSString class]], @"Expecting NSString from driver.strshark;");
    XCTAssertTrue([ret isEqualToString:@"shark"], @"Expecting 'shark' from driver.strshark but actually got: %@", ret);

    // list
    ret = [client rpc:@"driver.list_0_1_a_float15_false" args:@[@[@0, @1, @"a", @1.5, @NO]] error:nil];
    NSLog(@"driver.list_0_1_a_float15_false([0, 1, 'a', 1.5, NO]) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSArray class]], @"Expecting NSArray from driver.list_0_1_a_float15_false;");
    NSArray* array = @[@0, @1, @"a", @1.5, @NO];
    XCTAssertTrue([ret isEqualToArray:array], @"Expecting [0, 1, \"a\", 1.5, NO] but actually got: %@", ret);

    // dict
    ret = [client rpc:@"driver.dict_a_0" args:@[@{@"a": @0}] error:nil];
    NSLog(@"driver.dict_a_0({'a': 0})) received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSDictionary class]], @"Expecting NSDictionary from driver.dict_a_0;");
    NSDictionary* dict = @{@"a": @0};
    XCTAssertTrue([ret isEqualToDictionary:dict], @"Expecting {\"a\": 0} from driver.dict_a_0 but actually got: %@", ret);
}

/*
 * test rpcDictionaryArgs
 */
- (void)testRPCWithDictionaryArgs
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    //with rpcWithDictionaryArgs
    id ret = [client rpcWithDictionaryArgs:@{@"method": @"driver.float11", @"args":@[@1.1], @"kwargs":@{}} error:nil];
    NSLog(@"driver.float(1.1) through rpcWithDictionaryArgs received:%@", ret);
    XCTAssertTrue([ret isKindOfClass:[NSNumber class]], @"Expecting NSNumber from driver_float11;");
    XCTAssertTrue([ret isEqual:@1.1], @"Expecting 1.1 from driver_float11 but actually got: %@", ret);
}

/*
 * test createing multiple client instance
 */
- (void)testMultiClientInstance
{
    RPCClientWrapper* client = nil;
    id ret = nil;
    int i = 0;
    for (i = 0; i < 10; i++)
    {
        client = [RPCClientWrapper initWithIP:IP withPort:PORT];

        //with rpcWithDictionaryArgs
        //ret = [client rpcWithDictionaryArgs:@{@"method": @"driver_float11", @"args":@[@1.1], @"kwargs":@{}}];
        ret = [client rpc:@"sleep" args:@[@1.1] error:nil];
        NSLog(@"sleep(1.1) returns: %@", ret);
        XCTAssertTrue([ret isKindOfClass:[NSString class]], @"Expecting NSString from sleep();");
        XCTAssertTrue([ret containsString:@"server time cost for 1.1 second sleep: 1.1"], @"Unexpected result from sleep(1.1); actually got: %@", ret);
    }
}


/*
 * client side timeout
 */
- (void)testClientTimeoutLegacy
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    NSString* expect = @"[RPCError] Timeout waiting for response from server";
    NSError* error = nil;
    id ret = [client rpc:@"sleep" args:@[@4] kwargs:nil];
    NSLog(@"NSError: %@", error);
    XCTAssertTrue([ret containsString:expect], @"server response unexpected: %@, expecting to contain %@", ret, expect);

    // non-default timeout
    expect = @"server time cost for 4 second sleep: 4";
    ret = [client rpc:@"sleep" args:@[@4] kwargs:@{@"timeout_ms":@4500}];
    XCTAssertTrue([ret containsString:expect], @"server response unexpected: %@, expecting to contain %@", ret, expect);
}

/*
 * client timeout reporting through NSError
 */
- (void)testClientTimeout
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    NSString* expect = @"[RPCError] Timeout waiting for response from server";
    NSError* error = nil;
    id ret = [client rpc:@"sleep" args:@[@4] kwargs:nil error:&error];
    /*
     * Printed log is like this:
     *     2020-03-31 00:47:05.173244+0800 xctest[56559:4120968] NSError: Error Domain=mix.rpc.error Code=-32610
     *      "[RPCError] Timeout waiting for response from server" UserInfo={NSLocalizedDescription=[RPCError] Timeout waiting for response from server}
     */
    NSLog(@"NSError: %@", error);
    XCTAssertTrue(ret == nil, @"server response unexpected: %@, expecting to be nil", ret);
    XCTAssertTrue(error, @"Expected NSError not reported for rpc timeout event.");
    XCTAssertTrue([[error domain] isEqualToString:@"com.apple.mix.rpc.ErrorDomain"], @"Error domain not mix.rpc.error for rpc timeout: %@", [error domain]);
    XCTAssertTrue([error code] == -32610, @"Error code not 32610 for rpc timeout: %ld", [error code]);
    XCTAssertTrue([[error localizedDescription] isEqualToString:expect], @"Error localized description is not %@: %@", expect, [error localizedDescription]);
}

/*
 * Client initWithStringEndpoint will always return an RPCClientWrapper instance;
 * Users software could call "isServerReady" api to check for server network accessibility and version matching
 */
- (void)testServerIsReady
{
    // valid server: network accessible, version above min-allowed version.
    id clientToExistingServer = [RPCClientWrapper initWithIP:IP withPort:PORT];
    XCTAssertTrue([clientToExistingServer isKindOfClass:[RPCClientWrapper class]], @"clientToExistingServer(%@) should be RPCClientWrapper instance", clientToExistingServer);

    // valid server should return "normal".
    NSString* expect_mode = @"normal";
    NSString* mode = [clientToExistingServer getServerMode];
    XCTAssertTrue([mode isEqualToString:expect_mode], @"clientToExistingServer mode should be %@ while actually is %@", expect_mode, mode);

    // [client isServerReady] api, including mode check and version check; should be called only once.
    NSString* ret = [clientToExistingServer isServerReady];
    XCTAssertTrue([ret isEqualToString:@"PASS"], @"[client isServerReady] should be PASS while actually is %@", ret);


    // server that is not network accessible
    id clientToNonExistingServer = [RPCClientWrapper initWithIP:IP withPort:NON_EXISTING_PORT];
    XCTAssertTrue([clientToNonExistingServer isKindOfClass:[RPCClientWrapper class]], @"clientToNonExistingServer(%@) should be RPCClientWrapper instance", clientToNonExistingServer);
    // Non-existing server should return RPC timeout;
    mode = [clientToNonExistingServer getServerMode];
    NSString* expect = @"RPC error when getting server mode; error=[RPCError] Timeout waiting for response from server";
    XCTAssertTrue([mode isEqualToString:expect], @"clientToExistingServer should be equal to %@ while actually is %@", expect, mode);
}

/*
 * test client get file from server.
 */
- (void)testGetCurrentServerLog
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    NSFileManager* fm = [NSFileManager defaultManager];

    NSString* dstfile = [NSString stringWithFormat:@"dut_rpc_log_%@.tgz", [[NSUUID UUID] UUIDString]];
    NSString* dstpath = [NSString pathWithComponents:@[NSHomeDirectory(), dstfile]];

    NSError* error = nil;
    [client getAndWriteLogToFile:dstpath withTimeoutInMS:10000 error:&error];
    XCTAssertNil(error);

    XCTAssertTrue([fm fileExistsAtPath:dstpath], @"File should be written to ~/");
    [fm removeItemAtPath:dstpath error:nil];
}

/*
 * test client send file to server.
 */
- (void)testSendFile
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    NSString* filename = [NSString stringWithFormat:@"test_%@", [[NSUUID UUID] UUIDString]];
    NSFileManager* fm = [NSFileManager defaultManager];
    [fm createFileAtPath:filename contents:nil attributes:nil];
    NSString* content = @"abcdefg";
    [content writeToFile:filename atomically:false encoding:NSUTF8StringEncoding error:nil];
    NSError* error = nil;
    [client sendFile:filename intoFolder:@"~" withTimeoutInMS:6000 error:&error];
    XCTAssertNil(error);
    [fm removeItemAtPath:filename error:nil];
    NSString* dstFile = [NSString pathWithComponents:@[NSHomeDirectory(), filename]];
    XCTAssertTrue([fm fileExistsAtPath:dstFile], @"File should be transfered to ~/");
    NSString* dstContent = [NSString stringWithContentsOfFile:dstFile encoding:NSUTF8StringEncoding error:nil];
    XCTAssertTrue([content isEqualToString:dstContent], @"File should be transfered to ~/");
    [fm removeItemAtPath:dstFile error:nil];
}

/*
 * test client get file from server.
 */
- (void)testGetFile
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];

    NSString* filename = [NSString stringWithFormat:@"test_%@", [[NSUUID UUID] UUIDString]];
    NSString* filepath = [NSString pathWithComponents:@[NSHomeDirectory(), filename]];
    NSFileManager* fm = [NSFileManager defaultManager];
    [fm createFileAtPath:filepath contents:nil attributes:nil];
    NSString* content = @"abcdefg";
    [content writeToFile:filepath atomically:false encoding:NSUTF8StringEncoding error:nil];

    NSError* error = nil;
    NSData* data = [client getFile:filepath withTimeoutInMS:0 error:&error];
    XCTAssertNil(error);
    XCTAssertNotNil(data);
    NSString* str_ret = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];

    XCTAssertTrue([str_ret isEqualToString:content], @"Unexpected file content %@, expecting %@", str_ret, content);

    NSString* dstfile = [NSString stringWithFormat:@"dst_%@", [[NSUUID UUID] UUIDString]];
    NSString* dstpath = [NSString pathWithComponents:@[NSHomeDirectory(), dstfile]];

    [client getAndWriteFile:filepath intoDestFile:dstpath withTimeoutInMS:0 error:&error];
    XCTAssertNil(error);
    XCTAssertTrue([fm fileExistsAtPath:dstpath], @"File should be written to ~/");
    NSString* dstContent = [NSString stringWithContentsOfFile:dstpath encoding:NSUTF8StringEncoding error:nil];
    XCTAssertTrue([content isEqualToString:dstContent], @"Unexpected file content %@, expecting %@", dstContent, content);
    [fm removeItemAtPath:dstpath error:nil];
    [fm removeItemAtPath:filepath error:nil];
}

/*
 * test client get all log files from server;
 * only for mgmt server for the moment.
 */
- (void)testGetAllLog
{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    NSFileManager* fm = [NSFileManager defaultManager];

    NSString* dstfile = [NSString stringWithFormat:@"dst_%@.tgz", [[NSUUID UUID] UUIDString]];
    NSString* dstpath = [NSString pathWithComponents:@[NSHomeDirectory(), dstfile]];

    NSError* error = nil;
    [client getAndWriteAllLogsIntoDestFile:dstpath withTimeoutInMS:10000 error:&error];
    XCTAssertNil(error);

    XCTAssertTrue([fm fileExistsAtPath:dstpath], @"File should be written to ~/");
    [fm removeItemAtPath:dstpath error:nil];
}

/*
 *
 */
- (void)testClientThreadSafe
{
    int num = 10;
    int cycle = 10000;
    NSMutableArray* clients = [NSMutableArray array];
    for (int i = 0; i < num; i++)
    {
        RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
        [client.protocol setIsLogging:false];
        [client.transport setIsLogging:false];
        [clients addObject:client];
    }
    dispatch_queue_t queue = dispatch_queue_create("test.concurrent_queue", DISPATCH_QUEUE_CONCURRENT);

    // create different rpc for different thread to run
    void (^rpc_int_x) (RPCClientWrapper* client, int cycle, int x) = ^(RPCClientWrapper* client, int cycle, int x){
        id ret = nil;
        int i = 0;
        NSNumber* nx = [NSNumber numberWithInt:x];
        NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
        for (i = 0; i < cycle; i++)
        {
            @autoreleasepool{
                ret = [client rpc:@"driver.int1" args:@[nx] error:nil];

                XCTAssertTrue([ret isEqualToNumber:nx], @"Expecting %d from driver.int1(%d) but actually got: %@", x, x, ret);
            }
        }
        NSTimeInterval end = [[NSDate date] timeIntervalSince1970];
        NSLog(@"cost of %d RPC: %f", cycle, end - start);
    };

    RPCClientWrapper* single_client = [clients objectAtIndex:0];
    // single client single thread in threadpool
    NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
    dispatch_sync(queue, ^{rpc_int_x(single_client, cycle, 1);});
    NSTimeInterval cost_single_client_in_threadpool = [[NSDate date] timeIntervalSince1970] - start;

    // single client single thread in main thread
    start = [[NSDate date] timeIntervalSince1970];
    rpc_int_x(single_client, cycle, 1);
    NSTimeInterval cost_single_client_out_of_threadpool = [[NSDate date] timeIntervalSince1970] - start;

    // dedicate client in multiple threads
    NSMutableArray* blocks = [NSMutableArray array];
    for (int i = 0; i < num; i++)
    {
        RPCClientWrapper* client = [clients objectAtIndex:i];
        __auto_type block = dispatch_block_create(DISPATCH_BLOCK_NO_QOS_CLASS, ^(void){rpc_int_x(client, cycle, i);});
        [blocks addObject:block];
    }

    start = [[NSDate date] timeIntervalSince1970];
    for (int i = 0; i < num; i++)
    {
        void (^block)(void) = [blocks objectAtIndex:i];
        dispatch_async(queue, block);
    }

    for (int i = 0; i < num; i++)
    {
        void (^block)(void) = [blocks objectAtIndex:i];
        dispatch_block_wait(block, DISPATCH_TIME_FOREVER);
    }
    NSTimeInterval cost_dedicate_client_in_separate_threads = [[NSDate date] timeIntervalSince1970] - start;


    // single client shared in threadpool
    NSMutableArray* blocks_single_client = [NSMutableArray array];
    for (int i = 0; i < num; i++)
    {
        __auto_type block = dispatch_block_create(DISPATCH_BLOCK_NO_QOS_CLASS, ^(void){rpc_int_x(single_client, cycle, i);});
        [blocks_single_client addObject:block];
    }

    start = [[NSDate date] timeIntervalSince1970];
    for (int i = 0; i < num; i++)
    {
        void (^block)(void) = [blocks_single_client objectAtIndex:i];
        dispatch_async(queue, block);
    }

    for (int i = 0; i < num; i++)
    {
        void (^block)(void) = [blocks_single_client objectAtIndex:i];
        dispatch_block_wait(block, DISPATCH_TIME_FOREVER);
    }
    NSTimeInterval cost_single_client_multi_threads = [[NSDate date] timeIntervalSince1970] - start;

    NSLog(@"Test job of single thread: %d RPC doing echo(1)", cycle);
    NSLog(@"Total cost of single client out of threadpool: %f", cost_single_client_out_of_threadpool);
    NSLog(@"Total cost of single client in threadpool: %f", cost_single_client_in_threadpool);
    NSLog(@"Total cost of single client shared in %d threads: %f", num, cost_single_client_multi_threads);
    NSLog(@"Total cost of %d clients in %d separate threads:%f", num, num, cost_dedicate_client_in_separate_threads);

}

/*
 * function to profile logging; not run as a unit test item.
 * need to clean up later.
 */
- (void)__testLogProfiling
{
    NSString * logFile = @"/vault/mix_rpc_client_framework_test.log";

    freopen([logFile cStringUsingEncoding:NSASCIIStringEncoding], "w", stdout);
    freopen([logFile cStringUsingEncoding:NSASCIIStringEncoding], "w", stderr);

    int num = 1;
    int cycle = 10000;
    NSMutableArray* clients = [NSMutableArray array];
    for (int i = 0; i < num; i++)
    {
        RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
        [clients addObject:client];
    }

    // create different rpc for different thread to run
    void (^rpc_int_x) (RPCClientWrapper* client, int cycle, int x) = ^(RPCClientWrapper* client, int cycle, int x){
        id ret = nil;
        int i = 0;
        NSNumber* nx = [NSNumber numberWithInt:x];
        NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
        for (i = 0; i < cycle; i++)
        {
            ret = [client rpc:@"driver.int1" args:@[nx] error:nil];

            XCTAssertTrue([ret isEqualToNumber:nx], @"Expecting %d from driver_int1(%d) but actually got: %@", x, x, ret);
        }
        NSTimeInterval end = [[NSDate date] timeIntervalSince1970];
        NSLog(@"cost of %d RPC: %f", cycle, end - start);
    };

    RPCClientWrapper* single_client = [clients objectAtIndex:0];
    id <RPCTransport> t = single_client.transport;
    id <RPCProtocol> p = single_client.protocol;

    // no logging

    [t setIsLogging:false];
    [p setIsLogging:false];

    // single client single thread in main thread
    NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
    rpc_int_x(single_client, cycle, 1);
    NSTimeInterval cost_no_log = [[NSDate date] timeIntervalSince1970] - start;

    // without transport log, with protocol log
    [t setIsLogging:false];
    [p setIsLogging:true];

    start = [[NSDate date] timeIntervalSince1970];
    rpc_int_x(single_client, cycle, 1);
    NSTimeInterval cost_protocol_log_only = [[NSDate date] timeIntervalSince1970] - start;

    // with transport log, no protocol log
    [t setIsLogging:true];
    [p setIsLogging:false];

    start = [[NSDate date] timeIntervalSince1970];
    rpc_int_x(single_client, cycle, 1);
    NSTimeInterval cost_transport_log_only = [[NSDate date] timeIntervalSince1970] - start;

    // both transport log and protocol log
    [t setIsLogging:true];
    [p setIsLogging:true];

    start = [[NSDate date] timeIntervalSince1970];
    rpc_int_x(single_client, cycle, 1);
    NSTimeInterval cost_both_transport_protocol = [[NSDate date] timeIntervalSince1970] - start;

    // single NSLog profiling for dict
    NSDictionary* resp = @{
                    @"jsonrpc": @"2.0",
                    @"result": @1,
                    @"id": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",
                       };

    start = [[NSDate date] timeIntervalSince1970];

    for (int i = 0; i < cycle; i++)
    {
        NSLog(@"RPC response: %@", resp);
    }
    NSTimeInterval cost_nslog_dict = [[NSDate date] timeIntervalSince1970] - start;

    // single NSLog profiling for NSData
    NSDictionary* dictReq= @{
                            @"uuid": @"156A24D0-BAA1-4C5F-BD93-2251E6588B21",
                            @"method": @"driver.int1",
                            @"jsonrpc": @"2.0",
                            @"args":@[@1],
                            @"kwargs":[NSNull null]
                             };
    NSData* data = [NSJSONSerialization dataWithJSONObject:dictReq options:0 error:nil];

    start = [[NSDate date] timeIntervalSince1970];
    for (int i = 0; i < cycle; i++)
    {
        NSLog(@"[sendData]: data to send: %@", data);
    }
    NSTimeInterval cost_nslog_nsdata = [[NSDate date] timeIntervalSince1970] - start;

    // NSLog request

    NSString* uuid = dictReq[@"uuid"];
    NSString* method = dictReq[@"method"];
    NSArray* args = dictReq[@"args"];
    NSDictionary* kwargs = dictReq[@"kwargs"];

    start = [[NSDate date] timeIntervalSince1970];
    for (int i = 0; i < cycle; i++)
    {
        NSLog(@"RPC request: uuid: %@, method: %@, args: %@, kwargs: %@",
               uuid, method, args, kwargs);
    }
    NSTimeInterval cost_nslog_req = [[NSDate date] timeIntervalSince1970] - start;

    // summary
    NSLog(@"Test job of single thread: %d RPC doing echo(1)", cycle);
    NSLog(@"Total cost without logging: %f", cost_no_log);
    NSTimeInterval base = cost_no_log;
    NSTimeInterval overhead = cost_transport_log_only - cost_no_log;
    NSLog(@"Total cost with transport log without protocol log: %f, overhead: %f (%02f%%)", cost_transport_log_only, overhead, overhead*100/base);
    overhead = cost_protocol_log_only - cost_no_log;
    NSLog(@"Total cost without transport log with protocol log: %f, overhead: %f (%02f%%)", cost_protocol_log_only, overhead, overhead*100/base);
    overhead = cost_both_transport_protocol - cost_no_log;
    NSLog(@"Total cost with both transport and protocol log: %f, overhead: %f (%02f%%)", cost_both_transport_protocol, overhead, overhead*100/base);

    NSLog(@"Total cost of %d NSLog(\"@RPC response: %%@\", dict): %f", cycle, cost_nslog_dict);
    NSLog(@"Total cost of %d NSLog(\"@[sendData]: data to send: %%@\", dict): %f", cycle, cost_nslog_nsdata);
    NSLog(@"Total cost of %d NSLog(\"@RPC request: uuid: %%@, method: %%@, args: %%@, kwargs: %%@\", uuid, method, args, kwargs: %f", cycle, cost_nslog_req);

}

- (void)__testRPCProfile
{
    NSString * logFile = @"/vault/mix_rpc_client_framework_test.log";

    int num = 1;
    int cycle = 10000;

    freopen([logFile cStringUsingEncoding:NSASCIIStringEncoding], "w", stdout);
    freopen([logFile cStringUsingEncoding:NSASCIIStringEncoding], "w", stderr);

    NSMutableArray* clients = [NSMutableArray array];

    NSMutableArray* resultsNoLog = [NSMutableArray arrayWithCapacity:cycle];
    NSMutableArray* resultsOnlyTransportLog = [NSMutableArray arrayWithCapacity:cycle];
    NSMutableArray* resultsOnlyProtocolLog = [NSMutableArray arrayWithCapacity:cycle];
    NSMutableArray* resultsProtocolTransportLog = [NSMutableArray arrayWithCapacity:cycle];

    for (int i = 0; i < num; i++)
    {
        RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
        [clients addObject:client];
    }

    // create different rpc for different thread to run
    void (^rpc_int_x) (RPCClientWrapper* client, int cycle, int x, NSMutableArray* results) = ^(
                            RPCClientWrapper* client, int cycle, int x, NSMutableArray* results){
        id ret = nil;
        int i = 0;
        NSNumber* nx = [NSNumber numberWithInt:x];
        for (i = 0; i < cycle; i++)
        {
            NSTimeInterval start = [[NSDate date] timeIntervalSince1970];
            ret = [client rpc:@"driver.int1" args:@[nx] error:nil];
            XCTAssertTrue([ret isEqualToNumber:nx], @"Expecting %d from driver.int1(%d) but actually got: %@", x, x, ret);
            NSTimeInterval cost = [[NSDate date] timeIntervalSince1970] - start;
            [results addObject:[NSNumber numberWithFloat:cost*1000*1000]];
        }
        //NSLog(@"cost of %d RPC: %f", cycle, end - start);
    };

    RPCClientWrapper* single_client = [clients objectAtIndex:0];
    id <RPCTransport> t = single_client.transport;
    id <RPCProtocol> p = single_client.protocol;

    // get rid of initial threadpool thread creating overhead at server side.
    for (int i = 0; i < 20; i++)
    {
        [single_client rpc:@"driver.int1" args:@[@1] error:nil];
    }

    // no logging
    [t setIsLogging:false];
    [p setIsLogging:false];
    rpc_int_x(single_client, cycle, 1, resultsNoLog);

    // only transport log
    [t setIsLogging:true];
    [p setIsLogging:false];
    rpc_int_x(single_client, cycle, 1, resultsOnlyTransportLog);

    // only protocol log
    [t setIsLogging:false];
    [p setIsLogging:true];
    rpc_int_x(single_client, cycle, 1, resultsOnlyProtocolLog);

    // both protocol and transport log
    [t setIsLogging:true];
    [p setIsLogging:true];
    rpc_int_x(single_client, cycle, 1, resultsProtocolTransportLog);

    NSMutableArray* results = [NSMutableArray array];
    for (int i = 0; i < cycle; i++)
    {
        NSString* record = [NSString stringWithFormat:@"%d, %f, %f, %f, %f",
                                                        i,
                                                        [resultsNoLog[i] floatValue],
                                                        [resultsOnlyTransportLog[i] floatValue],
                                                        [resultsOnlyProtocolLog[i] floatValue],
                                                        [resultsProtocolTransportLog[i] floatValue]];
        [results addObject:record];
    }
    NSString* total = [results componentsJoinedByString:@"\n"];

    NSString * resultFile = @"/vault/mix_rpc_client_framework_profile.csv";
    [total writeToFile:resultFile atomically:false encoding:NSUTF8StringEncoding error:nil];
}

/*
 * test for only requesting endpoint as string.
 * dictionary endpoint is default way and is covered in all other cases.
 */
- (void)testStringEndpoint{
    NSString* STRING_ENDPOINT = @"tcp://127.0.0.1:5556";
    RPCClientWrapper* client = [RPCClientWrapper initWithStringEndpoint:STRING_ENDPOINT];

    NSString* expect = @"normal";
    NSString* ret = [client rpc:@"server.mode" error:nil];
    NSLog(@"server.mode rpc received:%@", ret);
    XCTAssertTrue([ret isEqualToString:expect], @"server response unexpected: %@, expecting to be %@", ret, expect);
}

/*
 * test for creating rpc client using dictionary.
 */
- (void)testClientCreationDictionary{
    NSDictionary *endpoint = @{
        @"requester": @"tcp://127.0.0.1:5556",
        @"receiver": @"tcp://127.0.0.1:15556"
    };

    RPCClientWrapper* client = [RPCClientWrapper initWithEndpoint:endpoint];

    NSString* expect = @"normal";
    NSError *err = nil;
    NSString* ret = [client rpc:@"server.mode" error:&err];
    XCTAssertNil(err);
    NSLog(@"server.mode rpc received:%@", ret);
    XCTAssertTrue([ret isEqualToString:expect], @"server response unexpected: %@, expecting to be %@", ret, expect);
}


/*
 * test for creating rpc client using ip and port.
 */
- (void)testClientCreationIPPort{
    NSString* ip = @"127.0.0.1";
    NSUInteger port = 5556;
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:ip withPort:port];

    NSString* expect = @"normal";
    NSString* ret = [client rpc:@"server.mode" error:nil];
    NSLog(@"server.mode rpc received:%@", ret);
    XCTAssertTrue([ret isEqualToString:expect], @"server response unexpected: %@, expecting to be %@", ret, expect);
}
/*
 * test for creating rpc client using ip and ports.
 */
- (void)testClientCreationReceiverPort{
    NSString* ip = @"127.0.0.1";
    NSUInteger port = 5556;
    NSUInteger receiverPort = 15556;
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:ip withPort:port withReceiverPort:receiverPort];

    NSString* expect = @"normal";
    NSString* ret = [client rpc:@"server.mode" error:nil];
    NSLog(@"server.mode rpc received:%@", ret);
    XCTAssertTrue([ret isEqualToString:expect], @"server response unexpected: %@, expecting to be %@", ret, expect);
}

- (void)testLoggingVariableFromInfoPlist {
    //Default setting: Logging is enabled.
    RPCClientWrapper* clientEnable = [RPCClientWrapper initWithIP:IP withPort:PORT];
    id <RPCTransport> t_enable = clientEnable.transport;
    id <RPCProtocol> p_enable = clientEnable.protocol;
    XCTAssertTrue(t_enable.isLogging);
    XCTAssertTrue(p_enable.isLogging);
    [clientEnable enableLogging:NO enableTransportLogging:NO];
    XCTAssertFalse(t_enable.isLogging);
    XCTAssertFalse(p_enable.isLogging);
}


/*
 * RPCClient wrapper support an instance method that support to be used as
 * RPCClientWrapper* client = [[RPCClientWrapper alloc] initializeWithIP:IP withPort:PORT];
 */
- (void)testInstanceInitMethod
{
    // valid server: network accessible, version above min-allowed version.
    RPCClientWrapper* clientToExistingServer = [[RPCClientWrapper alloc] initializeWithIP:IP withPort:@(PORT) error:nil];

    // valid server should return "normal".
    NSString* expect_mode = @"normal";
    NSString* mode = [clientToExistingServer rpc:@"server.mode" error:nil];
    XCTAssertTrue([mode isEqualToString:expect_mode], @"clientToExistingServer mode should be %@ while actually is %@", expect_mode, mode);
}

/*
 * ensure no crash when user call close explicitly.
 * by default, dealloc() will call shutdown() in case users does not call it; this is called by all other tests.
 * but when user call shutdown(), we need to ensure client won't crash when dealloc() call shutdown() again.
 */
- (void)testRPCClientShutdown{
    RPCClientWrapper* client = [RPCClientWrapper initWithIP:IP withPort:PORT];
    NSString* expect = @"normal";
    NSString* ret = [client rpc:@"server.mode" error:nil];
    NSLog(@"server.mode rpc received:%@", ret);
    XCTAssertTrue([ret isEqualToString:expect], @"server response unexpected: %@, expecting to be %@", ret, expect);
    [client shutdown];
}

- (void)testGetAndWriteLinuxBootLogToFile{
    RPCClientWrapper *client = [RPCClientWrapper initWithIP:@"127.0.0.1" withPort:5556];

    NSString* ret = [client rpc:@"server.mode"];
    NSLog(@"server.mode rpc received:%@", ret);
    
    NSFileManager* fm = [NSFileManager defaultManager];
    NSString* dstfile = [NSString stringWithFormat:@"syslog.tgz"];
    NSString* dstpath = [NSString pathWithComponents:@[NSHomeDirectory(), dstfile]];

    NSError *error = nil;
    [client getAndWriteLinuxBootLogToFile:dstpath withTimeoutInMS:10000 error:&error];
    XCTAssertNil(error);
    XCTAssertTrue([fm fileExistsAtPath:dstpath], @"File should be written to ~/");
    NSString* content = @"This is linux boot log for test";
    NSString* dstContent = [NSString stringWithContentsOfFile:dstpath encoding:NSUTF8StringEncoding error:nil];
    XCTAssertTrue([content isEqualToString:dstContent], @"File should be transfered to ~/");
    [fm removeItemAtPath:dstpath error:nil];
}
@end

