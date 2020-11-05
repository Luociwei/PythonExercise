//
//  USBDevice.m
//  USBDeviceFramework
//RyanG

//

#import "USBDevice.h"
#import <assert.h>

@implementation USBDevice
@synthesize deviceFriendlyName, deviceSerialNumber;

#pragma mark - Overrides
-(void)dealloc {
    if(_currentInterfaceInterface) {
        (*_currentInterfaceInterface)->USBInterfaceClose(_currentInterfaceInterface);
        (*_currentInterfaceInterface)->Release(_currentInterfaceInterface);
    }
    if(_currentDeviceInterface) {
        (*_currentDeviceInterface)->USBDeviceClose(_currentDeviceInterface);
        (*_currentDeviceInterface)->Release(_currentDeviceInterface);
    }
    [self resetIvars];
    //[super dealloc];
}

#pragma mark - Private methods.

-(void)resetIvars {
    _currentInterface = 0;
    _currentAlternateInterface = 0;
    _currentDeviceInterface = nil;
    _currentInterfaceInterface = nil;
    _currentPid = 0x0000;
    _currentVid = 0x0000;
    return;
}

+(NSString*)stringForSpeed:(uint8_t)deviceSpeed {
    switch(deviceSpeed) {
        case kUSBDeviceSpeedFull:
            return @"Full-Speed";
        case kUSBDeviceSpeedHigh:
            return @"High-Speed";
        case kUSBDeviceSpeedLow:
            return @"Low-Speed";
        case 3:                 // Super-Speed
            return @"Super-Speed";
        default:
            return @"Unknown";
    }
    return nil;
}

+(NSDictionary*)parseConfigurationDescriptor:(IOUSBConfigurationDescriptorPtr)descriptor {
    int descriptorLength;
    uint8_t *currentDescriptor = NULL;
    uint8_t *endingDescriptor = NULL;
    NSMutableDictionary* configurationDictionary = [[NSMutableDictionary alloc] initWithCapacity:10];
    
    // The dictionary must EXIST.
    assert(configurationDictionary != NULL);
    
    // Verify object exists.
    assert(descriptor != NULL && "Null device descriptors are not allowed, kind sir.");
    
    // Get length and parse descriptors.
    currentDescriptor = (uint8_t*)descriptor;
    descriptorLength = descriptor->wTotalLength;
    endingDescriptor = ((uint8_t*)descriptor) + descriptorLength;
    
    [configurationDictionary setObject:[NSNumber numberWithInt:descriptor->MaxPower] forKey:@"MaxPower"];
    [configurationDictionary setObject:[NSNumber numberWithInt:descriptor->wTotalLength] forKey:@"TotalLength"];
    
    // This is a horrible horrible thing. But it works for the most part.
    while(currentDescriptor < endingDescriptor) {
        IOUSBConfigurationDescriptor* castedDescriptor = (IOUSBConfigurationDescriptor*)currentDescriptor;
        uint8_t length, type;
        
        assert(castedDescriptor != NULL);
        
        length = castedDescriptor->bLength;
        type = castedDescriptor->bDescriptorType;
        
        // Add the specific type to the dictionary.
        if(length) {
            switch(type) {
                // This is an interface.
                case kUSBInterfaceDesc: {
                    IOUSBInterfaceDescriptorPtr interfaceDescriptor = (IOUSBInterfaceDescriptorPtr)currentDescriptor;
                    NSMutableDictionary* interfaceDictionary = [[NSMutableDictionary alloc] initWithCapacity:10];
    
                    assert(interfaceDictionary != NULL);

                    // Add interface crap to subdictionary.
                    [interfaceDictionary setObject:[NSNumber numberWithInt:interfaceDescriptor->bInterfaceNumber] forKey:@"InterfaceNumber"];
                    [interfaceDictionary setObject:[NSNumber numberWithInt:interfaceDescriptor->bInterfaceClass] forKey:@"InterfaceClass"];
                    [interfaceDictionary setObject:[NSNumber numberWithInt:interfaceDescriptor->bInterfaceSubClass] forKey:@"InterfaceSubClass"];
                    [interfaceDictionary setObject:[NSNumber numberWithInt:interfaceDescriptor->bInterfaceProtocol] forKey:@"InterfaceProtocol"];
                    [interfaceDictionary setObject:[NSNumber numberWithInt:interfaceDescriptor->bAlternateSetting] forKey:@"InterfaceAlternateSetting"];
                    
                    [configurationDictionary setObject:interfaceDictionary forKey:[NSString stringWithFormat:@"InterfaceDescriptor-%d", interfaceDescriptor->bInterfaceNumber]];
                    //[interfaceDictionary release];
                    break;
                }
                // This is an endpoint.
                case kUSBEndpointDesc: {
                    IOUSBEndpointDescriptorPtr endpointDescriptor = (IOUSBEndpointDescriptorPtr)currentDescriptor;
                    NSMutableDictionary* endpointDictionary = [[NSMutableDictionary alloc] initWithCapacity:10];
    
                    assert(endpointDictionary != NULL);

                    // Add interface crap to subdictionary.
                    [endpointDictionary setObject:[NSNumber numberWithInt:endpointDescriptor->bEndpointAddress] forKey:@"EndpointAddress"];
                    [endpointDictionary setObject:[NSNumber numberWithInt:endpointDescriptor->bInterval] forKey:@"EndpointInterval"];
                    [endpointDictionary setObject:[NSNumber numberWithInt:endpointDescriptor->bmAttributes] forKey:@"EndpointAttributes"];
                    [endpointDictionary setObject:[NSNumber numberWithInt:endpointDescriptor->wMaxPacketSize] forKey:@"EndpointMaxPacketSize"];
    
                    [configurationDictionary setObject:endpointDictionary forKey:[NSString stringWithFormat:@"EndpointDescriptor-%d", endpointDescriptor->bEndpointAddress]];
                    //[endpointDictionary release];
                    break;
                }
                default:
                    break;
            }
        }
        currentDescriptor += length;
    }
    return configurationDictionary;
}

#pragma mark - Initializer/class methods

+ (NSString *)ToHex:(uint32_t)tmpid
{
    NSString *nLetterValue;
    NSString *str =@"";
    uint32_t ttmpig;
    for (int i = 0; i<9; i++) {
        ttmpig=tmpid%16;
        tmpid=tmpid/16;
        switch (ttmpig)
        {
            case 10:
                nLetterValue =@"A";break;
            case 11:
                nLetterValue =@"B";break;
            case 12:
                nLetterValue =@"C";break;
            case 13:
                nLetterValue =@"D";break;
            case 14:
                nLetterValue =@"E";break;
            case 15:
                nLetterValue =@"F";break;
            default:
                nLetterValue = [NSString stringWithFormat:@"%u",ttmpig];
                
        }
        str = [nLetterValue stringByAppendingString:str];
        if (tmpid == 0) {
            break;
        }
        
    }
    return str;
}



+(NSArray*)getAllAttachedDevices {
    mach_port_t iokitPort = kIOMasterPortDefault;
    kern_return_t kernelStatus;
    io_iterator_t deviceIterator;
    io_service_t deviceService;
    io_name_t deviceName;
    int i=0;
    
    // Grand dictionary of all time
    NSMutableArray* usbArray = [[NSMutableArray alloc] initWithCapacity:10];
    
    // Create initial request used to get matching services for each usb device in the system.
    // Note: on embedded we have our devices connected to AppleSynopsysEHCI, sort of like how
    // on the desktop platform, we have them on AppleUSBEHCI. Apparently the root hub simulation
    // thing went missing, or I couldn't see it in ioreg last time I checked. Whatever.
    //
    // it works, also IOUSB has gone missing on embedded. SOMEONE SHOULD FIX THAT PLEASE.
    kernelStatus = IOServiceGetMatchingServices(iokitPort, IOServiceMatching(kIOUSBDeviceClassName), &deviceIterator);
    assert(kernelStatus == KERN_SUCCESS && "Failed to get matching service");
    
    while((deviceService = IOIteratorNext(deviceIterator))) {
        SInt32 score;
        IOCFPlugInInterface** plugInInterface;
        
        // Get device name and store it.
        kernelStatus = IORegistryEntryGetName(deviceService, deviceName);
        //NSLog(@"--kernelStatus:%@",kernelStatus);
        assert(kernelStatus == KERN_SUCCESS && "Failed to obtain device name");
        CFTypeRef deviceVersion = IORegistryEntryCreateCFProperty(deviceService, CFSTR("bcdDevice"), kCFAllocatorDefault, 0);
        CFTypeRef serialNumber = IORegistryEntryCreateCFProperty(deviceService, CFSTR("USB Serial Number"), kCFAllocatorDefault, 0);
        // Create CF plugin for device, this'll be used to get information.
        kernelStatus = IOCreatePlugInInterfaceForService(deviceService, kIOUSBDeviceUserClientTypeID, kIOCFPlugInInterfaceID, &plugInInterface, &score);
        assert(kernelStatus == KERN_SUCCESS && "Failed to get device");
        
        // Release objects
        kernelStatus = IOObjectRelease(deviceService);
        assert(kernelStatus == KERN_SUCCESS && "Failed to release kernel objects");
        
        // Verify object exists.
        if(plugInInterface) {
            uint16_t idVendor, idProduct;
            IOUSBDeviceInterface320** deviceInterface;
            HRESULT resultingStatus;
            NSMutableDictionary* usbDictionary = [[NSMutableDictionary alloc] initWithCapacity:10];

            // Get device interface
            resultingStatus = (*plugInInterface)->QueryInterface(plugInInterface, CFUUIDGetUUIDBytes(kIOUSBDeviceInterfaceID320), (LPVOID)&deviceInterface);
            assert(resultingStatus == kIOReturnSuccess && "Failed to create plug-in interface for device");
            (*plugInInterface)->Release(plugInInterface);
            
            // Get device VID/PID.
            (*deviceInterface)->GetDeviceProduct(deviceInterface, &idProduct);
            (*deviceInterface)->GetDeviceVendor(deviceInterface, &idVendor);
            
            // Get extra information.
            uint32_t locationId, busPowerAvailable;
            uint8_t deviceSpeed, numberOfConfigurations;
            uint8_t deviceClass;
            
            (*deviceInterface)->GetLocationID(deviceInterface, &locationId);
            (*deviceInterface)->GetDeviceSpeed(deviceInterface, &deviceSpeed);
            (*deviceInterface)->GetNumberOfConfigurations(deviceInterface, &numberOfConfigurations);
            (*deviceInterface)->GetDeviceBusPowerAvailable(deviceInterface, &busPowerAvailable);
            
            (*deviceInterface)->GetDeviceClass(deviceInterface, &deviceClass);
            
            // Add to dictionary.
            
            [usbDictionary setObject:[NSString stringWithFormat:@"%d",i] forKey:@"index"];
            [usbDictionary setObject:@[[NSString stringWithFormat:@"0x%@",[self ToHex:locationId]],[NSString stringWithFormat:@"%d",i]] forKey:@"LocationID"];
            //[usbDictionary setObject:[NSNumber numberWithLong:busPowerAvailable] forKey:@"BusPowerAvailable"];
            // [usbDictionary setObject:[USBDevice stringForSpeed:deviceSpeed] forKey:@"DeviceSpeed"];
            // [usbDictionary setObject:[NSNumber numberWithInt:numberOfConfigurations] forKey:@"NumberOfConfigurations"];
            [usbDictionary setObject:@[[NSString stringWithUTF8String:deviceName],[NSString stringWithFormat:@"%d",i]] forKey:@"DeviceFriendlyName"];
            //[usbDictionary setObject:[NSString stringWithUTF8String:deviceName] forKey:@"DeviceFriendlyName"];
            [usbDictionary setObject:[NSString stringWithFormat:@"0x%@",[self ToHex:idVendor]] forKey:@"VendorID"];
            [usbDictionary setObject:[NSString stringWithFormat:@"0x%@",[self ToHex:idProduct]] forKey:@"ProductID"];
            // [usbDictionary setObject:[NSNumber numberWithInt:deviceClass] forKey:@"DeviceClass"];
            [usbDictionary setObject: [NSString stringWithFormat:@"%@",serialNumber] forKey:@"SerialNumber"];
            //[usbDictionary setObject: [NSString stringWithFormat:@"%@",deviceVersion ] forKey:@"DeviceVersion"];
              [usbDictionary setObject: [NSString stringWithFormat:@"%@",[self ToHex:[[NSString stringWithFormat:@"%@",deviceVersion] intValue]]] forKey:@"DeviceVersion"];
            [usbArray addObject:usbDictionary];
            i++;
            //[usbDictionary release];
            
            // ..and other associated objects.
            (*deviceInterface)->USBDeviceClose(deviceInterface);
            (*deviceInterface)->Release(deviceInterface);
        }
    }
    
    return usbArray;
}



@end
