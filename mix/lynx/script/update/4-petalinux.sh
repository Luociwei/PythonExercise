
#!/bin/bash
#update petalinux img to emmc partition-1

PACKAGE_SOURCE_PATH=

PETA_LINUX_IMGAE_FILE_NAME="petalinux.img"

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


echo "update image is '$PETA_LINUX_IMGAE_FILE_NAME'"
#check update file exist?
if [ ! -f "$PACKAGE_SOURCE_PATH/$PETA_LINUX_IMGAE_FILE_NAME" ]; then
	echo "Petalinux image file '$PETA_LINUX_IMGAE_FILE_NAME' is not exist."
	#optional
	exit 0
fi

#--------------------------------------------

do_exit(){
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
}

echo "$PACKAGE_FILE_NAME updating..."

# umount /mnt in case there's node mounted
umount /mnt 2>/dev/null
umount /mnt 2>/dev/null
umount /mnt 2>/dev/null

echo "mount EMMC partition-1 device."
mount /dev/mmcblk0p1 /mnt
if [ ! $? -eq 0 ]; then
	echo "mount /dev/mmcblk0p4 /mnt failed."
	do_exit
	exit 1
fi

# copy image to mmcblk0p1
echo "update '$PETA_LINUX_IMGAE_FILE_NAME'..."
rm -rf /mnt/$PETA_LINUX_IMGAE_FILE_NAME
cp -f $PACKAGE_SOURCE_PATH/$PETA_LINUX_IMGAE_FILE_NAME  /mnt/
if [ ! $? -eq 0 ]; then
		echo "[Error ]update '$PETA_LINUX_IMGAE_FILE_NAME ' failed."
		do_exit
		exit 2
fi

# disable update rootfs in petalinux before it is ready
# # generate uEnv.txt to mmcblk0p1
# if [ -f /mnt/uEnv.txt ]; then
# 	rm /mnt/uEnv.txt
# fi

# echo "bootdelay=2" >> /mnt/uEnv.txt
# echo "modeboot=petalinux_boot" >> /mnt/uEnv.txt


sync
echo "update '$PETA_LINUX_IMGAE_FILE_NAME' finished."
do_exit


# reboot to petalinux
#reboot -nf

exit 0

