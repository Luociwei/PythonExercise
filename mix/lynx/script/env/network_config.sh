#!/bin/bash

ifconfig eth0 down
sleep 1

if [[ -s /boot/ip_addr.conf ]]
then
    ip_addr=`cat /boot/ip_addr.conf`
    ifconfig eth0 $ip_addr
else
    echo '/boot/ip_addr.conf not found; setting default ip 169.254.1.254'
    ifconfig eth0 169.254.1.254
fi

#set MAC address
if [ -f /boot/mac_addr ]; then

	#mac address string length
	length=`cat /boot/mac_addr | awk '{ print length($0) }'`
	#':' count
	count=`grep -o ':' /boot/mac_addr|wc -l`

	if [[ $length -eq 17 && $count -eq 5 ]]; then
		mac_address=`cat /boot/mac_addr`
		if [ -n '$mac_addr' ]; then
			ifconfig eth0 down
			sleep 1
			ifconfig eth0 hw ether $mac_address
			if [ $? -ne 0 ]; then
				echo "[Error ] Network MAC address set failed."
			fi	
		fi
	else
		echo "[Error ] MAC address string error."
	fi
fi

ifconfig eth0 up
