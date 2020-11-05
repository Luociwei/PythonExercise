//
//  GeneralConfig.m
//  DFUFixture
//
//  Created by ben on 2019/2/12.
//  Copyright © 2019 Jackie wang. All rights reserved.
//

#import "GeneralConfig.h"

@interface GeneralConfig ()
{
# pragma mark - Invisible variables
    NSDictionary *_generateData;
}

@end

@implementation GeneralConfig

+(GeneralConfig *) instance {
    static GeneralConfig *_instance;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        _instance = [[GeneralConfig alloc] init];
    });
    
    return _instance;
}

-(instancetype) init
{
    self = [super init];
    if (self) {
        [self loadProfile];
    }
    return self;
}

- (void)loadProfile {
    NSString *path=@"/Users/gdlocal/Library/Atlas/supportFiles/GeneralConfig.json";
//    NSString *path = [[NSBundle mainBundle] pathForResource:@"GeneralConfig.json" ofType:nil];
    NSData *data = [NSData dataWithContentsOfFile:path];
    if (!data) { return; }
    
    _generateData = [NSJSONSerialization JSONObjectWithData:data
                                                   options:NSJSONReadingAllowFragments error:nil];
}

-(NSString *) uartPath:(int)slot {
    NSString *_path;
    @synchronized (@"reading") {
//        NSInteger selectedIndex = [[_generateData objectForKey:@"SelectedFixture"] intValue];
        NSArray *arr = [_generateData objectForKey:@"Fixture List"][0];
        NSDictionary *slotDic = [arr objectAtIndex:slot-1];
        NSArray *mlbArr = slotDic[@"MLB"];
//        NSArray *uartArr = mlbDic[@"UART"];
//        NSArray *xavierArr = mlbDic[@"XAVIER"];
        _path = [mlbArr objectAtIndex:0];
    }
    
    return _path;
}

-(NSString *) mlbPath:(int)slot {
    NSString *_path;
    @synchronized (@"reading") {
        //        NSInteger selectedIndex = [[_generateData objectForKey:@"SelectedFixture"] intValue];
        NSArray *arr = [_generateData objectForKey:@"Fixture List"][0];
        NSDictionary *slotDic = [arr objectAtIndex:slot-1];
        NSArray *mcuArr = slotDic[@"MCU"];
        _path = [mcuArr objectAtIndex:0];
    }
    
    return _path;
}

-(NSString*)macmini_hardware_version
{
    
    NSTask *task = [[NSTask alloc] init];
    [task setLaunchPath:@"/bin/sh"];
    NSString* cmd = [NSString stringWithFormat:@"system_profiler SPHardwareDataType"]; // if you want to find usb port name ,prelikestring = cu.usb*
    
    NSArray* arguments = [NSArray arrayWithObjects:@"-c" ,cmd , nil];
    [task setArguments:arguments];
    
    NSPipe* pipe = [NSPipe pipe];
    [task setStandardOutput:pipe];
    
    NSFileHandle* file = [pipe fileHandleForReading];
    [task launch];
    [task waitUntilExit];
    NSString* hardware_info = [[NSString alloc] initWithData:[file readDataToEndOfFile] encoding:NSUTF8StringEncoding];
    
    NSRegularExpression *regex = [[NSRegularExpression alloc] initWithPattern:@"Model Identifier:\\s+(\\w+,\\w+)" options:0 error:nil];
    NSTextCheckingResult *ckResult = [regex firstMatchInString:hardware_info options:0 range:NSMakeRange(0, hardware_info.length)];
    NSString* macmini_v = @"Macmini7,1";
    if (ckResult.range.location != NSNotFound)
    {
        macmini_v = [hardware_info substringWithRange:[ckResult rangeAtIndex:ckResult.numberOfRanges - 1]];
    }
    
    return macmini_v;
}

-(NSString *)locationID:(int)slot {
    NSString *_path;
    @synchronized (@"reading") {
        //        NSInteger selectedIndex = [[_generateData objectForKey:@"SelectedFixture"] intValue];
        NSArray *arr = [_generateData objectForKey:@"Fixture List"][0];
        NSDictionary *slotDic = [arr objectAtIndex:slot-1];
        NSDictionary *dcsdDic = slotDic[@"DCSD"];
        _path = [dcsdDic objectForKey:[self macmini_hardware_version]][0];
    }
    
    return _path;
}

@end
