//
//  DFUFixture.m
//  DFUFixture
//
//  Created by RyanGao on 2020/10/02.
//  Copyright © 2020年 RyanGao. All rights reserved.
//


#import <Foundation/Foundation.h>
#import "plistParse.h"
#import "USBDevice.h"
#import "DFUFixture.h"
#import "RPCController.h"


int g_SLOTS = 0;
BOOL g_out_flag  = NO;
BOOL g_auto_flag = YES;
dispatch_queue_t g_queue = NULL;

NSMutableDictionary * cmd = NULL;
void* event_ctx_p = NULL;
fixture_event_callback_t on_fixture_event_fp = NULL;
stop_event_notfication_callback_t on_stop_event_notification_fp = NULL;

void writeFixtureLog(NSString *strContent)
{
//    dispatch_queue_t quene = dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0);
//    dispatch_async(quene, ^{
     @synchronized (@"com.writeFixtureLog.lock")
    {
        NSDateFormatter* DateFomatter = [[NSDateFormatter alloc] init];
        [DateFomatter setDateFormat:@"yyyy/MM/dd HH:mm:ss.SSS "];
        NSString* timeFlag = [DateFomatter stringFromDate:[NSDate date]];
        [DateFomatter setDateFormat:@"yyyy_MM_dd"];
        NSString* timeFilenName = [DateFomatter stringFromDate:[NSDate date]];
       // [DateFomatter release];
        NSString *pathLogFile=[NSString stringWithFormat:@"/vault/Atlas/FixtureLog/SunCode/SCFixture_Command_%@.txt",timeFilenName];
        [plistParse checkLogFileExist:pathLogFile];
        [plistParse writeLog2File:pathLogFile withTime:timeFlag andContent:strContent];
    }
}

void create_global_object(RPCController* controller)
{
    
    if (!g_queue)
    {
        g_queue = dispatch_queue_create("com.DFUFixture.global_queue", DISPATCH_QUEUE_SERIAL);
        writeFixtureLog(@"create_global_object: g_queue");
    }
}

void* create_fixture_controller(int index)
{
    if(cmd)
    {
        [cmd removeAllObjects];
    }
    else
    {
        cmd = [[NSMutableDictionary alloc]init];
    }
    [cmd setDictionary:[plistParse readAllCMD]];
    if([cmd count]>0)
    {
        g_SLOTS = [[cmd objectForKey:kFIXTURESLOTS]intValue];
    }
    if (g_SLOTS<1)
    {
        return nil;
    }
    NSMutableArray *ipPorts = [NSMutableArray array];
    for (int i=0; i<g_SLOTS; i++)
    {
        NSString * ipPort = [[cmd objectForKey:kFIXTUREPORT] objectForKey:[NSString stringWithFormat:@"UUT%d",i]];
        [ipPorts addObject:ipPort];
    }
    writeFixtureLog([NSString stringWithFormat:@"create_fixture_controller , ip: %@, index : %d\r\n",ipPorts,index]);
    RPCController *controller = [[RPCController alloc] initWithSlots:g_SLOTS withAddr:ipPorts];
    create_global_object(controller);
    return (__bridge_retained void *)controller;
}

void release_fixture_controller(void* controller)
{
    if(cmd)
    {
        [cmd removeAllObjects];
    }
    RPCController *fixture = (__bridge RPCController *)controller;
    if (on_stop_event_notification_fp != NULL) {
        on_stop_event_notification_fp(event_ctx_p);
    }
    [fixture Close];
    event_ctx_p = NULL;
    on_fixture_event_fp = NULL;
    on_stop_event_notification_fp = NULL;
    
    writeFixtureLog(@"release_fixture_controller %d\r\n");
}


/////////////////////////////////////////////////////

int executeAction(void *controller,NSString * key, int site)
{
    if(site<1)
        return -1;

    RPCController *fixture = (__bridge RPCController *)controller;
    id list = [cmd objectForKey:key];
    if ([list isEqual:@[@""]] || [list isEqual:@""] || list == NULL)
    {
        return 0;
    }
    NSArray * arr = [cmd objectForKey:key];
    for (int j=0; j<[arr count]; j++)
    {
        if ([[[arr objectAtIndex:j]uppercaseString] containsString:@"DELAY:"])
        {
            NSArray *arryDelay=[[arr objectAtIndex:j] componentsSeparatedByString:@":"];
             if ([[arryDelay[0] uppercaseString] isEqual:@"DELAY"])
             {
                 [NSThread sleepForTimeInterval:[arryDelay[1] doubleValue]];
             }
        }
        else
        {
            NSString *ret = [fixture WriteReadString:[arr objectAtIndex:j] atSite:site-1 timeOut:6000];
            if (j==[arr count]-1)
            {
                writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@\r\n",[arr objectAtIndex:j],ret]);
            }
            else
            {
                writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@",[arr objectAtIndex:j],ret]);
            }
            
        }
        
    }
    return 0;
}


int executeAllAction(void *controller,NSString * key)
{
    for (int i=0; i<4; i++)
    {
        executeAction(controller,key, i+1);
    }
    return 0;
}
///////////////////////////////////////////////////////
///////////////////////////////////////////////////////

const char * const get_vendor()
{
    id obj = [cmd objectForKey:kVENDER];
    if(obj)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_vendor : %@\r\n",obj]);
        return [obj UTF8String];
    }
    else
    {
        writeFixtureLog(@"get_vendor : SunCode\r\n");
        return "SunCode";
    }
}

int get_vendor_id(void)
{
    writeFixtureLog([NSString stringWithFormat:@"get_vendor_id, %d\r\n",4]);
    return 4;
}

const char * const get_serial_number(void* controller)
{
    writeFixtureLog([NSString stringWithFormat:@"get_serial_number : SC 20200813LH-100047 \r\n"]);
    return "SC 20200813LH-100047";
}

const char * const get_carrier_serial_number(void* controller, int site)
{
    if(site<1)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number, site : %d \r\n",site]);
        return "-1";
    }
    
    writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number, 20201006 , site : %d\r\n",site]);
    return "20201006";
    
}

const char* const get_error_message(int status)
{
    writeFixtureLog([NSString stringWithFormat:@"get_error_message, status : %d \r\n",status]);
    switch (status) {
        case 0:
            return "Successful";
        case (-1):
            return "No exist serial port.";
        case (-2):
            return "Failed to open serial port.";
        case (-3):
            return "Communication timeout.";
        case (-4):
            return "Invalid command.";
        case (-5):
            return "Failed to execute command.";
        case (-101):
            return "No implementate this function.";
        case (-6):
            return "Failed to init controller.";
        case (-7):
            return "Failed to reset controller.";
        default:
            return "Unexcepted error.";
            break;
    }
    return "Unexcepted error.";

}

const char* const get_version(void* controller)
{
    id obj = [cmd objectForKey:kVERSION];
    if(obj)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_version : %@ .\r\n",obj]);
        return [obj UTF8String];
    }
    else
    {
        writeFixtureLog([NSString stringWithFormat:@"get_version : 0.1 .\r\n"]);
        return "Lib_v1.0_XavierFW_1.0.0";
    }
    
}

int init(void* controller)
{
    writeFixtureLog(@"fixture_open");
    executeAction(controller,kFIXTUREOPEN, 1);
    g_out_flag = YES;
    writeFixtureLog(@"init");
    return executeAllAction(controller,kINIT);
}

int reset(void* controller)
{
    writeFixtureLog(@"reset");
    return executeAllAction(controller,kRESET);
}

int resetChannel(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"resetChannel, site: %d\r\n",site]);
    return executeAction(controller, kRESET, site);
}

int get_site_count(void* controller)
{
    writeFixtureLog([NSString stringWithFormat:@"get_site_count : %d .r\n",g_SLOTS]);
    return g_SLOTS;
}

int get_actuator_count(void* controller)
{
    writeFixtureLog([NSString stringWithFormat:@"get_actuator_count : %d \r\n",g_SLOTS]);
    return g_SLOTS;
}

const char* get_usb_location(void* controller, int site)
{
    if (site<1)
    {
        writeFixtureLog(@"get_usb_location: error\r\n");
        return "error";
    }
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString *locationid = [fixture usb_locationID:site];
    writeFixtureLog([NSString stringWithFormat:@"get_usb_location, site : %d , result: %@\r\n",site,locationid]);
    return [locationid UTF8String];
}

const char * const get_unit_location(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"get_unit_location : %d \r\n",site]);
    return [[NSString stringWithFormat:@"slot-%i\n",site] UTF8String];
}

const char* get_uart_path(void* controller, int site)
{
    if(site<1)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_uart_path : site should be from 1 , site : %d\r\n",site]);
        return "site should be from 1";
    }
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString *uartPath = [fixture uartPath:site];
    writeFixtureLog([NSString stringWithFormat:@"get_uart_path, site : %d, path: %@\r\n",site,uartPath]);
    return [uartPath UTF8String];
    
}


int actuator_for_site(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"actuator_for_site, site : %d\r\n",site]);
    if(site<1)
    {
        return -1;
    }
    return site-1;
}

int fixture_engage(void* controller, int actuator_index)
{
    if(actuator_index<0)
    {
        writeFixtureLog([NSString stringWithFormat:@"fixture_engage : -1 , actuator_index : %d \r\n",actuator_index]);
        return -1;
    }
    writeFixtureLog([NSString stringWithFormat:@"fixture_engage : 0 , actuator_index : %d\r\n",actuator_index]);
    return 0;
}

int fixture_disengage(void* controller, int actuator_index)
{
    if(actuator_index<0)
    {
        writeFixtureLog([NSString stringWithFormat:@"fixture_disengage : -1 , actuator_index : %d\r\n ",actuator_index]);
        return -1;
    }
    writeFixtureLog([NSString stringWithFormat:@"fixture_disengage : 0 , actuator_index : %d\r\n ",actuator_index]);
    return 0;
}

int fixture_open(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"fixture_open, actuator_index: %d",actuator_index]);
    g_out_flag = YES;
    return executeAction(controller,kFIXTUREOPEN, 1);
    
}

int fixture_close(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"fixture_close, actuator_index: %d",actuator_index]);
    RPCController *fixture = (__bridge RPCController *)controller;
    create_global_object(fixture);
    return executeAction(controller,kFIXTURECLOSE, 1);
}


int set_usb_power(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_usb_power, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kUSBPOWERON : kUSBPOWEROFF),site);
}

int set_battery_power(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_battery_power, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kBATTERYPOWERON : kBATTERYPOWEROFF),site);
}

int set_usb_signal(void* controller, RELAY_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_usb_signal, RELAY_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kUSBSIGNALON : kUSBSIGNALOFF),site);
}

int set_uart_signal(void* controller, RELAY_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_uart_signal, RELAY_STATE: %d, site: %d",action,site]);
    return 0;
}

int set_apple_id(void* controller, RELAY_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_apple_id, RELAY_STATE: %d, site: %d",action,site]);
    return 0;
}

int set_conn_det_grounded(void* controller, RELAY_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_conn_det_grounded, RELAY_STATE: %d, site: %d",action,site]);
    return 0;
}

int set_hi5_bs_grounded(void* controller, RELAY_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_hi5_bs_grounded, RELAY_STATE: %d, site: %d",action,site]);
    return 0;
}

int set_dut_power(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_dut_power, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kDUTPOWERON : kDUTPOWEROFF),site);
}

int set_dut_power_all(void* controller, POWER_STATE action)
{
    writeFixtureLog([NSString stringWithFormat:@"set_dut_power_all, POWER_STATE: %d",action]);
    return executeAllAction(controller,(action==0 ? kDUTPOWERON : kDUTPOWEROFF));
}

int set_force_dfu(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_force_dfu, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kFORCEDFUON : kFORCEDFUOFF), site);
}

int set_force_diags(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_force_diags, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kFORCEDIAGSON : kFORCEDIAGSOFF), site);
}

int set_force_iboot(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_force_iboot, POWER_STATE: %d, site: %d",action,site]);
    return executeAction(controller,(action==0 ? kFORCEIBOOTON : kFORCEIBOOTOFF), site);
}

int set_led_state(void* controller, LED_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_led_state, LED_STATE: %d, site : %d",action, site]);
    if (site<1)
    {
        return -1;
    }
    NSString *ledCmd = @"";
    switch (action)
    {
            case 0: // OFF
            {
                NSString *ledKey = [NSString stringWithFormat:@"uut%d_led_off",site];
                ledCmd = [cmd objectForKey:ledKey];
                break;
            }
            case 1: // PASS
            {
                NSString *ledKey = [NSString stringWithFormat:@"uut%d_led_green",site];
                ledCmd = [cmd objectForKey:ledKey];
                break;
            }
            case 2: // FAIL
            {
                NSString *ledKey = [NSString stringWithFormat:@"uut%d_led_red",site];
                ledCmd = [cmd objectForKey:ledKey];
                break;
            }
            case 3: // progress
            {
                NSString *ledKey = [NSString stringWithFormat:@"uut%d_led_blue",site];
                ledCmd = [cmd objectForKey:ledKey];
                break;
            }
            default:    // other  off
            {
                break;
            }
    }
    RPCController *fixture = (__bridge RPCController *)controller;
    if ([ledCmd length]>0)
    {
        NSString *ret = [fixture WriteReadString:ledCmd atSite:site-1 timeOut:5000];
        writeFixtureLog([NSString stringWithFormat:@"[cmd]%@, [result] : %@\r\n",ledCmd, ret]);
    }
    return 0;
}
int set_led_state_all(void* controller, LED_STATE action)
{
    writeFixtureLog([NSString stringWithFormat:@"set_led_state_all, LED_STATE: %d",action]);
    for (int i=0; i<g_SLOTS; i++) {
        set_led_state(controller, action, i+1);
    }
    return 0;
}

//************* section:status functions *******************
//when the actuator is in motion and not yet settled, neither is_engage nor is_disengage should return true
bool is_fixture_engaged(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_engaged : YES , actuator_index : %d \r\n",actuator_index]);
    return YES;
}

bool is_fixture_disengaged(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_disengaged : YES , actuator_index : %d \r\n",actuator_index]);
    return YES;
}

bool is_fixture_closed(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_closed : YES , actuator_index : %d \r\n",actuator_index]);
    return YES;
}

bool is_fixture_open(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_open : YES , actuator_index : %d \r\n",actuator_index]);
    return YES;
}

POWER_STATE usb_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"usb_power : TURN_ON , site : %d \r\n",site]);
    return TURN_ON;
}
POWER_STATE battery_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"battery_power : TURN_ON , site : %d \r\n",site]);
    return TURN_ON;
}

POWER_STATE force_dfu(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"force_dfu : TURN_ON , site : %d \r\n",site]);
    return TURN_ON;
}

RELAY_STATE usb_signal(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"usb_signal : OPEN_RELAY , site : %d \r\n",site]);
    return OPEN_RELAY;
}

RELAY_STATE uart_signal(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"uart_signal : OPEN_RELAY , site : %d \r\n",site]);
    return OPEN_RELAY;
}

RELAY_STATE apple_id(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"apple_id : OPEN_RELAY , site : %d \r\n",site]);
    return OPEN_RELAY;
}

RELAY_STATE conn_det_grounded(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"conn_det_grounded : OPEN_RELAY , site : %d \r\n",site]);
    return OPEN_RELAY;
}

RELAY_STATE hi5_bs_grounded(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"hi5_bs_grounded : OPEN_RELAY , site : %d \r\n",site]);
    return OPEN_RELAY;
}

POWER_STATE dut_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"dut_power : TURN_ON ,site : %d \r\n",site]);
    return TURN_ON;
}

bool is_board_detected(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"is_board_detected, site: %d",site]);
    if(site<1)
        return -1;
    
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString  *detectcmd =[NSString stringWithFormat:@"%@(%d)",[cmd objectForKey:kFIXTUREUUTDETECT],site];
    NSString *ret = [fixture WriteReadString:detectcmd atSite:site-1 timeOut:3000];
    
    if([ret intValue]==0)
    {
        writeFixtureLog([NSString stringWithFormat:@"is_board_detected , site : %d, [result] %@\r\n",site,@"YES"]);
        return YES;
    }
    else
    {
        writeFixtureLog([NSString stringWithFormat:@"is_board_detected , site : %d, [result] %@\r\n",site,@"NO"]);
        return NO;
    }
    
}

int set_fan_speed(void* controller, int fan_speed, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_fan_speed, fan_speed: %d, site: %d",fan_speed,site]);
    if(site<1)
        return -1;
    if (fan_speed > 100) { fan_speed = 100; }
    if (fan_speed < 0) { fan_speed = 0; }
    
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString  *fancmdIO = [cmd objectForKey:kFIXTUREFANSPEEDSETIO];
    NSString *ret = [fixture WriteReadString:fancmdIO atSite:site-1 timeOut:3000];
    writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@",fancmdIO,ret]);
    NSString *fancmd = [NSString stringWithFormat:@"%@(4000,%d)",[cmd objectForKey:kFIXTUREFANSPEEDSET],100-fan_speed];
    NSString *ret2 = [fixture WriteReadString:fancmd atSite:site-1 timeOut:5000];
    writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@\r\n",fancmd,ret2]);
    return 1;
}
int get_fan_speed(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"get_fan_speed, site: %d",site]);
    if(site<1)
        return -1;
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString  *fancmdIO = [cmd objectForKey:kFIXTUREFANSPEEDGETIO];
    NSString *ret1 = [fixture WriteReadString:fancmdIO atSite:site-1 timeOut:3000];
    writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@",fancmdIO,ret1]);
    NSString *fancmd = [NSString stringWithFormat:@"%@(%d)",[cmd objectForKey:kFIXTUREFANSPEEDGET],site];
    NSString *ret = [fixture WriteReadString:fancmd atSite:site-1 timeOut:6000];
    writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@\r\n",fancmd,ret]);
    return [ret intValue];
}

bool is_fan_ok(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fan_ok, site: %d",site]);
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString *fancmd = [NSString stringWithFormat:@"%@(%d)",[cmd objectForKey:kFIXTUREFANSPEEDGET],site];
    NSString *ret = [fixture WriteReadString:fancmd atSite:site-1 timeOut:6000];
    writeFixtureLog([NSString stringWithFormat:@"[cmd] %@, [result] %@\r\n",fancmd,ret]);
    if ([ret intValue]>0)
    {
        return YES;
    }
    return YES;
}
NSString* getHostModel(void* controller)
{
    RPCController *fixture = (__bridge RPCController *)controller;
    NSString* version = [fixture getHostModel];
    writeFixtureLog([NSString stringWithFormat: @"getHostModel, result: %@\r\n",version]);
    return version;
}
int set_debug_port(void* controller, POWER_STATE action, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"set_debug_port, POWER_STATE: %d, site : %d\r\n",action,site]);
    return 1;
}

void setup_event_notification(void* controller, void* event_ctx, fixture_event_callback_t on_fixture_event, stop_event_notfication_callback_t on_stop_event_notification)
{
    if (controller == NULL || event_ctx == NULL ||
        on_fixture_event == NULL || on_stop_event_notification == NULL)
    {
        NSLog(@"setup_event_notification error: parameter error!");
        writeFixtureLog(@"setup_event_notification, null\r\n");
        return;
    }
    NSString  *cmdStatus = [cmd objectForKey:kFIXTURESTATUS];
    writeFixtureLog(@"setup_event_notification\r\n");
    RPCController *fixture = (__bridge RPCController *)controller;
    event_ctx_p = event_ctx;
    on_fixture_event_fp = on_fixture_event;
    on_stop_event_notification_fp = on_stop_event_notification;
    dispatch_async(g_queue, ^{
        while (g_auto_flag)
            {
                if (event_ctx_p == NULL || on_fixture_event_fp == NULL) {
                    break;
                }
                if (g_out_flag)
                {
                    usleep(1000*1000);
                    @autoreleasepool
                    {
                        if (event_ctx_p == NULL || on_fixture_event_fp == NULL) { continue; }
                        int status = [fixture getCylinderStatus:cmdStatus];
                        if (status != 0) { continue; }
                        //cleanUartLog(controller);
                        // uart shutdown
                        [fixture uartShutdown:1];
                        usleep(1000*1000);
                        
                        BOOL isDetectDUT = NO;
                        for (int i = 1; i <= 4; i++) {
                            if (event_ctx_p == NULL || on_fixture_event_fp == NULL) { break; }
                            if (is_board_detected(controller, i))
                            {
                                if (on_fixture_event_fp) {
                                    isDetectDUT = YES;
                                    on_fixture_event_fp("TBD", controller, event_ctx_p, i, 0);
                                }
                            }
                            usleep(1000*100);
                        }
                        if (isDetectDUT) {
                            g_out_flag = NO;
                        } else {
                            usleep(1000*5000);
                        }
                    
                    }
                
                }
                if (event_ctx_p == NULL || on_fixture_event_fp == NULL) { continue; }
                usleep(1000*1000);
            }
    });
    writeFixtureLog(@"finished setup_event_notification\r\n");
}

