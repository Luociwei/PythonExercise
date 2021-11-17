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
FW_UPDATE_TEMP_FOLDER_PATH=$FW_UPDATE_FOLDER_BASE/temp
FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH=$FW_UPDATE_TEMP_FOLDER_PATH/script
FW_BACKUP_TEMP_FOLDER_PATH=$FW_UPDATE_FOLDER_BASE/backup
MIX_ROOT_FOLDER_PATH="/mix"

FW_Rollback(){
	echo ""
	echo "Firmware roll back ..."
	#---------------------------------------
	cd $FW_BACKUP_TEMP_FOLDER_PATH/mix
	file_list=`ls`
	for file_name in $file_list
	do
		rm -rf $MIX_ROOT_FOLDER_PATH/$file_name
		echo " $file_name retroversion"
		cp -af $file_name $MIX_ROOT_FOLDER_PATH/
	done
	sync
	echo "mix retroversion finished"

	#BOOT.bin
	echo ""
	echo "BOOT.bin retroversion ..."
	if [ -f "$FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd0_backup.bin" ]; then
		echo "mtd0 retroversion..."
		flashcp -v $FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd0_backup.bin /dev/mtd0
	fi

	if [ -f "$FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd1_backup.bin" ]; then
		echo "mtd0 retroversion..."
		flashcp -v $FW_BACKUP_TEMP_FOLDER_PATH/BOOT/mtd1_backup.bin /dev/mtd1
	fi
	echo "BOOT.bin retroversion finished"

	#fpga.bit devicetree, uImage
	echo ""
	echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) retroversion ..."

	echo "mount device"
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	mount /dev/mmcblk0p1 /mnt
	if [ $? -eq 0 ]; then
		echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) retroversion failed."
		umount /mnt 2>/dev/null
		umount /mnt 2>/dev/null
		umount /mnt 2>/dev/null
		return 1
	fi

	echo "mount '/dev/mmcblk0p1' device -> '/mnt'successedl"
	if [ -d "$FW_BACKUP_TEMP_FOLDER_PATH/mmcblk0p1" ]; then
		rm -rf /mnt/*
		cp -af $FW_BACKUP_TEMP_FOLDER_PATH/mmcblk0p1/* /mnt/
	fi
	sync
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	echo "'/dev/mmcblk0p1'(fpga.bit, uImage, devicetree) retroversion finished"

	echo ""
	echo "kernel modules retroversion ..."
	rm -rf /lib/modules/*
	cp -af $FW_BACKUP_TEMP_FOLDER_PATH/modules/* /lib/modules/
	echo "kernel modules retroversion ..."

	echo "Firmware retroversion finished"
	return 0
}


echo ""
#---------------------------------------
#updating
set +e
cd $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH/update

if [ $PACKAGE_SOURCE_PATH = "DEB" ]; then
    echo "Install DEB Only ..."
    script_files_list="6-deb.sh"
else
    script_files_list=`ls *.sh`
fi
for script_file in $script_files_list
do
    echo ""
    echo "---------Entering script $script_file--------"
    bash $script_file $FW_UPDATE_TEMP_FOLDER_PATH $FW_UPDATE_SCRIPTS_TEMP_FOLDER_PATH
    errno=$?
    echo "---------Leaving script $script_file---------"
    echo ""
    cd .

    if [ $errno -ne 0 ]; then
        echo "- Error - $script_file failed with return code $errno"
        FW_Rollback
        exit 1
    fi
done

echo "Write FW version file"
cp -f $FW_UPDATE_TEMP_FOLDER_PATH/version.json /mix/.

echo "Update firmware package finished"
exit 0
