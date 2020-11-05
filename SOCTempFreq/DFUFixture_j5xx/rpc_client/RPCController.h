//
//  RPCController.h
//  DFUFixture
//
//  Created by RyanGao on 2020/10/6.
//  Copyright © 2020 RyanGao. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <mix_rpc_client_framework/mix_rpc_client_framework.h>

NS_ASSUME_NONNULL_BEGIN

@interface RPCController : NSObject
{
    NSMutableDictionary *ENDPOINT;
    NSMutableDictionary* NON_EXISTING_ENDPOINT;
    int m_status;
}
@property (atomic,retain) NSMutableArray *m_Clients;

- (instancetype)initWithSlots:(int)slots withAddr:(NSArray *)devAddrArr;
-(NSString *)WriteReadString:(NSString *)cmd atSite:(int)site timeOut:(int)timeout;
-(int)Close;
-(int)getCylinderStatus:(NSString *)cmd;
-(void)uartShutdown:(int)site;

- (NSString*)getHostModel;
-(NSString*)usb_locationID:(int)index;
- (NSString *)uartPath:(int)index;

@end

NS_ASSUME_NONNULL_END
