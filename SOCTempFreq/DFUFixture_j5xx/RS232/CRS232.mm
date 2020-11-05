//
//  CRS232.cpp
//  RS232
//
//  Created by IvanGan on 16/4/9.
//  Copyright © 2016年 IvanGan. All rights reserved.
//

#include "CRS232.h"

//#include "zmq.h"

#include <iostream>
#include <sstream>

#include <unistd.h>


//NSLock * g_LockCB = [[NSLock alloc]init];

CRS232::CRS232()
{
    pthread_mutex_init(&m_mutex,nil);
    pthread_mutex_init(&m_lockOperate, nil);
    m_strBuffer = [[NSMutableString alloc]init];
    m_DataBuffer = [[NSMutableData alloc]init];
    m_strDetect = [[NSMutableString alloc]init];
    m_Return = [[NSMutableString alloc]init];
//    bNeedZmq = false;
//    bNeedReply = false;
//    bNeedPub = false;
//    iTimeout = 3000;
    m_event_context = nil;
    m_controller=nil;
    m_event_CallBack = nil;
    m_stop_context = nil;
    m_stop_CallBack = nil;
    m_status = -1;
    site_number=-1;
    start_flag=[[NSString alloc]init];
    
}

CRS232::~CRS232()
{
    pthread_mutex_destroy(&m_mutex);
    pthread_mutex_destroy(&m_lockOperate);
    [m_strDetect release];
    [m_strBuffer release];
    [m_DataBuffer release];
    [m_Return release];
    [start_flag release];
}

//int CRS232::CreateIPC(const char * reply, const char * publish)
//{
//    CPubliser::bind(publish);
//    CReplier::bind(reply);
//    bNeedZmq = true;
//    return 0;
//}

int CRS232::Set_Event_Callback(fixture_event_callback_t cb, void *ctoller,void * ctx,int site)
{
    m_event_CallBack = cb;
    m_controller=ctoller;
    m_event_context = ctx;
    site_number=site;
    return 0;
}

int CRS232::Set_Stop_Callback(stop_event_notfication_callback_t cb, void * ctx)
{
    m_stop_CallBack = cb;
    m_stop_context = ctx;
    return 0;
}

void * CRS232::didReceiveData(void * data, long len)
{
    if(len < 0)
        return nullptr;
    pthread_mutex_lock(&m_mutex);
//    if(bNeedZmq)
//        Pulish(data, len);
    [m_DataBuffer appendBytes:(Byte*)data length:len];
    char * p = (char *)data;
    for(int i=0; i<len; i++)
    {
        if(p[i] == '\0')
            p[i] = '.';
    }
    NSString * str = [[NSString alloc]initWithBytes:data length:len encoding:NSUTF8StringEncoding];
    if(str)
        [m_strBuffer appendString:str];
    [str release];
    pthread_mutex_unlock(&m_mutex);

    //if([m_strBuffer containsString:@"START"] && m_event_CallBack)
    if([m_strBuffer containsString:@"start"])
    {
        //[NSThread detachNewThreadSelector:@selector(m_event) toTarget:self withObject:nil];
        start_flag=@"1";
        dispatch_async(dispatch_get_main_queue(), ^{
            m_event_CallBack("TBD",m_controller,m_event_context,-1,0);
        });
        //m_event_CallBack("TBD",m_controller,m_event_context,-1,0);  //Darren request set -1
        //m_event_CallBack("",m_controller,m_event_context,site_number,0);
        [m_strBuffer setString:@""];
        [m_DataBuffer setLength:0];
    }
   // if([m_strBuffer containsString:@"STOP"] && m_event_CallBack)
    if([m_strBuffer containsString:@"stop"])
    {
        //stop_flag=@"1";
        //m_stop_CallBack(m_stop_context);
        [m_strBuffer setString:@""];
        [m_DataBuffer setLength:0];
    }

    return nullptr;
}


void CRS232::m_event_CallBack_2()
{
    
}
//int CRS232::SetRepOpt(int needReply, int timeout)
//{
//    bNeedReply = (needReply>0) ? YES : NO;
//    iTimeout = timeout;
//    return 0;
//}
//
//int CRS232::SetPubOpt(int needPub)
//{
//    bNeedPub = (needPub>0) ? YES : NO;
//    return 0;
//}

//void * CRS232::OnRequest(void * pData, long len)
//{
//    pthread_mutex_lock(&m_lockOperate);
//    if(bNeedPub)
//        Pulish(pData,len);
//    int err = CSerialPort::write(pData, len);
//    if(bNeedReply == NO)
//        CReplier::SendStrig((err>=0)?"OK":"Fail");
//    else
//    {
//        if([m_strDetect length]>0)
//            WaitDetect(iTimeout);
//        CReplier::SendStrig(ReadString());
//    }
//    pthread_mutex_unlock(&m_lockOperate);
//    return nullptr;
//}

int CRS232::Open(const char * dev, const char * opt)//opt:"9600,8,n,1"
{
    //int set_opt(int nSpeed, int nBits, char nEvent, int nStop);
    NSString * str = [NSString stringWithUTF8String:opt];
    NSLog(@"%@",str);
    NSArray * arr = [str componentsSeparatedByString:@","];
    int nSpeed = 9600;
    int nBits = 8;
    char nEvent = 'n';
    int nStop = 1;
    if([arr count]==4)
    {
        nSpeed = [[arr objectAtIndex:0]intValue];
        nBits = [[arr objectAtIndex:1]intValue];
        const char * tmp = [[arr objectAtIndex:2]UTF8String];
        nEvent = tmp[0];
        nStop = [[arr objectAtIndex:3]intValue];
    }
    int ret = CSerialPort::connect(dev);
    if (ret<0)
    {
        return ret;
    }
    ret = CSerialPort::set_opt(nSpeed, nBits, nEvent, nStop);
    m_status = ret;
    return ret;
}

int CRS232::WriteString(const char * buffer)
{
    if(m_status<0)
        return m_status;
    NSString * str = [NSString stringWithFormat:@"%s\r\n", buffer];
//    if(bNeedZmq && bNeedPub)
//        Pulish((void*)[str UTF8String], [str length]);
    return CSerialPort::write((void*)[str UTF8String], [str length]);
}

int CRS232::WriteBytes(unsigned char * ucData, int len)
{
//    if(bNeedZmq && bNeedPub)
//        Pulish((void*)ucData, len);
    if(m_status<0)
        return m_status;
    return CSerialPort::write((void*)ucData, len);
}

int CRS232::WriteStringBytes(const char * szData)//"0xFF,0xFE,..."
{
    if(m_status<0)
        return m_status;
    if(szData == NULL) return -1;
    if(strlen(szData)<=0) return -2;
    NSArray * arr = [[NSString stringWithUTF8String:szData] componentsSeparatedByString:@","];
    if([arr count]< 1) return -3;
    int size = [arr count];
    unsigned char * ucData = new unsigned char [size];
    for(int i=0; i<size; i++)
    {
        NSScanner * scanner = [NSScanner scannerWithString:[arr objectAtIndex:i]];
        unsigned int tmp;
        [scanner scanHexInt:&tmp];
        ucData[i] = tmp;
    }
//    if(bNeedZmq && bNeedPub)
//        Pulish((void*)ucData, size);
    CSerialPort::write((void*)ucData, size);
    return 0;
}

void CRS232::ClearBuffer()
{
    [m_strBuffer setString:@""];
}

const char * CRS232::ReadString()
{
    if(m_status<0)
        return nullptr;
    [NSThread sleepForTimeInterval:0.01];
    pthread_mutex_lock(&m_mutex);
    if(m_strBuffer && [m_strBuffer length]>0)
    {
        [m_Return setString:m_strBuffer];
        [m_strBuffer setString:@""];
    }
    else
        [m_Return setString:@""];
    [m_DataBuffer setLength:0];
    pthread_mutex_unlock(&m_mutex);
    return [m_Return UTF8String];
}

const char * CRS232::ReadBytes()
{
    if(m_status<0)
        return nullptr;
    if([m_DataBuffer length]>0)
    {
        NSData * data = [NSData dataWithData:m_DataBuffer];
        [m_DataBuffer setLength:0];
        [m_strBuffer setString:@""];
        return (const char*)[data bytes];
    }
    else
        return NULL;
    
}

const char * CRS232::ReadStringBytes()
{
    if(m_status<0)
        return nullptr;
    NSUInteger len = [m_DataBuffer length];
    if(len>0)
    {
        Byte * pByte = (Byte*)[m_DataBuffer bytes];
        [m_Return setString:@""];
        for(int i= 0; i<[m_DataBuffer length]-1; i++)
        {
            [m_Return appendFormat:@"0x%02X,",pByte[i]];
        }
        [m_Return appendFormat:@"0x%02X",pByte[len -1]] ;
        [m_DataBuffer setLength:0];
        [m_strBuffer setString:@""];
        return [m_Return UTF8String];
    }
    else
        return NULL;
}


int CRS232::WaitDetect(int timeout)
{
    int r = -1;
    //    NSLog(@" * * * * * \ndylib Detect :%@ * * * * * \n",m_strStringToDetect);
    NSTimeInterval starttime = [[NSDate date]timeIntervalSince1970];
    double tm = (double)timeout/1000.0;
    NSLog(@"starting to wait : %@",m_strDetect);
    while (1)
    {
        NSTimeInterval now = [[NSDate date]timeIntervalSince1970];
        if ((now-starttime)>=tm)
        {
            r = -2;
            break;
        }
        
        pthread_testcancel();       //if is cancel,exist current loop.
        
        //if([m_strBuffer containsString:m_MutableDetect])
        pthread_mutex_lock(&m_mutex);
        NSRange range  = [m_strBuffer rangeOfString:m_strDetect];
        pthread_mutex_unlock(&m_mutex);
        
        if (range.location != NSNotFound)
        {
            r = 0;
            break;
        }
        
        [[NSRunLoop currentRunLoop] runMode:NSDefaultRunLoopMode beforeDate:[NSDate date]];
        [NSThread sleepForTimeInterval:0.01];
    }
    
    NSLog(@"waiting finished : %d",r);
    return r;  //cancel
}

int CRS232::SetDetectString(const char * det)
{
    [m_strDetect setString:[NSString stringWithUTF8String:det]];
    return 0;
}

const char * CRS232::WriteReadString(const char * buffer,int timeout)
{
    if(m_status<0)
        return nullptr;
    NSLog(@"< write string > : %s, %d",buffer, timeout);
    WriteString(buffer);
    WaitDetect(timeout);
//    pthread_mutex_lock(&m_lockOperate);
    NSString * str = [NSString stringWithUTF8String:ReadString()];
//    pthread_mutex_unlock(&m_lockOperate);
    NSLog(@"< receiver > : %@",str);
    return [str UTF8String];
}

int CRS232::Close()
{
//    CPubliser::close();
//    CReplier::close();
    CSerialPort::close();
    return 0;
}




