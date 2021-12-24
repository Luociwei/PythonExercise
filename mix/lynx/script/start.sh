#!/bin/bash
#
# start the user program
#
# set timezone as Shanghai
cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

LOCAL_FILE_PATH=$(cd "$(dirname "$0")";pwd)
cd $LOCAL_FILE_PATH
source /etc/profile.d/env.sh

echo "-------------------- $0 --------------------"
if [ -f $LOCAL_FILE_PATH/env/net_reset.sh ]; then
	bash $LOCAL_FILE_PATH/env/net_reset.sh
fi

if [ -f $LOCAL_FILE_PATH/env/usb_reset.sh ]; then
	bash $LOCAL_FILE_PATH/env/usb_reset.sh
fi

depmod
modprobe axi4lite

sync

#network default config
if [ -f $LOCAL_FILE_PATH/env/network_config.sh ]; then
	bash $LOCAL_FILE_PATH/env/network_config.sh
fi

#set a time to avoid lib compiling issue
date 010100002019

#update
if [ -f $LOCAL_FILE_PATH/update.sh ]; then
	#create logs path
	if [ ! -d $MIX_LOG_PATH ]; then
		mkdir -p $MIX_LOG_PATH
	fi
	echo ""
	echo "FW updating ..."
	bash $LOCAL_FILE_PATH/update.sh | tee -a $MIX_LOG_PATH/update.log 2>&1
	if [ -f /tmp/update_success ]; then
		echo ""
		echo "Update FW Package finished, now restart system ...."
		sync
		reboot
		exit 0
	elif [ -f /tmp/update_skip ]; then
		echo ""
		echo "FW Update is Skipped, start to launch application ...."
		echo ""
	else
		echo ""
		echo "[Error ] FW update failed. Please check log in /var/log/fw_update"
		echo ""
	fi
fi

LAUNCHER_FOLDER=/mix/lynx/launcher
#application
if [ -f $LAUNCHER_FOLDER/run_launcher.sh ]; then
	cd $LAUNCHER_FOLDER
	sh run_launcher.sh &
	cd ..
elif [ -f $LAUNCHER_FOLDER/launcher.py ]; then
    cd $LAUNCHER_FOLDER
	python2.7 launcher.py &
    cd ..
fi

echo "-------------------- $0 end --------------------"


