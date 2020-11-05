//
//  ErrorCode.h
//  FxitureController
//
//  Created by suncode on 2020/10/2.
//  Copyright © 2020年 suncode. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface ErrorCode : NSObject
{
    NSMutableDictionary * errorDic;
}
- (int)setErrorCode:(int)errorcode :(NSString *)msg;
- (const char *)getErrorMsg:(int)errorcode;
@end
