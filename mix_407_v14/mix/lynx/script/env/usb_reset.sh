#!/bin/bash
# for reset PS USB ports by toggle USB_RESET_1V8 for USB3320 IC;
# according to SG Xiaojun the IC needs a reset to get working.

function reset_usb_phy(){
    if [ -d /sys/class/gpio/gpio906 ]; then
        echo 906 > /sys/class/gpio/unexport
    fi
    echo 906 > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio906/direction
    echo 0 > /sys/class/gpio/gpio906/value
    sleep 0.05
    echo 1 > /sys/class/gpio/gpio906/value
}

reset_usb_phy
modprobe -r ci_hdrc_usb2
modprobe ci_hdrc_usb2
