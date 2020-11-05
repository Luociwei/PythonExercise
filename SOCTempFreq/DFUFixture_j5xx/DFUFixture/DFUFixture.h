/*!
 *    Copyright 2016 Apple Inc. All rights reserved.
 *
 *    APPLE NEED TO KNOW CONFIDENTIAL
 *
 *  DFUFixture.h
 *
 */

#ifndef DFUFixture_DFUFixture_h
#define DFUFixture_DFUFixture_h
#define DFU_API_VERSION 2
#define DFU_API_MINOR_VERSION 9

typedef enum _POWER_STATE {
    TURN_ON = 0,
    TURN_OFF
} POWER_STATE;


typedef enum _RELAY_STATE {
    CLOSE_RELAY = 0,
    OPEN_RELAY
} RELAY_STATE;

typedef enum _EVENT_TYPE {
    START = 0,
    ABORT = 1,
    READY_TO_LOAD = 2
} FIXTURE_EVENT;

typedef enum _LED_STATE {
    OFF = 0,
    PASS = 1,
    FAIL = 2,
    INPROGRESS = 3,
    FAIL_GOTO_FA = 4,
    PANIC = 5
} LED_STATE;


#ifdef __cplusplus
extern "C" {
#endif
    
    //GENERAL COMMENT
    //1.fixture, actuator index are 0 based, site index is 1 based.
    //2.For return status, if it's an error it should be <0. 0 means success unless otherwise noted
    
    //index is the fixture index, incase one computer controls multiple fixtures or one fixtures has multiple actuators
    //when this function returns, the library should have actually established communication with the fixture, if not, createFixtureController
    //should return 0
    void* create_fixture_controller(int index);
    void release_fixture_controller(void* controller);
    
    
    //All functions below should be THREAD SAFE and they all should be re-entrant, meaning there should be no side effect other than the intended effects on the fixture
    
    //*****Section: General information functions******************
    //The caller is not responsible for releasing the returned string. The library may release the string
    //anytime after the function returns. If the caller wants to keep a copy
    //of the string, it's the caller's responsibility to make a copy of it.
    const char * const get_vendor(void* controller);
    int get_vendor_id(void);
    const char * const get_serial_number(void* controller);
    const char * const get_carrier_serial_number(void* controller, int site);
    const char * const get_error_message(int status); //For all the functions that return a status, 0 means OK, otherwise the meaning of the status is returned by this function
    const char * const get_version(void* controller); //anything changes (software/firmware/schematics/layout/mechanical) the version should be updated
    const char * const get_unit_location(void* controller, int site);
    
    //********* section: discovery functions ********************
    //fixture should reset to a known state. But the tray should not change position before and after reset.
    //in all the functions in this header file, the site number is 1 based.
    
    int init(void* controller);   //set fixture to init state (fixture open and disengaged, all LED off)
    int reset(void* controller);  //returns an status
    int resetChannel(void* controller, int site);
    int get_site_count(void* controller);
    int get_actuator_count(void* controller);  //one fixture may have multiple actuators
    const char* get_usb_location(void* controller, int site);
    const char* get_uart_path(void* controller, int site);
    int actuator_for_site(void* controller, int site); //returns the actuator index that controls this site)
    
    //********** section:control functions **********************
    //For all functions below, the returned value is a status code.
    //0 means success. If it's not 0, the returend value can be passed to getErroMessage to get a description.
    
    //the fixture should not block on these functions, they should return right away. The station software will
    //use the status functions below to check the actuator is in place
    //need 3s delay between close and engage
    int fixture_engage(void* controller, int actuator_index);
    int fixture_disengage(void* controller, int actuator_index);
    int fixture_open(void* controller, int actuator_index);
    int fixture_close(void* controller, int actuator_index);
    
    //when these functions return, the power rail or the relay should be stable. I will not add extra delay in the station code for the fixture.
    //for all the functions below, if the operation is succesful, the return code should be 0. If the opertaion is unsuccesful, the
    //return status code should be a negative integer. If the operation is invalid,  for instance, the usb signal is alwasy connected so you can not
    //open the relay for the usb signal, the returned code should be a positive integer.
    int set_usb_power(void* controller, POWER_STATE action, int site);
    int set_battery_power(void* controller, POWER_STATE action, int site);
    
    int set_usb_signal(void* controller, RELAY_STATE action, int site);
    int set_uart_signal(void* controller, RELAY_STATE action, int site);
    int set_apple_id(void* controller, RELAY_STATE action, int site);
    int set_conn_det_grounded(void* controller, RELAY_STATE action, int site);
    int set_hi5_bs_grounded(void* controller, RELAY_STATE action, int site);
    
    int set_dut_power(void* controller, POWER_STATE action, int site);
    int set_dut_power_all(void* controller, POWER_STATE action);
    
    int set_force_dfu(void* controller, POWER_STATE action, int site);
    int set_force_diags(void* controller, POWER_STATE action, int site);
    int set_force_iboot(void* controller, POWER_STATE action, int site);
    
    int set_led_state(void* controller, LED_STATE action, int site);
    int set_led_state_all(void* controller, LED_STATE action);
    
    //************* section:status functions *******************
    //when the actuator is in motion and not yet settled, neither is_engage nor is_disengage should return true
    bool is_fixture_engaged(void* controller, int actuator_index);
    bool is_fixture_disengaged(void* controller, int actuator_index);
    bool is_fixture_closed(void* controller, int actuator_index);
    bool is_fixture_open(void* controller, int actuator_index);
    
    POWER_STATE usb_power(void* controller, int site);
    POWER_STATE battery_power(void* controller, int site);
    POWER_STATE force_dfu(void* controller, int site);
    RELAY_STATE usb_signal(void* controller, int site);
    RELAY_STATE uart_signal(void* controller, int site);
    RELAY_STATE apple_id(void* controller, int site);
    RELAY_STATE conn_det_grounded(void* controller, int site);
    RELAY_STATE hi5_bs_grounded(void* controller, int site);
    POWER_STATE dut_power(void* controller, int site);
    
    bool is_board_detected(void* controller, int site);
    
    /*
     These three functions set up event notification. the event_ctx is initialized by the caller and passed to setup_event_notification.
     It's the library's responsibility to save this pointer and pass the exact same pointer back in the two call back events.
     
     All calls to fixture_event_callback_t should happen in the same thread.
     
     on_stop_event_notification must be called before the fixture is released. Once this function is called, further calls to on_fixture_event
     is illegal. You should call this function in release_fixture_controller
     */
    typedef void (*fixture_event_callback_t)(const char* sn, void *controller, void* event_ctx, int site, int event_type);
    typedef void (*stop_event_notfication_callback_t)(void* ctx);
    void setup_event_notification(void* controller, void* event_ctx, fixture_event_callback_t on_fixture_event, stop_event_notfication_callback_t on_stop_event_notification);
    NSString* getHostModel(void* controller);
    
    //turn debug port on/off
    int set_debug_port(void* controller, POWER_STATE action, int site);
    
    //fan settings and check, be careful if there's only one fan
    int get_fan_speed(void* controller, int site);
    int set_fan_speed(void* controller, int fan_speed, int site);
    bool is_fan_ok(void* controller, int site);
    
#ifdef __cplusplus
}
#endif
#endif

