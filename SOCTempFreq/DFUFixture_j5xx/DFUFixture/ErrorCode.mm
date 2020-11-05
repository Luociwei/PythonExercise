//
//  ErrorCode.h
//  FxitureController
//
//  Created by suncode on 2020/10/2.
//  Copyright © 2020年 suncode. All rights reserved.
//

#import "ErrorCode.h"
/*
 -1000 : ZMQ no response
 
 */
NSString * msg = @"0&Success@\
-1&invalide Index";

ErrorCode * g_errcode;
NSString * t = @"trw\
ahaha";

@implementation ErrorCode

- (id)init
{
    self = [super init];
    errorDic = [[NSMutableDictionary alloc]init];
    NSArray * arr = [msg componentsSeparatedByString:@"@"];
    for(int i=0; i<[arr count]; i++)
    {
        NSArray * t = [[arr objectAtIndex:i ]componentsSeparatedByString:@"&"];
        [errorDic setObject:[t objectAtIndex:1] forKey:[t objectAtIndex:0]];
    }
    return self;
}

- (void)dealloc
{
    [errorDic removeAllObjects];
    //[errorDic release];
    //[super dealloc];
}

- (const char *)getErrorMsg:(int)errorcode
{
    NSString * str = [errorDic valueForKey:[NSString stringWithFormat:@"%d",errorcode]];
    if(str)
        return [str UTF8String];
    else
        return "Unknow Error Code";
}

- (int)setErrorCode:(int)errorcode :(NSString *)msg
{
    [errorDic setObject:msg forKey:[NSString stringWithFormat:@"%d",errorcode]];
    return 0;
}

@end
