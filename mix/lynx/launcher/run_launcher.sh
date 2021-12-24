#!/bin/bash

basepath=$(cd `dirname $0`;cd ..;pwd)

export PYTHONPATH=$PYTHONPATH:$basepath
cd `dirname $0`
cd ..

# load driver from 2 folders:
# /mix/driver is module vendor driver, including
#    lynx-core-driver
#    other vendor's module/ic/ipcore driver.
# /mix/addon/driver is station specific drivers
#    mostly station base-board driver.
DRIVER_FOLDER='/mix/driver'
ADDON_DRIVER_FOLDER='/mix/addon/driver/'

PROFILE_FOLDER=/mix/addon/config/
HW_PROFILE=$PROFILE_FOLDER/hw_profile.json
SW_PROFILE=$PROFILE_FOLDER/sw_profile.json
# support both profile.json and hw+sw profile.
if [ -f $HW_PROFILE ]
then
    python launcher/launcher.py -p $HW_PROFILE -s $SW_PROFILE --driver_folder=$DRIVER_FOLDER --driver_folder=$ADDON_DRIVER_FOLDER
else
    echo 'Hardware profile (hw_profile.json) is not found in '$PROFILE_FOLDER'; launcher cannot run without hardware config file.'
fi
