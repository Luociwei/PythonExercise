//
//  USBDevice.h
//  USBDeviceFramework
//RyanG


#import <Foundation/Foundation.h>
#import <IOKit/IOKitLib.h>
#import <IOKit/usb/IOUSBLib.h>
#import <IOKit/IOCFPlugIn.h>

typedef struct __controlPacket {
    uint8_t bmRequestType;
    uint8_t bRequest;
    uint16_t wValue;
    uint16_t wIndex;
    uint8_t* data;
    uint16_t wLength;
} controlPacket, *controlPacketRef;

#define MakeRequest(packet, _bmRequestType, _bRequest, _wValue, _wIndex, _data, _wLength) \
    do {                                        \
        packet.bmRequestType = _bmRequestType;  \
        packet.bRequest = _bRequest;            \
        packet.wValue = _wValue;                \
        packet.wIndex = _wIndex;                \
        packet.data = _data;                    \
        packet.wLength = _wLength;              \
    } while(0);

typedef enum {
    kUSBDeviceErrorSuccess = 0,
    kUSBDeviceErrorIO,
    kUSBDeviceErrorUnsuccessful,
    kUSBDeviceErrorUnsupported
} kUSBDeviceErrorStatus;

@interface USBDevice : NSObject {
    int _currentVid;
    int _currentPid;
    int _currentConfiguration;
    int _currentInterface;
    uint8_t _currentAlternateInterface;
    IOCFPlugInInterface** _currentPlugInInterface;
    IOUSBDeviceInterface320** _currentDeviceInterface;
    IOUSBInterfaceInterface197** _currentInterfaceInterface;
}
#pragma mark - class methods

+(NSArray*)getAllAttachedDevices;

@property(copy, nonatomic) NSString* deviceSerialNumber;
@property(copy, nonatomic) NSString* deviceFriendlyName;

@end
