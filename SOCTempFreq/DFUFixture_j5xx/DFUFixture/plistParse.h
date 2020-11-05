//
//  plistParse.h
//  DFUFixture
//
//  Created by RyanGao on 2020/10/02.
//  Copyright © 2020年 RyanGao. All rights reserved.
//


#import <Foundation/Foundation.h>

#define kVENDER                 @"vender"
#define kSERIAL                 @"serial_number"
#define kVERSION                @"version"

#define kINIT                   @"init"
#define kRESET                  @"reset"
#define kUSBLOCATION            @"usb_location"
#define kUARTPATH               @"uart_path"
#define kUSBPOWERON             @"usb_power_on"
#define kUSBPOWEROFF            @"usb_power_off"
#define kBATTERYPOWERON         @"battery_power_on"
#define kBATTERYPOWEROFF        @"battery_power_off"
#define kUSBSIGNALON            @"usb_signal_on"
#define kUSBSIGNALOFF           @"usb_signal_off"
#define kUARTSIGNALON           @"uart_signal_on"
#define kUARTSIGNALOFF          @"uart_signal_off"
#define kAPPLEIDON              @"apple_id_on"
#define kAPPLEIDOFF             @"apple_id_off"
#define kCONNDETGNDON           @"conn_det_grounded_on"
#define kCONNDETGNDOFF          @"conn_det_grounded_off"
#define kHI5ON                  @"hi5_bs_grounded_on"
#define kHI5OFF                 @"hi5_bs_grounded_off"
#define kDUTPOWERON             @"dut_power_on"
#define kDUTPOWEROFF            @"dut_power_off"
#define kFORCEDFUON             @"force_dfu_on"
#define kFORCEDFUOFF            @"force_dfu_off"
#define kFORCEDIAGSON           @"force_diags_on"
#define kFORCEDIAGSOFF          @"force_diags_off"
#define kFORCEIBOOTON           @"force_iboot_on"
#define kFORCEIBOOTOFF          @"force_iboot_off"

#define kLEDSTATE               @"led_state"
#define kOFF                    @"off"
#define kPASS                   @"pass"
#define kFAIL                   @"fail"
#define kINPROCESS              @"inprocess"
#define kFAILGOTOFA             @"fail_goto_fa"
#define kPANIC                  @"panic"

#define kLED_POWEROFF           @"power_led_off"
#define kLED_POWERRED           @"power_led_red"
#define kLED_POWERGREEN         @"power_led_green"
#define kLED_POWERBLUE          @"power_led_blue"

#define kLED_UUT1OFF            @"uut1_led_off"
#define kLED_UUT1RED            @"uut1_led_red"
#define kLED_UUT1GREEN          @"uut1_led_green"
#define kLED_UUT1BLUE           @"uut1_led_blue"

#define kLED_UUT2OFF            @"uut2_led_off"
#define kLED_UUT2RED            @"uut2_led_red"
#define kLED_UUT2GREEN          @"uut2_led_green"
#define kLED_UUT2BLUE           @"uut2_led_blue"

#define kLED_UUT3OFF            @"uut3_led_off"
#define kLED_UUT3RED            @"uut3_led_red"
#define kLED_UUT3GREEN          @"uut3_led_green"
#define kLED_UUT3BLUE           @"uut3_led_blue"

#define kLED_UUT4OFF            @"uut4_led_off"
#define kLED_UUT4RED            @"uut4_led_red"
#define kLED_UUT4GREEN          @"uut4_led_green"
#define kLED_UUT4BLUE           @"uut4_led_blue"

#define kFIXTURESETTING         @"Fixture_Control_Setting"
#define kFIXTUREPORT            @"Fixture_Control_Port"
#define kFIXTURESLOTS           @"Fixture_Slots"
#define kFIXTUREOPEN            @"Fixture_Open"
#define kFIXTURECLOSE           @"Fixture_Close"
#define kFIXTURESTATUS          @"Fixture_Status"

#define kFIXTUREFANSPEEDSETIO   @"Fixture_Fan_Speed_Set_IO"
#define kFIXTUREFANSPEEDSET     @"Fixture_Fan_Speed_Set"
#define kFIXTUREFANSPEEDGETIO   @"Fixture_Fan_Speed_Get_IO"
#define kFIXTUREFANSPEEDGET     @"Fixture_Fan_Speed_Get"

#define kFIXTUREUUTDETECT       @"Fixture_UUT_Detect"

#define kUSBLocationPID         @"0x8"
#define kUSBLocationVID         @"0x2E13"

#define KBladeMCUName           @"FT232R USB UART"
#define KCarrierMCUName         @"Quad RS232-HS"



@interface plistParse : NSObject

+(NSDictionary*)parsePlist:(NSString *)file;
+(NSDictionary *)readAllCMD;
+(void)checkLogFileExist:(NSString *)filePath;
+(void)writeLog2File:(NSString *)filePath withTime:(NSString *) testTime andContent:(NSString *)str;

@end
