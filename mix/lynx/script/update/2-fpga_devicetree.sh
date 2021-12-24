#!/bin/bash

# device tree update script
PACKAGE_FILE_NAME="devicetree.dtb"

PACKAGE_SOURCE_PATH=

set +e

Usage()
{
cat <<EOF
Usage:
$0 <fw_update_temp_folder_path>
EOF
}

if [ "$#" -lt 1 ] ;then
    Usage
    exit 0
fi

PACKAGE_SOURCE_PATH=$1

echo "update package is '$PACKAGE_FILE_NAME'"
#check package file exsit?
if [ ! -f $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME ]; then

	echo "$PACKAGE_FILE_NAME is not exist."
	exit 1
fi


do_exit(){
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
}

echo "'$PACKAGE_FILE_NAME' updating..."

echo "mount emmc device"
do_exit
mount /dev/mmcblk0p1 /mnt
if [ ! $? -eq 0 ]; then
	echo "mount EMMC device failed."
	do_exit
	exit 2
fi

echo "updating ..."
rm -rf /mnt/$PACKAGE_FILE_NAME
cp $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME /mnt/
if [ $? -ne 0 ]; then
	echo "Update failed"
	do_exit
	exit 3
fi
echo "Update '$PACKAGE_FILE_NAME' finished"

# ------------------------------------------

PACKAGE_FILE_NAME="fpga.bit"
if [ ! -f $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME ]; then
	echo "$PACKAGE_FILE_NAME  not exist."
	exit 1
fi
echo "'$PACKAGE_FILE_NAME' updating..."
rm -rf /mnt/$PACKAGE_FILE_NAME
cp $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME /mnt/
if [ $? -ne 0 ]; then
	echo "Update failed"
	do_exit
	exit 3
fi
echo "Update '$PACKAGE_FILE_NAME' finished"

sync 
sleep 1
do_exit

exit 0