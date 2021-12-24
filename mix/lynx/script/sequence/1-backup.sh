#!/bin/bash

PACKAGE_SOURCE_PATH=
FW_UPDATE_FOLDER_BASE=

# --------------------------------------------------------------------------
set +e

Usage()
{
cat <<EOF
Usage:
$0 <fw_package_name> <fw_update_folder_base>
EOF
}

if [ "$#" -lt 2 ] ;then
    Usage
    exit 0
fi

PACKAGE_SOURCE_PATH=$1
FW_UPDATE_FOLDER_BASE=$2
FW_BACKUP_TEMP_FOLDER_PATH=$FW_UPDATE_FOLDER_BASE/backup
MIX_ROOT_FOLDER_PATH="/mix"

if [ $PACKAGE_SOURCE_PATH = "DEB" ]; then
    echo "[Install DEB] Backup is Skipped"
    exit 0
fi

echo ""
echo "Firmware backup ..."
#--------------------------------------------------------
rm -rf $FW_BACKUP_TEMP_FOLDER_PATH
mkdir -p $FW_BACKUP_TEMP_FOLDER_PATH

# mix
echo "mix folder backup-ing ..."
mkdir -p $FW_BACKUP_TEMP_FOLDER_PATH/mix
cp -avf $MIX_ROOT_FOLDER_PATH/* $FW_BACKUP_TEMP_FOLDER_PATH/mix
sync
echo "mix backup finished"

# BOOT.bin
echo "BOOT.bin backup ..."
mkdir -p $FW_BACKUP_TEMP_FOLDER_PATH/BOOT

if [ -c "/dev/mtd0" ]; then
	echo "backup mtd0..."
	cp /dev/mtd0 $FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd0_backup.bin
fi

if [ -c "/dev/mtd1" ]; then
	echo "backup mtd1..."
	cp /dev/mtd1 $FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd1_backup.bin
fi
sync
echo "BOOT.bin backup finished"

#fpga.bit devicetree, uImage
echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) backup-ing ..."

umount /mnt 2>/dev/null
umount /mnt 2>/dev/null
umount /mnt 2>/dev/null
echo "mount '/dev/mmcblk0p1' device -> /mnt"
mount /dev/mmcblk0p1 /mnt
if [ $? -ne 0 ]; then
	echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) backup failed."
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	exit 1
fi
echo "mount '/dev/mmcblk0p1' device -> /mnt successful"

mkdir -p $FW_BACKUP_TEMP_FOLDER_PATH/mmcblk0p1
cp -avf /mnt/* $FW_BACKUP_TEMP_FOLDER_PATH/mmcblk0p1/

echo "clean up mmcblk0p1"
rm -f /mnt/*
umount /mnt 2>/dev/null
umount /mnt 2>/dev/null
umount /mnt 2>/dev/null
sync
echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) backup finished"	

echo "kernel modules backup ..."
mkdir -p $FW_BACKUP_TEMP_FOLDER_PATH/modules
cp -avf /lib/modules/*  $FW_BACKUP_TEMP_FOLDER_PATH/modules/
sync
echo "kernel 'modules' backup  finished"

echo "Firmware backup finished"
exit 0