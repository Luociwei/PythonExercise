//
//  CRS232.h
//  RS232
//
//  Created by IvanGan on 16/4/9.
//  Copyright © 2016年 IvanGan. All rights reserved.
//

#ifndef CRS232_h
#define CRS232_h

#import <Foundation/Foundation.h>
#include <stdio.h>
#include "SerialPort.h"
#include <string>

#import <pthread.h>

typedef void (*fixture_event_callback_t)(const char* sn, void *controller, void* event_ctx, int site, int event_type);
typedef void (*stop_event_notfication_callback_t)(void* ctx);

class CRS232 : CSerialPort
{
public:
    CRS232();
    ~CRS232();
public:
    int Open(const char * dev, const char * opt);//opt:"9600,8,n,1"
    int Close();
    
    int WriteString(const char * buffer);
    int WriteBytes(unsigned char * ucData, int len);
    int WriteStringBytes(const char * szData);//"0xFF,0xFE,..."
    
    const char * ReadString();
    const char * ReadBytes();
    const char * ReadStringBytes();
    void ClearBuffer();
    int SetDetectString(const char * det);
    int WaitDetect(int timeout);//msec
    
    const char * WriteReadString(const char * buffer,int timeout);
//    
//    int SetRepOpt(int needReply, int timeout=3000);//set bNeedReplay
//    int SetPubOpt(int needPub);//it will publish command which is from function writeXXX
//    
    int WritePassControlBit(int stationid,char * szCmd);

    int Set_Event_Callback(fixture_event_callback_t cb, void *ctoller,void * ctx,int site);
    int Set_Stop_Callback(stop_event_notfication_callback_t cb, void * ctx);
    void * m_event_context;
    void * m_controller;
    fixture_event_callback_t m_event_CallBack;
    NSString *start_flag;
protected:
//    virtual void * OnRequest(void * pdata, long len);
    virtual void * didReceiveData(void * data, long len);
    //virtual void * didReceiveData2(void * data, long len);

private:
    int m_status;
    int site_number;
    pthread_mutex_t m_mutex;
    pthread_mutex_t m_lockOperate;
    
    NSMutableString * m_strBuffer;
    NSMutableData * m_DataBuffer;
    NSMutableString * m_strDetect;
    NSMutableString * m_Return;
    //fixture_event_callback_t m_event_CallBack;
    void m_event_CallBack_2();
    //void * m_event_context;
    stop_event_notfication_callback_t m_stop_CallBack;
    void * m_stop_context;
    
//    bool bNeedZmq;  //YES: will pub data from COM
                    //this will initial in "CreatIPC".
    
//    bool bNeedReply; // YES: will reply data from data, or it will return "OK" or "Fail"
//    int iTimeout;//msec
//    bool bNeedPub;

};

#endif /* CRS232_hpp */
