//
//  DFUFixture.m
//  DFUFixture
//
//  Created by RyanGao on 16/10/17.
//  Copyright © 2016年 RyanGao. All rights reserved.
//

#import "DFUFixture.h"
#import <Foundation/Foundation.h>
#import "plistParse.h"
#import "CRS232.h"
#import "ErrorCode.h"
#import "USBDevice.h"

#define noDebugMode

int g_SLOTS = 0;
extern ErrorCode * g_errcode;

NSMutableDictionary * cmd = [[NSMutableDictionary alloc]init];
NSMutableArray* BladeMCUArray =[[NSMutableArray alloc]initWithCapacity:20];
NSMutableArray* rs232Arr =[[NSMutableArray alloc]initWithCapacity:20];

//CRS232 * rs232_1 = new CRS232();
//CRS232 * rs232_2 = new CRS232();
//
//CRS232 * rs232Arr_Fixture1[] = {rs232_1};
//CRS232 * rs232Arr_Fixture2[] = {rs232_2};
static dispatch_once_t onceToken;
pthread_mutex_t writefile_mutex;

void writeFixtureLog_debug(int siteLog,NSString *strContent)
{
#ifdef DebugMode
   /* pthread_mutex_lock(&writefile_mutex);
    NSDateFormatter* DateFomatter = [[NSDateFormatter alloc] init];
    [DateFomatter setDateFormat:@"yyyy/MM/dd HH:mm:ss.SSS "];
    NSString* timeFlag = [DateFomatter stringFromDate:[NSDate date]];
    [DateFomatter setDateFormat:@"yyyy_MM_dd"];
    NSString* timeFilenName = [DateFomatter stringFromDate:[NSDate date]];
    [DateFomatter release];
    //NSString *pathLogFile=[NSString stringWithFormat:@"/vault/atlas/IAFixture_slot-%d_%@.txt",siteLog,timeFilenName];
    NSString *pathLogFile=[NSString stringWithFormat:@"/vault/atlas/IAFixture_Command_%@.txt",timeFilenName];
    [plistParse checkLogFileExist:pathLogFile];
    [plistParse writeLog2File:pathLogFile withTime:timeFlag andContent:strContent];
    pthread_mutex_unlock(&writefile_mutex);
    */
#endif
}

void writeFixtureLog(NSString *strContent)
{
    
    pthread_mutex_lock(&writefile_mutex);
    NSDateFormatter* DateFomatter = [[NSDateFormatter alloc] init];
    [DateFomatter setDateFormat:@"yyyy/MM/dd HH:mm:ss.SSS "];
    NSString* timeFlag = [DateFomatter stringFromDate:[NSDate date]];
    [DateFomatter setDateFormat:@"yyyy_MM_dd"];
    NSString* timeFilenName = [DateFomatter stringFromDate:[NSDate date]];
    [DateFomatter release];
    //NSString *pathLogFile=[NSString stringWithFormat:@"/vault/atlas/IAFixture_slot-%d_%@.txt",siteLog,timeFilenName];
    NSString *pathLogFile=[NSString stringWithFormat:@"/vault/atlas/IAFixture_Command_%@.txt",timeFilenName];
    [plistParse checkLogFileExist:pathLogFile];
    [plistParse writeLog2File:pathLogFile withTime:timeFlag andContent:strContent];
    pthread_mutex_unlock(&writefile_mutex);
    
}


void* create_fixture_controller(int index)
{
    if (BladeMCUArray) {
        [BladeMCUArray removeAllObjects];
    }
    NSArray *array=[USBDevice getAllAttachedDevices];
    for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
        int j=[myindex[1] intValue];
        if ([myindex[0] containsString:KBladeMCUName])
        {
           if ([[array[j] valueForKey:@"SerialNumber"] hasSuffix:@"BLD"])
            {
                [BladeMCUArray addObject:[array[j] valueForKey:@"SerialNumber"]];
            }
        }
    }
    
    [BladeMCUArray sortUsingComparator:^NSComparisonResult(__strong id obj1,__strong id obj2){
        NSString *str1=(NSString *)obj1;
        NSString *str2=(NSString *)obj2;
        return [str1 compare:str2];
    }];
    
    if(cmd)
    {
        [cmd removeAllObjects];
    }
    [cmd setDictionary:[plistParse readAllCMD]];
    if([cmd count]>0)
    {
        g_SLOTS = [[cmd objectForKey:kFIXTURESLOTS]intValue];
    }
    if(rs232Arr && [rs232Arr count]>0)
    {
        ((__bridge CRS232 *)[rs232Arr objectAtIndex:index])->Close();
    }
    
    CRS232 * rs232 = new CRS232();
    rs232->Open([[NSString stringWithFormat:@"/dev/cu.usbserial-%@",BladeMCUArray[index]] UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
    rs232->SetDetectString("\r\n");
    dispatch_once(&onceToken, ^{
        pthread_mutex_init(&writefile_mutex, nil);
    });
    writeFixtureLog([NSString stringWithFormat:@"create_fixture_controller , index : %d\r\n",index]);
    rs232Arr[index]=(__bridge id)rs232;
    return (__bridge void*)rs232Arr;
        
    
    
    
    
    /*
    if (index==0)
    {
        rs232Arr_Fixture1[0]->Close();
        if(dic)
            {
                    //rs232Arr_Fixture1[0]->Open([[dic objectForKey:[NSString stringWithFormat:@"UUT%d",0]]UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                rs232Arr_Fixture1[0]->Open([[NSString stringWithFormat:@"/dev/cu.usbserial-%@",BladeMCUArray[0]] UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                    rs232Arr_Fixture1[0]->SetDetectString("\r\n");
            }

        pthread_mutex_init(&writefile_mutex, nil);
        writeFixtureLog([NSString stringWithFormat:@"create_fixture_controller , index : %d\r\n",index]);
        return (__bridge void*)rs232Arr_Fixture1;
    }
    else if (index==1)
    {
        rs232Arr_Fixture2[0]->Close();
            if(dic)
            {
                //rs232Arr_Fixture2[0]->Open([[dic objectForKey:[NSString stringWithFormat:@"UUT%d",1]]UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                rs232Arr_Fixture2[0]->Open([[NSString stringWithFormat:@"/dev/cu.usbserial-%@",BladeMCUArray[1]] UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                rs232Arr_Fixture2[0]->SetDetectString("\r\n");
            }
        writeFixtureLog([NSString stringWithFormat:@"create_fixture_controller , index : %d\r\n",index]);
        return (__bridge void*)rs232Arr_Fixture2;
        
    }
    return nil;
    */
    //for(int i=0; i<g_SLOTS; i++)
    /*for(int i=0; i<4; i++)
    {
        if(dic)
        {
            if (index==0) {
                rs232Arr_Fixture1[i]->Open([[dic objectForKey:[NSString stringWithFormat:@"UUT%d",i]]UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                rs232Arr_Fixture1[i]->SetDetectString("\r\n");
            }
            else if(index==1)
            {
                rs232Arr[i]->Open([[dic objectForKey:[NSString stringWithFormat:@"UUT%d",i+4]]UTF8String], [[cmd objectForKey:kFIXTURESETTING]UTF8String]);
                rs232Arr[i]->SetDetectString("\r\n");
                
            }
            
        }
    }
    return (__bridge void*)rs232Arr;*/
}

void release_fixture_controller(void* controller)
{
    if (BladeMCUArray)
    {
        [BladeMCUArray removeAllObjects];
    }
    if(cmd)
    {
        [cmd removeAllObjects];
    }
    
    for (int i=0; i<[rs232Arr count]; i++) {
        if (controller==[rs232Arr objectAtIndex:i]) {
            writeFixtureLog([NSString stringWithFormat:@"release_fixture_controller , controller : %d\r\n",i]);
            ((__bridge CRS232 *)[rs232Arr objectAtIndex:i])->Close();
            
        }
    }
    
//    if (controller==rs232Arr_Fixture1)
//        {
//           rs232Arr_Fixture1[0]->Close();
//            //pthread_mutex_destroy(&writefile_mutex);
//            writeFixtureLog([NSString stringWithFormat:@"release_fixture_controller , controller : 0\r\n"]);
//        }
//    else if(controller==rs232Arr_Fixture2)
//        {
//           rs232Arr_Fixture2[0]->Close();
//           writeFixtureLog([NSString stringWithFormat:@"release_fixture_controller , controller : 1\r\n"]);
//        }
}


/////////////////////////////////////////////////////
/////////////////////////////////////////////////////


int executeAction(void *controller,NSString * key, int site)
{
    int i_controller=0;
    for (int i_controller=0; i_controller<[rs232Arr count]; i_controller++) {
        if (controller==[rs232Arr objectAtIndex:1]) {
            writeFixtureLog([NSString stringWithFormat:@"release_fixture_controller , controller : %d\r\n",i]);
            ((__bridge CRS232 *)[rs232Arr objectAtIndex:i])->Close();
            
        }
    }
    writeFixtureLog([NSString stringWithFormat:@"%@ start , controller : %d , site : %d",key,(controller==rs232Arr_Fixture1? 0:1),site]);
    if(site<1)
        return -1;

    id list = [cmd objectForKey:key];
    CRS232 * r = nil;//rs232Arr[site-1];
    if (controller==rs232Arr_Fixture1) {
        r=rs232Arr_Fixture1[0];
        
    }
    else if (controller==rs232Arr_Fixture2)
    {
         r=rs232Arr_Fixture2[0];
    }
    if (r==nil) {
        return -1;
    }
    
    NSArray * arr = (__bridge NSArray*)list;
    for (int j=0; j<[arr count]; j++) {
        if ([[[arr objectAtIndex:j]uppercaseString] containsString:@"DELAY:"]) {
            NSArray *arryDelay=[[arr objectAtIndex:j] componentsSeparatedByString:@":"];
             if ([[arryDelay[0] uppercaseString] isEqual:@"DELAY"]) {
                 [NSThread sleepForTimeInterval:[arryDelay[1] doubleValue]];
             }
        }
        else if (([[arr objectAtIndex:j] containsString:@"vbatt"])||([[arr objectAtIndex:j] containsString:@"vbus"]))
        {
            NSArray *arryCmd=[[arr objectAtIndex:j] componentsSeparatedByString:@" "];
            NSString *voltCmd=[NSString stringWithFormat:@"%@%d %@",arryCmd[0],site,arryCmd[1]];
            r->WriteReadString([voltCmd UTF8String], 1000);
        }
        else
        {
              r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
//            const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
//            NSString *u2=[NSString stringWithUTF8String:u1];
//            NSLog(@"IA:%@",u2);
            //if ([u2 containsString:@"OK"]) {
            //    break;
            //}
           //[NSThread sleepForTimeInterval:0.1];
       // }
        }
        
    }
    writeFixtureLog([NSString stringWithFormat:@"%@ : 0 , controller : %d , site : %d \r\n",key,(controller==rs232Arr_Fixture1? 0:1),site]);
    return 0;
}


int executeAction_all(void *controller,NSString * key)
{
    writeFixtureLog([NSString stringWithFormat:@"%@ start , controller : %d , site : all",key,(controller==rs232Arr_Fixture1? 0:1)]);
    
    id list = [cmd objectForKey:key];
    CRS232 * r = nil;//rs232Arr[site-1];
    if (controller==rs232Arr_Fixture1) {
        r=rs232Arr_Fixture1[0];
        
    }
    else if (controller==rs232Arr_Fixture2)
    {
        r=rs232Arr_Fixture2[0];
    }
    if (r==nil) {
        return -1;
    }
    
    NSArray * arr = (__bridge NSArray*)list;
    for (int j=0; j<[arr count]; j++) {
        if ([[[arr objectAtIndex:j]uppercaseString] containsString:@"DELAY:"]) {
            NSArray *arryDelay=[[arr objectAtIndex:j] componentsSeparatedByString:@":"];
            if ([[arryDelay[0] uppercaseString] isEqual:@"DELAY"]) {
                [NSThread sleepForTimeInterval:[arryDelay[1] doubleValue]];
            }
        }
        else if (([[arr objectAtIndex:j] containsString:@"vbatt"])||([[arr objectAtIndex:j] containsString:@"vbus"]))
        {
            NSArray *arryCmd=[[arr objectAtIndex:j] componentsSeparatedByString:@" "];
            NSString *voltCmd=[NSString stringWithFormat:@"%@%d %@",arryCmd[0],1,arryCmd[1]];
            r->WriteReadString([voltCmd UTF8String], 1000);
                      voltCmd=[NSString stringWithFormat:@"%@%d %@",arryCmd[0],2,arryCmd[1]];
            r->WriteReadString([voltCmd UTF8String], 1000);
                      voltCmd=[NSString stringWithFormat:@"%@%d %@",arryCmd[0],3,arryCmd[1]];
            r->WriteReadString([voltCmd UTF8String], 1000);
                      voltCmd=[NSString stringWithFormat:@"%@%d %@",arryCmd[0],4,arryCmd[1]];
            r->WriteReadString([voltCmd UTF8String], 1000);
        }
        else
        {
            r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
            //            const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
            //            NSString *u2=[NSString stringWithUTF8String:u1];
            //            NSLog(@"IA:%@",u2);
            //if ([u2 containsString:@"OK"]) {
            //    break;
            //}
            //[NSThread sleepForTimeInterval:0.1];
            // }
        }
        
    }
    writeFixtureLog([NSString stringWithFormat:@"%@ : 0 , controller : %d , site : all \r\n",key,(controller==rs232Arr_Fixture1? 0:1)]);
    return 0;
}


/////////////////////////////////////////////////////
int executeAllAction(void *controller,NSString * key)
{
    //writeFixtureLog([NSString stringWithFormat:@"%@ start , controller : %d",key,(controller==rs232Arr_Fixture1? 0:1)]);
    //for(int i=0; i<g_SLOTS; i++)
   // for(int i=0; i<4; i++)
   // {
        executeAction_all(controller,key);
   // }
    //writeFixtureLog([NSString stringWithFormat:@"execute %@ : 0 , controller : %d \r\n",key,(controller==rs232Arr_Fixture1? 0:1)]);
    return 0;
}
/////////////////////////////////////////////////////
/////////////////////////////////////////////////////


const char * const get_vendor()
{
    writeFixtureLog([NSString stringWithFormat:@"get_vendor start"]);
    id obj = [cmd objectForKey:kVENDER];
    if(obj)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_vendor : %@\r\n",obj]);
        return [obj UTF8String];
    }
    else
    {
        writeFixtureLog(@"get_vendor : IA\r\n");
        return "IA";
    }
}


const char * const get_serial_number(void* controller)
{
//    id obj = [cmd objectForKey:kSERIAL];
//    if(obj)
//        return [obj UTF8String];
//    else
//        return "TBD";
    writeFixtureLog([NSString stringWithFormat:@"get_serial_number start , controller : %d",(controller==rs232Arr_Fixture1?0:1)]);
    if (controller==rs232Arr_Fixture1)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_serial_number : 0 , controller : 0\r\n"]);
        return "0";
    }
    else if(controller==rs232Arr_Fixture2)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_serial_number : 0 , controller : 1\r\n"]);
        return "0";
    }
    return "-1";
    
    
}

const char * const get_carrier_serial_number(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number start , site : %d , controller : %d",site,(controller==rs232Arr_Fixture1?0:1)]);
    if(site<1)
    {
        writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : 0000 , site : %d , controller : %d\r\n",site,(controller==rs232Arr_Fixture1?0:1)]);
        return "0000";
    }
    /*NSMutableArray* uartSerialArray = [NSMutableArray array];
    NSMutableArray* uartSerialArray_sub1 = [NSMutableArray array];
    NSMutableArray* uartSerialArray_sub2 = [NSMutableArray array];
    NSMutableArray* uartSerialLocation = [NSMutableArray array];
    NSMutableArray* ProductIDArray = [NSMutableArray array];
    
    //ProductID
    if (controller==rs232Arr_Fixture2) {
        site+=4;
    }
    
    for (int ii=0; ii<4; ii++) {
        
        NSArray *array=[USBDevice getAllAttachedDevices];
        for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
            //if ([myindex[0] containsString:@"Serial Converter"]) {
            if ([myindex[0] containsString:@"RS232-HS"]||[myindex[0] containsString:@"Serial Converter"]) {
                int j=[myindex[1] intValue];
                [uartSerialArray addObject:array[j]];
                NSString *str=[[array[j] valueForKey:@"LocationID"][0] substringWithRange:NSMakeRange(0,6)];
                NSString *strProductID=[array[j] valueForKey:@"ProductID"];
                [uartSerialLocation addObject:str];
                [ProductIDArray addObject:strProductID];
            }
        }
        if ([uartSerialLocation count]<1) {
            writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : nil , site : %d \r\n",site]);
            writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : nil , site : %d , controller : %d\r\n",site,(controller==rs232Arr_Fixture1?0:1)]);
            return nil;
        }
        //remove duplicate
        //NSLog(@"--uartSerialLocation:-:%@",uartSerialLocation);
        
        NSSet *set = [NSSet setWithArray:uartSerialLocation];
        [uartSerialLocation addObject:[set allObjects]];
        NSArray *uartSerialLocationArray =[set allObjects];
        
        //NSLog(@"--uartSerialLocationArray--:%@",uartSerialLocationArray);
        
        if ([uartSerialLocationArray count]>0){
            for (id usbSerialArray_sub in uartSerialArray)
            {
                
                NSString *str=[usbSerialArray_sub valueForKey:@"LocationID"][0];
                NSString *strProductID=[usbSerialArray_sub valueForKey:@"ProductID"];
                if ([str containsString:uartSerialLocationArray[0]]&&[strProductID containsString:ProductIDArray[0]])
                {
                    [uartSerialArray_sub1 addObject:[usbSerialArray_sub valueForKey:@"SerialNumber"]];
                }
            }
        }else
        {
            [uartSerialArray_sub1 addObject:@""];
        }
        
        if ([uartSerialLocationArray count]>1)
        {
            for (id usbSerialArray_sub in uartSerialArray)
            {
                NSString *str=[usbSerialArray_sub valueForKey:@"LocationID"][0];
                NSString *strProductID=[usbSerialArray_sub valueForKey:@"ProductID"];
                
                if ([str containsString:uartSerialLocationArray[1]]&&[strProductID containsString:ProductIDArray[0]])
                {
                    [uartSerialArray_sub2 addObject:[usbSerialArray_sub valueForKey:@"SerialNumber"]];
                }
            }
        }
        else
        {
            [uartSerialArray_sub2 addObject:@""];
        }
        
        //sort K->A
        [uartSerialArray_sub1 sortUsingComparator:^NSComparisonResult(__strong id obj1,__strong id obj2){
            NSString *str1=(NSString *)obj1;
            NSString *str2=(NSString *)obj2;
            return [str2 compare:str1];
        }];
        if (uartSerialArray_sub2) {
            [uartSerialArray_sub2 sortUsingComparator:^NSComparisonResult(__strong id obj1,__strong id obj2){
                NSString *str1=(NSString *)obj1;
                NSString *str2=(NSString *)obj2;
                return [str2 compare:str1];
            }];
        }
        if (controller==rs232Arr_Fixture1)
        {
            if ([uartSerialArray_sub1[0] containsString:@"MCUA"]){
                if ([uartSerialArray_sub1 count]>1) {
                    break;
                }
            }
            else if ([uartSerialArray_sub2[0] containsString:@"MCUA"]) {
                if ([uartSerialArray_sub2 count]>1) {
                    break;
                }
            }
        }
        
        
        if (controller==rs232Arr_Fixture2)
        {
            if ([uartSerialArray_sub1[0] containsString:@"MCUB"]){
                if ([uartSerialArray_sub1 count]>1) {
                    break;
                }
            }
            else if ([uartSerialArray_sub2[0] containsString:@"MCUB"]) {
                if ([uartSerialArray_sub2 count]>1) {
                    break;
                }
            }
            
        }
        if (ii<3) {
            [uartSerialArray removeAllObjects];
            [uartSerialArray_sub1 removeAllObjects];
            [uartSerialArray_sub2 removeAllObjects];
            [uartSerialLocation removeAllObjects];
            [ProductIDArray removeAllObjects];
            [NSThread sleepForTimeInterval:2.5];
        }
    }
    
    NSString *serial_number=@"0000";
    
    if ([uartSerialArray_sub1[0] containsString:@"MCUA"]){
        if ([@"1234" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub1 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d get_carrier_serial_number : -1 . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : -1, site : %d , controller : %d \r\n",site,0]);
                return "-1";
            }
            serial_number=uartSerialArray_sub1[1];
        }
        
    }
    
    if ([uartSerialArray_sub1[0] containsString:@"MCUB"]) {
        if ([@"5678" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub1 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d get_carrier_serial_number : -1 . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : -1, site : %d , controller : %d \r\n",site,1]);
                return "-1";
            }
            serial_number=uartSerialArray_sub1[1];
        }
    }
    
    
    if ([uartSerialArray_sub2[0] containsString:@"MCUA"]) {
        if ([@"1234" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub2 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d get_carrier_serial_number : -1 . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : -1, site : %d , controller : %d \r\n",site,0]);
                return "-1";
            }
            serial_number=uartSerialArray_sub2[1];
        }
    }
    if ([uartSerialArray_sub2[0] containsString:@"MCUB"]) {
        if ([@"5678" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub2 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d get_carrier_serial_number : -1 . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : -1, site : %d , controller : %d \r\n",site,1]);
                return "-1";
            }
            serial_number=uartSerialArray_sub2[1];
        }
    }
    writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d get_carrier_serial_number : %@ . site : %d\r\n",site,serial_number,site]);
    writeFixtureLog([NSString stringWithFormat:@"get_carrier_serial_number : %@, site : %d , controller : %d \r\n",serial_number,site,(controller==rs232Arr_Fixture1?0:1)]);
    return [serial_number UTF8String];
    */
    return nil;
    
}

const char* const get_error_message(int status)
{
    
    writeFixtureLog([NSString stringWithFormat:@"get_error_message start . status : %d ",status]);
    if(g_errcode)
    {
        writeFixtureLog_debug(status,[NSString stringWithFormat:@"slot-0 : getErrorMsg : %s . status : %d",[g_errcode getErrorMsg:status],status]);
        writeFixtureLog([NSString stringWithFormat:@"get_error_message : %s . status : %d \r\n",[g_errcode getErrorMsg:status],status]);
        return [g_errcode getErrorMsg:status];
    }
    else
    {
        writeFixtureLog([NSString stringWithFormat:@"get_error_message : Invalide ErroCode center . status : %d\r\n ",status]);
        return "Invalide ErroCode center";
    }
}

const char* const get_version(void* controller)
{
    writeFixtureLog([NSString stringWithFormat:@"get_version start ."]);
    id obj = [cmd objectForKey:kVERSION];
    if(obj)
    {
        writeFixtureLog_debug(-1,[NSString stringWithFormat:@"slot-0 : get_version : %@",obj]);
        writeFixtureLog([NSString stringWithFormat:@"get_version : %@ . controller : %d \r\n",obj,(controller==rs232Arr_Fixture1?0:1)]);
        return [obj UTF8String];
    }
    else
    {
        writeFixtureLog([NSString stringWithFormat:@"get_version : 0.1 . controller : %d \r\n",(controller==rs232Arr_Fixture1?0:1)]);
        return "0.1";
    }
}

int init(void* controller)
{
    return executeAllAction(controller,kINIT);
}

int reset(void* controller)
{
    return executeAllAction(controller,kRESET);
}

int get_site_count(void* controller)
{
    writeFixtureLog_debug(-1,[NSString stringWithFormat:@"slot-0 : get_site_count : %d",4]);
    writeFixtureLog([NSString stringWithFormat:@"get_site_count : 2 , controller : %d \r\n",(controller==rs232Arr_Fixture1? 0:1) ]);
    return 4;//g_SLOTS;
}

int get_actuator_count(void* controller)
{
    writeFixtureLog_debug(-1,[NSString stringWithFormat:@"slot-0 : get_actuator_count : %d",4]);
    writeFixtureLog([NSString stringWithFormat:@"get_actuator_count : 4 , controller : %d \r\n",(controller==rs232Arr_Fixture1? 0:1)]);
    return 4;//g_SLOTS;
}

const char* get_usb_location(void* controller, int site)
{
    /*int st=site;
    writeFixtureLog([NSString stringWithFormat:@"get_usb_location start , site : %d , controller : %d",site,(controller==rs232Arr_Fixture1? 0:1)]);
    if(site<1)
        return "site should be from 1";
    
    if (controller==rs232Arr_Fixture2) {
        site+=4;
    }
    
    id usb = [cmd objectForKey:kUSBLOCATION];
    if(usb)
    {
        writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d usb Location: %@ . site : %d\r\n",site,[(NSDictionary*)usb objectForKey:[NSString stringWithFormat:@"UUT%d",site-1]],site]);
        id str = [(NSDictionary*)usb objectForKey:[NSString stringWithFormat:@"UUT%d",site-1] ];
        if(str)
        {
            writeFixtureLog([NSString stringWithFormat:@"get_usb_location : %@ , site : %d , controller : %d\r\n",str,st,(controller==rs232Arr_Fixture1? 0:1)]);
            return [str UTF8String];
        }
        return nil;
    }
    return nil;
     */
    
   
    writeFixtureLog([NSString stringWithFormat:@"get_usb_location start , site : %d , controller : %d",site,(controller==rs232Arr_Fixture1? 0:1)]);
    NSMutableDictionary* u_location = [NSMutableDictionary dictionary];
    NSArray *array=[USBDevice getAllAttachedDevices];
    int i=0;
    NSString *mm_str=@"0x111000000"; //default
    for (id myindex in [array valueForKey:@"ProductID"]) {
        
        if (([[NSString stringWithFormat:@"%@",myindex] isEqualToString:kUSBLocationPID])&&([[array[i] valueForKey:@"VendorID"] isEqualToString:kUSBLocationVID])) {
            mm_str=[array[i] valueForKey:@"LocationID"][0];
            [u_location setObject:mm_str forKey:[mm_str substringWithRange:NSMakeRange(0,[mm_str rangeOfString:@"00"].location-1)]];
        }
        i++;
    }
    
    for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
        int j=[myindex[1] intValue];
        if ([myindex[0] containsString:KBladeMCUName])
        {
            if (controller==rs232Arr_Fixture1)
            {
                if ([[array[j] valueForKey:@"SerialNumber"] containsString:BladeMCUArray[0]])
                    {
                        NSString *ss_str=[array[j] valueForKey:@"LocationID"][0];
                        NSString *usb_location_1=[u_location valueForKey:[ss_str substringWithRange:NSMakeRange(0,[ss_str rangeOfString:@"00"].location-1)]];
                        usb_location_1=[[usb_location_1 stringByReplacingCharactersInRange:NSMakeRange([usb_location_1 rangeOfString:@"00"].location, 1) withString:[NSString stringWithFormat:@"%d",5-site]]lowercaseString];
                        writeFixtureLog([NSString stringWithFormat:@"get_usb_location : %@ , site : %d , controller : %d\r\n",usb_location_1,site,(controller==rs232Arr_Fixture1? 0:1)]);
                        return [usb_location_1 UTF8String];
                    }
            }
            
            if (controller==rs232Arr_Fixture2)
            {
                if ([[array[j] valueForKey:@"SerialNumber"] containsString:BladeMCUArray[1]])
                    {
                        NSString *ss_str=[array[j] valueForKey:@"LocationID"][0];
                        NSString *usb_location_2=[u_location valueForKey:[ss_str substringWithRange:NSMakeRange(0,[ss_str rangeOfString:@"00"].location-1)]];
                        usb_location_2=[[usb_location_2 stringByReplacingCharactersInRange:NSMakeRange([usb_location_2 rangeOfString:@"00"].location, 1) withString:[NSString stringWithFormat:@"%d",5-site]]lowercaseString];
                        writeFixtureLog([NSString stringWithFormat:@"get_usb_location : %@ , site : %d , controller : %d\r\n",usb_location_2,site,(controller==rs232Arr_Fixture1? 0:1)]);
                        return [usb_location_2 UTF8String];
                    }
            }
        }
    }
   writeFixtureLog([NSString stringWithFormat:@"get_usb_location : nil , site : %d , controller : %d\r\n",site,(controller==rs232Arr_Fixture1? 0:1)]);
    return nil;
    
    
}

const char* get_uart_path(void* controller, int site)
{
    int st=site;
    writeFixtureLog([NSString stringWithFormat:@"get_uart_path start , site : %d , controller : %d",site,(controller==rs232Arr_Fixture1? 0:1)]);

    if(site<1)
        return "site should be from 1";
  
    NSMutableArray* uartSerialArray = [NSMutableArray array];
    NSMutableArray* uartSerialArray_sub1 = [NSMutableArray array];
    NSMutableArray* uartSerialArray_sub2 = [NSMutableArray array];
    NSMutableArray* uartSerialLocation = [NSMutableArray array];
    //NSMutableArray* ProductIDArray = [NSMutableArray array];
    
    //ProductID
    if (controller==rs232Arr_Fixture2) {
        site+=4;
    }
    
    for (int ii=0; ii<4; ii++) {
        
    NSArray *array=[USBDevice getAllAttachedDevices];
    for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
        //if ([myindex[0] containsString:@"Serial Converter"]) {
        if ([myindex[0] containsString:KBladeMCUName]||[myindex[0] containsString:KCarrierMCUName]) {
            int j=[myindex[1] intValue];
            [uartSerialArray addObject:array[j]];
            //NSString *str=[[array[j] valueForKey:@"LocationID"][0] substringWithRange:NSMakeRange(0,6)];
            NSString *str_temp=[array[j] valueForKey:@"LocationID"][0];
            NSString *str=[str_temp substringWithRange:NSMakeRange(0, [str_temp rangeOfString:@"00"].location-1)];
            //NSString *strProductID=[array[j] valueForKey:@"ProductID"];
            [uartSerialLocation addObject:str];
            //[ProductIDArray addObject:strProductID];
        }
    }
        if ([uartSerialLocation count]<1) {
            writeFixtureLog([NSString stringWithFormat:@"get_uart_path : nil , site : %d , controller : %d\r\n",st,(controller==rs232Arr_Fixture1? 0:1)]);
            return nil;
        }
    //remove duplicate
    //NSLog(@"--uartSerialLocation:-:%@",uartSerialLocation);
        
    NSSet *set = [NSSet setWithArray:uartSerialLocation];
    [uartSerialLocation addObject:[set allObjects]];
    NSArray *uartSerialLocationArray =[set allObjects];
    
    //NSLog(@"--uartSerialLocationArray--:%@",uartSerialLocationArray);
    
    if ([uartSerialLocationArray count]>0){
    for (id usbSerialArray_sub in uartSerialArray)
    {
       
        NSString *str=[usbSerialArray_sub valueForKey:@"LocationID"][0];
       // NSString *strProductID=[usbSerialArray_sub valueForKey:@"ProductID"];
        //if ([str containsString:uartSerialLocationArray[0]]&&[strProductID containsString:ProductIDArray[0]])
        if ([str containsString:uartSerialLocationArray[0]])
        {
            [uartSerialArray_sub1 addObject:[usbSerialArray_sub valueForKey:@"SerialNumber"]];
        }
    }
    }else
    {
        [uartSerialArray_sub1 addObject:@""];
    }
        
    if ([uartSerialLocationArray count]>1)
    {
        for (id usbSerialArray_sub in uartSerialArray)
        {
                NSString *str=[usbSerialArray_sub valueForKey:@"LocationID"][0];
               // NSString *strProductID=[usbSerialArray_sub valueForKey:@"ProductID"];
                //if ([str containsString:uartSerialLocationArray[1]]&&[strProductID containsString:ProductIDArray[0]])
               if ([str containsString:uartSerialLocationArray[1]])
                {
                    [uartSerialArray_sub2 addObject:[usbSerialArray_sub valueForKey:@"SerialNumber"]];
                }
        }
    }
    else
    {
        [uartSerialArray_sub2 addObject:@""];
    }
    
    //sort K->A
        [uartSerialArray_sub1 sortUsingComparator:^NSComparisonResult(__strong id obj1,__strong id obj2){
        NSString *str1=[(NSString *)obj1 substringFromIndex:5];
        NSString *str2=[(NSString *)obj2 substringFromIndex:5];
        return [str1 compare:str2];
    }];
        if (uartSerialArray_sub2) {
        [uartSerialArray_sub2 sortUsingComparator:^NSComparisonResult(__strong id obj1,__strong id obj2){
        NSString *str1=[(NSString *)obj1 substringFromIndex:5];
        NSString *str2=[(NSString *)obj2 substringFromIndex:5];
        return [str1 compare:str2];
    }];
            
            
        }
           if (controller==rs232Arr_Fixture1)
           {
               if ([uartSerialArray_sub1[0] containsString:BladeMCUArray[0]]){
                    if ([uartSerialArray_sub1 count]>1) {
                        break;
                        }
                    }
               else if ([uartSerialArray_sub2[0] containsString:BladeMCUArray[0]]) {
                    if ([uartSerialArray_sub2 count]>1) {
                    break;
                        }
                    }
            }
    
        
        if (controller==rs232Arr_Fixture2)
        {
            if ([uartSerialArray_sub1[0] containsString:BladeMCUArray[1]]){
                if ([uartSerialArray_sub1 count]>1) {
                    break;
                }
            }
            else if ([uartSerialArray_sub2[0] containsString:BladeMCUArray[1]]) {
                if ([uartSerialArray_sub2 count]>1) {
                    break;
                }
            }

        }
        if (ii<3) {
            [uartSerialArray removeAllObjects];
            [uartSerialArray_sub1 removeAllObjects];
            [uartSerialArray_sub2 removeAllObjects];
            [uartSerialLocation removeAllObjects];
            //[ProductIDArray removeAllObjects];
            [NSThread sleepForTimeInterval:2.5];
        }
    }
    
    NSString *uartPath=@"";
    NSString *pp=@"";
      switch (site)
            {
                case 1:
                    pp =@"A";break;
                case 2:
                    pp =@"B";break;
                case 3:
                    pp =@"C";break;
                case 4:
                    pp =@"D";break;
                case 5:
                    pp =@"A";break;
                case 6:
                    pp =@"B";break;
                case 7:
                    pp =@"C";break;
                case 8:
                    pp =@"D";break;
                default:
                    break;
            }
    
    if ([uartSerialArray_sub1[0] containsString:BladeMCUArray[0]]){
            if ([@"1234" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub1 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d : get_uart_path is null . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_uart_path : nil , site : %d , controller : %d\r\n",st,(controller==rs232Arr_Fixture1? 0:1)]);
                return nil;
            }
        uartPath=[NSString stringWithFormat:@"/dev/cu.usbserial-%@%@",uartSerialArray_sub1[1],pp];
        }
        
    }
    
    if ([uartSerialArray_sub1[0] containsString:BladeMCUArray[1]]) {
        if ([@"5678" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub1 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d : get_uart_path is null . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_uart_path : nil , site : %d , controller : %d\r\n",st,(controller==rs232Arr_Fixture1? 0:1)]);
                return nil;
            }
        uartPath=[NSString stringWithFormat:@"/dev/cu.usbserial-%@%@",uartSerialArray_sub1[1],pp];
        }
      }
    
    
        if ([uartSerialArray_sub2[0] containsString:BladeMCUArray[0]]) {
        if ([@"1234" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub2 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d : get_uart_path is null . site : %d\r\n",site,site]);
                 writeFixtureLog([NSString stringWithFormat:@"get_uart_path : nil , site : %d , controller : %d\r\n",st,(controller==rs232Arr_Fixture1? 0:1)]);
                return nil;
            }
        uartPath=[NSString stringWithFormat:@"/dev/cu.usbserial-%@%@",uartSerialArray_sub2[1],pp];
        }
    }
    if ([uartSerialArray_sub2[0] containsString:BladeMCUArray[1]]) {
        if ([@"5678" containsString:[NSString stringWithFormat:@"%d", site]])
        {
            if ([uartSerialArray_sub2 count]<2) {
                writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d : get_uart_path is null . site : %d\r\n",site,site]);
                writeFixtureLog([NSString stringWithFormat:@"get_uart_path : nil , site : %d , controller : %d\r\n",st,(controller==rs232Arr_Fixture1? 0:1)]);
                return nil;
            }
        uartPath=[NSString stringWithFormat:@"/dev/cu.usbserial-%@%@",uartSerialArray_sub2[1],pp];
        }
     }
    writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d :%@ . site : %d\r\n",site,uartPath,site]);
    writeFixtureLog([NSString stringWithFormat:@"get_uart_path : %@ , site : %d , controller : %d\r\n",uartPath,st,(controller==rs232Arr_Fixture1? 0:1)]);
    return [uartPath UTF8String];
    
//    id usb = [cmd objectForKey:kUARTPATH];
//    if(usb)
//    {
//        id str = [(NSDictionary*)usb objectForKey:[NSString stringWithFormat:@"UUT%d",site-1] ];
//        if(str)
//            return [str UTF8String];
//        return nil;
//    }
//    return nil;
}


int actuator_for_site(void* controller, int site)
{
    writeFixtureLog_debug(site,[NSString stringWithFormat:@"slot-%d : actuator_for_site . site : %d\r\n",site,site]);
    writeFixtureLog([NSString stringWithFormat:@"actuator_for_site start , site : %d , controller : %d",site,(controller==rs232Arr_Fixture1? 0:1)]);
    if(site<1)
    {
        return -1;
    }
    writeFixtureLog([NSString stringWithFormat:@"actuator_for_site : %d , site : %d , controller : %d\r\n",site-1,site,(controller==rs232Arr_Fixture1? 0:1)]);
    return site-1;
}

int fixture_engage(void* controller, int actuator_index)
{
    writeFixtureLog_debug(0,[NSString stringWithFormat:@"slot-0 : fixture_engage : %d\r\n",actuator_index]);
    writeFixtureLog([NSString stringWithFormat:@"fixture_engage start , actuator_index : %d , controller : %d",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    if(actuator_index<0)
    {
        writeFixtureLog([NSString stringWithFormat:@"fixture_engage : -1 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return -1;
    }
    writeFixtureLog([NSString stringWithFormat:@"fixture_engage : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    return 0;
}

int fixture_disengage(void* controller, int actuator_index)
{
    writeFixtureLog_debug(0,[NSString stringWithFormat:@"slot-0 : fixture_disengage : %d\r\n",actuator_index]);
    writeFixtureLog([NSString stringWithFormat:@"fixture_disengage start , actuator_index : %d , controller : %d ",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    if(actuator_index<0)
    {
        writeFixtureLog([NSString stringWithFormat:@"fixture_disengage : -1 , actuator_index : %d , controller : %d\r\n ",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return -1;
    }
        writeFixtureLog([NSString stringWithFormat:@"fixture_disengage : 0 , actuator_index : %d , controller : %d\r\n ",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    return 0;
}

int fixture_open(void* controller, int actuator_index)
{
   // if(actuator_index<0)
       // return -1;
//return executeAllAction(controller,kFIXTUREOPEN);
//    return 0;
 
     //return executeAction(controller,kFIXTUREOPEN,actuator_index);
    //return executeAllAction(controller,kFIXTUREOPEN);
  /*  writeFixtureLog([NSString stringWithFormat:@"fixture_open start , actuator_index : %d , controller : %d ",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    CRS232 * r = nil;//rs232Arr[site-1];
    id list = [cmd objectForKey:kFIXTUREOPEN];
    NSArray * arr = (__bridge NSArray*)list;
    
    if (controller==rs232Arr_Fixture1) {
        for(int i1=0; i1<4; i1++)
        {
            r=rs232Arr_Fixture1[i1];
            for (int j=0; j<[arr count]; j++) {
                writeFixtureLog_debug(i1+1,[NSString stringWithFormat:@"slot-%d send %@ command :%@ . actuator_index : %d",i1+1,kFIXTUREOPEN,[arr objectAtIndex:j],actuator_index]);
                const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
                NSString *u2=[NSString stringWithUTF8String:u1];
                writeFixtureLog_debug(i1+1,[NSString stringWithFormat:@"slot-%d receive %@ :%@",i1+1,kFIXTUREOPEN,u2]);
            }
            
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_open : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    else if(controller==rs232Arr_Fixture2){
        for(int i2=0; i2<4; i2++)
        {
            r=rs232Arr_Fixture2[i2];
            for (int j=0; j<[arr count]; j++) {
                writeFixtureLog_debug(i2+5,[NSString stringWithFormat:@"slot-%d send %@ command :%@ .  actuator_index : %d",i2+5,kFIXTUREOPEN,[arr objectAtIndex:j],actuator_index]);
                const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
                NSString *u2=[NSString stringWithUTF8String:u1];
                writeFixtureLog_debug(i2+5,[NSString stringWithFormat:@"slot-%d receive %@ :%@",i2+5,kFIXTUREOPEN,u2]);
            }
            
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_open : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
   */
    id list = [cmd objectForKey:kFIXTUREOPEN];
    NSArray * arr = (__bridge NSArray*)list;
    
    if (controller==rs232Arr_Fixture1) {
            for (int j=0; j<[arr count]; j++) {
                rs232Arr_Fixture1[0]->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_open : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    else if(controller==rs232Arr_Fixture2){
      for (int j=0; j<[arr count]; j++) {
          rs232Arr_Fixture2[0]->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
          
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_open : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    return 0;
    
}

int fixture_close(void* controller, int actuator_index)
{
    //return executeAllAction(kINIT);
   // if(actuator_index<0)
      //  return -1;
//    return 0;
   // return executeAllAction(controller,kFIXTURECLOSE);
   //return executeAction(controller,kFIXTURECLOSE,actuator_index);
  /*  writeFixtureLog([NSString stringWithFormat:@"fixture_close start , actuator_index : %d , controller : %d ",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
    CRS232 * r = nil;//rs232Arr[site-1];
    id list = [cmd objectForKey:kFIXTURECLOSE];
    NSArray * arr = (__bridge NSArray*)list;
    if (controller==rs232Arr_Fixture1) {
        for(int i=0; i<4; i++)
        {
            r=rs232Arr_Fixture1[i];
              for (int j=0; j<[arr count]; j++)
              {
                writeFixtureLog_debug(i+1,[NSString stringWithFormat:@"slot-%d send %@ command :%@ .  actuator_index : %d",i+1,kFIXTURECLOSE,[arr objectAtIndex:j],actuator_index]);
                const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
                NSString *u2=[NSString stringWithUTF8String:u1];
                writeFixtureLog_debug(i+1,[NSString stringWithFormat:@"slot-%d receive %@ :%@",i+1,kFIXTURECLOSE,u2]);
               }
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_close : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    else if(controller==rs232Arr_Fixture2){
        for(int i=0; i<4; i++)
        {
            r=rs232Arr_Fixture2[i];
            for (int j=0; j<[arr count]; j++) {
                writeFixtureLog_debug(i+5,[NSString stringWithFormat:@"slot-%d send %@ command :%@ .  actuator_index : %d",i+5,kFIXTURECLOSE,[arr objectAtIndex:j],actuator_index]);
                const char * u1= r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
                NSString *u2=[NSString stringWithUTF8String:u1];
                writeFixtureLog_debug(i+5,[NSString stringWithFormat:@"slot-%d receive %@ :%@",i+5,kFIXTURECLOSE,u2]);
            }
            
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_close : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
   */
    id list = [cmd objectForKey:kFIXTURECLOSE];
    NSArray * arr = (__bridge NSArray*)list;
    
    if (controller==rs232Arr_Fixture1) {
        for (int j=0; j<[arr count]; j++) {
            rs232Arr_Fixture1[0]->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_close : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    else if(controller==rs232Arr_Fixture2){
        for (int j=0; j<[arr count]; j++) {
            rs232Arr_Fixture2[0]->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
            
        }
        writeFixtureLog([NSString stringWithFormat:@"fixture_close : 0 , actuator_index : %d , controller : %d \r\n",actuator_index,(controller==rs232Arr_Fixture1? 0:1)]);
        return 0;
    }
    return 0;
    
}


int set_usb_power(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kUSBPOWERON : kUSBPOWEROFF),site);
}

int set_battery_power(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kBATTERYPOWERON : kBATTERYPOWEROFF),site);
}

int set_usb_signal(void* controller, RELAY_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kUSBSIGNALON : kUSBSIGNALOFF),site);
}

int set_uart_signal(void* controller, RELAY_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kUARTSIGNALON : kUARTSIGNALOFF),site);
}

int set_apple_id(void* controller, RELAY_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kAPPLEIDON : kAPPLEIDOFF),site);
}

int set_conn_det_grounded(void* controller, RELAY_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kCONNDETGNDON : kCONNDETGNDOFF),site);
}

int set_hi5_bs_grounded(void* controller, RELAY_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kHI5ON : kHI5OFF),site);
}

int set_dut_power(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kDUTPOWERON : kDUTPOWEROFF),site);
}

int set_dut_power_all(void* controller, POWER_STATE action)
{
    return executeAllAction(controller,(action==0 ? kDUTPOWERON : kDUTPOWEROFF));
}

int set_force_dfu(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kFORCEDFUON : kFORCEDFUOFF), site);
}

int set_force_diags(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kFORCEDIAGSON : kFORCEDIAGSOFF), site);
}

int set_force_iboot(void* controller, POWER_STATE action, int site)
{
    return executeAction(controller,(action==0 ? kFORCEIBOOTON : kFORCEIBOOTOFF), site);
}

int set_led_state(void* controller, LED_STATE action, int site)
{
    /*if (site<1)
        return -1;

    NSString * key = kOFF;
    switch (action) {
        case PASS:
            key = kPASS;
            break;
        case FAIL:
            key = kFAIL;
            break;
        case INPROGRESS:
            key = kINPROCESS;
            break;
        case FAIL_GOTO_FA:
            key = kFAILGOTOFA;
            break;
        case PANIC:
            key = kPANIC;
            break;
        default:
            break;
    }
    writeFixtureLog([NSString stringWithFormat:@"set_led_state %@ start , controller : %d , site : %d",key,(controller==rs232Arr_Fixture1? 0:1),site]);

    id list = [cmd objectForKey:kLEDSTATE];
    int st=0;
    if(list)
    {
        id cmdArr = [(NSDictionary*)list objectForKey:key];
        
        
        
        if(cmdArr)
        {
            NSArray * arr = (NSArray*)cmdArr;
            
            CRS232 * r = nil;//rs232Arr[site-1];
            if (controller==rs232Arr_Fixture1) {
                r=rs232Arr_Fixture1[site-1];
                st=site;
            }
            else if (controller==rs232Arr_Fixture2)
            {
                r=rs232Arr_Fixture2[site-1];
                st=site+4;
            }
            if (r==nil) {
                return -1;
            }

            for (int j=0; j<[arr count]; j++)
            {
                r->WriteReadString([[arr objectAtIndex:j]UTF8String], 1000);
                writeFixtureLog_debug(st,[NSString stringWithFormat:@"slot-%d : set_led_state : %@ . Command : %@\r\n",st,key,[arr objectAtIndex:j]]);
            }
        }
    }
    writeFixtureLog([NSString stringWithFormat:@"set_led_state %@ : 0 , controller : %d , site : %d \r\n",key,(controller==rs232Arr_Fixture1? 0:1),site]);
     */
    return 0;
}
int set_led_state_all(void* controller, LED_STATE action)
{
    //for (int i=0; i<g_SLOTS; i++) {
    for (int i=0; i<4; i++) {
        set_led_state(controller, action, i+1);
    }
    return 0;
}

//************* section:status functions *******************
//when the actuator is in motion and not yet settled, neither is_engage nor is_disengage should return true
bool is_fixture_engaged(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_engaged : YES , controller : %d , actuator_index : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),actuator_index]);
    return YES;
}

bool is_fixture_disengaged(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_disengaged : YES , controller : %d , actuator_index : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),actuator_index]);
    return YES;
}

bool is_fixture_closed(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_closed : YES , controller : %d , actuator_index : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),actuator_index]);
    return YES;
}

bool is_fixture_open(void* controller, int actuator_index)
{
    writeFixtureLog([NSString stringWithFormat:@"is_fixture_open : YES , controller : %d , actuator_index : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),actuator_index]);
    return YES;
}

POWER_STATE usb_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"usb_power : TURN_ON , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return TURN_ON;
}
POWER_STATE battery_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"battery_power : TURN_ON , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return TURN_ON;
}

POWER_STATE force_dfu(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"force_dfu : TURN_ON , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return TURN_ON;
}

RELAY_STATE usb_signal(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"usb_signal : CLOSE_RELAY , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return CLOSE_RELAY;
}

RELAY_STATE uart_signal(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"uart_signal : CLOSE_RELAY , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return CLOSE_RELAY;
}

RELAY_STATE apple_id(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"apple_id : CLOSE_RELAY , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return CLOSE_RELAY;
}

RELAY_STATE conn_det_grounded(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"conn_det_grounded : CLOSE_RELAY , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return CLOSE_RELAY;
}

RELAY_STATE hi5_bs_grounded(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"hi5_bs_grounded : CLOSE_RELAY , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return CLOSE_RELAY;
}

POWER_STATE dut_power(void* controller, int site)
{
    writeFixtureLog([NSString stringWithFormat:@"dut_power : TURN_ON , controller : %d , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    return TURN_ON;
}

bool is_board_detected(void* controller, int site)
{
//    pthread_t pth_id;
//    //pthread_create(&pth_id, NULL,sendDetectCmd, NULL);
//    if(pthread_create(&pth_id,NULL,sendDetectCmd,NULL))
//    {
//    
//    }
    
    writeFixtureLog([NSString stringWithFormat:@"is_board_detected start , controller : %d , site : %d",(controller==rs232Arr_Fixture1? 0:1),site]);
    CRS232 * r=nil;
    NSString *m_cmd=[NSString stringWithFormat:@"mlb_con_det %d",site];
    if (controller==rs232Arr_Fixture1)
    {
        r=rs232Arr_Fixture1[0];
        const char *u=r->WriteReadString([m_cmd UTF8String], 1000);
        NSString *str=[NSString stringWithCString:u encoding:NSUTF8StringEncoding];
        if ([str containsString:@"YES"])
        {
            writeFixtureLog([NSString stringWithFormat:@"is_board_detected : YES , controller : 0 , site : %d\r\n",site]);
            return YES;
        }
        else
        {
            writeFixtureLog([NSString stringWithFormat:@"is_board_detected : NO , controller : 0 , site : %d\r\n",site]);
            return NO;
        }
        
    }else if(controller==rs232Arr_Fixture2)
    {
        r=rs232Arr_Fixture2[0];
        const char *u=r->WriteReadString([m_cmd UTF8String], 1000);
        NSString *str=[NSString stringWithCString:u encoding:NSUTF8StringEncoding];
        
        if ([str containsString:@"YES"])
        {
            writeFixtureLog([NSString stringWithFormat:@"is_board_detected : YES, controller : 1 , site : %d\r\n",site]);
            return YES;
        }
        else
        {
            writeFixtureLog([NSString stringWithFormat:@"is_board_detected : NO, controller : 1 , site : %d\r\n",site]);
            return NO;
        }
    }
    
    writeFixtureLog([NSString stringWithFormat:@"is_board_detected : NO , controller : %d , site : %d\r\n",(controller==rs232Arr_Fixture1? 0:1),site]);
    
    return NO;
   
}


void setup_event_notification(void* controller, void* event_ctx, fixture_event_callback_t on_fixture_event, stop_event_notfication_callback_t on_stop_event_notification)
{
    /*if (controller == NULL || event_ctx == NULL ||
        on_fixture_event == NULL || on_stop_event_notification == NULL)
    {
        NSLog(@"setup_event_notification error: parameter error!");
        return;
    }
   */
    
    if (controller==rs232Arr_Fixture1)
    {
       
            NSLog(@"----do callback carrier 1--");
            writeFixtureLog_debug(1,[NSString stringWithFormat:@"slot-%d : setup_event_notification , event_ctx: %@, site : %d\r\n",1,event_ctx,1]);
            rs232Arr_Fixture1[0]->Set_Event_Callback(on_fixture_event,rs232Arr_Fixture1,event_ctx,1);
            rs232Arr_Fixture1[0]->Set_Stop_Callback(on_stop_event_notification, event_ctx);
            writeFixtureLog([NSString stringWithFormat:@"setup_event_notification , controller : %d , event_ctx : %@ , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),event_ctx,-1]);
        
    }
    if (controller==rs232Arr_Fixture2)
    {
        
            NSLog(@"----do callback carrier 2--");
            writeFixtureLog_debug(5,[NSString stringWithFormat:@"slot-%d : setup_event_notification , event_ctx : %@ , site : %d\r\n",5,event_ctx,5]);
            rs232Arr_Fixture2[0]->Set_Event_Callback(on_fixture_event,rs232Arr_Fixture2,event_ctx,1);
            rs232Arr_Fixture2[0]->Set_Stop_Callback(on_stop_event_notification, event_ctx);
            writeFixtureLog([NSString stringWithFormat:@"setup_event_notification , controller : %d , event_ctx : %@ , site : %d \r\n",(controller==rs232Arr_Fixture1? 0:1),event_ctx,-1]);
        
    }
    
    
}

