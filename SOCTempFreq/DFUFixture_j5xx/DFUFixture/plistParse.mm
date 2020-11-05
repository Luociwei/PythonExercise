#import "plistParse.h"

@implementation plistParse

+(NSDictionary*)parsePlist:(NSString *)file
{
    if(!file)
        file = @"/usr/local/lib/DFUFixtureCmd.plist";
    NSDictionary * dic = [NSDictionary dictionaryWithContentsOfFile:file];
    return dic;
}

+(NSDictionary *)readAllCMD
{
    NSString *file=@"/Users/gdlocal/Library/Atlas/supportFiles/DFUFixtureCmd.plist";
    NSFileManager *fileManager = [NSFileManager defaultManager];
    if ([fileManager fileExistsAtPath:file])
    {
        NSDictionary * dic = [NSDictionary dictionaryWithContentsOfFile:file];
        NSLog(@"-->file exist at path:%@",file);
        return dic;
    }
    else
    {
        NSDictionary *dic=@{
                            kFIXTUREPORT:@{
                                    @"UUT0":@"169.254.1.32:7801",
                                    @"UUT1":@"169.254.1.32:7802",
                                    @"UUT2":@"169.254.1.32:7803",
                                    @"UUT3":@"169.254.1.32:7804"
                                    },
                            
                            kFIXTURESLOTS:@"4",
 
                            kFIXTUREOPEN:@[@"fixturecontrol_release()"],
                            kFIXTURECLOSE:@[@"fixturecontrol_press()"],
                            kFIXTURESTATUS:@"fixturecontrol_get_fixture_status()",
                            
                            kAPPLEIDOFF:@[@""],
                            kAPPLEIDON:@[@""],
                            
                            kBATTERYPOWEROFF:@[@""],
                            kBATTERYPOWERON:@[@""],
                            
                            kCONNDETGNDOFF:@[@""],
                            kCONNDETGNDON:@[@""],
                            
                            kDUTPOWEROFF:@[@"io_set(bit14=0;bit22=0;bit40=0,bit31=1)"],//1023 David add bit30=1 to discharge vbus
                            
                            kDUTPOWERON:@[@""],
                            
                            kFORCEDFUOFF:@[@"reset_all_reset()"],
                            
                            kFORCEDFUON:@[@"batt_volt_set(4200))",
                                          @"Delay:0.2",
                                          @"reset_all_reset()",
                                          @"io_set(bit16=1;bit17=1;bit39=1;bit40=1;bit12=1;bit35=1;bit36=0;bit31=0;bit22=1;bit14=1)"],   // force dfu on
                                                      
                            kFORCEDIAGSOFF:@[@"reset_all_reset()"],
                            
                            kFORCEDIAGSON:@[@"batt_volt_set(4200)",
                                            @"Delay:0.2",
                                            @"reset_all_reset()",
                                            @"io_set(bit39=1;bit36=0;bit31=0;bit24=1;bit40=1;bit16=1;bit17=1;bit22=1;bit14=1)"],   //force diags on  1023 david change bit31 from 1 to 0 and change bit36=0
                            
                            kFORCEIBOOTOFF:@[@""],
                            kFORCEIBOOTON:@[@""],
                            
                            kHI5OFF:@[@""],
                            kHI5ON:@[@""],
                            
                            kINIT:@[@"io_set(bit24=1)",
                                    @"Delay:0.5",
                                    @"reset_all_reset()",
                                    @"io_set(bit27=1;bit28=1)",
                                    @"fan_speed_set(4000,100"],
                            
                            kLEDSTATE:@{kFAIL:@[@"",
                                                @""],
                                        
                                        kFAILGOTOFA:@[@"",
                                                      @""],
                                        
                                        kINPROCESS:@[@"",
                                                     @""],
                                        
                                        kOFF:@[@"",
                                               @""],
                                        
                                        kPANIC:@[@"",
                                                 @""],
                                        
                                        kPASS:@[@"",
                                                @""]},
                            
                            kRESET:@[@"io_set(bit24=1)",
                                     @"Delay:0.5",
                                     @"reset_all_reset()",
                                     @"io_set(bit27=1;bit28=1)"],
                            
                            kFIXTUREFANSPEEDSETIO:@"io_set(bit27=1)",
                            kFIXTUREFANSPEEDSET:@"fan_speed_set",
                            
                            kFIXTUREFANSPEEDGETIO:@"io_set(bit28=1)",
                            kFIXTUREFANSPEEDGET:@"fan_speed_get",
                            
                            kFIXTUREUUTDETECT:@"uut_detect_read_Volt",
                            
                            kLED_POWEROFF:  @"io_set(bit49=1;bit50=1;bit51=1)",
                            kLED_POWERRED:  @"io_set(bit49=0;bit50=1;bit51=1)",
                            kLED_POWERGREEN:@"io_set(bit49=1;bit50=0;bit51=1)",
                            kLED_POWERBLUE: @"io_set(bit49=1;bit50=1;bit51=0)",
                            
                            kLED_UUT1OFF  : @"io_set(bit52=1;bit53=1;bit54=1)",  //off
                            kLED_UUT1RED  : @"io_set(bit52=0;bit53=1;bit54=1)",  //red
                            kLED_UUT1GREEN: @"io_set(bit52=1;bit53=0;bit54=1)",  //green
                            kLED_UUT1BLUE : @"io_set(bit52=1;bit53=1;bit54=0)",  //blue
                            
                            kLED_UUT2OFF  :@"io_set(bit55=1;bit56=1;bit57=1)",  //off
                            kLED_UUT2RED  :@"io_set(bit55=0;bit56=1;bit57=1)",  //red
                            kLED_UUT2GREEN:@"io_set(bit55=1;bit56=0;bit57=1)",  //green
                            kLED_UUT2BLUE :@"io_set(bit55=1;bit56=1;bit57=0)",  //blue
                            
                            kLED_UUT3OFF  :@"io_set(bit65=1;bit66=1;bit67=1)",  //off
                            kLED_UUT3RED  :@"io_set(bit65=0;bit66=1;bit67=1)",  //red
                            kLED_UUT3GREEN:@"io_set(bit65=1;bit66=0;bit67=1)",  //green
                            kLED_UUT3BLUE :@"io_set(bit65=1;bit66=1;bit67=0)",  //blue
                            
                            kLED_UUT4OFF  :@"io_set(bit68=1;bit69=1;bit70=1)",  // off
                            kLED_UUT4RED  :@"io_set(bit68=0;bit69=1;bit70=1)",  // red
                            kLED_UUT4GREEN:@"io_set(bit68=1;bit69=0;bit70=1)",  // green
                            kLED_UUT4BLUE :@"io_set(bit68=1;bit69=1;bit70=0)",  // blue
                            
                            kSERIAL:@"TBD",
                            
                            kUARTPATH:@{@"UUT0":@"",  //not use kUARTPATH, using auto detecting
                                        @"UUT1":@""},
                            
                            kUARTSIGNALOFF:@[@""],
                            kUARTSIGNALON:@[@""],
                            
                            kUSBLOCATION:@{@"UUT0":@"",   //not use
                                           @"UUT1":@"",
                                           @"UUT2":@"",
                                           @"UUT3":@"",
                                           @"UUT4":@"",
                                           @"UUT5":@"",
                                           @"UUT6":@"",
                                           @"UUT7":@""},
                            
                            kUSBPOWEROFF:@[@""],
                            
                            kUSBPOWERON:@[@""],
                            
                            kUSBSIGNALOFF:@[@""],
                            kUSBSIGNALON:@[@""],
                            
                            kVENDER:@"SunCode",
                            kVERSION:@"1.0"  //
                            };
        
        NSLog(@"-->file not exist at path:%@",file);
        return dic;
    }
}


+(void)checkLogFileExist:(NSString *)filePath
{
    NSFileManager *fm = [NSFileManager defaultManager];
    NSError *error = nil;
    BOOL isExist = [fm fileExistsAtPath:filePath];
    if (!isExist)
    {
        BOOL ret = [fm createFileAtPath:filePath contents:nil attributes:nil];
        if (ret)
        {
            NSLog(@"create file is successful");
        }
        else
        {
            [fm createDirectoryAtPath:@"/vault/Atlas/FixtureLog/SunCode/" withIntermediateDirectories:YES attributes:nil error:&error];
            [fm createFileAtPath:filePath contents:nil attributes:nil];
            NSLog(@"create folder and file is successful");
        }
    }
    else
    {
        NSLog(@"file already exit");
    }
}


+(void)writeLog2File:(NSString *)filePath withTime:(NSString *) testTime andContent:(NSString *)str
{
    NSFileHandle* fh=[NSFileHandle fileHandleForWritingAtPath:filePath];
    [fh seekToEndOfFile];
    [fh writeData:[[NSString stringWithFormat:@"%@  %@\r\n",testTime,str] dataUsingEncoding:NSUTF8StringEncoding]];
    [fh closeFile];
}


@end
