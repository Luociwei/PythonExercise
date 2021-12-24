#!/bin/bash

# dpkg update script
# FW_UPDATE_BASE_FOLDER=/var/fw_update
# FW_UPDATE_TEMP_FOLDER_PATH=$FW_UPDATE_BASE_FOLDER/temp

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
echo "update deb packages"


do_exit(){
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
	umount /mnt 2>/dev/null
}


FWUpdateDeb(){
	echo ""
	echo "Update deb packages..."
	cd $PACKAGE_SOURCE_PATH
	file_list=`ls *.deb`
	for file in $file_list
	do
		echo ""
		echo "install $file..."
		dpkg -i $file
        # check failure
        r=$?
        if [[ $r -ne 0 ]]
        then
            # only print error.
            # tried that if return 1 here, update will break in rollback.
            # TO BE REFINED when reviewing FWUP in next fw workshop, or later commit.
            echo "ERROR: install $file failed with ret:"$r
        else
		    echo "install $file done"
        fi
	done
	echo "Install deb package finished"
    return 0
}

FWUpdateDeb
if [ $? -ne 0 ];then
	exit 1
fi

exit 0
