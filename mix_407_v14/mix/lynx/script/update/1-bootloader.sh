
#!/bin/bash

#update BOOT.bin to flash device
PACKAGE_FILE_NAME="BOOT.bin"

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

if [ ! -f "$PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME" ]; then
	echo "Application update package file '$PACKAGE_FILE_NAME' is not exist."
	exit 1
fi

echo "$PACKAGE_FILE_NAME updating..."

#write to flash device
if [ -c "/dev/mtd0" ]; then
	echo "update mtd0..."
	flash_erase /dev/mtd0 0xe0000 32
	flashcp -v $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME /dev/mtd0
	if [ $? -ne 0 ];then
		echo "[Error ]update mtd0 BOOT.bin failed."
		do_exit
		exit 3
	fi
fi

if [ -c "/dev/mtd1" ]; then
	echo "update mtd1..."
	flash_erase /dev/mtd1 0xe0000 32
	flashcp -v $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME /dev/mtd1
	if [ $? -ne 0 ];then
		echo "[Error ]update mtd1 BOOT.bin failed."
		do_exit
		exit 4
	fi
fi

sync

echo "$PACKAGE_FILE_NAME update finished."

exit 0