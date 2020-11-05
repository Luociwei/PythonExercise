//
//  main.m
//  test
//
//  Created by IvanGan on 16/10/18.
//  Copyright © 2016年 IvanGan. All rights reserved.
//

#import <Foundation/Foundation.h>

#import "DFUFixture.h"
#import "USBDevice.h"
#import "IAFileHandle.h"
#include <pthread.h>
#import "plistParse.h"

#define Debug1

#define THREAD_NUM 10
void *test(void *args) {
    printf("tid : i say 'Hello'.\n");
    return NULL;
}


void on_fixture_event(const char* sn, void *controller, void* event_ctx, int site, int event_type)
{
    //[NSThread sleepForTimeInterval:3];
    NSLog(@"---fixture event call back : %s, %d, %d",sn, site,event_type);
//    for (int i=1; i<3; i++) {
//        sleep(1);
//        NSLog(@"---my fixture event call back: %d",i);
//    }
//    NSLog(@"--=====1 %d",is_board_detected(controller, 1));
//    NSLog(@"--======2 %d",is_board_detected(controller, 2));
//    NSLog(@"--=====3 %d",is_board_detected(controller, 3));
//    NSLog(@"--=====4 %d",is_board_detected(controller, 4));
    
}

void on_stop_event_notification(void* ctx)
{
    NSLog(@"stop notification : here");
}



#import "plistParse.h"
int main()
{
//    [plistParse checkLogFileExist:@"/vault/atlas/FixtureLog/Suncode/11.txt"];
//    NSLog(@"-------");
//    NSString *filePath =@"/vault/Suncode_log/BarCode.txt";
//    NSFileHandle* fh=[NSFileHandle fileHandleForWritingAtPath:filePath];
//    [fh seekToEndOfFile];
//    [fh writeData:[[NSString stringWithFormat:@"%@  %@\r\n",@"testTime",@"-0000-===="] dataUsingEncoding:NSUTF8StringEncoding]];
//    [fh closeFile];
//    NSFileHandle* fh2=[NSFileHandle fileHandleForWritingAtPath:filePath];
//    [fh2 seekToEndOfFile];
//    [fh2 writeData:[[NSString stringWithFormat:@"%@  %@\r\n",@"testTime",@"-1111-===="] dataUsingEncoding:NSUTF8StringEncoding]];
//    [fh2 closeFile];
//    NSFileHandle* fh3=[NSFileHandle fileHandleForWritingAtPath:filePath];
//    [fh3 seekToEndOfFile];
//    [fh3 writeData:[[NSString stringWithFormat:@"%@  %@\r\n",@"testTime",@"-2222-===="] dataUsingEncoding:NSUTF8StringEncoding]];
//    [fh3 closeFile];
    void * cf = create_fixture_controller(0);
//    NSLog(@"--=====1 %d",fixture_open(cf,1));
//
//    NSLog(@"===>>>%p",cf);
    // NSLog(@"--=====1 %d",reset(cf));
//    NSLog(@"--=====1 %d",fixture_close(cf,1));
//    NSLog(@"[init] : %d",init(cf));
    NSLog(@"[reset] : %d",reset(cf));
//    release_fixture_controller(cf);
//    NSLog(@"--=====1 %d",set_force_dfu(cf,TURN_ON,1));
    //NSLog(@"--=====1 %d",set_force_diags(cf,TURN_ON,1));
}
          
          
          
          
          
int main2222() {

#ifdef Debug
    NSLog(@"sss");
#endif
       NSLog(@"s222ss");
//    pthread_t myThread;
//    int err=pthread_create(&myThread,NULL,test,0);
//    if(err) {
//                    printf("Can't create thread \n");
//        
//                }
    
    void * cf = create_fixture_controller(1);
    
    NSLog(@"===>>>%p",cf);
//    NSLog(@"--=====1 %d",fixture_close(cf,1));
    //NSLog(@"--=====1 %d",fixture_open(cf,1));
//    NSLog(@"[init] : %d",init(cf));
//    NSLog(@"[reset] : %d",reset(cf));
    NSLog(@"--=====1 %d",fixture_close(cf,1));
//    NSLog(@"--=====1 %d",set_force_dfu(cf,TURN_ON,1));
    
//    release_fixture_controller(cf);
    
   // void * cf2 = create_fixture_controller(1);
//    NSLog(@"--1 %s",get_uart_path(cf, 1));
//    NSLog(@"--2 %s",get_uart_path(cf, 2));
//    NSLog(@"--3 %s",get_uart_path(cf, 3));
//    NSLog(@"--4 %s",get_uart_path(cf, 4));
//    NSLog(@"--5 %s",get_uart_path(cf2, 1));
//    NSLog(@"--6 %s",get_uart_path(cf2, 2));
//    NSLog(@"--7 %s",get_uart_path(cf2, 3));
//    NSLog(@"--8 %s",get_uart_path(cf2, 4));
//    NSLog(@"--1 %s",get_usb_location(cf, 1));
//    NSLog(@"--2 %s",get_usb_location(cf, 2));
//    NSLog(@"--3 %s",get_usb_location(cf, 3));
//    NSLog(@"--4 %s",get_usb_location(cf, 4));
//    NSLog(@"--5 %s",get_usb_location(cf2, 1));
//    NSLog(@"--6 %s",get_usb_location(cf2, 2));
//    NSLog(@"--7 %s",get_usb_location(cf2, 3));
//    NSLog(@"--8 %s",get_usb_location(cf2, 4));
    
 //   setup_event_notification(cf,0,on_fixture_event,on_stop_event_notification);

//        NSLog(@"--=====1 %d",is_board_detected(cf, 1));
//        NSLog(@"--======2 %d",is_board_detected(cf, 2));
//        NSLog(@"--=====3 %d",is_board_detected(cf, 3));
//        NSLog(@"--=====4 %d",is_board_detected(cf, 4));
    
//    NSLog(@"--=====5 %d",is_board_detected(cf2, 1));
//    NSLog(@"--=====6 %d",is_board_detected(cf2, 2));
//    NSLog(@"--=====7 %d",is_board_detected(cf2, 3));
//    NSLog(@"--=====8 %d",is_board_detected(cf2, 4));
    
    
  //  [[NSRunLoop currentRunLoop] run];
    
   
    //release_fixture_controller(cf2);
//    NSLog(@"[set_force_dfu] : %d",set_force_diags(cf,TURN_ON,1));
//    release_fixture_controller(cf);
    
  /*  NSString *a1=@"IA000BLD";
    NSString *a2=@"IA001BLD";
    NSString *usb_location_1=@"";
    NSString *usb_location_2=@"";
    
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
                if ([[array[j] valueForKey:@"SerialNumber"] containsString:a1])
                {
                    NSString *ss_str=[array[j] valueForKey:@"LocationID"][0];
                    usb_location_1=[u_location valueForKey:[ss_str substringWithRange:NSMakeRange(0,[ss_str rangeOfString:@"00"].location-1)]];
                }
                if ([[array[j] valueForKey:@"SerialNumber"] containsString:a2])
                {
                    //usb_location_2=[array[j] valueForKey:@"LocationID"][0];
                    NSString *ss_str=[array[j] valueForKey:@"LocationID"][0];
                    usb_location_2=[u_location valueForKey:[ss_str substringWithRange:NSMakeRange(0,[ss_str rangeOfString:@"00"].location-1)]];
                    
                    
                }
            }
        }
    
    
    NSLog(@"usb_location_1: %@",usb_location_1);
    NSLog(@"usb_location_2: %@",usb_location_2);*/
//    NSString *usb_location_1=@"";
//    NSString *usb_location_2=@"";
//    
//    for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
//        int j=[myindex[1] intValue];
//        if ([myindex[0] containsString:KBladeMCUName])
//        {
//            if ([[array[j] valueForKey:@"SerialNumber"] containsString:a1])
//            {
//                usb_location_1=[array[j] valueForKey:@"LocationID"][0];
//            }
//            if ([[array[j] valueForKey:@"SerialNumber"] containsString:a2])
//            {
//                usb_location_2=[array[j] valueForKey:@"LocationID"][0];
//            }
//        }
//    }
//    NSLog(@"--%@   %@",usb_location_1,usb_location_2);

    
    /*
     
     IA000BLD
     */
    
    
//
//    NSLog(@"-=----------------");
//    
//    for (id myindex in [array valueForKey:@"DeviceFriendlyName"]) {
//        int j=[myindex[1] intValue];
//        if ([myindex[0] containsString:KBladeMCUName])
//            {
//                
//                if (([[array[j] valueForKey:@"SerialNumber"] containsString:@"IA"])&&([[array[j] valueForKey:@"SerialNumber"] containsString:@"BLD"]))
//                {
//                    NSLog(@"---%@",[array[j] valueForKey:@"SerialNumber"]);
//                }
//            }
//    }
//    
    
    
    
    
    return 0;
}















///////
void timer(int sig)
{
    if(SIGALRM == sig)
    {
        printf("timer\n");
        alarm(5);       //we contimue set the timer
    }
    
    return ;
}

void timer2(int sig)
{
    if(SIGALRM == sig)
    {
        printf("timer2=====\n");
        alarm(5);       //we contimue set the timer
    }
    
    return ;
}

int main0090909()
{
   
    signal(SIGALRM, timer2); //relate the signal and function
    alarm(1);       //trigger the timer
    
    getchar();
    
    return 0;
}














void test3(){
    NSString *str = @"123123123这是一个导出的字符串\r\n";
    //文件不存在会自动创建，文件夹不存在则不会自动创建会报错
    NSString *path = @"/Users/RyanGao/Desktop/test_export.txt";
    NSError *error;
    [str writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        NSLog(@"导出失败:%@",error);
    }else{
        NSLog(@"导出成功");
    }
}
void test4(){
    NSString *str = @"2222222这是一个导出的字符串\r\n";
    //文件不存在会自动创建，文件夹不存在则不会自动创建会报错
    NSString *path = @"/Users/RyanGao/Desktop/test_export.txt";
    NSError *error;
    //NSString *fp=[NSHomeDirectory() stringByAppendingPathComponent:path];
    [str writeToFile:path atomically:YES encoding:NSUTF8StringEncoding error:&error];
    if (error) {
        NSLog(@"导出失败:%@",error);
    }else{
        NSLog(@"导出成功");
    }
}


void writeFile()
{
    NSString *path = @"/Users/RyanGao/Desktop/test_export.txt";
    NSString *fp=[NSHomeDirectory() stringByAppendingPathComponent:path];
    NSLog(@"%@",fp);
    NSString *test=@"somethingaaaddddd";
    [test writeToFile:fp atomically:YES encoding:NSUTF8StringEncoding error:nil];
    
}






#define N 100 //设置最大的定时器个数
int i=0,t=1; //i代表定时器的个数；t表示时间，逐秒递增

struct Timer //Timer结构体，用来保存一个定时器的信息
{
    int total_time; //每隔total_time秒
    int left_time; //还剩left_time秒
    int func; //该定时器超时，要执行的代码的标志
}myTimer[N]; //定义Timer类型的数组，用来保存所有的定时器

void setTimer(int t,int f) //新建一个计时器
{
    struct Timer a;
    a.total_time=t;
    a.left_time=t;
    a.func=f;
    myTimer[i++]=a;
}

void timeout() //判断定时器是否超时，以及超时时所要执行的动作
{
    printf("Time: %d\n",t++);
    int j;
    for(j=0;j<i;j++)
    {
        if(myTimer[j].left_time!=0)
            myTimer[j].left_time--;
        else
        {
            switch(myTimer[j].func)
            {      //通过匹配myTimer[j].func，判断下一步选择哪种操作
                case 1:
                    printf("------Timer 1: --Hello Aillo!\n");break;
                case 2:
                    printf("------Timer 2: --Hello Jackie!\n");break;
                case 3:
                    printf("------Timer 3: --Hello PiPi!\n");break;
            }
            myTimer[j].left_time=myTimer[j].total_time; //循环计时
        }
    }
}

int main33333() //测试函数，定义三个定时器
{
    setTimer(3,1);
    setTimer(4,2);
    setTimer(5,3);
    signal(SIGALRM,timeout); //接到SIGALRM信号，则执行timeout函数
    
    while(1)
    {
        sleep(1); //每隔一秒发送一个SIGALRM
        kill(getpid(),SIGALRM);
    }
    return 0;
}

int main21112(int argc, const char * argv[]) {
    @autoreleasepool {
        
//        void * cf = create_fixture_controller(0);
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,1));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,4));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,2));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,3));
//       // NSLog(@"[get_usb_location] : %d",fixture_open(cf, 3));
//        release_fixture_controller(cf);
//        NSObject *object = [[NSObject alloc] init];
//       
//        [NSTimer scheduledTimerWithTimeInterval:5 target:object selector:@selector(timerAction2:) userInfo:nil repeats:YES];
//        [object release];
        
        
//        uint64_t interval=2*NSEC_PER_SEC;
//        dispatch_queue_t queue=dispatch_queue_create("my_queue", 0);
//        dispatch_source_t timer = dispatch_source_create(DISPATCH_SOURCE_TYPE_TIMER, 0, 0, <#dispatchQueue#>);
//        dispatch_source_set_timer(timer, DISPATCH_TIME_NOW, <#intervalInSeconds#> * NSEC_PER_SEC, <#leewayInSeconds#> * NSEC_PER_SEC);
//        dispatch_source_set_event_handler(timer, ^{
//            code to be executed when timer fires
//        });
//        dispatch_resume(timer);
        
     
        
    }
    return 0;
}
//channel 2 is 3

int main3333(int argc, const char * argv[]) {
    @autoreleasepool {
//        NSLog(@"--end--");
//        NSFileHandle* fh=[NSFileHandle fileHandleForWritingAtPath:@"/Users/RyanGao/Desktop/test_export2.txt"];//以只写的方式
//        
//        [fh seekToEndOfFile];//将读写指针设置在文件末尾
//        [fh writeData:[@"gaogao\r\n" dataUsingEncoding:NSUTF8StringEncoding]];//这样就相当于按-a方式写入
//        NSLog(@"--end--");
//        NSFileManager *fm = [NSFileManager defaultManager];
//        NSError *error = nil;
//        BOOL ret1 = [fm createDirectoryAtPath:@"/vault/atlas/" withIntermediateDirectories:NO attributes:nil error:&error];//执行这句话就已经创建目录
//        if (ret1) {
//            NSLog(@"文件夹 创建成功");
//        }else {
//            NSLog(@"文件夹创建失败");
//            NSLog(@"error:%@",error);
//        }
        
        /*
         NSString *pathLogFile=[NSString stringWithFormat:@"/vault/atlas/IAFixture_slot%d_%@.txt",i+1,TimeFile];
         [plistParse checkLogFileExist:pathLogFile];
         NSDateFormatter* DateFomatter = [[NSDateFormatter alloc] init];
         [DateFomatter setDateFormat:@"yyyy_MM_dd"];
         NSString* TimeFile = [DateFomatter stringFromDate:[NSDate date]];
         [DateFomatter release];
         
         */
        
        
        //NSDateFormatter* DateFomatter = [[[NSDateFormatter alloc] init] autorelease];
        NSDateFormatter* DateFomatter = [[NSDateFormatter alloc] init];
        [DateFomatter setDateFormat:@"yyyy/MM/dd HH:mm:ss"];
        NSString* Time0 = [DateFomatter stringFromDate:[NSDate date]];
        
        [DateFomatter setDateFormat:@"yyyy_MM_dd"];
        NSString* Time2 = [DateFomatter stringFromDate:[NSDate date]];
        
        NSFileManager *fm = [NSFileManager defaultManager];
        NSError *error = nil;
        NSString *dfuFixtureLog=[NSString stringWithFormat:@"/vault/atlas/IAFixture_%@.txt",Time2];
        BOOL isExist = [fm fileExistsAtPath:dfuFixtureLog];
        if (!isExist) {
            BOOL ret = [fm createFileAtPath:dfuFixtureLog contents:nil attributes:nil];
            if (ret) {
                NSLog(@"create file is successful");
            }else {
                [fm createDirectoryAtPath:@"/vault/atlas/" withIntermediateDirectories:NO attributes:nil error:&error];
                [fm createFileAtPath:dfuFixtureLog contents:nil attributes:nil];
                NSLog(@"create folder and file is successful");
            }
        }else{
            //NSLog(@"file already exit");
        }
        

        NSFileHandle* fh=[NSFileHandle fileHandleForWritingAtPath:dfuFixtureLog];//以只写的方式
        [fh seekToEndOfFile];//将读写指针设置在文件末尾
        [fh writeData:[[NSString stringWithFormat:@"%@\r\n",Time0] dataUsingEncoding:NSUTF8StringEncoding]];//这样就相当于按-a方式写入
        
        
//        NSArray *arr = @[@"a",@"b",@"b",@"c"];
//        NSString *path = [NSHomeDirectory() stringByAppendingPathComponent:@"/Users/RyanGao/Desktop/test_export.txt"];
//        [arr writeToFile:path atomically:YES];
        
    }
    return 0;
}
int main22(int argc, const char * argv[]) {
    @autoreleasepool {
        // insert code here...
        NSLog(@"Hello, World!");
       // void * cf = create_fixture_controller(1);
        NSLog(@"----------");
      /* NSLog(@"[set_dut_power] : %d",set_dut_power(cf,TURN_ON,1));
         setup_event_notification(cf,0,on_fixture_event,on_stop_event_notification);
        NSLog(@"----------");
         NSLog(@"[set_dut_power] : %d",set_dut_power(cf,TURN_ON,1));
       NSLog(@"[Vender ]: %s",get_vendor());
        NSLog(@"[Serial Number ]: %s",get_serial_number(cf));
        NSLog(@"[version] : %s",get_version(cf));
        NSLog(@"[get_error_message] : %s",get_error_message(0));
        NSLog(@"[init] : %d",init(cf));
        NSLog(@"[reset] : %d",reset(cf));
        NSLog(@"[get_site_count] : %d",get_site_count(cf));
        NSLog(@"[get_actuator_count] : %d",get_actuator_count(cf));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,1));
        NSLog(@"[get_uart_path] : %s",get_uart_path(cf,1));
        NSLog(@"[actuator_for_site] : %d",actuator_for_site(cf,1));

        NSLog(@"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!");
        
        NSLog(@"[fixture_engage] : %d",fixture_engage(cf,1));
        NSLog(@"[fixture_disengage] : %d",fixture_disengage(cf,1));
        NSLog(@"[fixture_open] : %d",fixture_open(cf,1));
        NSLog(@"[fixture_close] : %d",fixture_close(cf,1));

        NSLog(@"[set_usb_power] : %d",set_usb_power(cf,TURN_ON,1));
        NSLog(@"[set_battery_power] : %d",set_battery_power(cf,TURN_ON,1));
        NSLog(@"[set_usb_signal] : %d",set_usb_signal(cf,CLOSE_RELAY,1));
        NSLog(@"[set_uart_signal] : %d",set_uart_signal(cf,CLOSE_RELAY,1));
        NSLog(@"[set_apple_id] : %d",set_apple_id(cf,CLOSE_RELAY,1));
        NSLog(@"[set_conn_det_grounded] : %d",set_conn_det_grounded(cf,CLOSE_RELAY,1));
        NSLog(@"[set_hi5_bs_grounded] : %d",set_hi5_bs_grounded(cf,CLOSE_RELAY,1));

        NSLog(@"[set_dut_power] : %d",set_dut_power(cf,TURN_ON,1));
        NSLog(@"[set_dut_power_all] : %d",set_dut_power_all(cf,TURN_ON));

        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_ON,1));
        NSLog(@"[set_force_diags] : %d",set_force_diags(cf,TURN_ON,1));
        NSLog(@"[set_force_iboot] : %d",set_force_iboot(cf,TURN_ON,1));

        NSLog(@"[set_led_state] : %d",set_led_state(cf,PASS,1));
        NSLog(@"[set_led_state_all] : %d",set_led_state_all(cf,PASS));

       // NSLog(@"fixture_write_string : %d",fixture_write_string(cf,"kao"));

    
        NSLog(@"[release_fixture_controller]");
        */
      
    
       
       // void * cf = create_fixture_controller(0);
       // void * cf1 = create_fixture_controller(1);
        
       /* NSLog(@"[set_led_state] : %d",set_led_state(cf,PASS,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,PASS,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,PASS,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,PASS,4));
       
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,FAIL,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,FAIL,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,FAIL,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,FAIL,4));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,INPROGRESS,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,INPROGRESS,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,INPROGRESS,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf,INPROGRESS,4));

        
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,PASS,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,PASS,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,PASS,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,PASS,4));
        
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,FAIL,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,FAIL,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,FAIL,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,FAIL,4));
        
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,INPROGRESS,1));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,INPROGRESS,2));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,INPROGRESS,3));
        [NSThread sleepForTimeInterval:1];
        NSLog(@"[set_led_state] : %d",set_led_state(cf1,INPROGRESS,4));
        NSLog(@"*************************************");
        NSLog(@"*************************************");
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,1));
        NSLog(@"=====slot 1===::::[get_uart_path] : %s",get_uart_path(cf,1));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,2));
        NSLog(@"======slot 2==::::[get_uart_path] : %s",get_uart_path(cf,2));
        
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,3));
        NSLog(@"=====slot 3===::::[get_uart_path] : %s",get_uart_path(cf,3));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,4));
        NSLog(@"======slot 4==::::[get_uart_path] : %s",get_uart_path(cf,4));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,1));
        NSLog(@"======slot 5==::::[get_uart_path] : %s",get_uart_path(cf1,1));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,2));
        NSLog(@"======slot 6==::::[get_uart_path] : %s",get_uart_path(cf1,2));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,3));
        NSLog(@"======slot 7==::::[get_uart_path] : %s",get_uart_path(cf1,4));
        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,4));
        NSLog(@"======slot 8==::::[get_uart_path] : %s",get_uart_path(cf1,4));
        */
        
       /* NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_ON,1));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_ON,2));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_ON,3));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_ON,4));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_ON,1));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_ON,2));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_ON,3));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_ON,4));
        [NSThread sleepForTimeInterval:2];
       */
        
       /*
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_OFF,1));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_OFF,2));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_OFF,3));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf,TURN_OFF,4));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_OFF,1));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_OFF,2));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_OFF,3));
        [NSThread sleepForTimeInterval:2];
        NSLog(@"[set_force_dfu] : %d",set_force_dfu(cf1,TURN_OFF,4));
        [NSThread sleepForTimeInterval:2];*/
        
        
        //
        
//        void * cf = create_fixture_controller(0);
//        void * cf1 = create_fixture_controller(1);
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,1));
//        NSLog(@"=====slot 1===::::[get_uart_path] : %s",get_uart_path(cf,1));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,2));
//        NSLog(@"======slot 2==::::[get_uart_path] : %s",get_uart_path(cf,2));
//        
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,3));
//        NSLog(@"=====slot 3===::::[get_uart_path] : %s",get_uart_path(cf,3));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf,4));
//        NSLog(@"======slot 4==::::[get_uart_path] : %s",get_uart_path(cf,4));
//       NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,1));
//       
//        NSLog(@"======slot 5==::::[get_uart_path] : %s",get_uart_path(cf1,1));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,2));
//        NSLog(@"======slot 6==::::[get_uart_path] : %s",get_uart_path(cf1,2));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,3));
//        NSLog(@"======slot 7==::::[get_uart_path] : %s",get_uart_path(cf1,3));
//        NSLog(@"[get_usb_location] : %s",get_usb_location(cf1,4));
//        NSLog(@"======slot 8==::::[get_uart_path] : %s",get_uart_path(cf1,4));
//        
//       release_fixture_controller(cf1);
//        release_fixture_controller(cf);
        
       // NSLog(@"-:%@",[USBDevice getAllAttachedDevices]);
        
//   NSArray *arr =@[@"IO SET(1,BIT25=0)",
//                  @"IO SET(8,BIT20=0,BIT3=0,BIT5=0,BIT11=0,BIT12=0,BIT13=0,BIT14=0,BIT15=0)",
//                  @"IO SET(1,BIT25=0)",
//                  @"IO SET(8,BIT20=0,BIT3=0,BIT5=0,BIT11=0,BIT12=0,BIT13=0,BIT14=0,BIT15=0)",
//                  @"Delay:4",
//                  @"IO SET(8,BIT14=1,BIT15=1,BIT3=1,BIT5=0,BIT11=1,BIT12=1,BIT13=1)",
//                  @"IO SET(8,BIT14=1,BIT15=1,BIT3=1,BIT5=0,BIT11=1,BIT12=1,BIT13=1)",
//                  @"IO SET(1,BIT25=1)",
//                   @"IO SET(1,BIT25=1)"];
//         for (int j=0; j<[arr count]; j++) {
//        if ([[[arr objectAtIndex:j]uppercaseString] containsString:@"DELAY:"]) {
//            NSArray *arryDelay=[[arr objectAtIndex:j] componentsSeparatedByString:@":"];
//            if ([[arryDelay[0] uppercaseString] isEqual:@"DELAY"]) {
//                [NSThread sleepForTimeInterval:[arryDelay[1] doubleValue]];
//                NSLog(@"----delay:%f",[arryDelay[1] doubleValue]);
//            }
//        
//        }
//         }
//
        
//         NSArray *array=[USBDevice getAllAttachedDevices];
//        NSLog(@"%@",array);
        
        
    }
    return 0;
}

