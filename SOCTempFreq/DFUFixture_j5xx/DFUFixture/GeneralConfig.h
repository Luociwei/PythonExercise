//
//  GeneralConfig.h
//  DFUFixture
//
//  Created by ben on 2019/2/12.
//  Copyright © 2019 Jackie wang. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface GeneralConfig : NSObject
{
#pragma mark - Member variables

}

#pragma mark - Getter/Setter

#pragma mark - Class methods, eg: + (void)demo:
+(GeneralConfig *) instance;

#pragma mark - Object methods, eg: - (void)demo:
-(NSString *) uartPath:(int)slot;

-(NSString *) mlbPath:(int)slot;

-(NSString *) locationID:(int)slot;

-(NSString*)macmini_hardware_version;

@end
