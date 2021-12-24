#!/bin/bash
#ubuntu rootfs update scripts file

PACKAGE_FILE_NAME="rootfs.tgz"

NEW_MIX_FW_FOLDER_NAME="mix_fw_pack"
NEW_MIX_FW_PACKET_FILE_NAME="MIX_FW_TEMP.tgz"
VAR_LOG_FOLDER="/var/log"
MIX_FOLDER_FILE_LIST=

BACKUP_CHROOT_NAME="backup_chroot"

PACKAGE_SOURCE_PATH=
SCRIPT_SOURCE_PATH=

set +e

Usage()
{
cat <<EOF
Usage:
$0 <fw_update_temp_folder_path> <fw_update_temp_scripts_path>
EOF
}
if [ "$#" -lt 2 ] ;then
    Usage
    exit 0
fi

PACKAGE_SOURCE_PATH=$1
SCRIPT_SOURCE_PATH=$2
echo "Modules update package is '$PACKAGE_FILE_NAME'"
#check package file exsit?
if [ ! -f $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME ]; then

	echo "$PACKAGE_FILE_NAME is not exist."
	#optional
	exit 0
fi


#-------------------------------------------------
#TODO
echo "Update '$PACKAGE_FILE_NAME' files..."

if [ -d /mix ]; then
	MIX_FOLDER_FILE_LIST="`ls`"
	MIX_FOLDER_FILE_LIST=${MIX_FOLDER_FILE_LIST//upload/ }
fi


cd $PACKAGE_SOURCE_PATH/


echo ""
echo "Prepare '$BACKUP_CHROOT_NAME' ...."
umount /mnt 2>>/dev/null

if [ ! -d /$BACKUP_CHROOT_NAME ]; then
	mkdir /$BACKUP_CHROOT_NAME
else
	rm -rf /$BACKUP_CHROOT_NAME/* 2>/dev/null
fi

update_file_list="`ls / 2>>/dev/null`"
for update_file in $update_file_list
do 
	if [ $update_file = $BACKUP_CHROOT_NAME ] || [ $update_file = "proc" ] || [ $update_file = "sys" ] || [ $update_file = "dev" ] || [ $update_file = "run" ];then
		continue
	fi

	echo "  '$update_file' -> '/$BACKUP_CHROOT_NAME/'"
	cp -af /$update_file /$BACKUP_CHROOT_NAME/

done
ls /$BACKUP_CHROOT_NAME/

set -e
mkdir -p /$BACKUP_CHROOT_NAME/proc
mkdir -p /$BACKUP_CHROOT_NAME/sys
mkdir -p /$BACKUP_CHROOT_NAME/dev
mkdir -p /$BACKUP_CHROOT_NAME/mnt
set +e	
sync
sleep 1

mount -t proc /proc/ /$BACKUP_CHROOT_NAME/proc/
if [ $? -ne 0 ]; then
	exit 2
fi
mount -t sysfs /sys/ /$BACKUP_CHROOT_NAME/sys/
if [ $? -ne 0 ]; then
	umount /$BACKUP_CHROOT_NAME/proc/
	exit 3
fi
mount -o bind /dev/ /$BACKUP_CHROOT_NAME/dev/
if [ $? -ne 0 ]; then
	umount /$BACKUP_CHROOT_NAME/sys/
	umount /$BACKUP_CHROOT_NAME/proc/
	exit 4
fi

cd /
ls -l
echo "Prepare '$BACKUP_CHROOT_NAME' finished"

#get rm old file list
file_list=`ls /`
rm_old_file_list=
for file in $file_list
do
	if [ $file = 'backup_chroot' ] || [ $file = 'proc' ] || [ $file = 'sys' ] || [ $file = 'dev' ] || [ $file = 'run' ]; then
		continue
	fi
	rm_old_file_list=${rm_old_file_list}" "${file}	
done
echo "remove file list: [$rm_old_file_list]"

echo "Enter ROOT '/$BACKUP_CHROOT_NAME'..."
chroot /$BACKUP_CHROOT_NAME <<-EOF_CHROOT

echo "Mount device to '/mnt' "
mount /dev/mmcblk0p2 /mnt

cd /mnt
ls -lh
echo "Clean old rootfs..."
rm -rf $rm_old_file_list
echo "Clean old rootfs finished"
ls /mnt -lh


echo "update new rootfs..."
echo "FW: $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME "
ls $PACKAGE_SOURCE_PATH/
tar -xmzf $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME -C /mnt

#------------------------------
#boot
mkdir -p /mnt/boot
cp -af /boot/*  /mnt/boot/

#restore update folder
mkdir -p /mnt$PACKAGE_SOURCE_PATH/
cp -af $PACKAGE_SOURCE_PATH/* /mnt$PACKAGE_SOURCE_PATH/
ls /mnt$PACKAGE_SOURCE_PATH/

mkdir -p /mnt$SCRIPT_SOURCE_PATH/
cp -af $SCRIPT_SOURCE_PATH/* /mnt$SCRIPT_SOURCE_PATH/
ls /mnt$SCRIPT_SOURCE_PATH/

cp -af $VAR_LOG_FOLDER/* /mnt$VAR_LOG_FOLDER/
rm -rf $PACKAGE_SOURCE_PATH/$PACKAGE_FILE_NAME


#-------------------------------

cd /
sync
umount /mnt
EOF_CHROOT

echo "Exit ROOT '/$BACKUP_CHROOT_NAME' "
umount /$BACKUP_CHROOT_NAME/proc
umount /$BACKUP_CHROOT_NAME/sys
umount /$BACKUP_CHROOT_NAME/dev
cd .

mv /sbin/reboot /sbin/reboot_orig
echo "#!/bin/bash" >> /sbin/reboot
echo "reboot_orig -nf" >> /sbin/reboot
chmod +x /sbin/reboot

echo "Update '$PACKAGE_FILE_NAME' files finished"
#--------------------------------------------------
exit 0



