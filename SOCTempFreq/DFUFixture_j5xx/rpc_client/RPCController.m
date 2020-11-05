//
//  RPCController.m
//  DFUFixture
//
//  Created by RyanGao on 2020/10/6.
//  Copyright © 2020 RyanGao. All rights reserved.
//

#import "RPCController.h"
#import "GeneralConfig.h"

#define kRPCClientRequester           @"requester"
#define kRPCClientReceiver            @"receiver"

@implementation RPCController
@synthesize m_Clients = _m_Clients;

-(instancetype)init
{
    self = [super init];
    if (self)
    {
        ENDPOINT = [[NSMutableDictionary alloc] init];
        NON_EXISTING_ENDPOINT = [[NSMutableDictionary alloc] init];
        [ENDPOINT setValue:@"tcp://127.0.0.1:5556" forKey:kRPCClientRequester];
        [ENDPOINT setValue:@"tcp://127.0.0.1:15556" forKey:kRPCClientReceiver];
        [NON_EXISTING_ENDPOINT setValue:@"tcp://127.0.0.1:5555" forKey:kRPCClientRequester];
        [NON_EXISTING_ENDPOINT setValue:@"tcp://127.0.0.1:15555" forKey:kRPCClientReceiver];
        m_status = -1;
    }
    return self;
    
}

-(instancetype)initWithSlots:(int)slots withAddr:(NSArray *)devAddrArr
{
    self = [super init];
    if (self)
    {
        ENDPOINT = [[NSMutableDictionary alloc] init];
        NON_EXISTING_ENDPOINT = [[NSMutableDictionary alloc] init];
        [ENDPOINT setValue:@"tcp://127.0.0.1:5556" forKey:kRPCClientRequester];
        [ENDPOINT setValue:@"tcp://127.0.0.1:15556" forKey:kRPCClientReceiver];
        [NON_EXISTING_ENDPOINT setValue:@"tcp://127.0.0.1:5555" forKey:kRPCClientRequester];
        [NON_EXISTING_ENDPOINT setValue:@"tcp://127.0.0.1:15555" forKey:kRPCClientReceiver];
        m_status = -1;
        [self Open:devAddrArr withSlot:slots];
    }
    return self;
}

-(int)Open:(NSString *)devAddr
{
    if (self.m_Clients)
    {
        [self.m_Clients removeAllObjects];
    }
    else
    {
        self.m_Clients = [[NSMutableArray alloc] init];
    }
    int retries = 4;
    int interval_ms = 1000;
    for (int i=0; i<= retries; i++)
    {
        RPCClientWrapper *m_Client = [RPCClientWrapper initWithStringEndpoint:[NSString stringWithFormat:@"tcp://%@",devAddr]];
        if (m_Client)
        {
            m_status = 0;
            [self.m_Clients addObject:m_Client];
            [self syncXavierClock];
            return 0;
        }
        usleep(1000*interval_ms);
    }
    NSLog(@"RPCClientWrapper cannot initial successful, retry: %d times", retries);
    m_status = -1;
    [self syncXavierClock];
    return m_status;
}

-(NSString *)executePingCommand:(NSString *)ip
{
    //NSLog(@"ping: %@",ip);
    NSTask *task;
    task = [[NSTask alloc] init];
    [task setLaunchPath: @"/sbin/ping"];
    
    NSArray *arguments;
    arguments = [NSArray arrayWithObjects: @"-c1", @"-W1",ip,nil];
    [task setArguments: arguments];
    
    NSPipe *pipe;
    pipe = [NSPipe pipe];
    [task setStandardOutput: pipe];
    
    NSFileHandle *file;
    file = [pipe fileHandleForReading];
    
    [task launch];
    
    NSData *data;
    data = [file readDataToEndOfFile];
    
    NSString *string;
    string = [[NSString alloc] initWithData: data encoding: NSUTF8StringEncoding];
    //[task release];
    [file closeFile];
    return string;
}

-(int)Open:(NSArray *)devAddrArr withSlot:(int) slots
{
    if (self.m_Clients)
    {
        [self.m_Clients removeAllObjects];
    }
    else
    {
        self.m_Clients = [[NSMutableArray alloc] init];
    }
    
    NSString *ipAdd = devAddrArr[0];
    NSArray * strArray = [ipAdd componentsSeparatedByString:@":"];
    NSString *retPing = [self executePingCommand:strArray[0]];
    if ([retPing rangeOfString:@"100.0% packet loss"].location != NSNotFound)
    {
        NSLog(@"%@",retPing);
        m_status = -1;
        return m_status;
    }
    
    int retries = 4;
    int interval_ms = 1000;
    
    m_status = 0;
    for (int i=0; i<slots; i++)
    {
        for (int j=0; j<= retries; j++)
        {
            RPCClientWrapper *m_Client = [RPCClientWrapper initWithStringEndpoint:[NSString stringWithFormat:@"tcp://%@",devAddrArr[i]]];
            if (m_Client)
            {
                m_status ++;
                [self.m_Clients addObject:m_Client];
                break;
            }
            usleep(1000*interval_ms);
        }
    }
    
    if (m_status ==slots)
    {
        m_status =0;
    }
    else
    {
        NSLog(@"RPCClientWrapper cannot initial successful, retry: %d times...", retries);
        m_status = -1;
    }
    [self uartShutdown:1];
    [self syncXavierClock];
    return m_status;
}

- (void)syncXavierClock
{
    system("/usr/bin/expect /Users/gdlocal/Library/Atlas/supportFiles/syncXavierClock.exp");
    sleep(0.5);
}

-(NSString *)WriteReadString:(NSString *)cmd atSite:(int)site timeOut:(int)timeout
{
    if(m_status<0)
    {
        return @"init error";
    }
    
    NSArray *arrCmd = nil;
    if ([cmd containsString:@"]"])
    {
        NSArray *arrSub= [cmd componentsSeparatedByString:@"]"];
        arrCmd = [arrSub[1] componentsSeparatedByString:@"("];
    }
    else
    {
        arrCmd = [cmd componentsSeparatedByString:@"("];
    }
    if ([arrCmd count]<2)
    {
        return @"command format error\r\n";
    }
    
    NSString *method = arrCmd[0];
    NSString * strArgs = [arrCmd[1] stringByReplacingOccurrencesOfString:@")" withString:@""];
    NSArray *arrArgs = [strArgs componentsSeparatedByString:@","];
  
    NSMutableDictionary* dicKwargs = [NSMutableDictionary dictionary];
    [dicKwargs setObject:@(timeout) forKey:@"timeout_ms"];
    NSString *rpc_args = [arrArgs componentsJoinedByString:@" "];
    NSLog(@"[rpc_client] %@ %@  . Method: %@, args: %@, kwargs: nil,timeout_ms: %d",method,rpc_args,method,strArgs,timeout);
    
    if ([[arrArgs[0] stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceCharacterSet]] isEqualToString:@""] )
    {
        arrArgs = nil;
    }
    NSError *error = nil;
    id rtn = [self.m_Clients[site] rpc:method args:arrArgs kwargs:dicKwargs error:&error];
    NSString* receiver = [NSString stringWithFormat:@"%@",rtn];
    if (error)
    {
        receiver = [NSString stringWithFormat:@"%@\r\nError:%@",receiver,error];
    }
    return receiver;
}

-(int)getCylinderStatus:(NSString *)cmd
{
    NSString *ret = [self WriteReadString:cmd atSite:0 timeOut:3000];
    if ([ret containsString:@"down"])
    {
        return 0;
    }
    return -1;
}
-(void)uartShutdown:(int)site
{
    NSString *ret = [self WriteReadString:@"uart_SoC_shutdown_all()" atSite:0 timeOut:3000];
    NSLog(@"uartShutdown,[cmd]: uart_SoC_shutdown_all, [result]: %@",ret);
    
}

-(int)Close
{
    if(m_status<0)
    {
        NSLog(@"error for init");
        return -1;
    }
    for (int i=0; i<[self.m_Clients count]; i++)
    {
        [self.m_Clients[i] shutdown];
    }
    return 0;
}

-(NSString*)getHostModel
{
    return [[GeneralConfig instance] macmini_hardware_version];
}

-(NSString*)usb_locationID:(int)index
{
    return [[GeneralConfig instance] locationID:index];
}

- (NSString *)uartPath:(int)index
{
    NSString *devicePath = @"";
    devicePath = [[GeneralConfig instance] uartPath:index];
    return devicePath;
}



//-(void)dealloc
//{
//    [ENDPOINT release];
//    [NON_EXISTING_ENDPOINT release];
//    [super dealloc];
//}

@end
